from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_page_shows_form():
    """REQ-011: The page shows a form to add a task."""
    reply = client.get("/")
    assert reply.status_code == 200
    html = reply.text
    # Check form elements exist in static HTML
    assert "<form" in html
    assert 'id="add-form"' in html
    assert 'id="title"' in html
    assert 'id="due-date"' in html
    # Task list is populated client-side, so we can't check content here,
    # but we can check that the container exists.
    assert 'id="task-list"' in html


def test_page_shows_task_area():
    """REQ-011: The page has a container for the task list (title, due date, status rendered client-side)."""
    reply = client.get("/")
    html = reply.text
    assert '<div id="task-list">' in html


def test_done_button_templated_in_js():
    """REQ-012: The JavaScript template contains the Done button HTML."""
    reply = client.get("/")
    html = reply.text
    # The JS template includes the literal string for the done button
    assert 'class="done-btn"' in html


def test_delete_button_templated_in_js():
    """REQ-012: The JavaScript template contains the Delete button HTML."""
    reply = client.get("/")
    html = reply.text
    assert 'class="delete-btn"' in html


def test_error_display_on_form():
    """REQ-013: The page contains an error div next to the form."""
    reply = client.get("/")
    assert 'id="form-error"' in reply.text
    assert 'class="error"' in reply.text


def test_api_rejects_empty_title():
    """REQ-013: API returns proper error for invalid input."""
    err_reply = client.post("/tasks", json={"title": "   "})
    assert err_reply.status_code == 422
    assert "title must be 1 to 120 characters" in err_reply.text
