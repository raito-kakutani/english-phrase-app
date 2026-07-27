from datetime import datetime
from unittest.mock import MagicMock

import mysql.connector
import pytest

from app.services import phrase_get


def make_connection(rows):
    cursor = MagicMock()
    cursor.fetchall.return_value = rows
    connection = MagicMock()
    connection.cursor.return_value = cursor
    return connection, cursor


def test_returns_phrases_with_isoformatted_dates(monkeypatch):
    created_at = datetime(2026, 7, 5, 9, 30)
    rows = [
        {
            "id": 1,
            "japanese_text": "こんにちは",
            "english_text": "hello",
            "created_at": created_at,
        }
    ]
    connection, cursor = make_connection(rows)
    monkeypatch.setattr(phrase_get, "create_connection", lambda: connection)

    result = phrase_get.get_phrases_by_date("2026-07-05", "no phrases", user_id=1)

    assert result == [
        {
            "id": 1,
            "japanese_text": "こんにちは",
            "english_text": "hello",
            "created_at": created_at.isoformat(),
        }
    ]

    sql, params = cursor.execute.call_args.args
    assert "FROM phrases" in sql
    assert params == (1, "2026-07-05")
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_handles_missing_created_at(monkeypatch):
    rows = [{"id": 1, "japanese_text": "a", "english_text": "b", "created_at": None}]
    connection, _ = make_connection(rows)
    monkeypatch.setattr(phrase_get, "create_connection", lambda: connection)

    result = phrase_get.get_phrases_by_date("2026-07-05", "no phrases", user_id=1)

    assert result[0]["created_at"] is None


def test_raises_value_error_when_no_phrases(monkeypatch):
    connection, _ = make_connection([])
    monkeypatch.setattr(phrase_get, "create_connection", lambda: connection)

    with pytest.raises(ValueError, match="no phrases for this date"):
        phrase_get.get_phrases_by_date("2026-07-05", "no phrases for this date", user_id=1)


def test_wraps_connector_errors_and_still_closes(monkeypatch):
    connection, cursor = make_connection([])
    cursor.execute.side_effect = mysql.connector.Error("syntax error")
    monkeypatch.setattr(phrase_get, "create_connection", lambda: connection)

    with pytest.raises(RuntimeError, match="Failed to load phrase"):
        phrase_get.get_phrases_by_date("2026-07-05", "no phrases", user_id=1)

    cursor.close.assert_called_once()
    connection.close.assert_called_once()
