import pytest

import app as app_module
import database


@pytest.fixture
def db(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.init_db()
    return database


@pytest.fixture
def client(db):
    app = app_module.create_app()
    app.config["TESTING"] = True
    return app.test_client()
