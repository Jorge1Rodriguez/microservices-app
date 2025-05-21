import pytest
from fastapi.testclient import TestClient
from gateway.main import app

client = TestClient(app)

# Función auxiliar para obtener un token
def get_token():
    response = client.post(
        "/api/login",
        data={"username": "admin", "password": "admin123"}
    )
    return response.json()["access_token"]

def test_get_orders():
    token = get_token()
    response = client.get(
        "/api/orders",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_order():
    token = get_token()
    response = client.get(
        "/api/orders/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_create_order():
    token = get_token()
    order_data = {
        "products": [
            {"name": "Test Product", "price": 25.99, "quantity": 1}
        ],
        "total_amount": 25.99,
        "status": "pending"
    }
    response = client.post(
        "/api/orders",
        json=order_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["total_amount"] == 25.99
