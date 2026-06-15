from typing import Any, Dict, List, Optional
from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult, WebhookEvent, WebhookEventType
from app.core.exceptions import (
    AuthenticationError, ConnectorHTTPError, InvalidParameterError,
    ActionExecutionError, WebhookValidationError
)

class MISPConnector(BaseConnector):
    NAME = "misp"
    VERSION = "1.0.0"
    DESCRIPTION = "MISP (Malware Information Sharing Platform) Threat Intelligence Connector"

    def __init__(self, config: Dict[str, Any]) -> None:
        if "extra_headers" not in config:
            config["extra_headers"] = {}
        # Ensure correct Accept and Content-Type headers for MISP
        config["extra_headers"]["Accept"] = "application/json"
        config["extra_headers"]["Content-Type"] = "application/json"
        super().__init__(config)

    async def test_connection(self) -> ConnectionResult:
        """
        Verify connectivity and authentication by calling the /servers/getVersion endpoint.
        """
        try:
            client = await self._get_http_client()
            response = await client.get("/servers/getVersion")
            version = response.get("version", "Unknown") if isinstance(response, dict) else "Unknown"
            return ConnectionResult(
                success=True,
                connector=self.NAME,
                message=f"Connected to MISP successfully. Version: {version}",
                details={"version": version}
            )
        except Exception as e:
            return ConnectionResult(
                success=False,
                connector=self.NAME,
                message=f"Failed to connect to MISP: {str(e)}"
            )

    @register_action(
        name="search_events",
        description="Search for MISP events."
    )
    async def search_events(
        self,
        limit: int = 10,
        value: str = "",
        type: str = "",
        tags: Optional[List[str]] = None
    ) -> ActionResult:
        """
        Search for events in MISP.
        """
        tags = tags or []
        payload: Dict[str, Any] = {
            "limit": limit,
            "returnFormat": "json"
        }
        if value:
            payload["value"] = value
        if type:
            payload["type"] = type
        if tags:
            payload["tags"] = tags

        client = await self._get_http_client()
        result = await client.post("/events/restSearch", json=payload)
        return ActionResult.ok(connector=self.NAME, action="search_events", data=result)

    @register_action(
        name="get_event",
        description="Retrieve a specific event by ID."
    )
    async def get_event(self, event_id: str) -> ActionResult:
        """
        Retrieve an event's details.
        """
        if not event_id:
            raise InvalidParameterError(param="event_id", reason="event_id is required.")
        
        client = await self._get_http_client()
        result = await client.get(f"/events/view/{event_id}")
        return ActionResult.ok(connector=self.NAME, action="get_event", data=result)

    @register_action(
        name="add_event",
        description="Create a new event."
    )
    async def add_event(
        self,
        info: str,
        distribution: str = "0",
        threat_level_id: str = "1",
        analysis: str = "0"
    ) -> ActionResult:
        """
        Add a new MISP event.
        """
        if not info:
            raise InvalidParameterError(param="info", reason="info is required.")

        payload = {
            "Event": {
                "info": info,
                "distribution": distribution,
                "threat_level_id": threat_level_id,
                "analysis": analysis
            }
        }
        client = await self._get_http_client()
        result = await client.post("/events", json=payload)
        return ActionResult.ok(connector=self.NAME, action="add_event", data=result)

    @register_action(
        name="add_attribute",
        description="Add a new attribute to an existing event."
    )
    async def add_attribute(
        self,
        event_id: str,
        type: str,
        value: str,
        category: str = "Network activity",
        to_ids: bool = True,
        comment: str = ""
    ) -> ActionResult:
        """
        Add an attribute to a MISP event.
        """
        if not event_id:
            raise InvalidParameterError(param="event_id", reason="event_id is required.")
        if not type:
            raise InvalidParameterError(param="type", reason="type is required.")
        if not value:
            raise InvalidParameterError(param="value", reason="value is required.")

        payload = {
            "type": type,
            "value": value,
            "category": category,
            "to_ids": to_ids,
            "comment": comment
        }
        client = await self._get_http_client()
        result = await client.post(f"/attributes/add/{event_id}", json=payload)
        return ActionResult.ok(connector=self.NAME, action="add_attribute", data=result)

    @register_action(
        name="search_attributes",
        description="Search for MISP attributes."
    )
    async def search_attributes(
        self,
        limit: int = 10,
        value: str = "",
        type: str = ""
    ) -> ActionResult:
        """
        Search for attributes in MISP.
        """
        payload: Dict[str, Any] = {
            "limit": limit,
            "returnFormat": "json"
        }
        if value:
            payload["value"] = value
        if type:
            payload["type"] = type

        client = await self._get_http_client()
        result = await client.post("/attributes/restSearch", json=payload)
        return ActionResult.ok(connector=self.NAME, action="search_attributes", data=result)

    async def parse_webhook(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str],
    ) -> Optional[WebhookEvent]:
        """
        Parse an incoming webhook payload from MISP into a normalized WebhookEvent.
        """
        if not payload:
            return None
        
        event_data = payload.get("Event", payload)
        event_id = str(event_data.get("id", "")) if isinstance(event_data, dict) else ""
        info = event_data.get("info", "") if isinstance(event_data, dict) else ""

        return WebhookEvent(
            connector=self.NAME,
            event_type=WebhookEventType.GENERIC,
            raw_payload=payload,
            normalized={
                "event_id": event_id,
                "info": info,
                "action": payload.get("action", "unknown")
            }
        )
