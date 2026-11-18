from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_200_and_status_ok():
    """REQ-014: The API answers GET /health with HTTP 200 and {"status": "ok"}."""
    reply = client.get("/health")
    assert reply.status_code == 200
    assert reply.json() == {"status": "ok"}


def test_health_method_not_allowed():
    reply = client.post("/health")
    assert reply.status_code == 405


def test_health_with_trailing_slash():
    reply = client.get("/health/")
    assert reply.status_code == 200
    assert reply.json() == {"status": "ok"}


def test_tasks_are_in_memory():
    """REQ-015: Tasks are kept in memory in version 1.0; a restart clears them."""
    from app.database import InMemoryDatabase
    from app.database import db as live_db
    # Create a task via the live database
    task = live_db.create_task(title="In-memory task", due_date_str=None)
    # The task should be accessible from the same db instance
    assert live_db.get_task(task.id) is not None
    # A new InMemoryDatabase instance simulates a restart: it is empty
    fresh_db = InMemoryDatabase()
    assert fresh_db.get_task(task.id) is None
