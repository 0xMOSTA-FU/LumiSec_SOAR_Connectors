"""
SOAR Connector Hub — Abstract Base Connector
=============================================
Every connector MUST inherit from BaseConnector.
Provides:
  - Authenticated HTTP client injection
  - Standardized action execution with timing
  - Action registry via @register_action decorator
  - Connection test
  - Webhook parsing interface
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from app.core.auth import BaseAuthHandler, build_auth_handler
from app.core.exceptions import ActionNotFoundError, ConnectorHTTPError, SOARConnectorError
from app.core.http_client import ConnectorHTTPClient
from app.core.models import (
    ActionDefinition,
    ActionResult,
    ConnectionResult,
    ConnectorConfig,
    WebhookEvent,
)


def register_action(name: str = "", description: str = "", category: str = "general", tags: List[str] = [], **kwargs):
    """
    Decorator to register a method as a named connector action.
    Populates the connector's action registry at class definition time.
    """
    def decorator(fn: Callable):
        fn._action_name = name or fn.__name__
        fn._action_description = description
        fn._action_category = category
        fn._action_tags = tags
        return fn
    return decorator


class BaseConnector(ABC):
    """
    Abstract base class for all SOAR connectors.

    Subclasses MUST implement:
      - NAME: str — unique connector identifier (e.g. "virustotal")
      - VERSION: str
      - DESCRIPTION: str
      - test_connection() -> ConnectionResult

    Subclasses MAY implement:
      - parse_webhook(payload, headers) -> WebhookEvent
    """

    NAME: str = ""
    VERSION: str = "1.0.0"
    DESCRIPTION: str = ""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.NAME:
            from app.core.registry import ConnectorRegistry
            ConnectorRegistry.register(cls)

    def __init__(self, config: Dict[str, Any]) -> None:
        self._raw_config = config
        self._auth_handler: Optional[BaseAuthHandler] = None
        self._http: Optional[ConnectorHTTPClient] = None
        self._action_registry: Dict[str, Callable] = {}
        self._setup_auth(config)
        self._register_actions()

    # ─── Setup ────────────────────────────────────────────────────────────────

    def _setup_auth(self, config: Dict[str, Any]) -> None:
        auth_type = config.get("auth_type", "no_auth")
        auth_config = config.get("auth_config", {})
        self._auth_handler = build_auth_handler(auth_type, auth_config)

    def _register_actions(self) -> None:
        """Walk all methods and collect those decorated with @register_action."""
        for attr_name in dir(self.__class__):
            method = getattr(self.__class__, attr_name, None)
            if callable(method) and hasattr(method, "_action_name"):
                self._action_registry[method._action_name] = getattr(self, attr_name)

    async def _get_http_client(self) -> ConnectorHTTPClient:
        """Return an initialized HTTP client with auth headers already injected."""
        if self._http is None:
            auth_headers = await self._auth_handler.get_headers()
            extra_headers = self._raw_config.get("extra_headers", {})
            self._http = ConnectorHTTPClient(
                base_url=self._raw_config.get("base_url", ""),
                headers={**auth_headers, **extra_headers},
                timeout=self._raw_config.get("timeout_seconds", 30),
                max_retries=self._raw_config.get("max_retries", 3),
                backoff_factor=self._raw_config.get("retry_backoff_factor", 0.5),
                verify_ssl=self._raw_config.get("verify_ssl", True),
                proxy_url=self._raw_config.get("proxy_url"),
            )
            await self._http._open()
        return self._http

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._http:
            await self._http._close()
            self._http = None

    # ─── Action Execution ─────────────────────────────────────────────────────

    async def execute_action(
        self,
        action_name: str,
        params: Dict[str, Any],
        request_id: str = "",
    ) -> ActionResult:
        """
        Dispatch an action by name and wrap result in ActionResult.
        Measures wall-clock duration and catches all exceptions.
        """
        handler = self._action_registry.get(action_name)
        if not handler:
            raise ActionNotFoundError(action=action_name, connector=self.NAME)

        start = time.monotonic()
        try:
            result = await handler(**params)
            duration_ms = int((time.monotonic() - start) * 1000)

            # If the action already returns an ActionResult, stamp duration
            if isinstance(result, ActionResult):
                result.duration_ms = duration_ms
                result.request_id = request_id or result.request_id
                return result

            # Otherwise wrap it
            return ActionResult.ok(
                connector=self.NAME,
                action=action_name,
                data=result,
                request_id=request_id,
                duration_ms=duration_ms,
            )

        except SOARConnectorError as exc:
            duration_ms = int((time.monotonic() - start) * 1000)
            return ActionResult.fail(
                connector=self.NAME,
                action=action_name,
                error=exc.message,
                error_code=type(exc).__name__,
                request_id=request_id,
                duration_ms=duration_ms,
            )
        except Exception as exc:
            duration_ms = int((time.monotonic() - start) * 1000)
            return ActionResult.fail(
                connector=self.NAME,
                action=action_name,
                error=str(exc),
                error_code="UnexpectedError",
                request_id=request_id,
                duration_ms=duration_ms,
            )

    # ─── Introspection ────────────────────────────────────────────────────────

    def get_available_actions(self) -> List[Dict[str, str]]:
        """Return list of available actions with name + description."""
        result = []
        for attr_name in dir(self.__class__):
            method = getattr(self.__class__, attr_name, None)
            if callable(method) and hasattr(method, "_action_name"):
                result.append({
                    "name": method._action_name,
                    "description": method._action_description,
                    "category": method._action_category,
                    "tags": method._action_tags,
                })
        return result

    # ─── Abstract Methods ─────────────────────────────────────────────────────

    @abstractmethod
    async def test_connection(self) -> ConnectionResult:
        """
        Verify connectivity and authentication.
        Must hit a lightweight endpoint to confirm the connector works.
        """

    # ─── Optional Webhook Interface ───────────────────────────────────────────

    async def parse_webhook(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str],
    ) -> Optional[WebhookEvent]:
        """
        Parse an incoming webhook payload into a normalized WebhookEvent.
        Override in connectors that support incoming webhooks.
        Returns None if the payload should be ignored.
        """
        return None

    async def validate_webhook_signature(
        self,
        payload: bytes,
        headers: Dict[str, str],
    ) -> bool:
        """
        Validate the webhook signature (HMAC, etc.).
        Override in connectors that sign their webhook payloads.
        """
        return True  # permissive default — override to enforce
