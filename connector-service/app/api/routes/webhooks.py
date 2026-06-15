"""
SOAR Connector Hub — Webhooks Reception Route
=============================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Request, Header, HTTPException

from app.core.registry import ConnectorRegistry

logger = logging.getLogger("soar.api.webhooks")
router = APIRouter()


@router.post("/{connector_name}", summary="Receive a webhook event")
async def receive_webhook(connector_name: str, request: Request):
    """
    Generic webhook ingestion endpoint.
    Passes the raw body and headers to the connector's parse_webhook implementation.
    """
    logger.info("Received webhook for connector: %s", connector_name)
    
    try:
        klass = ConnectorRegistry.get_class(connector_name)
        # Note: Webhooks usually require configuration to validate signatures.
        # In a real architecture, the platform would look up the config by a webhook ID.
        # For this prototype hub, we instantiate the connector with an empty/default config
        # or require the platform to pass it, but standard webhooks don't have that payload.
        # So we create a lightweight instance just for parsing.
        connector = klass({})
    except Exception as e:
        logger.error("Connector not found or failed to init: %s", e)
        raise HTTPException(status_code=404, detail="Connector not found")

    try:
        # Try to parse as JSON, fallback to raw bytes
        try:
            payload = await request.json()
        except Exception:
            body = await request.body()
            payload = {"raw_body": body.decode("utf-8", errors="ignore")}

        headers = dict(request.headers)
        
        # 1. Signature validation (if implemented by connector and config provided)
        # is_valid = await connector.validate_webhook_signature(await request.body(), headers)
        
        # 2. Parse event
        event = await connector.parse_webhook(payload, headers)
        
        if event is None:
            return {"status": "ignored", "message": "Webhook payload ignored by connector"}
            
        # 3. Here you would normally push 'event' to a message queue (RabbitMQ/Kafka)
        # For now, return it to the caller (or simulate forwarding to the Node.js backend)
        
        return {
            "status": "success",
            "event": event.dict()
        }
    except Exception as e:
        logger.error("Failed to process webhook: %s", e)
        raise HTTPException(status_code=500, detail="Failed to process webhook")
    finally:
        await connector.close()
