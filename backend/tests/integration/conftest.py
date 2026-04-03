import pytest

from app import database


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Każdy test dostaje własną, tymczasową bazę danych."""
    test_db = tmp_path / "test_listings.db"
    monkeypatch.setattr(database, "DB_PATH", test_db)
    database.init_db()