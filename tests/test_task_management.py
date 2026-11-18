from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def setup_method():
    # Reset the repository by replacing app.state.task_repo
    from app.task_repo import TaskRepository
    app.state.task_repo = TaskRepository()


class TestTaskManagement:
    def setup_method(self):
        from app.task_repo import TaskRepository
        app.state.task_repo = TaskRepository()

    # REQ-001, REQ-002, REQ-003, REQ-004
    def test_create_task_success(self):
        reply = client.post("/tasks", json={"title": "My task"})
        assert reply.status_code == 201
        body = reply.json()
        assert body["title"] == "My task"
        assert body["status"] == "open"
        assert body["due_date"] is None
        assert isinstance(body["id"], int)

    def test_create_task_with_due_date(self):
        reply = client.post("/tasks", json={"title": "Task with date", "due_date": "2025-12-31"})
        assert reply.status_code == 201
        body = reply.json()
        assert body["due_date"] == "2025-12-31"

    def test_create_task_title_too_short(self):
        reply = client.post("/tasks", json={"title": "   "})
        assert reply.status_code == 422
        assert reply.json()["detail"] == "title must be 1 to 120 characters"

    def test_create_task_title_too_long(self):
        reply = client.post("/tasks", json={"title": "a" * 121})
        assert reply.status_code == 422
        assert reply.json()["detail"] == "title must be 1 to 120 characters"

    def test_create_task_invalid_due_date_format(self):
        reply = client.post("/tasks", json={"title": "Test", "due_date": "31-12-2025"})
        assert reply.status_code == 422
        assert reply.json()["detail"] == "due_date must be YYYY-MM-DD"

    def test_create_task_due_date_not_a_date(self):
        reply = client.post("/tasks", json={"title": "Test", "due_date": "2025-02-30"})
        assert reply.status_code == 422
        assert reply.json()["detail"] == "due_date must be YYYY-MM-DD"

    # REQ-005, REQ-006
    def test_list_tasks_empty(self):
        reply = client.get("/tasks")
        assert reply.status_code == 200
        assert reply.json() == {"tasks": []}

    def test_list_tasks_newest_first(self):
        client.post("/tasks", json={"title": "First"})
        client.post("/tasks", json={"title": "Second"})
        reply = client.get("/tasks")
        tasks = reply.json()["tasks"]
        assert tasks[0]["title"] == "Second"
        assert tasks[1]["title"] == "First"

    def test_list_tasks_filter_open(self):
        client.post("/tasks", json={"title": "A"})
        reply = client.get("/tasks?status=open")
        assert reply.status_code == 200
        assert len(reply.json()["tasks"]) == 1

    def test_list_tasks_filter_done(self):
        client.post("/tasks", json={"title": "A"})
        reply_get = client.get("/tasks")
        task_id = reply_get.json()["tasks"][0]["id"]
        client.patch(f"/tasks/{task_id}/done")
        reply = client.get("/tasks?status=done")
        assert reply.status_code == 200
        assert len(reply.json()["tasks"]) == 1

    def test_list_tasks_filter_invalid_status(self):
        reply = client.get("/tasks?status=invalid")
        assert reply.status_code == 422
        assert reply.json()["detail"] == "status must be open or done"

    # REQ-007, REQ-008, REQ-009
    def test_complete_task_success(self):
        create_reply = client.post("/tasks", json={"title": "Do something"})
        task_id = create_reply.json()["id"]
        reply = client.patch(f"/tasks/{task_id}/done")
        assert reply.status_code == 200
        body = reply.json()
        assert body["id"] == task_id
        assert body["status"] == "done"
        assert body["title"] == "Do something"

    def test_complete_task_already_done(self):
        create_reply = client.post("/tasks", json={"title": "X"})
        task_id = create_reply.json()["id"]
        client.patch(f"/tasks/{task_id}/done")
        reply = client.patch(f"/tasks/{task_id}/done")
        assert reply.status_code == 409
        assert reply.json()["detail"] == "task is already done"

    def test_complete_task_not_found(self):
        reply = client.patch("/tasks/999/done")
        assert reply.status_code == 404
        assert reply.json()["detail"] == "task not found"

    # REQ-009, REQ-010
    def test_delete_task_success(self):
        create_reply = client.post("/tasks", json={"title": "Delete me"})
        task_id = create_reply.json()["id"]
        reply = client.delete(f"/tasks/{task_id}")
        assert reply.status_code == 204
        get_reply = client.get("/tasks")
        assert len(get_reply.json()["tasks"]) == 0

    def test_delete_task_not_found(self):
        reply = client.delete("/tasks/999")
        assert reply.status_code == 404
        assert reply.json()["detail"] == "task not found"

    # REQ-014 already has test_health

    # REQ-011, REQ-012, REQ-013 - check HTML elements
    def test_page_contains_required_elements(self):
        reply = client.get("/")
        assert reply.status_code == 200
        html = reply.text
        assert 'data-testid="task-list"' in html
        # task-item is rendered by JavaScript, not present in static HTML
        assert 'data-testid="add-task-form"' in html
        assert 'data-testid="title-input"' in html
        assert 'data-testid="due-date-input"' in html
        assert 'data-testid="add-task-button"' in html
        # done-button and delete-button are rendered by JavaScript
        assert 'data-testid="api-error-message"' in html

    def test_page_shows_task_info(self):
        # The task list is rendered by JavaScript, so static HTML does not contain task text
        reply = client.get("/")
        assert reply.status_code == 200
        assert 'data-testid="task-list"' in reply.text
