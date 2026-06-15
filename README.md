# SOAR Connector Engine
**Developed by the Security Engineering Team**

This repository contains the core Execution Engine and Connectors for the organization's SOAR platform. It is designed as a standalone Python FastAPI microservice that handles all external security integrations natively.

## Architecture Overview
The engine uses a dynamic `ConnectorRegistry` and an advanced `ConnectorHTTPClient`. 
It natively supports:
- Automatic Retry & Exponential Backoff
- Rate Limit (429) Handling
- Proxy configurations & SSL Verification bypass
- OAuth2, Bearer, API Key, and Custom JWT authentications.

## Available Endpoints for the Backend Team

### 1. Discovery API (GET `/api/v1/connectors`)
Returns a list of all available connectors, their actions, and the **dynamically parsed parameters** required for each action.
**Frontend/Backend usage:** Use this endpoint to dynamically draw the Playbook UI forms. No need to hardcode inputs on the frontend!

### 2. Execution API (POST `/api/v1/connectors/execute`)
The main engine endpoint. Pass the connector name, action, parameters, and credentials.
```json
POST /api/v1/connectors/execute
{
  "connector": "slack",
  "action": "send_alert_message",
  "config": {
    "auth_type": "bearer",
    "auth_config": {"token": "xoxb-...."}
  },
  "params": {
    "channel": "#alerts",
    "title": "Malware Detected",
    "severity": "high"
  }
}
```

### 3. Connection Test (POST `/api/v1/connectors/{connector_name}/test`)
Tests if the credentials are valid before saving them to the database.
```json
POST /api/v1/connectors/slack/test
{
  "config": { ... }
}
```

### 4. Webhook Ingestion (POST `/api/v1/webhooks/{connector_name}`)
Receives raw webhooks from external systems (like Splunk or Wazuh) and normalizes them into a unified `WebhookEvent` format to trigger playbooks.

## Adding New Connectors
1. Create a new folder in `app/connectors/`.
2. Inherit from `BaseConnector`.
3. Use the `@register_action` decorator on any method.
4. The engine will automatically discover it and expose it to the UI!
