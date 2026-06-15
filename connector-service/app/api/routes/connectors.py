"""
SOAR Connector Hub — Connectors Routes
=======================================
Endpoints for managing connector configurations and testing connections.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional

from app.core.registry import ConnectorRegistry
from app.core.exceptions import ConfigurationError

router = APIRouter()


class ConnectorConfigPayload(BaseModel):
    """Payload to initialize a connector for connection testing."""
    config: Dict[str, Any]


# ─── List & Inspect ───────────────────────────────────────────────────────────

@router.get("/", summary="List all available connectors")
async def list_connectors():
    """Return metadata for every registered connector."""
    connectors = ConnectorRegistry.list_connectors()
    for c in connectors:
        try:
            klass = ConnectorRegistry.get_class(c["name"])
            instance = klass.__new__(klass)
            actions = []
            import inspect
            for attr in dir(klass):
                method = getattr(klass, attr)
                if callable(method) and hasattr(method, "_action_name"):
                    sig = inspect.signature(method)
                    params_list = []
                    for name, param in sig.parameters.items():
                        if name in ("self", "request_id", "args", "kwargs"):
                            continue
                        param_info = {
                            "name": name,
                            "type": param.annotation.__name__ if hasattr(param.annotation, "__name__") else str(param.annotation),
                            "required": param.default == inspect.Parameter.empty
                        }
                        if param.default != inspect.Parameter.empty:
                            param_info["default"] = param.default
                        params_list.append(param_info)
                    
                    actions.append({
                        "name": method._action_name,
                        "description": method._action_description,
                        "category": method._action_category,
                        "parameters": params_list
                    })
            c["actions"] = actions
        except Exception:
            c["actions"] = []
    return {"connectors": connectors, "total": len(connectors)}


@router.get("/{connector_name}", summary="Get connector metadata and available actions")
async def get_connector(connector_name: str):
    """Return detailed connector metadata including all actions."""
    try:
        klass = ConnectorRegistry.get_class(connector_name)
    except ConfigurationError as e:
        raise HTTPException(status_code=404, detail=str(e))

    import inspect

    actions = []
    for attr in dir(klass):
        method = getattr(klass, attr)
        if callable(method) and hasattr(method, "_action_name"):
            sig = inspect.signature(method)
            params_list = []
            for name, param in sig.parameters.items():
                if name in ("self", "request_id", "args", "kwargs"):
                    continue
                param_info = {
                    "name": name,
                    "type": param.annotation.__name__ if hasattr(param.annotation, "__name__") else str(param.annotation),
                    "required": param.default == inspect.Parameter.empty
                }
                if param.default != inspect.Parameter.empty:
                    param_info["default"] = param.default
                params_list.append(param_info)

            actions.append({
                "name": method._action_name,
                "description": method._action_description,
                "category": method._action_category,
                "tags": method._action_tags,
                "parameters": params_list
            })

    return {
        "name": klass.NAME,
        "version": klass.VERSION,
        "description": klass.DESCRIPTION,
        "actions": actions,
        "action_count": len(actions),
    }


# ─── Connection Test ──────────────────────────────────────────────────────────

@router.post("/{connector_name}/test", summary="Test connector connection")
async def test_connector_connection(connector_name: str, payload: ConnectorConfigPayload):
    """
    Test connectivity and authentication for a connector.
    Provide the connector config in the request body.
    """
    try:
        connector = ConnectorRegistry.create_instance(connector_name, payload.config)
    except ConfigurationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid config: {e}")

    try:
        result = await connector.test_connection()
        return result.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await connector.close()
