import bcrypt
import mysql.connector

from app.db import create_connection
from app.services.session import create_session


def authenticate_user(email: str, password: str) -> dict[str, int | str]:
    normalized_email = email.strip().lower()

    connection = create_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, password_hash FROM users WHERE email = %s",
            (normalized_email,),
        )
        user = cursor.fetchone()
    except mysql.connector.Error as exc:
        raise RuntimeError(f"Failed to authenticate user: {exc}") from exc
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

    if user is None or not bcrypt.checkpw(
        password.encode("utf-8"), user["password_hash"].encode("utf-8")
    ):
        raise ValueError("Invalid email or password.")

    session = create_session(user["id"])

    return {
        "user_id": user["id"],
        "session_token": session["session_token"],
        "expires_at": session["expires_at"],
    }
