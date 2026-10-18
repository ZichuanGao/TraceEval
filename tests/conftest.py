"""Provide authenticated API fixtures and HTTP isolation for offline tests."""

from unittest.mock import patch

import pytest
from django.conf import settings
from rest_framework.test import APIClient


@pytest.fixture
def client():
    """Provide an API client authenticated with the isolated test service token."""
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {settings.API_TOKEN}")
    return client


@pytest.fixture(autouse=True)
def deny_external_http():
    """Prevent real urllib HTTP calls across the entire offline test suite."""
    with patch(
        "urllib.request.OpenerDirector.open",
        side_effect=AssertionError("Network disabled in offline tests"),
    ):
        yield
