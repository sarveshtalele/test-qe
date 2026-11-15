from datetime import date, datetime
from fastapi.testclient import TestClient

from app.main import app
from app.routers.tasks import _tasks

client = TestClient(app)


def setup_function():
    _tasks.clear()


def test_create_task():
    reply = client.post("/tasks", json={"title": "Buy milk"})
    assert reply.status_code == 201
    data = reply.json()
    assert data["title"] == "Buy milk"
    assert data["status"] == "open"
    assert "id" in data
    assert "created_at" in data


def test_create_task_with_due_date():
    reply = client.post(
        "/tasks", json={"title": "Submit report", "due_date": "2026-12-31"}
    )
    assert reply.status_code == 201
    data = reply.json()
    assert data["due_date"] == "2026-12-31"


def test_list_tasks_newest_first():
    client.post("/tasks", json={"title": "Task A"})
    client.post("/tasks", json={"title": "Task B"})
    reply = client.get("/tasks")
    assert reply.status_code == 200
    tasks = reply.json()
    assert len(tasks) == 2
    # Task B was created second, should appear first
    assert tasks[0]["title"] == "Task B"
    assert tasks[1]["title"] == "Task A"


def test_complete_task_returns_200_and_done_status():
    create_reply = client.post("/tasks", json={"title": "Test"})
    task_id = create_reply.json()["id"]
    reply = client.patch(f"/tasks/{task_id}/complete")
    assert reply.status_code == 200
    assert reply.json()["status"] == "done"


def test_complete_already_done_task_returns_409():
    create_reply = client.post("/tasks", json={"title": "Test"})
    task_id = create_reply.json()["id"]
    client.patch(f"/tasks/{task_id}/complete")  # first completion
    reply = client.patch(f"/tasks/{task_id}/complete")
    assert reply.status_code == 409
    assert reply.json()["detail"] == "task is already done"


def test_complete_nonexistent_task_returns_404():
    reply = client.patch("/tasks/nonexistent/complete")
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"


def test_delete_task_returns_204_and_removes_task():
    create_reply = client.post("/tasks", json={"title": "Delete me"})
    task_id = create_reply.json()["id"]
    reply = client.delete(f"/tasks/{task_id}")
    assert reply.status_code == 204
    assert reply.content == b""
    # verify it no longer appears in list
    list_reply = client.get("/tasks")
    ids = [t["id"] for t in list_reply.json()]
    assert task_id not in ids


def test_delete_nonexistent_task_returns_404():
    reply = client.delete("/tasks/nonexistent")
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"
