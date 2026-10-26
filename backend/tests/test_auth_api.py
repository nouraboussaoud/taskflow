from fastapi.testclient import TestClient


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
