from typing import Any, Optional

from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult, WebhookEvent, WebhookEventType
from app.core.exceptions import ActionExecutionError, WebhookValidationError


class JiraConnector(BaseConnector):
    NAME = "Jira"
    VERSION = "1.0.0"
    DESCRIPTION = "Jira Cloud Connector for managing issues and comments."

    async def test_connection(self) -> ConnectionResult:
        """Test the connection to the Jira API by requesting the user's profile."""
        try:
            response = await self.client.get("/rest/api/2/myself")
            response.raise_for_status()
            return ConnectionResult(success=True, message="Connection successful")
        except Exception as e:
            return ConnectionResult(success=False, message=f"Connection failed: {str(e)}")

    @register_action
    async def create_issue(
        self,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str = "Task"
    ) -> ActionResult:
        """
        Create a new issue in Jira.
        
        Args:
            project_key: The key of the project to create the issue in.
            summary: The summary (title) of the issue.
            description: The description of the issue.
            issue_type: The type of issue (e.g., Task, Bug, Story).
        """
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type}
            }
        }
        try:
            response = await self.client.post("/rest/api/2/issue", json=payload)
            response.raise_for_status()
            return ActionResult.ok(data=response.json())
        except Exception as e:
            raise ActionExecutionError(f"Failed to create issue: {str(e)}")

    @register_action
    async def update_issue(
        self,
        issue_id: str,
        summary: Optional[str] = None,
        description: Optional[str] = None
    ) -> ActionResult:
        """
        Update an existing Jira issue.
        
        Args:
            issue_id: The ID or key of the issue to update.
            summary: The new summary (optional).
            description: The new description (optional).
        """
        fields = {}
        if summary is not None:
            fields["summary"] = summary
        if description is not None:
            fields["description"] = description
            
        payload = {"fields": fields}
        try:
            response = await self.client.put(f"/rest/api/2/issue/{issue_id}", json=payload)
            response.raise_for_status()
            
            # Jira PUT usually returns 204 No Content
            if response.status_code == 204:
                return ActionResult.ok(data={"message": f"Issue {issue_id} updated successfully"})
                
            return ActionResult.ok(data=response.json())
        except Exception as e:
            raise ActionExecutionError(f"Failed to update issue {issue_id}: {str(e)}")

    @register_action
    async def add_comment(
        self,
        issue_id: str,
        comment: str
    ) -> ActionResult:
        """
        Add a comment to a Jira issue.
        
        Args:
            issue_id: The ID or key of the issue to comment on.
            comment: The comment text.
        """
        payload = {"body": comment}
        try:
            response = await self.client.post(f"/rest/api/2/issue/{issue_id}/comment", json=payload)
            response.raise_for_status()
            return ActionResult.ok(data=response.json())
        except Exception as e:
            raise ActionExecutionError(f"Failed to add comment to issue {issue_id}: {str(e)}")

    async def parse_webhook(self, request: Any) -> WebhookEvent:
        """Parse generic Jira webhook events."""
        try:
            payload = await request.json()
            return WebhookEvent(
                event_type=WebhookEventType.GENERIC,
                raw_data=payload
            )
        except Exception as e:
            raise WebhookValidationError(f"Invalid Jira webhook payload: {str(e)}")
