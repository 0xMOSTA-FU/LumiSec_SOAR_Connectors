"""
SOAR Connector Hub — Wazuh Connector
====================================
"""

from __future__ import annotations

import httpx
import time
from typing import Any, Dict, List, Optional

from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult, WebhookEvent, WebhookEventType
from app.core.exceptions import InvalidParameterError, ActionExecutionError, AuthenticationError
from app.core.auth import BaseAuthHandler
from app.core.http_client import ConnectorHTTPClient


class WazuhJwtHandler(BaseAuthHandler):
    """Custom JWT Handler for Wazuh, which returns the token at data.token"""

    def __init__(
        self,
        username: str,
        password: str,
        token_endpoint: str,
        expiry_seconds: int = 900,
        verify_ssl: bool = True,
    ):
        self._username = username
        self._password = password
        self._token_endpoint = token_endpoint
        self._expiry_seconds = expiry_seconds
        self._verify_ssl = verify_ssl
        self._token: Optional[str] = None
        self._token_expiry: float = 0.0

    def _is_expired(self) -> bool:
        return time.monotonic() >= self._token_expiry - 60

    async def _refresh(self) -> None:
        try:
            async with httpx.AsyncClient(verify=self._verify_ssl) as client:
                auth = (self._username, self._password)
                response = await client.get(self._token_endpoint, auth=auth, timeout=10)
                response.raise_for_status()
                body = response.json()
                
                token = body.get("data", {}).get("token")
                if not token:
                    raise AuthenticationError("Token not found in Wazuh auth response.")
                self._token = token
                self._token_expiry = time.monotonic() + self._expiry_seconds
        except httpx.HTTPStatusError as e:
            raise AuthenticationError(f"Wazuh auth failed: HTTP {e.response.status_code}")

    async def get_headers(self) -> Dict[str, str]:
        if self._token is None or self._is_expired():
            await self._refresh()
        return {"Authorization": f"Bearer {self._token}"}


class WazuhConnector(BaseConnector):
    NAME = "wazuh"
    VERSION = "1.0.0"
    DESCRIPTION = "Wazuh REST API v4.x connector for SIEM and XDR."

    def _setup_auth(self, config: Dict[str, Any]) -> None:
        auth_type = config.get("auth_type", "no_auth")
        if auth_type == "jwt":
            auth_config = config.get("auth_config", {})
            self._auth_handler = WazuhJwtHandler(
                username=auth_config.get("username", ""),
                password=auth_config.get("password", ""),
                token_endpoint=auth_config.get("token_endpoint", ""),
                verify_ssl=config.get("verify_ssl", True)
            )
        else:
            super()._setup_auth(config)

    def _extract_data(self, response: dict) -> Any:
        if "data" in response:
            return response["data"]
        return response

    async def test_connection(self) -> ConnectionResult:
        try:
            http = await self._get_http_client()
            resp = await http.get("/manager/info")
            data = self._extract_data(resp)
            if "title" in data or "name" in data:
                return ConnectionResult(
                    success=True,
                    connector=self.NAME,
                    message="Connected successfully to Wazuh Manager."
                )
            return ConnectionResult(success=False, connector=self.NAME, message="Unexpected response")
        except Exception as e:
            return ConnectionResult(success=False, connector=self.NAME, message=str(e))

    @register_action("get_alerts", "Get security alerts", "monitoring", ["alerts"])
    async def get_alerts(self, limit: int = 20, offset: int = 0, level: str = "", rule_id: str = "", agent_id: str = "", sort: str = "-timestamp") -> dict:
        http = await self._get_http_client()
        params = {"limit": limit, "offset": offset, "sort": sort}
        if level: params["level"] = level
        if rule_id: params["rule_ids"] = rule_id
        if agent_id: params["agents_list"] = agent_id
        
        response = await http.get("/alerts", params=params)
        return self._extract_data(response)

    @register_action("get_alert", "Get a specific alert by ID", "monitoring", ["alert"])
    async def get_alert(self, alert_id: str) -> dict:
        http = await self._get_http_client()
        response = await http.get("/alerts", params={"q": f"id={alert_id}"})
        data = self._extract_data(response)
        return data

    @register_action("get_agents", "Get a list of agents", "inventory", ["agents"])
    async def get_agents(self, limit: int = 20, offset: int = 0, status: str = "", name: str = "", os_platform: str = "") -> dict:
        http = await self._get_http_client()
        params = {"limit": limit, "offset": offset}
        if status: params["status"] = status
        if name: params["q"] = f"name={name}"
        if os_platform: params["os.platform"] = os_platform
        
        response = await http.get("/agents", params=params)
        return self._extract_data(response)

    @register_action("get_agent_info", "Get detailed agent info", "inventory", ["agent"])
    async def get_agent_info(self, agent_id: str) -> dict:
        http = await self._get_http_client()
        response = await http.get(f"/agents/{agent_id}")
        return self._extract_data(response)

    @register_action("get_agent_key", "Get agent registration key", "inventory", ["agent", "key"])
    async def get_agent_key(self, agent_id: str) -> dict:
        http = await self._get_http_client()
        response = await http.get(f"/agents/{agent_id}/key")
        return self._extract_data(response)

    @register_action("restart_agent", "Restart a specific agent", "response", ["agent", "restart"])
    async def restart_agent(self, agent_id: str) -> dict:
        http = await self._get_http_client()
        response = await http.put(f"/agents/{agent_id}/restart")
        return self._extract_data(response)

    @register_action("restart_agents_in_group", "Restart all agents in a group", "response", ["group", "restart"])
    async def restart_agents_in_group(self, group_id: str) -> dict:
        http = await self._get_http_client()
        response = await http.put(f"/agents/group/{group_id}/restart")
        return self._extract_data(response)

    @register_action("delete_agent", "Delete an agent", "inventory", ["agent", "delete"])
    async def delete_agent(self, agent_id: str, purge: bool = False) -> dict:
        http = await self._get_http_client()
        response = await http.delete("/agents", params={"agents_list": agent_id, "purge": str(purge).lower()})
        return self._extract_data(response)

    @register_action("run_active_response", "Run active response command", "response", ["ar", "command"])
    async def run_active_response(self, agent_id: str, command: str, arguments: list = []) -> dict:
        http = await self._get_http_client()
        body = {
            "command": command,
            "arguments": arguments,
            "custom": False
        }
        params = {"agents_list": agent_id} if agent_id else {}
        response = await http.put("/active-response", json=body, params=params)
        return self._extract_data(response)

    @register_action("get_groups", "Get list of agent groups", "inventory", ["groups"])
    async def get_groups(self, limit: int = 20) -> dict:
        http = await self._get_http_client()
        response = await http.get("/groups", params={"limit": limit})
        return self._extract_data(response)

    @register_action("create_group", "Create an agent group", "inventory", ["group", "create"])
    async def create_group(self, group_id: str) -> dict:
        http = await self._get_http_client()
        response = await http.post("/groups", json={"group_id": group_id})
        return self._extract_data(response)

    @register_action("add_agent_to_group", "Add an agent to a group", "inventory", ["agent", "group"])
    async def add_agent_to_group(self, agent_id: str, group_id: str) -> dict:
        http = await self._get_http_client()
        response = await http.put(f"/agents/{agent_id}/group/{group_id}")
        return self._extract_data(response)

    @register_action("remove_agent_from_group", "Remove an agent from a group", "inventory", ["agent", "group"])
    async def remove_agent_from_group(self, agent_id: str, group_id: str) -> dict:
        http = await self._get_http_client()
        response = await http.delete(f"/agents/{agent_id}/group/{group_id}")
        return self._extract_data(response)

    @register_action("get_vulnerabilities", "Get agent vulnerabilities", "monitoring", ["vuln", "cve"])
    async def get_vulnerabilities(self, agent_id: str, limit: int = 20, severity: str = "", cve: str = "") -> dict:
        http = await self._get_http_client()
        params = {"limit": limit}
        if severity: params["severity"] = severity
        if cve: params["cve"] = cve
        response = await http.get(f"/vulnerability/{agent_id}", params=params)
        return self._extract_data(response)

    @register_action("get_sca_results", "Get Security Configuration Assessment results", "monitoring", ["sca"])
    async def get_sca_results(self, agent_id: str, limit: int = 20) -> dict:
        http = await self._get_http_client()
        response = await http.get(f"/sca/{agent_id}", params={"limit": limit})
        return self._extract_data(response)

    @register_action("get_sca_checks", "Get SCA checks for a policy", "monitoring", ["sca", "checks"])
    async def get_sca_checks(self, agent_id: str, policy_id: str, result: str = "") -> dict:
        http = await self._get_http_client()
        params = {}
        if result: params["result"] = result
        response = await http.get(f"/sca/{agent_id}/checks/{policy_id}", params=params)
        return self._extract_data(response)

    @register_action("get_fim_events", "Get File Integrity Monitoring events", "monitoring", ["fim"])
    async def get_fim_events(self, agent_id: str, limit: int = 20, file: str = "", type_: str = "") -> dict:
        http = await self._get_http_client()
        params = {"limit": limit}
        if file: params["file"] = file
        if type_: params["type"] = type_
        response = await http.get(f"/syscheck/{agent_id}", params=params)
        return self._extract_data(response)

    @register_action("run_rootcheck", "Run rootcheck on an agent", "response", ["rootcheck"])
    async def run_rootcheck(self, agent_id: str) -> dict:
        http = await self._get_http_client()
        response = await http.put("/rootcheck", params={"agents_list": agent_id})
        return self._extract_data(response)

    @register_action("get_rootcheck_results", "Get rootcheck results", "monitoring", ["rootcheck"])
    async def get_rootcheck_results(self, agent_id: str) -> dict:
        http = await self._get_http_client()
        response = await http.get(f"/rootcheck/{agent_id}")
        return self._extract_data(response)

    @register_action("get_rules", "Get Wazuh detection rules", "configuration", ["rules"])
    async def get_rules(self, limit: int = 20, offset: int = 0, status: str = "enabled", level: str = "", group: str = "") -> dict:
        http = await self._get_http_client()
        params = {"limit": limit, "offset": offset, "status": status}
        if level: params["level"] = level
        if group: params["group"] = group
        response = await http.get("/rules", params=params)
        return self._extract_data(response)

    @register_action("get_decoders", "Get Wazuh decoders", "configuration", ["decoders"])
    async def get_decoders(self, limit: int = 20, offset: int = 0) -> dict:
        http = await self._get_http_client()
        response = await http.get("/decoders", params={"limit": limit, "offset": offset})
        return self._extract_data(response)

    @register_action("get_statistics", "Get Wazuh manager statistics", "monitoring", ["stats"])
    async def get_statistics(self, component: str = "logcollector") -> dict:
        http = await self._get_http_client()
        response = await http.get(f"/manager/stats/{component}")
        return self._extract_data(response)

    @register_action("get_manager_info", "Get Wazuh manager info", "inventory", ["manager", "info"])
    async def get_manager_info(self) -> dict:
        http = await self._get_http_client()
        response = await http.get("/manager/info")
        return self._extract_data(response)

    @register_action("get_cluster_nodes", "Get cluster nodes list", "inventory", ["cluster"])
    async def get_cluster_nodes(self) -> dict:
        http = await self._get_http_client()
        response = await http.get("/cluster/nodes")
        return self._extract_data(response)

    @register_action("get_logs", "Get Wazuh manager logs", "monitoring", ["logs"])
    async def get_logs(self, limit: int = 20, offset: int = 0, level: str = "", tag: str = "") -> dict:
        http = await self._get_http_client()
        params = {"limit": limit, "offset": offset}
        if level: params["level"] = level
        if tag: params["tag"] = tag
        response = await http.get("/manager/logs", params=params)
        return self._extract_data(response)

    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> WebhookEvent | None:
        """Parse Wazuh Integratord webhooks."""
        rule = payload.get("rule", {})
        agent = payload.get("agent", {})
        
        level = int(rule.get("level", 0))
        if level >= 12:
            severity = "critical"
        elif level >= 8:
            severity = "high"
        elif level >= 4:
            severity = "medium"
        else:
            severity = "low"
            
        return WebhookEvent(
            connector=self.NAME,
            event_type=WebhookEventType.ALERT,
            raw_payload=payload,
            normalized={
                "rule_id": rule.get("id"),
                "description": rule.get("description"),
                "agent_id": agent.get("id"),
                "agent_name": agent.get("name"),
                "agent_ip": agent.get("ip")
            },
            severity=severity,
            tags=rule.get("groups", [])
        )
