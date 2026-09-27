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


def test_create_order():
    response = client.post("/orders", json={"item_id": 1, "quantity": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 2
    assert data["total"] == 498


def test_order_not_found():
    response = client.get("/orders/9999")
    assert response.status_code == 404
