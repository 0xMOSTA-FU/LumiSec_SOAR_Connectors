from typing import Any, Dict, Optional

from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult, WebhookEvent, WebhookEventType
from app.core.exceptions import (
    AuthenticationError, ConnectorHTTPError, InvalidParameterError,
    ActionExecutionError, WebhookValidationError
)


class VelociraptorConnector(BaseConnector):
    NAME = "Velociraptor"
    VERSION = "1.0.0"
    DESCRIPTION = "Connector for Velociraptor Server API."

    async def test_connection(self) -> ConnectionResult:
        """
        Test the connection by performing a lightweight API call.
        """
        try:
            response = await self.http_client.post(
                "/api/v1/SearchClients",
                json={"query": "", "limit": 1}
            )
            response.raise_for_status()
            return ConnectionResult.ok("Connection successful")
        except Exception as e:
            return ConnectionResult.fail(f"Connection failed: {str(e)}")

    @register_action
    async def search_clients(self, query: str, limit: int = 50) -> ActionResult:
        """
        Search for clients.

        Args:
            query: The search query string.
            limit: The maximum number of clients to return. Defaults to 50.
            
        Returns:
            ActionResult containing the list of clients.
        """
        try:
            response = await self.http_client.post(
                "/api/v1/SearchClients",
                json={"query": query, "limit": limit}
            )
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            raise ActionExecutionError(f"Failed to search clients: {str(e)}")

    @register_action
    async def hunt_malware(self, artifact_name: str, description: str = 'SOAR Hunt') -> ActionResult:
        """
        Create a hunt.

        Args:
            artifact_name: The name of the artifact to hunt for.
            description: Description of the hunt. Defaults to 'SOAR Hunt'.
            
        Returns:
            ActionResult containing the created hunt details.
        """
        try:
            response = await self.http_client.post(
                "/api/v1/CreateHunt",
                json={"artifact": artifact_name, "description": description}
            )
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            raise ActionExecutionError(f"Failed to create hunt: {str(e)}")

    @register_action
    async def get_hunt_results(self, hunt_id: str, limit: int = 100) -> ActionResult:
        """
        Get results for a specific hunt.

        Args:
            hunt_id: The ID of the hunt.
            limit: The maximum number of results to return. Defaults to 100.
            
        Returns:
            ActionResult containing the hunt results.
        """
        try:
            response = await self.http_client.post(
                "/api/v1/GetHuntResults",
                json={"hunt_id": hunt_id, "limit": limit}
            )
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            raise ActionExecutionError(f"Failed to get hunt results: {str(e)}")

    async def parse_webhook(self, request: Any) -> WebhookEvent:
        """
        Parse an incoming webhook request from Velociraptor.
        """
        try:
            payload = await request.json()
            return WebhookEvent(
                type=WebhookEventType.GENERIC,
                raw_data=payload
            )
        except Exception as e:
            raise WebhookValidationError(f"Failed to parse webhook: {str(e)}")

    async def validate_webhook_signature(self, request: Any) -> bool:
        """
        Velociraptor signature validation (override if needed).
        """
        return True
