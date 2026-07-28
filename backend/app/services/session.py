import secrets
from datetime import datetime, timedelta, timezone

import mysql.connector

from app.db import create_connection

SESSION_LIFETIME = timedelta(days=7)
SESSION_LIFETIME_SECONDS = int(SESSION_LIFETIME.total_seconds())


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def create_session(user_id: int) -> dict[str, str]:
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + SESSION_LIFETIME

    connection = create_connection()
    cursor = None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO sessions (session_token, user_id, expires_at)
            VALUES (%s, %s, %s)
            """,
            (session_token, user_id, expires_at),
        )
        connection.commit()

        return {"session_token": session_token, "expires_at": expires_at}
    except mysql.connector.Error as exc:
        raise RuntimeError(f"セッションの作成に失敗しました: {exc}") from exc
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def get_user_id_for_token(session_token: str) -> int | None:
    connection = create_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT user_id, expires_at
            FROM sessions
            WHERE session_token = %s
            """,
            (session_token,),
        )
        row = cursor.fetchone()

        if row is None:
            return None

        if _as_utc(row["expires_at"]) < datetime.now(timezone.utc):
            return None

        return row["user_id"]
    except mysql.connector.Error as exc:
        raise RuntimeError(f"セッションの確認に失敗しました: {exc}") from exc
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def delete_session(session_token: str) -> None:
    connection = create_connection()
    cursor = None

    try:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM sessions WHERE session_token = %s",
            (session_token,),
        )
        connection.commit()
    except mysql.connector.Error as exc:
        raise RuntimeError(f"セッションの削除に失敗しました: {exc}") from exc
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()
