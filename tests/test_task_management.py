from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_task_with_only_title():
    resp = client.post("/tasks", params={"title": "Buy groceries"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Buy groceries"
    assert data["status"] == "open"
    assert "id" in data
    assert "createdAt" in data
    assert data["dueDate"] is None


def test_create_task_with_due_date():
    resp = client.post("/tasks", params={"title": "Meeting", "dueDate": "2025-12-31"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Meeting"
    assert data["dueDate"] == "2025-12-31"


def test_create_task_title_empty_after_trim():
    resp = client.post("/tasks", params={"title": "   "})
    assert resp.status_code == 422
    assert resp.json()["detail"] == "title must be 1 to 120 characters"


def test_create_task_title_too_long():
    resp = client.post("/tasks", params={"title": "a" * 121})
    assert resp.status_code == 422
    assert resp.json()["detail"] == "title must be 1 to 120 characters"


def test_list_tasks_newest_first():
    # Clear store by creating a new client that uses a fresh store? Here we rely on known state (test isolation).
    # We'll create two tasks and verify order.
    resp1 = client.post("/tasks", params={"title": "First"})
    resp2 = client.post("/tasks", params={"title": "Second"})
    resp = client.get("/tasks")
    assert resp.status_code == 200
    data = resp.json()
    # Second was created after First
    assert data[0]["title"] == "Second"
    assert data[1]["title"] == "First"


def test_complete_open_task():
    resp = client.post("/tasks", params={"title": "Open task"})
    task_id = resp.json()["id"]
    resp = client.patch(f"/tasks/{task_id}/complete")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "done"
    assert data["title"] == "Open task"


def test_complete_already_done_task():
    resp = client.post("/tasks", params={"title": "Already done"})
    task_id = resp.json()["id"]
    client.patch(f"/tasks/{task_id}/complete")
    resp = client.patch(f"/tasks/{task_id}/complete")
    assert resp.status_code == 409
    assert resp.json()["detail"] == "task is already done"


def test_complete_nonexistent_task():
    resp = client.patch("/tasks/9999/complete")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "task not found"


def test_delete_task():
    resp = client.post("/tasks", params={"title": "Delete me"})
    task_id = resp.json()["id"]
    resp = client.delete(f"/tasks/{task_id}")
    assert resp.status_code == 204
    # Should not appear in list
    resp = client.get("/tasks")
    ids = [t["id"] for t in resp.json()]
    assert task_id not in ids


def test_delete_nonexistent_task():
    resp = client.delete("/tasks/9999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "task not found"


def test_health_still_works():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_page_still_served():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "<h1>App</h1>" in resp.text