import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def generate_markdown():
    response = client.get("/api/v1/connectors/")
    if response.status_code != 200:
        print("Failed to get connectors")
        return
    
    data = response.json()
    connectors = data.get("connectors", [])
    
    md = "# SOAR Connectors Reference\n\n"
    md += f"**Total Connectors:** {data.get('total')}\n\n"
    md += "This document is auto-generated and contains every single connector, action, and parameter available in the engine.\n\n"
    md += "---\n\n"
    
    for c in sorted(connectors, key=lambda x: x["name"]):
        md += f"## 🔌 {c['name']} (v{c['version']})\n"
        md += f"> {c['description']}\n\n"
        
        actions = c.get("actions", [])
        if not actions:
            md += "*No actions exposed yet.*\n\n"
            continue
            
        md += "### Available Actions\n\n"
        for act in sorted(actions, key=lambda x: x["name"]):
            md += f"#### `{act['name']}`\n"
            md += f"**Description:** {act.get('description', 'N/A')}\n\n"
            md += f"**Category:** `{act.get('category', 'general')}`\n\n"
            
            params = act.get("parameters", [])
            if params:
                md += "**Parameters:**\n"
                md += "| Name | Type | Required | Default |\n"
                md += "|------|------|----------|---------|\n"
                for p in params:
                    req = "✅" if p["required"] else "❌"
                    default = p.get("default", "")
                    if default == "":
                        default = "None"
                    md += f"| `{p['name']}` | `{p['type']}` | {req} | `{default}` |\n"
                md += "\n"
            else:
                md += "*No parameters required.*\n\n"
            
            # Add JSON Payload Example
            md += "**Execution Payload Example:**\n"
            example_params = {}
            for p in params:
                if p['type'] == 'int': example_params[p['name']] = 0
                elif p['type'] == 'str': example_params[p['name']] = "string"
                elif p['type'] == 'bool': example_params[p['name']] = True
                elif p['type'] == 'dict': example_params[p['name']] = {}
                elif p['type'] == 'list': example_params[p['name']] = []
                else: example_params[p['name']] = "..."
                
            example = {
                "connector": c['name'],
                "action": act['name'],
                "config": {"auth_type": "...", "auth_config": {}},
                "params": example_params
            }
            md += "```json\n" + json.dumps(example, indent=2) + "\n```\n\n"
            
        md += "---\n\n"
        
    with open("CONNECTORS_REFERENCE.md", "w", encoding="utf-8") as f:
        f.write(md)
        
    print("✅ CONNECTORS_REFERENCE.md generated successfully!")

if __name__ == "__main__":
    generate_markdown()
