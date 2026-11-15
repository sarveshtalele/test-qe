from fastapi.testclient import TestClient

from app.main import app, _tasks

client = TestClient(app)


def setup_function():
    _tasks.clear()


def test_in_memory_storage_clears_on_restart():
    """REQ-015: Tasks are kept in memory in version 1.0; a restart clears them."""
    # Simulate a restart by clearing the in-memory store
    client.post("/tasks", json={"title": "Task before restart"})
    assert len(_tasks) == 1
    _tasks.clear()
    assert len(_tasks) == 0
    # After restart, the previous task is gone
    reply = client.get("/tasks")
    assert reply.status_code == 200
    assert reply.json() == []


def test_health_endpoint_returns_correct_response():
    """REQ-001: The API answers GET /health with HTTP 200 and {"status": "ok"}."""
    reply = client.get("/health")
    assert reply.status_code == 200
    assert reply.json() == {"status": "ok"}
