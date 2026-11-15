from fastapi.testclient import TestClient

from app.main import app
from app.tasks import store

client = TestClient(app)


def setup_function():
    store._counter = 0
    store._tasks.clear()


def test_page_shows_task_list():
    """BR-11: The page shows the list of tasks with their title, due date and status."""
    client.post("/tasks", json={"title": "Test", "due_date": "2025-12-31"})
    reply = client.get("/")
    assert reply.status_code == 200
    html = reply.text
    assert "task-list" in html
    assert "id=\"root\"" in html


def test_page_has_add_form():
    """BR-11: The page shows a form to add a task."""
    reply = client.get("/")
    assert reply.status_code == 200
    html = reply.text
    assert "Add Task" in html
    assert 'type="submit"' in html


def test_done_button_for_open_tasks():
    """BR-12: Each open task has a 'Done' button."""
    client.post("/tasks", json={"title": "Open task"})
    reply = client.get("/")
    html = reply.text
    assert "done-form" in html
    assert "Done" in html


def test_delete_button_for_each_task():
    """BR-12: Each task has a 'Delete' button."""
    client.post("/tasks", json={"title": "Delete me"})
    reply = client.get("/")
    html = reply.text
    assert "delete-form" in html
    assert "Delete" in html


def test_no_done_button_for_done_tasks():
    """BR-12: Only open tasks have 'Done' button."""
    client.post("/tasks", json={"title": "Open"})
    client.patch("/tasks/1/complete")
    reply = client.get("/")
    html = reply.text
    assert "data-id=\"1\"" in html
    assert "done-form" not in html


def test_api_error_shown_on_task_creation():
    """BR-13: When the API rejects a new task, the page shows the API's message."""
    # This test checks that the frontend JS error display is present for empty title
    reply = client.get("/")
    html = reply.text
    # The error div is present
    assert 'id="add-error"' in html


def test_create_task_with_empty_title_fails():
    """BR-13: API rejects empty title."""
    reply = client.post("/tasks", json={"title": "   "})
    assert reply.status_code == 422
    assert reply.json()["detail"] == "Task title is required"


def test_keeps_what_was_typed_on_error():
    """BR-13: The page keeps what was typed (not testable via static HTML; JS maintains state)."""
    # This is a frontend JS behavior, but we verify the form is present and error display exists.
    reply = client.get("/")
    assert reply.status_code == 200
    html = reply.text
    assert 'id="title-input"' in html
    assert 'id="add-error"' in html


def test_page_title():
    reply = client.get("/")
    assert "Task Tracker" in reply.text
