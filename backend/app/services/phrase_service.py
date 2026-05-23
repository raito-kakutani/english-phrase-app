from pathlib import Path
import os


DEFAULT_USER_ID = 1
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def _load_env_file() -> dict[str, str]:
    if not ENV_PATH.exists():
        return {}

    values: dict[str, str] = {}
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("#") or "=" not in stripped_line:
            continue

        key, value = stripped_line.split("=", 1)
        values[key.strip()] = value.strip()

    return values


def _get_setting(key: str, default: str) -> str:
    env_values = _load_env_file()
    return os.getenv(key) or env_values.get(key) or default


def process_phrase_submission(japanese: str, english: str) -> dict[str, int | str]:
    normalized_japanese = japanese.strip()
    normalized_english = english.strip()

    if not normalized_japanese or not normalized_english:
        raise ValueError("Both Japanese and English are required.")

    try:
        import mysql.connector
    except ImportError as exc:
        raise RuntimeError(
            "mysql-connector-python is not installed. Run `pip install -r requirements.txt`."
        ) from exc

    try:
        connection = mysql.connector.connect(
            host=_get_setting("MYSQL_HOST", "127.0.0.1"),
            port=int(_get_setting("MYSQL_PORT", "3307")),
            user=_get_setting("MYSQL_USER", "app_user"),
            password=_get_setting("MYSQL_PASSWORD", "english_app"),
            database=_get_setting("MYSQL_DATABASE", "english_app"),
        )
    except mysql.connector.Error as exc:
        raise RuntimeError(f"Failed to connect to MySQL: {exc}") from exc

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
