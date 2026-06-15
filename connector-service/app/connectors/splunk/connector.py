"""
SOAR Connector Hub — Splunk Connector
=====================================
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, List, Optional

from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult, WebhookEvent, WebhookEventType
from app.core.exceptions import InvalidParameterError, ActionExecutionError, ConfigurationError
from app.core.http_client import ConnectorHTTPClient


class SplunkConnector(BaseConnector):
    NAME = "splunk"
    VERSION = "1.0.0"
    DESCRIPTION = "Splunk REST API and HTTP Event Collector (HEC) connector."

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self._hec_url = self._raw_config.get("hec_url", "")
        self._hec_token = self._raw_config.get("hec_token", "")
        self._hec_http: Optional[ConnectorHTTPClient] = None

    async def _get_hec_http(self) -> ConnectorHTTPClient:
        if not self._hec_url or not self._hec_token:
            raise ConfigurationError("hec_url and hec_token are required for HEC actions")
            
        if self._hec_http is None:
            self._hec_http = ConnectorHTTPClient(
                base_url=self._hec_url,
                headers={"Authorization": f"Splunk {self._hec_token}"},
                timeout=self._raw_config.get("timeout_seconds", 30),
                verify_ssl=self._raw_config.get("verify_ssl", True)
            )
            await self._hec_http._open()
        return self._hec_http

    async def close(self) -> None:
        await super().close()
        if self._hec_http:
            await self._hec_http._close()

    async def test_connection(self) -> ConnectionResult:
        try:
            http = await self._get_http_client()
            resp = await http.get("/services/server/info?output_mode=json")
            entry = resp.get("entry", [])
            if entry:
                version = entry[0].get("content", {}).get("version", "unknown")
                return ConnectionResult(
                    success=True,
                    connector=self.NAME,
                    message=f"Connected successfully to Splunk (Version: {version})"
                )
            return ConnectionResult(success=False, connector=self.NAME, message="Unexpected response format")
        except Exception as e:
            return ConnectionResult(success=False, connector=self.NAME, message=str(e))

    # ─── Search ──────────────────────────────────────────────────────────────

    @register_action("search", "Run a Splunk search job", "search", ["search", "job"])
    async def search(self, query: str, earliest_time: str = "-24h", latest_time: str = "now", max_results: int = 100, mode: str = "normal") -> list:
        if not query.strip().startswith("search "):
            query = f"search {query}"
            
        http = await self._get_http_client()
        
        # 1. Create Job
        payload = {
            "search": query,
            "earliest_time": earliest_time,
            "latest_time": latest_time,
            "output_mode": "json"
        }
        resp = await http.post("/services/search/jobs", data=payload)
        job_id = resp.get("sid")
        if not job_id:
            raise ActionExecutionError(f"Failed to get job ID: {resp}")

        # 2. Poll Job
        for _ in range(30):
            job_resp = await http.get(f"/services/search/jobs/{job_id}?output_mode=json")
            entry = job_resp.get("entry", [])
            if entry:
                state = entry[0].get("content", {}).get("dispatchState")
                if state == "DONE":
                    break
                elif state == "FAILED":
                    raise ActionExecutionError("Search job failed")
            await asyncio.sleep(2)

        # 3. Get Results
        res_resp = await http.get(f"/services/search/jobs/{job_id}/results?output_mode=json&count={max_results}")
        return res_resp.get("results", [])

    @register_action("search_oneshot", "Run a blocking oneshot search", "search", ["search", "oneshot"])
    async def search_oneshot(self, query: str, earliest_time: str = "-1h", latest_time: str = "now", max_results: int = 100) -> list:
        if not query.strip().startswith("search "):
            query = f"search {query}"
            
        http = await self._get_http_client()
        payload = {
            "search": query,
            "earliest_time": earliest_time,
            "latest_time": latest_time,
            "output_mode": "json"
        }
        resp = await http.request("POST", "/services/search/jobs/export", data=payload, raw_response=True)
        
        results = []
        async for line in resp.aiter_lines():
            if line.strip():
                try:
                    results.append(json.loads(line).get("result", {}))
                except Exception:
                    pass
        return results[:max_results]

    @register_action("get_search_job", "Get search job status", "search", ["job", "status"])
    async def get_search_job(self, job_id: str) -> dict:
        http = await self._get_http_client()
        resp = await http.get(f"/services/search/jobs/{job_id}?output_mode=json")
        entry = resp.get("entry", [])
        if entry:
            return entry[0].get("content", {})
        return {}

    @register_action("get_search_results", "Get search job results", "search", ["job", "results"])
    async def get_search_results(self, job_id: str, count: int = 100, offset: int = 0) -> list:
        http = await self._get_http_client()
        resp = await http.get(f"/services/search/jobs/{job_id}/results?output_mode=json&count={count}&offset={offset}")
        return resp.get("results", [])

    @register_action("cancel_search_job", "Cancel a search job", "search", ["job", "cancel"])
    async def cancel_search_job(self, job_id: str) -> dict:
        http = await self._get_http_client()
        # To delete, POST with action=cancel or use DELETE method
        await http.request("DELETE", f"/services/search/jobs/{job_id}")
        return {"status": "success", "job_id": job_id}

    @register_action("create_saved_search", "Create a saved search", "search", ["saved", "create"])
    async def create_saved_search(self, name: str, query: str, description: str = "", cron_schedule: str = "", is_scheduled: bool = False, alert_type: str = "always", alert_actions: list = []) -> dict:
        http = await self._get_http_client()
        payload = {
            "name": name,
            "search": query,
            "description": description,
            "output_mode": "json"
        }
        if is_scheduled:
            payload["is_scheduled"] = 1
            payload["cron_schedule"] = cron_schedule
        if alert_actions:
            payload["actions"] = ",".join(alert_actions)
            
        resp = await http.post("/services/saved/searches", data=payload)
        return resp.get("entry", [{}])[0]

    @register_action("list_saved_searches", "List saved searches", "search", ["saved", "list"])
    async def list_saved_searches(self, app: str = "") -> list:
        http = await self._get_http_client()
        url = f"/servicesNS/nobody/{app}/saved/searches" if app else "/services/saved/searches"
        resp = await http.get(f"{url}?output_mode=json")
        return [e.get("name") for e in resp.get("entry", [])]

    @register_action("run_saved_search", "Dispatch a saved search", "search", ["saved", "run"])
    async def run_saved_search(self, saved_search_name: str) -> dict:
        http = await self._get_http_client()
        resp = await http.post(f"/services/saved/searches/{saved_search_name}/dispatch", data={"output_mode": "json"})
        return {"sid": resp.get("sid")}

    @register_action("delete_saved_search", "Delete a saved search", "search", ["saved", "delete"])
    async def delete_saved_search(self, name: str) -> dict:
        http = await self._get_http_client()
        await http.request("DELETE", f"/services/saved/searches/{name}")
        return {"status": "success", "name": name}

    # ─── HEC ─────────────────────────────────────────────────────────────────

    @register_action("send_event_hec", "Send single event to HEC", "ingest", ["hec", "event"])
    async def send_event_hec(self, event: dict, index: str = "", source: str = "soar-connector", sourcetype: str = "json", host: str = "") -> dict:
        hec_http = await self._get_hec_http()
        payload = {
            "event": event,
            "source": source,
            "sourcetype": sourcetype,
            "time": time.time()
        }
        if index: payload["index"] = index
        if host: payload["host"] = host
            
        resp = await hec_http.post("/services/collector/event", json=payload)
        return resp

    @register_action("send_events_batch_hec", "Send batch of events to HEC", "ingest", ["hec", "batch"])
    async def send_events_batch_hec(self, events: list, index: str = "", sourcetype: str = "json") -> dict:
        hec_http = await self._get_hec_http()
        payload = ""
        for e in events:
            item = {"event": e, "sourcetype": sourcetype}
            if index: item["index"] = index
            payload += json.dumps(item) + "\n"
            
        resp = await hec_http.request("POST", "/services/collector/event", data=payload)
        return resp

    @register_action("send_raw_hec", "Send raw string to HEC", "ingest", ["hec", "raw"])
    async def send_raw_hec(self, raw_text: str, index: str = "", sourcetype: str = "_raw") -> dict:
        hec_http = await self._get_hec_http()
        params = {"sourcetype": sourcetype}
        if index: params["index"] = index
        resp = await hec_http.post("/services/collector/raw", params=params, data=raw_text.encode())
        return resp

    # ─── Splunk ES ───────────────────────────────────────────────────────────

    @register_action("get_notable_events", "Get notable events from Splunk ES", "es", ["notable"])
    async def get_notable_events(self, earliest_time: str = "-24h", latest_time: str = "now", urgency: str = "", owner: str = "", limit: int = 20) -> list:
        query = 'search index=notable | search status!="closed"'
        if urgency: query += f' | search urgency="{urgency}"'
        if owner: query += f' | search owner="{owner}"'
        return await self.search(query=query, earliest_time=earliest_time, latest_time=latest_time, max_results=limit)

    @register_action("update_notable_status", "Update notable event status", "es", ["notable", "update"])
    async def update_notable_status(self, event_ids: list, status: str, comment: str = "", owner: str = "") -> dict:
        http = await self._get_http_client()
        payload = {
            "ruleUIDs": event_ids,
            "status": status,
            "comment": comment,
            "output_mode": "json"
        }
        if owner: payload["newOwner"] = owner
        resp = await http.post("/services/notable_update", data=payload)
        return resp

    @register_action("create_correlation_search", "Create ES correlation search", "es", ["correlation"])
    async def create_correlation_search(self, name: str, search: str, description: str = "", cron_schedule: str = "*/5 * * * *", severity: str = "high") -> dict:
        # ES correlation searches are just saved searches with specific metadata/actions
        return await self.create_saved_search(
            name=name,
            query=search,
            description=description,
            cron_schedule=cron_schedule,
            is_scheduled=True,
            alert_actions=["notable"]
        )

    # ─── Indexes & Data ──────────────────────────────────────────────────────

    @register_action("list_indexes", "List all indexes", "data", ["indexes"])
    async def list_indexes(self) -> list:
        http = await self._get_http_client()
        resp = await http.get("/services/data/indexes?output_mode=json")
        return [{"name": e.get("name"), "totalEventCount": e.get("content", {}).get("totalEventCount")} for e in resp.get("entry", [])]

    @register_action("get_index_info", "Get index info", "data", ["index"])
    async def get_index_info(self, index_name: str) -> dict:
        http = await self._get_http_client()
        resp = await http.get(f"/services/data/indexes/{index_name}?output_mode=json")
        entry = resp.get("entry", [])
        return entry[0].get("content", {}) if entry else {}

    @register_action("create_index", "Create an index", "data", ["index", "create"])
    async def create_index(self, index_name: str, max_hot_buckets: int = 3, max_total_data_size_mb: int = 500000) -> dict:
        http = await self._get_http_client()
        payload = {
            "name": index_name,
            "maxHotBuckets": max_hot_buckets,
            "maxTotalDataSizeMB": max_total_data_size_mb,
            "output_mode": "json"
        }
        resp = await http.post("/services/data/indexes", data=payload)
        return resp.get("entry", [{}])[0]

    # ─── Dashboards & Reports ────────────────────────────────────────────────

    @register_action("list_dashboards", "List dashboards", "ui", ["dashboards"])
    async def list_dashboards(self, app: str = "") -> list:
        http = await self._get_http_client()
        url = f"/servicesNS/nobody/{app}/data/ui/views" if app else "/services/data/ui/views"
        resp = await http.get(f"{url}?output_mode=json&type=views")
        return [e.get("name") for e in resp.get("entry", [])]

    @register_action("list_reports", "List scheduled reports", "reports", ["reports"])
    async def list_reports(self) -> list:
        http = await self._get_http_client()
        resp = await http.get("/services/saved/searches?output_mode=json&search=is_scheduled=1")
        return [e.get("name") for e in resp.get("entry", [])]

    @register_action("get_field_summary", "Get field summary", "data", ["fields", "summary"])
    async def get_field_summary(self, index: str, field: str, earliest_time: str = "-24h") -> list:
        query = f"search index={index} | fieldsummary | search field=\"{field}\""
        return await self.search(query, earliest_time=earliest_time)

    # ─── System ──────────────────────────────────────────────────────────────

    @register_action("get_server_info", "Get server info", "system", ["server"])
    async def get_server_info(self) -> dict:
        http = await self._get_http_client()
        resp = await http.get("/services/server/info?output_mode=json")
        entry = resp.get("entry", [])
        return entry[0].get("content", {}) if entry else {}

    @register_action("list_apps", "List installed apps", "system", ["apps"])
    async def list_apps(self) -> list:
        http = await self._get_http_client()
        resp = await http.get("/services/apps/local?output_mode=json")
        return [e.get("name") for e in resp.get("entry", [])]

    @register_action("get_license_usage", "Get license usage", "system", ["license"])
    async def get_license_usage(self) -> dict:
        http = await self._get_http_client()
        resp = await http.get("/services/licenser/usage?output_mode=json")
        entry = resp.get("entry", [])
        return entry[0].get("content", {}) if entry else {}

    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> WebhookEvent | None:
        """Parse Splunk Alert webhook payload."""
        result = payload.get("result", {})
        return WebhookEvent(
            connector=self.NAME,
            event_type=WebhookEventType.ALERT,
            raw_payload=payload,
            normalized={
                "search_name": payload.get("search_name"),
                "owner": payload.get("owner"),
                "results_link": payload.get("results_link"),
                "result_count": result.get("_count")
            },
            severity="high"
        )
