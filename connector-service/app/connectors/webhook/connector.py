"""
SOAR Connector Hub — Generic Webhook Trigger
============================================
"""

from __future__ import annotations

from typing import Any, Dict

from app.core.base_connector import BaseConnector, register_action
from app.core.models import ConnectionResult, WebhookEvent, WebhookEventType


class WebhookTriggerConnector(BaseConnector):
    NAME = "webhook"
    VERSION = "1.0.0"
    DESCRIPTION = "Generic Webhook Trigger to receive events from any external system."

    async def test_connection(self) -> ConnectionResult:
        # Webhook connector doesn't dial out, so test connection is always successful 
        # as long as the SOAR engine is running.
        return ConnectionResult(
            success=True,
            connector=self.NAME,
            message="Webhook connector is active and ready to receive payloads."
        )

    # ─── Webhook Parsing ──────────────────────────────────────────────────────

    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> WebhookEvent | None:
        """
        Generic parsing: Takes any payload and wraps it as a generic event.
        No signature validation is enforced by default, but could be added via config.
        """
        # We can extract common fields if they happen to be present, but default is raw.
        return WebhookEvent(
            connector=self.NAME,
            event_type=WebhookEventType.GENERIC,
            raw_payload=payload,
            normalized={
                "trigger": "generic_webhook",
                "headers": {k: v for k, v in headers.items() if k.lower() not in ["authorization"]}
            }
        )
