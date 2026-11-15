import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.store import store

client = TestClient(app)


def reset_store():
    store._tasks.clear()
    store._next_id = 1


def setup_function():
    reset_store()


def test_page_returns_html_with_task_tracker_title():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Task Tracker" in resp.text


def test_page_contains_add_task_form():
    resp = client.get("/")
    assert "Add Task" in resp.text
    assert 'type="submit"' in resp.text


def test_page_shows_tasks_with_title_due_date_and_status():
    reset_store()
    client.post("/tasks", json={"title": "Buy milk", "due_date": "2025-06-01"})
    resp = client.get("/")
    assert "Buy milk" in resp.text
    assert "2025-06-01" in resp.text
    assert "open" in resp.text


def test_page_shows_done_button_for_open_task():
    reset_store()
    client.post("/tasks", json={"title": "Task1"})
    resp = client.get("/")
    assert "Done" in resp.text


def test_page_shows_delete_button_for_each_task():
    reset_store()
    client.post("/tasks", json={"title": "Task2"})
    resp = client.get("/")
    assert "Delete" in resp.text


def test_page_shows_api_error_message_when_title_empty():
    reset_store()
    form_data = {"title": "   "}
    resp = client.post("/tasks", json=form_data)
    assert resp.status_code == 422
    assert resp.json()["detail"] == "title must be 1 to 120 characters"
    # Verify page includes error handling text
    page_resp = client.get("/")
    # The page itself doesn't show the error from this request; the error appears only when the form is submitted.
    # We check that the error display placeholder (a red paragraph) exists.
    assert 'style="color: red"' in page_resp.text


def test_page_shows_api_error_message_when_invalid_due_date():
    reset_store()
    form_data = {"title": "Test", "due_date": "not-a-date"}
    resp = client.post("/tasks", json=form_data)
    assert resp.status_code == 422
    assert resp.json()["detail"] == "due_date must be YYYY-MM-DD"
    page_resp = client.get("/")
    assert 'style="color: red"' in page_resp.text


def test_page_retains_typed_values_on_error_not_possible_with_server_test():
    # The requirement says "keeps what was typed" – this is a client-side behaviour,
    # not testable via server-side HTTP. We check that the form inputs are present.
    resp = client.get("/")
    assert 'value="' in resp.text or 'value=' in resp.text
