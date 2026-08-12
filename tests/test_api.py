from fastapi.testclient import (
    TestClient,
)

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] in {
        "ok",
        "degraded",
    }

    assert data["service"] == "MD Notes Agent"

    assert "version" in data

    assert "checks" in data


def test_home_page():
    response = client.get("/")

    assert response.status_code == 200


def test_organize_rejects_empty_input():
    response = client.post(
        "/api/organize",
        json={
            "text": "",
            "mode": "fast",
            "language": "auto",
            "detail_level": ("medium"),
        },
    )

    # Pydantic request validation
    assert response.status_code == 422


def test_invalid_mode_rejected():
    response = client.post(
        "/api/organize",
        json={
            "text": ("Some valid text."),
            "mode": "invalid-mode",
            "language": "auto",
            "detail_level": ("medium"),
        },
    )

    assert response.status_code == 422


def test_invalid_detail_level_rejected():
    response = client.post(
        "/api/organize",
        json={
            "text": ("Some valid text."),
            "mode": "fast",
            "language": "auto",
            "detail_level": ("super-long"),
        },
    )

    assert response.status_code == 422
