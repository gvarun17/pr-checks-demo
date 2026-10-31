import pytest
from fastapi.testclient import TestClient

from app.main import _ITEMS, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_items() -> None:
    _ITEMS.clear()


def test_healthz() -> None:
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_and_get_item() -> None:
    payload = {"id": 1, "name": "widget", "price": 9.99}
    assert client.post("/items", json=payload).status_code == 201
    resp = client.get("/items/1")
    assert resp.status_code == 200
    assert resp.json() == payload


def test_duplicate_item_conflicts() -> None:
    payload = {"id": 1, "name": "widget", "price": 1.0}
    client.post("/items", json=payload)
    assert client.post("/items", json=payload).status_code == 409


def test_missing_item_404() -> None:
    assert client.get("/items/42").status_code == 404


def test_invalid_price_rejected() -> None:
    resp = client.post("/items", json={"id": 2, "name": "bad", "price": -1})
    assert resp.status_code == 422
