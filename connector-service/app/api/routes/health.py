"""
SOAR Connector Hub — Health Routes
"""

from fastapi import APIRouter
from app.core.registry import ConnectorRegistry

router = APIRouter()


@router.get("/", summary="Service health check")
async def health_check():
    connectors = ConnectorRegistry.list_connectors()
    return {
        "status": "healthy",
        "service": "SOAR Connector Hub",
        "version": "1.0.0",
        "connectors_loaded": len(connectors),
    }


@router.get("/connectors", summary="List loaded connectors")
async def list_loaded_connectors():
    return {
        "connectors": ConnectorRegistry.list_connectors()
    }
