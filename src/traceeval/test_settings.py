"""Configure isolated Django tests without requiring production API credentials."""

import os

os.environ.setdefault("DJANGO_SECRET_KEY", "traceeval-isolated-tests-only")
os.environ.setdefault("TRACEEVAL_API_TOKEN", "test-token")

from .settings import *  # noqa: E402,F403

ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
