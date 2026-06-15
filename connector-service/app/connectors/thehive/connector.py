from typing import Any, Dict, List, Optional
from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult, WebhookEvent, WebhookEventType
from app.core.exceptions import (
    AuthenticationError, ConnectorHTTPError, InvalidParameterError,
    ActionExecutionError, WebhookValidationError
)

class TheHiveConnector(BaseConnector):
    NAME = "TheHive"
    VERSION = "1.0.0"
    DESCRIPTION = "Connector for TheHive v4 REST API"

    async def test_connection(self) -> ConnectionResult:
        """
        Test connection to TheHive by hitting /api/status.
        """
        try:
            client = self._get_http_client()
            response = await client.get("/api/status")
            
            if response.status_code == 200:
                return ConnectionResult.ok()
            return ConnectionResult.fail(f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            return ConnectionResult.fail(f"Connection failed: {str(e)}")

    @register_action
    async def create_case(
        self,
        title: str,
        description: str,
        severity: int = 2,
        tags: Optional[List[str]] = None,
        tlp: int = 2
    ) -> ActionResult:
        """
        Create a new case in TheHive.
        """
        if tags is None:
            tags = []
            
        payload = {
            "title": title,
            "description": description,
            "severity": severity,
            "tags": tags,
            "tlp": tlp
        }
        
        try:
            client = self._get_http_client()
            response = await client.post("/api/case", json=payload)
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            return ActionResult.fail(f"Failed to create case: {str(e)}")

    @register_action
    async def get_case(self, case_id: str) -> ActionResult:
        """
        Retrieve a case from TheHive by its ID.
        """
        if not case_id:
            raise InvalidParameterError("case_id is required")
            
        try:
            client = self._get_http_client()
            response = await client.get(f"/api/case/{case_id}")
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            return ActionResult.fail(f"Failed to get case: {str(e)}")

    @register_action
    async def create_alert(
        self,
        title: str,
        description: str,
        severity: int = 2,
        tags: Optional[List[str]] = None,
        type: str = "soar",
        source: str = "soar",
        tlp: int = 2
    ) -> ActionResult:
        """
        Create a new alert in TheHive.
        """
        if tags is None:
            tags = []
            
        payload = {
            "title": title,
            "description": description,
            "severity": severity,
            "tags": tags,
            "type": type,
            "source": source,
            "tlp": tlp
        }
        
        try:
            client = self._get_http_client()
            response = await client.post("/api/alert", json=payload)
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            return ActionResult.fail(f"Failed to create alert: {str(e)}")

    @register_action
    async def get_alert(self, alert_id: str) -> ActionResult:
        """
        Retrieve an alert from TheHive by its ID.
        """
        if not alert_id:
            raise InvalidParameterError("alert_id is required")
            
        try:
            client = self._get_http_client()
            response = await client.get(f"/api/alert/{alert_id}")
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            return ActionResult.fail(f"Failed to get alert: {str(e)}")

    @register_action
    async def add_observable(
        self,
        case_id: str,
        data_type: str,
        data: str,
        message: str = "",
        tlp: int = 2
    ) -> ActionResult:
        """
        Add an observable (artifact) to a specific case.
        """
        if not case_id:
            raise InvalidParameterError("case_id is required")
        if not data_type or not data:
            raise InvalidParameterError("data_type and data are required")
            
        payload = {
            "dataType": data_type,
            "data": data,
            "message": message,
            "tlp": tlp
        }
        
        try:
            client = self._get_http_client()
            response = await client.post(f"/api/case/{case_id}/artifact", json=payload)
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            return ActionResult.fail(f"Failed to add observable: {str(e)}")

    @register_action
    async def get_case_observables(self, case_id: str) -> ActionResult:
        """
        Retrieve all observables (artifacts) for a specific case.
        """
        if not case_id:
            raise InvalidParameterError("case_id is required")
            
        try:
            client = self._get_http_client()
            response = await client.get(f"/api/case/{case_id}/artifact")
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            return ActionResult.fail(f"Failed to get observables: {str(e)}")

    async def parse_webhook(self, request: Any) -> WebhookEvent:
        """
        Parse a webhook payload from TheHive into a WebhookEvent.
        """
        try:
            payload = request.json() if hasattr(request, "json") else request
            
            if not isinstance(payload, dict):
                raise WebhookValidationError("Invalid webhook payload format: expected a JSON dictionary.")

            object_type = payload.get("objectType", "").lower()
            
            if object_type == "alert":
                event_type = WebhookEventType.ALERT
            elif object_type == "case":
                event_type = WebhookEventType.CASE
            else:
                event_type = WebhookEventType.OTHER
                
            return WebhookEvent(
                event_type=event_type,
                raw_payload=payload
            )
        except WebhookValidationError:
            raise
        except Exception as e:
            raise WebhookValidationError(f"Failed to parse TheHive webhook: {str(e)}") from e
