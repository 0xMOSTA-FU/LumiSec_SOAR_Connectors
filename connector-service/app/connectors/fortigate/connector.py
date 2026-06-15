"""
SOAR Connector Hub — FortiGate Connector
========================================
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult, WebhookEvent, WebhookEventType
from app.core.exceptions import InvalidParameterError, ActionExecutionError


class FortiGateConnector(BaseConnector):
    NAME = "fortigate"
    VERSION = "1.0.0"
    DESCRIPTION = "FortiGate (FortiOS REST API) connector for firewall management."

    def _extract_results(self, response: dict) -> Any:
        if response.get("status") == "success" or response.get("http_status") in [200, 201]:
            return response.get("results", response.get("result", response))
        raise ActionExecutionError(f"FortiGate error: {response.get('cli_error', response)}")

    def _append_token(self, path: str) -> str:
        """FortiGate sometimes requires token in query string."""
        if "auth_config" in self._raw_config and "token" in self._raw_config["auth_config"]:
            token = self._raw_config["auth_config"]["token"]
            sep = "&" if "?" in path else "?"
            return f"{path}{sep}access_token={token}"
        return path

    async def _get(self, path: str, **kwargs) -> Any:
        http = await self._get_http_client()
        return await http.get(self._append_token(path), **kwargs)

    async def _post(self, path: str, **kwargs) -> Any:
        http = await self._get_http_client()
        return await http.post(self._append_token(path), **kwargs)

    async def _put(self, path: str, **kwargs) -> Any:
        http = await self._get_http_client()
        return await http.put(self._append_token(path), **kwargs)

    async def _delete(self, path: str, **kwargs) -> Any:
        http = await self._get_http_client()
        return await http.delete(self._append_token(path), **kwargs)

    async def test_connection(self) -> ConnectionResult:
        try:
            resp = await self._get("/monitor/system/status")
            if resp.get("status") == "success":
                return ConnectionResult(
                    success=True,
                    connector=self.NAME,
                    message="Connected successfully to FortiGate."
                )
            return ConnectionResult(success=False, connector=self.NAME, message="Unexpected response")
        except Exception as e:
            return ConnectionResult(success=False, connector=self.NAME, message=str(e))

    # ─── Firewall Policy ─────────────────────────────────────────────────────

    @register_action("get_firewall_policies", "Get firewall policies", "firewall", ["policy", "list"])
    async def get_firewall_policies(self, vdom: str = "root") -> list:
        resp = await self._get(f"/cmdb/firewall/policy/?vdom={vdom}")
        return self._extract_results(resp)

    @register_action("get_firewall_policy", "Get a specific firewall policy", "firewall", ["policy"])
    async def get_firewall_policy(self, policy_id: int, vdom: str = "root") -> dict:
        resp = await self._get(f"/cmdb/firewall/policy/{policy_id}/?vdom={vdom}")
        return self._extract_results(resp)

    @register_action("create_firewall_policy", "Create a firewall policy", "firewall", ["policy", "create"])
    async def create_firewall_policy(self, policy: dict, vdom: str = "root") -> dict:
        resp = await self._post(f"/cmdb/firewall/policy/?vdom={vdom}", json=policy)
        return self._extract_results(resp)

    @register_action("update_firewall_policy", "Update a firewall policy", "firewall", ["policy", "update"])
    async def update_firewall_policy(self, policy_id: int, updates: dict, vdom: str = "root") -> dict:
        resp = await self._put(f"/cmdb/firewall/policy/{policy_id}/?vdom={vdom}", json=updates)
        return self._extract_results(resp)

    @register_action("delete_firewall_policy", "Delete a firewall policy", "firewall", ["policy", "delete"])
    async def delete_firewall_policy(self, policy_id: int, vdom: str = "root") -> dict:
        resp = await self._delete(f"/cmdb/firewall/policy/{policy_id}/?vdom={vdom}")
        return self._extract_results(resp)

    @register_action("move_firewall_policy", "Move a firewall policy", "firewall", ["policy", "move"])
    async def move_firewall_policy(self, policy_id: int, position: str, neighbour: int, vdom: str = "root") -> dict:
        if position not in ["before", "after"]:
            raise InvalidParameterError("position", "Must be 'before' or 'after'")
        resp = await self._put(f"/cmdb/firewall/policy/{policy_id}/?action=move&{position}={neighbour}&vdom={vdom}")
        return self._extract_results(resp)

    # ─── Address Objects ─────────────────────────────────────────────────────

    @register_action("get_address_objects", "Get address objects", "objects", ["address"])
    async def get_address_objects(self, vdom: str = "root") -> list:
        resp = await self._get(f"/cmdb/firewall/address/?vdom={vdom}")
        return self._extract_results(resp)

    @register_action("get_address_object", "Get specific address object", "objects", ["address"])
    async def get_address_object(self, name: str, vdom: str = "root") -> dict:
        resp = await self._get(f"/cmdb/firewall/address/{name}/?vdom={vdom}")
        return self._extract_results(resp)

    @register_action("create_address_object", "Create an address object", "objects", ["address", "create"])
    async def create_address_object(self, name: str, subnet: str = "", fqdn: str = "", type_: str = "ipmask", comment: str = "", vdom: str = "root") -> dict:
        payload = {"name": name, "type": type_, "comment": comment}
        if type_ == "ipmask":
            payload["subnet"] = subnet or "0.0.0.0 0.0.0.0"
        elif type_ == "fqdn":
            payload["fqdn"] = fqdn
            
        resp = await self._post(f"/cmdb/firewall/address/?vdom={vdom}", json=payload)
        return self._extract_results(resp)

    @register_action("delete_address_object", "Delete an address object", "objects", ["address", "delete"])
    async def delete_address_object(self, name: str, vdom: str = "root") -> dict:
        resp = await self._delete(f"/cmdb/firewall/address/{name}/?vdom={vdom}")
        return self._extract_results(resp)

    # ─── Quick Block/Unblock ─────────────────────────────────────────────────

    @register_action("block_ip", "Block an IP address quickly", "response", ["block", "ip"])
    async def block_ip(self, ip: str, comment: str = "Blocked by SOAR", vdom: str = "root") -> dict:
        addr_name = f"SOAR-BLOCK-{ip}"
        
        # 1. Create Address Object
        try:
            await self.create_address_object(name=addr_name, subnet=f"{ip} 255.255.255.255", comment=comment, vdom=vdom)
        except ActionExecutionError:
            pass # Might already exist
            
        # 2. Create Deny Policy
        policy = {
            "name": addr_name,
            "srcintf": [{"name": "any"}],
            "dstintf": [{"name": "any"}],
            "srcaddr": [{"name": addr_name}],
            "dstaddr": [{"name": "all"}],
            "action": "deny",
            "schedule": "always",
            "service": [{"name": "ALL"}]
        }
        resp = await self._post(f"/cmdb/firewall/policy/?vdom={vdom}", json=policy)
        
        # 3. Move policy to top
        results = self._extract_results(resp)
        policy_id = results.get("mkey")
        if policy_id:
            # Move to top by moving before the first policy. Requires getting policies first
            all_pol = await self.get_firewall_policies(vdom=vdom)
            if all_pol and len(all_pol) > 0:
                first_pol_id = all_pol[0].get("policyid")
                if first_pol_id and first_pol_id != policy_id:
                    await self.move_firewall_policy(policy_id, "before", first_pol_id, vdom)
                    
        return {"status": "success", "policy_id": policy_id, "address_object": addr_name}

    @register_action("unblock_ip", "Unblock an IP address", "response", ["unblock", "ip"])
    async def unblock_ip(self, ip: str, policy_id: int = 0, vdom: str = "root") -> dict:
        addr_name = f"SOAR-BLOCK-{ip}"
        
        if policy_id == 0:
            # Find policy
            all_pol = await self.get_firewall_policies(vdom=vdom)
            for p in all_pol:
                if p.get("name") == addr_name or (p.get("srcaddr") and p["srcaddr"][0].get("name") == addr_name):
                    policy_id = p.get("policyid")
                    break
                    
        if policy_id != 0:
            await self.delete_firewall_policy(policy_id, vdom)
            
        # Delete address object
        try:
            await self.delete_address_object(addr_name, vdom)
        except ActionExecutionError:
            pass
            
        return {"status": "success", "unblocked_ip": ip}

    # ─── Address Groups ──────────────────────────────────────────────────────

    @register_action("get_address_groups", "Get address groups", "objects", ["group"])
    async def get_address_groups(self, vdom: str = "root") -> list:
        resp = await self._get(f"/cmdb/firewall/addrgrp/?vdom={vdom}")
        return self._extract_results(resp)

    @register_action("create_address_group", "Create an address group", "objects", ["group", "create"])
    async def create_address_group(self, name: str, members: list, vdom: str = "root") -> dict:
        payload = {"name": name, "member": [{"name": m} for m in members]}
        resp = await self._post(f"/cmdb/firewall/addrgrp/?vdom={vdom}", json=payload)
        return self._extract_results(resp)

    @register_action("add_member_to_group", "Add a member to an address group", "objects", ["group", "add"])
    async def add_member_to_group(self, group_name: str, member_name: str, vdom: str = "root") -> dict:
        resp = await self._get(f"/cmdb/firewall/addrgrp/{group_name}/?vdom={vdom}")
        group = self._extract_results(resp)[0]
        
        members = group.get("member", [])
        members.append({"name": member_name})
        
        update_resp = await self._put(f"/cmdb/firewall/addrgrp/{group_name}/?vdom={vdom}", json={"member": members})
        return self._extract_results(update_resp)

    # ─── Service Objects ─────────────────────────────────────────────────────

    @register_action("get_services", "Get service objects", "objects", ["service"])
    async def get_services(self, vdom: str = "root") -> list:
        resp = await self._get(f"/cmdb/firewall.service/custom/?vdom={vdom}")
        return self._extract_results(resp)

    @register_action("get_service_groups", "Get service groups", "objects", ["service", "group"])
    async def get_service_groups(self, vdom: str = "root") -> list:
        resp = await self._get(f"/cmdb/firewall.service/group/?vdom={vdom}")
        return self._extract_results(resp)

    # ─── VPN ─────────────────────────────────────────────────────────────────

    @register_action("get_vpn_ipsec_tunnels", "Get IPsec VPN tunnels", "vpn", ["ipsec"])
    async def get_vpn_ipsec_tunnels(self, vdom: str = "root") -> list:
        resp = await self._get(f"/cmdb/vpn.ipsec/phase1-interface/?vdom={vdom}")
        return self._extract_results(resp)

    @register_action("get_vpn_ssl_sessions", "Get SSL VPN sessions", "vpn", ["ssl", "sessions"])
    async def get_vpn_ssl_sessions(self) -> dict:
        resp = await self._get("/monitor/vpn/ssl?vdom=root")
        return self._extract_results(resp)

    @register_action("get_vpn_status", "Get IPsec VPN status", "vpn", ["status"])
    async def get_vpn_status(self) -> dict:
        resp = await self._get("/monitor/vpn/ipsec?vdom=root")
        return self._extract_results(resp)

    # ─── System & Monitoring ─────────────────────────────────────────────────

    @register_action("get_system_status", "Get system status", "system", ["status"])
    async def get_system_status(self) -> dict:
        resp = await self._get("/monitor/system/status")
        return self._extract_results(resp)

    @register_action("get_active_sessions", "Get active firewall sessions", "monitoring", ["sessions"])
    async def get_active_sessions(self, vdom: str = "root", count: int = 100) -> list:
        resp = await self._get(f"/monitor/firewall/session?count={count}&vdom={vdom}")
        return self._extract_results(resp)

    @register_action("get_threat_log", "Get threat logs", "monitoring", ["threat", "logs"])
    async def get_threat_log(self, rows: int = 100) -> list:
        resp = await self._get(f"/monitor/log/fortiview/threat?rows={rows}&vdom=root")
        return self._extract_results(resp)

    @register_action("get_interface_stats", "Get interface statistics", "monitoring", ["interface"])
    async def get_interface_stats(self) -> dict:
        resp = await self._get("/monitor/system/interface?include_vlan=true")
        return self._extract_results(resp)

    @register_action("backup_config", "Backup FortiGate configuration", "system", ["backup"])
    async def backup_config(self, destination: str = "file", vdom: str = "") -> dict:
        vdom_param = f"&vdom={vdom}" if vdom else ""
        http = await self._get_http_client()
        # Backup endpoint usually returns raw config text, not json
        resp = await http.request("GET", self._append_token(f"/monitor/system/config/backup?destination={destination}{vdom_param}"), raw_response=True)
        return {"config": resp.text}

    @register_action("run_diagnose_command", "Run CLI diagnose command", "system", ["cli", "diagnose"])
    async def run_diagnose_command(self, command: str) -> dict:
        resp = await self._post("/monitor/util/cli-exec", json={"data": command})
        return self._extract_results(resp)

    @register_action("get_ips_statistics", "Get IPS anomaly statistics", "monitoring", ["ips"])
    async def get_ips_statistics(self) -> dict:
        resp = await self._get("/monitor/ips/anomaly")
        return self._extract_results(resp)

    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> WebhookEvent | None:
        """Parse FortiGate Syslog/Webhook events."""
        level = payload.get("level", "information")
        
        severity_map = {
            "emergency": "critical",
            "alert": "critical",
            "critical": "critical",
            "error": "high",
            "warning": "medium",
            "notice": "low",
            "information": "low",
            "debug": "low"
        }
        severity = severity_map.get(level.lower(), "low")
        
        return WebhookEvent(
            connector=self.NAME,
            event_type=WebhookEventType.ALERT if severity in ["critical", "high"] else WebhookEventType.GENERIC,
            raw_payload=payload,
            normalized={
                "msg": payload.get("msg"),
                "srcip": payload.get("srcip"),
                "dstip": payload.get("dstip"),
                "action": payload.get("action")
            },
            severity=severity,
            source_ip=payload.get("srcip")
        )
