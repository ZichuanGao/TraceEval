"""Expose the configured Django WSGI application."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "traceeval.settings")
application = get_wsgi_application()
