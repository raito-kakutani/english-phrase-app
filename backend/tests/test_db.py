import mysql.connector
import pytest

from app import db


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    """Keep tests from depending on the developer's real backend/app/.env file."""
    monkeypatch.setattr(db, "ENV_PATH", tmp_path / ".env")
    for key in ("MYSQL_HOST", "MYSQL_PORT", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE"):
        monkeypatch.delenv(key, raising=False)


def test_get_setting_prefers_env_var_over_file(tmp_path, monkeypatch):
    db.ENV_PATH.write_text("MYSQL_USER=from_file\n", encoding="utf-8")
    monkeypatch.setenv("MYSQL_USER", "from_env")

    assert db._get_setting("MYSQL_USER") == "from_env"


def test_get_setting_falls_back_to_env_file(tmp_path):
    db.ENV_PATH.write_text("MYSQL_USER=from_file\n", encoding="utf-8")

    assert db._get_setting("MYSQL_USER") == "from_file"


def test_load_env_file_skips_blank_lines_and_comments(tmp_path):
    db.ENV_PATH.write_text(
        "\n# a comment\nMYSQL_USER=app_user\nMALFORMED_LINE\n",
        encoding="utf-8",
    )

    assert db._load_env_file() == {"MYSQL_USER": "app_user"}


def test_load_env_file_returns_empty_dict_when_missing():
    assert not db.ENV_PATH.exists()
    assert db._load_env_file() == {}


def test_get_setting_uses_default_when_unset():
    assert db._get_setting("MYSQL_HOST", "127.0.0.1") == "127.0.0.1"


def test_get_setting_raises_when_required_and_unset():
    with pytest.raises(RuntimeError, match="MYSQL_PASSWORD is not set"):
        db._get_setting("MYSQL_PASSWORD")


def test_create_connection_passes_settings_to_connector(monkeypatch):
    monkeypatch.setenv("MYSQL_HOST", "db.internal")
    monkeypatch.setenv("MYSQL_PORT", "3306")
    monkeypatch.setenv("MYSQL_USER", "app_user")
    monkeypatch.setenv("MYSQL_PASSWORD", "secret")
    monkeypatch.setenv("MYSQL_DATABASE", "english_app")

    captured = {}

    def fake_connect(**kwargs):
        captured.update(kwargs)
        return "connection"

    monkeypatch.setattr(mysql.connector, "connect", fake_connect)

    result = db.create_connection()

    assert result == "connection"
    assert captured == {
        "host": "db.internal",
        "port": 3306,
        "user": "app_user",
        "password": "secret",
        "database": "english_app",
    }


def test_create_connection_wraps_connector_errors(monkeypatch):
    monkeypatch.setenv("MYSQL_PASSWORD", "secret")

    def fake_connect(**kwargs):
        raise mysql.connector.Error("connection refused")

    monkeypatch.setattr(mysql.connector, "connect", fake_connect)

    with pytest.raises(RuntimeError, match="MySQLへの接続に失敗しました"):
        db.create_connection()
