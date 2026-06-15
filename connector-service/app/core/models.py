"""
SOAR Connector Hub — Core Pydantic Models
==========================================
Shared data models used across all connectors and the API layer.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, SecretStr


# ─── Enums ───────────────────────────────────────────────────────────────────

class AuthType(str, Enum):
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    JWT = "jwt"
    OAUTH2_CLIENT_CREDENTIALS = "oauth2_client_credentials"
    NO_AUTH = "no_auth"


class ActionStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    PENDING = "pending"


class WebhookEventType(str, Enum):
    ALERT = "alert"
    INCIDENT = "incident"
    VULNERABILITY = "vulnerability"
    AUDIT = "audit"
    GENERIC = "generic"


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


# ─── Auth Config Models ───────────────────────────────────────────────────────

class ApiKeyAuth(BaseModel):
    api_key: SecretStr
    header_name: str = "X-Api-Key"
    prefix: str = ""                    # e.g. "Token " or "Bearer "


class BearerTokenAuth(BaseModel):
    token: SecretStr


class BasicAuth(BaseModel):
    username: str
    password: SecretStr


class JwtAuth(BaseModel):
    username: str
    password: SecretStr
    token_endpoint: str
    token_field: str = "token"          # JSON field containing the token in response
    expiry_seconds: int = 3600


class OAuth2ClientCredentials(BaseModel):
    client_id: str
    client_secret: SecretStr
    token_url: str
    scope: str = ""


# ─── Connector Config ─────────────────────────────────────────────────────────

class ConnectorConfig(BaseModel):
    """Base configuration shared by every connector."""
    connector_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    base_url: str
    auth_type: AuthType
    auth_config: Dict[str, Any]
    verify_ssl: bool = True
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_backoff_factor: float = 0.5
    proxy_url: Optional[str] = None
    extra_headers: Dict[str, str] = {}
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ─── Action Definition ────────────────────────────────────────────────────────

class ParameterDefinition(BaseModel):
    name: str
    type: str                           # "string", "integer", "boolean", "array", "object"
    required: bool = True
    description: str = ""
    default: Optional[Any] = None
    example: Optional[Any] = None
    enum: Optional[List[Any]] = None


class ActionDefinition(BaseModel):
    name: str
    description: str
    category: str = "general"
    parameters: List[ParameterDefinition] = []
    output_schema: Optional[Dict[str, Any]] = None
    tags: List[str] = []


# ─── Execution Models ─────────────────────────────────────────────────────────

class ActionRequest(BaseModel):
    connector_name: str
    action_name: str
    params: Dict[str, Any] = {}
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timeout_override: Optional[int] = None


class ActionResult(BaseModel):
    """Standardized output for every connector action."""
    success: bool
    connector: str
    action: str
    status: ActionStatus
    data: Optional[Any] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = {}
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: Optional[int] = None

    @classmethod
    def ok(
        cls,
        connector: str,
        action: str,
        data: Any,
        request_id: str = "",
        duration_ms: int = 0,
        **metadata,
    ) -> "ActionResult":
        return cls(
            success=True,
            connector=connector,
            action=action,
            status=ActionStatus.SUCCESS,
            data=data,
            request_id=request_id or str(uuid.uuid4()),
            duration_ms=duration_ms,
            metadata=metadata,
        )

    @classmethod
    def fail(
        cls,
        connector: str,
        action: str,
        error: str,
        error_code: str = "",
        request_id: str = "",
        duration_ms: int = 0,
    ) -> "ActionResult":
        return cls(
            success=False,
            connector=connector,
            action=action,
            status=ActionStatus.FAILURE,
            error=error,
            error_code=error_code,
            request_id=request_id or str(uuid.uuid4()),
            duration_ms=duration_ms,
        )


# ─── Webhook Models ───────────────────────────────────────────────────────────

class WebhookEvent(BaseModel):
    """Normalized webhook event that gets forwarded to the platform."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    connector: str
    event_type: WebhookEventType = WebhookEventType.GENERIC
    raw_payload: Dict[str, Any]
    normalized: Dict[str, Any] = {}     # Normalized fields common across connectors
    severity: Optional[str] = None      # low, medium, high, critical
    source_ip: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = []


# ─── Connection Test ──────────────────────────────────────────────────────────

class ConnectionResult(BaseModel):
    success: bool
    connector: str
    message: str
    latency_ms: Optional[int] = None
    details: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
