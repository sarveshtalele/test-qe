from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def setup_function():
    from app.main import in_memory_tasks, _next_id

    in_memory_tasks.clear()
    import app.main as m

    m._next_id = 1


def test_health_is_ok():
    reply = client.get("/health")
    assert reply.status_code == 200
    assert reply.json() == {"status": "ok"}


def test_page_is_served():
    reply = client.get("/")
    assert reply.status_code == 200
    assert "Task Tracker" in reply.text
