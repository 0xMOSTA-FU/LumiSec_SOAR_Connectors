from typing import Any

from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult, WebhookEvent, WebhookEventType
from app.core.exceptions import (
    AuthenticationError, ConnectorHTTPError, InvalidParameterError,
    ActionExecutionError, WebhookValidationError
)


class OPNsenseConnector(BaseConnector):
    NAME = "OPNsense"
    VERSION = "1.0.0"
    DESCRIPTION = "OPNsense firewall connector for managing aliases and rules"

    async def test_connection(self) -> ConnectionResult:
        """
        Test connection to OPNsense using the menu search endpoint.
        """
        try:
            response = await self.client.get("/api/core/menu/search")
            if response.status_code == 200:
                return ConnectionResult(success=True)
            return ConnectionResult(
                success=False, 
                error=f"Connection failed with status code: {response.status_code}"
            )
        except Exception as e:
            return ConnectionResult(success=False, error=str(e))

    @register_action
    async def get_aliases(self) -> ActionResult:
        """
        Retrieve all firewall aliases.
        """
        try:
            response = await self.client.get("/api/firewall/alias/searchItem")
            if response.status_code != 200:
                raise ActionExecutionError(f"Failed to get aliases: {response.text}")
            
            return ActionResult.ok(data=response.json())
        except Exception as e:
            raise ActionExecutionError(f"Error executing get_aliases: {str(e)}")

    @register_action
    async def block_ip(self, alias_uuid: str, ip: str, description: str = 'Blocked by SOAR') -> ActionResult:
        """
        Add an IP to an alias and set a description.
        
        Args:
            alias_uuid: The UUID of the alias to modify.
            ip: The IP address to block.
            description: Description for the block action.
        """
        if not alias_uuid or not ip:
            raise InvalidParameterError("alias_uuid and ip must be provided")

        payload = {
            "alias": {
                "content": ip,
                "description": description
            }
        }

        try:
            response = await self.client.post(
                f"/api/firewall/alias/setItem/{alias_uuid}",
                json=payload
            )
            if response.status_code != 200:
                raise ActionExecutionError(f"Failed to block IP: {response.text}")

            return ActionResult.ok(data=response.json())
        except Exception as e:
            raise ActionExecutionError(f"Error executing block_ip: {str(e)}")

    @register_action
    async def update_alias_content(self, alias_uuid: str, content: str) -> ActionResult:
        """
        Update the content of a specific alias.
        
        Args:
            alias_uuid: The UUID of the alias to update.
            content: The new content (IPs, networks) for the alias.
        """
        if not alias_uuid or not content:
            raise InvalidParameterError("alias_uuid and content must be provided")

        payload = {
            "alias": {
                "content": content
            }
        }

        try:
            response = await self.client.post(
                f"/api/firewall/alias/setItem/{alias_uuid}",
                json=payload
            )
            if response.status_code != 200:
                raise ActionExecutionError(f"Failed to update alias content: {response.text}")

            return ActionResult.ok(data=response.json())
        except Exception as e:
            raise ActionExecutionError(f"Error executing update_alias_content: {str(e)}")

    @register_action
    async def apply_changes(self) -> ActionResult:
        """
        Reconfigure the firewall to apply changes made to aliases.
        """
        try:
            response = await self.client.post("/api/firewall/alias/reconfigure")
            if response.status_code != 200:
                raise ActionExecutionError(f"Failed to apply changes: {response.text}")

            return ActionResult.ok(data=response.json())
        except Exception as e:
            raise ActionExecutionError(f"Error executing apply_changes: {str(e)}")

    async def parse_webhook(self, request: Any) -> WebhookEvent:
        """
        Parse generic webhook event.
        """
        try:
            payload = await request.json()
        except Exception:
            payload = {}

        return WebhookEvent(
            event_type=WebhookEventType.GENERIC,
            payload=payload,
            raw_request=request
        )
