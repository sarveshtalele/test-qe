from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_task():
    reply = client.post("/tasks", json={"title": "  Buy milk  "})
    assert reply.status_code == 201
    data = reply.json()
    assert data["title"] == "Buy milk"
    assert data["due_date"] is None
    assert data["status"] == "open"
    assert isinstance(data["id"], int)


def test_create_task_with_due_date():
    reply = client.post("/tasks", json={"title": "Meeting", "due_date": "2025-12-31"})
    assert reply.status_code == 201
    data = reply.json()
    assert data["title"] == "Meeting"
    assert data["due_date"] == "2025-12-31"
    assert data["status"] == "open"


def test_create_task_title_too_short():
    reply = client.post("/tasks", json={"title": "   "})
    assert reply.status_code == 422
    assert reply.json()["detail"][0]["msg"] == "Value error, title must be 1 to 120 characters"


def test_create_task_title_too_long():
    reply = client.post("/tasks", json={"title": "x" * 121})
    assert reply.status_code == 422
    assert reply.json()["detail"][0]["msg"] == "Value error, title must be 1 to 120 characters"


def test_create_task_invalid_due_date():
    reply = client.post("/tasks", json={"title": "Task", "due_date": "31-12-2025"})
    assert reply.status_code == 422
    assert reply.json()["detail"][0]["msg"] == "Value error, due_date must be YYYY-MM-DD"


def test_list_tasks_newest_first():
    client.post("/tasks", json={"title": "First"})
    client.post("/tasks", json={"title": "Second"})
    reply = client.get("/tasks")
    assert reply.status_code == 200
    data = reply.json()
    assert len(data) >= 2
    # newest first means higher id first
    assert data[0]["id"] > data[1]["id"]


def test_list_tasks_filter_open():
    # create two tasks, complete one
    r1 = client.post("/tasks", json={"title": "OpenTask"})
    tid = r1.json()["id"]
    client.post("/tasks", json={"title": "DoneTask"})
    client.put(f"/tasks/{tid}/complete")
    reply = client.get("/tasks?status=open")
    assert reply.status_code == 200
    tasks = reply.json()
    for t in tasks:
        assert t["status"] == "open"


def test_list_tasks_filter_done():
    r1 = client.post("/tasks", json={"title": "WillBeDone"})
    tid = r1.json()["id"]
    client.put(f"/tasks/{tid}/complete")
    reply = client.get("/tasks?status=done")
    assert reply.status_code == 200
    tasks = reply.json()
    for t in tasks:
        assert t["status"] == "done"


def test_list_tasks_invalid_status():
    reply = client.get("/tasks?status=unknown")
    assert reply.status_code == 422
    assert reply.json()["detail"] == "status must be open or done"


def test_complete_task():
    r = client.post("/tasks", json={"title": "Do this"})
    tid = r.json()["id"]
    reply = client.put(f"/tasks/{tid}/complete")
    assert reply.status_code == 200
    data = reply.json()
    assert data["status"] == "done"


def test_complete_already_done_task():
    r = client.post("/tasks", json={"title": "Already done"})
    tid = r.json()["id"]
    client.put(f"/tasks/{tid}/complete")
    reply = client.put(f"/tasks/{tid}/complete")
    assert reply.status_code == 409
    assert reply.json()["detail"] == "task is already done"


def test_complete_non_existent_task():
    reply = client.put("/tasks/9999/complete")
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"


def test_delete_task():
    r = client.post("/tasks", json={"title": "Delete me"})
    tid = r.json()["id"]
    reply = client.delete(f"/tasks/{tid}")
    assert reply.status_code == 204
    assert reply.text == ""
    # verify it no longer appears in list
    list_reply = client.get("/tasks")
    ids = [t["id"] for t in list_reply.json()]
    assert tid not in ids


def test_delete_non_existent_task():
    reply = client.delete("/tasks/9999")
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"
