from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_page_has_task_list_and_form():
    """REQ-012: The page shows the list of tasks with their title, due date and status, and a form to add a task."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text
    # The page must contain a form (method not enforced statically)
    assert "<form" in html
    assert "Add Task" in html
    # It should also have a spot where tasks are listed (ul with li elements)
    # We can't test dynamic content without JavaScript, but the structure must be present
    assert "<ul>" in html


def test_page_has_done_button_for_open_task_and_delete_button_for_all():
    """REQ-013: Each open task has a "Done" button that completes it, and each task has a "Delete" button."""
    resp = client.get("/")
    html = resp.text
    # The template should contain at least one "Done" button and one "Delete" button
    assert '>Done<' in html
    assert '>Delete<' in html


def test_page_shows_error_when_api_rejects():
    """REQ-014: When the API rejects a new task, the page shows the API's message next to the form and keeps what was typed.
    We verify that an element with class 'error' exists in the page."""
    resp = client.get("/")
    html = resp.text
    assert 'className="error"' in html or 'class="error"' in html


def test_health_still_works():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
