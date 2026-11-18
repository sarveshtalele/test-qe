import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    # Reset store for each test
    from app.tasks import store as tasks_store
    from app.task_store import TaskStore
    tasks_store = TaskStore()
    # hack: reassign the module-level store
    import app.tasks
    app.tasks.store = TaskStore()
    return TestClient(app)


def test_create_task_minimal(client):
    # REQ-001, REQ-004: create with just title -> status open, 201
    resp = client.post("/tasks", json={"title": "Do something"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Do something"
    assert data["status"] == "open"
    assert isinstance(data["id"], int)
    assert data["due_date"] is None


def test_create_task_with_due_date():
    # REQ-001, REQ-003: with due date YYYY-MM-DD
    resp = client.post("/tasks", json={"title": "Buy milk", "due_date": "2025-12-31"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["due_date"] == "2025-12-31"


def test_create_task_trim_title():
    # REQ-002: title is trimmed
    resp = client.post("/tasks", json={"title": "   spaced   "})
    assert resp.status_code == 201
    assert resp.json()["title"] == "spaced"


def test_create_task_title_too_long():
    # REQ-002: title >120 -> 422
    long = "x" * 121
    resp = client.post("/tasks", json={"title": long})
    assert resp.status_code == 422
    detail = resp.json().get("detail", "")
    # may be string or list of errors; check the message appears
    if isinstance(detail, list):
        detail = " ".join(e.get("msg", "") for e in detail)
    assert "title must be 1 to 120 characters" in detail


def test_create_task_title_empty_after_trim():
    # REQ-002: only spaces -> 422
    resp = client.post("/tasks", json={"title": "   "})
    assert resp.status_code == 422
    detail = resp.json().get("detail", "")
    if isinstance(detail, list):
        detail = " ".join(e.get("msg", "") for e in detail)
    assert "title must be 1 to 120 characters" in detail


def test_create_task_invalid_due_date_format():
    # REQ-003: wrong format -> 422
    resp = client.post("/tasks", json={"title": "Test", "due_date": "31-12-2025"})
    assert resp.status_code == 422
    data = resp.json()
    detail = data.get("detail", "")
    if isinstance(detail, list):
        detail = " ".join(e.get("msg", "") for e in detail)
    assert "due_date must be YYYY-MM-DD" in detail


def test_list_tasks_newest_first():
    # REQ-005: newest first
    client.post("/tasks", json={"title": "First"})
    client.post("/tasks", json={"title": "Second"})
    resp = client.get("/tasks")
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.json()]
    assert titles == ["Second", "First"]


def test_list_tasks_filter_by_status():
    # REQ-006: filter open/done
    client.post("/tasks", json={"title": "Open task"})
    resp = client.get("/tasks?status=open")
    assert resp.status_code == 200
    for t in resp.json():
        assert t["status"] == "open"
    # no tasks are done, so empty
    resp = client.get("/tasks?status=done")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_tasks_filter_invalid_status():
    # REQ-006: invalid status -> 422
    resp = client.get("/tasks?status=unknown")
    assert resp.status_code == 422
    assert resp.json()["detail"] == "status must be open or done"


def test_complete_task():
    # REQ-007: complete an open task -> 200, status done
    create = client.post("/tasks", json={"title": "Task to finish"})
    tid = create.json()["id"]
    resp = client.patch(f"/tasks/{tid}/complete")
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"


def test_complete_already_done():
    # REQ-008: complete twice -> 409
    create = client.post("/tasks", json={"title": "Already done"})
    tid = create.json()["id"]
    client.patch(f"/tasks/{tid}/complete")
    resp = client.patch(f"/tasks/{tid}/complete")
    assert resp.status_code == 409
    assert resp.json()["detail"] == "task is already done"


def test_complete_not_found():
    # REQ-009: complete nonexistent -> 404
    resp = client.patch("/tasks/9999/complete")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "task not found"


def test_delete_task():
    # REQ-010: delete -> 204, no longer in list
    create = client.post("/tasks", json={"title": "Delete me"})
    tid = create.json()["id"]
    resp = client.delete(f"/tasks/{tid}")
    assert resp.status_code == 204
    assert resp.text == ""
    # does not appear in list
    resp = client.get("/tasks")
    ids = [t["id"] for t in resp.json()]
    assert tid not in ids


def test_delete_not_found():
    # REQ-009: delete nonexistent -> 404
    resp = client.delete("/tasks/9999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "task not found"
