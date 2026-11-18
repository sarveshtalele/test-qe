from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Fixture: clear in-memory store before each test
# ---------------------------------------------------------------------------


def setup_function():
    from app.main import in_memory_tasks, _next_id

    in_memory_tasks.clear()
    import app.main as m

    m._next_id = 1


# ---------------------------------------------------------------------------
# REQ-011 — Task list and add form
# ---------------------------------------------------------------------------


def test_page_shows_task_list():
    """The page displays a list of tasks (REQ-011)."""
    client.post("/tasks", json={"title": "Task A"})
    client.post("/tasks", json={"title": "Task B"})
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text
    # Both tasks appear
    assert "Task A" in html
    assert "Task B" in html
    # Has the correct data-testid
    assert 'data-testid="task-list"' in html
    assert 'data-testid="task-item"' in html
    assert 'data-testid="task-title"' in html
    assert 'data-testid="task-due-date"' in html
    assert 'data-testid="task-status"' in html
    assert 'data-testid="add-task-form"' in html
    assert 'data-testid="task-title-input"' in html
    assert 'data-testid="task-due-date-input"' in html
    assert 'data-testid="add-task-submit"' in html


def test_page_shows_due_date_and_status():
    """The page shows due date and status (REQ-011)."""
    client.post("/tasks", json={"title": "Task", "due_date": "2025-12-31"})
    resp = client.get("/")
    assert "2025-12-31" in resp.text
    assert "open" in resp.text


def test_page_has_add_form():
    """The page includes an add task form (REQ-011)."""
    resp = client.get("/")
    assert 'method="post"' in resp.text
    assert 'data-testid="add-task-submit"' in resp.text


def test_add_task_via_form():
    """Adding a task via the form creates it (REQ-011)."""
    resp = client.post("/", data={"title": "New Task", "due_date": "2024-01-01"})
    assert resp.status_code == 200
    assert "New Task" in resp.text
    assert "2024-01-01" in resp.text
    # Verify via API
    list_resp = client.get("/tasks")
    titles = [t["title"] for t in list_resp.json()["tasks"]]
    assert "New Task" in titles


# ---------------------------------------------------------------------------
# REQ-012 — Done and Delete buttons
# ---------------------------------------------------------------------------


def test_done_button_present_for_open_task():
    """Open tasks have a Done button (REQ-012)."""
    client.post("/tasks", json={"title": "Open Task"})
    resp = client.get("/")
    assert 'data-testid="done-button"' in resp.text


def test_done_not_present_for_done_task():
    """Done tasks do not have a Done button (REQ-012)."""
    created = client.post("/tasks", json={"title": "Task"}).json()
    client.patch(f"/tasks/{created['id']}/complete")
    resp = client.get("/")
    assert resp.text.count('data-testid="done-button"') == 0


def test_delete_button_present_for_all_tasks():
    """All tasks have a Delete button (REQ-012)."""
    client.post("/tasks", json={"title": "Open Task"})
    created = client.post("/tasks", json={"title": "Done Task"}).json()
    client.patch(f"/tasks/{created['id']}/complete")
    resp = client.get("/")
    # Each task has a delete button
    assert resp.text.count('data-testid="delete-button"') == 2


def test_done_button_marks_task_done():
    """Clicking Done marks the task as done (REQ-012)."""
    created = client.post("/tasks", json={"title": "Task"}).json()
    tid = created["id"]
    resp = client.post(f"/tasks/{tid}/done")
    assert resp.status_code == 200
    # Verify via API
    get_resp = client.get("/tasks")
    task = get_resp.json()["tasks"][0]
    assert task["status"] == "done"


def test_delete_button_removes_task():
    """Clicking Delete removes the task (REQ-012)."""
    created = client.post("/tasks", json={"title": "Task"}).json()
    tid = created["id"]
    resp = client.post(f"/tasks/{tid}/delete")
    assert resp.status_code == 200
    # Verify via API
    get_resp = client.get("/tasks")
    ids = [t["id"] for t in get_resp.json()["tasks"]]
    assert tid not in ids


# ---------------------------------------------------------------------------
# REQ-013 — Error display on form submission
# ---------------------------------------------------------------------------


def test_form_error_empty_title():
    """Submitting empty title shows error and keeps input (REQ-013)."""
    resp = client.post("/", data={"title": "  ", "due_date": ""})
    assert resp.status_code == 200
    html = resp.text
    assert 'data-testid="task-error"' in html
    assert "title must be 1 to 120 characters" in html
    # Input keeps the submitted value (trimmed, but since empty after trim, we show original)
    assert 'value="  "' in html or 'value=""' in html


def test_form_error_too_long_title():
    """Submitting a title >120 chars shows error (REQ-013)."""
    long_title = "x" * 121
    resp = client.post("/", data={"title": long_title, "due_date": ""})
    assert resp.status_code == 200
    html = resp.text
    assert 'data-testid="task-error"' in html
    assert "title must be 1 to 120 characters" in html
    # Input keeps the submitted value
    assert 'value="' + "x" * 121 + '"' in html


def test_form_error_invalid_due_date():
    """Submitting an invalid due date shows error (REQ-013)."""
    resp = client.post("/", data={"title": "Task", "due_date": "31-12-2025"})
    assert resp.status_code == 200
    html = resp.text
    assert 'data-testid="task-error"' in html
    assert "due_date must be YYYY-MM-DD" in html
    # Input keeps the submitted values
    assert 'value="Task"' in html
    assert 'value="31-12-2025"' in html


def test_form_success_no_error():
    """Submitting valid data does not show error (REQ-011, REQ-013)."""
    resp = client.post("/", data={"title": "Valid Task", "due_date": "2025-12-01"})
    assert resp.status_code == 200
    assert 'data-testid="task-error"' not in resp.text
    assert "Valid Task" in resp.text
    assert "2025-12-01" in resp.text