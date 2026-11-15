from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestCreateTask:
    def test_create_task_minimal(self):
        """REQ-001, REQ-004: title only -> status open, unique id, 201"""
        reply = client.post("/tasks", json={"title": "hello"})
        assert reply.status_code == 201
        data = reply.json()
        assert data["title"] == "hello"
        assert data["status"] == "open"
        assert isinstance(data["id"], int)
        assert data["id"] > 0

    def test_create_task_with_due_date(self):
        """REQ-001, REQ-003, REQ-004: valid due date"""
        reply = client.post("/tasks", json={"title": "task", "due_date": "2025-01-02"})
        assert reply.status_code == 201
        data = reply.json()
        assert data["due_date"] == "2025-01-02"
        assert data["status"] == "open"

    def test_title_trimmed(self):
        """REQ-002: leading/trailing spaces trimmed"""
        reply = client.post("/tasks", json={"title": "  my task  "})
        assert reply.status_code == 201
        assert reply.json()["title"] == "my task"

    def test_title_empty_after_trim(self):
        """REQ-002: only spaces -> 422 with exact message"""
        reply = client.post("/tasks", json={"title": "   "})
        assert reply.status_code == 422
        assert reply.json()["detail"][0]["msg"] == "title must be 1 to 120 characters"

    def test_title_too_short(self):
        """REQ-002: empty string -> 422 with exact message"""
        reply = client.post("/tasks", json={"title": ""})
        assert reply.status_code == 422
        assert reply.json()["detail"][0]["msg"] == "title must be 1 to 120 characters"

    def test_title_too_long(self):
        """REQ-002: 121 chars -> 422 with exact message"""
        reply = client.post("/tasks", json={"title": "a" * 121})
        assert reply.status_code == 422
        assert reply.json()["detail"][0]["msg"] == "title must be 1 to 120 characters"

    def test_due_date_bad_format(self):
        """REQ-003: wrong format -> 422 with exact message"""
        reply = client.post("/tasks", json={"title": "test", "due_date": "01-02-2025"})
        assert reply.status_code == 422
        assert reply.json()["detail"][0]["msg"] == "due_date must be YYYY-MM-DD"

    def test_due_date_non_date_string(self):
        """REQ-003: non-date string -> 422 with exact message"""
        reply = client.post("/tasks", json={"title": "test", "due_date": "not-a-date"})
        assert reply.status_code == 422
        assert reply.json()["detail"][0]["msg"] == "due_date must be YYYY-MM-DD"

    def test_unique_ids(self):
        """REQ-004: consecutive ids"""
        first = client.post("/tasks", json={"title": "a"}).json()["id"]
        second = client.post("/tasks", json={"title": "b"}).json()["id"]
        assert second == first + 1

    def test_status_open(self):
        """REQ-004: status open"""
        reply = client.post("/tasks", json={"title": "test"})
        assert reply.json()["status"] == "open"

    def test_health_still_works(self):
        reply = client.get("/health")
        assert reply.status_code == 200
        assert reply.json() == {"status": "ok"}
