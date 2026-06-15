"""
SOAR Connector Hub — VirusTotal Connector
=========================================
"""

from __future__ import annotations

import base64
import os
from typing import Any, Dict

from app.core.base_connector import BaseConnector, register_action
from app.core.exceptions import ActionExecutionError, InvalidParameterError
from app.core.models import ActionResult, ConnectionResult, WebhookEvent, WebhookEventType


class VirusTotalConnector(BaseConnector):
    NAME = "virustotal"
    VERSION = "1.0.0"
    DESCRIPTION = "VirusTotal v3 API connector for threat intelligence and scanning."

    async def test_connection(self) -> ConnectionResult:
        """Test API key by fetching the user profile."""
        try:
            http = await self._get_http_client()
            resp = await http.get("/users/me")
            if "data" in resp:
                return ConnectionResult(
                    success=True,
                    connector=self.NAME,
                    message=f"Connected successfully to VirusTotal. User: {resp['data'].get('id', 'Unknown')}"
                )
            return ConnectionResult(
                success=False,
                connector=self.NAME,
                message="Unexpected response from VirusTotal API."
            )
        except Exception as e:
            return ConnectionResult(success=False, connector=self.NAME, message=str(e))

    @register_action(
        name="scan_file",
        description="Upload a file for scanning by VirusTotal",
        category="scanning",
        tags=["file", "scan"]
    )
    async def scan_file(self, file_path: str) -> dict:
        if not os.path.exists(file_path):
            raise InvalidParameterError("file_path", f"File not found: {file_path}")
        
        http = await self._get_http_client()
        with open(file_path, "rb") as f:
            file_name = os.path.basename(file_path)
            files = {"file": (file_name, f)}
            # Note: ConnectorHTTPClient request supports files
            response = await http.request("POST", "/files", files=files)
            
            data = response.get("data", {})
            return {
                "id": data.get("id"),
                "type": data.get("type"),
                "links": data.get("links", {})
            }

    @register_action(
        name="scan_url",
        description="Submit a URL for scanning by VirusTotal",
        category="scanning",
        tags=["url", "scan"]
    )
    async def scan_url(self, url: str) -> dict:
        if not url:
            raise InvalidParameterError("url", "URL is required")
        
        http = await self._get_http_client()
        response = await http.post("/urls", data={"url": url})
        
        data = response.get("data", {})
        return {
            "id": data.get("id"),
            "type": data.get("type"),
            "links": data.get("links", {})
        }

    @register_action(
        name="get_file_report",
        description="Get full file report by hash",
        category="intelligence",
        tags=["file", "report", "hash"]
    )
    async def get_file_report(self, resource: str) -> dict:
        if not resource:
            raise InvalidParameterError("resource", "File hash is required")
            
        http = await self._get_http_client()
        response = await http.get(f"/files/{resource}")
        return response.get("data", {})

    @register_action(
        name="get_url_report",
        description="Get full URL report",
        category="intelligence",
        tags=["url", "report"]
    )
    async def get_url_report(self, url: str) -> dict:
        if not url:
            raise InvalidParameterError("url", "URL is required")
            
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        http = await self._get_http_client()
        response = await http.get(f"/urls/{url_id}")
        return response.get("data", {})

    @register_action(
        name="get_ip_report",
        description="Get full IP address report",
        category="intelligence",
        tags=["ip", "report"]
    )
    async def get_ip_report(self, ip: str) -> dict:
        if not ip:
            raise InvalidParameterError("ip", "IP address is required")
            
        http = await self._get_http_client()
        response = await http.get(f"/ip_addresses/{ip}")
        return response.get("data", {})

    @register_action(
        name="get_domain_report",
        description="Get full domain report",
        category="intelligence",
        tags=["domain", "report"]
    )
    async def get_domain_report(self, domain: str) -> dict:
        if not domain:
            raise InvalidParameterError("domain", "Domain is required")
            
        http = await self._get_http_client()
        response = await http.get(f"/domains/{domain}")
        return response.get("data", {})

    @register_action(
        name="get_file_behaviour",
        description="Get sandbox behaviour report for a file hash",
        category="intelligence",
        tags=["file", "sandbox", "behaviour"]
    )
    async def get_file_behaviour(self, hash: str, sandbox: str = "") -> dict:
        if not hash:
            raise InvalidParameterError("hash", "File hash is required")
            
        http = await self._get_http_client()
        if sandbox:
            response = await http.get(f"/file_behaviours/{sandbox}")
        else:
            response = await http.get(f"/files/{hash}/behaviours")
        return response

    @register_action(
        name="search",
        description="VT Intelligence search (Enterprise)",
        category="search",
        tags=["search", "intelligence"]
    )
    async def search(self, query: str, limit: int = 20, cursor: str = "") -> dict:
        if not query:
            raise InvalidParameterError("query", "Search query is required")
            
        http = await self._get_http_client()
        params = {"query": query, "limit": limit}
        if cursor:
            params["cursor"] = cursor
            
        response = await http.get("/intelligence/search", params=params)
        return response

    @register_action(
        name="get_object_relationships",
        description="Get related entities for a given object",
        category="intelligence",
        tags=["relationships", "graph"]
    )
    async def get_object_relationships(self, object_type: str, object_id: str, relationship: str, limit: int = 10) -> dict:
        valid_types = ["files", "urls", "domains", "ip_addresses"]
        if object_type not in valid_types:
            raise InvalidParameterError("object_type", f"Must be one of {valid_types}")
            
        http = await self._get_http_client()
        response = await http.get(f"/{object_type}/{object_id}/{relationship}", params={"limit": limit})
        return response

    @register_action(
        name="add_comment",
        description="Add a comment to an object",
        category="community",
        tags=["comment"]
    )
    async def add_comment(self, object_type: str, object_id: str, comment: str) -> dict:
        valid_types = ["files", "urls", "domains", "ip_addresses"]
        if object_type not in valid_types:
            raise InvalidParameterError("object_type", f"Must be one of {valid_types}")
            
        http = await self._get_http_client()
        payload = {
            "data": {
                "type": "comment",
                "attributes": {
                    "text": comment
                }
            }
        }
        response = await http.post(f"/{object_type}/{object_id}/comments", json=payload)
        return response.get("data", {})

    @register_action(
        name="get_comments",
        description="Get comments for an object",
        category="community",
        tags=["comment"]
    )
    async def get_comments(self, object_type: str, object_id: str, limit: int = 10) -> dict:
        valid_types = ["files", "urls", "domains", "ip_addresses"]
        if object_type not in valid_types:
            raise InvalidParameterError("object_type", f"Must be one of {valid_types}")
            
        http = await self._get_http_client()
        response = await http.get(f"/{object_type}/{object_id}/comments", params={"limit": limit})
        return response

    @register_action(
        name="get_analysis",
        description="Get analysis status",
        category="scanning",
        tags=["analysis"]
    )
    async def get_analysis(self, analysis_id: str) -> dict:
        if not analysis_id:
            raise InvalidParameterError("analysis_id", "Analysis ID is required")
            
        http = await self._get_http_client()
        response = await http.get(f"/analyses/{analysis_id}")
        return response.get("data", {})

    @register_action(
        name="download_file",
        description="Download a file sample (Enterprise API)",
        category="file",
        tags=["download", "sample"]
    )
    async def download_file(self, hash: str, output_path: str) -> dict:
        if not hash:
            raise InvalidParameterError("hash", "File hash is required")
            
        http = await self._get_http_client()
        response = await http.request("GET", f"/files/{hash}/download", raw_response=True)
        
        with open(output_path, "wb") as f:
            async for chunk in response.aiter_bytes():
                f.write(chunk)
                
        return {"status": "success", "file_path": output_path, "size": os.path.getsize(output_path)}

    @register_action(
        name="get_livehunt_rulesets",
        description="Get YARA LiveHunt rulesets (Enterprise)",
        category="hunting",
        tags=["yara", "livehunt"]
    )
    async def get_livehunt_rulesets(self, limit: int = 10) -> dict:
        http = await self._get_http_client()
        response = await http.get("/intelligence/hunting_rulesets", params={"limit": limit})
        return response

    @register_action(
        name="create_livehunt_ruleset",
        description="Create a YARA LiveHunt ruleset (Enterprise)",
        category="hunting",
        tags=["yara", "livehunt", "create"]
    )
    async def create_livehunt_ruleset(self, name: str, rules: str, enabled: bool = True) -> dict:
        if not name or not rules:
            raise InvalidParameterError("name/rules", "Name and rules are required")
            
        payload = {
            "data": {
                "type": "hunting_ruleset",
                "attributes": {
                    "name": name,
                    "rules": rules,
                    "enabled": enabled
                }
            }
        }
        
        http = await self._get_http_client()
        response = await http.post("/intelligence/hunting_rulesets", json=payload)
        return response.get("data", {})

    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> WebhookEvent | None:
        """Parse VirusTotal Hunting notifications."""
        if "type" in payload and "attributes" in payload:
            return WebhookEvent(
                connector=self.NAME,
                event_type=WebhookEventType.ALERT,
                raw_payload=payload,
                normalized={
                    "rule_name": payload.get("attributes", {}).get("rule_name"),
                    "tags": payload.get("attributes", {}).get("tags", []),
                },
                severity="high",
                tags=payload.get("attributes", {}).get("tags", [])
            )
        return WebhookEvent(
            connector=self.NAME,
            event_type=WebhookEventType.GENERIC,
            raw_payload=payload
        )
