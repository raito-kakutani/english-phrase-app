import mysql.connector

from app.db import create_connection


def process_phrase_submission(japanese: str, english: str, user_id: int) -> dict[str, int | str]:
    normalized_japanese = japanese.strip()
    normalized_english = english.strip()

    if not normalized_japanese or not normalized_english:
        raise ValueError("日本語と英語の両方を入力してください。")

    connection = create_connection()
    cursor = None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO phrases (user_id, japanese_text, english_text)
            VALUES (%s, %s, %s)
            """,
            (user_id, normalized_japanese, normalized_english),
        )
        connection.commit()

        return {
            "status": "saved",
            "phrase_id": cursor.lastrowid,
            "user_id": user_id,
        }
    except mysql.connector.Error as exc:
        raise RuntimeError(f"フレーズの保存に失敗しました: {exc}") from exc
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()
