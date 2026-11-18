from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Fixture: clear in-memory store before each test
# ---------------------------------------------------------------------------


def setup_function():
    # Reset the in-memory store (REQ-015)
    from app.main import in_memory_tasks, _next_id

    in_memory_tasks.clear()
    # Make _next_id writable again for tests
    import app.main as m

    m._next_id = 1


# ---------------------------------------------------------------------------
# REQ-001, REQ-002, REQ-003, REQ-004 — Create task
# ---------------------------------------------------------------------------


def test_create_task_minimal():
    """A team member creates a task with a title and no due_date (REQ-001, REQ-004)."""
    resp = client.post("/tasks", json={"title": "  Buy milk  "})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Buy milk"  # trimmed (REQ-002)
    assert data["status"] == "open"
    assert data["due_date"] is None
    assert isinstance(data["id"], int)


def test_create_task_with_due_date():
    """Create a task with a valid due_date (REQ-001, REQ-003)."""
    resp = client.post("/tasks", json={"title": "Task", "due_date": "2025-12-31"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["due_date"] == "2025-12-31"
    assert data["status"] == "open"


def test_create_task_title_empty():
    """Title after trimming is empty -> 422 (REQ-002)."""
    resp = client.post("/tasks", json={"title": "   "})
    assert resp.status_code == 422
    assert resp.json()["detail"][0]["msg"] == "title must be 1 to 120 characters"


def test_create_task_title_too_long():
    """Title longer than 120 chars after trimming -> 422 (REQ-002)."""
    long_title = "x" * 121
    resp = client.post("/tasks", json={"title": long_title})
    assert resp.status_code == 422
    assert resp.json()["detail"][0]["msg"] == "title must be 1 to 120 characters"


def test_create_task_invalid_due_date():
    """Invalid due_date format -> 422 (REQ-003)."""
    resp = client.post("/tasks", json={"title": "Valid", "due_date": "31-12-2025"})
    assert resp.status_code == 422
    assert resp.json()["detail"][0]["msg"] == "due_date must be YYYY-MM-DD"


def test_create_task_auto_id():
    """Each task gets a unique, incrementing integer id (REQ-004)."""
    r1 = client.post("/tasks", json={"title": "First"})
    r2 = client.post("/tasks", json={"title": "Second"})
    assert r1.json()["id"] == 1
    assert r2.json()["id"] == 2


# ---------------------------------------------------------------------------
# REQ-005, REQ-006 — List tasks
# ---------------------------------------------------------------------------


def test_list_tasks_newest_first():
    """List returns tasks ordered by id descending (newest first) (REQ-005)."""
    client.post("/tasks", json={"title": "A"})  # id 1
    client.post("/tasks", json={"title": "B"})  # id 2
    resp = client.get("/tasks")
    assert resp.status_code == 200
    tasks = resp.json()["tasks"]
    assert len(tasks) == 2
    assert tasks[0]["title"] == "B"
    assert tasks[1]["title"] == "A"


def test_list_tasks_filter_open():
    """Filter by status=open (REQ-006)."""
    client.post("/tasks", json={"title": "Open1"})
    client.post("/tasks", json={"title": "Open2"})
    done_id = client.post("/tasks", json={"title": "Done1"}).json()["id"]
    client.patch(f"/tasks/{done_id}/complete")
    resp = client.get("/tasks?status=open")
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.json()["tasks"]]
    assert "Open1" in titles
    assert "Open2" in titles
    assert "Done1" not in titles


def test_list_tasks_filter_done():
    """Filter by status=done (REQ-006)."""
    client.post("/tasks", json={"title": "Open"})
    done_id = client.post("/tasks", json={"title": "Done1"}).json()["id"]
    client.patch(f"/tasks/{done_id}/complete")
    resp = client.get("/tasks?status=done")
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.json()["tasks"]]
    assert "Done1" in titles
    assert "Open" not in titles


def test_list_tasks_invalid_status():
    """Invalid status filter -> 422 (REQ-006)."""
    resp = client.get("/tasks?status=invalid")
    assert resp.status_code == 422
    assert resp.json()["detail"] == "status must be open or done"


# ---------------------------------------------------------------------------
# REQ-007, REQ-008, REQ-009 — Complete task
# ---------------------------------------------------------------------------


def test_complete_open_task():
    """Mark an open task as done (REQ-007)."""
    create_resp = client.post("/tasks", json={"title": "Task1"})
    task_id = create_resp.json()["id"]
    resp = client.patch(f"/tasks/{task_id}/complete")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "done"
    assert data["id"] == task_id


def test_complete_already_done():
    """Completing an already done task -> 409 (REQ-008)."""
    create_resp = client.post("/tasks", json={"title": "Task1"})
    task_id = create_resp.json()["id"]
    client.patch(f"/tasks/{task_id}/complete")
    resp = client.patch(f"/tasks/{task_id}/complete")
    assert resp.status_code == 409
    assert resp.json()["detail"] == "task is already done"


def test_complete_nonexistent():
    """Completing a nonexistent task -> 404 (REQ-009)."""
    resp = client.patch("/tasks/9999/complete")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "task not found"


# ---------------------------------------------------------------------------
# REQ-009, REQ-010 — Delete task
# ---------------------------------------------------------------------------


def test_delete_task():
    """Delete a task -> 204, and it no longer appears in list (REQ-010)."""
    create_resp = client.post("/tasks", json={"title": "ToDelete"})
    task_id = create_resp.json()["id"]
    resp = client.delete(f"/tasks/{task_id}")
    assert resp.status_code == 204
    assert resp.text == ""
    # Verify it is gone
    list_resp = client.get("/tasks")
    task_ids = [t["id"] for t in list_resp.json()["tasks"]]
    assert task_id not in task_ids


def test_delete_nonexistent():
    """Delete a nonexistent task -> 404 (REQ-009)."""
    resp = client.delete("/tasks/9999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "task not found"


# ---------------------------------------------------------------------------
# REQ-014 — Health check (still works)
# ---------------------------------------------------------------------------

def test_health_is_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# REQ-015 — In-memory storage (tested implicitly by each test)
# ---------------------------------------------------------------------------

def test_in_memory_resets_on_restart():
    """After resetting the store, tasks are lost (REQ-015)."""
    client.post("/tasks", json={"title": "Vanishing"})
    from app.main import in_memory_tasks

    in_memory_tasks.clear()
    resp = client.get("/tasks")
    assert len(resp.json()["tasks"]) == 0
