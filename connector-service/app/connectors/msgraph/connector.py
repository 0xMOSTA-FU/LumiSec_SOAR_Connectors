from typing import Any, Dict, List, Optional

from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult, WebhookEvent, WebhookEventType
from app.core.exceptions import (
    AuthenticationError, ConnectorHTTPError, InvalidParameterError,
    ActionExecutionError, WebhookValidationError
)

class MSGraphConnector(BaseConnector):
    NAME = "msgraph"
    VERSION = "1.0.0"
    DESCRIPTION = "Microsoft Graph connector for Teams and Outlook"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = self.config.get("base_url", "https://graph.microsoft.com/v1.0")

    async def test_connection(self) -> ConnectionResult:
        """Test connection to MS Graph using a lightweight endpoint."""
        try:
            response = await self.client.get(f"{self.base_url}/organization")
            response.raise_for_status()
            return ConnectionResult.ok()
        except Exception as e:
            return ConnectionResult.fail(str(e))

    @register_action
    async def send_teams_message(self, team_id: str, channel_id: str, message: str) -> ActionResult:
        """Send a message to a specific Teams channel."""
        if not team_id or not channel_id or not message:
            raise InvalidParameterError("team_id, channel_id, and message are required.")
            
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages"
        payload = {
            "body": {
                "content": message,
                "contentType": "text"
            }
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            raise ActionExecutionError(f"Failed to send Teams message: {str(e)}")

    @register_action
    async def get_teams(self) -> ActionResult:
        """Retrieve all teams in the organization."""
        url = f"{self.base_url}/groups?$filter=resourceProvisioningOptions/Any(x:x eq 'Team')"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            return ActionResult.ok(data.get("value", data))
        except Exception as e:
            raise ActionExecutionError(f"Failed to get teams: {str(e)}")

    @register_action
    async def get_channels(self, team_id: str) -> ActionResult:
        """Retrieve channels for a specific team."""
        if not team_id:
            raise InvalidParameterError("team_id is required.")
            
        url = f"{self.base_url}/teams/{team_id}/channels"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            return ActionResult.ok(data.get("value", data))
        except Exception as e:
            raise ActionExecutionError(f"Failed to get channels: {str(e)}")

    @register_action
    async def send_email(self, user_id: str, to_email: str, subject: str, body: str, is_html: bool = False) -> ActionResult:
        """Send an email from a specific user's mailbox."""
        if not user_id or not to_email or not subject or not body:
            raise InvalidParameterError("user_id, to_email, subject, and body are required.")
            
        url = f"{self.base_url}/users/{user_id}/sendMail"
        payload = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML" if is_html else "Text",
                    "content": body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": to_email
                        }
                    }
                ]
            }
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            # POST to sendMail usually responds with 202 Accepted and empty body
            return ActionResult.ok({"status": "Email sent successfully"})
        except Exception as e:
            raise ActionExecutionError(f"Failed to send email: {str(e)}")

    @register_action
    async def read_emails(self, user_id: str, folder: str = "inbox", top: int = 10) -> ActionResult:
        """Read emails from a specific user's folder."""
        if not user_id:
            raise InvalidParameterError("user_id is required.")
            
        url = f"{self.base_url}/users/{user_id}/mailFolders/{folder}/messages?$top={top}"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            return ActionResult.ok(data.get("value", data))
        except Exception as e:
            raise ActionExecutionError(f"Failed to read emails: {str(e)}")

    @register_action
    async def move_email(self, user_id: str, message_id: str, destination_id: str) -> ActionResult:
        """Move an email to a different folder."""
        if not user_id or not message_id or not destination_id:
            raise InvalidParameterError("user_id, message_id, and destination_id are required.")
            
        url = f"{self.base_url}/users/{user_id}/messages/{message_id}/move"
        payload = {
            "destinationId": destination_id
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            raise ActionExecutionError(f"Failed to move email: {str(e)}")

    async def parse_webhook(self, request: Any) -> WebhookEvent:
        """Parse incoming Microsoft Graph subscriptions webhook."""
        try:
            # Depending on framework, request may be a dict or a request object
            if hasattr(request, 'json'):
                payload = await request.json()
            else:
                payload = request

            # Microsoft Graph sends a validation token to verify subscription creation
            query_params = getattr(request, 'query_params', {})
            validation_token = query_params.get("validationToken")
            
            if validation_token:
                return WebhookEvent(
                    event_type=WebhookEventType.OTHER,
                    raw_data={"validationToken": validation_token}
                )

            return WebhookEvent(
                event_type=WebhookEventType.OTHER,
                raw_data=payload
            )
        except Exception as e:
            raise WebhookValidationError(f"Failed to parse MS Graph webhook: {str(e)}")
