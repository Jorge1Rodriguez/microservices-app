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

def test_get_users():
    token = get_token()
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_user():
    token = get_token()
    response = client.get(
        "/api/users/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_create_user():
    token = get_token()
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    response = client.post(
        "/api/users",
        json=user_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
