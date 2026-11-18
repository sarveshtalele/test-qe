from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_task_minimal():
    # REQ-001: create task with title
    reply = client.post("/tasks", json={"title": "  Buy milk  "})
    # REQ-002: title trimmed
    data = reply.json()
    assert data["title"] == "Buy milk"
    # REQ-004: status open, id assigned, HTTP 201
    assert reply.status_code == 201
    assert data["status"] == "open"
    assert isinstance(data["id"], int)
    assert data["id"] > 0


def test_create_task_with_due_date():
    # REQ-001, REQ-003
    reply = client.post("/tasks", json={"title": "Finish report", "due_date": "2025-06-01"})
    assert reply.status_code == 201
    data = reply.json()
    assert data["due_date"] == "2025-06-01"
    assert data["status"] == "open"


def test_create_task_title_too_short():
    # REQ-002: empty string after trim -> 422
    reply = client.post("/tasks", json={"title": "   "})
    assert reply.status_code == 422
    # Our custom validator runs because pydantic doesn't reject whitespace-only as too short
    assert "title must be 1 to 120 characters" in reply.text


def test_create_task_title_too_long():
    # REQ-002: title with 121 characters after trim -> 422 from our validator
    # Use a title that's 121 chars after providing it as-is
    reply = client.post("/tasks", json={"title": "a" * 121})
    assert reply.status_code == 422
    assert "title must be 1 to 120 characters" in reply.text


def test_create_task_invalid_due_date():
    # REQ-003
    reply = client.post("/tasks", json={"title": "Task", "due_date": "01-06-2025"})
    assert reply.status_code == 422
    # The error message may come from pydantic with the text we specified
    detail = reply.json()["detail"]
    # pydantic wraps it in a list; find the message with our text
    msg = " "
    if isinstance(detail, list):
        for err in detail:
            if "due_date must be YYYY-MM-DD" in str(err.get("msg", "")):
                msg = err["msg"]
                break
    else:
        msg = detail.get("msg", "")
    assert "due_date must be YYYY-MM-DD" in msg


def test_list_tasks_newest_first():
    # REQ-005
    client.post("/tasks", json={"title": "A"})
    client.post("/tasks", json={"title": "B"})
    reply = client.get("/tasks")
    assert reply.status_code == 200
    data = reply.json()
    assert len(data) >= 2
    assert data[0]["id"] > data[1]["id"]


def test_list_tasks_filter_open():
    # REQ-006
    client.post("/tasks", json={"title": "Filter open test"})
    reply = client.get("/tasks?status=open")
    assert reply.status_code == 200
    for t in reply.json():
        assert t["status"] == "open"


def test_list_tasks_filter_done():
    # REQ-006
    # create a task and mark it done
    created = client.post("/tasks", json={"title": "Filter done test"}).json()
    client.post(f"/tasks/{created['id']}/done")
    reply = client.get("/tasks?status=done")
    assert reply.status_code == 200
    for t in reply.json():
        assert t["status"] == "done"


def test_list_tasks_invalid_status():
    # REQ-006
    reply = client.get("/tasks?status=invalid")
    assert reply.status_code == 422
    assert "status must be open or done" in reply.text


def test_mark_task_done():
    # REQ-007
    created = client.post("/tasks", json={"title": "Mark done"}).json()
    reply = client.post(f"/tasks/{created['id']}/done")
    assert reply.status_code == 200
    data = reply.json()
    assert data["status"] == "done"
    assert data["id"] == created["id"]


def test_mark_already_done_task():
    # REQ-008
    created = client.post("/tasks", json={"title": "Already done"}).json()
    client.post(f"/tasks/{created['id']}/done")
    reply = client.post(f"/tasks/{created['id']}/done")
    assert reply.status_code == 409
    assert "task is already done" in reply.text


def test_mark_done_not_found():
    # REQ-009
    reply = client.post("/tasks/99999/done")
    assert reply.status_code == 404
    assert "task not found" in reply.text


def test_delete_task():
    # REQ-010
    created = client.post("/tasks", json={"title": "Delete me"}).json()
    reply = client.delete(f"/tasks/{created['id']}")
    assert reply.status_code == 204
    # verify it no longer appears in list
    reply_list = client.get("/tasks")
    ids = [t["id"] for t in reply_list.json()]
    assert created["id"] not in ids


def test_delete_task_not_found():
    # REQ-009
    reply = client.delete("/tasks/99999")
    assert reply.status_code == 404
    assert "task not found" in reply.text
