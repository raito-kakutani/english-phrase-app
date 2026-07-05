import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    return TestClient(app)


def test_submit_phrases_success(client, monkeypatch):
    monkeypatch.setattr(
        "app.main.process_phrase_submission",
        lambda japanese, english: {"status": "saved", "phrase_id": 1, "user_id": 1},
    )

    response = client.post(
        "/api/phrases",
        json={"japanese": "こんにちは", "english": "hello"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "saved", "phrase_id": 1, "user_id": 1}


def test_submit_phrases_validation_error_returns_400(client, monkeypatch):
    def raise_value_error(japanese, english):
        raise ValueError("Both Japanese and English are required.")

    monkeypatch.setattr("app.main.process_phrase_submission", raise_value_error)

    response = client.post("/api/phrases", json={"japanese": "", "english": ""})

    assert response.status_code == 400
    assert response.json()["detail"] == "Both Japanese and English are required."


def test_submit_phrases_db_error_returns_500(client, monkeypatch):
    def raise_runtime_error(japanese, english):
        raise RuntimeError("Failed to save phrase: db down")

    monkeypatch.setattr("app.main.process_phrase_submission", raise_runtime_error)

    response = client.post(
        "/api/phrases",
        json={"japanese": "こんにちは", "english": "hello"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to save phrase: db down"


def test_fetch_phrase_by_date_success(client, monkeypatch):
    monkeypatch.setattr(
        "app.main.get_phrases_by_date",
        lambda date_str, empty_message: [
            {"id": 1, "japanese_text": "a", "english_text": "b", "created_at": None}
        ],
    )

    response = client.get("/api/phrases/date/2026-07-05")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "japanese_text": "a", "english_text": "b", "created_at": None}
    ]


def test_fetch_phrase_by_date_not_found_returns_404(client, monkeypatch):
    def raise_value_error(date_str, empty_message):
        raise ValueError(empty_message)

    monkeypatch.setattr("app.main.get_phrases_by_date", raise_value_error)

    response = client.get("/api/phrases/date/2026-07-05")

    assert response.status_code == 404
    assert response.json()["detail"] == "2026-07-05のフレーズはありません。"


def test_fetch_phrase_by_date_db_error_returns_500(client, monkeypatch):
    def raise_runtime_error(date_str, empty_message):
        raise RuntimeError("Failed to load phrase: db down")

    monkeypatch.setattr("app.main.get_phrases_by_date", raise_runtime_error)

    response = client.get("/api/phrases/date/2026-07-05")

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to load phrase: db down"
