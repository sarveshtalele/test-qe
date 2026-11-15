from fastapi.testclient import TestClient

from app.main import app
from app.tasks import store

client = TestClient(app)


def setup_function():
    store._counter = 0
    store._tasks.clear()


def test_create_task():
    reply = client.post("/tasks", json={"title": "My task"})
    assert reply.status_code == 200
    data = reply.json()
    assert data["title"] == "My task"
    assert data["status"] == "open"
    assert data["due_date"] is None
    assert "id" in data
    assert "created_at" in data


def test_create_task_with_due_date():
    reply = client.post("/tasks", json={"title": "With due", "due_date": "2025-12-31"})
    assert reply.status_code == 200
    data = reply.json()
    assert data["due_date"] == "2025-12-31"


def test_list_tasks_newest_first():
    client.post("/tasks", json={"title": "first"})
    client.post("/tasks", json={"title": "second"})
    reply = client.get("/tasks")
    assert reply.status_code == 200
    tasks = reply.json()
    assert len(tasks) == 2
    assert tasks[0]["title"] == "second"
    assert tasks[1]["title"] == "first"


def test_complete_task():
    create = client.post("/tasks", json={"title": "do it"})
    task_id = create.json()["id"]
    reply = client.patch(f"/tasks/{task_id}/complete")
    assert reply.status_code == 200
    data = reply.json()
    assert data["status"] == "done"


def test_complete_already_done_returns_409():
    create = client.post("/tasks", json={"title": "twice"})
    task_id = create.json()["id"]
    client.patch(f"/tasks/{task_id}/complete")
    reply = client.patch(f"/tasks/{task_id}/complete")
    assert reply.status_code == 409
    assert reply.json()["detail"] == "task is already done"


def test_complete_nonexistent_returns_404():
    reply = client.patch("/tasks/999/complete")
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"


def test_delete_task():
    create = client.post("/tasks", json={"title": "delete me"})
    task_id = create.json()["id"]
    reply = client.delete(f"/tasks/{task_id}")
    assert reply.status_code == 204
    assert reply.content == b""
    # verify task is gone
    list_reply = client.get("/tasks")
    assert len(list_reply.json()) == 0


def test_delete_nonexistent_returns_404():
    reply = client.delete("/tasks/999")
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"
