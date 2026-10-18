"""Verify bootstrap entry points, required settings, and service-token boundaries."""

import os
import sys
from unittest.mock import patch

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from django.urls import path
from rest_framework.response import Response
from rest_framework.test import APIClient
from rest_framework.views import APIView

from traceeval import main
from traceeval.settings import required_env


class AuthenticatedProbe(APIView):
    """Exercise global authentication without depending on business applications."""

    def get(self, request):
        """Return an authenticated response without accessing any database tables."""
        return Response({"authenticated": request.user.is_authenticated})


urlpatterns = [path("probe/", AuthenticatedProbe.as_view())]


@pytest.mark.parametrize("value", ["", "replace-with-an-example"])
def test_required_setting_rejects_missing_or_placeholder_values(monkeypatch, value):
    """Reject blank and example values instead of silently booting with invalid settings."""
    monkeypatch.setenv("TRACEEVAL_BOOTSTRAP_TEST_SETTING", value)
    with pytest.raises(ImproperlyConfigured, match="TRACEEVAL_BOOTSTRAP_TEST_SETTING"):
        required_env("TRACEEVAL_BOOTSTRAP_TEST_SETTING")


def test_explicit_environment_value_is_used(monkeypatch):
    """Read a supplied environment setting without substituting example configuration."""
    monkeypatch.setenv("TRACEEVAL_BOOTSTRAP_TEST_SETTING", "configured-value")
    assert required_env("TRACEEVAL_BOOTSTRAP_TEST_SETTING") == "configured-value"


def test_console_entry_delegates_to_django_management(monkeypatch):
    """Preserve management arguments and select the configured Django settings module."""
    monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)
    monkeypatch.setattr(sys, "argv", ["traceeval", "check"])
    with patch("django.core.management.execute_from_command_line") as dispatch:
        main()
    dispatch.assert_called_once_with(["traceeval", "check"])
    assert os.environ["DJANGO_SETTINGS_MODULE"] == "traceeval.settings"


@pytest.mark.parametrize("authorization", [None, "Bearer wrong", "Basic wrong", "Bearer"])
@override_settings(ROOT_URLCONF=__name__)
def test_default_api_authentication_rejects_invalid_credentials(authorization):
    """Return a Bearer challenge when credentials are absent, malformed, or incorrect."""
    client = APIClient()
    if authorization is not None:
        client.credentials(HTTP_AUTHORIZATION=authorization)
    response = client.get("/probe/")
    assert response.status_code == 401
    assert response["WWW-Authenticate"] == "Bearer"


@override_settings(ROOT_URLCONF=__name__)
def test_default_api_authentication_accepts_the_configured_token():
    """Authenticate the service owner without requiring Django user tables."""
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {settings.API_TOKEN}")
    response = client.get("/probe/")
    assert response.status_code == 200
    assert response.data == {"authenticated": True}
