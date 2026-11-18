from fastapi.testclient import TestClient

from app.main import app
from app.store import tasks
import app.store as store_module

client = TestClient(app)


def setup_function():
    import app.store as store_module
    tasks.clear()
    store_module._next_id = 1


def test_create_task_minimal():
    resp = client.post("/tasks", json={"title": "Buy milk"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == 1
    assert data["title"] == "Buy milk"
    assert data["due_date"] is None
    assert data["status"] == "open"


def test_create_task_with_due_date():
    resp = client.post("/tasks", json={"title": "Submit report", "due_date": "2025-12-31"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == 1
    assert data["due_date"] == "2025-12-31"
    assert data["status"] == "open"


def test_create_task_title_too_long():
    title = "a" * 121
    resp = client.post("/tasks", json={"title": title})
    assert resp.status_code == 422
    assert any(
        err["msg"] == "String should have at most 120 characters"
        or err["msg"] == "title must be 1 to 120 characters"
        for err in resp.json()["detail"]
    )


def test_create_task_title_empty():
    resp = client.post("/tasks", json={"title": ""})
    assert resp.status_code == 422
    assert any(
        err["msg"] == "String should have at least 1 character"
        or err["msg"] == "title must be 1 to 120 characters"
        for err in resp.json()["detail"]
    )


def test_create_task_title_whitespace_only():
    resp = client.post("/tasks", json={"title": "   "})
    assert resp.status_code == 422
    assert resp.json()["detail"] == "title must be 1 to 120 characters"


def test_create_task_invalid_due_date():
    resp = client.post("/tasks", json={"title": "Task", "due_date": "31-12-2025"})
    assert resp.status_code == 422
    assert any(
        "due_date must be YYYY-MM-DD" in err["msg"]
        for err in resp.json()["detail"]
    )


def test_list_tasks_newest_first():
    client.post("/tasks", json={"title": "First"})
    client.post("/tasks", json={"title": "Second"})
    client.post("/tasks", json={"title": "Third"})
    resp = client.get("/tasks")
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.json()]
    assert titles == ["Third", "Second", "First"]


def test_list_tasks_filter_open():
    client.post("/tasks", json={"title": "Task A"})
    client.post("/tasks", json={"title": "Task B"})
    client.patch("/tasks/1/complete")
    resp = client.get("/tasks?status=open")
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.json()]
    assert titles == ["Task B"]


def test_list_tasks_filter_done():
    client.post("/tasks", json={"title": "Task A"})
    client.post("/tasks", json={"title": "Task B"})
    client.patch("/tasks/1/complete")
    resp = client.get("/tasks?status=done")
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.json()]
    assert titles == ["Task A"]


def test_list_tasks_invalid_status():
    resp = client.get("/tasks?status=invalid")
    assert resp.status_code == 422
    assert resp.json()["detail"] == "status must be open or done"


def test_complete_open_task():
    client.post("/tasks", json={"title": "My task"})
    resp = client.patch("/tasks/1/complete")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "done"


def test_complete_already_done_task():
    client.post("/tasks", json={"title": "My task"})
    client.patch("/tasks/1/complete")
    resp = client.patch("/tasks/1/complete")
    assert resp.status_code == 409
    assert resp.json()["detail"] == "task is already done"


def test_complete_nonexistent_task():
    resp = client.patch("/tasks/999/complete")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "task not found"


def test_delete_task():
    client.post("/tasks", json={"title": "Delete me"})
    resp = client.delete("/tasks/1")
    assert resp.status_code == 204
    assert resp.text == ""
    # task no longer appears in list
    list_resp = client.get("/tasks")
    assert list_resp.json() == []


def test_in_memory_clears_on_restart():
    """Tasks are kept in memory in version 1.0; a restart clears them (REQ-015)."""
    client.post("/tasks", json={"title": "Temp"})
    tasks.clear()
    store_module._next_id = 1
    resp = client.get("/tasks")
    assert resp.status_code == 200
    assert resp.json() == []


def test_delete_nonexistent_task():
    resp = client.delete("/tasks/999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "task not found"
