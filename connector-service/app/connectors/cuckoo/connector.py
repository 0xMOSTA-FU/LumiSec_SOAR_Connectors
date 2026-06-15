import os
from typing import Any, Dict

from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult, WebhookEvent, WebhookEventType
from app.core.exceptions import (
    AuthenticationError, ConnectorHTTPError, InvalidParameterError,
    ActionExecutionError, WebhookValidationError
)

class CuckooConnector(BaseConnector):
    NAME = "cuckoo"
    VERSION = "1.0.0"
    DESCRIPTION = "Cuckoo Sandbox REST API v2 connector"

    async def test_connection(self) -> ConnectionResult:
        """
        Test the connection to the Cuckoo Sandbox REST API.
        
        Returns:
            ConnectionResult indicating success or failure.
        """
        try:
            response = await self.client.get("/cuckoo/status")
            response.raise_for_status()
            return ConnectionResult.ok()
        except Exception as e:
            return ConnectionResult.fail(f"Connection to Cuckoo Sandbox failed: {str(e)}")

    @register_action
    async def submit_file(self, file_path: str) -> ActionResult:
        """
        Submit a file to Cuckoo Sandbox for analysis.
        
        Args:
            file_path: The absolute path to the file to be analyzed.
            
        Returns:
            ActionResult containing the submitted task information.
        """
        if not file_path:
            raise InvalidParameterError("file_path parameter is required")
            
        if not os.path.exists(file_path):
            return ActionResult.fail(f"File not found at path: {file_path}")
            
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f)}
                response = await self.client.post("/tasks/create/file", files=files)
                response.raise_for_status()
                return ActionResult.ok(response.json())
        except Exception as e:
            return ActionResult.fail(f"Failed to submit file to Cuckoo: {str(e)}")

    @register_action
    async def submit_url(self, url: str) -> ActionResult:
        """
        Submit a URL to Cuckoo Sandbox for analysis.
        
        Args:
            url: The URL to be analyzed.
            
        Returns:
            ActionResult containing the submitted task information.
        """
        if not url:
            raise InvalidParameterError("url parameter is required")
            
        try:
            data = {"url": url}
            response = await self.client.post("/tasks/create/url", data=data)
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            return ActionResult.fail(f"Failed to submit URL to Cuckoo: {str(e)}")

    @register_action
    async def get_task_status(self, task_id: int) -> ActionResult:
        """
        Get the status and details of a specific analysis task.
        
        Args:
            task_id: The ID of the task to query.
            
        Returns:
            ActionResult containing the task information and status.
        """
        if not isinstance(task_id, int):
            raise InvalidParameterError("task_id must be an integer")
            
        try:
            response = await self.client.get(f"/tasks/view/{task_id}")
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            return ActionResult.fail(f"Failed to get task status for task_id {task_id}: {str(e)}")

    @register_action
    async def get_report(self, task_id: int) -> ActionResult:
        """
        Get the analysis report for a specific task.
        
        Args:
            task_id: The ID of the task to retrieve the report for.
            
        Returns:
            ActionResult containing the analysis report.
        """
        if not isinstance(task_id, int):
            raise InvalidParameterError("task_id must be an integer")
            
        try:
            response = await self.client.get(f"/tasks/report/{task_id}")
            response.raise_for_status()
            return ActionResult.ok(response.json())
        except Exception as e:
            return ActionResult.fail(f"Failed to get report for task_id {task_id}: {str(e)}")

    async def parse_webhook(self, request: Any) -> WebhookEvent:
        """
        Parse a generic webhook event from Cuckoo Sandbox.
        
        Args:
            request: The incoming webhook HTTP request object.
            
        Returns:
            WebhookEvent object representing the event.
        """
        try:
            body = await request.json()
            return WebhookEvent(
                type=WebhookEventType.GENERIC,
                payload=body
            )
        except Exception as e:
            raise ActionExecutionError(f"Failed to parse webhook: {str(e)}")
