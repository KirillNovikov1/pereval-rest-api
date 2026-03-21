from __future__ import annotations

import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_HOST = os.getenv("FSTR_DB_HOST", "localhost")
    DB_PORT = os.getenv("FSTR_DB_PORT", "5432")
    DB_LOGIN = os.getenv("FSTR_LOGIN", os.getenv("FSTR_DB_LOGIN", "postgres"))
    DB_PASS = os.getenv("FSTR_PASS", os.getenv("FSTR_DB_PASS", ""))
    DB_NAME = os.getenv("FSTR_DB_NAME", "pereval_db")
    DB_URL = os.getenv("FSTR_DB_URL")

    @staticmethod
    def get_db_url() -> str:
        if Config.DB_URL:
            return Config.DB_URL

        login = quote_plus(Config.DB_LOGIN)
        password = quote_plus(Config.DB_PASS)
        return (
            f"postgresql://{login}:{password}"
            f"@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
        )
