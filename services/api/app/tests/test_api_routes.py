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


def test_backend_v1_rest_endpoints_return_seeded_data():
    client = build_client()
    headers = auth_headers(client)

    for path in [
        "/api/v1/companies",
        "/api/v1/industries",
        "/api/v1/countries",
        "/api/v1/models",
        "/api/v1/metrics",
        "/api/v1/metrics/search",
    ]:
        response = client.get(path, headers=headers)
        assert response.status_code == 200
        assert response.json()["items"]


def test_confidence_endpoint_returns_metric_confidence():
    client = build_client()
    headers = auth_headers(client)
    metrics = client.get("/api/v1/metrics/search", headers=headers).json()["items"]

    response = client.get(f"/api/v1/confidence/{metrics[0]['id']}", headers=headers)

    assert response.status_code == 200
    assert response.json()["score"] >= 0


def test_metric_responses_include_confidence_engine_fields():
    client = build_client()
    headers = auth_headers(client)

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
        headers=headers,
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
        headers=headers,
    )
    assert metrics.status_code == 200
    assert metrics.json()["items"] == []
