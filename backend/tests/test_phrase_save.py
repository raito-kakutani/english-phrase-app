from unittest.mock import MagicMock

import mysql.connector
import pytest

from app.services import phrase_save


def make_connection():
    cursor = MagicMock()
    cursor.lastrowid = 42
    connection = MagicMock()
    connection.cursor.return_value = cursor
    return connection, cursor


def test_rejects_blank_japanese(monkeypatch):
    connect = MagicMock()
    monkeypatch.setattr(phrase_save, "create_connection", connect)

    with pytest.raises(ValueError):
        phrase_save.process_phrase_submission(japanese="   ", english="hello", user_id=1)

    connect.assert_not_called()


def test_rejects_blank_english(monkeypatch):
    connect = MagicMock()
    monkeypatch.setattr(phrase_save, "create_connection", connect)

    with pytest.raises(ValueError):
        phrase_save.process_phrase_submission(japanese="こんにちは", english="   ", user_id=1)

    connect.assert_not_called()


def test_saves_trimmed_phrase_and_returns_id(monkeypatch):
    connection, cursor = make_connection()
    monkeypatch.setattr(phrase_save, "create_connection", lambda: connection)

    result = phrase_save.process_phrase_submission(
        japanese="  こんにちは  ",
        english="  hello  ",
        user_id=1,
    )

    assert result == {"status": "saved", "phrase_id": 42, "user_id": 1}

    cursor.execute.assert_called_once()
    sql, params = cursor.execute.call_args.args
    assert "INSERT INTO phrases" in sql
    assert params == (1, "こんにちは", "hello")

    connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_wraps_connector_errors_and_still_closes(monkeypatch):
    connection, cursor = make_connection()
    cursor.execute.side_effect = mysql.connector.Error("duplicate key")
    monkeypatch.setattr(phrase_save, "create_connection", lambda: connection)

    with pytest.raises(RuntimeError, match="フレーズの保存に失敗しました"):
        phrase_save.process_phrase_submission(japanese="こんにちは", english="hello", user_id=1)

    cursor.close.assert_called_once()
    connection.close.assert_called_once()
    connection.commit.assert_not_called()
