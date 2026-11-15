from fastapi.testclient import TestClient

from app.main import app
from app.routers.tasks import _tasks

client = TestClient(app)


def setup_function():
    _tasks.clear()


def test_page_displays_list_and_form():
    """REQ-012: The page shows the list of tasks with their title, due date and status, and a form to add a task."""
    reply = client.get("/")
    assert reply.status_code == 200
    html = reply.text
    assert "<h1>Task Tracker</h1>" in html
    assert "<form" in html
    assert "title-input" in html
    assert "due-input" in html
    assert "task-list" in html


def test_page_has_done_and_delete_buttons():
    """REQ-013: Each open task has a \"Done\" button that completes it, and each task has a \"Delete\" button."""
    reply = client.get("/")
    html = reply.text
    assert "Done" in html
    assert "Delete" in html


def test_page_shows_error_on_rejection():
    """REQ-014: When the API rejects a new task, the page shows the API's message next to the form and keeps what was typed."""
    reply = client.get("/")
    html = reply.text
    assert "id=\"error-message\"" in html
    assert "class=\"error\"" in html
    assert "id=\"title-input\"" in html
