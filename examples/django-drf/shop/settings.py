"""Django settings for the MainMoney mini-shop example."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-drf-example-change-me")
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "catalog",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "shop.urls"
WSGI_APPLICATION = "shop.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
STATIC_URL = "static/"

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ORIGINS",
        "http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175,http://127.0.0.1:4200",
    ).split(",")
    if origin.strip()
]
CORS_ALLOW_HEADERS = ["accept", "authorization", "content-type", "idempotency-key"]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}

MM_CLIENT_ID = os.environ.get("MM_CLIENT_ID", "")
MM_API_SECRET = os.environ.get("MM_API_SECRET", "")
MM_TEST = os.environ.get("MM_TEST", "true").lower() in {"1", "true", "yes"}
MM_WEBHOOK_SECRET = os.environ.get("MM_WEBHOOK_SECRET", "")
MM_BASE_URI = os.environ.get("MM_BASE_URI") or None
