from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

load_dotenv(BASE_DIR / ".env")

SESSION_SECRET = os.environ.get("SESSION_SECRET", "dev-secret-change-me")
SESSION_MAX_AGE = int(os.environ.get("SESSION_MAX_AGE", str(86400 * 365)))  # 1 year

TZ = os.environ.get("TZ", "America/Caracas")

KASH_HOST = os.environ.get("KASH_HOST", "0.0.0.0")
KASH_PORT = int(os.environ.get("KASH_PORT", "8200"))

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_NAME = os.environ.get("DB_NAME", "kash")
DB_USER = os.environ.get("DB_USER", "admin_root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

SUPPORTED_LOCALES = ("es", "en")
DEFAULT_LOCALE = "es"
PAYMENT_METHODS = ("cash", "card", "zelle")
RECORD_KINDS = ("income", "expense")
