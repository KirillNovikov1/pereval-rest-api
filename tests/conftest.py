from __future__ import annotations

import base64
import os

import pytest

TEST_DB_URL = "sqlite:///test_pereval.db"
os.environ["FSTR_DB_URL"] = TEST_DB_URL

from app import create_app  # noqa: E402
from database import Database  # noqa: E402
from models import Base  # noqa: E402


@pytest.fixture()
def database() -> Database:
    db = Database(TEST_DB_URL)
    Base.metadata.drop_all(db.engine)
    Base.metadata.create_all(db.engine)
    yield db
    Base.metadata.drop_all(db.engine)


@pytest.fixture()
def client(database: Database):
    app = create_app(database)
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def valid_payload() -> dict:
    return {
        "beautyTitle": "пер.",
        "title": "Пхия",
        "other_titles": "Триев",
        "connect": "",
        "add_time": "2026-03-22 12:00:00",
        "user": {
            "email": "user@example.com",
            "phone": "+79990001122",
            "fam": "Иванов",
            "name": "Иван",
            "otc": "Иванович",
        },
        "coords": {
            "latitude": 45.3842,
            "longitude": 7.1525,
            "height": 1200,
        },
        "level": {
            "winter": "",
            "summer": "1А",
            "autumn": "1А",
            "spring": "",
        },
        "images": [
            {
                "title": "Вид на перевал",
                "data": base64.b64encode(b"fake-image").decode("utf-8"),
            }
        ],
    }
