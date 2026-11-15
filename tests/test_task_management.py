from fastapi.testclient import TestClient

from app.main import app, _tasks

client = TestClient(app)


def setup_function():
    _tasks.clear()


def test_create_task_returns_201_with_task():
    reply = client.post("/tasks", json={"title": "Test task"})
    assert reply.status_code == 201
    body = reply.json()
    assert body["title"] == "Test task"
    assert body["status"] == "open"
    assert body["dueDate"] is None
    assert "id" in body


def test_create_task_with_due_date():
    reply = client.post("/tasks", json={"title": "Task with due", "dueDate": "2025-12-31"})
    assert reply.status_code == 201
    body = reply.json()
    assert body["dueDate"] == "2025-12-31"


def test_list_tasks_newest_first():
    client.post("/tasks", json={"title": "first"})
    client.post("/tasks", json={"title": "second"})
    reply = client.get("/tasks")
    assert reply.status_code == 200
    tasks = reply.json()
    assert len(tasks) == 2
    # newest first: sorted by id descending (uuid v4 lexicographic order roughly matches creation order)
    ids = [t["id"] for t in tasks]
    assert ids == sorted(ids, reverse=True)


def test_complete_task_returns_200_with_done_status():
    create = client.post("/tasks", json={"title": "do it"})
    task_id = create.json()["id"]
    reply = client.patch(f"/tasks/{task_id}/complete")
    assert reply.status_code == 200
    assert reply.json()["status"] == "done"
    assert reply.json()["title"] == "do it"


def test_complete_already_done_task_returns_409():
    create = client.post("/tasks", json={"title": "done already"})
    task_id = create.json()["id"]
    client.patch(f"/tasks/{task_id}/complete")
    reply = client.patch(f"/tasks/{task_id}/complete")
    assert reply.status_code == 409
    assert reply.json()["detail"] == "task is already done"


def test_complete_nonexistent_task_returns_404():
    reply = client.patch("/tasks/nonexistent/complete")
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"


def test_delete_task_returns_204():
    create = client.post("/tasks", json={"title": "delete me"})
    task_id = create.json()["id"]
    reply = client.delete(f"/tasks/{task_id}")
    assert reply.status_code == 204
    assert reply.text == ""


def test_deleted_task_no_longer_in_list():
    create = client.post("/tasks", json={"title": "gone"})
    task_id = create.json()["id"]
    client.delete(f"/tasks/{task_id}")
    reply = client.get("/tasks")
    assert len(reply.json()) == 0


def test_delete_nonexistent_task_returns_404():
    reply = client.delete("/tasks/nonexistent")
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"
