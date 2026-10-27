import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "stockpilot-demo-session-change-me")
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "stockpilot.db"))
    ORACLE_DSN = os.getenv("ORACLE_DSN", "")
    ORACLE_USER = os.getenv("ORACLE_USER", "")
    ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "")
    DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    SESSION_COOKIE_NAME = "stockpilot_session"
    JSON_SORT_KEYS = False
