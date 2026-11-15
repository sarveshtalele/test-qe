from fastapi.testclient import TestClient

from app.main import app, _tasks

client = TestClient(app)


def setup_function():
    _tasks.clear()


def test_page_shows_list_container_and_form():
    """REQ-012: The page includes a container for the task list and a form to add a task.
    Note: The actual list rendering happens in JavaScript; test only static HTML."""
    reply = client.get("/")
    assert reply.status_code == 200
    html = reply.text
    assert "Task Tracker" in html
    # The page has a container with id="task-list" where JS renders tasks
    assert '<ul id="task-list">' in html
    # Form elements present
    assert '<form id="add-form"' in html
    assert '<input id="title"' in html
    assert '<input id="dueDate"' in html


def test_page_has_done_and_delete_button_markup():
    """REQ-013: The page includes Done and Delete buttons for each task in the JavaScript template."""
    reply = client.get("/")
    assert reply.status_code == 200
    html = reply.text
    # The JS template contains '>Done<' and '>Delete<' markers
    assert '>Done<' in html
    assert '>Delete<' in html


def test_api_error_shows_next_to_form():
    """REQ-014: When the API rejects a new task, the page shows the API's message next to the form and keeps what was typed."""
    reply = client.get("/")
    assert reply.status_code == 200
    html = reply.text
    # Error container present next to form
    assert '<div id="error" class="error"></div>' in html
    # Input fields present
    assert '<input id="title"' in html
    assert '<input id="dueDate"' in html
