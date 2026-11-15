from fastapi.testclient import TestClient

from app.main import app
from app.store import store

client = TestClient(app)


def reset_store():
    store._tasks.clear()
    store._next_id = 1


def setup_function():
    reset_store()


class TestCreateTask:
    def test_creates_task_with_title_only(self):
        reset_store()
        resp = client.post("/tasks", json={"title": "Buy milk"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Buy milk"
        assert data["status"] == "open"
        assert isinstance(data["id"], int)
        assert data["due_date"] is None
        assert "created_at" in data

    def test_creates_task_with_due_date(self):
        reset_store()
        resp = client.post("/tasks", json={"title": "Submit report", "due_date": "2025-06-01"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["due_date"] == "2025-06-01"

    def test_trims_title(self):
        reset_store()
        resp = client.post("/tasks", json={"title": "  Hello world  "})
        assert resp.status_code == 201
        assert resp.json()["title"] == "Hello world"

    def test_rejects_empty_title_after_trim(self):
        reset_store()
        resp = client.post("/tasks", json={"title": "   "})
        assert resp.status_code == 422
        assert resp.json()["detail"] == "title must be 1 to 120 characters"

    def test_rejects_too_long_title(self):
        reset_store()
        long_title = "a" * 121
        resp = client.post("/tasks", json={"title": long_title})
        assert resp.status_code == 422
        assert resp.json()["detail"] == "title must be 1 to 120 characters"

    def test_rejects_invalid_due_date_format(self):
        reset_store()
        resp = client.post("/tasks", json={"title": "Task", "due_date": "01-06-2025"})
        assert resp.status_code == 422
        assert resp.json()["detail"] == "due_date must be YYYY-MM-DD"

    def test_accepts_boundary_title_lengths(self):
        reset_store()
        resp = client.post("/tasks", json={"title": "a"})
        assert resp.status_code == 201
        reset_store()
        resp = client.post("/tasks", json={"title": "a" * 120})
        assert resp.status_code == 201

    def test_auto_increments_id(self):
        reset_store()
        r1 = client.post("/tasks", json={"title": "Task 1"})
        r2 = client.post("/tasks", json={"title": "Task 2"})
        assert r1.json()["id"] == 1
        assert r2.json()["id"] == 2


class TestListTasks:
    def test_list_all_tasks_newest_first(self):
        reset_store()
        import time

        client.post("/tasks", json={"title": "First"})
        time.sleep(0.01)
        client.post("/tasks", json={"title": "Second"})
        time.sleep(0.01)
        client.post("/tasks", json={"title": "Third"})
        resp = client.get("/tasks")
        assert resp.status_code == 200
        titles = [t["title"] for t in resp.json()]
        assert titles == ["Third", "Second", "First"]

    def test_filter_by_status_open(self):
        reset_store()
        client.post("/tasks", json={"title": "Open task"})
        resp = client.get("/tasks?status=open")
        assert resp.status_code == 200
        assert all(t["status"] == "open" for t in resp.json())

    def test_filter_by_status_done(self):
        reset_store()
        client.post("/tasks", json={"title": "Task to complete"})
        client.patch("/tasks/1/complete")
        resp = client.get("/tasks?status=done")
        assert resp.status_code == 200
        assert all(t["status"] == "done" for t in resp.json())

    def test_rejects_invalid_status_filter(self):
        reset_store()
        resp = client.get("/tasks?status=invalid")
        assert resp.status_code == 422
        assert resp.json()["detail"] == "status must be open or done"


class TestCompleteTask:
    def test_completes_open_task(self):
        reset_store()
        client.post("/tasks", json={"title": "Do something"})
        resp = client.patch("/tasks/1/complete")
        assert resp.status_code == 200
        assert resp.json()["status"] == "done"

    def test_completing_already_done_task_returns_409(self):
        reset_store()
        client.post("/tasks", json={"title": "Test"})
        client.patch("/tasks/1/complete")
        resp = client.patch("/tasks/1/complete")
        assert resp.status_code == 409
        assert resp.json()["detail"] == "task is already done"

    def test_completing_nonexistent_task_returns_404(self):
        reset_store()
        resp = client.patch("/tasks/999/complete")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "task not found"


class TestDeleteTask:
    def test_deletes_task_returns_204(self):
        reset_store()
        client.post("/tasks", json={"title": "Delete me"})
        resp = client.delete("/tasks/1")
        assert resp.status_code == 204
        assert resp.text == ""

    def test_deleted_task_no_longer_in_list(self):
        reset_store()
        client.post("/tasks", json={"title": "Gone"})
        client.delete("/tasks/1")
        resp = client.get("/tasks")
        assert len(resp.json()) == 0

    def test_deleting_nonexistent_task_returns_404(self):
        reset_store()
        resp = client.delete("/tasks/999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "task not found"

    def test_delete_preserves_other_tasks(self):
        reset_store()
        client.post("/tasks", json={"title": "Keep"})
        client.post("/tasks", json={"title": "Remove"})
        client.delete("/tasks/2")
        resp = client.get("/tasks")
        titles = [t["title"] for t in resp.json()]
        assert titles == ["Keep"]
