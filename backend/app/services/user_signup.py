import re

import bcrypt
import mysql.connector

from app.db import create_connection

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


def create_user(
    email: str,
    password: str,
    first_name: str | None = None,
    last_name: str | None = None,
) -> dict[str, int | str]:
    normalized_email = email.strip().lower()

    if not EMAIL_PATTERN.match(normalized_email):
        raise ValueError("有効なメールアドレスを入力してください。")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"パスワードは{MIN_PASSWORD_LENGTH}文字以上で入力してください。")

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    connection = create_connection()
    cursor = None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO users (email, password_hash, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            """,
            (normalized_email, password_hash, first_name, last_name),
        )
        connection.commit()

        return {
            "status": "created",
            "user_id": cursor.lastrowid,
            "email": normalized_email,
        }
    except mysql.connector.IntegrityError as exc:
        raise ValueError("このメールアドレスは既に登録されています。") from exc
    except mysql.connector.Error as exc:
        raise RuntimeError(f"ユーザー登録に失敗しました: {exc}") from exc
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()
