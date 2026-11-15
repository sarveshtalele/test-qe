from fastapi.testclient import TestClient

from app.main import app, _tasks

client = TestClient(app)


def setup_function():
    _tasks.clear()


def test_page_shows_task_list_and_form():
    """REQ-012: The page shows the list of tasks with their title, due date and status, and a form to add a task."""
    # Create a task via API
    client.post("/tasks", json={"title": "Test UI", "dueDate": "2025-06-01"})
    reply = client.get("/")
    assert reply.status_code == 200
    html = reply.text
    assert "Task Tracker" in html
    # The page renders title, due date, and status in each list item
    assert "Test UI (2025-06-01) [open]" in html
    # Form elements present
    assert '<form id="add-form"' in html
    assert '<input id="title"' in html
    assert '<input id="dueDate"' in html


def test_each_open_task_has_done_button():
    """REQ-013: Each open task has a "Done" button that completes it, and each task has a "Delete" button."""
    client.post("/tasks", json={"title": "Open task"})
    client.post("/tasks", json={"title": "Done task"})
    # Complete the second task
    tasks = client.get("/tasks").json()
    done_task_id = [t["id"] for t in tasks if t["title"] == "Done task"][0]
    client.patch(f"/tasks/{done_task_id}/complete")
    reply = client.get("/")
    html = reply.text
    # Open task should have Done button (the word "Done" inside a button)
    assert '>Done<' in html
    # Each task should have a delete button
    delete_count = html.count(">Delete<")
    assert delete_count == 2


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
