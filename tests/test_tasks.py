from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_task_minimum():
    payload = {"title": "Test task"}
    reply = client.post("/tasks", json=payload)
    assert reply.status_code == 201
    data = reply.json()
    assert data["title"] == "Test task"
    assert data["status"] == "open"
    assert isinstance(data["id"], int)
    assert "created_at" in data
    assert data["due_date"] is None


def test_create_task_with_due_date():
    payload = {"title": "Task with due date", "due_date": "2025-12-31"}
    reply = client.post("/tasks", json=payload)
    assert reply.status_code == 201
    data = reply.json()
    assert data["due_date"] == "2025-12-31"


def test_create_task_title_trimmed():
    payload = {"title": "  spaced title  "}
    reply = client.post("/tasks", json=payload)
    assert reply.status_code == 201
    assert reply.json()["title"] == "spaced title"


def test_create_task_title_missing():
    reply = client.post("/tasks", json={})
    assert reply.status_code == 422
    assert reply.json()["detail"][0]["msg"]


def test_create_task_title_too_long():
    payload = {"title": "a" * 121}
    reply = client.post("/tasks", json=payload)
    assert reply.status_code == 422
    detail = reply.json()["detail"]
    # Pydantic v2 wraps errors in a list of dicts with 'msg'
    errors = [e.get("msg", "") if isinstance(e, dict) else str(e) for e in detail]
    # Flatten all 'msg' values from each error
    msgs = []
    for e in detail:
        if isinstance(e, dict) and "msg" in e:
            msgs.append(e["msg"])
        elif isinstance(e, dict):
            for v in e.values():
                msgs.append(str(v))
        else:
            msgs.append(str(e))
    assert any("title must be 1 to 120 characters" in m for m in msgs)


def test_create_task_title_after_trim_too_long():
    payload = {"title": "a" * 121 + " "}
    reply = client.post("/tasks", json=payload)
    assert reply.status_code == 422
    detail = reply.json()["detail"]
    errors = [e.get("msg", "") if isinstance(e, dict) else str(e) for e in detail]
    msgs = []
    for e in detail:
        if isinstance(e, dict) and "msg" in e:
            msgs.append(e["msg"])
        elif isinstance(e, dict):
            for v in e.values():
                msgs.append(str(v))
        else:
            msgs.append(str(e))
    assert any("title must be 1 to 120 characters" in m for m in msgs)


def test_create_task_title_empty_after_trim():
    payload = {"title": "   "}
    reply = client.post("/tasks", json=payload)
    assert reply.status_code == 422
    detail = reply.json()["detail"]
    errors = [e.get("msg", "") if isinstance(e, dict) else str(e) for e in detail]
    msgs = []
    for e in detail:
        if isinstance(e, dict) and "msg" in e:
            msgs.append(e["msg"])
        elif isinstance(e, dict):
            for v in e.values():
                msgs.append(str(v))
        else:
            msgs.append(str(e))
    assert any("title must be 1 to 120 characters" in m for m in msgs)


def test_create_task_invalid_due_date():
    payload = {"title": "Task", "due_date": "31-12-2025"}
    reply = client.post("/tasks", json=payload)
    assert reply.status_code == 422
    detail = reply.json()["detail"]
    errors = [e.get("msg", "") if isinstance(e, dict) else str(e) for e in detail]
    assert any("due_date must be YYYY-MM-DD" in e for e in errors)


def test_list_tasks_newest_first():
    # Clear by creating fresh tasks (shared DB; order relies on created_at)
    r1 = client.post("/tasks", json={"title": "First"})
    r2 = client.post("/tasks", json={"title": "Second"})
    r3 = client.post("/tasks", json={"title": "Third"})
    reply = client.get("/tasks")
    assert reply.status_code == 200
    tasks = reply.json()
    # The newest first: Third, Second, First
    assert [t["title"] for t in tasks[:3]] == ["Third", "Second", "First"]


def test_list_tasks_filter_open():
    # Create one open and one done task
    open_task = client.post("/tasks", json={"title": "Open task"}).json()
    done_task = client.post("/tasks", json={"title": "Done task"}).json()
    client.patch(f"/tasks/{done_task['id']}/complete")
    reply = client.get("/tasks", params={"status": "open"})
    assert reply.status_code == 200
    tasks = reply.json()
    for t in tasks:
        assert t["status"] == "open"
    assert any(t["id"] == open_task["id"] for t in tasks)


def test_list_tasks_filter_done():
    reply = client.get("/tasks", params={"status": "done"})
    assert reply.status_code == 200
    tasks = reply.json()
    for t in tasks:
        assert t["status"] == "done"


def test_list_tasks_invalid_status():
    reply = client.get("/tasks", params={"status": "invalid"})
    assert reply.status_code == 422
    assert reply.json()["detail"] == "status must be open or done"


def test_complete_task():
    task = client.post("/tasks", json={"title": "Complete me"}).json()
    reply = client.patch(f"/tasks/{task['id']}/complete")
    assert reply.status_code == 200
    data = reply.json()
    assert data["status"] == "done"
    assert data["id"] == task["id"]


def test_complete_task_already_done():
    task = client.post("/tasks", json={"title": "Already done"}).json()
    client.patch(f"/tasks/{task['id']}/complete")
    reply = client.patch(f"/tasks/{task['id']}/complete")
    assert reply.status_code == 409
    assert reply.json()["detail"] == "task is already done"


def test_complete_task_not_found():
    reply = client.patch("/tasks/99999/complete")
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"


def test_delete_task():
    task = client.post("/tasks", json={"title": "Delete me"}).json()
    reply = client.delete(f"/tasks/{task['id']}")
    assert reply.status_code == 204
    assert reply.text == ""
    # Verify it no longer appears
    tasks = client.get("/tasks").json()
    assert not any(t["id"] == task["id"] for t in tasks)


def test_delete_task_not_found():
    reply = client.delete("/tasks/99999")
    assert reply.status_code == 404
    assert reply.json()["detail"] == "task not found"
