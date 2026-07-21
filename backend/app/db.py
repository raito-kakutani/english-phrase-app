from pathlib import Path
import os


ENV_PATH = Path(__file__).resolve().parent / ".env"

# 環境変数ファイル読み込み
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


def _get_setting(key: str, default: str | None = None) -> str:
    env_values = _load_env_file()
    value = os.getenv(key) or env_values.get(key) or default
    if value is None:
        raise RuntimeError(f"{key} is not set. Define it in the environment or in backend/app/.env.")
    return value


def create_connection():
    try:
        import mysql.connector
    except ImportError as exc:
        raise RuntimeError(
            "mysql-connector-python is not installed. Run `pip install -r requirements.txt`."
        ) from exc

    try:
        return mysql.connector.connect(
            host=_get_setting("MYSQL_HOST", "127.0.0.1"),
            port=int(_get_setting("MYSQL_PORT", "3306")),
            user=_get_setting("MYSQL_USER", "app_user"),
            password=_get_setting("MYSQL_PASSWORD"),
            database=_get_setting("MYSQL_DATABASE", "english_app"),
        )
    except mysql.connector.Error as exc:
        raise RuntimeError(f"Failed to connect to MySQL: {exc}") from exc
