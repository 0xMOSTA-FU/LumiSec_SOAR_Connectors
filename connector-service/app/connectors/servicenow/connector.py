from typing import Any, Dict, Optional

from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult, WebhookEvent, WebhookEventType
from app.core.exceptions import (
    AuthenticationError, ConnectorHTTPError, InvalidParameterError,
    ActionExecutionError, WebhookValidationError
)

class ServiceNowConnector(BaseConnector):
    """
    ServiceNow connector for ITSM incident management.
    Handles creation, retrieval, and updating of incidents via the ServiceNow Table API.
    """
    NAME = "ServiceNow"
    VERSION = "1.0.0"
    DESCRIPTION = "ServiceNow connector for ITSM incident management."

    async def test_connection(self) -> ConnectionResult:
        """
        Test the connection to ServiceNow by fetching a single incident.
        """
        try:
            response = await self.client.get("/api/now/table/incident", params={"sysparm_limit": "1"})
            response.raise_for_status()
            return ConnectionResult.ok()
        except Exception as e:
            return ConnectionResult.fail(str(e))

    @register_action(description="Create a new incident in ServiceNow")
    async def create_incident(self, short_description: str, description: str, urgency: str = '3', impact: str = '3') -> ActionResult:
        """
        Create a new incident in ServiceNow.
        
        Args:
            short_description: A brief summary of the incident.
            description: Detailed description of the incident.
            urgency: The urgency of the incident (default: '3').
            impact: The impact of the incident (default: '3').
            
        Returns:
            ActionResult containing the created incident data.
        """
        try:
            payload = {
                "short_description": short_description,
                "description": description,
                "urgency": urgency,
                "impact": impact
            }
            response = await self.client.post("/api/now/table/incident", json=payload)
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            raise ActionExecutionError(f"Failed to create incident: {str(e)}")

    @register_action(description="Get an incident from ServiceNow by sys_id")
    async def get_incident(self, sys_id: str) -> ActionResult:
        """
        Retrieve an incident from ServiceNow using its sys_id.
        
        Args:
            sys_id: The unique identifier of the incident.
            
        Returns:
            ActionResult containing the incident data.
        """
        if not sys_id:
            raise InvalidParameterError("sys_id is required")
            
        try:
            response = await self.client.get(f"/api/now/table/incident/{sys_id}")
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            raise ActionExecutionError(f"Failed to get incident: {str(e)}")

    @register_action(description="Update an existing incident in ServiceNow")
    async def update_incident(self, sys_id: str, state: Optional[str] = None, work_notes: Optional[str] = None) -> ActionResult:
        """
        Update an existing incident in ServiceNow.
        
        Args:
            sys_id: The unique identifier of the incident.
            state: Optional new state for the incident.
            work_notes: Optional work notes to add to the incident.
            
        Returns:
            ActionResult containing the updated incident data.
        """
        if not sys_id:
            raise InvalidParameterError("sys_id is required")
            
        try:
            payload = {}
            if state is not None:
                payload["state"] = state
            if work_notes is not None:
                payload["work_notes"] = work_notes
                
            response = await self.client.patch(f"/api/now/table/incident/{sys_id}", json=payload)
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            raise ActionExecutionError(f"Failed to update incident: {str(e)}")

    async def parse_webhook(self, request: Any) -> WebhookEvent:
        """
        Parse an incoming generic webhook request from ServiceNow.
        """
        try:
            # Assuming a standard request object with a .json() awaitable method
            payload = await request.json()
            return WebhookEvent(
                event_type=WebhookEventType.GENERIC,
                payload=payload,
                raw_request=payload
            )
        except Exception as e:
            raise WebhookValidationError(f"Failed to parse generic webhook: {str(e)}")
