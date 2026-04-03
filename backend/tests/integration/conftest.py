import pytest

from app.database import init_db


@pytest.fixture(autouse=True)
def setup_db():
    init_db()