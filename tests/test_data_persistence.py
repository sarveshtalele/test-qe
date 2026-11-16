from fastapi.testclient import TestClient

from app.main import app
import app.routers.tasks as tasks_module

client = TestClient(app)


def reset_storage() -> None:
    """Simulate a restart by clearing the in-memory storage."""
    tasks_module._tasks_db.clear()
    tasks_module._next_id = 1


def test_tasks_cleared_on_restart() -> None:
    """REQ-014: Tasks are kept in memory only; a restart clears all tasks."""
    # Create a task
    r = client.post("/tasks", json={"title": "persist?"})
    assert r.status_code == 201
    task_id = r.json()["id"]
    # Verify it exists
    reply = client.get("/tasks")
    assert any(t["id"] == task_id for t in reply.json())

    # Simulate restart
    reset_storage()

    # Verify task list is empty
    reply = client.get("/tasks")
    assert reply.status_code == 200
    assert reply.json() == []
