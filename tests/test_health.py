from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_200_with_status_ok() -> None:
    # REQ-001: "The API answers GET /health with HTTP 200 and {"status": "ok"}."
    reply = client.get("/health")
    assert reply.status_code == 200
    assert reply.json() == {"status": "ok"}


def test_page_is_served():
    reply = client.get("/")
    assert reply.status_code == 200
    assert "<h1>Task Tracker</h1>" in reply.text
