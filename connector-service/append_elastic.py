import os

CODE_TO_APPEND = """
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
"""

file_path = "C:/Users/mosta/.gemini/antigravity/scratch/soar-connectors/connector-service/app/connectors/elastic/connector.py"
with open(file_path, "a", encoding="utf-8") as f:
    f.write(CODE_TO_APPEND)

print("✅ Append successful!")
