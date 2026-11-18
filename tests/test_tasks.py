from fastapi.testclient import TestClient

from app.main import app
from app.store import tasks_db, next_id

client = TestClient(app)


def setup_function():
    tasks_db.clear()
    # reset counter by reimporting next_id (hack for simplicity)
    import app.store
    app.store._counter = [0]


def test_create_task_minimal():
    resp = client.post("/tasks", json={"title": "  Buy milk  "})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Buy milk"
    assert data["status"] == "open"
    assert "id" in data
    assert data["due_date"] is None
    assert "created_at" in data


def test_create_task_with_due_date():
    resp = client.post("/tasks", json={"title": "Task", "due_date": "2025-12-31"})
    assert resp.status_code == 201
    assert resp.json()["due_date"] == "2025-12-31"


def test_create_task_invalid_title_empty():
    resp = client.post("/tasks", json={"title": "   "})
    assert resp.status_code == 422
    assert resp.json()["detail"] == "title must be 1 to 120 characters"


def test_create_task_title_too_long():
    resp = client.post("/tasks", json={"title": "x" * 121})
    assert resp.status_code == 422
    assert resp.json()["detail"] == "title must be 1 to 120 characters"


def test_create_task_invalid_due_date():
    resp = client.post("/tasks", json={"title": "Task", "due_date": "31-12-2025"})
    assert resp.status_code == 422
    assert resp.json()["detail"] == "due_date must be YYYY-MM-DD"


def test_list_tasks_empty():
    resp = client.get("/tasks")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_tasks_newest_first():
    client.post("/tasks", json={"title": "first"})
    client.post("/tasks", json={"title": "second"})
    resp = client.get("/tasks")
    assert resp.status_code == 200
    tasks = resp.json()
    assert len(tasks) == 2
    assert tasks[0]["title"] == "second"
    assert tasks[1]["title"] == "first"


def test_list_tasks_filter_by_status():
    client.post("/tasks", json={"title": "open1"})
    client.post("/tasks", json={"title": "open2"})
    # mark first as done
    tasks = client.get("/tasks").json()
    done_id = tasks[-1]["id"]
    client.put(f"/tasks/{done_id}/done")

    resp_open = client.get("/tasks?status=open")
    assert resp_open.status_code == 200
    assert len(resp_open.json()) == 1
    assert resp_open.json()[0]["title"] == "open2"

    resp_done = client.get("/tasks?status=done")
    assert resp_done.status_code == 200
    assert len(resp_done.json()) == 1
    assert resp_done.json()[0]["title"] == "open1"


def test_list_tasks_invalid_status():
    resp = client.get("/tasks?status=invalid")
    assert resp.status_code == 422
    assert resp.json()["detail"] == "status must be open or done"


def test_mark_task_done():
    create_resp = client.post("/tasks", json={"title": "Do it"})
    task_id = create_resp.json()["id"]
    resp = client.put(f"/tasks/{task_id}/done")
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"
    assert resp.json()["title"] == "Do it"


def test_mark_already_done_task():
    create_resp = client.post("/tasks", json={"title": "Do it"})
    task_id = create_resp.json()["id"]
    client.put(f"/tasks/{task_id}/done")
    resp = client.put(f"/tasks/{task_id}/done")
    assert resp.status_code == 409
    assert resp.json()["detail"] == "task is already done"


def test_mark_nonexistent_task():
    resp = client.put("/tasks/99999/done")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "task not found"


def test_delete_task():
    create_resp = client.post("/tasks", json={"title": "Delete me"})
    task_id = create_resp.json()["id"]
    resp = client.delete(f"/tasks/{task_id}")
    assert resp.status_code == 204
    # verify it's gone
    list_resp = client.get("/tasks")
    assert list_resp.json() == []


def test_delete_nonexistent_task():
    resp = client.delete("/tasks/99999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "task not found"
