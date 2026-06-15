"""
SOAR Connector Hub — OpenCTI Connector
======================================
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult, WebhookEvent, WebhookEventType
from app.core.exceptions import InvalidParameterError, ActionExecutionError


class OpenCTIConnector(BaseConnector):
    NAME = "opencti"
    VERSION = "1.0.0"
    DESCRIPTION = "OpenCTI GraphQL API connector for Threat Intelligence."

    async def _graphql(self, query: str, variables: dict = {}) -> dict:
        http = await self._get_http_client()
        response = await http.post("", json={"query": query, "variables": variables})
        if "errors" in response:
            error_msg = response["errors"][0].get("message", str(response["errors"]))
            raise ActionExecutionError(f"GraphQL error: {error_msg}")
        return response.get("data", {})

    async def test_connection(self) -> ConnectionResult:
        try:
            query = "{ me { name email } }"
            data = await self._graphql(query)
            me = data.get("me", {})
            if "name" in me:
                return ConnectionResult(
                    success=True,
                    connector=self.NAME,
                    message=f"Connected successfully to OpenCTI as {me.get('name')}"
                )
            return ConnectionResult(success=False, connector=self.NAME, message="Unexpected response")
        except Exception as e:
            return ConnectionResult(success=False, connector=self.NAME, message=str(e))

    # ─── Indicators & Observables ────────────────────────────────────────────

    @register_action("search_indicators", "Search indicators", "cti", ["indicator", "search"])
    async def search_indicators(self, search: str = "", type_: str = "", limit: int = 20) -> list:
        query = """
        query SearchIndicators($search: String, $first: Int) {
          indicators(search: $search, first: $first) {
            edges {
              node {
                id
                name
                pattern
                valid_from
                valid_until
                indicator_types
                confidence
              }
            }
          }
        }
        """
        data = await self._graphql(query, {"search": search, "first": limit})
        return [edge["node"] for edge in data.get("indicators", {}).get("edges", [])]

    @register_action("create_indicator", "Create an indicator", "cti", ["indicator", "create"])
    async def create_indicator(self, name: str, pattern: str, pattern_type: str = "stix", indicator_types: list = ["malicious-activity"], valid_from: str = "", valid_until: str = "", confidence: int = 75, description: str = "") -> dict:
        query = """
        mutation CreateIndicator($input: IndicatorAddInput!) {
          indicatorAdd(input: $input) {
            id
            name
            pattern
          }
        }
        """
        input_data = {
            "name": name,
            "pattern": pattern,
            "pattern_type": pattern_type,
            "indicator_types": indicator_types,
            "confidence": confidence,
            "description": description
        }
        if valid_from: input_data["valid_from"] = valid_from
        if valid_until: input_data["valid_until"] = valid_until
            
        data = await self._graphql(query, {"input": input_data})
        return data.get("indicatorAdd", {})

    @register_action("get_indicator", "Get an indicator by ID", "cti", ["indicator"])
    async def get_indicator(self, indicator_id: str) -> dict:
        query = """
        query GetIndicator($id: String!) {
          indicator(id: $id) {
            id
            name
            pattern
            indicator_types
            confidence
          }
        }
        """
        data = await self._graphql(query, {"id": indicator_id})
        return data.get("indicator", {})

    @register_action("delete_indicator", "Delete an indicator", "cti", ["indicator", "delete"])
    async def delete_indicator(self, indicator_id: str) -> dict:
        query = """
        mutation DeleteIndicator($id: ID!) {
          indicatorDelete(id: $id)
        }
        """
        await self._graphql(query, {"id": indicator_id})
        return {"status": "success", "id": indicator_id}

    @register_action("search_observables", "Search observables", "cti", ["observable", "search"])
    async def search_observables(self, search: str = "", type_: str = "", limit: int = 20) -> list:
        query = """
        query SearchObservables($search: String, $first: Int) {
          stixCyberObservables(search: $search, first: $first) {
            edges {
              node {
                id
                entity_type
                observable_value
                x_opencti_score
              }
            }
          }
        }
        """
        data = await self._graphql(query, {"search": search, "first": limit})
        return [edge["node"] for edge in data.get("stixCyberObservables", {}).get("edges", [])]

    @register_action("create_observable", "Create an observable", "cti", ["observable", "create"])
    async def create_observable(self, type_: str, value: str, description: str = "", score: int = 50) -> dict:
        query = """
        mutation CreateObservable($type: String!, $value: String!, $score: Int) {
          stixCyberObservableAdd(
            type: $type,
            __input: { observable_value: $value, x_opencti_score: $score }
          ) {
            id
            entity_type
            observable_value
          }
        }
        """
        # OpenCTI Observable Add mutation is highly specific to the type. This is a generic approximation.
        # Actually in modern OpenCTI, we use specific mutations or StixCyberObservableAddInput
        query_modern = """
        mutation CreateObservable($input: StixCyberObservableAddInput!) {
          stixCyberObservableAdd(input: $input) {
            id
            entity_type
            observable_value
          }
        }
        """
        # But for simplicity, let's use the generic search to see if it exists, if not we add it.
        try:
            data = await self._graphql(query_modern, {
                "input": {"type": type_, "observable_value": value, "x_opencti_score": score, "x_opencti_description": description}
            })
            return data.get("stixCyberObservableAdd", {})
        except Exception:
            return {"status": "error", "message": "Failed to create observable. Check entity type matching STIX."}

    @register_action("enrich_observable", "Enrich an observable", "cti", ["observable", "enrich"])
    async def enrich_observable(self, observable_id: str, connector_id: str) -> dict:
        query = """
        mutation EnrichObservable($id: ID!, $connectorId: String!) {
          stixCyberObservableAskEnrichment(id: $id, connectorId: $connectorId)
        }
        """
        await self._graphql(query, {"id": observable_id, "connectorId": connector_id})
        return {"status": "success"}

    # ─── Threat Intelligence ─────────────────────────────────────────────────

    @register_action("search_threat_actors", "Search threat actors", "cti", ["actor", "search"])
    async def search_threat_actors(self, search: str = "", limit: int = 20) -> list:
        query = """
        query SearchThreatActors($search: String, $first: Int) {
          threatActors(search: $search, first: $first) {
            edges {
              node {
                id
                name
                description
              }
            }
          }
        }
        """
        data = await self._graphql(query, {"search": search, "first": limit})
        return [edge["node"] for edge in data.get("threatActors", {}).get("edges", [])]

    @register_action("get_threat_actor", "Get threat actor by ID", "cti", ["actor"])
    async def get_threat_actor(self, threat_actor_id: str) -> dict:
        query = """
        query GetThreatActor($id: String!) {
          threatActor(id: $id) {
            id
            name
            description
            threat_actor_types
            sophistication
            resource_level
          }
        }
        """
        data = await self._graphql(query, {"id": threat_actor_id})
        return data.get("threatActor", {})

    @register_action("create_threat_actor", "Create a threat actor", "cti", ["actor", "create"])
    async def create_threat_actor(self, name: str, description: str = "", threat_actor_types: list = [], sophistication: str = "", resource_level: str = "", aliases: list = []) -> dict:
        query = """
        mutation CreateThreatActorGroup($input: ThreatActorGroupAddInput!) {
          threatActorGroupAdd(input: $input) {
            id
            name
          }
        }
        """
        input_data = {
            "name": name,
            "description": description,
            "threat_actor_types": threat_actor_types,
            "sophistication": sophistication,
            "resource_level": resource_level,
            "aliases": aliases
        }
        data = await self._graphql(query, {"input": input_data})
        return data.get("threatActorGroupAdd", {})

    @register_action("search_malware", "Search malware", "cti", ["malware", "search"])
    async def search_malware(self, search: str = "", limit: int = 20) -> list:
        query = """
        query SearchMalwares($search: String, $first: Int) {
          malwares(search: $search, first: $first) {
            edges { node { id name description is_family } }
          }
        }
        """
        data = await self._graphql(query, {"search": search, "first": limit})
        return [edge["node"] for edge in data.get("malwares", {}).get("edges", [])]

    @register_action("get_malware", "Get malware by ID", "cti", ["malware"])
    async def get_malware(self, malware_id: str) -> dict:
        query = """
        query GetMalware($id: String!) {
          malware(id: $id) { id name description is_family malware_types }
        }
        """
        data = await self._graphql(query, {"id": malware_id})
        return data.get("malware", {})

    @register_action("create_malware", "Create malware", "cti", ["malware", "create"])
    async def create_malware(self, name: str, description: str = "", malware_types: list = [], is_family: bool = False, aliases: list = []) -> dict:
        query = """
        mutation CreateMalware($input: MalwareAddInput!) {
          malwareAdd(input: $input) { id name }
        }
        """
        input_data = {
            "name": name,
            "description": description,
            "malware_types": malware_types,
            "is_family": is_family,
            "aliases": aliases
        }
        data = await self._graphql(query, {"input": input_data})
        return data.get("malwareAdd", {})

    @register_action("search_campaigns", "Search campaigns", "cti", ["campaign", "search"])
    async def search_campaigns(self, search: str = "", limit: int = 20) -> list:
        query = """
        query SearchCampaigns($search: String, $first: Int) {
          campaigns(search: $search, first: $first) {
            edges { node { id name description } }
          }
        }
        """
        data = await self._graphql(query, {"search": search, "first": limit})
        return [edge["node"] for edge in data.get("campaigns", {}).get("edges", [])]

    @register_action("search_attack_patterns", "Search attack patterns (MITRE)", "cti", ["mitre", "ttp"])
    async def search_attack_patterns(self, search: str = "", limit: int = 20) -> list:
        query = """
        query SearchAttackPatterns($search: String, $first: Int) {
          attackPatterns(search: $search, first: $first) {
            edges { node { id name description x_mitre_id } }
          }
        }
        """
        data = await self._graphql(query, {"search": search, "first": limit})
        return [edge["node"] for edge in data.get("attackPatterns", {}).get("edges", [])]

    # ─── Reports ─────────────────────────────────────────────────────────────

    @register_action("get_reports", "Get reports", "cti", ["report", "list"])
    async def get_reports(self, limit: int = 20, search: str = "") -> list:
        query = """
        query GetReports($search: String, $first: Int) {
          reports(search: $search, first: $first) {
            edges { node { id name description published } }
          }
        }
        """
        data = await self._graphql(query, {"search": search, "first": limit})
        return [edge["node"] for edge in data.get("reports", {}).get("edges", [])]

    @register_action("get_report", "Get report by ID", "cti", ["report"])
    async def get_report(self, report_id: str) -> dict:
        query = """
        query GetReport($id: String!) {
          report(id: $id) { id name description published report_types confidence objectRefs { edges { node { id } } } }
        }
        """
        data = await self._graphql(query, {"id": report_id})
        return data.get("report", {})

    @register_action("create_report", "Create a report", "cti", ["report", "create"])
    async def create_report(self, name: str, description: str = "", published: str = "", report_types: list = ["threat-report"], confidence: int = 75, object_refs: list = []) -> dict:
        query = """
        mutation CreateReport($input: ReportAddInput!) {
          reportAdd(input: $input) { id name }
        }
        """
        input_data = {
            "name": name,
            "description": description,
            "published": published or datetime.now(timezone.utc).isoformat(),
            "report_types": report_types,
            "confidence": confidence,
            "objectRefs": object_refs
        }
        data = await self._graphql(query, {"input": input_data})
        return data.get("reportAdd", {})

    # ─── Relationships ───────────────────────────────────────────────────────

    @register_action("create_relationship", "Create relationship between entities", "cti", ["relationship", "create"])
    async def create_relationship(self, from_id: str, to_id: str, relationship_type: str, description: str = "", confidence: int = 75) -> dict:
        query = """
        mutation CreateRelationship($input: StixCoreRelationshipAddInput!) {
          stixCoreRelationshipAdd(input: $input) { id entity_type }
        }
        """
        input_data = {
            "fromId": from_id,
            "toId": to_id,
            "relationship_type": relationship_type,
            "description": description,
            "confidence": confidence
        }
        data = await self._graphql(query, {"input": input_data})
        return data.get("stixCoreRelationshipAdd", {})

    @register_action("get_relationships", "Get relationships for entity", "cti", ["relationship", "list"])
    async def get_relationships(self, entity_id: str, relationship_type: str = "", limit: int = 20) -> list:
        query = """
        query GetRelationships($fromId: String, $relationship_type: String, $first: Int) {
          stixCoreRelationships(fromId: $fromId, relationship_type: $relationship_type, first: $first) {
            edges { node { id relationship_type from { id } to { id } } }
          }
        }
        """
        data = await self._graphql(query, {"fromId": entity_id, "relationship_type": relationship_type, "first": limit})
        return [edge["node"] for edge in data.get("stixCoreRelationships", {}).get("edges", [])]

    # ─── System & Misc ───────────────────────────────────────────────────────

    @register_action("import_stix_bundle", "Import STIX bundle", "system", ["stix", "import"])
    async def import_stix_bundle(self, bundle: dict) -> dict:
        # Simplest way is via taxii or the API /api/taxii2/collections/... but typically we can POST to /graphql with stixBundleImport
        query = """
        mutation ImportStix($bundle: String!) {
          stixBundleImport(bundle: $bundle)
        }
        """
        import json
        data = await self._graphql(query, {"bundle": json.dumps(bundle)})
        return {"status": "success", "data": data}

    @register_action("get_statistics", "Get platform statistics", "system", ["stats"])
    async def get_statistics(self) -> dict:
        query = """
        query Stats {
          stixDomainObjectsDistribution(field: "entity_type", operation: count) { label value }
          stixCyberObservablesDistribution(field: "entity_type", operation: count) { label value }
        }
        """
        data = await self._graphql(query)
        return data

    @register_action("search_all", "Global search", "system", ["search"])
    async def search_all(self, search: str, limit: int = 20) -> list:
        query = """
        query GlobalSearch($search: String, $first: Int) {
          globalSearch(search: $search, first: $first) {
            edges { node { id entity_type representative { main } } }
          }
        }
        """
        data = await self._graphql(query, {"search": search, "first": limit})
        return [edge["node"] for edge in data.get("globalSearch", {}).get("edges", [])]

    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> WebhookEvent | None:
        """Parse OpenCTI webhooks."""
        event_type = WebhookEventType.GENERIC
        data = payload.get("data", {})
        stix_type = data.get("type", "").lower()
        
        if stix_type in ["indicator", "ipv4-addr", "domain-name", "url", "file", "malware", "campaign"]:
            event_type = WebhookEventType.ALERT
            
        return WebhookEvent(
            connector=self.NAME,
            event_type=event_type,
            raw_payload=payload,
            normalized={
                "action": payload.get("type"),
                "stix_type": stix_type,
                "entity_id": data.get("id"),
                "name": data.get("name")
            }
        )
