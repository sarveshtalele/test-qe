from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_is_ok():
    reply = client.get("/health")
    assert reply.status_code == 200
    assert reply.json() == {"status": "ok"}


def test_page_is_served():
    reply = client.get("/")
    assert reply.status_code == 200
    assert "<h1>App</h1>" in reply.text


def test_health_method_must_be_get():
    # POST, PUT, DELETE, etc. should not be allowed
    reply = client.post("/health")
    assert reply.status_code == 405
    reply = client.put("/health")
    assert reply.status_code == 405
    reply = client.delete("/health")
    assert reply.status_code == 405
    reply = client.patch("/health")
    assert reply.status_code == 405


def test_health_response_has_only_status_key():
    reply = client.get("/health")
    assert set(reply.json().keys()) == {"status"}
