from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)
test_user = {"username": "user@example.com", "password": "string"}


def test_login():
    response = client.post("/api/v1/auth/login", data=test_user)

    assert response.status_code == 204

    token = response.cookies.get("fastapiusersauth")

    assert token is not None
