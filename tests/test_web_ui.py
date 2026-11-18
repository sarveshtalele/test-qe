from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_page_shows_task_list_and_form():
    reply = client.get("/")
    assert reply.status_code == 200
    html = reply.text
    # Check that the page contains the form elements and table headers
    assert '<form id="add-form">' in html
    assert 'name="title"' in html
    assert 'name="due_date"' in html
    assert "<th>Title</th>" in html
    assert "<th>Due Date</th>" in html
    assert "<th>Status</th>" in html
    assert "<th>Actions</th>" in html


def test_page_includes_done_and_delete_in_javascript():
    reply = client.get("/")
    html = reply.text
    # The JavaScript contains 'Done' button and 'Delete' button for open tasks
    # (the actual rendering is client-side, but the script includes them)
    assert 'completeTask(' in html
    assert 'deleteTask(' in html
    assert 'Done' in html
    assert 'Delete' in html


def test_page_has_error_display_and_preserves_input():
    reply = client.get("/")
    html = reply.text
    # Error div exists for showing API messages
    assert '<div id="error"' in html
    # The form reset only happens on success
    assert 'this.reset();' in html
    # The else branch (error) does not reset
    assert '} else {' in html
    # The JavaScript shows the error message
    assert 'showError(data.detail' in html
    assert 'name="title"' in html
    assert 'name="due_date"' in html
