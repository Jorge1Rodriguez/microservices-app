import pytest
from fastapi.testclient import TestClient
from gateway.main import app

client = TestClient(app)

def test_login():
    response = client.post(
        "/api/login",
        data={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_bad_credentials():
    response = client.post(
        "/api/login",
        data={"username": "admin", "password": "wrong_password"}
    )
    assert response.status_code == 401
