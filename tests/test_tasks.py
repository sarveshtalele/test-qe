from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_task_minimal():
    reply = client.post("/tasks", json={"title": "Buy milk"})
    assert reply.status_code == 201
    data = reply.json()
    assert data["title"] == "Buy milk"
    assert data["due_date"] is None
    assert data["status"] == "open"
    assert isinstance(data["id"], int)
    assert "created_at" in data


def test_create_task_with_due_date():
    reply = client.post("/tasks", json={"title": "Pay bills", "due_date": "2025-06-01"})
    assert reply.status_code == 201
    data = reply.json()
    assert data["title"] == "Pay bills"
    assert data["due_date"] == "2025-06-01"


def test_create_task_title_trimmed():
    reply = client.post("/tasks", json={"title": "  Do laundry  "})
    assert reply.status_code == 201
    assert reply.json()["title"] == "Do laundry"


def test_create_task_title_empty_after_trim_rejected():
    reply = client.post("/tasks", json={"title": "   "})
    assert reply.status_code == 422
    assert reply.json()["detail"][0]["msg"] == "Value error, title must be 1 to 120 characters"


def test_create_task_title_too_long_rejected():
    # 121 characters after stripping
    long_title = "a" * 121
    reply = client.post("/tasks", json={"title": long_title})
    assert reply.status_code == 422
    assert reply.json()["detail"][0]["msg"] == "Value error, title must be 1 to 120 characters"


def test_create_task_invalid_due_date_rejected():
    reply = client.post("/tasks", json={"title": "Test", "due_date": "2025/06/01"})
    assert reply.status_code == 422
    assert reply.json()["detail"][0]["msg"] == "Value error, due_date must be YYYY-MM-DD"


def test_list_tasks_newest_first():
    # Ensure clean state
    client.post("/tasks", json={"title": "First"})
    client.post("/tasks", json={"title": "Second"})
    reply = client.get("/tasks")
    assert reply.status_code == 200
    data = reply.json()
    # The second created should have a later created_at
    titles = [t["title"] for t in data]
    # There may be more tasks from other tests; just check order of these two
    first_idx = titles.index("First")
    second_idx = titles.index("Second")
    assert second_idx < first_idx


def test_list_tasks_filter_by_status():
    reply = client.get("/tasks?status=open")
    assert reply.status_code == 200
    for t in reply.json():
        assert t["status"] == "open"

    reply = client.get("/tasks?status=done")
    assert reply.status_code == 200
    for t in reply.json():
        assert t["status"] == "done"


def test_list_tasks_invalid_status_rejected():
    reply = client.get("/tasks?status=invalid")
    assert reply.status_code == 422
    assert reply.json()["detail"] == "status must be open or done"


def test_complete_task():
    create_reply = client.post("/tasks", json={"title": "Complete me"})
    task_id = create_reply.json()["id"]
    reply = client.patch(f"/tasks/{task_id}/complete")
    assert reply.status_code == 200
    assert reply.json()["status"] == "done"


def test_complete_already_done_conflict():
    create_reply = client.post("/tasks", json={"title": "Already done"})
    task_id = create_reply.json()["id"]
    client.patch(f"/tasks/{task_id}/complete")
    reply = client.patch(f"/tasks/{task_id}/complete")
    assert reply.status_code == 409
    assert reply.json()["detail"] == "task is already done"


def test_complete_nonexistent_task():
    reply = client.patch("/tasks/99999/complete")
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"


def test_delete_task():
    create_reply = client.post("/tasks", json={"title": "Delete me"})
    task_id = create_reply.json()["id"]
    reply = client.delete(f"/tasks/{task_id}")
    assert reply.status_code == 204
    assert reply.text == ""
    # Verify task no longer in list
    list_reply = client.get("/tasks")
    ids = [t["id"] for t in list_reply.json()]
    assert task_id not in ids


def test_delete_nonexistent_task():
    reply = client.delete("/tasks/99999")
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"
