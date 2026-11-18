from starlette.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_is_ok():
    """REQ-014: GET /health returns 200 and {"status": "ok"}."""
    reply = client.get("/health")
    assert reply.status_code == 200
    assert reply.json() == {"status": "ok"}


def test_page_is_served():
    reply = client.get("/")
    assert reply.status_code == 200
    assert "<h1>Task Tracker</h1>" in reply.text


def test_health_is_not_cached():
    """REQ-014: Ensure health endpoint is always reachable and returns correct format multiple times."""
    for _ in range(3):
        reply = client.get("/health")
        assert reply.status_code == 200
        assert reply.json() == {"status": "ok"}
