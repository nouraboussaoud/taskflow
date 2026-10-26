from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


def test_register_login_and_reject_duplicate_email(client: TestClient) -> None:
    payload = {"email": "ada@example.com", "password": "a-safe-test-password"}

    registered = client.post("/api/v1/auth/register", json=payload)
    duplicate = client.post("/api/v1/auth/register", json=payload)
    logged_in = client.post("/api/v1/auth/login", json=payload)

    assert registered.status_code == 201
    assert registered.json()["email"] == "ada@example.com"
    assert "password_hash" not in registered.json()
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "http_error"
    assert logged_in.status_code == 200
    assert logged_in.json()["token_type"] == "bearer"


def test_invalid_login_and_missing_token_return_401(client: TestClient) -> None:
    invalid_login = client.post(
        "/api/v1/auth/login", json={"email": "missing@example.com", "password": "wrong-password"}
    )
    protected = client.get("/api/v1/projects")

    assert invalid_login.status_code == 401
    assert protected.status_code == 401
    assert protected.headers["www-authenticate"] == "Bearer"


def test_unexpected_error_keeps_cors_header_for_configured_origin() -> None:
    # Simulate an internal failure without writing a user to the test database.
    with patch("app.api.routes.auth.hash_password", side_effect=RuntimeError("test failure")):
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.post(
                "/api/v1/auth/register",
                headers={"Origin": "http://localhost:5173"},
                json={"email": "test@example.com", "password": "a-safe-test-password"},
            )

    assert response.status_code == 500
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert response.json()["error"]["code"] == "internal_error"
