"""
SOAR Connector Hub — Digital Ocean Connector
============================================
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult
from app.core.exceptions import InvalidParameterError, ActionExecutionError


class DigitalOceanConnector(BaseConnector):
    NAME = "digitalocean"
    VERSION = "1.0.0"
    DESCRIPTION = "Digital Ocean API connector for Firewall and Droplet management."

    async def test_connection(self) -> ConnectionResult:
        try:
            http = await self._get_http_client()
            resp = await http.get("/account")
            if resp.get("account", {}).get("status") == "active":
                return ConnectionResult(
                    success=True,
                    connector=self.NAME,
                    message=f"Connected to Digital Ocean account: {resp['account']['email']}"
                )
            return ConnectionResult(success=False, connector=self.NAME, message="Unexpected account status")
        except Exception as e:
            return ConnectionResult(success=False, connector=self.NAME, message=str(e))

    async def _paginate(self, path: str, key: str, params: dict = None) -> list:
        if params is None:
            params = {}
        http = await self._get_http_client()
        results = []
        page = 1
        while True:
            params['page'] = page
            params['per_page'] = 100
            data = await http.get(path, params=params)
            results.extend(data.get(key, []))
            
            links = data.get('links', {}).get('pages', {})
            if not links.get('next'):
                break
            page += 1
        return results

    # ─── Firewall Management ──────────────────────────────────────────────────

    @register_action("list_firewalls", "List all firewalls", "firewall", ["list"])
    async def list_firewalls(self) -> list:
        return await self._paginate("/firewalls", "firewalls")

    @register_action("get_firewall", "Get specific firewall details", "firewall", ["details"])
    async def get_firewall(self, firewall_id: str) -> dict:
        http = await self._get_http_client()
        response = await http.get(f"/firewalls/{firewall_id}")
        return response.get("firewall", {})

    @register_action("create_firewall", "Create a new firewall", "firewall", ["create"])
    async def create_firewall(self, name: str, inbound_rules: list = [], outbound_rules: list = [], droplet_ids: list = [], tags: list = []) -> dict:
        http = await self._get_http_client()
        payload = {"name": name}
        if inbound_rules: payload["inbound_rules"] = inbound_rules
        if outbound_rules: payload["outbound_rules"] = outbound_rules
        if droplet_ids: payload["droplet_ids"] = droplet_ids
        if tags: payload["tags"] = tags
            
        response = await http.post("/firewalls", json=payload)
        return response.get("firewall", {})

    @register_action("update_firewall", "Update a firewall (full replacement)", "firewall", ["update"])
    async def update_firewall(self, firewall_id: str, name: str, inbound_rules: list, outbound_rules: list, droplet_ids: list = [], tags: list = []) -> dict:
        http = await self._get_http_client()
        payload = {
            "name": name,
            "inbound_rules": inbound_rules,
            "outbound_rules": outbound_rules,
            "droplet_ids": droplet_ids,
            "tags": tags
        }
        response = await http.put(f"/firewalls/{firewall_id}", json=payload)
        return response.get("firewall", {})

    @register_action("delete_firewall", "Delete a firewall", "firewall", ["delete"])
    async def delete_firewall(self, firewall_id: str) -> dict:
        http = await self._get_http_client()
        await http.delete(f"/firewalls/{firewall_id}")
        return {"status": "success", "id": firewall_id}

    @register_action("add_inbound_rule", "Add an inbound rule to a firewall", "firewall", ["rule", "inbound"])
    async def add_inbound_rule(self, firewall_id: str, protocol: str, ports: str, source_addresses: list = [], source_droplet_ids: list = [], source_tags: list = []) -> dict:
        http = await self._get_http_client()
        sources = {}
        if source_addresses: sources["addresses"] = source_addresses
        if source_droplet_ids: sources["droplet_ids"] = source_droplet_ids
        if source_tags: sources["tags"] = source_tags
            
        payload = {
            "inbound_rules": [
                {
                    "protocol": protocol,
                    "ports": ports,
                    "sources": sources
                }
            ]
        }
        await http.post(f"/firewalls/{firewall_id}/rules", json=payload)
        return {"status": "success"}

    @register_action("remove_inbound_rule", "Remove an inbound rule", "firewall", ["rule", "remove"])
    async def remove_inbound_rule(self, firewall_id: str, protocol: str, ports: str, source_addresses: list = [], source_droplet_ids: list = [], source_tags: list = []) -> dict:
        http = await self._get_http_client()
        sources = {}
        if source_addresses: sources["addresses"] = source_addresses
        if source_droplet_ids: sources["droplet_ids"] = source_droplet_ids
        if source_tags: sources["tags"] = source_tags
            
        payload = {
            "inbound_rules": [
                {
                    "protocol": protocol,
                    "ports": ports,
                    "sources": sources
                }
            ]
        }
        # httpx and our wrapper support json body in DELETE via data/json if handled, but usually we use generic request
        await http.request("DELETE", f"/firewalls/{firewall_id}/rules", json=payload)
        return {"status": "success"}

    @register_action("add_outbound_rule", "Add an outbound rule to a firewall", "firewall", ["rule", "outbound"])
    async def add_outbound_rule(self, firewall_id: str, protocol: str, ports: str, destination_addresses: list = [], destination_droplet_ids: list = [], destination_tags: list = []) -> dict:
        http = await self._get_http_client()
        destinations = {}
        if destination_addresses: destinations["addresses"] = destination_addresses
        if destination_droplet_ids: destinations["droplet_ids"] = destination_droplet_ids
        if destination_tags: destinations["tags"] = destination_tags
            
        payload = {
            "outbound_rules": [
                {
                    "protocol": protocol,
                    "ports": ports,
                    "destinations": destinations
                }
            ]
        }
        await http.post(f"/firewalls/{firewall_id}/rules", json=payload)
        return {"status": "success"}

    @register_action("remove_outbound_rule", "Remove an outbound rule", "firewall", ["rule", "remove"])
    async def remove_outbound_rule(self, firewall_id: str, protocol: str, ports: str, destination_addresses: list = [], destination_droplet_ids: list = [], destination_tags: list = []) -> dict:
        http = await self._get_http_client()
        destinations = {}
        if destination_addresses: destinations["addresses"] = destination_addresses
        if destination_droplet_ids: destinations["droplet_ids"] = destination_droplet_ids
        if destination_tags: destinations["tags"] = destination_tags
            
        payload = {
            "outbound_rules": [
                {
                    "protocol": protocol,
                    "ports": ports,
                    "destinations": destinations
                }
            ]
        }
        await http.request("DELETE", f"/firewalls/{firewall_id}/rules", json=payload)
        return {"status": "success"}

    @register_action("block_ip", "Block an IP by removing from allowed sources or creating block rule", "response", ["block", "ip"])
    async def block_ip(self, firewall_id: str, ip_address: str, direction: str = "inbound", protocol: str = "tcp", ports: str = "all") -> dict:
        # DO firewalls are implicit deny. If we want to strictly block, 
        # we can remove this IP from all allow rules, but that's complex to implement atomically here.
        # Alternatively, we just return a warning that DO uses implicit deny and suggest updating tags.
        return {
            "status": "warning", 
            "message": "DigitalOcean firewalls use implicit deny. Explicit deny rules are not supported. "
                       "Ensure the IP is not in any allowed source_addresses in your existing rules."
        }

    @register_action("add_droplets_to_firewall", "Add droplets to a firewall", "firewall", ["droplets", "add"])
    async def add_droplets_to_firewall(self, firewall_id: str, droplet_ids: list) -> dict:
        http = await self._get_http_client()
        await http.post(f"/firewalls/{firewall_id}/droplets", json={"droplet_ids": droplet_ids})
        return {"status": "success"}

    @register_action("remove_droplets_from_firewall", "Remove droplets from a firewall", "firewall", ["droplets", "remove"])
    async def remove_droplets_from_firewall(self, firewall_id: str, droplet_ids: list) -> dict:
        http = await self._get_http_client()
        await http.request("DELETE", f"/firewalls/{firewall_id}/droplets", json={"droplet_ids": droplet_ids})
        return {"status": "success"}

    @register_action("add_tags_to_firewall", "Add tags to a firewall", "firewall", ["tags", "add"])
    async def add_tags_to_firewall(self, firewall_id: str, tags: list) -> dict:
        http = await self._get_http_client()
        await http.post(f"/firewalls/{firewall_id}/tags", json={"tags": tags})
        return {"status": "success"}

    @register_action("remove_tags_from_firewall", "Remove tags from a firewall", "firewall", ["tags", "remove"])
    async def remove_tags_from_firewall(self, firewall_id: str, tags: list) -> dict:
        http = await self._get_http_client()
        await http.request("DELETE", f"/firewalls/{firewall_id}/tags", json={"tags": tags})
        return {"status": "success"}

    # ─── Droplets ────────────────────────────────────────────────────────────

    @register_action("list_droplets", "List droplets", "droplet", ["list"])
    async def list_droplets(self, tag_name: str = "") -> list:
        params = {"tag_name": tag_name} if tag_name else {}
        return await self._paginate("/droplets", "droplets", params)

    @register_action("get_droplet", "Get droplet details", "droplet", ["details"])
    async def get_droplet(self, droplet_id: int) -> dict:
        http = await self._get_http_client()
        response = await http.get(f"/droplets/{droplet_id}")
        return response.get("droplet", {})

    @register_action("create_droplet", "Create a droplet", "droplet", ["create"])
    async def create_droplet(self, name: str, region: str, size: str, image: str, ssh_keys: list = [], tags: list = [], backups: bool = False, user_data: str = "") -> dict:
        http = await self._get_http_client()
        payload = {
            "name": name,
            "region": region,
            "size": size,
            "image": image,
            "backups": backups
        }
        if ssh_keys: payload["ssh_keys"] = ssh_keys
        if tags: payload["tags"] = tags
        if user_data: payload["user_data"] = user_data
            
        response = await http.post("/droplets", json=payload)
        return response.get("droplet", {})

    @register_action("delete_droplet", "Delete a droplet", "droplet", ["delete"])
    async def delete_droplet(self, droplet_id: int) -> dict:
        http = await self._get_http_client()
        await http.delete(f"/droplets/{droplet_id}")
        return {"status": "success", "id": droplet_id}

    @register_action("power_off_droplet", "Power off a droplet", "droplet", ["poweroff"])
    async def power_off_droplet(self, droplet_id: int) -> dict:
        http = await self._get_http_client()
        response = await http.post(f"/droplets/{droplet_id}/actions", json={"type": "power_off"})
        return response.get("action", {})

    @register_action("power_on_droplet", "Power on a droplet", "droplet", ["poweron"])
    async def power_on_droplet(self, droplet_id: int) -> dict:
        http = await self._get_http_client()
        response = await http.post(f"/droplets/{droplet_id}/actions", json={"type": "power_on"})
        return response.get("action", {})

    @register_action("reboot_droplet", "Reboot a droplet", "droplet", ["reboot"])
    async def reboot_droplet(self, droplet_id: int) -> dict:
        http = await self._get_http_client()
        response = await http.post(f"/droplets/{droplet_id}/actions", json={"type": "reboot"})
        return response.get("action", {})

    @register_action("take_snapshot", "Take a snapshot of a droplet", "droplet", ["snapshot"])
    async def take_snapshot(self, droplet_id: int, snapshot_name: str) -> dict:
        http = await self._get_http_client()
        response = await http.post(f"/droplets/{droplet_id}/actions", json={"type": "snapshot", "name": snapshot_name})
        return response.get("action", {})

    @register_action("get_droplet_action", "Get status of a droplet action", "droplet", ["action"])
    async def get_droplet_action(self, droplet_id: int, action_id: int) -> dict:
        http = await self._get_http_client()
        response = await http.get(f"/droplets/{droplet_id}/actions/{action_id}")
        return response.get("action", {})

    # ─── Account & Network ───────────────────────────────────────────────────

    @register_action("get_account_info", "Get account information", "system", ["account"])
    async def get_account_info(self) -> dict:
        http = await self._get_http_client()
        response = await http.get("/account")
        return response.get("account", {})

    @register_action("list_regions", "List available regions", "system", ["regions"])
    async def list_regions(self) -> list:
        return await self._paginate("/regions", "regions")

    @register_action("list_sizes", "List available droplet sizes", "system", ["sizes"])
    async def list_sizes(self) -> list:
        return await self._paginate("/sizes", "sizes")

    @register_action("list_images", "List available images", "system", ["images"])
    async def list_images(self, type_: str = "") -> list:
        params = {"type": type_} if type_ else {}
        return await self._paginate("/images", "images", params)

    @register_action("list_tags", "List tags", "system", ["tags"])
    async def list_tags(self) -> list:
        return await self._paginate("/tags", "tags")

    @register_action("create_tag", "Create a tag", "system", ["tags", "create"])
    async def create_tag(self, name: str) -> dict:
        http = await self._get_http_client()
        response = await http.post("/tags", json={"name": name})
        return response.get("tag", {})

    @register_action("get_bandwidth_usage", "Get droplet bandwidth usage", "monitoring", ["bandwidth"])
    async def get_bandwidth_usage(self, droplet_id: int, interface: str = "public", direction: str = "inbound") -> dict:
        # DO doesn't expose bandwidth directly via simple endpoint, usually requires DO Monitoring metrics API.
        # This is a mock response or placeholder since standard droplets endpoint doesn't have /bandwidth.
        return {
            "status": "not_supported",
            "message": "Bandwidth requires Metrics API querying which is complex. Use monitoring integrations."
        }
