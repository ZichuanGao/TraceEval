"""Configure the single-owner API and PostgreSQL using private environment settings."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=False)


def required_env(name):
    """Read a required setting and reject missing or example placeholder values."""
    value = os.getenv(name, "")
    if not value or value.startswith("replace-with-"):
        raise ImproperlyConfigured(f"Set {name} in the environment or project .env")
    return value


SECRET_KEY = required_env("DJANGO_SECRET_KEY")
API_TOKEN = required_env("TRACEEVAL_API_TOKEN")
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
INSTALLED_APPS = ["rest_framework"]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]
ROOT_URLCONF = "traceeval.urls"
WSGI_APPLICATION = "traceeval.wsgi.application"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("PGDATABASE", "traceeval"),
        "USER": os.getenv("PGUSER", "traceeval"),
        "PASSWORD": required_env("PGPASSWORD"),
        "HOST": os.getenv("PGHOST", "127.0.0.1"),
        "PORT": os.getenv("PGPORT", "5432"),
        "CONN_MAX_AGE": 60,
        "OPTIONS": {"connect_timeout": 5},
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
TIME_ZONE = "UTC"
DATA_UPLOAD_MAX_MEMORY_SIZE = 1_048_576
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["traceeval.authentication.ServiceTokenAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "UNAUTHENTICATED_USER": None,
}
