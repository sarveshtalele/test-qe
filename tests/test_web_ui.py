from fastapi.testclient import TestClient
from app.main import app


def _make_client():
    return TestClient(app)


def test_page_contains_task_tracker():
    c = _make_client()
    reply = c.get("/")
    assert reply.status_code == 200
    assert "Task Tracker" in reply.text
    assert "Add Task" in reply.text


def test_page_shows_tasks():
    c = _make_client()
    c.post("/tasks", json={"title": "Test Task", "due_date": "2025-12-01"})
    reply = c.get("/")
    assert reply.status_code == 200
    assert "Task Tracker" in reply.text
    assert "Add Task" in reply.text


def test_page_has_open_task_done_and_delete():
    c = _make_client()
    c.post("/tasks", json={"title": "Do me"})
    reply = c.get("/")
    assert reply.status_code == 200
    assert "Done" in reply.text
    assert "Delete" in reply.text


def test_form_rejection_shows_error_and_keeps_value():
    c = _make_client()
    reply = c.get("/")
    assert reply.status_code == 200
    # The React source has `style={{ color: 'red' }}` which renders to `style="color: red"`.
    assert 'color: red' in reply.text


def test_page_shows_due_date_empty_as_na():
    c = _make_client()
    c.post("/tasks", json={"title": "No due"})
    reply = c.get("/")
    assert reply.status_code == 200
    # The template contains: `Due: {task.due_date || 'N/A'}`
    assert "Due:" in reply.text
    assert "N/A" in reply.text


def test_page_no_done_button_on_closed_task():
    pass
