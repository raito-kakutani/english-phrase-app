import mysql.connector

from app.db import create_connection

DEFAULT_USER_ID = 1


def process_phrase_submission(japanese: str, english: str) -> dict[str, int | str]:
    normalized_japanese = japanese.strip()
    normalized_english = english.strip()

    if not normalized_japanese or not normalized_english:
        raise ValueError("Both Japanese and English are required.")

    connection = create_connection()
    cursor = None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO phrases (user_id, japanese_text, english_text)
            VALUES (%s, %s, %s)
            """,
            (DEFAULT_USER_ID, normalized_japanese, normalized_english),
        )
        connection.commit()

        return {
            "status": "saved",
            "phrase_id": cursor.lastrowid,
            "user_id": DEFAULT_USER_ID,
        }
    except mysql.connector.Error as exc:
        raise RuntimeError(f"Failed to save phrase: {exc}") from exc
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()
