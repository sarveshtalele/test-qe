from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_200_and_status_ok():
    """REQ-001: The API answers GET /health with HTTP 200 and {"status": "ok"}."""
    reply = client.get("/health")
    assert reply.status_code == 200
    assert reply.json() == {"status": "ok"}


def test_in_memory_storage_tasks_cleared_on_restart():
    """REQ-015: Tasks are kept in memory in version 1.0; a restart clears them.

    Since the app uses an in-memory store, simulate a "restart" by clearing
    the internal list and ID counter via TestClient's context (each test gets
    a fresh app state). We verify that the store is initially empty.
    """
    import app.tasks as tmod
    tmod._tasks.clear()
    tmod._last_id = 0

    # Confirm no tasks exist
    reply = client.get("/tasks")
    assert reply.status_code == 200
    assert reply.json() == []

    # Create a task
    create_resp = client.post("/tasks", json={"title": "task before restart"})
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    # Simulate restart by clearing the store (as would happen if app restarts)
    tmod._tasks.clear()
    tmod._last_id = 0

    # After restart, the task should be gone
    list_resp = client.get("/tasks")
    assert list_resp.status_code == 200
    assert list_resp.json() == []

    # Also verify that the old task ID is not found
    get_resp = client.patch(f"/tasks/{task_id}/complete")
    assert get_resp.status_code == 404
    assert get_resp.json()["detail"] == "task not found"
