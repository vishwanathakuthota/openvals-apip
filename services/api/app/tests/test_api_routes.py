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
