import os
from typing import Any, Dict

from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult, WebhookEvent, WebhookEventType
from app.core.exceptions import (
    AuthenticationError,
    ConnectorHTTPError,
    InvalidParameterError,
    ActionExecutionError,
    WebhookValidationError
)
from app.core.http_client import ConnectorHTTPClient


class DefectDojoConnector(BaseConnector):
    NAME = "DefectDojo"
    VERSION = "1.0.0"
    DESCRIPTION = "DefectDojo SOAR connector for vulnerability management."

    def __init__(self, config: Dict[str, Any]):
        """Initialize the DefectDojo connector with user configuration."""
        super().__init__(config)
        self.base_url = self.config.get("base_url", "").rstrip("/")
        self.token = self.config.get("token")
        
        if not self.base_url:
            raise AuthenticationError("Missing required config: base_url")
        if not self.token:
            raise AuthenticationError("Missing required config: token")

        self.client = ConnectorHTTPClient(
            base_url=self.base_url,
            headers={"Authorization": f"Token {self.token}"}
        )

    async def test_connection(self) -> ConnectionResult:
        """Test the connection to the DefectDojo API by fetching users."""
        try:
            await self.client.get("/api/v2/users/")
            return ConnectionResult.ok()
        except ConnectorHTTPError as e:
            return ConnectionResult.fail(f"HTTP Error during connection test: {e}")
        except Exception as e:
            return ConnectionResult.fail(f"Unexpected error during connection test: {e}")

    @register_action
    async def get_findings(self, limit: int = 20, active: str = 'true', severity: str = '') -> ActionResult:
        """Retrieve a list of findings from DefectDojo."""
        if limit < 1:
            raise InvalidParameterError("Limit must be a positive integer.")
            
        params: Dict[str, Any] = {
            "limit": limit,
            "active": active
        }
        if severity:
            params["severity"] = severity

        try:
            response = await self.client.get("/api/v2/findings/", params=params)
            return ActionResult.ok(response)
        except ConnectorHTTPError as e:
            return ActionResult.fail(f"Failed to get findings via HTTP: {e}")
        except Exception as e:
            raise ActionExecutionError(f"Unexpected error retrieving findings: {e}")

    @register_action
    async def create_finding(self, title: str, description: str, severity: str, test_id: int, active: bool = True) -> ActionResult:
        """Create a new finding in DefectDojo."""
        if not title or not description or not severity:
            raise InvalidParameterError("Title, description, and severity are required to create a finding.")
        if test_id <= 0:
            raise InvalidParameterError("test_id must be a positive integer.")
            
        payload = {
            "title": title,
            "description": description,
            "severity": severity,
            "test": test_id,
            "active": active,
            "verified": True
        }

        try:
            response = await self.client.post("/api/v2/findings/", json=payload)
            return ActionResult.ok(response)
        except ConnectorHTTPError as e:
            return ActionResult.fail(f"Failed to create finding via HTTP: {e}")
        except Exception as e:
            raise ActionExecutionError(f"Unexpected error creating finding: {e}")

    @register_action
    async def close_finding(self, finding_id: int) -> ActionResult:
        """Close an existing finding in DefectDojo."""
        if finding_id <= 0:
            raise InvalidParameterError("finding_id must be a positive integer.")
            
        payload = {
            "is_mitigated": True,
            "active": False
        }

        try:
            response = await self.client.patch(f"/api/v2/findings/{finding_id}/", json=payload)
            return ActionResult.ok(response)
        except ConnectorHTTPError as e:
            return ActionResult.fail(f"Failed to close finding via HTTP: {e}")
        except Exception as e:
            raise ActionExecutionError(f"Unexpected error closing finding: {e}")

    @register_action
    async def upload_scan(self, engagement_id: int, scan_type: str, file_path: str) -> ActionResult:
        """Upload a scan report to DefectDojo."""
        if engagement_id <= 0:
            raise InvalidParameterError("engagement_id must be a positive integer.")
        if not scan_type:
            raise InvalidParameterError("scan_type is required.")
        if not os.path.exists(file_path):
            raise InvalidParameterError(f"Scan file not found: {file_path}")

        data = {
            "engagement": engagement_id,
            "scan_type": scan_type
        }

        try:
            with open(file_path, "rb") as f:
                file_content = f.read()

            filename = os.path.basename(file_path)
            # Typically, http clients expect files in a dictionary
            # mapping field name to (filename, content) or similar structure.
            files = {"file": (filename, file_content)}

            response = await self.client.post("/api/v2/import-scan/", data=data, files=files)
            return ActionResult.ok(response)
        except ConnectorHTTPError as e:
            return ActionResult.fail(f"Failed to upload scan via HTTP: {e}")
        except Exception as e:
            raise ActionExecutionError(f"Unexpected error uploading scan: {e}")

    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> WebhookEvent:
        """Parse incoming generic webhooks from DefectDojo."""
        if not payload:
            raise WebhookValidationError("Received empty webhook payload.")
            
        return WebhookEvent(
            event_type=WebhookEventType.GENERIC,
            payload=payload,
            raw_headers=headers
        )
