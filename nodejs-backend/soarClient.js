/**
 * Example Node.js Client to communicate with the Python SOAR Connector Hub
 * This is what your backend team will use to integrate.
 */
const axios = require('axios');

const CONNECTOR_SERVICE_URL = process.env.CONNECTOR_SERVICE_URL || 'http://localhost:8000';

class SoarConnectorClient {
    /**
     * Test a connector's credentials
     * @param {string} connectorName e.g., 'virustotal', 'slack'
     * @param {Object} config The configuration object (auth details)
     */
    static async testConnection(connectorName, config) {
        try {
            const response = await axios.post(`${CONNECTOR_SERVICE_URL}/api/v1/connectors/${connectorName}/test`, {
                config: config
            });
            return response.data; // { success: true/false, message: "..." }
        } catch (error) {
            console.error(`Failed to test connection for ${connectorName}:`, error.response?.data || error.message);
            throw error;
        }
    }

    /**
     * Execute any action on any connector
     * @param {string} connectorName e.g., 'virustotal'
     * @param {Object} config The configuration (usually retrieved from MongoDB)
     * @param {string} actionName e.g., 'get_ip_report'
     * @param {Object} params Action parameters e.g., { ip: '1.1.1.1' }
     */
    static async executeAction(connectorName, config, actionName, params) {
        const payload = {
            config: config,
            request: {
                connector_name: connectorName,
                action_name: actionName,
                params: params,
                request_id: `req-${Date.now()}` // for tracking logs
            }
        };

        try {
            const response = await axios.post(`${CONNECTOR_SERVICE_URL}/api/v1/connectors/execute`, payload);
            return response.data; // Standardized ActionResult schema
        } catch (error) {
            console.error(`Action execution failed:`, error.response?.data || error.message);
            throw error;
        }
    }
}

// =========================================================================
// USAGE EXAMPLE: How your Node.js Platform calls the Python Connectors
// =========================================================================

async function runExample() {
    // 1. Fetch config from your MongoDB (simulated here)
    const slackConfig = {
        base_url: "https://slack.com/api",
        auth_type: "bearer_token",
        auth_config: { token: "xoxb-your-slack-bot-token-here" }
    };

    console.log("1. Testing Slack Connection...");
    // const testRes = await SoarConnectorClient.testConnection("slack", slackConfig);
    // console.log("Test Result:", testRes);

    console.log("2. Executing 'send_alert_message' on Slack...");
    const actionParams = {
        channel: "#security-alerts",
        title: "Malware Detected on Endpoint",
        severity: "high", // Automatically makes the Slack message orange
        description: "Wazuh agent reported a suspicious file execution.",
        fields: {
            "Hostname": "DESKTOP-1234",
            "IP Address": "192.168.1.50"
        }
    };

    // const result = await SoarConnectorClient.executeAction("slack", slackConfig, "send_alert_message", actionParams);
    // console.log("Action Result:", JSON.stringify(result, null, 2));
    
    console.log("Ready! Integration is that simple.");
}

if (require.main === module) {
    runExample();
}

module.exports = SoarConnectorClient;
