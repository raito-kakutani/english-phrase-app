import pytest
from fastapi.testclient import TestClient

from app.main import app, get_current_user_id


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def authed_client():
    app.dependency_overrides[get_current_user_id] = lambda: 1
    client = TestClient(app)
    yield client
    app.dependency_overrides.pop(get_current_user_id, None)


def test_submit_phrases_success(authed_client, monkeypatch):
    monkeypatch.setattr(
        "app.main.process_phrase_submission",
        lambda japanese, english, user_id: {"status": "saved", "phrase_id": 1, "user_id": 1},
    )

    response = authed_client.post(
        "/api/phrases",
        json={"japanese": "こんにちは", "english": "hello"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "saved", "phrase_id": 1, "user_id": 1}


def test_submit_phrases_requires_login(client):
    response = client.post(
        "/api/phrases",
        json={"japanese": "こんにちは", "english": "hello"},
    )

    assert response.status_code == 401


def test_submit_phrases_validation_error_returns_400(authed_client, monkeypatch):
    def raise_value_error(japanese, english, user_id):
        raise ValueError("Both Japanese and English are required.")

    monkeypatch.setattr("app.main.process_phrase_submission", raise_value_error)

    response = authed_client.post("/api/phrases", json={"japanese": "", "english": ""})

    assert response.status_code == 400
    assert response.json()["detail"] == "Both Japanese and English are required."


def test_submit_phrases_db_error_returns_500(authed_client, monkeypatch):
    def raise_runtime_error(japanese, english, user_id):
        raise RuntimeError("Failed to save phrase: db down")

    monkeypatch.setattr("app.main.process_phrase_submission", raise_runtime_error)

    response = authed_client.post(
        "/api/phrases",
        json={"japanese": "こんにちは", "english": "hello"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to save phrase: db down"


def test_fetch_phrase_by_date_success(authed_client, monkeypatch):
    monkeypatch.setattr(
        "app.main.get_phrases_by_date",
        lambda date_str, empty_message, user_id: [
            {"id": 1, "japanese_text": "a", "english_text": "b", "created_at": None}
        ],
    )

    response = authed_client.get("/api/phrases/date/2026-07-05")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "japanese_text": "a", "english_text": "b", "created_at": None}
    ]


def test_fetch_phrase_by_date_requires_login(client):
    response = client.get("/api/phrases/date/2026-07-05")

    assert response.status_code == 401


def test_fetch_phrase_by_date_not_found_returns_404(authed_client, monkeypatch):
    def raise_value_error(date_str, empty_message, user_id):
        raise ValueError(empty_message)

    monkeypatch.setattr("app.main.get_phrases_by_date", raise_value_error)

    response = authed_client.get("/api/phrases/date/2026-07-05")

    assert response.status_code == 404
    assert response.json()["detail"] == "2026-07-05のフレーズはありません。"


def test_fetch_phrase_by_date_db_error_returns_500(authed_client, monkeypatch):
    def raise_runtime_error(date_str, empty_message, user_id):
        raise RuntimeError("Failed to load phrase: db down")

    monkeypatch.setattr("app.main.get_phrases_by_date", raise_runtime_error)

    response = authed_client.get("/api/phrases/date/2026-07-05")

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to load phrase: db down"


def test_signup_success(client, monkeypatch):
    monkeypatch.setattr(
        "app.main.create_user",
        lambda email, password, first_name, last_name: {
            "status": "created",
            "user_id": 1,
            "email": email,
        },
    )

    response = client.post(
        "/api/auth/signup",
        json={"email": "a@example.com", "password": "supersecret123"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "created", "user_id": 1, "email": "a@example.com"}


def test_signup_validation_error_returns_400(client, monkeypatch):
    def raise_value_error(email, password, first_name, last_name):
        raise ValueError("A valid email address is required.")

    monkeypatch.setattr("app.main.create_user", raise_value_error)

    response = client.post(
        "/api/auth/signup",
        json={"email": "not-an-email", "password": "supersecret123"},
    )

    assert response.status_code == 400


def test_login_success_sets_cookie(client, monkeypatch):
    monkeypatch.setattr(
        "app.main.authenticate_user",
        lambda email, password: {
            "user_id": 1,
            "session_token": "tok123",
            "expires_at": "later",
        },
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "a@example.com", "password": "supersecret123"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "logged_in", "user_id": 1}
    assert response.cookies.get("session_token") == "tok123"


def test_login_invalid_credentials_returns_401(client, monkeypatch):
    def raise_value_error(email, password):
        raise ValueError("Invalid email or password.")

    monkeypatch.setattr("app.main.authenticate_user", raise_value_error)

    response = client.post(
        "/api/auth/login",
        json={"email": "a@example.com", "password": "wrong"},
    )

    assert response.status_code == 401


def test_logout_clears_cookie(client, monkeypatch):
    deleted_tokens = []
    monkeypatch.setattr("app.main.delete_session", deleted_tokens.append)

    client.cookies.set("session_token", "tok123")
    response = client.post("/api/auth/logout")

    assert response.status_code == 200
    assert deleted_tokens == ["tok123"]
    assert response.cookies.get("session_token") is None


def test_me_requires_login(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_me_returns_user_id(authed_client):
    response = authed_client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json() == {"user_id": 1}
