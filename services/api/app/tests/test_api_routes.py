from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.models import Base
from app.db.seed import seed_database
from app.main import app


def build_client() -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    with TestingSessionLocal() as db:
        seed_database(db)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@openvalidations.com", "password": "apip-admin-change-me"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def api_key_headers(client: TestClient, plan: str = "pro") -> dict[str, str]:
    response = client.post(
        "/api/v1/admin/api-keys",
        headers=auth_headers(client),
        json={"name": f"{plan.title()} test key", "plan": plan},
    )
    assert response.status_code == 201
    return {"X-API-Key": response.json()["api_key"]}


def test_backend_v1_rest_endpoints_return_seeded_data():
    client = build_client()
    headers = api_key_headers(client)

    for path in [
        "/api/v1/scoreboard",
        "/api/v1/companies",
        "/api/v1/industries",
        "/api/v1/countries",
        "/api/v1/models",
        "/api/v1/metrics",
        "/api/v1/metrics/search",
        "/api/v1/sources",
    ]:
        response = client.get(path, headers=headers)
        assert response.status_code == 200
        if "items" in response.json():
            assert response.json()["items"]


def test_api_v1_health_endpoint_reports_service_status():
    client = build_client()

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"ok", "degraded"}
    assert payload["checks"]["api"] == "ok"
    assert set(payload["checks"]) == {"api", "postgres", "redis"}


def test_confidence_endpoint_returns_metric_confidence():
    client = build_client()
    headers = api_key_headers(client)
    metrics = client.get("/api/v1/metrics/search", headers=headers).json()["items"]

    response = client.get(f"/api/v1/confidence/{metrics[0]['id']}", headers=headers)

    assert response.status_code == 200
    assert response.json()["score"] >= 0


def test_ai_reality_index_endpoint_returns_ranked_entity_scores():
    client = build_client()
    headers = api_key_headers(client)

    response = client.get("/api/v1/ai-reality-index", headers=headers)

    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    assert {item["entity_type"] for item in items} >= {"company", "industry", "country"}
    first = items[0]
    assert first["score"] >= items[-1]["score"]
    assert first["classification"] in {
        "Elite",
        "Strong",
        "Emerging",
        "Speculative",
        "Cash Burn Zone",
    }
    assert first["components"]["roi"] >= 0
    assert first["components"]["revenue_growth"] >= 0
    assert first["components"]["margin"] >= 0
    assert first["components"]["adoption"] >= 0
    assert first["confidence"]["source_count"] >= 1
    assert first["confidence"]["last_updated"]


def test_ai_reality_index_endpoint_filters_by_entity_type():
    client = build_client()
    headers = api_key_headers(client)

    response = client.get("/api/v1/ai-reality-index?entity_type=industry", headers=headers)

    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    assert {item["entity_type"] for item in items} == {"industry"}


def test_company_validation_dashboard_returns_seeded_beta_companies():
    client = build_client()
    headers = api_key_headers(client)

    response = client.get("/api/v1/company-validations", headers=headers)

    assert response.status_code == 200
    items = response.json()["items"]
    assert {item["company"] for item in items} >= {
        "Microsoft",
        "Google",
        "Meta",
        "Amazon",
        "NVIDIA",
        "OpenAI",
        "Anthropic",
        "xAI",
        "Mistral",
        "Perplexity",
    }
    nvidia = next(item for item in items if item["company"] == "NVIDIA")
    assert nvidia["openvals_validation_score"] > 0
    assert nvidia["openvals_validation_label"]
    assert nvidia["evidence_coverage_score"] > 0
    assert nvidia["confidence_score"] > 0
    assert nvidia["evidence_count"] >= 1
    assert nvidia["evidence"][0]["source"]["url"].startswith("https://")
    assert nvidia["source_reviews"]


def test_microsoft_gold_standard_validation_report_returns_required_sections():
    client = build_client()
    headers = api_key_headers(client)

    response = client.get("/api/v1/companies/microsoft/validation-report", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["company"] == "Microsoft"
    assert payload["report_path"] == "/companies/microsoft/validation-report"
    assert payload["methodology_version"] == "gold-standard-v1"
    assert payload["evidence_coverage_score"] == 100.0
    assert payload["openvals_validation_score"] > 0
    assert payload["openvals_validation_label"]
    assert "methodology" in payload["methodology_trace"].lower()
    assert {section["title"] for section in payload["sections"]} == {
        "Revenue Evidence",
        "AI Revenue Evidence",
        "AI Investment Evidence",
        "Infrastructure Investment Evidence",
        "Earnings Call Evidence",
        "Investor Presentation Evidence",
    }
    for section in payload["sections"]:
        assert section["coverage_score"] == 100.0
        assert section["source_approval_status"] == "approved"
        assert section["reviewer_notes"]
        assert section["methodology_trace"]
        assert section["lineage"]
        assert section["evidence"]
        assert all(item["approval_status"] == "approved" for item in section["evidence"])
    assert payload["source_lineage"]


def test_admin_microsoft_validation_source_review_and_export_workflow():
    client = build_client()
    headers = auth_headers(client)

    workspace = client.get("/api/v1/admin/microsoft-validation", headers=headers)

    assert workspace.status_code == 200
    report = workspace.json()
    evidence_id = report["sections"][0]["evidence"][0]["id"]

    review = client.patch(
        f"/api/v1/admin/microsoft-validation/evidence/{evidence_id}/review",
        headers=headers,
        json={
            "approval_status": "verified",
            "reviewer_notes": "Verified against Microsoft investor source lineage.",
        },
    )

    assert review.status_code == 200
    reviewed = review.json()
    reviewed_evidence = reviewed["sections"][0]["evidence"][0]
    assert reviewed_evidence["approval_status"] == "verified"
    assert reviewed_evidence["reviewer_notes"] == "Verified against Microsoft investor source lineage."

    exported = client.post("/api/v1/admin/microsoft-validation/export", headers=headers)

    assert exported.status_code == 200
    exported_payload = exported.json()
    assert exported_payload["exported_at"]
    assert exported_payload["report_path"] == "/companies/microsoft/validation-report"

    audit = client.get("/api/v1/admin/audit-logs", headers=headers)
    actions = {item["action"] for item in audit.json()["items"]}
    assert "microsoft_validation.source_reviewed" in actions
    assert "microsoft_validation.report_exported" in actions


def test_autonomous_research_trust_center_queues_phase_one_evidence_without_auto_publish():
    client = build_client()
    headers = api_key_headers(client)

    response = client.get("/api/v1/trust-center", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["auto_publish_enabled"] is False
    assert payload["workflow"] == "COLLECT -> ANALYZE -> SCORE -> QUEUE -> REVIEW -> APPROVE -> PUBLISH"
    companies = {item["company"] for item in payload["items"]}
    assert companies >= {"Microsoft", "NVIDIA", "Google"}
    assert payload["metrics"]["total_records"] >= 9
    assert payload["metrics"]["under_review_records"] >= 9
    assert payload["metrics"]["published_records"] == 0
    first = payload["items"][0]
    assert first["status"] == "Under Review"
    assert first["evidence_classification"] in {"Reported", "Estimated", "Derived", "Validated"}
    assert first["confidence_score"] >= 0
    assert first["evidence_coverage_score"] >= 0
    assert first["openvals_score"] >= 0
    assert first["approval_recommendation"] in {"Auto Approve", "Manual Review", "Reject"}
    assert first["lineage"]["source_url"].startswith("https://")


def test_admin_autonomous_review_and_publisher_flow_updates_public_lineage():
    client = build_client()
    headers = auth_headers(client)

    dashboard = client.get("/api/v1/admin/autonomous-research", headers=headers)

    assert dashboard.status_code == 200
    record = dashboard.json()["approval_queue"][0]

    review = client.patch(
        f"/api/v1/admin/autonomous-research/evidence/{record['id']}/review",
        headers=headers,
        json={"decision": "approve", "notes": "Approved for controlled V1 publication."},
    )

    assert review.status_code == 200
    reviewed = review.json()
    assert reviewed["status"] == "Approved"
    assert reviewed["evidence_classification"] == "Validated"
    assert reviewed["reviewer"] == "APIP Admin"
    assert reviewed["approved_at"]

    publish = client.post("/api/v1/admin/autonomous-research/run/publisher", headers=headers)

    assert publish.status_code == 200
    assert publish.json()["agent"] == "Publisher Agent"
    lineage = client.get("/api/v1/source-lineage", headers=api_key_headers(client))
    assert lineage.status_code == 200
    assert lineage.json()["items"]
    published = client.get("/api/v1/trust-center", headers=api_key_headers(client)).json()
    assert published["metrics"]["published_records"] >= 1


def test_research_operations_dashboard_returns_queue_and_progress_metrics():
    client = build_client()
    headers = api_key_headers(client)

    response = client.get("/api/v1/research-operations", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    items = payload["items"]
    assert {item["company"] for item in items} >= {
        "Microsoft",
        "Google",
        "Meta",
        "Amazon",
        "NVIDIA",
        "OpenAI",
        "Anthropic",
        "xAI",
        "Mistral",
        "Perplexity",
    }
    microsoft = next(item for item in items if item["company"] == "Microsoft")
    assert microsoft["status"] in {
        "Not Started",
        "Researching",
        "Evidence Collected",
        "Under Review",
        "Approved",
        "Published",
    }
    assert microsoft["assigned_to"] == "APIP Admin"
    assert microsoft["reviewer"] == "APIP Admin"
    assert microsoft["evidence_count"] >= 1
    assert microsoft["evidence_coverage_score"] > 0
    assert microsoft["progress_percent"] > 0
    metrics = payload["metrics"]
    assert metrics["total_items"] >= 10
    assert metrics["assigned_items"] >= 10
    assert metrics["collected_evidence_count"] >= 10
    assert metrics["approved_evidence_count"] >= 10


def test_admin_routes_require_admin_authentication():
    client = build_client()

    response = client.get("/api/v1/admin/dashboard")

    assert response.status_code == 401


def test_admin_research_assignment_status_evidence_review_and_audit_flow():
    client = build_client()
    headers = auth_headers(client)

    queue = client.get("/api/v1/admin/research-queue", headers=headers)
    assert queue.status_code == 200
    item = next(entry for entry in queue.json()["items"] if entry["company"] == "OpenAI")

    assignment = client.patch(
        f"/api/v1/admin/research-queue/{item['id']}/assign",
        headers=headers,
        json={"notes": "Assigned for beta research verification."},
    )
    assert assignment.status_code == 200
    assert assignment.json()["assigned_to"] == "APIP Admin"

    status_update = client.patch(
        f"/api/v1/admin/research-queue/{item['id']}/status",
        headers=headers,
        json={"status": "Researching", "notes": "Research resumed for beta verification."},
    )
    assert status_update.status_code == 200
    assert status_update.json()["status"] == "Researching"

    source = client.post(
        "/api/v1/admin/sources",
        headers=headers,
        json={
            "title": "OpenAI research operations evidence",
            "source_type": "public_company_statement",
            "url": "https://openai.com/business/",
            "publisher": "OpenAI",
            "status": "pending",
        },
    )
    assert source.status_code == 201
    source_id = source.json()["id"]

    collection = client.post(
        f"/api/v1/admin/research-queue/{item['id']}/evidence",
        headers=headers,
        json={
            "source_id": source_id,
            "evidence_type": "public_company_statement",
            "notes": "Collected OpenAI business evidence for operations workflow.",
        },
    )
    assert collection.status_code == 201
    collected = collection.json()
    assert collected["status"] == "Evidence Collected"
    evidence = next(entry for entry in collected["evidence"] if entry["source"]["id"] == source_id)
    assert evidence["approval_status"] == "pending"

    review = client.patch(
        f"/api/v1/admin/research-evidence/{evidence['id']}/review",
        headers=headers,
        json={
            "approval_status": "approved",
            "reviewer_notes": "Approved source for research operations.",
        },
    )
    assert review.status_code == 200
    reviewed = review.json()
    assert reviewed["status"] == "Under Review"
    reviewed_evidence = next(entry for entry in reviewed["evidence"] if entry["id"] == evidence["id"])
    assert reviewed_evidence["approval_status"] == "approved"
    assert reviewed_evidence["source"]["status"] == "approved"

    progress = client.get("/api/v1/admin/research-progress", headers=headers)
    assert progress.status_code == 200
    assert progress.json()["approved_evidence_count"] >= 1

    audit = client.get("/api/v1/admin/research-audit", headers=headers)
    assert audit.status_code == 200
    actions = {entry["action"] for entry in audit.json()["items"]}
    assert {
        "research.assigned",
        "research.status_updated",
        "research.evidence_collected",
        "research.evidence_reviewed",
    } <= actions


def test_admin_company_validation_review_and_approval_workflow():
    client = build_client()
    headers = auth_headers(client)

    dashboard = client.get("/api/v1/admin/company-validations", headers=headers)
    assert dashboard.status_code == 200
    validation = next(item for item in dashboard.json()["items"] if item["company"] == "Microsoft")
    evidence_id = validation["evidence"][0]["id"]
    review_id = validation["source_reviews"][0]["id"]

    evidence_review = client.patch(
        f"/api/v1/admin/company-validations/evidence/{evidence_id}/review",
        headers=headers,
        json={
            "review_status": "verified",
            "reviewer_notes": "Validated against official Microsoft source.",
        },
    )
    assert evidence_review.status_code == 200
    assert evidence_review.json()["openvals_validation_score"] > 0

    source_review = client.patch(
        f"/api/v1/admin/company-validations/source-reviews/{review_id}",
        headers=headers,
        json={
            "review_status": "verified",
            "reviewer_notes": "Source remains accepted for beta validation.",
        },
    )
    assert source_review.status_code == 200
    assert source_review.json()["source_reviews"][0]["review_status"] == "verified"

    approval = client.patch(
        f"/api/v1/admin/company-validations/{validation['id']}/approve",
        headers=headers,
        json={"reviewer_notes": "Approved for beta company validation dashboard."},
    )
    assert approval.status_code == 200
    approved = approval.json()
    assert approved["status"] == "approved"
    assert approved["approved_by"] == "APIP Admin"
    assert approved["approved_at"]

    audit_logs = client.get("/api/v1/admin/audit-logs", headers=headers)
    actions = {item["action"] for item in audit_logs.json()["items"]}
    assert {
        "company_validation.evidence_reviewed",
        "company_validation.source_reviewed",
        "company_validation.approved",
    } <= actions


def test_admin_dashboard_catalog_management_source_management_and_seed_import():
    client = build_client()
    headers = auth_headers(client)

    dashboard = client.get("/api/v1/admin/dashboard", headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["counts"]["companies"] >= 1

    api_key = client.post(
        "/api/v1/admin/api-keys",
        headers=headers,
        json={"name": "Partner API", "plan": "free"},
    )
    assert api_key.status_code == 201
    assert api_key.json()["api_key"].startswith("apip_live_")
    assert api_key.json()["daily_limit"] == 100

    company = client.post(
        "/api/v1/admin/companies",
        headers=headers,
        json={
            "name": "Test AI Corp",
            "ticker": "TAIC",
            "website_url": "https://example.com/test-ai-corp",
        },
    )
    assert company.status_code == 201
    company_id = company.json()["id"]
    company_update = client.patch(
        f"/api/v1/admin/companies/{company_id}",
        headers=headers,
        json={"status": "archived"},
    )
    assert company_update.status_code == 200
    assert company_update.json()["status"] == "archived"

    industry = client.post(
        "/api/v1/admin/industries",
        headers=headers,
        json={"name": "Robotics AI"},
    )
    assert industry.status_code == 201
    country = client.post(
        "/api/v1/admin/countries",
        headers=headers,
        json={"name": "Brazil", "iso_code": "BR", "region": "South America"},
    )
    assert country.status_code == 201
    model = client.post(
        "/api/v1/admin/models",
        headers=headers,
        json={"name": "Nova", "model_family": "Nova"},
    )
    assert model.status_code == 201

    source = client.post(
        "/api/v1/admin/sources",
        headers=headers,
        json={
            "title": "Test Source",
            "source_type": "annual_report",
            "url": "https://example.com/test-source",
            "publisher": "OpenVals",
        },
    )
    assert source.status_code == 201
    source_id = source.json()["id"]
    approval = client.patch(f"/api/v1/admin/sources/{source_id}/approve", headers=headers)
    assert approval.status_code == 200
    assert approval.json()["status"] == "approved"

    seed = client.post("/api/v1/admin/seed-import", headers=headers)
    assert seed.status_code == 200
    assert seed.json()["status"] == "completed"

    audit_logs = client.get("/api/v1/admin/audit-logs", headers=headers)
    actions = {item["action"] for item in audit_logs.json()["items"]}
    assert {
        "company.created",
        "industry.created",
        "country.created",
        "model.created",
        "source.approved",
        "seed_import.triggered",
        "api_key.created",
    } <= actions


def test_public_api_requires_api_key():
    client = build_client()

    response = client.get("/api/v1/companies")

    assert response.status_code == 401


def test_seeded_local_development_api_key_can_access_public_api():
    client = build_client()

    response = client.get(
        "/api/v1/companies",
        headers={"X-API-Key": "apip_live_local_dev_key"},
    )

    assert response.status_code == 200
    companies = response.json()["items"]
    assert companies
    assert {item["name"] for item in companies} >= {
        "Microsoft",
        "Google",
        "Meta",
        "Amazon",
        "NVIDIA",
        "OpenAI",
        "Anthropic",
        "xAI",
        "Mistral",
        "Perplexity",
    }


def test_free_api_key_daily_rate_limit_is_enforced():
    client = build_client()
    headers = api_key_headers(client, plan="free")

    for _ in range(100):
        response = client.get("/api/v1/companies", headers=headers)
        assert response.status_code == 200

    limited = client.get("/api/v1/companies", headers=headers)

    assert limited.status_code == 429


def test_metric_responses_include_confidence_engine_fields():
    client = build_client()
    headers = api_key_headers(client)

    response = client.get("/api/v1/metrics/search", headers=headers)

    assert response.status_code == 200
    metric = response.json()["items"][0]
    assert "value" in metric
    assert "confidence_score" in metric
    assert "confidence_label" in metric
    assert "source_count" in metric
    assert "coverage_score" in metric
    assert "coverage_label" in metric
    assert "coverage" in metric
    assert "last_updated" in metric
    assert "methodology_note" in metric
    assert metric["source_count"] >= 1
    assert metric["coverage_score"] > 0
    assert metric["coverage"]["tier_counts"]
    assert metric["sources"]
    source = metric["sources"][0]
    assert "source_tier" in source
    assert "credibility_score" in source
    assert source["url"].startswith("https://")


def test_admin_csv_import_review_approval_and_audit_flow():
    client = build_client()
    headers = auth_headers(client)
    csv_bytes = (
        b"company,year,metric_type,value,source_url,source_type,methodology_note,published_at\n"
        b"OpenAI,2025,ai_cash_flow,123456789,"
        b"https://example.com/openai-2025-cash-flow,annual_report,"
        b"Annual report value normalized from reported AI cash flow with clear extraction notes,"
        b"2026-05-01T00:00:00+00:00\n"
    )

    upload = client.post(
        "/api/v1/admin/imports/csv",
        headers=headers,
        files={"file": ("financial_metrics.csv", csv_bytes, "text/csv")},
    )

    assert upload.status_code == 201
    imported = upload.json()["items"][0]
    assert upload.json()["imported_count"] == 1
    assert imported["company"] == "OpenAI"
    assert imported["approved_status"] == "pending"
    assert imported["confidence_score"] > 0

    review = client.get("/api/v1/admin/source-metrics", headers=headers)
    assert review.status_code == 200
    reviewed_metric = review.json()["items"][0]
    assert reviewed_metric["value"] == 123456789
    assert reviewed_metric["source_url"] == "https://example.com/openai-2025-cash-flow"
    assert reviewed_metric["source_type"] == "annual_report"
    assert reviewed_metric["created_by"] == "APIP Admin"

    approval = client.patch(
        f"/api/v1/admin/source-metrics/{imported['id']}/approve",
        headers=headers,
    )
    assert approval.status_code == 200
    assert approval.json()["approved_status"] == "approved"

    metrics = client.get(
        "/api/v1/metrics/search?entity_type=company&metric_key=ai_cash_flow",
        headers=api_key_headers(client),
    )
    assert metrics.status_code == 200
    published_metric = metrics.json()["items"][0]
    assert published_metric["value"] == 123456789
    assert published_metric["confidence_score"] > 0
    assert published_metric["confidence_label"]
    assert published_metric["source_count"] >= 1
    assert published_metric["last_updated"]
    assert published_metric["methodology_note"]

    audit_logs = client.get("/api/v1/admin/audit-logs", headers=headers)
    assert audit_logs.status_code == 200
    actions = {item["action"] for item in audit_logs.json()["items"]}
    assert {"source_metric.imported", "source_metric.approved", "metric_value.published"} <= actions


def test_admin_can_reject_imported_source_metric():
    client = build_client()
    headers = auth_headers(client)
    csv_bytes = (
        b"company,year,metric_type,value,source_url,source_type,methodology_note\n"
        b"Anthropic,2025,ai_operating_cost,987654321,"
        b"https://example.com/anthropic-costs,news_article,"
        b"News article estimate captured for review and held from publication until approved\n"
    )

    upload = client.post(
        "/api/v1/admin/imports/csv",
        headers=headers,
        files={"file": ("financial_metrics.csv", csv_bytes, "text/csv")},
    )
    imported_id = upload.json()["items"][0]["id"]

    rejection = client.patch(
        f"/api/v1/admin/source-metrics/{imported_id}/reject",
        headers=headers,
    )

    assert rejection.status_code == 200
    assert rejection.json()["approved_status"] == "rejected"

    metrics = client.get(
        "/api/v1/metrics/search?entity_type=company&metric_key=ai_operating_cost",
        headers=api_key_headers(client),
    )
    assert metrics.status_code == 200
    assert metrics.json()["items"] == []


def test_admin_manual_research_entry_connector_creates_pending_source_metric():
    client = build_client()
    headers = auth_headers(client)

    response = client.post(
        "/api/v1/admin/research-entries",
        headers=headers,
        json={
            "company": "Mistral",
            "year": 2026,
            "metric_type": "adoption",
            "value": 58,
            "title": "Mistral AI beta research note",
            "source_url": "https://mistral.ai/news",
            "source_type": "public_company_statement",
            "publisher": "Mistral AI",
            "published_at": "2026-05-01T00:00:00+00:00",
            "methodology_note": (
                "Manual beta research entry created from Mistral public company statements "
                "and held pending admin review before publication."
            ),
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["company"] == "Mistral"
    assert payload["approved_status"] == "pending"
    assert payload["source_type"] == "public_company_statement"
    assert payload["confidence_score"] > 0


def test_admin_catalog_csv_import_tracks_source_confidence_and_lineage():
    client = build_client()
    headers = auth_headers(client)

    country_csv = (
        b"name,slug,iso_code,region,source_url,source_type,source_title,publisher,published_at,methodology_note\n"
        b"Australia,australia,AU,Oceania,https://example.com/australia-country,industry_report,"
        b"Australia Country Reference,Example Data Bureau,2026-01-15T00:00:00+00:00,"
        b"Country catalog row validated from a published source and normalized for APIP lineage tracking.\n"
    )
    country_upload = client.post(
        "/api/v1/admin/imports/catalog/countries/csv",
        headers=headers,
        files={"file": ("countries.csv", country_csv, "text/csv")},
    )
    assert country_upload.status_code == 201
    country_item = country_upload.json()["items"][0]
    assert country_item["entity_type"] == "countries"
    assert country_item["source_type"] == "industry_report"
    assert country_item["confidence_score"] > 0
    assert country_item["imported_by"]
    assert country_item["imported_at"]

    company_csv = (
        b"name,slug,ticker,website_url,headquarters_country_iso_code,status,source_url,source_type,"
        b"source_title,publisher,published_at,methodology_note\n"
        b"Real Data Co,real-data-co,RDC,https://example.com/real-data-co,AU,active,"
        b"https://example.com/real-data-co-sec,sec_filing,Real Data Co Filing,Real Data Co,"
        b"2026-02-01T00:00:00+00:00,"
        b"Company catalog row validated from a filing and normalized for APIP lineage tracking.\n"
    )
    company_upload = client.post(
        "/api/v1/admin/imports/catalog/company/csv",
        headers=headers,
        files={"file": ("companies.csv", company_csv, "text/csv")},
    )
    assert company_upload.status_code == 201
    company_item = company_upload.json()["items"][0]
    assert company_item["entity_type"] == "companies"
    assert company_item["name"] == "Real Data Co"
    assert company_item["source_url"] == "https://example.com/real-data-co-sec"
    assert company_item["source_type"] == "sec_filing"
    assert company_item["confidence_score"] >= country_item["confidence_score"]

    industry_csv = (
        b"name,slug,status,source_url,source_type,source_title,publisher,published_at,methodology_note\n"
        b"Applied Automation,applied-automation,active,https://example.com/applied-automation,"
        b"industry_report,Applied Automation Taxonomy,Example Research,2026-02-10T00:00:00+00:00,"
        b"Industry catalog row validated from a published taxonomy and normalized for APIP lineage tracking.\n"
    )
    industry_upload = client.post(
        "/api/v1/admin/imports/catalog/industries/csv",
        headers=headers,
        files={"file": ("industries.csv", industry_csv, "text/csv")},
    )
    assert industry_upload.status_code == 201
    assert industry_upload.json()["items"][0]["entity_type"] == "industries"

    model_csv = (
        b"name,slug,model_family,provider_company_slug,status,source_url,source_type,source_title,"
        b"publisher,published_at,methodology_note\n"
        b"Real Reasoner,real-reasoner,Real Reasoner,real-data-co,active,"
        b"https://example.com/real-reasoner-presentation,investor_presentation,"
        b"Real Reasoner Model Brief,Real Data Co,2026-03-01T00:00:00+00:00,"
        b"Model catalog row validated from a provider presentation and normalized for APIP lineage tracking.\n"
    )
    model_upload = client.post(
        "/api/v1/admin/imports/catalog/models/csv",
        headers=headers,
        files={"file": ("models.csv", model_csv, "text/csv")},
    )
    assert model_upload.status_code == 201
    assert model_upload.json()["items"][0]["entity_type"] == "models"

    lineage = client.get("/api/v1/admin/lineage?entity_type=companies", headers=headers)
    assert lineage.status_code == 200
    company_lineage = lineage.json()["items"][0]
    assert company_lineage["source_url"] == "https://example.com/real-data-co-sec"
    assert company_lineage["source_type"] == "sec_filing"
    assert company_lineage["confidence_score"] > 0
    assert company_lineage["imported_by"] == "APIP Admin"
    assert company_lineage["imported_at"]
    assert company_lineage["metadata"]["source_url"] == "https://example.com/real-data-co-sec"

    public_companies = client.get("/api/v1/companies", headers=api_key_headers(client))
    assert public_companies.status_code == 200
    assert any(item["name"] == "Real Data Co" for item in public_companies.json()["items"])

    audit_logs = client.get("/api/v1/admin/audit-logs", headers=headers)
    actions = {item["action"] for item in audit_logs.json()["items"]}
    assert {"country.imported", "company.imported", "industry.imported", "model.imported"} <= actions


def test_admin_catalog_csv_import_validates_required_source_fields():
    client = build_client()
    headers = auth_headers(client)
    invalid_csv = b"name,slug,ticker\nMissing Source Co,missing-source-co,MSC\n"

    response = client.post(
        "/api/v1/admin/imports/catalog/companies/csv",
        headers=headers,
        files={"file": ("companies.csv", invalid_csv, "text/csv")},
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "invalid_csv_template"
    assert "source_url" in detail["message"]
    assert "source_type" in detail["message"]


def test_admin_catalog_csv_import_validates_country_iso_code():
    client = build_client()
    headers = auth_headers(client)
    invalid_csv = (
        b"name,slug,iso_code,region,source_url,source_type\n"
        b"Invalid Country,invalid-country,USA,Nowhere,https://example.com/country,industry_report\n"
    )

    response = client.post(
        "/api/v1/admin/imports/catalog/countries/csv",
        headers=headers,
        files={"file": ("countries.csv", invalid_csv, "text/csv")},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_csv_row"
