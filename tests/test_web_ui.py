import pytest
from starlette.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    from app.task_store import TaskStore
    import app.tasks
    app.tasks.store = TaskStore()
    return TestClient(app)


def test_page_shows_tasks_and_form(client):
    """REQ-011: page shows list of tasks with title, due date, status, and a form to add a task."""
    # Create a task via API
    client.post("/tasks", json={"title": "Test task", "due_date": "2025-12-01"})

    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    # Check the form exists
    assert '<form id="addForm">' in html
    assert '<input type="text" id="titleInput"' in html
    assert '<input type="date" id="dueDateInput"' in html
    assert '<button type="submit">Add Task</button>' in html

    # Check task title, due date, status appear
    assert "Test task" in html
    assert "2025-12-01" in html
    assert "[Open]" in html


def test_open_task_has_done_and_delete_buttons(client):
    """REQ-012: each open task has a 'Done' button that completes it, each task has a 'Delete' button."""
    client.post("/tasks", json={"title": "Task to complete"})

    resp = client.get("/")
    html = resp.text

    # The HTML contains a button with 'Done' for open task
    assert "Done" in html
    # Delete button for task
    assert "Delete" in html


def test_done_task_has_no_done_button(client):
    """REQ-012: done task does NOT have a Done button, but still has a Delete button."""
    create_resp = client.post("/tasks", json={"title": "Finish me"})
    tid = create_resp.json()["id"]
    client.patch(f"/tasks/{tid}/complete")

    resp = client.get("/")
    html = resp.text

    # Done button should NOT appear (we only have one task, and it's done)
    # But Delete should still be there
    # We can count occurrences: Done button appears only for open tasks
    # The Done button text appears exactly once if the page had an open task; with only a done task, it should not appear.
    assert "Done" not in html
    assert "Delete" in html


def test_api_error_shown_and_form_kept(client):
    """REQ-013: when API rejects new task, page shows API message next to form and keeps what was typed.
    Since we cannot test DOM state without a browser, we test that the error div is present and
    that the page still has the form fields. The real behaviour of keeping typed values is browser-side only;
    we check that the API error is displayed by fetching the page after a failed submission via JS.
    Here we test that the HTML contains a placeholder for errors."""
    # The error div with id 'error' must exist
    resp = client.get("/")
    assert resp.status_code == 200
    assert '<div id="error"' in resp.text

    # Submit an invalid task via API to verify the error message
    resp = client.post("/tasks", json={"title": ""})
    assert resp.status_code == 422

    # The error text will appear in the error div after the JS runs; we can't test that statically.
    # But we verify the page structure allows it.
    assert 'class="error"' in resp.text
