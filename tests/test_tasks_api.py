from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_task_returns_201():
    payload = {"title": "Write report"}
    reply = client.post("/tasks", json=payload)
    assert reply.status_code == 201
    data = reply.json()
    assert data["title"] == "Write report"
    assert data["status"] == "open"
    assert data["id"] > 0
    assert data["due_date"] is None


def test_create_task_with_due_date():
    payload = {"title": "Meeting", "due_date": "2025-04-15"}
    reply = client.post("/tasks", json=payload)
    assert reply.status_code == 201
    data = reply.json()
    assert data["due_date"] == "2025-04-15"


def test_list_tasks_newest_first():
    # Create two tasks with known ids
    r1 = client.post("/tasks", json={"title": "first"})
    r2 = client.post("/tasks", json={"title": "second"})
    id1 = r1.json()["id"]
    id2 = r2.json()["id"]
    reply = client.get("/tasks")
    assert reply.status_code == 200
    tasks = reply.json()
    # Newest (largest id) first
    assert tasks[0]["id"] == id2
    assert tasks[1]["id"] == id1


def test_list_tasks_filter_open():
    # create an open task (status stays open when created)
    r = client.post("/tasks", json={"title": "open task"})
    open_id = r.json()["id"]
    reply = client.get("/tasks?status=open")
    assert reply.status_code == 200
    tasks = reply.json()
    assert all(t["status"] == "open" for t in tasks)
    assert any(t["id"] == open_id for t in tasks)


def test_list_tasks_filter_done():
    # create a task and complete it so it appears in done list
    r = client.post("/tasks", json={"title": "done task"})
    task_id = r.json()["id"]
    client.patch(f"/tasks/{task_id}/complete")
    reply = client.get("/tasks?status=done")
    assert reply.status_code == 200
    tasks = reply.json()
    assert all(t["status"] == "done" for t in tasks)
    assert any(t["id"] == task_id for t in tasks)


def test_list_tasks_invalid_status_422():
    reply = client.get("/tasks?status=invalid")
    assert reply.status_code == 422
    assert reply.json()["detail"] == "status must be open or done"


def test_complete_open_task_returns_200():
    r = client.post("/tasks", json={"title": "do me"})
    task_id = r.json()["id"]
    reply = client.patch(f"/tasks/{task_id}/complete")
    assert reply.status_code == 200
    assert reply.json()["status"] == "done"


def test_complete_done_task_409():
    r = client.post("/tasks", json={"title": "already done"})
    task_id = r.json()["id"]
    client.patch(f"/tasks/{task_id}/complete")
    reply = client.patch(f"/tasks/{task_id}/complete")
    assert reply.status_code == 409
    assert reply.json()["detail"] == "task is already done"


def test_complete_missing_task_404():
    reply = client.patch("/tasks/99999/complete")
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"


def test_delete_task_returns_204():
    r = client.post("/tasks", json={"title": "delete me"})
    task_id = r.json()["id"]
    reply = client.delete(f"/tasks/{task_id}")
    assert reply.status_code == 204
    assert reply.text == ""


def test_delete_missing_task_404():
    reply = client.delete("/tasks/99999")
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"


def test_deleted_task_does_not_appear():
    r = client.post("/tasks", json={"title": "gone"})
    task_id = r.json()["id"]
    client.delete(f"/tasks/{task_id}")
    reply = client.get("/tasks")
    ids = [t["id"] for t in reply.json()]
    assert task_id not in ids
