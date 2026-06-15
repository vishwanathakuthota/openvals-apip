from collections.abc import Generator
from datetime import UTC, date, datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.models import Base, DataAcquisitionRun, SourceMetric
from app.db.seed import seed_database
from app.domains.data_acquisition.connectors import AcquiredMetric, ConnectorResult
from app.domains.data_acquisition.service import data_acquisition_status, run_acquisition
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


class FixtureRevenueConnector:
    name = "fixture_revenue"
    source_name = "Fixture SEC Revenue"

    def collect(self, target, now: datetime | None = None) -> ConnectorResult:
        retrieved_at = now or datetime(2026, 6, 15, 9, 0, tzinfo=UTC)
        metric = AcquiredMetric(
            company_slug=target.slug,
            metric_key="revenue",
            value=Decimal("1000000000"),
            unit="usd",
            currency="USD",
            period_start=date(2025, 1, 1),
            period_end=date(2025, 12, 31),
            source_name=f"Fixture SEC revenue for {target.name}",
            source_type="sec_filing",
            source_url=f"https://data.sec.gov/fixture/{target.cik}",
            publisher="SEC EDGAR",
            published_at=datetime(2026, 2, 1, tzinfo=UTC),
            retrieved_at=retrieved_at,
            methodology_note=(
                "Fixture connector value representing an SEC-sourced revenue fact with "
                "retrieval timestamp and source lineage."
            ),
            raw_payload={"fixture": True, "ticker": target.ticker},
        )
        return ConnectorResult(
            connector=self.name,
            source_name=self.source_name,
            target=target,
            retrieved_at=retrieved_at,
            metrics=[metric],
            source_url=metric.source_url,
            raw_payload={"fixture": True},
        )


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


def test_admin_routes_require_admin_authentication():
    client = build_client()

    response = client.get("/api/v1/admin/dashboard")

    assert response.status_code == 401


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
    assert response.json()["items"]


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
    assert "last_updated" in metric
    assert "methodology_note" in metric
    assert metric["source_count"] >= 1
    assert metric["sources"]


def test_realtime_data_acquisition_persists_lineage_freshness_and_metrics():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    with TestingSessionLocal() as db:
        seed_database(db)
        result = run_acquisition(db, connectors=[FixtureRevenueConnector()])

        assert result["status"] == "completed"
        assert result["metrics"] == 3
        assert db.scalars(select(DataAcquisitionRun)).all()

        source_metrics = db.scalars(
            select(SourceMetric).where(SourceMetric.metric_type == "revenue")
        ).all()
        assert len(source_metrics) == 3
        assert all(item.retrieved_at for item in source_metrics)
        assert all(item.freshness_score is not None for item in source_metrics)

        status_payload = data_acquisition_status(db)
        assert status_payload["refresh_interval_seconds"] == 1800
        assert {target["slug"] for target in status_payload["targets"]} >= {
            "microsoft",
            "nvidia",
            "alphabet",
        }


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
