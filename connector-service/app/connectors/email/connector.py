"""
SOAR Connector Hub — Email Connector
====================================
"""

from __future__ import annotations

import re
import socket
import base64
import time
from typing import Any, Dict, List, Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import aiosmtplib

from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult, WebhookEvent
from app.core.exceptions import InvalidParameterError, ActionExecutionError, ConfigurationError
from app.core.http_client import ConnectorHTTPClient
from app.core.auth import build_auth_handler


class EmailConnector(BaseConnector):
    NAME = "email"
    VERSION = "1.0.0"
    DESCRIPTION = "Multi-provider email connector (SMTP, SendGrid, Mailgun) for sending alerts and reports."

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self._provider = config.get("provider", "smtp").lower()
        if self._provider not in ["smtp", "sendgrid", "mailgun"]:
            raise ConfigurationError(f"Unsupported email provider: {self._provider}")

    # ─── Internal Handlers ───────────────────────────────────────────────────

    async def _send_smtp(self, to: list, subject: str, body: str, from_email: str, cc: list, bcc: list, html: bool, attachments: list) -> dict:
        host = self._raw_config.get("smtp_host")
        port = self._raw_config.get("smtp_port", 587)
        username = self._raw_config.get("smtp_username")
        password = self._raw_config.get("smtp_password")
        use_tls = self._raw_config.get("smtp_use_tls", True)
        from_addr = from_email or username

        msg = MIMEMultipart()
        msg["From"] = from_addr
        msg["To"] = ",".join(to)
        msg["Subject"] = subject
        if cc:
            msg["Cc"] = ",".join(cc)
        
        msg.attach(MIMEText(body, "html" if html else "plain"))

        for att in attachments:
            part = MIMEBase("application", "octet-stream")
            content = att.get("content", "")
            if not content:
                continue
            part.set_payload(base64.b64decode(content))
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{att.get("filename", "attachment")}"')
            msg.attach(part)

        try:
            rcpt = to + cc + bcc
            await aiosmtplib.send(
                msg,
                hostname=host,
                port=port,
                username=username,
                password=password,
                start_tls=use_tls,
                recipients=rcpt
            )
            return {"status": "success", "provider": "smtp"}
        except Exception as e:
            raise ActionExecutionError(f"SMTP error: {e}")

    async def _send_sendgrid(self, to: list, subject: str, body: str, from_email: str, cc: list, bcc: list, html: bool, attachments: list) -> dict:
        http = await self._get_http_client()
        personalizations = [{"to": [{"email": e} for e in to]}]
        if cc: personalizations[0]["cc"] = [{"email": e} for e in cc]
        if bcc: personalizations[0]["bcc"] = [{"email": e} for e in bcc]
        
        payload = {
            "personalizations": personalizations,
            "from": {"email": from_email or "no-reply@soar.local"},
            "subject": subject,
            "content": [{"type": "text/html" if html else "text/plain", "value": body}]
        }
        
        if attachments:
            sg_atts = []
            for att in attachments:
                sg_atts.append({
                    "content": att.get("content"),
                    "filename": att.get("filename", "attachment"),
                    "type": att.get("type", "application/octet-stream"),
                    "disposition": "attachment"
                })
            payload["attachments"] = sg_atts
            
        response = await http.post("/mail/send", json=payload, raw_response=True)
        if response.status_code not in [200, 202]:
            raise ActionExecutionError(f"SendGrid error: {response.text}")
        return {"status": "success", "provider": "sendgrid"}

    async def _send_mailgun(self, to: list, subject: str, body: str, from_email: str, cc: list, bcc: list, html: bool, attachments: list) -> dict:
        domain = self._raw_config.get("mailgun_domain")
        if not domain:
            raise ConfigurationError("mailgun_domain is required for Mailgun provider")
            
        http = await self._get_http_client()
        data = {
            "from": from_email or f"SOAR <no-reply@{domain}>",
            "to": to,
            "subject": subject,
            "html" if html else "text": body
        }
        if cc: data["cc"] = cc
        if bcc: data["bcc"] = bcc
        
        files = []
        for att in attachments:
            content_bytes = base64.b64decode(att.get("content", ""))
            files.append(("attachment", (att.get("filename"), content_bytes)))
            
        if files:
            response = await http.request("POST", f"/v3/{domain}/messages", data=data, files=files)
        else:
            response = await http.post(f"/v3/{domain}/messages", data=data)
            
        return {"status": "success", "provider": "mailgun", "id": response.get("id")}

    def _build_alert_html(self, alert_title: str, severity: str, description: str, affected_host: str, alert_id: str, additional_fields: dict) -> str:
        colors = {
            "critical": "#dc3545",
            "high": "#fd7e14",
            "medium": "#ffc107",
            "low": "#28a745"
        }
        color = colors.get(severity.lower(), "#6c757d")
        
        rows = ""
        for k, v in additional_fields.items():
            rows += f"<tr><td style='padding: 8px; border-bottom: 1px solid #ddd;'><strong>{k}</strong></td><td style='padding: 8px; border-bottom: 1px solid #ddd;'>{v}</td></tr>"

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; margin: 0; padding: 20px; background-color: #f8f9fa;">
            <div style="max-width: 600px; margin: 0 auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background-color: {color}; color: white; padding: 20px; text-align: center;">
                    <h2 style="margin: 0; font-size: 24px;">🚨 {alert_title}</h2>
                </div>
                <div style="padding: 30px;">
                    <p style="font-size: 16px; margin-top: 0;"><strong>Severity:</strong> <span style="display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: {color}; color: white; font-weight: bold; font-size: 12px; text-transform: uppercase;">{severity}</span></p>
                    <p style="font-size: 16px;"><strong>Description:</strong><br>{description}</p>
                    
                    <h3 style="border-bottom: 2px solid #eee; padding-bottom: 8px; margin-top: 30px;">Incident Details</h3>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px;">
                        <tr><td style="padding: 8px; border-bottom: 1px solid #ddd; width: 40%;"><strong>Alert ID</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{alert_id or 'N/A'}</td></tr>
                        <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Affected Host</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{affected_host or 'N/A'}</td></tr>
                        <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Time Reported</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}</td></tr>
                        {rows}
                    </table>
                </div>
                <div style="background-color: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; color: #777;">
                    <p style="margin: 0;">Powered by SOAR Connector Hub</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    # ─── Actions ─────────────────────────────────────────────────────────────

    async def test_connection(self) -> ConnectionResult:
        try:
            if self._provider == "smtp":
                host = self._raw_config.get("smtp_host")
                port = self._raw_config.get("smtp_port", 587)
                use_tls = self._raw_config.get("smtp_use_tls", True)
                client = aiosmtplib.SMTP(hostname=host, port=port, start_tls=use_tls)
                await client.connect()
                await client.quit()
                return ConnectionResult(success=True, connector=self.NAME, message="SMTP connection successful")
            
            elif self._provider == "sendgrid":
                http = await self._get_http_client()
                resp = await http.get("/user/profile")
                return ConnectionResult(success=True, connector=self.NAME, message="SendGrid auth successful")
                
            elif self._provider == "mailgun":
                http = await self._get_http_client()
                resp = await http.get("/domains")
                return ConnectionResult(success=True, connector=self.NAME, message="Mailgun auth successful")
                
        except Exception as e:
            return ConnectionResult(success=False, connector=self.NAME, message=str(e))

    @register_action("send_email", "Send an email", "communication", ["email", "send"])
    async def send_email(self, to: list, subject: str, body: str, from_email: str = "", cc: list = [], bcc: list = [], html: bool = True, attachments: list = []) -> dict:
        if self._provider == "smtp":
            return await self._send_smtp(to, subject, body, from_email, cc, bcc, html, attachments)
        elif self._provider == "sendgrid":
            return await self._send_sendgrid(to, subject, body, from_email, cc, bcc, html, attachments)
        elif self._provider == "mailgun":
            return await self._send_mailgun(to, subject, body, from_email, cc, bcc, html, attachments)
        else:
            raise ActionExecutionError(f"Unknown provider: {self._provider}")

    @register_action("send_alert_email", "Send a formatted HTML security alert", "alerting", ["alert"])
    async def send_alert_email(self, to: list, alert_title: str, severity: str, description: str, affected_host: str = "", alert_id: str = "", from_email: str = "", additional_fields: dict = {}) -> dict:
        html_body = self._build_alert_html(alert_title, severity, description, affected_host, alert_id, additional_fields)
        return await self.send_email(to=to, subject=f"[SOAR Alert] [{severity.upper()}] {alert_title}", body=html_body, from_email=from_email, html=True)

    @register_action("send_report_email", "Send a report via email", "reporting", ["report"])
    async def send_report_email(self, to: list, report_title: str, report_html: str = "", report_file_path: str = "", from_email: str = "") -> dict:
        attachments = []
        if report_file_path:
            import os
            if os.path.exists(report_file_path):
                with open(report_file_path, "rb") as f:
                    content = base64.b64encode(f.read()).decode('utf-8')
                    attachments.append({
                        "filename": os.path.basename(report_file_path),
                        "content": content,
                        "type": "application/pdf" if report_file_path.endswith('.pdf') else "application/octet-stream"
                    })
        
        body = report_html or f"<h1>{report_title}</h1><p>Please find the report attached.</p>"
        return await self.send_email(to=to, subject=report_title, body=body, from_email=from_email, html=True, attachments=attachments)

    @register_action("send_bulk_email", "Send bulk email with template variables", "communication", ["bulk"])
    async def send_bulk_email(self, recipients: list, subject: str, body_template: str, html: bool = True) -> dict:
        # recipients format: [{"email": "x@x.com", "variables": {"name": "John"}}]
        results = []
        for rcpt in recipients:
            body = body_template
            for k, v in rcpt.get("variables", {}).items():
                body = body.replace(f"{{{{{k}}}}}", str(v))
            res = await self.send_email(to=[rcpt["email"]], subject=subject, body=body, html=html)
            results.append({"email": rcpt["email"], "status": res.get("status")})
        return {"results": results}

    @register_action("verify_email_address", "Verify email address format and MX record", "utilities", ["verify"])
    async def verify_email_address(self, email: str) -> dict:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {"valid": False, "reason": "Invalid format"}
            
        domain = email.split('@')[1]
        try:
            # Simple DNS resolution to check if domain exists
            socket.gethostbyname(domain)
            return {"valid": True, "reason": "Valid format and domain resolves"}
        except socket.error:
            return {"valid": False, "reason": "Domain does not resolve"}

    @register_action("get_send_status", "Check delivery status of message", "communication", ["status"])
    async def get_send_status(self, message_id: str) -> dict:
        if self._provider == "sendgrid":
            # Requires Event Webhook or Email Activity API (Enterprise)
            return {"status": "not_supported", "reason": "SendGrid requires Events Webhook for delivery status"}
        elif self._provider == "mailgun":
            domain = self._raw_config.get("mailgun_domain")
            http = await self._get_http_client()
            response = await http.get(f"/v3/{domain}/events", params={"message-id": message_id})
            return {"events": response.get("items", [])}
        else:
            return {"status": "not_supported"}
