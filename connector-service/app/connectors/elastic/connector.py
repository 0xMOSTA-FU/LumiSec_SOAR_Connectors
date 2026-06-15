"""
Elastic Stack SOAR Connector
============================
Covers Elasticsearch API v8.x, Kibana Security (SIEM), and Fleet.

Supports two authentication modes:
  - api_key : Authorization: ApiKey <base64(id:key)>
  - basic_auth : standard HTTP Basic Auth (username / password)

Kibana requests use a dedicated HTTP client initialised against `kibana_url`
and always carry the mandatory ``kbn-xsrf: true`` header.
"""

from __future__ import annotations

import base64
import json
from typing import Any, Dict, List, Optional

from app.core.auth import build_auth_handler
from app.core.base_connector import BaseConnector, register_action
from app.core.exceptions import (
    ActionExecutionError,
    ConfigurationError,
    InvalidParameterError,
)
from app.core.http_client import ConnectorHTTPClient
from app.core.models import (
    ActionResult,
    ConnectionResult,
    WebhookEvent,
    WebhookEventType,
)


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _build_api_key_header(api_key_id: str, api_key_secret: str) -> str:
    """Return the encoded value for the ``Authorization: ApiKey`` header.

    Args:
        api_key_id: The Elasticsearch API key ID.
        api_key_secret: The Elasticsearch API key secret value.

    Returns:
        A base64-encoded ``id:key`` credential string suitable for use as the
        value of an ``Authorization: ApiKey`` header.
    """
    raw = f"{api_key_id}:{api_key_secret}"
    encoded = base64.b64encode(raw.encode("utf-8")).decode("utf-8")
    return encoded


def _build_common_headers(config: Dict[str, Any]) -> Dict[str, str]:
    """Construct the authentication headers for Elasticsearch requests.

    Args:
        config: The connector configuration dictionary.

    Returns:
        A dict of HTTP headers to add to every Elasticsearch request.

    Raises:
        ConfigurationError: If required authentication fields are missing or
            the auth_type value is unrecognised.
    """
    auth_type = config.get("auth_type", "api_key").lower()
    headers: Dict[str, str] = {"Content-Type": "application/json"}

    if auth_type == "api_key":
        api_key_id = config.get("api_key_id", "")
        api_key_secret = config.get("api_key_secret", "")
        if not api_key_id or not api_key_secret:
            raise ConfigurationError(
                "auth_type is 'api_key' but 'api_key_id' or 'api_key_secret' "
                "is missing from the connector configuration."
            )
        encoded = _build_api_key_header(api_key_id, api_key_secret)
        headers["Authorization"] = f"ApiKey {encoded}"

    elif auth_type == "basic_auth":
        username = config.get("username", "")
        password = config.get("password", "")
        if not username or not password:
            raise ConfigurationError(
                "auth_type is 'basic_auth' but 'username' or 'password' "
                "is missing from the connector configuration."
            )
        raw = f"{username}:{password}"
        encoded = base64.b64encode(raw.encode("utf-8")).decode("utf-8")
        headers["Authorization"] = f"Basic {encoded}"

    else:
        raise ConfigurationError(
            f"Unsupported auth_type '{auth_type}'. "
            "Expected 'api_key' or 'basic_auth'."
        )

    return headers


def _build_kibana_headers(es_headers: Dict[str, str]) -> Dict[str, str]:
    """Build Kibana request headers by extending the Elasticsearch headers.

    Kibana requires the ``kbn-xsrf`` header on all mutating requests (and it
    is safe to send it on read requests too), so we always include it.

    Args:
        es_headers: The authentication headers already built for Elasticsearch.

    Returns:
        A copy of *es_headers* with the ``kbn-xsrf`` header added.
    """
    kibana_headers = dict(es_headers)
    kibana_headers["kbn-xsrf"] = "true"
    return kibana_headers


# ---------------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------------

class ElasticConnector(BaseConnector):
    """Production SOAR connector for the Elastic Stack.

    Covers:
    * **Elasticsearch** – search, ES|QL, document CRUD, index management,
      bulk indexing, and index statistics.
    * **Kibana Security (SIEM)** – alert retrieval and status management,
      detection rule lifecycle (create / list / enable / disable / delete).
    * **Fleet** – agent inventory, host isolation / unisolation, and live
      Osquery execution.

    Authentication:
        Two modes are supported and selected via the ``auth_type`` config key:

        * ``api_key``   – ``Authorization: ApiKey <base64(id:key)>``
        * ``basic_auth`` – standard HTTP Basic Auth

    Config keys:
        base_url (str):       Elasticsearch base URL (e.g. https://host:9200)
        kibana_url (str):     Kibana base URL (e.g. https://host:5601)
        auth_type (str):      ``api_key`` or ``basic_auth``
        api_key_id (str):     API key ID (required when auth_type=api_key)
        api_key_secret (str): API key secret (required when auth_type=api_key)
        username (str):       Username (required when auth_type=basic_auth)
        password (str):       Password (required when auth_type=basic_auth)
    """

    NAME: str = "elastic"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = (
        "Elastic Stack connector covering Elasticsearch v8.x, "
        "Kibana Security SIEM, and Fleet."
    )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialise the connector and lazily prepare Kibana client state.

        Args:
            config: Connector configuration dictionary provided by the SOAR
                platform at runtime.
        """
        super().__init__(config)

        self._es_url: str = config.get("base_url", "").rstrip("/")
        self._kibana_url: str = config.get("kibana_url", "").rstrip("/")
        self._kibana_http: Optional[ConnectorHTTPClient] = None

        # Build headers once; reused across all requests.
        self._es_headers: Dict[str, str] = _build_common_headers(config)
        self._kibana_headers: Dict[str, str] = _build_kibana_headers(
            self._es_headers
        )

    def _get_kibana_http(self) -> ConnectorHTTPClient:
        """Lazily initialise and return the Kibana HTTP client.

        Returns:
            A ``ConnectorHTTPClient`` pointed at the configured Kibana URL.

        Raises:
            ConfigurationError: If ``kibana_url`` was not provided in config.
        """
        if not self._kibana_url:
            raise ConfigurationError(
                "'kibana_url' is required for Kibana actions but was not "
                "found in the connector configuration."
            )
        if self._kibana_http is None:
            self._kibana_http = ConnectorHTTPClient(
                base_url=self._kibana_url,
                default_headers=self._kibana_headers,
            )
        return self._kibana_http

    # ------------------------------------------------------------------
    # Connection test
    # ------------------------------------------------------------------

    async def test_connection(self) -> ConnectionResult:
        """Verify connectivity by calling the Elasticsearch root endpoint.

        Hits ``GET /`` and validates that the response contains a
        ``cluster_name`` field, which every healthy cluster returns.

        Returns:
            ConnectionResult indicating success or failure with a message.
        """
        try:
            response = await self.http_client.get(
                "/",
                headers=self._es_headers,
            )
            cluster_name: str = response.get("cluster_name", "")
            if not cluster_name:
                return ConnectionResult.fail(
                    "Connected to Elasticsearch but the response did not "
                    "contain a 'cluster_name'. The endpoint may not be a "
                    "valid Elasticsearch cluster."
                )
            version_info: Dict[str, Any] = response.get("version", {})
            es_version: str = version_info.get("number", "unknown")
            return ConnectionResult.ok(
                f"Successfully connected to Elasticsearch cluster "
                f"'{cluster_name}' (version {es_version})."
            )
        except Exception as exc:
            return ConnectionResult.fail(
                f"Failed to connect to Elasticsearch at '{self._es_url}': "
                f"{exc}"
            )

    # ------------------------------------------------------------------
    # Elasticsearch – Search
    # ------------------------------------------------------------------

    @register_action(
        name="search",
        description="Search documents in an Elasticsearch index.",
        category="data",
        tags=["search", "query"]
    )
    async def search(
        self,
        index: str,
        query: Dict[str, Any],
        size: int = 10,
        from_: int = 0,
        sort: Optional[List[Any]] = None,
    ) -> ActionResult:
        """Execute a DSL search against an Elasticsearch index.

        Args:
            index:  Target index name or index pattern (e.g. ``logs-*``).
            query:  Elasticsearch query DSL object (e.g. ``{"match_all": {}}``).
            size:   Maximum number of hits to return.
            from_:  Starting document offset for pagination.
            sort:   Optional list of sort clauses.

        Returns:
            ActionResult containing ``hits`` (list of hit objects) and
            ``total`` (total hit count dict with ``value`` and ``relation``).

        Raises:
            InvalidParameterError: If *index* or *query* are not provided.
        """
        if not index:
            raise InvalidParameterError("'index' is required for search.")
        if query is None:
            raise InvalidParameterError("'query' is required for search.")

        body: Dict[str, Any] = {
            "query": query,
            "size": size,
            "from": from_,
        }
        if sort:
            body["sort"] = sort

        try:
            response = await self.http_client.post(
                f"/{index}/_search",
                json=body,
                headers=self._es_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Elasticsearch search failed on index '{index}': {exc}"
            ) from exc

        hits_wrapper: Dict[str, Any] = response.get("hits", {})
        return ActionResult.ok(
            data={
                "hits": hits_wrapper.get("hits", []),
                "total": hits_wrapper.get("total", {}),
            }
        )

    # ------------------------------------------------------------------
    # Elasticsearch – ES|QL
    # ------------------------------------------------------------------

    @register_action(
        name="run_esql_query",
        description="Execute an ES|QL query via the /_query endpoint.",
        parameters={
            "query": {
                "type": "string",
                "description": "ES|QL query string.",
                "required": True,
            },
            "filter": {
                "type": "object",
                "description": "Optional DSL filter applied alongside the ES|QL query.",
                "required": False,
            },
        },
    )
    async def run_esql_query(
        self,
        query: str,
        filter: Optional[Dict[str, Any]] = None,
    ) -> ActionResult:
        """Execute an ES|QL query via the Elasticsearch ``/_query`` endpoint.

        Args:
            query:  The ES|QL query string (e.g. ``FROM logs-* | LIMIT 10``).
            filter: Optional Elasticsearch DSL filter object to restrict the
                    data the query runs over.

        Returns:
            ActionResult with the full ``/_query`` response payload, including
            ``columns`` and ``values`` keys.

        Raises:
            InvalidParameterError: If *query* is empty.
        """
        if not query:
            raise InvalidParameterError("'query' is required for run_esql_query.")

        body: Dict[str, Any] = {"query": query}
        if filter:
            body["filter"] = filter

        # ES|QL requires a specific Accept header in addition to Content-Type.
        esql_headers = dict(self._es_headers)
        esql_headers["Accept"] = "application/vnd.elasticsearch+json"

        try:
            response = await self.http_client.post(
                "/_query",
                json=body,
                headers=esql_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"ES|QL query execution failed: {exc}"
            ) from exc

        return ActionResult.ok(data=response)

    # ------------------------------------------------------------------
    # Elasticsearch – Document CRUD
    # ------------------------------------------------------------------

    @register_action(
        name="index_document",
        description="Index (create or update) a document in Elasticsearch.",
        parameters={
            "index": {
                "type": "string",
                "description": "Target index name.",
                "required": True,
            },
            "document": {
                "type": "object",
                "description": "Document body to index.",
                "required": True,
            },
            "doc_id": {
                "type": "string",
                "description": (
                    "Optional document ID. If omitted, Elasticsearch "
                    "auto-generates one."
                ),
                "required": False,
            },
        },
    )
    async def index_document(
        self,
        index: str,
        document: Dict[str, Any],
        doc_id: str = "",
    ) -> ActionResult:
        """Index a document into Elasticsearch, optionally with a specific ID.

        If *doc_id* is provided the request uses ``PUT /{index}/_doc/{id}``
        (upsert semantics).  Otherwise ``POST /{index}/_doc`` is used and
        Elasticsearch auto-generates the document ID.

        Args:
            index:    Target index name.
            document: The document body to index.
            doc_id:   Optional explicit document ID.

        Returns:
            ActionResult with ``_id`` and ``result`` fields from the API
            response.

        Raises:
            InvalidParameterError: If *index* or *document* are missing.
        """
        if not index:
            raise InvalidParameterError("'index' is required for index_document.")
        if not document:
            raise InvalidParameterError("'document' must be a non-empty object.")

        try:
            if doc_id:
                response = await self.http_client.put(
                    f"/{index}/_doc/{doc_id}",
                    json=document,
                    headers=self._es_headers,
                )
            else:
                response = await self.http_client.post(
                    f"/{index}/_doc",
                    json=document,
                    headers=self._es_headers,
                )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to index document into '{index}': {exc}"
            ) from exc

        return ActionResult.ok(
            data={
                "_id": response.get("_id"),
                "result": response.get("result"),
                "_index": response.get("_index"),
                "_version": response.get("_version"),
            }
        )

    @register_action(
        name="get_document",
        description="Retrieve a document from Elasticsearch by ID.",
        parameters={
            "index": {
                "type": "string",
                "description": "Index name.",
                "required": True,
            },
            "doc_id": {
                "type": "string",
                "description": "Document ID to retrieve.",
                "required": True,
            },
        },
    )
    async def get_document(
        self,
        index: str,
        doc_id: str,
    ) -> ActionResult:
        """Retrieve a document from Elasticsearch by its ID.

        Args:
            index:  Name of the index containing the document.
            doc_id: The document's unique ID.

        Returns:
            ActionResult with the document ``_source`` and metadata fields
            (``_id``, ``_index``, ``_version``, ``found``).

        Raises:
            InvalidParameterError: If *index* or *doc_id* are missing.
        """
        if not index:
            raise InvalidParameterError("'index' is required for get_document.")
        if not doc_id:
            raise InvalidParameterError("'doc_id' is required for get_document.")

        try:
            response = await self.http_client.get(
                f"/{index}/_doc/{doc_id}",
                headers=self._es_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to retrieve document '{doc_id}' from '{index}': {exc}"
            ) from exc

        return ActionResult.ok(
            data={
                "_id": response.get("_id"),
                "_index": response.get("_index"),
                "_version": response.get("_version"),
                "found": response.get("found"),
                "_source": response.get("_source", {}),
            }
        )

    @register_action(
        name="delete_document",
        description="Delete a document from Elasticsearch by ID.",
        parameters={
            "index": {
                "type": "string",
                "description": "Index name.",
                "required": True,
            },
            "doc_id": {
                "type": "string",
                "description": "Document ID to delete.",
                "required": True,
            },
        },
    )
    async def delete_document(
        self,
        index: str,
        doc_id: str,
    ) -> ActionResult:
        """Delete a document from Elasticsearch by its ID.

        Args:
            index:  Name of the index containing the document.
            doc_id: The document's unique ID to delete.

        Returns:
            ActionResult with the ``result`` field (e.g. ``"deleted"`` or
            ``"not_found"``).

        Raises:
            InvalidParameterError: If *index* or *doc_id* are missing.
        """
        if not index:
            raise InvalidParameterError("'index' is required for delete_document.")
        if not doc_id:
            raise InvalidParameterError("'doc_id' is required for delete_document.")

        try:
            response = await self.http_client.delete(
                f"/{index}/_doc/{doc_id}",
                headers=self._es_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to delete document '{doc_id}' from '{index}': {exc}"
            ) from exc

        return ActionResult.ok(
            data={
                "_id": response.get("_id"),
                "result": response.get("result"),
                "_index": response.get("_index"),
            }
        )

    # ------------------------------------------------------------------
    # Elasticsearch – Index Management
    # ------------------------------------------------------------------

    @register_action(
        name="create_index",
        description="Create a new Elasticsearch index with optional mappings and settings.",
        parameters={
            "index": {
                "type": "string",
                "description": "Name of the index to create.",
                "required": True,
            },
            "mappings": {
                "type": "object",
                "description": "Optional index mappings definition.",
                "required": False,
            },
            "settings": {
                "type": "object",
                "description": "Optional index settings (e.g. number_of_shards).",
                "required": False,
            },
        },
    )
    async def create_index(
        self,
        index: str,
        mappings: Optional[Dict[str, Any]] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> ActionResult:
        """Create a new Elasticsearch index.

        Args:
            index:    Name of the index to create.
            mappings: Optional mapping definition for the index.
            settings: Optional settings (e.g. ``number_of_shards``,
                      ``number_of_replicas``).

        Returns:
            ActionResult with ``acknowledged``, ``shards_acknowledged``,
            and ``index`` fields from the Elasticsearch response.

        Raises:
            InvalidParameterError: If *index* is not provided.
        """
        if not index:
            raise InvalidParameterError("'index' is required for create_index.")

        body: Dict[str, Any] = {}
        if mappings:
            body["mappings"] = mappings
        if settings:
            body["settings"] = settings

        try:
            response = await self.http_client.put(
                f"/{index}",
                json=body,
                headers=self._es_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to create index '{index}': {exc}"
            ) from exc

        return ActionResult.ok(
            data={
                "acknowledged": response.get("acknowledged"),
                "shards_acknowledged": response.get("shards_acknowledged"),
                "index": response.get("index"),
            }
        )

    @register_action(
        name="delete_index",
        description="Delete an Elasticsearch index.",
        parameters={
            "index": {
                "type": "string",
                "description": "Name of the index to delete.",
                "required": True,
            },
        },
    )
    async def delete_index(self, index: str) -> ActionResult:
        """Delete an Elasticsearch index permanently.

        Args:
            index: Name of the index to delete.

        Returns:
            ActionResult with the ``acknowledged`` field from the response.

        Raises:
            InvalidParameterError: If *index* is not provided.
        """
        if not index:
            raise InvalidParameterError("'index' is required for delete_index.")

        try:
            response = await self.http_client.delete(
                f"/{index}",
                headers=self._es_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to delete index '{index}': {exc}"
            ) from exc

        return ActionResult.ok(data={"acknowledged": response.get("acknowledged")})

    @register_action(
        name="get_index_stats",
        description="Retrieve statistics for one or more Elasticsearch indices.",
        parameters={
            "index": {
                "type": "string",
                "description": (
                    "Index name or pattern to retrieve stats for. "
                    "Defaults to '*' (all indices)."
                ),
                "required": False,
            },
        },
    )
    async def get_index_stats(self, index: str = "*") -> ActionResult:
        """Retrieve document and storage statistics for an index or pattern.

        Args:
            index: Index name or wildcard pattern (defaults to ``*``).

        Returns:
            ActionResult with ``indices`` dict keyed by index name, each
            containing ``docs_count`` and ``store_size_in_bytes``.
        """
        target = index if index else "*"

        try:
            response = await self.http_client.get(
                f"/{target}/_stats",
                headers=self._es_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to retrieve stats for index '{target}': {exc}"
            ) from exc

        raw_indices: Dict[str, Any] = response.get("indices", {})
        parsed: Dict[str, Dict[str, Any]] = {}
        for idx_name, idx_data in raw_indices.items():
            primaries: Dict[str, Any] = idx_data.get("primaries", {})
            docs_info: Dict[str, Any] = primaries.get("docs", {})
            store_info: Dict[str, Any] = primaries.get("store", {})
            parsed[idx_name] = {
                "docs_count": docs_info.get("count", 0),
                "store_size_in_bytes": store_info.get("size_in_bytes", 0),
            }

        return ActionResult.ok(data={"indices": parsed})

    # ------------------------------------------------------------------
    # Elasticsearch – Bulk Indexing
    # ------------------------------------------------------------------

    @register_action(
        name="bulk_index",
        description="Bulk-index a list of documents into an Elasticsearch index.",
        parameters={
            "index": {
                "type": "string",
                "description": "Target index name.",
                "required": True,
            },
            "documents": {
                "type": "array",
                "description": "List of document objects to index.",
                "required": True,
            },
        },
    )
    async def bulk_index(
        self,
        index: str,
        documents: List[Dict[str, Any]],
    ) -> ActionResult:
        """Bulk-index a list of documents using the Elasticsearch ``/_bulk`` API.

        Each document in *documents* may optionally carry a ``_id`` key; if
        present it is used as the document ID, otherwise Elasticsearch
        auto-generates one.  The ``_id`` key is stripped from the document
        body before indexing.

        Args:
            index:     Target index name.
            documents: List of document dictionaries to index.

        Returns:
            ActionResult with ``took``, ``errors``, and ``items`` from the
            bulk response.

        Raises:
            InvalidParameterError: If *index* or *documents* are missing /
                empty.
        """
        if not index:
            raise InvalidParameterError("'index' is required for bulk_index.")
        if not documents:
            raise InvalidParameterError(
                "'documents' must be a non-empty list for bulk_index."
            )

        ndjson_lines: List[str] = []
        for doc in documents:
            doc_copy = dict(doc)
            doc_id: Optional[str] = doc_copy.pop("_id", None)

            action_meta: Dict[str, Any] = {"_index": index}
            if doc_id:
                action_meta["_id"] = doc_id

            ndjson_lines.append(json.dumps({"index": action_meta}))
            ndjson_lines.append(json.dumps(doc_copy))

        # Bulk body must end with a newline.
        bulk_body: str = "\n".join(ndjson_lines) + "\n"

        bulk_headers = dict(self._es_headers)
        bulk_headers["Content-Type"] = "application/x-ndjson"

        try:
            response = await self.http_client.post(
                "/_bulk",
                data=bulk_body,
                headers=bulk_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Bulk index operation failed for index '{index}': {exc}"
            ) from exc

        return ActionResult.ok(
            data={
                "took": response.get("took"),
                "errors": response.get("errors", False),
                "items": response.get("items", []),
            }
        )

    # ------------------------------------------------------------------
    # Kibana Security – Alerts
    # ------------------------------------------------------------------

    @register_action(
        name="get_alerts",
        description="Retrieve security alerts from Kibana's alerts index.",
        parameters={
            "index": {
                "type": "string",
                "description": (
                    "Alerts index to query. Defaults to "
                    "'.alerts-security.alerts-default'."
                ),
                "required": False,
            },
            "size": {
                "type": "integer",
                "description": "Number of alerts to return. Defaults to 20.",
                "required": False,
            },
            "status": {
                "type": "string",
                "description": (
                    "Filter by workflow status: 'open', 'acknowledged', "
                    "or 'closed'. Defaults to 'open'."
                ),
                "required": False,
            },
        },
    )
    async def get_alerts(
        self,
        index: str = ".alerts-security.alerts-default",
        size: int = 20,
        status: str = "open",
    ) -> ActionResult:
        """Search the Kibana security alerts index filtered by workflow status.

        Uses the Elasticsearch ``/_search`` API against the Kibana alert index,
        filtering on the ``kibana.alert.workflow_status`` field.

        Args:
            index:  Alerts backing index (defaults to the standard security
                    alerts index).
            size:   Maximum number of alerts to return.
            status: Workflow status to filter on (``open``, ``acknowledged``,
                    or ``closed``).

        Returns:
            ActionResult with ``hits`` (alert documents) and ``total`` count.
        """
        valid_statuses = {"open", "acknowledged", "closed"}
        if status and status not in valid_statuses:
            raise InvalidParameterError(
                f"Invalid status '{status}'. Must be one of: "
                + ", ".join(sorted(valid_statuses))
            )

        query: Dict[str, Any] = {
            "bool": {
                "filter": [
                    {
                        "term": {
                            "kibana.alert.workflow_status": status or "open"
                        }
                    }
                ]
            }
        }

        body: Dict[str, Any] = {
            "query": query,
            "size": size,
            "sort": [{"@timestamp": {"order": "desc"}}],
        }

        try:
            response = await self.http_client.post(
                f"/{index}/_search",
                json=body,
                headers=self._es_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to retrieve alerts from '{index}': {exc}"
            ) from exc

        hits_wrapper: Dict[str, Any] = response.get("hits", {})
        return ActionResult.ok(
            data={
                "hits": hits_wrapper.get("hits", []),
                "total": hits_wrapper.get("total", {}),
            }
        )

    @register_action(
        name="get_alert",
        description="Retrieve a single Kibana alert by its ID.",
        parameters={
            "alert_id": {
                "type": "string",
                "description": "Kibana alert UUID.",
                "required": True,
            },
        },
    )
    async def get_alert(self, alert_id: str) -> ActionResult:
        """Retrieve a single Kibana alert by its UUID.

        Calls ``GET /api/alerts/alert/{id}`` on the Kibana API.

        Args:
            alert_id: The Kibana alert UUID.

        Returns:
            ActionResult containing the full alert object from the Kibana API.

        Raises:
            InvalidParameterError: If *alert_id* is not provided.
        """
        if not alert_id:
            raise InvalidParameterError("'alert_id' is required for get_alert.")

        kibana = self._get_kibana_http()
        try:
            response = await kibana.get(
                f"/api/alerts/alert/{alert_id}",
                headers=self._kibana_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to retrieve Kibana alert '{alert_id}': {exc}"
            ) from exc

        return ActionResult.ok(data=response)

    @register_action(
        name="update_alert_status",
        description="Update the workflow status of one or more Kibana security alerts.",
        parameters={
            "alert_ids": {
                "type": "array",
                "description": "List of alert signal IDs to update.",
                "required": True,
            },
            "status": {
                "type": "string",
                "description": (
                    "New status for the alerts: 'open', 'acknowledged', "
                    "or 'closed'."
                ),
                "required": True,
            },
        },
    )
    async def update_alert_status(
        self,
        alert_ids: List[str],
        status: str,
    ) -> ActionResult:
        """Bulk-update the workflow status of Kibana security alerts.

        Calls ``POST /api/detection_engine/signals/status`` on the Kibana API.

        Args:
            alert_ids: List of signal/alert IDs to update.
            status:    New workflow status (``open``, ``acknowledged``, or
                       ``closed``).

        Returns:
            ActionResult with the API response including ``updated`` count.

        Raises:
            InvalidParameterError: If *alert_ids* is empty or *status* is
                invalid.
        """
        valid_statuses = {"open", "acknowledged", "closed"}
        if not alert_ids:
            raise InvalidParameterError(
                "'alert_ids' must be a non-empty list."
            )
        if status not in valid_statuses:
            raise InvalidParameterError(
                f"Invalid status '{status}'. Must be one of: "
                + ", ".join(sorted(valid_statuses))
            )

        body: Dict[str, Any] = {
            "signal_ids": alert_ids,
            "status": status,
        }

        kibana = self._get_kibana_http()
        try:
            response = await kibana.post(
                "/api/detection_engine/signals/status",
                json=body,
                headers=self._kibana_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to update alert status to '{status}': {exc}"
            ) from exc

        return ActionResult.ok(data=response)

    # ------------------------------------------------------------------
    # Kibana Security – Detection Rules
    # ------------------------------------------------------------------

    @register_action(
        name="create_detection_rule",
        description="Create a new Kibana detection rule.",
        parameters={
            "rule": {
                "type": "object",
                "description": (
                    "Detection rule definition following the Kibana detection "
                    "rule schema (e.g. name, type, query, index, severity)."
                ),
                "required": True,
            },
        },
    )
    async def create_detection_rule(
        self,
        rule: Dict[str, Any],
    ) -> ActionResult:
        """Create a new Kibana detection (SIEM) rule.

        Calls ``POST /api/detection_engine/rules`` on the Kibana API.

        Args:
            rule: Detection rule body following the Kibana rule schema.  At a
                  minimum this should include ``name``, ``type``, ``query``,
                  ``index``, ``severity``, and ``risk_score``.

        Returns:
            ActionResult with the created rule object including its auto-
            assigned ``id``.

        Raises:
            InvalidParameterError: If *rule* is empty.
        """
        if not rule:
            raise InvalidParameterError(
                "'rule' must be a non-empty object for create_detection_rule."
            )

        kibana = self._get_kibana_http()
        try:
            response = await kibana.post(
                "/api/detection_engine/rules",
                json=rule,
                headers=self._kibana_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to create detection rule: {exc}"
            ) from exc

        return ActionResult.ok(data=response)

    @register_action(
        name="get_detection_rules",
        description="List Kibana detection rules with pagination and optional filter.",
        parameters={
            "page": {
                "type": "integer",
                "description": "Page number (1-indexed). Defaults to 1.",
                "required": False,
            },
            "per_page": {
                "type": "integer",
                "description": "Number of rules per page. Defaults to 20.",
                "required": False,
            },
            "filter": {
                "type": "string",
                "description": "Optional KQL filter string to narrow results.",
                "required": False,
            },
        },
    )
    async def get_detection_rules(
        self,
        page: int = 1,
        per_page: int = 20,
        filter: str = "",
    ) -> ActionResult:
        """List Kibana detection rules with pagination and optional KQL filter.

        Calls ``GET /api/detection_engine/rules/_find`` on the Kibana API.

        Args:
            page:     1-indexed page number.
            per_page: Number of rules per page.
            filter:   Optional KQL filter string (e.g.
                      ``alert.attributes.name: "My Rule"``).

        Returns:
            ActionResult with ``data`` (list of rule objects), ``page``,
            ``perPage``, and ``total`` from the Kibana response.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }
        if filter:
            params["filter"] = filter

        kibana = self._get_kibana_http()
        try:
            response = await kibana.get(
                "/api/detection_engine/rules/_find",
                params=params,
                headers=self._kibana_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to list detection rules: {exc}"
            ) from exc

        return ActionResult.ok(data=response)

    @register_action(
        name="enable_detection_rule",
        description="Enable a Kibana detection rule by its rule ID.",
        parameters={
            "rule_id": {
                "type": "string",
                "description": "UUID of the detection rule to enable.",
                "required": True,
            },
        },
    )
    async def enable_detection_rule(self, rule_id: str) -> ActionResult:
        """Enable a Kibana detection rule using the bulk action endpoint.

        Calls ``POST /api/detection_engine/rules/_bulk_action`` with action
        ``enable`` on the Kibana API.

        Args:
            rule_id: UUID of the detection rule to enable.

        Returns:
            ActionResult with the bulk action response.

        Raises:
            InvalidParameterError: If *rule_id* is not provided.
        """
        if not rule_id:
            raise InvalidParameterError(
                "'rule_id' is required for enable_detection_rule."
            )

        body: Dict[str, Any] = {
            "action": "enable",
            "ids": [rule_id],
        }

        kibana = self._get_kibana_http()
        try:
            response = await kibana.post(
                "/api/detection_engine/rules/_bulk_action",
                json=body,
                headers=self._kibana_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to enable detection rule '{rule_id}': {exc}"
            ) from exc

        return ActionResult.ok(data=response)

    @register_action(
        name="disable_detection_rule",
        description="Disable a Kibana detection rule by its rule ID.",
        parameters={
            "rule_id": {
                "type": "string",
                "description": "UUID of the detection rule to disable.",
                "required": True,
            },
        },
    )
    async def disable_detection_rule(self, rule_id: str) -> ActionResult:
        """Disable a Kibana detection rule using the bulk action endpoint.

        Calls ``POST /api/detection_engine/rules/_bulk_action`` with action
        ``disable`` on the Kibana API.

        Args:
            rule_id: UUID of the detection rule to disable.

        Returns:
            ActionResult with the bulk action response.

        Raises:
            InvalidParameterError: If *rule_id* is not provided.
        """
        if not rule_id:
            raise InvalidParameterError(
                "'rule_id' is required for disable_detection_rule."
            )

        body: Dict[str, Any] = {
            "action": "disable",
            "ids": [rule_id],
        }

        kibana = self._get_kibana_http()
        try:
            response = await kibana.post(
                "/api/detection_engine/rules/_bulk_action",
                json=body,
                headers=self._kibana_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to disable detection rule '{rule_id}': {exc}"
            ) from exc

        return ActionResult.ok(data=response)

    @register_action(
        name="delete_detection_rule",
        description="Permanently delete a Kibana detection rule by its rule ID.",
        parameters={
            "rule_id": {
                "type": "string",
                "description": "UUID of the detection rule to delete.",
                "required": True,
            },
        },
    )
    async def delete_detection_rule(self, rule_id: str) -> ActionResult:
        """Permanently delete a Kibana detection rule.

        Calls ``DELETE /api/detection_engine/rules?id={rule_id}`` on the
        Kibana API.

        Args:
            rule_id: UUID of the detection rule to delete.

        Returns:
            ActionResult with the deleted rule object returned by Kibana.

        Raises:
            InvalidParameterError: If *rule_id* is not provided.
        """
        if not rule_id:
            raise InvalidParameterError(
                "'rule_id' is required for delete_detection_rule."
            )

        kibana = self._get_kibana_http()
        try:
            response = await kibana.delete(
                "/api/detection_engine/rules",
                params={"id": rule_id},
                headers=self._kibana_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to delete detection rule '{rule_id}': {exc}"
            ) from exc

        return ActionResult.ok(data=response)

    # ------------------------------------------------------------------
    # Fleet – Agent Management
    # ------------------------------------------------------------------

    @register_action(
        name="get_agents",
        description="List Elastic Fleet agents with optional status filtering.",
        parameters={
            "page": {
                "type": "integer",
                "description": "Page number (1-indexed). Defaults to 1.",
                "required": False,
            },
            "per_page": {
                "type": "integer",
                "description": "Agents per page. Defaults to 20.",
                "required": False,
            },
            "status": {
                "type": "string",
                "description": (
                    "Filter by agent status: 'online', 'offline', "
                    "'enrolling', 'unenrolling', 'inactive', 'error', "
                    "'degraded'. Leave empty for all."
                ),
                "required": False,
            },
        },
    )
    async def get_agents(
        self,
        page: int = 1,
        per_page: int = 20,
        status: str = "",
    ) -> ActionResult:
        """List Fleet agents with pagination and optional status filter.

        Calls ``GET /api/fleet/agents`` on the Kibana API.

        Args:
            page:     1-indexed page number.
            per_page: Number of agents per page.
            status:   Optional agent status filter.

        Returns:
            ActionResult with ``items`` (list of agent objects), ``page``,
            ``perPage``, and ``total`` from the Fleet API response.
        """
        params: Dict[str, Any] = {
            "page": page,
            "perPage": per_page,
        }
        if status:
            params["status"] = status

        kibana = self._get_kibana_http()
        try:
            response = await kibana.get(
                "/api/fleet/agents",
                params=params,
                headers=self._kibana_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to list Fleet agents: {exc}"
            ) from exc

        return ActionResult.ok(data=response)

    @register_action(
        name="get_agent_info",
        description="Retrieve detailed information about a specific Fleet agent.",
        parameters={
            "agent_id": {
                "type": "string",
                "description": "Fleet agent ID.",
                "required": True,
            },
        },
    )
    async def get_agent_info(self, agent_id: str) -> ActionResult:
        """Retrieve detailed information about a Fleet agent.

        Calls ``GET /api/fleet/agents/{id}`` on the Kibana API.

        Args:
            agent_id: The Fleet agent ID.

        Returns:
            ActionResult with the full agent object from the Fleet API.

        Raises:
            InvalidParameterError: If *agent_id* is not provided.
        """
        if not agent_id:
            raise InvalidParameterError(
                "'agent_id' is required for get_agent_info."
            )

        kibana = self._get_kibana_http()
        try:
            response = await kibana.get(
                f"/api/fleet/agents/{agent_id}",
                headers=self._kibana_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to retrieve Fleet agent '{agent_id}': {exc}"
            ) from exc

        return ActionResult.ok(data=response)

    # ------------------------------------------------------------------
    # Fleet – Host Isolation
    # ------------------------------------------------------------------

    @register_action(
        name="isolate_host",
        description="Network-isolate an endpoint via the Fleet agent actions API.",
        parameters={
            "agent_id": {
                "type": "string",
                "description": "Fleet agent ID of the host to isolate.",
                "required": True,
            },
            "comment": {
                "type": "string",
                "description": (
                    "Reason or note for the isolation action. "
                    "Defaults to 'Isolated by SOAR'."
                ),
                "required": False,
            },
        },
    )
    async def isolate_host(
        self,
        agent_id: str,
        comment: str = "Isolated by SOAR",
    ) -> ActionResult:
        """Network-isolate a host via the Fleet agent actions API.

        Calls ``POST /api/fleet/agents/{id}/actions`` with action type
        ``ISOLATE`` on the Kibana API.

        Args:
            agent_id: The Fleet agent ID of the target host.
            comment:  Human-readable reason recorded with the action.

        Returns:
            ActionResult with the Fleet action object including the action
            ``id`` and ``creation_time``.

        Raises:
            InvalidParameterError: If *agent_id* is not provided.
        """
        if not agent_id:
            raise InvalidParameterError(
                "'agent_id' is required for isolate_host."
            )

        body: Dict[str, Any] = {
            "action": {
                "type": "ISOLATE",
                "data": {"comment": comment},
            }
        }

        kibana = self._get_kibana_http()
        try:
            response = await kibana.post(
                f"/api/fleet/agents/{agent_id}/actions",
                json=body,
                headers=self._kibana_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to isolate host via agent '{agent_id}': {exc}"
            ) from exc

        return ActionResult.ok(data=response)

    @register_action(
        name="unisolate_host",
        description="Release a previously isolated endpoint via the Fleet agent actions API.",
        parameters={
            "agent_id": {
                "type": "string",
                "description": "Fleet agent ID of the host to unisolate.",
                "required": True,
            },
            "comment": {
                "type": "string",
                "description": "Optional reason or note for releasing isolation.",
                "required": False,
            },
        },
    )
    async def unisolate_host(
        self,
        agent_id: str,
        comment: str = "",
    ) -> ActionResult:
        """Release a previously isolated host via the Fleet agent actions API.

        Calls ``POST /api/fleet/agents/{id}/actions`` with action type
        ``UNISOLATE`` on the Kibana API.

        Args:
            agent_id: The Fleet agent ID of the target host.
            comment:  Optional human-readable reason recorded with the action.

        Returns:
            ActionResult with the Fleet action object.

        Raises:
            InvalidParameterError: If *agent_id* is not provided.
        """
        if not agent_id:
            raise InvalidParameterError(
                "'agent_id' is required for unisolate_host."
            )

        action_payload: Dict[str, Any] = {"type": "UNISOLATE"}
        if comment:
            action_payload["data"] = {"comment": comment}

        body: Dict[str, Any] = {"action": action_payload}

        kibana = self._get_kibana_http()
        try:
            response = await kibana.post(
                f"/api/fleet/agents/{agent_id}/actions",
                json=body,
                headers=self._kibana_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to unisolate host via agent '{agent_id}': {exc}"
            ) from exc

        return ActionResult.ok(data=response)

    # ------------------------------------------------------------------
    # Fleet – Osquery
    # ------------------------------------------------------------------

    @register_action(
        name="run_osquery",
        description="Execute a live Osquery SQL query against a Fleet agent.",
        parameters={
            "agent_id": {
                "type": "string",
                "description": "Fleet agent ID to run the Osquery against.",
                "required": True,
            },
            "query": {
                "type": "string",
                "description": "Osquery SQL query string to execute.",
                "required": True,
            },
        },
    )
    async def run_osquery(
        self,
        agent_id: str,
        query: str,
    ) -> ActionResult:
        """Execute a live Osquery SQL query against a Fleet-managed agent.

        Calls ``POST /api/osquery/live_queries`` on the Kibana API.

        Args:
            agent_id: The Fleet agent ID to target with the query.
            query:    The Osquery SQL query string (e.g.
                      ``SELECT * FROM processes LIMIT 10``).

        Returns:
            ActionResult with the live query response, including the
            ``action_id`` that can be polled for results.

        Raises:
            InvalidParameterError: If *agent_id* or *query* are not provided.
        """
        if not agent_id:
            raise InvalidParameterError(
                "'agent_id' is required for run_osquery."
            )
        if not query:
            raise InvalidParameterError(
                "'query' is required for run_osquery."
            )

        body: Dict[str, Any] = {
            "query": query,
            "agent_ids": [agent_id],
        }

        kibana = self._get_kibana_http()
        try:
            response = await kibana.post(
                "/api/osquery/live_queries",
                json=body,
                headers=self._kibana_headers,
            )
        except Exception as exc:
            raise ActionExecutionError(
                f"Failed to run Osquery on agent '{agent_id}': {exc}"
            ) from exc

        return ActionResult.ok(data=response)

    # ------------------------------------------------------------------
    # Webhook – Elastic Watcher
    # ------------------------------------------------------------------

    async def parse_webhook(
        self,
        headers: Dict[str, str],
        body: bytes,
    ) -> WebhookEvent:
        """Parse an inbound Elastic Watcher webhook payload.

        Elastic Watcher can be configured to send HTTP POST requests when an
        alert condition is met.  The body is a JSON object whose structure
        depends on the watcher ``webhook`` action template, but this
        implementation follows the common convention where the payload
        contains at least:

        * ``trigger.triggered_time`` (ISO-8601 timestamp)
        * ``trigger.scheduled_time`` (ISO-8601 scheduled evaluation time)
        * ``metadata`` (arbitrary watcher metadata dict)
        * ``payload`` (the watch's execution context / hits)

        Args:
            headers: HTTP request headers from the incoming webhook.
            body:    Raw request body bytes.

        Returns:
            A ``WebhookEvent`` with ``event_type`` set to
            ``WebhookEventType.ALERT`` and the parsed watcher payload in
            ``data``.

        Raises:
            WebhookValidationError: If the body cannot be decoded as JSON or
                does not contain the expected ``trigger`` key.
        """
        try:
            payload: Dict[str, Any] = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            from app.core.exceptions import WebhookValidationError
            raise WebhookValidationError(
                f"Elastic Watcher webhook body is not valid JSON: {exc}"
            ) from exc

        trigger: Dict[str, Any] = payload.get("trigger", {})
        triggered_time: str = trigger.get("triggered_time", "")
        scheduled_time: str = trigger.get("scheduled_time", "")

        watcher_metadata: Dict[str, Any] = payload.get("metadata", {})
        watcher_payload: Any = payload.get("payload", {})

        return WebhookEvent(
            event_type=WebhookEventType.ALERT,
            source=self.NAME,
            data={
                "triggered_time": triggered_time,
                "scheduled_time": scheduled_time,
                "metadata": watcher_metadata,
                "payload": watcher_payload,
                "raw": payload,
            },
        )

    # ------------------------------------------------------------------
    # Kibana Cases API
    # ------------------------------------------------------------------

    @register_action(
        name="create_case",
        description="Create a new case in Kibana.",
        category="cases",
        tags=["cases", "create"]
    )
    async def create_case(
        self,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
    ) -> ActionResult:
        if not title:
            raise InvalidParameterError("'title' is required.")
        body = {
            "title": title,
            "description": description,
            "tags": tags or []
        }
        kibana = self._get_kibana_http()
        try:
            response = await kibana.post(
                "/api/cases",
                json=body
            )
        except Exception as exc:
            raise ActionExecutionError(f"Failed to create case: {exc}") from exc
        return ActionResult.ok(data=response)

    @register_action(
        name="get_cases",
        description="Get a list of Kibana cases.",
        category="cases",
        tags=["cases", "list"]
    )
    async def get_cases(self, page: int = 1, per_page: int = 20) -> ActionResult:
        kibana = self._get_kibana_http()
        try:
            response = await kibana.get(
                "/api/cases",
                params={"page": page, "perPage": per_page}
            )
        except Exception as exc:
            raise ActionExecutionError(f"Failed to retrieve cases: {exc}") from exc
        return ActionResult.ok(data=response)

    @register_action(
        name="get_case",
        description="Get a specific Kibana case by ID.",
        category="cases",
        tags=["cases", "read"]
    )
    async def get_case(self, case_id: str) -> ActionResult:
        if not case_id:
            raise InvalidParameterError("'case_id' is required.")
        kibana = self._get_kibana_http()
        try:
            response = await kibana.get(f"/api/cases/{case_id}")
        except Exception as exc:
            raise ActionExecutionError(f"Failed to retrieve case: {exc}") from exc
        return ActionResult.ok(data=response)

    @register_action(
        name="delete_cases",
        description="Delete one or more Kibana cases.",
        category="cases",
        tags=["cases", "delete"]
    )
    async def delete_cases(self, case_ids: List[str]) -> ActionResult:
        if not case_ids:
            raise InvalidParameterError("'case_ids' must be provided.")
        kibana = self._get_kibana_http()
        ids_str = ",".join(case_ids)
        try:
            response = await kibana.delete(f"/api/cases?ids={ids_str}")
        except Exception as exc:
            raise ActionExecutionError(f"Failed to delete cases: {exc}") from exc
        return ActionResult.ok(data=response)

    @register_action(
        name="add_case_comment",
        description="Add a comment to a Kibana case.",
        category="cases",
        tags=["cases", "comment"]
    )
    async def add_case_comment(self, case_id: str, comment: str) -> ActionResult:
        if not case_id or not comment:
            raise InvalidParameterError("'case_id' and 'comment' are required.")
        kibana = self._get_kibana_http()
        body = {"comment": comment, "type": "user"}
        try:
            response = await kibana.post(
                f"/api/cases/{case_id}/comments",
                json=body
            )
        except Exception as exc:
            raise ActionExecutionError(f"Failed to add comment: {exc}") from exc
        return ActionResult.ok(data=response)

    # ------------------------------------------------------------------
    # Kibana Exception Lists API
    # ------------------------------------------------------------------

    @register_action(
        name="create_exception_list",
        description="Create a new exception list.",
        category="exceptions",
        tags=["exceptions", "create"]
    )
    async def create_exception_list(
        self,
        name: str,
        description: str,
        type_: str = "detection"
    ) -> ActionResult:
        if not name:
            raise InvalidParameterError("'name' is required.")
        body = {
            "name": name,
            "description": description,
            "type": type_
        }
        kibana = self._get_kibana_http()
        try:
            response = await kibana.post(
                "/api/exception_lists",
                json=body
            )
        except Exception as exc:
            raise ActionExecutionError(f"Failed to create exception list: {exc}") from exc
        return ActionResult.ok(data=response)

    @register_action(
        name="get_exception_lists",
        description="List exception lists.",
        category="exceptions",
        tags=["exceptions", "list"]
    )
    async def get_exception_lists(self, page: int = 1, per_page: int = 20) -> ActionResult:
        kibana = self._get_kibana_http()
        try:
            response = await kibana.get(
                "/api/exception_lists",
                params={"page": page, "per_page": per_page}
            )
        except Exception as exc:
            raise ActionExecutionError(f"Failed to list exception lists: {exc}") from exc
        return ActionResult.ok(data=response)
