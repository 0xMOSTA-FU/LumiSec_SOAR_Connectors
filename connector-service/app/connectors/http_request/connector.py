"""
SOAR Connector Hub — Generic HTTP Request
=========================================
"""

from __future__ import annotations

import json
from typing import Any, Dict

import httpx

from app.core.base_connector import BaseConnector, register_action
from app.core.models import ConnectionResult
from app.core.exceptions import ActionExecutionError


class HttpRequestConnector(BaseConnector):
    NAME = "http_request"
    VERSION = "1.0.0"
    DESCRIPTION = "Make arbitrary HTTP/S requests to any external API or webhook."

    async def test_connection(self) -> ConnectionResult:
        return ConnectionResult(
            success=True,
            connector=self.NAME,
            message="HTTP Request connector is active and ready."
        )

    @register_action("make_request", "Send an HTTP request", "network", ["http", "api", "request"])
    async def make_request(
        self,
        url: str,
        method: str = "GET",
        headers: dict = {},
        query_params: dict = {},
        payload: dict = {},
        content_type: str = "application/json",
        timeout: int = 30
    ) -> dict:
        method = method.upper()
        if method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
            raise ActionExecutionError(f"Invalid HTTP method: {method}")

        req_headers = {k: v for k, v in headers.items()}
        
        # Determine payload formatting based on content type
        json_body = None
        data_body = None
        
        if method in ["POST", "PUT", "PATCH", "DELETE"]:
            if "json" in content_type.lower():
                json_body = payload
                req_headers["Content-Type"] = "application/json"
            elif "form-urlencoded" in content_type.lower():
                data_body = payload
                req_headers["Content-Type"] = "application/x-www-form-urlencoded"
            else:
                # If it's a string disguised as a dict or just standard data
                data_body = payload
                req_headers["Content-Type"] = content_type

        # We create a clean httpx AsyncClient for this single ad-hoc request.
        # We don't use self._get_http_client() because that binds to a specific base_url
        # configured globally for the connector, whereas this action needs to hit ANY url.
        try:
            async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=req_headers,
                    params=query_params,
                    json=json_body,
                    data=data_body
                )
                
                # Try to parse response as JSON, fallback to text
                try:
                    response_data = response.json()
                except Exception:
                    response_data = response.text

                return {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response_data,
                    "url": str(response.url)
                }
        except Exception as e:
            raise ActionExecutionError(f"HTTP Request failed: {str(e)}")
