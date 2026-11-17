import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import _tasks

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    _tasks.clear()


def test_create_task():
    reply = client.post("/tasks", json={"title": "Buy milk"})
    assert reply.status_code == 201
    data = reply.json()
    assert data["title"] == "Buy milk"
    assert data["due_date"] is None
    assert data["status"] == "open"


def test_create_task_with_due_date():
    reply = client.post("/tasks", json={"title": "Submit report", "due_date": "2025-12-31"})
    assert reply.status_code == 201
    data = reply.json()
    assert data["title"] == "Submit report"
    assert data["due_date"] == "2025-12-31"


def test_list_tasks_newest_first():
    client.post("/tasks", json={"title": "First"})
    client.post("/tasks", json={"title": "Second"})
    reply = client.get("/tasks")
    assert reply.status_code == 200
    data = reply.json()
    assert len(data) == 2
    # Second was created after First, so it should appear first
    assert data[0]["title"] == "Second"
    assert data[1]["title"] == "First"


def test_mark_task_done():
    create_resp = client.post("/tasks", json={"title": "Clean room"})
    task_id = create_resp.json()["id"]
    reply = client.put(f"/tasks/{task_id}/done")
    assert reply.status_code == 200
    data = reply.json()
    assert data["status"] == "done"


def test_mark_already_done_task_returns_409():
    create_resp = client.post("/tasks", json={"title": "Already done"})
    task_id = create_resp.json()["id"]
    client.put(f"/tasks/{task_id}/done")
    reply = client.put(f"/tasks/{task_id}/done")
    assert reply.status_code == 409
    assert reply.json()["detail"] == "task is already done"


def test_mark_nonexistent_task_returns_404():
    reply = client.put("/tasks/nonexistent-id/done")
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"


def test_delete_task():
    create_resp = client.post("/tasks", json={"title": "Delete me"})
    task_id = create_resp.json()["id"]
    reply = client.delete(f"/tasks/{task_id}")
    assert reply.status_code == 204
    assert reply.text == ""
    # Task should no longer appear in the list
    list_resp = client.get("/tasks")
    assert len(list_resp.json()) == 0


def test_delete_nonexistent_task_returns_404():
    reply = client.delete("/tasks/nonexistent-id")
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"


def test_health_still_works():
    reply = client.get("/health")
    assert reply.status_code == 200
    assert reply.json() == {"status": "ok"}
