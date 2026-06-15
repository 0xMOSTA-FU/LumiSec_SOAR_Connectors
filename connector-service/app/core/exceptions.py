"""
SOAR Connector Hub — Custom Exceptions
========================================
Centralized exception hierarchy for all connector errors.
"""


class SOARConnectorError(Exception):
    """Base exception for all SOAR connector errors."""

    def __init__(self, message: str, connector: str = "", action: str = "", status_code: int = 0):
        self.message = message
        self.connector = connector
        self.action = action
        self.status_code = status_code
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "connector": self.connector,
            "action": self.action,
            "status_code": self.status_code,
        }


# ─── Authentication Errors ──────────────────────────────────────────────────

class AuthenticationError(SOARConnectorError):
    """Raised when authentication fails (invalid credentials, expired token, etc.)."""
    pass


class TokenExpiredError(AuthenticationError):
    """Raised when a JWT or OAuth2 token has expired."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when API key or username/password is wrong."""
    pass


# ─── HTTP / Network Errors ───────────────────────────────────────────────────

class ConnectorHTTPError(SOARConnectorError):
    """Raised on non-2xx HTTP responses from external APIs."""

    def __init__(self, message: str, status_code: int, response_body: str = "", **kwargs):
        self.response_body = response_body
        super().__init__(message, status_code=status_code, **kwargs)


class RateLimitError(ConnectorHTTPError):
    """Raised when the API rate limit is hit (HTTP 429)."""

    def __init__(self, message: str, retry_after: int = 60, **kwargs):
        self.retry_after = retry_after
        super().__init__(message, status_code=429, **kwargs)


class ConnectionError(SOARConnectorError):
    """Raised when the connector cannot reach the target service."""
    pass


class TimeoutError(SOARConnectorError):
    """Raised when a request exceeds its timeout threshold."""
    pass


# ─── Configuration Errors ────────────────────────────────────────────────────

class ConfigurationError(SOARConnectorError):
    """Raised when the connector configuration is invalid or missing fields."""
    pass


class MissingConfigError(ConfigurationError):
    """Raised when a required configuration field is absent."""

    def __init__(self, field: str, connector: str = ""):
        super().__init__(
            message=f"Missing required configuration field: '{field}'",
            connector=connector,
        )
        self.field = field


# ─── Action / Execution Errors ───────────────────────────────────────────────

class ActionNotFoundError(SOARConnectorError):
    """Raised when an unknown action is requested."""

    def __init__(self, action: str, connector: str = ""):
        super().__init__(
            message=f"Action '{action}' not found in connector '{connector}'",
            connector=connector,
            action=action,
        )


class ActionExecutionError(SOARConnectorError):
    """Raised when an action fails during execution."""
    pass


class InvalidParameterError(SOARConnectorError):
    """Raised when a required parameter for an action is missing or invalid."""

    def __init__(self, param: str, reason: str = "", **kwargs):
        super().__init__(
            message=f"Invalid parameter '{param}': {reason}",
            **kwargs,
        )
        self.param = param


# ─── Webhook Errors ──────────────────────────────────────────────────────────

class WebhookValidationError(SOARConnectorError):
    """Raised when an incoming webhook payload fails signature validation."""
    pass


class WebhookProcessingError(SOARConnectorError):
    """Raised when processing an incoming webhook event fails."""
    pass
