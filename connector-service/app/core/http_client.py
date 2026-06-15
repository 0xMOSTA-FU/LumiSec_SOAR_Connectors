"""
SOAR Connector Hub — HTTP Client
==================================
Async HTTP client with:
 - Automatic retry with exponential back-off
 - Rate-limit detection & auto-wait
 - Per-request logging
 - Timeout & SSL management
 - Proxy support
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, Optional

import httpx

from app.core.exceptions import (
    AuthenticationError,
    ConnectorHTTPError,
    ConnectionError,
    RateLimitError,
    TimeoutError,
)

logger = logging.getLogger("soar.http_client")


class ConnectorHTTPClient:
    """
    Thin async wrapper around httpx.AsyncClient.

    Handles:
    - Authentication header injection
    - Retry logic with exponential back-off
    - Rate-limit (429) detection + wait
    - Unified error translation
    """

    def __init__(
        self,
        base_url: str,
        headers: Dict[str, str] = {},
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        verify_ssl: bool = True,
        proxy_url: Optional[str] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_headers = headers
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.verify_ssl = verify_ssl
        self.proxy_url = proxy_url
        self._client: Optional[httpx.AsyncClient] = None

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    async def __aenter__(self) -> "ConnectorHTTPClient":
        await self._open()
        return self

    async def __aexit__(self, *_) -> None:
        await self._close()

    async def _open(self) -> None:
        proxies = {"all://": self.proxy_url} if self.proxy_url else None
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.default_headers,
            timeout=httpx.Timeout(self.timeout),
            verify=self.verify_ssl,
            proxies=proxies,
            follow_redirects=True,
        )

    async def _close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    # ─── Core Request ─────────────────────────────────────────────────────────

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        data: Optional[Any] = None,
        files: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout_override: Optional[int] = None,
        raw_response: bool = False,
    ) -> Any:
        """
        Execute an HTTP request with retry + rate-limit handling.

        Returns parsed JSON (dict/list) unless raw_response=True.
        """
        if self._client is None:
            await self._open()

        url = path if path.startswith("http") else path
        merged_headers = {**self.default_headers, **(headers or {})}
        timeout = timeout_override or self.timeout

        last_exc: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                start = time.monotonic()
                response = await self._client.request(
                    method.upper(),
                    url,
                    params=params,
                    json=json,
                    data=data,
                    files=files,
                    headers=merged_headers,
                    timeout=timeout,
                )
                elapsed_ms = int((time.monotonic() - start) * 1000)

                logger.debug(
                    "[%s %s] → %d (%dms) [attempt %d/%d]",
                    method.upper(),
                    url,
                    response.status_code,
                    elapsed_ms,
                    attempt,
                    self.max_retries,
                )

                # ── Rate limit ────────────────────────────────────────────────
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning("Rate limited. Waiting %ds before retry.", retry_after)
                    if attempt < self.max_retries:
                        await asyncio.sleep(retry_after)
                        continue
                    raise RateLimitError(
                        f"Rate limit exceeded after {self.max_retries} attempts.",
                        retry_after=retry_after,
                    )

                # ── Auth errors ───────────────────────────────────────────────
                if response.status_code in (401, 403):
                    raise AuthenticationError(
                        message=f"Authentication failed: HTTP {response.status_code}",
                        status_code=response.status_code,
                    )

                # ── Other HTTP errors ─────────────────────────────────────────
                if not response.is_success:
                    body = response.text[:500]
                    if attempt < self.max_retries and response.status_code >= 500:
                        wait = self.backoff_factor * (2 ** (attempt - 1))
                        logger.warning(
                            "Server error %d. Retrying in %.1fs...",
                            response.status_code,
                            wait,
                        )
                        await asyncio.sleep(wait)
                        last_exc = ConnectorHTTPError(
                            message=f"HTTP {response.status_code}: {body}",
                            status_code=response.status_code,
                            response_body=body,
                        )
                        continue
                    raise ConnectorHTTPError(
                        message=f"HTTP {response.status_code}: {body}",
                        status_code=response.status_code,
                        response_body=body,
                    )

                if raw_response:
                    return response
                if not response.content:
                    return {}
                try:
                    return response.json()
                except Exception:
                    return response.text

            except httpx.TimeoutException as exc:
                wait = self.backoff_factor * (2 ** (attempt - 1))
                logger.warning("Request timed out. Retry %d/%d in %.1fs", attempt, self.max_retries, wait)
                last_exc = TimeoutError(f"Request timed out after {timeout}s")
                if attempt < self.max_retries:
                    await asyncio.sleep(wait)

            except httpx.ConnectError as exc:
                wait = self.backoff_factor * (2 ** (attempt - 1))
                logger.warning("Connection failed: %s. Retry %d/%d in %.1fs", exc, attempt, self.max_retries, wait)
                last_exc = ConnectionError(f"Cannot connect to {self.base_url}: {exc}")
                if attempt < self.max_retries:
                    await asyncio.sleep(wait)

        raise last_exc or ConnectionError(f"Request failed after {self.max_retries} attempts.")

    # ─── Convenience Methods ──────────────────────────────────────────────────

    async def get(self, path: str, **kwargs) -> Any:
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs) -> Any:
        return await self.request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs) -> Any:
        return await self.request("PUT", path, **kwargs)

    async def patch(self, path: str, **kwargs) -> Any:
        return await self.request("PATCH", path, **kwargs)

    async def delete(self, path: str, **kwargs) -> Any:
        return await self.request("DELETE", path, **kwargs)
