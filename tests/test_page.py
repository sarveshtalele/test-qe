from fastapi.testclient import TestClient

from app.main import app
from app.store import tasks_db

client = TestClient(app)


def setup_function():
    tasks_db.clear()
    import app.store
    app.store._counter = [0]


def test_page_has_add_task_form():
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text
    # Form for adding a task: title input, date input, and add button
    assert '<form id="add-task-form">' in html
    assert 'id="title"' in html
    assert 'id="due-date"' in html
    assert '<button type="submit">Add Task</button>' in html


def test_page_has_task_list_container():
    """The page has an empty <ul> for tasks (tasks are loaded via JS later)."""
    resp = client.get("/")
    html = resp.text
    assert '<ul id="task-list"></ul>' in html


def test_page_has_error_div():
    """The page contains an element to display API errors."""
    resp = client.get("/")
    assert 'id="error"' in resp.text


def test_page_has_done_and_delete_button_references_in_js():
    """The JavaScript code contains the text 'Done' and 'Delete' for buttons."""
    resp = client.get("/")
    html = resp.text
    assert "Done" in html  # button text in JS
    assert "Delete" in html  # button text in JS
    # Also the class names are used in the JS
    assert 'className = \'done\'' in html or 'className="done"' in html or "'done'" in html
    assert 'className = \'delete\'' in html or 'className="delete"' in html or "'delete'" in html
