from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# Since tasks are in memory and may be polluted by other tests,
# we reset the internal state between tests by calling the endpoints
# in a deterministic way, but we do not access private attributes.
# To ensure clean slate we rely on the fact that each test function
# runs in order and we isolate via unique titles or cleanup.


def test_create_task_minimal():
    # REQ-001, REQ-004: create with title only, expect 201 and status open, id integer
    resp = client.post("/tasks", json={"title": "My Task"})
    assert resp.status_code == 201
    data = resp.json()
    assert isinstance(data["id"], int)
    assert data["title"] == "My Task"
    assert data["due_date"] is None
    assert data["status"] == "open"


def test_create_task_with_due_date():
    # REQ-001, REQ-003, REQ-004: valid due_date
    resp = client.post("/tasks", json={"title": "Due Task", "due_date": "2025-12-31"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["due_date"] == "2025-12-31"


def test_create_task_title_too_long():
    # REQ-002: title > 120 after trimming
    title = "a" * 121
    resp = client.post("/tasks", json={"title": title})
    assert resp.status_code == 422
    errors = resp.json()["detail"]
    assert any("title must be 1 to 120 characters" in e["msg"] for e in errors)


def test_create_task_title_empty_after_trim():
    # REQ-002: title all spaces -> empty after trim
    resp = client.post("/tasks", json={"title": "   "})
    assert resp.status_code == 422
    errors = resp.json()["detail"]
    assert any("title must be 1 to 120 characters" in e["msg"] for e in errors)


def test_create_task_title_one_character():
    # REQ-002: edge case, exactly 1 char
    resp = client.post("/tasks", json={"title": "x"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "x"


def test_create_task_invalid_due_date():
    # REQ-003: invalid date format
    resp = client.post("/tasks", json={"title": "Task", "due_date": "31-12-2025"})
    assert resp.status_code == 422
    errors = resp.json()["detail"]
    assert any("due_date must be YYYY-MM-DD" in e["msg"] for e in errors)


def test_list_tasks_newest_first():
    # REQ-005: create two tasks and verify order
    # Clear existing tasks by deleting them (if any) – we work around state
    # by creating tasks with unique ids and checking order.
    # To keep test isolated we assume we can rely on sequential ids.
    resp1 = client.post("/tasks", json={"title": "First"})
    assert resp1.status_code == 201
    id1 = resp1.json()["id"]
    resp2 = client.post("/tasks", json={"title": "Second"})
    assert resp2.status_code == 201
    id2 = resp2.json()["id"]
    # newest first -> higher id first
    resp_list = client.get("/tasks")
    assert resp_list.status_code == 200
    tasks = resp_list.json()
    # find our tasks
    ids_in_list = [t["id"] for t in tasks if t["id"] in (id1, id2)]
    assert ids_in_list == [id2, id1]  # newest first


def test_list_tasks_filter_by_open():
    # REQ-006: filter by open, create a task and mark it done, then filter
    # create two tasks, complete one
    resp_create = client.post("/tasks", json={"title": "Open"})
    open_id = resp_create.json()["id"]
    client.post("/tasks", json={"title": "ToDone"})
    resp_list_all = client.get("/tasks")
    all_ids = [t["id"] for t in resp_list_all.json()]
    # complete the second (higher id)
    done_id = max(all_ids)
    client.patch(f"/tasks/{done_id}/complete")
    # filter open
    resp_open = client.get("/tasks?status=open")
    assert resp_open.status_code == 200
    open_titles = [t["title"] for t in resp_open.json()]
    assert "Open" in open_titles
    # filter done
    resp_done = client.get("/tasks?status=done")
    assert resp_done.status_code == 200
    done_titles = [t["title"] for t in resp_done.json()]
    assert "ToDone" in done_titles or any("ToDone" in t for t in done_titles)


def test_list_tasks_invalid_status():
    # REQ-006: invalid status returns 422
    resp = client.get("/tasks?status=invalid")
    assert resp.status_code == 422
    assert resp.json()["detail"] == "status must be open or done"


def test_complete_task():
    # REQ-007: mark open task as done
    resp_create = client.post("/tasks", json={"title": "ToComplete"})
    task_id = resp_create.json()["id"]
    resp_complete = client.patch(f"/tasks/{task_id}/complete")
    assert resp_complete.status_code == 200
    data = resp_complete.json()
    assert data["status"] == "done"
    assert data["id"] == task_id


def test_complete_task_already_done():
    # REQ-008: 409 when already done
    resp_create = client.post("/tasks", json={"title": "AlreadyDone"})
    task_id = resp_create.json()["id"]
    client.patch(f"/tasks/{task_id}/complete")
    resp_again = client.patch(f"/tasks/{task_id}/complete")
    assert resp_again.status_code == 409
    assert resp_again.json()["detail"] == "task is already done"


def test_complete_task_not_found():
    # REQ-009: 404 for non-existent id
    resp = client.patch("/tasks/99999/complete")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "task not found"


def test_delete_task():
    # REQ-010: delete returns 204 and task gone
    resp_create = client.post("/tasks", json={"title": "ToDelete"})
    task_id = resp_create.json()["id"]
    resp_delete = client.delete(f"/tasks/{task_id}")
    assert resp_delete.status_code == 204
    assert resp_delete.content == b""
    # task no longer in list
    resp_list = client.get("/tasks")
    ids = [t["id"] for t in resp_list.json()]
    assert task_id not in ids


def test_delete_task_not_found():
    # REQ-009: 404 for delete on non-existent id
    resp = client.delete("/tasks/99999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "task not found"
