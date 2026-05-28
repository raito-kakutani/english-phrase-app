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
        import mysql.connector

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


def get_phrases_by_day_offset(
    day_offset: int,
    empty_message: str,
) -> list[dict[str, int | str | None]]:
    connection = create_connection()
    cursor = None

    try:
        import mysql.connector

        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, japanese_text, english_text, created_at
            FROM phrases
            WHERE user_id = %s
              AND DATE(created_at) = DATE_ADD(CURRENT_DATE(), INTERVAL %s DAY)
            ORDER BY created_at ASC, id ASC
            """,
            (DEFAULT_USER_ID, day_offset),
        )
        phrases = cursor.fetchall()

        if not phrases:
            raise ValueError(empty_message)

        return [
            {
                "id": phrase["id"],
                "japanese_text": phrase["japanese_text"],
                "english_text": phrase["english_text"],
                "created_at": phrase["created_at"].isoformat()
                if phrase["created_at"] is not None
                else None,
            }
            for phrase in phrases
        ]
    except mysql.connector.Error as exc:
        raise RuntimeError(f"Failed to load phrase: {exc}") from exc
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()
