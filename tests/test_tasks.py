from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_task():
    # REQ-002: A team member creates a task with a title and an optional due date.
    reply = client.post("/tasks", json={"title": "Test task", "due_date": "2025-01-01"})
    assert reply.status_code == 201
    data = reply.json()
    assert data["title"] == "Test task"
    assert data["due_date"] == "2025-01-01"
    assert data["status"] == "open"
    assert "id" in data


def test_create_task_without_due_date():
    reply = client.post("/tasks", json={"title": "No due date"})
    assert reply.status_code == 201
    assert reply.json()["due_date"] is None


def test_list_tasks_newest_first():
    # Clean up previous tasks by resetting the app state (only for testing)
    import app.tasks as tmod
    tmod._tasks.clear()
    tmod._last_id = 0

    t1 = client.post("/tasks", json={"title": "first"}).json()
    t2 = client.post("/tasks", json={"title": "second"}).json()

    reply = client.get("/tasks")
    assert reply.status_code == 200
    tasks = reply.json()
    # newest first means id descending
    assert len(tasks) >= 2
    # the last created must appear first
    assert tasks[0]["id"] == t2["id"]
    assert tasks[1]["id"] == t1["id"]


def test_complete_task():
    import app.tasks as tmod
    tmod._tasks.clear()
    tmod._last_id = 0

    created = client.post("/tasks", json={"title": "do me"}).json()
    tid = created["id"]
    reply = client.patch(f"/tasks/{tid}/complete")
    # REQ-008: API answers HTTP 200 with the task, now with the status 'done'
    assert reply.status_code == 200
    assert reply.json()["status"] == "done"


def test_complete_already_done():
    import app.tasks as tmod
    tmod._tasks.clear()
    tmod._last_id = 0

    created = client.post("/tasks", json={"title": "done already"}).json()
    tid = created["id"]
    client.patch(f"/tasks/{tid}/complete")
    # second completion
    reply = client.patch(f"/tasks/{tid}/complete")
    # REQ-009: HTTP 409 with message 'task is already done'
    assert reply.status_code == 409
    assert reply.json()["detail"] == "task is already done"


def test_complete_not_found():
    reply = client.patch("/tasks/99999/complete")
    # REQ-010: HTTP 404 with message 'task not found'
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"


def test_delete_task():
    import app.tasks as tmod
    tmod._tasks.clear()
    tmod._last_id = 0

    created = client.post("/tasks", json={"title": "delete me"}).json()
    tid = created["id"]
    # REQ-011: HTTP 204 with no body
    reply = client.delete(f"/tasks/{tid}")
    assert reply.status_code == 204
    assert reply.text == ""
    # task no longer in list
    tasks = client.get("/tasks").json()
    assert all(t["id"] != tid for t in tasks)


def test_delete_not_found():
    reply = client.delete("/tasks/99999")
    # REQ-010: HTTP 404 with message 'task not found'
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"
