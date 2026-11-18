from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_page_has_form_and_title():
    """REQ-012: The page shows the list of tasks with their title, due date and status,
    and a form to add a task. Since the tasks are loaded client-side via fetch,
    we can only verify the static template includes the required elements."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text
    assert "<form" in html
    assert "Add Task" in html
    assert "task-list" in html
    assert "Task Tracker" in html


def test_page_has_expected_script_and_placeholders():
    """REQ-012 and REQ-013: The static HTML must include the script that
    renders tasks, form, and buttons."""
    resp = client.get("/")
    html = resp.text
    assert "done-btn" in html
    assert "delete-btn" in html
    assert "fetch('/tasks')" in html
    assert "title-input" in html
    assert "due-date-input" in html
    assert "form-error" in html


def test_api_error_response_has_detail():
    """REQ-014: When the API rejects, it returns a detail string."""
    resp = client.post("/tasks", json={"title": "   "})
    assert resp.status_code == 422
    assert resp.json()["detail"] == "title must be 1 to 120 characters"


def test_api_error_detail_for_empty_title():
    resp = client.post("/tasks", json={"title": ""})
    assert resp.status_code == 422
    err_data = resp.json()
    detail = err_data.get("detail")
    assert detail is not None


def test_health_remains_working():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
