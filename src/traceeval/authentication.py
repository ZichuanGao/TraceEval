"""Authenticate the single-owner service API with a private Bearer token."""

from dataclasses import dataclass
from secrets import compare_digest

from django.conf import settings
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed


@dataclass(frozen=True)
class ServicePrincipal:
    """Represent the authenticated owner without requiring Django user tables."""

    is_authenticated: bool = True


class ServiceTokenAuthentication(BaseAuthentication):
    """Single-owner development API; credentials never appear in query strings."""

    def authenticate(self, request):
        """Validate the Bearer token with constant-time comparison."""
        parts = get_authorization_header(request).split()
        if not parts:
            return None
        if len(parts) != 2 or parts[0].lower() != b"bearer":
            raise AuthenticationFailed("Use Authorization: Bearer <token>.")
        if not compare_digest(parts[1], settings.API_TOKEN.encode()):
            raise AuthenticationFailed("Invalid API token.")
        return ServicePrincipal(), None

    def authenticate_header(self, request):
        """Return the Bearer challenge so unauthenticated requests receive HTTP 401."""
        return "Bearer"
