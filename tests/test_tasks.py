import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def tc():
    # Reset store for each test
    import app.tasks
    from app.task_store import TaskStore
    app.tasks.store = TaskStore()
    return TestClient(app)


def test_create_task_minimal(tc):
    # REQ-001, REQ-004: create with just title -> status open, 201
    resp = tc.post("/tasks", json={"title": "Do something"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Do something"
    assert data["status"] == "open"
    assert isinstance(data["id"], int)
    assert data["due_date"] is None


def test_create_task_with_due_date(tc):
    # REQ-001, REQ-003: with due date YYYY-MM-DD
    resp = tc.post("/tasks", json={"title": "Buy milk", "due_date": "2025-12-31"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["due_date"] == "2025-12-31"


def test_create_task_trim_title(tc):
    # REQ-002: title is trimmed
    resp = tc.post("/tasks", json={"title": "   spaced   "})
    assert resp.status_code == 201
    assert resp.json()["title"] == "spaced"


def test_create_task_title_too_long(tc):
    # REQ-002: title >120 -> 422
    long = "x" * 121
    resp = tc.post("/tasks", json={"title": long})
    assert resp.status_code == 422
    detail = resp.json().get("detail", "")
    # may be string or list of errors; check the message appears
    if isinstance(detail, list):
        detail = " ".join(e.get("msg", "") for e in detail)
    assert "title must be 1 to 120 characters" in detail


def test_create_task_title_empty_after_trim(tc):
    # REQ-002: only spaces -> 422
    resp = tc.post("/tasks", json={"title": "   "})
    assert resp.status_code == 422
    detail = resp.json().get("detail", "")
    if isinstance(detail, list):
        detail = " ".join(e.get("msg", "") for e in detail)
    assert "title must be 1 to 120 characters" in detail


def test_create_task_invalid_due_date_format(tc):
    # REQ-003: wrong format -> 422
    resp = tc.post("/tasks", json={"title": "Test", "due_date": "31-12-2025"})
    assert resp.status_code == 422
    data = resp.json()
    detail = data.get("detail", "")
    if isinstance(detail, list):
        detail = " ".join(e.get("msg", "") for e in detail)
    assert "due_date must be YYYY-MM-DD" in detail


def test_list_tasks_newest_first(tc):
    # REQ-005: newest first
    tc.post("/tasks", json={"title": "First"})
    tc.post("/tasks", json={"title": "Second"})
    resp = tc.get("/tasks")
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.json()]
    assert titles == ["Second", "First"]


def test_list_tasks_filter_by_status(tc):
    # REQ-006: filter open/done
    tc.post("/tasks", json={"title": "Open task"})
    resp = tc.get("/tasks?status=open")
    assert resp.status_code == 200
    for t in resp.json():
        assert t["status"] == "open"
    # no tasks are done, so empty
    resp = tc.get("/tasks?status=done")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_tasks_filter_invalid_status(tc):
    # REQ-006: invalid status -> 422
    resp = tc.get("/tasks?status=unknown")
    assert resp.status_code == 422
    assert resp.json()["detail"] == "status must be open or done"


def test_complete_task(tc):
    # REQ-007: complete an open task -> 200, status done
    create = tc.post("/tasks", json={"title": "Task to finish"})
    tid = create.json()["id"]
    resp = tc.patch(f"/tasks/{tid}/complete")
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"


def test_complete_already_done(tc):
    # REQ-008: complete twice -> 409
    create = tc.post("/tasks", json={"title": "Already done"})
    tid = create.json()["id"]
    tc.patch(f"/tasks/{tid}/complete")
    resp = tc.patch(f"/tasks/{tid}/complete")
    assert resp.status_code == 409
    assert resp.json()["detail"] == "task is already done"


def test_complete_not_found(tc):
    # REQ-009: complete nonexistent -> 404
    resp = tc.patch("/tasks/9999/complete")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "task not found"


def test_delete_task(tc):
    # REQ-010: delete -> 204, no longer in list
    create = tc.post("/tasks", json={"title": "Delete me"})
    tid = create.json()["id"]
    resp = tc.delete(f"/tasks/{tid}")
    assert resp.status_code == 204
    assert resp.text == ""
    # does not appear in list
    resp = tc.get("/tasks")
    ids = [t["id"] for t in resp.json()]
    assert tid not in ids


def test_delete_not_found(tc):
    # REQ-009: delete nonexistent -> 404
    resp = tc.delete("/tasks/9999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "task not found"
