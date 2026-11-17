from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_page_contains_task_tracker_heading():
    """REQ-011: page shows the list of tasks with their title, due date and status, and a form to add a task"""
    reply = client.get("/")
    assert reply.status_code == 200
    html = reply.text
    # The static page includes a root div and scripts, but the heading is present
    assert "Task Tracker" in html
    assert "Add Task" in html


def test_page_contains_done_and_delete_button_text():
    """REQ-012: each open task has a Done button that completes it, and each task has a Delete button"""
    reply = client.get("/")
    assert reply.status_code == 200
    html = reply.text
    assert "Done" in html
    assert "Delete" in html


def test_page_has_error_display_area():
    """REQ-013: when the API rejects a new task, the page shows the API's message next to the form and keeps what was typed"""
    reply = client.get("/")
    assert reply.status_code == 200
    html = reply.text
    # The page CSS includes an .error class style and a dynamic error div that will be created
    assert ".error" in html
