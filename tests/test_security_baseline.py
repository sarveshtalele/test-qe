from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_anonymous_access_to_health():
    """REQ-015: The application does not require authentication; /health is accessible without sign-in."""
    reply = client.get("/health")
    assert reply.status_code == 200
    assert reply.json() == {"status": "ok"}


def test_anonymous_access_to_tasks():
    """REQ-015: The application does not require authentication; /tasks endpoints are accessible without sign-in."""
    # GET /tasks
    reply = client.get("/tasks")
    assert reply.status_code == 200
    # POST /tasks
    reply = client.post("/tasks", json={"title": "test"})
    assert reply.status_code == 201
    # PATCH /tasks/{id}/complete
    task_id = reply.json()["id"]
    reply = client.patch(f"/tasks/{task_id}/complete")
    assert reply.status_code == 200
    # DELETE /tasks/{id}
    reply = client.delete(f"/tasks/{task_id}")
    assert reply.status_code == 204


def test_anonymous_access_to_root():
    """REQ-015: The application does not require authentication; the root page is accessible without sign-in."""
    reply = client.get("/")
    assert reply.status_code == 200
    assert "Task Tracker" in reply.text
