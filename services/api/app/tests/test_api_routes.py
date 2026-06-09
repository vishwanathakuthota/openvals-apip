from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.models import Base
from app.db.seed import seed_database
from app.main import app

AI_ECONOMY_COMPANIES = {
    "amazon": "Amazon",
    "anthropic": "Anthropic",
    "alphabet": "Alphabet",
    "meta": "Meta",
    "microsoft": "Microsoft",
    "mistral": "Mistral",
    "nvidia": "NVIDIA",
    "openai": "OpenAI",
    "perplexity": "Perplexity",
    "xai": "xAI",
}


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
    assert payload["status"] == "gold_standard"
    assert payload["gold_standard_rank"] == 1
    assert payload["gold_standard_label"] == "Gold Standard Company #1"
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
    assert (
        reviewed_evidence["reviewer_notes"] == "Verified against Microsoft investor source lineage."
    )

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
    assert (
        payload["workflow"]
        == "COLLECT -> ANALYZE -> SCORE -> QUEUE -> REVIEW -> APPROVE -> PUBLISH"
    )
    companies = {item["company"] for item in payload["items"]}
    assert companies >= {"Microsoft", "NVIDIA", "Google"}
    assert payload["metrics"]["total_records"] >= 18
    assert payload["metrics"]["under_review_records"] >= 0
    assert payload["metrics"]["published_records"] >= 18
    assert payload["trust_index"]["trust_index"] > 0
    assert payload["trust_trend"]
    assert payload["trust_notifications"]
    assert payload["methodology"]["version"] == "trust-index-v1"
    microsoft_records = [item for item in payload["items"] if item["company"] == "Microsoft"]
    assert microsoft_records
    assert {item["status"] for item in microsoft_records} == {"Published"}
    assert {item["evidence_classification"] for item in microsoft_records} == {"Validated"}
    for item in microsoft_records:
        assert item["confidence_score"] >= 0
        assert item["evidence_coverage_score"] >= 0
        assert item["openvals_score"] >= 0
        assert item["reviewer"] == "APIP Admin"
        assert item["approved_at"]
        assert item["published_at"]
        assert item["lineage"]["source_url"].startswith("https://")


def test_openvals_trust_index_api_returns_summary_leaderboard_trend_and_methodology():
    client = build_client()
    headers = api_key_headers(client)

    response = client.get("/api/v1/trust-index", headers=headers)
    leaderboard = client.get("/api/v1/leaderboard", headers=headers)
    methodology = client.get("/api/v1/trust-methodology", headers=headers)

    assert response.status_code == 200
    assert leaderboard.status_code == 200
    assert methodology.status_code == 200
    payload = response.json()
    assert payload["summary"]["entity_type"] == "global"
    assert payload["summary"]["trust_index"] > 0
    assert payload["summary"]["trust_rating"] in {
        "Verified",
        "High Trust",
        "Trusted",
        "Watchlist",
        "Low Trust",
    }
    assert payload["summary"]["trust_classification"] in {
        "Gold Standard",
        "Strong Evidence",
        "Reliable",
        "Developing",
        "Insufficient Evidence",
    }
    assert payload["summary"]["components"]["confidence"] > 0
    assert payload["summary"]["weights"] == {
        "confidence": 0.3,
        "evidence_coverage": 0.25,
        "transparency": 0.2,
        "reproducibility": 0.15,
        "source_quality": 0.1,
    }
    assert payload["leaderboard"]
    assert payload["trend"]
    assert payload["notifications"]
    companies = {item["entity_name"] for item in leaderboard.json()["items"]}
    assert companies >= {"Microsoft", "NVIDIA", "Alphabet"}
    assert methodology.json()["formula"].startswith("30% Confidence")


def test_ai_economy_expansion_publishes_all_ten_companies_to_trust_index():
    client = build_client()
    headers = api_key_headers(client)

    trust_center = client.get("/api/v1/trust-center", headers=headers).json()
    leaderboard = client.get("/api/v1/leaderboard", headers=headers).json()["items"]

    assert trust_center["metrics"]["published_records"] >= 60
    assert trust_center["metrics"]["public_lineage_records"] >= 60
    assert {item["entity_name"] for item in leaderboard} >= set(AI_ECONOMY_COMPANIES.values())
    for company_name in AI_ECONOMY_COMPANIES.values():
        item = next(entry for entry in leaderboard if entry["entity_name"] == company_name)
        assert item["trust_index"] > 0
        assert item["published_record_count"] == 6
        assert item["source_count"] >= 1


def test_ai_economy_expansion_company_artifacts_are_generated_for_all_companies():
    client = build_client()
    headers = api_key_headers(client)

    for slug, company_name in AI_ECONOMY_COMPANIES.items():
        report = client.get(f"/api/v1/companies/{slug}/validation-report", headers=headers)
        timeline = client.get(f"/api/v1/companies/{slug}/evidence-timeline", headers=headers)
        lineage = client.get(f"/api/v1/companies/{slug}/source-lineage", headers=headers)
        score = client.get(f"/api/v1/companies/{slug}/openvals-score", headers=headers)
        trust = client.get(f"/api/v1/companies/{slug}/trust-report", headers=headers)

        assert report.status_code == 200
        assert timeline.status_code == 200
        assert lineage.status_code == 200
        assert score.status_code == 200
        assert trust.status_code == 200
        report_payload = report.json()
        assert report_payload["company"] == company_name
        assert report_payload["status"] in {"gold_standard", "validated"}
        assert report_payload["validation_label"]
        assert report_payload["published_records"] == 6
        assert report_payload["evidence_coverage_score"] > 0
        assert report_payload["openvals_validation_score"] > 0
        assert len(report_payload["sections"]) == 6
        assert timeline.json()["items"]
        assert lineage.json()["items"]
        assert score.json()["published_records"] == 6
        assert score.json()["validation_label"]
        assert score.json()["openvals_score"] > 0
        assert trust.json()["metrics"]["published_records"] == 6


def test_company_and_metric_payloads_include_trust_index_fields():
    client = build_client()
    headers = api_key_headers(client)

    companies = client.get("/api/v1/companies", headers=headers).json()["items"]
    microsoft = next(item for item in companies if item["slug"] == "microsoft")
    company = client.get(f"/api/v1/companies/{microsoft['id']}", headers=headers).json()
    metrics = client.get(
        f"/api/v1/metrics/search?entity_type=company&entity_id={microsoft['id']}",
        headers=headers,
    ).json()["items"]

    assert company["trust_index"]["entity_name"] == "Microsoft"
    assert company["trust_index"]["trust_index"] > 0
    assert company["trust_index"]["components"]["evidence_coverage"] > 0
    assert metrics
    for metric in metrics:
        assert metric["trust_index"] > 0
        assert metric["trust_rating"]
        assert metric["trust_classification"]


def test_microsoft_pilot_artifact_endpoints_are_generated():
    client = build_client()
    headers = api_key_headers(client)

    timeline = client.get("/api/v1/companies/microsoft/evidence-timeline", headers=headers)
    lineage = client.get("/api/v1/companies/microsoft/source-lineage", headers=headers)
    score = client.get("/api/v1/companies/microsoft/openvals-score", headers=headers)
    trust = client.get("/api/v1/companies/microsoft/trust-report", headers=headers)

    assert timeline.status_code == 200
    assert lineage.status_code == 200
    assert score.status_code == 200
    assert trust.status_code == 200
    assert timeline.json()["items"]
    assert lineage.json()["items"]
    assert score.json()["company"] == "Microsoft"
    assert score.json()["gold_standard_rank"] == 1
    assert score.json()["gold_standard_label"] == "Gold Standard Company #1"
    assert score.json()["openvals_score"] > 0
    assert score.json()["published_records"] == 6
    assert trust.json()["status"] == "gold_standard"
    assert trust.json()["gold_standard_rank"] == 1
    assert trust.json()["gold_standard_label"] == "Gold Standard Company #1"
    assert trust.json()["metrics"]["published_records"] == 6


def test_microsoft_gold_standard_metrics_have_evidence_lineage_and_scores():
    client = build_client()
    headers = api_key_headers(client)

    companies = client.get("/api/v1/companies", headers=headers).json()["items"]
    microsoft = next(item for item in companies if item["slug"] == "microsoft")
    response = client.get(
        f"/api/v1/metrics/search?entity_type=company&entity_id={microsoft['id']}",
        headers=headers,
    )

    assert response.status_code == 200
    metrics = {
        item["metric_key"]: item
        for item in response.json()["items"]
        if item["entity_id"] == microsoft["id"]
    }
    assert set(metrics) == {
        "adoption",
        "ai_revenue",
        "ai_spend",
        "gross_margin",
        "revenue_growth",
        "roi",
    }
    for metric in metrics.values():
        assert metric["value"] is not None
        assert metric["confidence_score"] > 0
        assert metric["confidence_label"]
        assert metric["source_count"] >= 1
        assert metric["last_updated"]
        assert metric["methodology_note"]
        assert metric["coverage_score"] > 0
        assert metric["coverage"]["source_count"] >= 1
        assert metric["openvals_score"] > 0
        assert metric["openvals_classification"]
        assert metric["evidence_classification"] == "Validated"
        assert metric["validation_status"] == "Published"
        assert metric["sources"]
        assert metric["source_lineage"]
        for lineage in metric["source_lineage"]:
            assert lineage["source_url"].startswith("https://")
            assert lineage["confidence"] > 0
            assert lineage["evidence_coverage"] > 0
            assert lineage["reviewer"] == "APIP Admin"
            assert lineage["approval_date"]
            assert lineage["openvals_score"] > 0


def test_nvidia_gold_standard_validation_report_and_artifacts_are_generated():
    client = build_client()
    headers = api_key_headers(client)

    report = client.get("/api/v1/companies/nvidia/validation-report", headers=headers)
    timeline = client.get("/api/v1/companies/nvidia/evidence-timeline", headers=headers)
    lineage = client.get("/api/v1/companies/nvidia/source-lineage", headers=headers)
    score = client.get("/api/v1/companies/nvidia/openvals-score", headers=headers)
    trust = client.get("/api/v1/companies/nvidia/trust-report", headers=headers)

    assert report.status_code == 200
    assert timeline.status_code == 200
    assert lineage.status_code == 200
    assert score.status_code == 200
    assert trust.status_code == 200
    report_payload = report.json()
    assert report_payload["company"] == "NVIDIA"
    assert report_payload["status"] == "gold_standard"
    assert report_payload["gold_standard_rank"] == 2
    assert report_payload["gold_standard_label"] == "Gold Standard Company #2"
    assert report_payload["report_path"] == "/companies/nvidia/validation-report"
    assert report_payload["evidence_coverage_score"] == 100.0
    assert {section["title"] for section in report_payload["sections"]} == {
        "Revenue Evidence",
        "AI Revenue Evidence",
        "AI Investment Evidence",
        "Infrastructure Investment Evidence",
        "Earnings Call Evidence",
        "Investor Presentation Evidence",
    }
    for section in report_payload["sections"]:
        assert section["coverage_score"] == 100.0
        assert section["source_approval_status"] == "approved"
        assert section["lineage"]
        assert section["evidence"]
    assert timeline.json()["items"]
    assert lineage.json()["items"]
    assert score.json()["gold_standard_rank"] == 2
    assert score.json()["gold_standard_label"] == "Gold Standard Company #2"
    assert score.json()["published_records"] == 6
    assert trust.json()["status"] == "gold_standard"
    assert trust.json()["metrics"]["published_records"] == 6


def test_nvidia_gold_standard_metrics_have_evidence_lineage_and_scores():
    client = build_client()
    headers = api_key_headers(client)

    companies = client.get("/api/v1/companies", headers=headers).json()["items"]
    nvidia = next(item for item in companies if item["slug"] == "nvidia")
    response = client.get(
        f"/api/v1/metrics/search?entity_type=company&entity_id={nvidia['id']}",
        headers=headers,
    )

    assert response.status_code == 200
    metrics = {
        item["metric_key"]: item
        for item in response.json()["items"]
        if item["entity_id"] == nvidia["id"]
    }
    assert set(metrics) == {
        "adoption",
        "ai_revenue",
        "ai_spend",
        "gross_margin",
        "revenue_growth",
        "roi",
    }
    for metric in metrics.values():
        assert metric["value"] is not None
        assert metric["confidence_score"] > 0
        assert metric["confidence_label"]
        assert metric["source_count"] >= 1
        assert metric["last_updated"]
        assert metric["methodology_note"]
        assert metric["coverage_score"] > 0
        assert metric["coverage"]["source_count"] >= 1
        assert metric["openvals_score"] > 0
        assert metric["openvals_classification"]
        assert metric["evidence_classification"] == "Validated"
        assert metric["validation_status"] == "Published"
        assert metric["sources"]
        assert metric["source_lineage"]
        for lineage_item in metric["source_lineage"]:
            assert lineage_item["source_url"].startswith("https://")
            assert lineage_item["confidence"] > 0
            assert lineage_item["evidence_coverage"] > 0
            assert lineage_item["reviewer"] == "APIP Admin"
            assert lineage_item["approval_date"]
            assert lineage_item["openvals_score"] > 0


def test_alphabet_gold_standard_validation_report_and_artifacts_are_generated():
    client = build_client()
    headers = api_key_headers(client)

    report = client.get("/api/v1/companies/alphabet/validation-report", headers=headers)
    timeline = client.get("/api/v1/companies/alphabet/evidence-timeline", headers=headers)
    lineage = client.get("/api/v1/companies/alphabet/source-lineage", headers=headers)
    score = client.get("/api/v1/companies/alphabet/openvals-score", headers=headers)
    trust = client.get("/api/v1/companies/alphabet/trust-report", headers=headers)

    assert report.status_code == 200
    assert timeline.status_code == 200
    assert lineage.status_code == 200
    assert score.status_code == 200
    assert trust.status_code == 200
    report_payload = report.json()
    assert report_payload["company"] == "Alphabet"
    assert report_payload["company_slug"] == "alphabet"
    assert report_payload["status"] == "gold_standard"
    assert report_payload["gold_standard_rank"] == 3
    assert report_payload["gold_standard_label"] == "Gold Standard Company #3"
    assert report_payload["report_path"] == "/companies/alphabet/validation-report"
    assert report_payload["evidence_coverage_score"] == 100.0
    assert {section["title"] for section in report_payload["sections"]} == {
        "Revenue Evidence",
        "AI Revenue Evidence",
        "AI Investment Evidence",
        "Infrastructure Investment Evidence",
        "Earnings Call Evidence",
        "Investor Presentation Evidence",
    }
    for section in report_payload["sections"]:
        assert section["coverage_score"] == 100.0
        assert section["source_approval_status"] == "approved"
        assert section["lineage"]
        assert section["evidence"]
    assert timeline.json()["items"]
    assert lineage.json()["items"]
    assert score.json()["company"] == "Alphabet"
    assert score.json()["company_slug"] == "alphabet"
    assert score.json()["gold_standard_rank"] == 3
    assert score.json()["gold_standard_label"] == "Gold Standard Company #3"
    assert score.json()["published_records"] == 6
    assert trust.json()["company"] == "Alphabet"
    assert trust.json()["status"] == "gold_standard"
    assert trust.json()["metrics"]["published_records"] == 6


def test_alphabet_gold_standard_metrics_have_evidence_lineage_and_scores():
    client = build_client()
    headers = api_key_headers(client)

    companies = client.get("/api/v1/companies", headers=headers).json()["items"]
    alphabet = next(item for item in companies if item["slug"] == "google")
    response = client.get(
        f"/api/v1/metrics/search?entity_type=company&entity_id={alphabet['id']}",
        headers=headers,
    )

    assert response.status_code == 200
    metrics = {
        item["metric_key"]: item
        for item in response.json()["items"]
        if item["entity_id"] == alphabet["id"]
    }
    assert set(metrics) == {
        "adoption",
        "ai_revenue",
        "ai_spend",
        "gross_margin",
        "revenue_growth",
        "roi",
    }
    for metric in metrics.values():
        assert metric["value"] is not None
        assert metric["confidence_score"] > 0
        assert metric["confidence_label"]
        assert metric["source_count"] >= 1
        assert metric["last_updated"]
        assert metric["methodology_note"]
        assert metric["coverage_score"] > 0
        assert metric["coverage"]["source_count"] >= 1
        assert metric["openvals_score"] > 0
        assert metric["openvals_classification"]
        assert metric["evidence_classification"] == "Validated"
        assert metric["validation_status"] == "Published"
        assert metric["sources"]
        assert metric["source_lineage"]
        for lineage_item in metric["source_lineage"]:
            assert lineage_item["source_url"].startswith("https://")
            assert lineage_item["confidence"] > 0
            assert lineage_item["evidence_coverage"] > 0
            assert lineage_item["reviewer"] == "APIP Admin"
            assert lineage_item["approval_date"]
            assert lineage_item["openvals_score"] > 0


def test_admin_autonomous_review_and_publisher_flow_updates_public_lineage():
    client = build_client()
    headers = auth_headers(client)

    dashboard = client.get("/api/v1/admin/autonomous-research", headers=headers)

    assert dashboard.status_code == 200
    approval_queue = dashboard.json()["approval_queue"]
    if not approval_queue:
        assert dashboard.json()["source_lineage"]
        assert dashboard.json()["trust_center"]["published_records"] >= 18
        return
    record = approval_queue[0]

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
    reviewed_evidence = next(
        entry for entry in reviewed["evidence"] if entry["id"] == evidence["id"]
    )
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


def test_commercial_foundation_api_key_lifecycle_metering_and_dashboard():
    client = build_client()
    headers = auth_headers(client)

    created = client.post(
        "/api/v1/admin/api-keys",
        headers=headers,
        json={"name": "Research API", "plan": "research"},
    )
    assert created.status_code == 201
    created_payload = created.json()
    assert created_payload["plan"] == "research"
    assert created_payload["daily_limit"] == 1000
    assert "source_lineage" in created_payload["entitlements"]

    public_headers = {"X-API-Key": created_payload["api_key"]}
    public_response = client.get("/api/v1/companies", headers=public_headers)
    assert public_response.status_code == 200

    usage = client.get("/api/v1/admin/api-usage", headers=headers)
    assert usage.status_code == 200
    assert any(item["endpoint"] == "/api/v1/companies" for item in usage.json()["items"])

    commercial = client.get("/api/v1/admin/commercial-dashboard", headers=headers)
    assert commercial.status_code == 200
    commercial_payload = commercial.json()
    assert commercial_payload["dashboard"]["api_consumption"]["requests_today"] >= 1
    assert commercial_payload["dashboard"]["plan_distribution"]["research"] >= 1
    assert commercial_payload["subscriptions"]
    assert commercial_payload["invoices"]

    rotated = client.post(
        f"/api/v1/admin/api-keys/{created_payload['id']}/rotate",
        headers=headers,
    )
    assert rotated.status_code == 200
    rotated_payload = rotated.json()
    assert rotated_payload["api_key"].startswith("apip_live_")
    assert rotated_payload["api_key"] != created_payload["api_key"]

    old_key_response = client.get("/api/v1/companies", headers=public_headers)
    assert old_key_response.status_code == 401

    new_headers = {"X-API-Key": rotated_payload["api_key"]}
    assert client.get("/api/v1/companies", headers=new_headers).status_code == 200

    revoked = client.post(
        f"/api/v1/admin/api-keys/{created_payload['id']}/revoke",
        headers=headers,
    )
    assert revoked.status_code == 200
    assert revoked.json()["status"] == "revoked"
    assert client.get("/api/v1/companies", headers=new_headers).status_code == 401


def test_commercial_plans_and_subscription_records_are_exposed_to_admins():
    client = build_client()
    headers = auth_headers(client)

    plans = client.get("/api/v1/admin/plans", headers=headers)
    assert plans.status_code == 200
    plan_keys = {item["key"] for item in plans.json()["items"]}
    assert plan_keys == {"community", "research", "professional", "enterprise"}

    key_response = client.post(
        "/api/v1/admin/api-keys",
        headers=headers,
        json={"name": "Legacy Pro Alias", "plan": "pro"},
    )
    assert key_response.status_code == 201
    assert key_response.json()["plan"] == "professional"

    subscriptions = client.get("/api/v1/admin/subscriptions", headers=headers)
    assert subscriptions.status_code == 200
    assert any(item["plan"] == "professional" for item in subscriptions.json()["items"])

    invoices = client.get("/api/v1/admin/invoices", headers=headers)
    assert invoices.status_code == 200
    assert any(item["payment_provider"] == "manual" for item in invoices.json()["items"])


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
    reviewed_metric = next(
        item
        for item in review.json()["items"]
        if item["company"] == "OpenAI" and item["metric_type"] == "ai_cash_flow"
    )
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
        b"Country catalog row validated from a published source and normalized "
        b"for APIP lineage tracking.\n"
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
        b"Industry catalog row validated from a published taxonomy and normalized "
        b"for APIP lineage tracking.\n"
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
        b"Model catalog row validated from a provider presentation and normalized "
        b"for APIP lineage tracking.\n"
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
    assert {
        "country.imported",
        "company.imported",
        "industry.imported",
        "model.imported",
    } <= actions


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
