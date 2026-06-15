"""
SOAR Connector Hub — Slack Connector
====================================
"""

from __future__ import annotations

import hmac
import hashlib
import time
import os
from typing import Any, Dict, List, Optional

from app.core.base_connector import BaseConnector, register_action
from app.core.models import ActionResult, ConnectionResult, WebhookEvent, WebhookEventType
from app.core.exceptions import InvalidParameterError, ActionExecutionError, WebhookValidationError


class SlackConnector(BaseConnector):
    NAME = "slack"
    VERSION = "1.0.0"
    DESCRIPTION = "Slack Web API connector for sending messages and automating channels."

    def _check_ok(self, response: dict) -> dict:
        """Check if Slack API returned 'ok': true."""
        if isinstance(response, dict) and not response.get("ok", True):
            error = response.get("error", "unknown_error")
            raise ActionExecutionError(f"Slack API error: {error}")
        return response

    async def test_connection(self) -> ConnectionResult:
        try:
            http = await self._get_http_client()
            resp = await http.post("/auth.test")
            self._check_ok(resp)
            return ConnectionResult(
                success=True,
                connector=self.NAME,
                message=f"Connected successfully to Slack workspace '{resp.get('team')}' as user '{resp.get('user')}'"
            )
        except Exception as e:
            return ConnectionResult(success=False, connector=self.NAME, message=str(e))

    @register_action("send_message", "Send a message to a channel", "communication", ["message", "chat"])
    async def send_message(self, channel: str, text: str, blocks: list = [], thread_ts: str = "", mrkdwn: bool = True) -> dict:
        http = await self._get_http_client()
        payload = {
            "channel": channel,
            "text": text,
            "mrkdwn": mrkdwn
        }
        if blocks: payload["blocks"] = blocks
        if thread_ts: payload["thread_ts"] = thread_ts
        
        response = await http.post("/chat.postMessage", json=payload)
        self._check_ok(response)
        return {"ts": response.get("ts"), "channel": response.get("channel")}

    @register_action("send_alert_message", "Send a formatted alert message", "alerting", ["alert", "blocks"])
    async def send_alert_message(self, channel: str, title: str, severity: str, description: str, fields: dict = {}, actions: list = []) -> dict:
        colors = {
            "critical": "danger",
            "high": "warning",
            "medium": "good",
            "low": "#439FE0"
        }
        color = colors.get(severity.lower(), "#439FE0")
        
        fields_blocks = []
        for k, v in fields.items():
            fields_blocks.append({
                "title": k,
                "value": str(v),
                "short": True
            })
            
        attachment = {
            "color": color,
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 {title}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Severity:*\n{severity.upper()}"},
                        {"type": "mrkdwn", "text": f"*Time:*\n<!date^{int(time.time())}^{{date_num}} {{time_secs}}|{time.strftime('%Y-%m-%d %H:%M:%S')}>"}
                    ]
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Description:*\n{description}"}
                }
            ]
        }
        
        if fields_blocks:
            attachment["fields"] = fields_blocks
            
        if actions:
            attachment["blocks"].append({"type": "actions", "elements": actions})

        http = await self._get_http_client()
        payload = {
            "channel": channel,
            "attachments": [attachment]
        }
        response = await http.post("/chat.postMessage", json=payload)
        self._check_ok(response)
        return {"ts": response.get("ts"), "channel": response.get("channel")}

    @register_action("create_incident_thread", "Create an incident thread", "incident", ["incident", "thread"])
    async def create_incident_thread(self, channel: str, incident_id: str, title: str, severity: str, assignee: str = "", description: str = "") -> dict:
        text = f"Incident {incident_id}: {title} (Severity: {severity})"
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🔥 New Incident: {incident_id}"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Title:*\n{title}"},
                    {"type": "mrkdwn", "text": f"*Severity:*\n{severity}"},
                    {"type": "mrkdwn", "text": f"*Assignee:*\n{assignee or 'Unassigned'}"}
                ]
            }
        ]
        if description:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Description:*\n{description}"}
            })
            
        return await self.send_message(channel=channel, text=text, blocks=blocks)

    @register_action("update_message", "Update an existing message", "communication", ["update"])
    async def update_message(self, channel: str, ts: str, text: str = "", blocks: list = []) -> dict:
        http = await self._get_http_client()
        payload = {"channel": channel, "ts": ts}
        if text: payload["text"] = text
        if blocks: payload["blocks"] = blocks
        
        response = await http.post("/chat.update", json=payload)
        return self._check_ok(response)

    @register_action("delete_message", "Delete a message", "communication", ["delete"])
    async def delete_message(self, channel: str, ts: str) -> dict:
        http = await self._get_http_client()
        response = await http.post("/chat.delete", json={"channel": channel, "ts": ts})
        return self._check_ok(response)

    @register_action("add_reaction", "Add emoji reaction to message", "communication", ["reaction"])
    async def add_reaction(self, channel: str, ts: str, reaction: str) -> dict:
        http = await self._get_http_client()
        response = await http.post("/reactions.add", json={"channel": channel, "timestamp": ts, "name": reaction.strip(":")})
        return self._check_ok(response)

    @register_action("remove_reaction", "Remove emoji reaction", "communication", ["reaction"])
    async def remove_reaction(self, channel: str, ts: str, reaction: str) -> dict:
        http = await self._get_http_client()
        response = await http.post("/reactions.remove", json={"channel": channel, "timestamp": ts, "name": reaction.strip(":")})
        return self._check_ok(response)

    @register_action("get_channel_history", "Get channel message history", "history", ["messages"])
    async def get_channel_history(self, channel: str, limit: int = 20, oldest: str = "", latest: str = "") -> dict:
        http = await self._get_http_client()
        params = {"channel": channel, "limit": limit}
        if oldest: params["oldest"] = oldest
        if latest: params["latest"] = latest
        response = await http.get("/conversations.history", params=params)
        return self._check_ok(response)

    @register_action("get_thread_replies", "Get replies in a thread", "history", ["thread"])
    async def get_thread_replies(self, channel: str, thread_ts: str, limit: int = 20) -> dict:
        http = await self._get_http_client()
        params = {"channel": channel, "ts": thread_ts, "limit": limit}
        response = await http.get("/conversations.replies", params=params)
        return self._check_ok(response)

    @register_action("create_channel", "Create a new channel", "channels", ["create"])
    async def create_channel(self, name: str, is_private: bool = False) -> dict:
        http = await self._get_http_client()
        name = name.lower().replace(" ", "-")
        payload = {"name": name, "is_private": is_private}
        response = await http.post("/conversations.create", json=payload)
        return self._check_ok(response)

    @register_action("archive_channel", "Archive a channel", "channels", ["archive"])
    async def archive_channel(self, channel: str) -> dict:
        http = await self._get_http_client()
        response = await http.post("/conversations.archive", json={"channel": channel})
        return self._check_ok(response)

    @register_action("invite_users", "Invite users to channel", "channels", ["invite"])
    async def invite_users(self, channel: str, user_ids: list) -> dict:
        http = await self._get_http_client()
        payload = {"channel": channel, "users": ",".join(user_ids)}
        response = await http.post("/conversations.invite", json=payload)
        return self._check_ok(response)

    @register_action("kick_user", "Kick a user from a channel", "channels", ["kick"])
    async def kick_user(self, channel: str, user_id: str) -> dict:
        http = await self._get_http_client()
        payload = {"channel": channel, "user": user_id}
        response = await http.post("/conversations.kick", json=payload)
        return self._check_ok(response)

    @register_action("set_channel_topic", "Set channel topic", "channels", ["topic"])
    async def set_channel_topic(self, channel: str, topic: str) -> dict:
        http = await self._get_http_client()
        payload = {"channel": channel, "topic": topic}
        response = await http.post("/conversations.setTopic", json=payload)
        return self._check_ok(response)

    @register_action("set_channel_purpose", "Set channel purpose", "channels", ["purpose"])
    async def set_channel_purpose(self, channel: str, purpose: str) -> dict:
        http = await self._get_http_client()
        payload = {"channel": channel, "purpose": purpose}
        response = await http.post("/conversations.setPurpose", json=payload)
        return self._check_ok(response)

    @register_action("get_channel_info", "Get info about a channel", "channels", ["info"])
    async def get_channel_info(self, channel: str) -> dict:
        http = await self._get_http_client()
        response = await http.get("/conversations.info", params={"channel": channel})
        return self._check_ok(response)

    @register_action("list_channels", "List channels", "channels", ["list"])
    async def list_channels(self, types: str = "public_channel,private_channel", limit: int = 100) -> dict:
        http = await self._get_http_client()
        response = await http.get("/conversations.list", params={"types": types, "limit": limit})
        return self._check_ok(response)

    @register_action("get_user_info", "Get user info", "users", ["info"])
    async def get_user_info(self, user_id: str) -> dict:
        http = await self._get_http_client()
        response = await http.get("/users.info", params={"user": user_id})
        resp = self._check_ok(response)
        user = resp.get("user", {})
        return {
            "real_name": user.get("real_name"),
            "email": user.get("profile", {}).get("email"),
            "display_name": user.get("profile", {}).get("display_name"),
            "is_admin": user.get("is_admin")
        }

    @register_action("get_user_by_email", "Lookup user by email", "users", ["email"])
    async def get_user_by_email(self, email: str) -> dict:
        http = await self._get_http_client()
        response = await http.get("/users.lookupByEmail", params={"email": email})
        return self._check_ok(response)

    @register_action("list_users", "List all users", "users", ["list"])
    async def list_users(self, limit: int = 200) -> dict:
        http = await self._get_http_client()
        response = await http.get("/users.list", params={"limit": limit})
        return self._check_ok(response)

    @register_action("upload_file", "Upload a file to Slack", "files", ["upload"])
    async def upload_file(self, channels: list, content: str = "", filename: str = "report.txt", filetype: str = "text", title: str = "", file_path: str = "") -> dict:
        http = await self._get_http_client()
        data = {
            "channels": ",".join(channels),
            "filename": filename,
            "filetype": filetype,
            "title": title
        }
        files = None
        if file_path and os.path.exists(file_path):
            files = {"file": (filename, open(file_path, "rb"))}
        elif content:
            data["content"] = content
        else:
            raise InvalidParameterError("content/file_path", "Provide either content or file_path")
            
        # Slack files.upload requires multipart/form-data if using 'file' param, or URL encoded if using 'content'
        if files:
            response = await http.request("POST", "/files.upload", data=data, files=files)
        else:
            response = await http.post("/files.upload", data=data)
            
        return self._check_ok(response)

    @register_action("pin_message", "Pin a message", "channels", ["pin"])
    async def pin_message(self, channel: str, ts: str) -> dict:
        http = await self._get_http_client()
        response = await http.post("/pins.add", json={"channel": channel, "timestamp": ts})
        return self._check_ok(response)

    @register_action("unpin_message", "Unpin a message", "channels", ["unpin"])
    async def unpin_message(self, channel: str, ts: str) -> dict:
        http = await self._get_http_client()
        response = await http.post("/pins.remove", json={"channel": channel, "timestamp": ts})
        return self._check_ok(response)

    @register_action("get_workspace_info", "Get workspace info", "system", ["team"])
    async def get_workspace_info(self) -> dict:
        http = await self._get_http_client()
        response = await http.get("/team.info")
        return self._check_ok(response)

    @register_action("set_status", "Set user status", "users", ["status"])
    async def set_status(self, status_text: str, status_emoji: str, status_expiration: int = 0) -> dict:
        http = await self._get_http_client()
        payload = {
            "profile": {
                "status_text": status_text,
                "status_emoji": status_emoji,
                "status_expiration": status_expiration
            }
        }
        response = await http.post("/users.profile.set", json=payload)
        return self._check_ok(response)

    async def validate_webhook_signature(self, payload: bytes, headers: Dict[str, str]) -> bool:
        """Validate Slack Events API signature."""
        signing_secret = self._raw_config.get("signing_secret", "")
        if not signing_secret:
            return True # Not strictly enforced if secret not provided
            
        slack_signature = headers.get("x-slack-signature", "")
        slack_timestamp = headers.get("x-slack-request-timestamp", "")
        
        if abs(time.time() - float(slack_timestamp)) > 60 * 5:
            return False
            
        sig_basestring = f"v0:{slack_timestamp}:{payload.decode()}"
        my_signature = "v0=" + hmac.new(
            signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(my_signature, slack_signature)

    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> WebhookEvent | None:
        """Parse Slack Events API payload."""
        if payload.get("type") == "url_verification":
            # API layer usually handles this directly
            pass
            
        event = payload.get("event", {})
        event_type = event.get("type", "")
        
        normalized = {}
        if event_type == "message":
            normalized = {
                "text": event.get("text"),
                "user": event.get("user"),
                "channel": event.get("channel"),
                "ts": event.get("ts")
            }
            
        return WebhookEvent(
            connector=self.NAME,
            event_type=WebhookEventType.GENERIC,
            raw_payload=payload,
            normalized=normalized
        )
