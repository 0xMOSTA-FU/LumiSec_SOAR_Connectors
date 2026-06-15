"""
SOAR Connector Hub — Authentication Handlers
=============================================
Pluggable auth handlers. Each handler resolves credentials and
returns HTTP headers ready to be injected into every request.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Dict, Optional

import httpx

from app.core.exceptions import AuthenticationError, TokenExpiredError


class BaseAuthHandler(ABC):
    """Abstract auth handler interface."""

    @abstractmethod
    async def get_headers(self) -> Dict[str, str]:
        """Return ready-to-use auth headers."""


# ─── API Key ──────────────────────────────────────────────────────────────────

class ApiKeyAuthHandler(BaseAuthHandler):
    """
    Adds a single API key header.
    Examples:
      - X-Api-Key: <key>
      - Authorization: Token <key>
      - X-VirusTotal-Auth: <key>
    """

    def __init__(self, api_key: str, header_name: str = "X-Api-Key", prefix: str = ""):
        self._api_key = api_key
        self._header_name = header_name
        self._prefix = prefix

    async def get_headers(self) -> Dict[str, str]:
        value = f"{self._prefix}{self._api_key}" if self._prefix else self._api_key
        return {self._header_name: value}


# ─── Bearer Token ─────────────────────────────────────────────────────────────

class BearerTokenAuthHandler(BaseAuthHandler):
    """Authorization: Bearer <token>"""

    def __init__(self, token: str):
        self._token = token

    async def get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self._token}"}


# ─── Basic Auth ───────────────────────────────────────────────────────────────

class BasicAuthHandler(BaseAuthHandler):
    """Standard HTTP Basic authentication."""

    def __init__(self, username: str, password: str):
        import base64
        raw = f"{username}:{password}".encode()
        self._encoded = base64.b64encode(raw).decode()

    async def get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Basic {self._encoded}"}


# ─── JWT (Username+Password → Token) ─────────────────────────────────────────

class JwtAuthHandler(BaseAuthHandler):
    """
    Authenticates with username/password against a token endpoint,
    then injects the resulting JWT as a Bearer token.
    Auto-refreshes before expiry.
    """

    def __init__(
        self,
        username: str,
        password: str,
        token_endpoint: str,
        token_field: str = "token",
        expiry_seconds: int = 3600,
        verify_ssl: bool = True,
    ):
        self._username = username
        self._password = password
        self._token_endpoint = token_endpoint
        self._token_field = token_field
        self._expiry_seconds = expiry_seconds
        self._verify_ssl = verify_ssl
        self._token: Optional[str] = None
        self._token_expiry: float = 0.0

    def _is_expired(self) -> bool:
        return time.monotonic() >= self._token_expiry - 60  # refresh 60s early

    async def _refresh(self) -> None:
        try:
            async with httpx.AsyncClient(verify=self._verify_ssl) as client:
                response = await client.post(
                    self._token_endpoint,
                    json={"username": self._username, "password": self._password},
                    timeout=10,
                )
                response.raise_for_status()
                body = response.json()
                token = body.get(self._token_field)
                if not token:
                    raise AuthenticationError(
                        f"Token field '{self._token_field}' not found in auth response."
                    )
                self._token = token
                self._token_expiry = time.monotonic() + self._expiry_seconds
        except httpx.HTTPStatusError as e:
            raise AuthenticationError(
                f"JWT auth failed: HTTP {e.response.status_code} from {self._token_endpoint}"
            )

    async def get_headers(self) -> Dict[str, str]:
        if self._token is None or self._is_expired():
            await self._refresh()
        return {"Authorization": f"Bearer {self._token}"}


# ─── OAuth2 Client Credentials ────────────────────────────────────────────────

class OAuth2ClientCredentialsHandler(BaseAuthHandler):
    """
    OAuth2 client_credentials flow.
    Auto-refreshes the access token before expiry.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        scope: str = "",
        verify_ssl: bool = True,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = token_url
        self._scope = scope
        self._verify_ssl = verify_ssl
        self._access_token: Optional[str] = None
        self._token_expiry: float = 0.0

    def _is_expired(self) -> bool:
        return time.monotonic() >= self._token_expiry - 60

    async def _refresh(self) -> None:
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        if self._scope:
            payload["scope"] = self._scope

        try:
            async with httpx.AsyncClient(verify=self._verify_ssl) as client:
                response = await client.post(self._token_url, data=payload, timeout=10)
                response.raise_for_status()
                body = response.json()
                self._access_token = body["access_token"]
                self._token_expiry = time.monotonic() + body.get("expires_in", 3600)
        except (httpx.HTTPStatusError, KeyError) as e:
            raise AuthenticationError(f"OAuth2 token refresh failed: {e}")

    async def get_headers(self) -> Dict[str, str]:
        if self._access_token is None or self._is_expired():
            await self._refresh()
        return {"Authorization": f"Bearer {self._access_token}"}


# ─── No Auth ──────────────────────────────────────────────────────────────────

class NoAuthHandler(BaseAuthHandler):
    """For connectors or endpoints that need no authentication."""

    async def get_headers(self) -> Dict[str, str]:
        return {}


# ─── Factory ──────────────────────────────────────────────────────────────────

def build_auth_handler(auth_type: str, config: dict) -> BaseAuthHandler:
    """
    Factory function: create the right auth handler from config dict.

    auth_type values match AuthType enum strings:
      api_key, bearer_token, basic_auth, jwt, oauth2_client_credentials, no_auth
    """
    handlers = {
        "api_key": lambda c: ApiKeyAuthHandler(
            api_key=c["api_key"],
            header_name=c.get("header_name", "X-Api-Key"),
            prefix=c.get("prefix", ""),
        ),
        "bearer_token": lambda c: BearerTokenAuthHandler(token=c["token"]),
        "basic_auth": lambda c: BasicAuthHandler(
            username=c["username"],
            password=c["password"],
        ),
        "jwt": lambda c: JwtAuthHandler(
            username=c["username"],
            password=c["password"],
            token_endpoint=c["token_endpoint"],
            token_field=c.get("token_field", "token"),
            expiry_seconds=c.get("expiry_seconds", 3600),
            verify_ssl=c.get("verify_ssl", True),
        ),
        "oauth2_client_credentials": lambda c: OAuth2ClientCredentialsHandler(
            client_id=c["client_id"],
            client_secret=c["client_secret"],
            token_url=c["token_url"],
            scope=c.get("scope", ""),
            verify_ssl=c.get("verify_ssl", True),
        ),
        "no_auth": lambda c: NoAuthHandler(),
    }

    factory = handlers.get(auth_type)
    if not factory:
        raise ValueError(f"Unknown auth_type: '{auth_type}'")
    return factory(config)
