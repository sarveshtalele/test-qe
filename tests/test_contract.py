"""Written by the Agentic QE Platform from the contract approved at Gate A. Do not edit: the platform rewrites this file on every build."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def _has(reply, text):
    assert any(text in s for s in _strings(reply.json())), f"{text!r} is not in {reply.text[:300]}"


def _keys(reply, keys):  # ponytail: an empty list body shows no item, so its keys are not checked
    body = reply.json()
    body = body[0] if isinstance(body, list) and body else body
    if isinstance(body, dict):
        for key in keys:
            assert key in body, f"{key!r} is not in {reply.text[:300]}"


def test_health_check_200():
    reply = client.request('GET', '/health')
    assert reply.status_code == 200, reply.text
    assert reply.json()['status'] == 'ok'
