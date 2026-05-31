import mysql.connector

from app.db import create_connection

DEFAULT_USER_ID = 1

# =====================================================
# 指定した日付のフレーズ取得処理
# =====================================================
def get_phrases_by_day_offset(
    day_offset: int,
    empty_message: str,
) -> list[dict[str, int | str | None]]:
    connection = create_connection()
    cursor = None

    try:
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
