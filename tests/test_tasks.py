from __future__ import annotations

from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.store import store

client = TestClient(app)


def setup_function() -> None:
    # Fresh in-memory store before each test (REQ-016)
    store._tasks.clear()
    store._next_id = 1


def test_create_task_returns_201_with_task() -> None:
    # REQ-002, REQ-005
    payload = {"title": "Buy milk"}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["status"] == "open"
    assert isinstance(data["id"], int)
    assert "created_at" in data
    assert data["due_date"] is None


def test_create_task_with_due_date() -> None:
    # REQ-002, REQ-005
    payload = {"title": "Meeting", "due_date": "2025-06-15"}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Meeting"
    assert data["due_date"] == "2025-06-15"
    assert data["status"] == "open"


def test_create_task_title_blank_returns_422() -> None:
    # REQ-003: title after trimming less than 1 character
    payload = {"title": "   "}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, title must be 1 to 120 characters"


def test_create_task_title_too_long_returns_422() -> None:
    # REQ-003: title > 120 characters
    long_title = "a" * 121
    payload = {"title": long_title}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422
    detail = response.json()["detail"]
    # FastAPI returns an error detail list; Pydantic's Field validation raises a different error than the validator
    # Check for the min_length/max_length condition: it produces an error with 'msg' containing 'String should have at most 120 characters'
    assert any(
        "String should have at most 120 characters" in err.get("msg", "")
        for err in detail
    )


def test_create_task_title_empty_string_returns_422() -> None:
    # REQ-003: title empty after trim
    payload = {"title": ""}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422


def test_create_task_invalid_due_date_format_returns_422() -> None:
    # REQ-004
    payload = {"title": "Task", "due_date": "2025/06/15"}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422
    detail = response.json()["detail"]
    # The pattern validation on the Field rejects the wrong format with a msg like 'String should match pattern "^\\d{4}-\\d{2}-\\d{2}$"'
    assert any(
        "String should match pattern" in err.get("msg", "")
        for err in detail
    )


def test_list_tasks_returns_newest_first() -> None:
    # REQ-006
    client.post("/tasks", json={"title": "First"})
    client.post("/tasks", json={"title": "Second"})
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # newest first (Second created later)
    assert data[0]["title"] == "Second"
    assert data[1]["title"] == "First"


def test_list_tasks_filter_by_status_open() -> None:
    # REQ-007
    client.post("/tasks", json={"title": "Task A"})
    # mark one as done
    resp = client.post("/tasks", json={"title": "Task B"})
    task_id = resp.json()["id"]
    client.patch(f"/tasks/{task_id}/complete")
    response = client.get("/tasks?status=open")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Task A"


def test_list_tasks_filter_by_status_done() -> None:
    # REQ-007
    client.post("/tasks", json={"title": "Task A"})
    resp = client.post("/tasks", json={"title": "Task B"})
    task_id = resp.json()["id"]
    client.patch(f"/tasks/{task_id}/complete")
    response = client.get("/tasks?status=done")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Task B"


def test_list_tasks_invalid_status_returns_422() -> None:
    # REQ-008
    response = client.get("/tasks?status=invalid")
    assert response.status_code == 422
    assert response.json()["detail"] == "status must be open or done"


def test_complete_open_task_returns_200_with_status_done() -> None:
    # REQ-009
    resp = client.post("/tasks", json={"title": "Task"})
    task_id = resp.json()["id"]
    response = client.patch(f"/tasks/{task_id}/complete")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"
    assert data["id"] == task_id


def test_complete_already_done_task_returns_409() -> None:
    # REQ-010
    resp = client.post("/tasks", json={"title": "Task"})
    task_id = resp.json()["id"]
    client.patch(f"/tasks/{task_id}/complete")
    response = client.patch(f"/tasks/{task_id}/complete")
    assert response.status_code == 409
    assert response.json()["detail"] == "task is already done"


def test_complete_nonexistent_task_returns_404() -> None:
    # REQ-011
    response = client.patch("/tasks/9999/complete")
    assert response.status_code == 404
    assert response.json()["detail"] == "task not found"


def test_delete_task_returns_204_and_removes_from_list() -> None:
    # REQ-012
    resp = client.post("/tasks", json={"title": "Delete me"})
    task_id = resp.json()["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    # task no longer appears in list
    list_resp = client.get("/tasks")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 0


def test_delete_nonexistent_task_returns_404() -> None:
    # REQ-011
    response = client.delete("/tasks/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "task not found"


def test_tasks_are_in_memory_restart_clears() -> None:
    # REQ-016: verify store is fresh (setup_function clears it)
    resp = client.post("/tasks", json={"title": "Temp"})
    assert resp.status_code == 201
    # simulate restart by clearing store
    store._tasks.clear()
    store._next_id = 1
    list_resp = client.get("/tasks")
    assert list_resp.json() == []
