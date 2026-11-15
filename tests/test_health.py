from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_is_ok():
    reply = client.get("/health")
    assert reply.status_code == 200
    assert reply.json() == {"status": "ok"}


def test_page_is_served():
    reply = client.get("/")
    assert reply.status_code == 200
    assert "<h1>Task Tracker</h1>" in reply.text


def test_page_contains_list_and_form():
    """REQ-011: page shows list of tasks with title, due date, status, and add form"""
    reply = client.get("/")
    html = reply.text
    assert "Title" in html
    assert "Due date" in html
    assert "Status" in html
    assert "Add task" in html


def test_page_contains_done_and_delete_buttons():
    """REQ-012: page contains Done and Delete buttons"""
    reply = client.get("/")
    html = reply.text
    assert "Done" in html
    assert "Delete" in html


def test_page_shows_error_container():
    """REQ-013: page has an element to show API error messages"""
    reply = client.get("/")
    # The error div exists and uses class="error" or className="error"
    assert 'class="error"' in reply.text or 'className="error"' in reply.text
