# SOAR Connector Engine - Backend Handover Documentation
**Version:** 1.0.0
**Target Audience:** Node.js Backend Engineering Team
**Author:** Security Engineering Team

---

## 1. Executive Summary & Architecture
Welcome to the Core SOAR Connector Engine. This engine is a standalone **Python 3.13 FastAPI Microservice**. Its sole responsibility is to act as the "Integration Hub" between your Node.js backend and the outside world.

**Why a Microservice?**
Writing 22 complex integrations (handling API keys, JWTs, OAuth2, Rate Limits, Proxies, and SSL bypasses) inside a Node.js workflow runner is heavily error-prone. This Python microservice abstracts all of that. 
Your Node.js app doesn't need to know *how* to talk to Splunk or Jira; it just tells this Python service "Execute this action on Jira with these parameters", and the Python service securely handles the rest, returning a unified JSON result.

---

## 2. Project Directory Structure
The workspace is located at: `soar-connectors/`
```text
soar-connectors/
├── docker-compose.yml       # Production-ready Compose file for the microservice
├── nodejs-backend/          # Example Node.js SDK and test client (soarClient.js)
├── README.md                # Quickstart guide
└── connector-service/       # The core Python Microservice codebase
    ├── Dockerfile           # Docker configuration for the engine
    ├── requirements.txt     # Python dependencies (FastAPI, httpx, pydantic)
    └── app/
        ├── main.py          # FastAPI application entry point
        ├── api/             # API Routes (Discovery, Execution, Webhooks, Health)
        ├── core/            # The Core Engine Logic
        │   ├── base_connector.py # Base class inherited by all 22 connectors
        │   ├── http_client.py    # Resilient HTTP Client (Retries, RateLimits, Proxy)
        │   ├── auth.py           # Universal Auth Handler (Bearer, Basic, API Key, JWT)
        │   └── registry.py       # Auto-discovery mechanism for connectors
        └── connectors/      # The 22 Integrations (The actual vendor code)
            ├── jira/
            ├── servicenow/
            ├── elastic/
            ├── ...
```

---

## 3. Advanced Engine Capabilities (Zero Node.js Logic Needed)
The backend team **DOES NOT** need to code any of the following; the Python engine handles it natively:
1. **Auto-Retries & Backoff:** If Jira returns a `503 Service Unavailable`, the engine automatically retries 3 times using exponential backoff.
2. **Rate Limit Management:** If Splunk returns `429 Too Many Requests`, the engine pauses execution based on the `Retry-After` header automatically.
3. **Enterprise Proxies:** If the customer requires outbound traffic to go through a corporate proxy, simply pass `proxy_url` in the connection config.
4. **SSL Bypasses:** For On-Premises systems using self-signed certs (e.g., OPNsense, Wazuh), pass `verify_ssl: false` in the config to bypass certificate validation.

---

## 4. REST API Endpoints (The Node.js Contract)

### 4.1. Discovery API (Dynamic UI Generation)
**Endpoint:** `GET /api/v1/connectors`
**Purpose:** Returns a massive JSON array of all 22 connectors, their actions, and the **data types** of the parameters needed.
**Backend Task:** Expose this to the Frontend (React/Vue). The frontend should map this JSON to dynamically render input forms. **Never hardcode inputs!**

### 4.2. Connection Test API
**Endpoint:** `POST /api/v1/connectors/{connector_name}/test`
**Purpose:** Tests the provided API keys/tokens *before* you save them to the MongoDB database.
**Backend Task:** When a user creates a new "Credential" in your UI, hit this endpoint first. If it returns success, save it.

### 4.3. Execution API (The Workflow Runner)
**Endpoint:** `POST /api/v1/connectors/execute`
**Purpose:** Executes a specific action.
**Backend Task:** During Playbook execution (DAG node traversal), when a node is triggered, the Node.js backend retrieves the saved credentials from the DB and makes this call.
**Payload Schema:**
```json
{
  "connector": "slack",
  "action": "send_message",
  "config": {
    "auth_type": "bearer",
    "auth_config": {"token": "xoxb-..."},
    "proxy_url": "http://corp-proxy:8080"  // Optional
  },
  "params": {
    "channel": "#security-alerts",
    "text": "Alert triggered!"
  }
}
```

### 4.4. Webhook Ingestion API
**Endpoint:** `POST /api/v1/webhooks/{connector_name}`
**Purpose:** Receives raw webhooks from external vendors (like Elastic or Wazuh), normalizes them into a unified `WebhookEvent` JSON, and can forward them to the Node.js workflow trigger logic.

---

## 5. The 22 Supported Integrations (Connectors)
This engine ships with 22 production-grade integrations, fully covering modern SOAR use cases:

**IT & Ticketing (Case Management):**
- **Jira:** Create, Update, and Comment on IT issues.
- **ServiceNow:** Enterprise Incident creation and tracking.
- **TheHive:** Dedicated Security Incident Response platform.
- **PagerDuty:** On-call alerting and automated phone calls.

**Security Information & Event Management (SIEM):**
- **Elastic Stack:** Search, ES|QL, SIEM Rules, Alerts, Cases, Exceptions, Fleet isolation.
- **Splunk:** Run SPL searches, create alerts, manage lookup tables.
- **Wazuh:** Open-source SIEM (Agents, Active Response, SCA, FIM).

**Endpoint Detection & Response (EDR):**
- **Velociraptor:** Run VQL forensic hunts, download forensic files.

**Firewalls & Network:**
- **OPNsense:** Block malicious IPs/Domains, update Firewall Aliases.
- **FortiGate:** Address objects management, address groups.

**Threat Intelligence & Sandboxing:**
- **VirusTotal:** Scan files/URLs, get reputation reports, YARA hunting.
- **OpenCTI:** Threat Intel platform (Stix indicators, Observables).
- **MISP:** Malware Information Sharing Platform.
- **Cuckoo Sandbox:** Submit malware for behavioral analysis.

**Cloud & Collaboration:**
- **MS Graph:** Send Outlook emails, manage Teams channels/messages.
- **Slack:** Block-kit messages, dynamic alerts.
- **DigitalOcean:** Cloud infrastructure isolation (Droplets, Firewalls, Snapshots).

**Vulnerability Management:**
- **DefectDojo:** Manage findings, endpoints, and engagements.

**Core Utilities:**
- **soar_utils:** Defang URLs, compute Hashes, Base64 encoding.
- **email:** Generic SMTP/IMAP handler.
- **http_request:** Universal Joker block for any undocumented REST API.
- **webhook:** Generic webhook receiver for custom triggers.

---

## 6. Your Mission (Node.js Backend Tasks)
To finalize the SOAR platform, your Node.js system must implement:
1. **Credential Vault:** Securely encrypt and store the API keys provided by the user.
2. **Playbook DAG Engine:** A Graph runner that executes nodes sequentially, taking the `result.data` output of one execution and injecting it as `params` into the next execution.
3. **Cron Job Scheduler:** E.g., `node-cron` to automatically trigger playbooks every 5 minutes (like pulling new alerts from Elastic).
4. **State Management:** Keeping track of running, failed, and completed Playbooks.

You have the engine. You have the weapons. Now, build the command center! 
