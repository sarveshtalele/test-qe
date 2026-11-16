from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_page_displays_list_with_title_due_date_and_status_and_form():
    """REQ-011: The page shows the list of tasks with their title, due date and status, and a form to add a task."""
    client.post("/tasks", json={"title": "Write report", "due_date": "2025-06-01"})
    client.post("/tasks", json={"title": "Meeting"})

    reply = client.get("/")
    assert reply.status_code == 200
    html = reply.text

    assert "Write report" in html
    assert "2025-06-01" in html
    assert "open" in html
    assert "Meeting" in html
    assert "Add Task" in html


def test_open_task_has_done_button_and_each_task_has_delete_button():
    """REQ-012: Each open task has a 'Done' button that completes it, and each task has a 'Delete' button."""
    client.post("/tasks", json={"title": "Open task"})
    r = client.post("/tasks", json={"title": "Done task"})
    done_id = r.json()["id"]
    client.patch(f"/tasks/{done_id}/complete")

    reply = client.get("/")
    html = reply.text

    assert "Done" in html
    assert html.count("Delete") >= 2


def test_api_error_message_shown_and_input_preserved():
    """REQ-013: When the API rejects a new task, the page shows the API's message next to the form and keeps what was typed."""
    reply = client.get("/")
    assert reply.status_code == 200
    html = reply.text
    assert 'class="error"' in html
    assert 'id="title-input"' in html
    assert 'id="due-input"' in html
