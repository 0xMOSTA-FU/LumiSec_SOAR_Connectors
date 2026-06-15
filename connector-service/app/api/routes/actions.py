"""
SOAR Connector Hub — Actions Execution Route
============================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.core.registry import ConnectorRegistry
from app.core.models import ActionRequest, ActionResult

logger = logging.getLogger("soar.api.actions")
router = APIRouter()


class ActionExecutionPayload(BaseModel):
    """Payload to execute an action on a given connector."""
    config: Dict[str, Any]
    request: ActionRequest


@router.post("/execute", response_model=ActionResult, summary="Execute a connector action")
async def execute_action(payload: ActionExecutionPayload):
    """
    Executes a specified action on a connector dynamically.
    The caller must provide the connector configuration and the action parameters.
    """
    connector_name = payload.request.connector_name
    action_name = payload.request.action_name
    
    logger.info("Executing action '%s' on connector '%s'", action_name, connector_name)
    
    try:
        connector = ConnectorRegistry.create_instance(connector_name, payload.config)
    except Exception as e:
        logger.error("Failed to initialize connector %s: %s", connector_name, e)
        raise HTTPException(status_code=400, detail=f"Configuration error: {e}")

    try:
        result = await connector.execute_action(
            action_name=action_name,
            params=payload.request.params,
            request_id=payload.request.request_id
        )
        return result
    except Exception as e:
        logger.error("Action execution failed: %s", e)
        # Even on failure, return ActionResult format with success=False
        return ActionResult.fail(
            connector=connector_name,
            action=action_name,
            error=str(e),
            error_code="ExecutionException",
            request_id=payload.request.request_id
        )
    finally:
        await connector.close()
