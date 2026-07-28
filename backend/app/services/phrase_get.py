import mysql.connector

from app.db import create_connection


def get_phrases_by_date(
    date_str: str,
    empty_message: str,
    user_id: int,
) -> list[dict[str, int | str | None]]:
    connection = create_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            f"""
            SELECT id, japanese_text, english_text, created_at
            FROM phrases
            WHERE user_id = %s
              AND DATE(created_at) = %s
            ORDER BY created_at ASC, id ASC
            """,
            (user_id, date_str),
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
        raise RuntimeError(f"フレーズの取得に失敗しました: {exc}") from exc
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()
