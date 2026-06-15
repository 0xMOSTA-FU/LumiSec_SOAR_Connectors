from typing import List, Dict, Any, Optional

from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult, WebhookEvent, WebhookEventType
from app.core.exceptions import (
    AuthenticationError, ConnectorHTTPError, InvalidParameterError,
    ActionExecutionError, WebhookValidationError
)

class PagerDutyConnector(BaseConnector):
    NAME = "PagerDuty"
    VERSION = "1.0.0"
    DESCRIPTION = "Connector for PagerDuty REST API v2"

    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = "https://api.pagerduty.com"
        self.http_client.headers.update({
            "Accept": "application/vnd.pagerduty+json;version=2"
        })

    async def test_connection(self) -> ConnectionResult:
        """
        Test the connection to PagerDuty API by fetching the users list.
        """
        try:
            response = await self.http_client.get(f"{self.base_url}/users")
            response.raise_for_status()
            return ConnectionResult.ok()
        except Exception as e:
            return ConnectionResult.fail(str(e))

    @register_action
    async def create_incident(
        self,
        title: str,
        service_id: str,
        details: str,
        escalation_policy_id: Optional[str] = None
    ) -> ActionResult:
        """
        Create a new incident in PagerDuty.
        """
        if not title or not service_id:
            raise InvalidParameterError("title and service_id are required.")

        payload = {
            "incident": {
                "type": "incident",
                "title": title,
                "service": {
                    "id": service_id,
                    "type": "service_reference"
                },
                "body": {
                    "type": "incident_body",
                    "details": details
                }
            }
        }
        
        if escalation_policy_id:
            payload["incident"]["escalation_policy"] = {
                "id": escalation_policy_id,
                "type": "escalation_policy_reference"
            }

        try:
            response = await self.http_client.post(
                f"{self.base_url}/incidents",
                json=payload
            )
            response.raise_for_status()
            # Handle both sync and async json() methods depending on the underlying client
            data = response.json() if callable(getattr(response, 'json', None)) else response.json
            import asyncio
            if asyncio.iscoroutine(data):
                data = await data
                
            return ActionResult.ok(data)
        except Exception as e:
            raise ActionExecutionError(f"Failed to create incident: {str(e)}")

    @register_action
    async def resolve_incident(
        self,
        incident_id: str,
        from_email: str
    ) -> ActionResult:
        """
        Resolve an existing incident in PagerDuty.
        """
        if not incident_id or not from_email:
            raise InvalidParameterError("incident_id and from_email are required.")

        payload = {
            "incident": {
                "type": "incident",
                "status": "resolved"
            }
        }
        
        headers = {
            "From": from_email
        }

        try:
            response = await self.http_client.put(
                f"{self.base_url}/incidents/{incident_id}",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json() if callable(getattr(response, 'json', None)) else response.json
            import asyncio
            if asyncio.iscoroutine(data):
                data = await data

            return ActionResult.ok(data)
        except Exception as e:
            raise ActionExecutionError(f"Failed to resolve incident: {str(e)}")

    @register_action
    async def get_incidents(
        self,
        statuses: Optional[List[str]] = None
    ) -> ActionResult:
        """
        Get a list of incidents from PagerDuty, optionally filtered by status.
        """
        if statuses is None:
            statuses = ['triggered', 'acknowledged']

        params = {
            "statuses[]": statuses
        }

        try:
            response = await self.http_client.get(
                f"{self.base_url}/incidents",
                params=params
            )
            response.raise_for_status()
            data = response.json() if callable(getattr(response, 'json', None)) else response.json
            import asyncio
            if asyncio.iscoroutine(data):
                data = await data

            return ActionResult.ok(data)
        except Exception as e:
            raise ActionExecutionError(f"Failed to get incidents: {str(e)}")

    async def parse_webhook(self, request: Any) -> WebhookEvent:
        """
        Parse incoming generic PagerDuty webhook event.
        """
        try:
            payload = await request.json() if callable(getattr(request, 'json', None)) else request.json
            import asyncio
            if asyncio.iscoroutine(payload):
                payload = await payload

            return WebhookEvent(
                type=WebhookEventType.GENERIC,
                raw_data=payload,
                source=self.NAME
            )
        except Exception as e:
            raise WebhookValidationError(f"Failed to parse PagerDuty webhook: {str(e)}")
