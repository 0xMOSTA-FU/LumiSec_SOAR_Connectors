"""
SOAR Connector Hub — Built-in Security Utilities
================================================
"""

from __future__ import annotations

import re
import base64
import hashlib
from typing import Any, Dict

from app.core.base_connector import BaseConnector, register_action
from app.core.models import ConnectionResult


class SoarUtilsConnector(BaseConnector):
    NAME = "soar_utils"
    VERSION = "1.0.0"
    DESCRIPTION = "Built-in SOAR utilities for local data processing, cryptography, and IOC extraction."

    async def test_connection(self) -> ConnectionResult:
        # Local utility connector is always active
        return ConnectionResult(
            success=True,
            connector=self.NAME,
            message="Built-in SOAR Utils connector is active."
        )

    # ─── Data Extraction ──────────────────────────────────────────────────────

    @register_action("extract_iocs", "Extract IOCs (IPs, Domains, Hashes) from text", "utilities", ["ioc", "extract"])
    async def extract_iocs(self, text: str) -> dict:
        ipv4_pattern = r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
        # Simple domain regex for common TLDs
        domain_pattern = r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b"
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        md5_pattern = r"\b[a-fA-F0-9]{32}\b"
        sha1_pattern = r"\b[a-fA-F0-9]{40}\b"
        sha256_pattern = r"\b[a-fA-F0-9]{64}\b"
        
        iocs = {
            "ipv4": list(set(re.findall(ipv4_pattern, text))),
            "domains": list(set(re.findall(domain_pattern, text))),
            "emails": list(set(re.findall(email_pattern, text))),
            "md5": list(set(re.findall(md5_pattern, text))),
            "sha1": list(set(re.findall(sha1_pattern, text))),
            "sha256": list(set(re.findall(sha256_pattern, text))),
        }
        
        # Clean up domains to avoid matching emails as domains
        cleaned_domains = []
        for domain in iocs["domains"]:
            is_email = any(email.endswith(domain) for email in iocs["emails"])
            if not is_email:
                cleaned_domains.append(domain)
        iocs["domains"] = cleaned_domains
        
        return iocs

    # ─── Defang / Refang ──────────────────────────────────────────────────────

    @register_action("defang_ioc", "Defang an IOC to make it safe to click/copy", "utilities", ["ioc", "defang"])
    async def defang_ioc(self, ioc: str) -> dict:
        defanged = ioc.replace("http://", "hxxp[://]")\
                      .replace("https://", "hxxps[://]")\
                      .replace(".", "[.]")\
                      .replace("@", "[at]")
        return {"original": ioc, "defanged": defanged}

    @register_action("refang_ioc", "Refang an IOC to its original form", "utilities", ["ioc", "refang"])
    async def refang_ioc(self, defanged_ioc: str) -> dict:
        refanged = defanged_ioc.replace("hxxp[://]", "http://")\
                               .replace("hxxps[://]", "https://")\
                               .replace("hxxp://", "http://")\
                               .replace("hxxps://", "https://")\
                               .replace("[.]", ".")\
                               .replace("(.)", ".")\
                               .replace("[at]", "@")
        return {"original": defanged_ioc, "refanged": refanged}

    # ─── Cryptography ─────────────────────────────────────────────────────────

    @register_action("calculate_hash", "Calculate hash for a string", "cryptography", ["hash"])
    async def calculate_hash(self, text: str, algorithm: str = "sha256") -> dict:
        data = text.encode("utf-8")
        algo = algorithm.lower()
        
        if algo == "md5":
            result = hashlib.md5(data).hexdigest()
        elif algo == "sha1":
            result = hashlib.sha1(data).hexdigest()
        elif algo == "sha256":
            result = hashlib.sha256(data).hexdigest()
        elif algo == "sha512":
            result = hashlib.sha512(data).hexdigest()
        else:
            return {"error": f"Unsupported algorithm: {algorithm}"}
            
        return {"algorithm": algo, "hash": result}

    @register_action("base64_encode", "Encode text to Base64", "cryptography", ["base64", "encode"])
    async def base64_encode(self, text: str) -> dict:
        encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        return {"original": text, "encoded": encoded}

    @register_action("base64_decode", "Decode Base64 to text", "cryptography", ["base64", "decode"])
    async def base64_decode(self, encoded_text: str) -> dict:
        try:
            decoded = base64.b64decode(encoded_text).decode("utf-8")
            return {"original": encoded_text, "decoded": decoded}
        except Exception as e:
            return {"error": f"Failed to decode base64: {e}"}

    # ─── Parsing ──────────────────────────────────────────────────────────────

    @register_action("parse_user_agent", "Parse a User-Agent string", "parsing", ["user-agent"])
    async def parse_user_agent(self, user_agent: str) -> dict:
        # Simple heuristic parsing (in a real scenario, use 'user_agents' library)
        browser = "Unknown"
        os = "Unknown"
        device = "Desktop"
        
        ua_lower = user_agent.lower()
        
        # OS
        if "windows" in ua_lower: os = "Windows"
        elif "mac os" in ua_lower: os = "macOS"
        elif "android" in ua_lower: os = "Android"
        elif "linux" in ua_lower: os = "Linux"
        elif "iphone" in ua_lower or "ipad" in ua_lower: os = "iOS"
        
        # Device
        if os in ["Android", "iOS"]: device = "Mobile"
        
        # Browser
        if "edg" in ua_lower: browser = "Edge"
        elif "chrome" in ua_lower: browser = "Chrome"
        elif "safari" in ua_lower: browser = "Safari"
        elif "firefox" in ua_lower: browser = "Firefox"
        elif "msie" in ua_lower or "trident" in ua_lower: browser = "Internet Explorer"
            
        return {
            "browser": browser,
            "os": os,
            "device": device,
            "raw": user_agent
        }
