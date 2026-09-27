import logging

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_menu():
    response = client.get("/menu")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_ui_click_is_logged(caplog):
    with caplog.at_level(logging.DEBUG, logger="quickbite"):
        response = client.post("/ui-events", json={"target": "button#cart-btn"})

    assert response.status_code == 204
    assert "UI click: target=button#cart-btn" in caplog.text


def test_ui_status_is_logged(caplog):
    with caplog.at_level(logging.DEBUG, logger="quickbite"):
        response = client.post(
            "/ui-events/status",
            json={"message": "Add something to your cart first."},
        )

    assert response.status_code == 204
    assert "UI status: Add something to your cart first." in caplog.text


def test_create_order():
    response = client.post("/orders", json={"item_id": 1, "quantity": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 2
    assert data["total"] == 498


def test_order_not_found():
    response = client.get("/orders/9999")
    assert response.status_code == 404
