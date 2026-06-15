# SOAR Connectors Reference

**Total Connectors:** 22

This document is auto-generated and contains every single connector, action, and parameter available in the engine.

---

## 🔌 DefectDojo (v1.0.0)
> DefectDojo SOAR connector for vulnerability management.

*No actions exposed yet.*

## 🔌 Jira (v1.0.0)
> Jira Cloud Connector for managing issues and comments.

*No actions exposed yet.*

## 🔌 OPNsense (v1.0.0)
> OPNsense firewall connector for managing aliases and rules

*No actions exposed yet.*

## 🔌 PagerDuty (v1.0.0)
> Connector for PagerDuty REST API v2

*No actions exposed yet.*

## 🔌 ServiceNow (v1.0.0)
> ServiceNow connector for ITSM incident management.

### Available Actions

#### `create_incident`
**Description:** Create a new incident in ServiceNow

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `short_description` | `str` | ✅ | `None` |
| `description` | `str` | ✅ | `None` |
| `urgency` | `str` | ❌ | `3` |
| `impact` | `str` | ❌ | `3` |

**Execution Payload Example:**
```json
{
  "connector": "ServiceNow",
  "action": "create_incident",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "short_description": "string",
    "description": "string",
    "urgency": "string",
    "impact": "string"
  }
}
```

#### `get_incident`
**Description:** Get an incident from ServiceNow by sys_id

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `sys_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "ServiceNow",
  "action": "get_incident",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "sys_id": "string"
  }
}
```

#### `update_incident`
**Description:** Update an existing incident in ServiceNow

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `sys_id` | `str` | ✅ | `None` |
| `state` | `Optional` | ❌ | `None` |
| `work_notes` | `Optional` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "ServiceNow",
  "action": "update_incident",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "sys_id": "string",
    "state": "...",
    "work_notes": "..."
  }
}
```

---

## 🔌 TheHive (v1.0.0)
> Connector for TheHive v4 REST API

*No actions exposed yet.*

## 🔌 Velociraptor (v1.0.0)
> Connector for Velociraptor Server API.

*No actions exposed yet.*

## 🔌 cuckoo (v1.0.0)
> Cuckoo Sandbox REST API v2 connector

*No actions exposed yet.*

## 🔌 digitalocean (v1.0.0)
> Digital Ocean API connector for Firewall and Droplet management.

### Available Actions

#### `add_droplets_to_firewall`
**Description:** Add droplets to a firewall

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `firewall_id` | `str` | ✅ | `None` |
| `droplet_ids` | `list` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "add_droplets_to_firewall",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "firewall_id": "string",
    "droplet_ids": []
  }
}
```

#### `add_inbound_rule`
**Description:** Add an inbound rule to a firewall

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `firewall_id` | `str` | ✅ | `None` |
| `protocol` | `str` | ✅ | `None` |
| `ports` | `str` | ✅ | `None` |
| `source_addresses` | `list` | ❌ | `[]` |
| `source_droplet_ids` | `list` | ❌ | `[]` |
| `source_tags` | `list` | ❌ | `[]` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "add_inbound_rule",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "firewall_id": "string",
    "protocol": "string",
    "ports": "string",
    "source_addresses": [],
    "source_droplet_ids": [],
    "source_tags": []
  }
}
```

#### `add_outbound_rule`
**Description:** Add an outbound rule to a firewall

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `firewall_id` | `str` | ✅ | `None` |
| `protocol` | `str` | ✅ | `None` |
| `ports` | `str` | ✅ | `None` |
| `destination_addresses` | `list` | ❌ | `[]` |
| `destination_droplet_ids` | `list` | ❌ | `[]` |
| `destination_tags` | `list` | ❌ | `[]` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "add_outbound_rule",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "firewall_id": "string",
    "protocol": "string",
    "ports": "string",
    "destination_addresses": [],
    "destination_droplet_ids": [],
    "destination_tags": []
  }
}
```

#### `add_tags_to_firewall`
**Description:** Add tags to a firewall

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `firewall_id` | `str` | ✅ | `None` |
| `tags` | `list` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "add_tags_to_firewall",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "firewall_id": "string",
    "tags": []
  }
}
```

#### `block_ip`
**Description:** Block an IP by removing from allowed sources or creating block rule

**Category:** `response`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `firewall_id` | `str` | ✅ | `None` |
| `ip_address` | `str` | ✅ | `None` |
| `direction` | `str` | ❌ | `inbound` |
| `protocol` | `str` | ❌ | `tcp` |
| `ports` | `str` | ❌ | `all` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "block_ip",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "firewall_id": "string",
    "ip_address": "string",
    "direction": "string",
    "protocol": "string",
    "ports": "string"
  }
}
```

#### `create_droplet`
**Description:** Create a droplet

**Category:** `droplet`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |
| `region` | `str` | ✅ | `None` |
| `size` | `str` | ✅ | `None` |
| `image` | `str` | ✅ | `None` |
| `ssh_keys` | `list` | ❌ | `[]` |
| `tags` | `list` | ❌ | `[]` |
| `backups` | `bool` | ❌ | `False` |
| `user_data` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "create_droplet",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string",
    "region": "string",
    "size": "string",
    "image": "string",
    "ssh_keys": [],
    "tags": [],
    "backups": true,
    "user_data": "string"
  }
}
```

#### `create_firewall`
**Description:** Create a new firewall

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |
| `inbound_rules` | `list` | ❌ | `[]` |
| `outbound_rules` | `list` | ❌ | `[]` |
| `droplet_ids` | `list` | ❌ | `[]` |
| `tags` | `list` | ❌ | `[]` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "create_firewall",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string",
    "inbound_rules": [],
    "outbound_rules": [],
    "droplet_ids": [],
    "tags": []
  }
}
```

#### `create_tag`
**Description:** Create a tag

**Category:** `system`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "create_tag",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string"
  }
}
```

#### `delete_droplet`
**Description:** Delete a droplet

**Category:** `droplet`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `droplet_id` | `int` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "delete_droplet",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "droplet_id": 0
  }
}
```

#### `delete_firewall`
**Description:** Delete a firewall

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `firewall_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "delete_firewall",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "firewall_id": "string"
  }
}
```

#### `get_account_info`
**Description:** Get account information

**Category:** `system`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "get_account_info",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `get_bandwidth_usage`
**Description:** Get droplet bandwidth usage

**Category:** `monitoring`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `droplet_id` | `int` | ✅ | `None` |
| `interface` | `str` | ❌ | `public` |
| `direction` | `str` | ❌ | `inbound` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "get_bandwidth_usage",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "droplet_id": 0,
    "interface": "string",
    "direction": "string"
  }
}
```

#### `get_droplet`
**Description:** Get droplet details

**Category:** `droplet`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `droplet_id` | `int` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "get_droplet",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "droplet_id": 0
  }
}
```

#### `get_droplet_action`
**Description:** Get status of a droplet action

**Category:** `droplet`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `droplet_id` | `int` | ✅ | `None` |
| `action_id` | `int` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "get_droplet_action",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "droplet_id": 0,
    "action_id": 0
  }
}
```

#### `get_firewall`
**Description:** Get specific firewall details

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `firewall_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "get_firewall",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "firewall_id": "string"
  }
}
```

#### `list_droplets`
**Description:** List droplets

**Category:** `droplet`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `tag_name` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "list_droplets",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "tag_name": "string"
  }
}
```

#### `list_firewalls`
**Description:** List all firewalls

**Category:** `firewall`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "list_firewalls",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `list_images`
**Description:** List available images

**Category:** `system`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `type_` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "list_images",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "type_": "string"
  }
}
```

#### `list_regions`
**Description:** List available regions

**Category:** `system`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "list_regions",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `list_sizes`
**Description:** List available droplet sizes

**Category:** `system`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "list_sizes",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `list_tags`
**Description:** List tags

**Category:** `system`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "list_tags",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `power_off_droplet`
**Description:** Power off a droplet

**Category:** `droplet`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `droplet_id` | `int` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "power_off_droplet",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "droplet_id": 0
  }
}
```

#### `power_on_droplet`
**Description:** Power on a droplet

**Category:** `droplet`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `droplet_id` | `int` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "power_on_droplet",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "droplet_id": 0
  }
}
```

#### `reboot_droplet`
**Description:** Reboot a droplet

**Category:** `droplet`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `droplet_id` | `int` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "reboot_droplet",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "droplet_id": 0
  }
}
```

#### `remove_droplets_from_firewall`
**Description:** Remove droplets from a firewall

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `firewall_id` | `str` | ✅ | `None` |
| `droplet_ids` | `list` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "remove_droplets_from_firewall",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "firewall_id": "string",
    "droplet_ids": []
  }
}
```

#### `remove_inbound_rule`
**Description:** Remove an inbound rule

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `firewall_id` | `str` | ✅ | `None` |
| `protocol` | `str` | ✅ | `None` |
| `ports` | `str` | ✅ | `None` |
| `source_addresses` | `list` | ❌ | `[]` |
| `source_droplet_ids` | `list` | ❌ | `[]` |
| `source_tags` | `list` | ❌ | `[]` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "remove_inbound_rule",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "firewall_id": "string",
    "protocol": "string",
    "ports": "string",
    "source_addresses": [],
    "source_droplet_ids": [],
    "source_tags": []
  }
}
```

#### `remove_outbound_rule`
**Description:** Remove an outbound rule

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `firewall_id` | `str` | ✅ | `None` |
| `protocol` | `str` | ✅ | `None` |
| `ports` | `str` | ✅ | `None` |
| `destination_addresses` | `list` | ❌ | `[]` |
| `destination_droplet_ids` | `list` | ❌ | `[]` |
| `destination_tags` | `list` | ❌ | `[]` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "remove_outbound_rule",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "firewall_id": "string",
    "protocol": "string",
    "ports": "string",
    "destination_addresses": [],
    "destination_droplet_ids": [],
    "destination_tags": []
  }
}
```

#### `remove_tags_from_firewall`
**Description:** Remove tags from a firewall

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `firewall_id` | `str` | ✅ | `None` |
| `tags` | `list` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "remove_tags_from_firewall",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "firewall_id": "string",
    "tags": []
  }
}
```

#### `take_snapshot`
**Description:** Take a snapshot of a droplet

**Category:** `droplet`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `droplet_id` | `int` | ✅ | `None` |
| `snapshot_name` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "take_snapshot",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "droplet_id": 0,
    "snapshot_name": "string"
  }
}
```

#### `update_firewall`
**Description:** Update a firewall (full replacement)

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `firewall_id` | `str` | ✅ | `None` |
| `name` | `str` | ✅ | `None` |
| `inbound_rules` | `list` | ✅ | `None` |
| `outbound_rules` | `list` | ✅ | `None` |
| `droplet_ids` | `list` | ❌ | `[]` |
| `tags` | `list` | ❌ | `[]` |

**Execution Payload Example:**
```json
{
  "connector": "digitalocean",
  "action": "update_firewall",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "firewall_id": "string",
    "name": "string",
    "inbound_rules": [],
    "outbound_rules": [],
    "droplet_ids": [],
    "tags": []
  }
}
```

---

## 🔌 elastic (v1.0.0)
> Elastic Stack connector covering Elasticsearch v8.x, Kibana Security SIEM, and Fleet.

### Available Actions

#### `add_case_comment`
**Description:** Add a comment to a Kibana case.

**Category:** `cases`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `case_id` | `str` | ✅ | `None` |
| `comment` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "add_case_comment",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "case_id": "string",
    "comment": "string"
  }
}
```

#### `bulk_index`
**Description:** Bulk-index a list of documents into an Elasticsearch index.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `index` | `str` | ✅ | `None` |
| `documents` | `List[Dict[str, Any]]` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "bulk_index",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "index": "string",
    "documents": "..."
  }
}
```

#### `create_case`
**Description:** Create a new case in Kibana.

**Category:** `cases`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `title` | `str` | ✅ | `None` |
| `description` | `str` | ✅ | `None` |
| `tags` | `Optional[List[str]]` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "create_case",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "title": "string",
    "description": "string",
    "tags": "..."
  }
}
```

#### `create_detection_rule`
**Description:** Create a new Kibana detection rule.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `rule` | `Dict[str, Any]` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "create_detection_rule",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "rule": "..."
  }
}
```

#### `create_exception_list`
**Description:** Create a new exception list.

**Category:** `exceptions`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |
| `description` | `str` | ✅ | `None` |
| `type_` | `str` | ❌ | `detection` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "create_exception_list",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string",
    "description": "string",
    "type_": "string"
  }
}
```

#### `create_index`
**Description:** Create a new Elasticsearch index with optional mappings and settings.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `index` | `str` | ✅ | `None` |
| `mappings` | `Optional[Dict[str, Any]]` | ❌ | `None` |
| `settings` | `Optional[Dict[str, Any]]` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "create_index",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "index": "string",
    "mappings": "...",
    "settings": "..."
  }
}
```

#### `delete_cases`
**Description:** Delete one or more Kibana cases.

**Category:** `cases`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `case_ids` | `List[str]` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "delete_cases",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "case_ids": "..."
  }
}
```

#### `delete_detection_rule`
**Description:** Permanently delete a Kibana detection rule by its rule ID.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `rule_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "delete_detection_rule",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "rule_id": "string"
  }
}
```

#### `delete_document`
**Description:** Delete a document from Elasticsearch by ID.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `index` | `str` | ✅ | `None` |
| `doc_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "delete_document",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "index": "string",
    "doc_id": "string"
  }
}
```

#### `delete_index`
**Description:** Delete an Elasticsearch index.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `index` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "delete_index",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "index": "string"
  }
}
```

#### `disable_detection_rule`
**Description:** Disable a Kibana detection rule by its rule ID.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `rule_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "disable_detection_rule",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "rule_id": "string"
  }
}
```

#### `enable_detection_rule`
**Description:** Enable a Kibana detection rule by its rule ID.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `rule_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "enable_detection_rule",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "rule_id": "string"
  }
}
```

#### `get_agent_info`
**Description:** Retrieve detailed information about a specific Fleet agent.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "get_agent_info",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string"
  }
}
```

#### `get_agents`
**Description:** List Elastic Fleet agents with optional status filtering.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `page` | `int` | ❌ | `1` |
| `per_page` | `int` | ❌ | `20` |
| `status` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "get_agents",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "page": 0,
    "per_page": 0,
    "status": "string"
  }
}
```

#### `get_alert`
**Description:** Retrieve a single Kibana alert by its ID.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `alert_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "get_alert",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "alert_id": "string"
  }
}
```

#### `get_alerts`
**Description:** Retrieve security alerts from Kibana's alerts index.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `index` | `str` | ❌ | `.alerts-security.alerts-default` |
| `size` | `int` | ❌ | `20` |
| `status` | `str` | ❌ | `open` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "get_alerts",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "index": "string",
    "size": 0,
    "status": "string"
  }
}
```

#### `get_case`
**Description:** Get a specific Kibana case by ID.

**Category:** `cases`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `case_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "get_case",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "case_id": "string"
  }
}
```

#### `get_cases`
**Description:** Get a list of Kibana cases.

**Category:** `cases`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `page` | `int` | ❌ | `1` |
| `per_page` | `int` | ❌ | `20` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "get_cases",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "page": 0,
    "per_page": 0
  }
}
```

#### `get_detection_rules`
**Description:** List Kibana detection rules with pagination and optional filter.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `page` | `int` | ❌ | `1` |
| `per_page` | `int` | ❌ | `20` |
| `filter` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "get_detection_rules",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "page": 0,
    "per_page": 0,
    "filter": "string"
  }
}
```

#### `get_document`
**Description:** Retrieve a document from Elasticsearch by ID.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `index` | `str` | ✅ | `None` |
| `doc_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "get_document",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "index": "string",
    "doc_id": "string"
  }
}
```

#### `get_exception_lists`
**Description:** List exception lists.

**Category:** `exceptions`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `page` | `int` | ❌ | `1` |
| `per_page` | `int` | ❌ | `20` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "get_exception_lists",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "page": 0,
    "per_page": 0
  }
}
```

#### `get_index_stats`
**Description:** Retrieve statistics for one or more Elasticsearch indices.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `index` | `str` | ❌ | `*` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "get_index_stats",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "index": "string"
  }
}
```

#### `index_document`
**Description:** Index (create or update) a document in Elasticsearch.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `index` | `str` | ✅ | `None` |
| `document` | `Dict[str, Any]` | ✅ | `None` |
| `doc_id` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "index_document",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "index": "string",
    "document": "...",
    "doc_id": "string"
  }
}
```

#### `isolate_host`
**Description:** Network-isolate an endpoint via the Fleet agent actions API.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |
| `comment` | `str` | ❌ | `Isolated by SOAR` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "isolate_host",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string",
    "comment": "string"
  }
}
```

#### `run_esql_query`
**Description:** Execute an ES|QL query via the /_query endpoint.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `query` | `str` | ✅ | `None` |
| `filter` | `Optional[Dict[str, Any]]` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "run_esql_query",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "query": "string",
    "filter": "..."
  }
}
```

#### `run_osquery`
**Description:** Execute a live Osquery SQL query against a Fleet agent.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |
| `query` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "run_osquery",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string",
    "query": "string"
  }
}
```

#### `search`
**Description:** Search documents in an Elasticsearch index.

**Category:** `data`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `index` | `str` | ✅ | `None` |
| `query` | `Dict[str, Any]` | ✅ | `None` |
| `size` | `int` | ❌ | `10` |
| `from_` | `int` | ❌ | `0` |
| `sort` | `Optional[List[Any]]` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "search",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "index": "string",
    "query": "...",
    "size": 0,
    "from_": 0,
    "sort": "..."
  }
}
```

#### `unisolate_host`
**Description:** Release a previously isolated endpoint via the Fleet agent actions API.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |
| `comment` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "unisolate_host",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string",
    "comment": "string"
  }
}
```

#### `update_alert_status`
**Description:** Update the workflow status of one or more Kibana security alerts.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `alert_ids` | `List[str]` | ✅ | `None` |
| `status` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "elastic",
  "action": "update_alert_status",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "alert_ids": "...",
    "status": "string"
  }
}
```

---

## 🔌 email (v1.0.0)
> Multi-provider email connector (SMTP, SendGrid, Mailgun) for sending alerts and reports.

### Available Actions

#### `get_send_status`
**Description:** Check delivery status of message

**Category:** `communication`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `message_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "email",
  "action": "get_send_status",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "message_id": "string"
  }
}
```

#### `send_alert_email`
**Description:** Send a formatted HTML security alert

**Category:** `alerting`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `to` | `list` | ✅ | `None` |
| `alert_title` | `str` | ✅ | `None` |
| `severity` | `str` | ✅ | `None` |
| `description` | `str` | ✅ | `None` |
| `affected_host` | `str` | ❌ | `None` |
| `alert_id` | `str` | ❌ | `None` |
| `from_email` | `str` | ❌ | `None` |
| `additional_fields` | `dict` | ❌ | `{}` |

**Execution Payload Example:**
```json
{
  "connector": "email",
  "action": "send_alert_email",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "to": [],
    "alert_title": "string",
    "severity": "string",
    "description": "string",
    "affected_host": "string",
    "alert_id": "string",
    "from_email": "string",
    "additional_fields": {}
  }
}
```

#### `send_bulk_email`
**Description:** Send bulk email with template variables

**Category:** `communication`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `recipients` | `list` | ✅ | `None` |
| `subject` | `str` | ✅ | `None` |
| `body_template` | `str` | ✅ | `None` |
| `html` | `bool` | ❌ | `True` |

**Execution Payload Example:**
```json
{
  "connector": "email",
  "action": "send_bulk_email",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "recipients": [],
    "subject": "string",
    "body_template": "string",
    "html": true
  }
}
```

#### `send_email`
**Description:** Send an email

**Category:** `communication`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `to` | `list` | ✅ | `None` |
| `subject` | `str` | ✅ | `None` |
| `body` | `str` | ✅ | `None` |
| `from_email` | `str` | ❌ | `None` |
| `cc` | `list` | ❌ | `[]` |
| `bcc` | `list` | ❌ | `[]` |
| `html` | `bool` | ❌ | `True` |
| `attachments` | `list` | ❌ | `[]` |

**Execution Payload Example:**
```json
{
  "connector": "email",
  "action": "send_email",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "to": [],
    "subject": "string",
    "body": "string",
    "from_email": "string",
    "cc": [],
    "bcc": [],
    "html": true,
    "attachments": []
  }
}
```

#### `send_report_email`
**Description:** Send a report via email

**Category:** `reporting`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `to` | `list` | ✅ | `None` |
| `report_title` | `str` | ✅ | `None` |
| `report_html` | `str` | ❌ | `None` |
| `report_file_path` | `str` | ❌ | `None` |
| `from_email` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "email",
  "action": "send_report_email",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "to": [],
    "report_title": "string",
    "report_html": "string",
    "report_file_path": "string",
    "from_email": "string"
  }
}
```

#### `verify_email_address`
**Description:** Verify email address format and MX record

**Category:** `utilities`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `email` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "email",
  "action": "verify_email_address",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "email": "string"
  }
}
```

---

## 🔌 fortigate (v1.0.0)
> FortiGate (FortiOS REST API) connector for firewall management.

### Available Actions

#### `add_member_to_group`
**Description:** Add a member to an address group

**Category:** `objects`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `group_name` | `str` | ✅ | `None` |
| `member_name` | `str` | ✅ | `None` |
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "add_member_to_group",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "group_name": "string",
    "member_name": "string",
    "vdom": "string"
  }
}
```

#### `backup_config`
**Description:** Backup FortiGate configuration

**Category:** `system`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `destination` | `str` | ❌ | `file` |
| `vdom` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "backup_config",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "destination": "string",
    "vdom": "string"
  }
}
```

#### `block_ip`
**Description:** Block an IP address quickly

**Category:** `response`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `ip` | `str` | ✅ | `None` |
| `comment` | `str` | ❌ | `Blocked by SOAR` |
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "block_ip",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "ip": "string",
    "comment": "string",
    "vdom": "string"
  }
}
```

#### `create_address_group`
**Description:** Create an address group

**Category:** `objects`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |
| `members` | `list` | ✅ | `None` |
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "create_address_group",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string",
    "members": [],
    "vdom": "string"
  }
}
```

#### `create_address_object`
**Description:** Create an address object

**Category:** `objects`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |
| `subnet` | `str` | ❌ | `None` |
| `fqdn` | `str` | ❌ | `None` |
| `type_` | `str` | ❌ | `ipmask` |
| `comment` | `str` | ❌ | `None` |
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "create_address_object",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string",
    "subnet": "string",
    "fqdn": "string",
    "type_": "string",
    "comment": "string",
    "vdom": "string"
  }
}
```

#### `create_firewall_policy`
**Description:** Create a firewall policy

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `policy` | `dict` | ✅ | `None` |
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "create_firewall_policy",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "policy": {},
    "vdom": "string"
  }
}
```

#### `delete_address_object`
**Description:** Delete an address object

**Category:** `objects`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "delete_address_object",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string",
    "vdom": "string"
  }
}
```

#### `delete_firewall_policy`
**Description:** Delete a firewall policy

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `policy_id` | `int` | ✅ | `None` |
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "delete_firewall_policy",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "policy_id": 0,
    "vdom": "string"
  }
}
```

#### `get_active_sessions`
**Description:** Get active firewall sessions

**Category:** `monitoring`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `vdom` | `str` | ❌ | `root` |
| `count` | `int` | ❌ | `100` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "get_active_sessions",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "vdom": "string",
    "count": 0
  }
}
```

#### `get_address_groups`
**Description:** Get address groups

**Category:** `objects`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "get_address_groups",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "vdom": "string"
  }
}
```

#### `get_address_object`
**Description:** Get specific address object

**Category:** `objects`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "get_address_object",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string",
    "vdom": "string"
  }
}
```

#### `get_address_objects`
**Description:** Get address objects

**Category:** `objects`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "get_address_objects",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "vdom": "string"
  }
}
```

#### `get_firewall_policies`
**Description:** Get firewall policies

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "get_firewall_policies",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "vdom": "string"
  }
}
```

#### `get_firewall_policy`
**Description:** Get a specific firewall policy

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `policy_id` | `int` | ✅ | `None` |
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "get_firewall_policy",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "policy_id": 0,
    "vdom": "string"
  }
}
```

#### `get_interface_stats`
**Description:** Get interface statistics

**Category:** `monitoring`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "get_interface_stats",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `get_ips_statistics`
**Description:** Get IPS anomaly statistics

**Category:** `monitoring`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "get_ips_statistics",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `get_service_groups`
**Description:** Get service groups

**Category:** `objects`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "get_service_groups",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "vdom": "string"
  }
}
```

#### `get_services`
**Description:** Get service objects

**Category:** `objects`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "get_services",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "vdom": "string"
  }
}
```

#### `get_system_status`
**Description:** Get system status

**Category:** `system`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "get_system_status",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `get_threat_log`
**Description:** Get threat logs

**Category:** `monitoring`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `rows` | `int` | ❌ | `100` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "get_threat_log",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "rows": 0
  }
}
```

#### `get_vpn_ipsec_tunnels`
**Description:** Get IPsec VPN tunnels

**Category:** `vpn`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "get_vpn_ipsec_tunnels",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "vdom": "string"
  }
}
```

#### `get_vpn_ssl_sessions`
**Description:** Get SSL VPN sessions

**Category:** `vpn`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "get_vpn_ssl_sessions",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `get_vpn_status`
**Description:** Get IPsec VPN status

**Category:** `vpn`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "get_vpn_status",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `move_firewall_policy`
**Description:** Move a firewall policy

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `policy_id` | `int` | ✅ | `None` |
| `position` | `str` | ✅ | `None` |
| `neighbour` | `int` | ✅ | `None` |
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "move_firewall_policy",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "policy_id": 0,
    "position": "string",
    "neighbour": 0,
    "vdom": "string"
  }
}
```

#### `run_diagnose_command`
**Description:** Run CLI diagnose command

**Category:** `system`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `command` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "run_diagnose_command",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "command": "string"
  }
}
```

#### `unblock_ip`
**Description:** Unblock an IP address

**Category:** `response`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `ip` | `str` | ✅ | `None` |
| `policy_id` | `int` | ❌ | `0` |
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "unblock_ip",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "ip": "string",
    "policy_id": 0,
    "vdom": "string"
  }
}
```

#### `update_firewall_policy`
**Description:** Update a firewall policy

**Category:** `firewall`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `policy_id` | `int` | ✅ | `None` |
| `updates` | `dict` | ✅ | `None` |
| `vdom` | `str` | ❌ | `root` |

**Execution Payload Example:**
```json
{
  "connector": "fortigate",
  "action": "update_firewall_policy",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "policy_id": 0,
    "updates": {},
    "vdom": "string"
  }
}
```

---

## 🔌 http_request (v1.0.0)
> Make arbitrary HTTP/S requests to any external API or webhook.

### Available Actions

#### `make_request`
**Description:** Send an HTTP request

**Category:** `network`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `url` | `str` | ✅ | `None` |
| `method` | `str` | ❌ | `GET` |
| `headers` | `dict` | ❌ | `{}` |
| `query_params` | `dict` | ❌ | `{}` |
| `payload` | `dict` | ❌ | `{}` |
| `content_type` | `str` | ❌ | `application/json` |
| `timeout` | `int` | ❌ | `30` |

**Execution Payload Example:**
```json
{
  "connector": "http_request",
  "action": "make_request",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "url": "string",
    "method": "string",
    "headers": {},
    "query_params": {},
    "payload": {},
    "content_type": "string",
    "timeout": 0
  }
}
```

---

## 🔌 misp (v1.0.0)
> MISP (Malware Information Sharing Platform) Threat Intelligence Connector

### Available Actions

#### `add_attribute`
**Description:** Add a new attribute to an existing event.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `event_id` | `str` | ✅ | `None` |
| `type` | `str` | ✅ | `None` |
| `value` | `str` | ✅ | `None` |
| `category` | `str` | ❌ | `Network activity` |
| `to_ids` | `bool` | ❌ | `True` |
| `comment` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "misp",
  "action": "add_attribute",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "event_id": "string",
    "type": "string",
    "value": "string",
    "category": "string",
    "to_ids": true,
    "comment": "string"
  }
}
```

#### `add_event`
**Description:** Create a new event.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `info` | `str` | ✅ | `None` |
| `distribution` | `str` | ❌ | `0` |
| `threat_level_id` | `str` | ❌ | `1` |
| `analysis` | `str` | ❌ | `0` |

**Execution Payload Example:**
```json
{
  "connector": "misp",
  "action": "add_event",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "info": "string",
    "distribution": "string",
    "threat_level_id": "string",
    "analysis": "string"
  }
}
```

#### `get_event`
**Description:** Retrieve a specific event by ID.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `event_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "misp",
  "action": "get_event",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "event_id": "string"
  }
}
```

#### `search_attributes`
**Description:** Search for MISP attributes.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `limit` | `int` | ❌ | `10` |
| `value` | `str` | ❌ | `None` |
| `type` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "misp",
  "action": "search_attributes",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "limit": 0,
    "value": "string",
    "type": "string"
  }
}
```

#### `search_events`
**Description:** Search for MISP events.

**Category:** `general`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `limit` | `int` | ❌ | `10` |
| `value` | `str` | ❌ | `None` |
| `type` | `str` | ❌ | `None` |
| `tags` | `Optional` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "misp",
  "action": "search_events",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "limit": 0,
    "value": "string",
    "type": "string",
    "tags": "..."
  }
}
```

---

## 🔌 msgraph (v1.0.0)
> Microsoft Graph connector for Teams and Outlook

*No actions exposed yet.*

## 🔌 opencti (v1.0.0)
> OpenCTI GraphQL API connector for Threat Intelligence.

### Available Actions

#### `create_indicator`
**Description:** Create an indicator

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |
| `pattern` | `str` | ✅ | `None` |
| `pattern_type` | `str` | ❌ | `stix` |
| `indicator_types` | `list` | ❌ | `['malicious-activity']` |
| `valid_from` | `str` | ❌ | `None` |
| `valid_until` | `str` | ❌ | `None` |
| `confidence` | `int` | ❌ | `75` |
| `description` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "create_indicator",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string",
    "pattern": "string",
    "pattern_type": "string",
    "indicator_types": [],
    "valid_from": "string",
    "valid_until": "string",
    "confidence": 0,
    "description": "string"
  }
}
```

#### `create_malware`
**Description:** Create malware

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |
| `description` | `str` | ❌ | `None` |
| `malware_types` | `list` | ❌ | `[]` |
| `is_family` | `bool` | ❌ | `False` |
| `aliases` | `list` | ❌ | `[]` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "create_malware",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string",
    "description": "string",
    "malware_types": [],
    "is_family": true,
    "aliases": []
  }
}
```

#### `create_observable`
**Description:** Create an observable

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `type_` | `str` | ✅ | `None` |
| `value` | `str` | ✅ | `None` |
| `description` | `str` | ❌ | `None` |
| `score` | `int` | ❌ | `50` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "create_observable",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "type_": "string",
    "value": "string",
    "description": "string",
    "score": 0
  }
}
```

#### `create_relationship`
**Description:** Create relationship between entities

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `from_id` | `str` | ✅ | `None` |
| `to_id` | `str` | ✅ | `None` |
| `relationship_type` | `str` | ✅ | `None` |
| `description` | `str` | ❌ | `None` |
| `confidence` | `int` | ❌ | `75` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "create_relationship",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "from_id": "string",
    "to_id": "string",
    "relationship_type": "string",
    "description": "string",
    "confidence": 0
  }
}
```

#### `create_report`
**Description:** Create a report

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |
| `description` | `str` | ❌ | `None` |
| `published` | `str` | ❌ | `None` |
| `report_types` | `list` | ❌ | `['threat-report']` |
| `confidence` | `int` | ❌ | `75` |
| `object_refs` | `list` | ❌ | `[]` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "create_report",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string",
    "description": "string",
    "published": "string",
    "report_types": [],
    "confidence": 0,
    "object_refs": []
  }
}
```

#### `create_threat_actor`
**Description:** Create a threat actor

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |
| `description` | `str` | ❌ | `None` |
| `threat_actor_types` | `list` | ❌ | `[]` |
| `sophistication` | `str` | ❌ | `None` |
| `resource_level` | `str` | ❌ | `None` |
| `aliases` | `list` | ❌ | `[]` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "create_threat_actor",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string",
    "description": "string",
    "threat_actor_types": [],
    "sophistication": "string",
    "resource_level": "string",
    "aliases": []
  }
}
```

#### `delete_indicator`
**Description:** Delete an indicator

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `indicator_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "delete_indicator",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "indicator_id": "string"
  }
}
```

#### `enrich_observable`
**Description:** Enrich an observable

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `observable_id` | `str` | ✅ | `None` |
| `connector_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "enrich_observable",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "observable_id": "string",
    "connector_id": "string"
  }
}
```

#### `get_indicator`
**Description:** Get an indicator by ID

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `indicator_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "get_indicator",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "indicator_id": "string"
  }
}
```

#### `get_malware`
**Description:** Get malware by ID

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `malware_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "get_malware",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "malware_id": "string"
  }
}
```

#### `get_relationships`
**Description:** Get relationships for entity

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `entity_id` | `str` | ✅ | `None` |
| `relationship_type` | `str` | ❌ | `None` |
| `limit` | `int` | ❌ | `20` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "get_relationships",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "entity_id": "string",
    "relationship_type": "string",
    "limit": 0
  }
}
```

#### `get_report`
**Description:** Get report by ID

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `report_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "get_report",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "report_id": "string"
  }
}
```

#### `get_reports`
**Description:** Get reports

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `limit` | `int` | ❌ | `20` |
| `search` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "get_reports",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "limit": 0,
    "search": "string"
  }
}
```

#### `get_statistics`
**Description:** Get platform statistics

**Category:** `system`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "get_statistics",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `get_threat_actor`
**Description:** Get threat actor by ID

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `threat_actor_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "get_threat_actor",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "threat_actor_id": "string"
  }
}
```

#### `import_stix_bundle`
**Description:** Import STIX bundle

**Category:** `system`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `bundle` | `dict` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "import_stix_bundle",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "bundle": {}
  }
}
```

#### `search_all`
**Description:** Global search

**Category:** `system`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `search` | `str` | ✅ | `None` |
| `limit` | `int` | ❌ | `20` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "search_all",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "search": "string",
    "limit": 0
  }
}
```

#### `search_attack_patterns`
**Description:** Search attack patterns (MITRE)

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `search` | `str` | ❌ | `None` |
| `limit` | `int` | ❌ | `20` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "search_attack_patterns",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "search": "string",
    "limit": 0
  }
}
```

#### `search_campaigns`
**Description:** Search campaigns

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `search` | `str` | ❌ | `None` |
| `limit` | `int` | ❌ | `20` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "search_campaigns",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "search": "string",
    "limit": 0
  }
}
```

#### `search_indicators`
**Description:** Search indicators

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `search` | `str` | ❌ | `None` |
| `type_` | `str` | ❌ | `None` |
| `limit` | `int` | ❌ | `20` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "search_indicators",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "search": "string",
    "type_": "string",
    "limit": 0
  }
}
```

#### `search_malware`
**Description:** Search malware

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `search` | `str` | ❌ | `None` |
| `limit` | `int` | ❌ | `20` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "search_malware",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "search": "string",
    "limit": 0
  }
}
```

#### `search_observables`
**Description:** Search observables

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `search` | `str` | ❌ | `None` |
| `type_` | `str` | ❌ | `None` |
| `limit` | `int` | ❌ | `20` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "search_observables",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "search": "string",
    "type_": "string",
    "limit": 0
  }
}
```

#### `search_threat_actors`
**Description:** Search threat actors

**Category:** `cti`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `search` | `str` | ❌ | `None` |
| `limit` | `int` | ❌ | `20` |

**Execution Payload Example:**
```json
{
  "connector": "opencti",
  "action": "search_threat_actors",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "search": "string",
    "limit": 0
  }
}
```

---

## 🔌 slack (v1.0.0)
> Slack Web API connector for sending messages and automating channels.

### Available Actions

#### `add_reaction`
**Description:** Add emoji reaction to message

**Category:** `communication`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |
| `ts` | `str` | ✅ | `None` |
| `reaction` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "add_reaction",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string",
    "ts": "string",
    "reaction": "string"
  }
}
```

#### `archive_channel`
**Description:** Archive a channel

**Category:** `channels`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "archive_channel",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string"
  }
}
```

#### `create_channel`
**Description:** Create a new channel

**Category:** `channels`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |
| `is_private` | `bool` | ❌ | `False` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "create_channel",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string",
    "is_private": true
  }
}
```

#### `create_incident_thread`
**Description:** Create an incident thread

**Category:** `incident`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |
| `incident_id` | `str` | ✅ | `None` |
| `title` | `str` | ✅ | `None` |
| `severity` | `str` | ✅ | `None` |
| `assignee` | `str` | ❌ | `None` |
| `description` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "create_incident_thread",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string",
    "incident_id": "string",
    "title": "string",
    "severity": "string",
    "assignee": "string",
    "description": "string"
  }
}
```

#### `delete_message`
**Description:** Delete a message

**Category:** `communication`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |
| `ts` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "delete_message",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string",
    "ts": "string"
  }
}
```

#### `get_channel_history`
**Description:** Get channel message history

**Category:** `history`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |
| `limit` | `int` | ❌ | `20` |
| `oldest` | `str` | ❌ | `None` |
| `latest` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "get_channel_history",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string",
    "limit": 0,
    "oldest": "string",
    "latest": "string"
  }
}
```

#### `get_channel_info`
**Description:** Get info about a channel

**Category:** `channels`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "get_channel_info",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string"
  }
}
```

#### `get_thread_replies`
**Description:** Get replies in a thread

**Category:** `history`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |
| `thread_ts` | `str` | ✅ | `None` |
| `limit` | `int` | ❌ | `20` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "get_thread_replies",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string",
    "thread_ts": "string",
    "limit": 0
  }
}
```

#### `get_user_by_email`
**Description:** Lookup user by email

**Category:** `users`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `email` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "get_user_by_email",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "email": "string"
  }
}
```

#### `get_user_info`
**Description:** Get user info

**Category:** `users`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `user_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "get_user_info",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "user_id": "string"
  }
}
```

#### `get_workspace_info`
**Description:** Get workspace info

**Category:** `system`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "get_workspace_info",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `invite_users`
**Description:** Invite users to channel

**Category:** `channels`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |
| `user_ids` | `list` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "invite_users",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string",
    "user_ids": []
  }
}
```

#### `kick_user`
**Description:** Kick a user from a channel

**Category:** `channels`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |
| `user_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "kick_user",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string",
    "user_id": "string"
  }
}
```

#### `list_channels`
**Description:** List channels

**Category:** `channels`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `types` | `str` | ❌ | `public_channel,private_channel` |
| `limit` | `int` | ❌ | `100` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "list_channels",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "types": "string",
    "limit": 0
  }
}
```

#### `list_users`
**Description:** List all users

**Category:** `users`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `limit` | `int` | ❌ | `200` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "list_users",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "limit": 0
  }
}
```

#### `pin_message`
**Description:** Pin a message

**Category:** `channels`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |
| `ts` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "pin_message",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string",
    "ts": "string"
  }
}
```

#### `remove_reaction`
**Description:** Remove emoji reaction

**Category:** `communication`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |
| `ts` | `str` | ✅ | `None` |
| `reaction` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "remove_reaction",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string",
    "ts": "string",
    "reaction": "string"
  }
}
```

#### `send_alert_message`
**Description:** Send a formatted alert message

**Category:** `alerting`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |
| `title` | `str` | ✅ | `None` |
| `severity` | `str` | ✅ | `None` |
| `description` | `str` | ✅ | `None` |
| `fields` | `dict` | ❌ | `{}` |
| `actions` | `list` | ❌ | `[]` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "send_alert_message",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string",
    "title": "string",
    "severity": "string",
    "description": "string",
    "fields": {},
    "actions": []
  }
}
```

#### `send_message`
**Description:** Send a message to a channel

**Category:** `communication`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |
| `text` | `str` | ✅ | `None` |
| `blocks` | `list` | ❌ | `[]` |
| `thread_ts` | `str` | ❌ | `None` |
| `mrkdwn` | `bool` | ❌ | `True` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "send_message",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string",
    "text": "string",
    "blocks": [],
    "thread_ts": "string",
    "mrkdwn": true
  }
}
```

#### `set_channel_purpose`
**Description:** Set channel purpose

**Category:** `channels`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |
| `purpose` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "set_channel_purpose",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string",
    "purpose": "string"
  }
}
```

#### `set_channel_topic`
**Description:** Set channel topic

**Category:** `channels`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |
| `topic` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "set_channel_topic",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string",
    "topic": "string"
  }
}
```

#### `set_status`
**Description:** Set user status

**Category:** `users`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `status_text` | `str` | ✅ | `None` |
| `status_emoji` | `str` | ✅ | `None` |
| `status_expiration` | `int` | ❌ | `0` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "set_status",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "status_text": "string",
    "status_emoji": "string",
    "status_expiration": 0
  }
}
```

#### `unpin_message`
**Description:** Unpin a message

**Category:** `channels`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |
| `ts` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "unpin_message",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string",
    "ts": "string"
  }
}
```

#### `update_message`
**Description:** Update an existing message

**Category:** `communication`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channel` | `str` | ✅ | `None` |
| `ts` | `str` | ✅ | `None` |
| `text` | `str` | ❌ | `None` |
| `blocks` | `list` | ❌ | `[]` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "update_message",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channel": "string",
    "ts": "string",
    "text": "string",
    "blocks": []
  }
}
```

#### `upload_file`
**Description:** Upload a file to Slack

**Category:** `files`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `channels` | `list` | ✅ | `None` |
| `content` | `str` | ❌ | `None` |
| `filename` | `str` | ❌ | `report.txt` |
| `filetype` | `str` | ❌ | `text` |
| `title` | `str` | ❌ | `None` |
| `file_path` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "slack",
  "action": "upload_file",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "channels": [],
    "content": "string",
    "filename": "string",
    "filetype": "string",
    "title": "string",
    "file_path": "string"
  }
}
```

---

## 🔌 soar_utils (v1.0.0)
> Built-in SOAR utilities for local data processing, cryptography, and IOC extraction.

### Available Actions

#### `base64_decode`
**Description:** Decode Base64 to text

**Category:** `cryptography`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `encoded_text` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "soar_utils",
  "action": "base64_decode",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "encoded_text": "string"
  }
}
```

#### `base64_encode`
**Description:** Encode text to Base64

**Category:** `cryptography`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `text` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "soar_utils",
  "action": "base64_encode",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "text": "string"
  }
}
```

#### `calculate_hash`
**Description:** Calculate hash for a string

**Category:** `cryptography`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `text` | `str` | ✅ | `None` |
| `algorithm` | `str` | ❌ | `sha256` |

**Execution Payload Example:**
```json
{
  "connector": "soar_utils",
  "action": "calculate_hash",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "text": "string",
    "algorithm": "string"
  }
}
```

#### `defang_ioc`
**Description:** Defang an IOC to make it safe to click/copy

**Category:** `utilities`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `ioc` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "soar_utils",
  "action": "defang_ioc",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "ioc": "string"
  }
}
```

#### `extract_iocs`
**Description:** Extract IOCs (IPs, Domains, Hashes) from text

**Category:** `utilities`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `text` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "soar_utils",
  "action": "extract_iocs",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "text": "string"
  }
}
```

#### `parse_user_agent`
**Description:** Parse a User-Agent string

**Category:** `parsing`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `user_agent` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "soar_utils",
  "action": "parse_user_agent",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "user_agent": "string"
  }
}
```

#### `refang_ioc`
**Description:** Refang an IOC to its original form

**Category:** `utilities`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `defanged_ioc` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "soar_utils",
  "action": "refang_ioc",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "defanged_ioc": "string"
  }
}
```

---

## 🔌 splunk (v1.0.0)
> Splunk REST API and HTTP Event Collector (HEC) connector.

### Available Actions

#### `cancel_search_job`
**Description:** Cancel a search job

**Category:** `search`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `job_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "cancel_search_job",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "job_id": "string"
  }
}
```

#### `create_correlation_search`
**Description:** Create ES correlation search

**Category:** `es`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |
| `search` | `str` | ✅ | `None` |
| `description` | `str` | ❌ | `None` |
| `cron_schedule` | `str` | ❌ | `*/5 * * * *` |
| `severity` | `str` | ❌ | `high` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "create_correlation_search",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string",
    "search": "string",
    "description": "string",
    "cron_schedule": "string",
    "severity": "string"
  }
}
```

#### `create_index`
**Description:** Create an index

**Category:** `data`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `index_name` | `str` | ✅ | `None` |
| `max_hot_buckets` | `int` | ❌ | `3` |
| `max_total_data_size_mb` | `int` | ❌ | `500000` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "create_index",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "index_name": "string",
    "max_hot_buckets": 0,
    "max_total_data_size_mb": 0
  }
}
```

#### `create_saved_search`
**Description:** Create a saved search

**Category:** `search`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |
| `query` | `str` | ✅ | `None` |
| `description` | `str` | ❌ | `None` |
| `cron_schedule` | `str` | ❌ | `None` |
| `is_scheduled` | `bool` | ❌ | `False` |
| `alert_type` | `str` | ❌ | `always` |
| `alert_actions` | `list` | ❌ | `[]` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "create_saved_search",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string",
    "query": "string",
    "description": "string",
    "cron_schedule": "string",
    "is_scheduled": true,
    "alert_type": "string",
    "alert_actions": []
  }
}
```

#### `delete_saved_search`
**Description:** Delete a saved search

**Category:** `search`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "delete_saved_search",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string"
  }
}
```

#### `get_field_summary`
**Description:** Get field summary

**Category:** `data`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `index` | `str` | ✅ | `None` |
| `field` | `str` | ✅ | `None` |
| `earliest_time` | `str` | ❌ | `-24h` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "get_field_summary",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "index": "string",
    "field": "string",
    "earliest_time": "string"
  }
}
```

#### `get_index_info`
**Description:** Get index info

**Category:** `data`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `index_name` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "get_index_info",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "index_name": "string"
  }
}
```

#### `get_license_usage`
**Description:** Get license usage

**Category:** `system`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "get_license_usage",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `get_notable_events`
**Description:** Get notable events from Splunk ES

**Category:** `es`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `earliest_time` | `str` | ❌ | `-24h` |
| `latest_time` | `str` | ❌ | `now` |
| `urgency` | `str` | ❌ | `None` |
| `owner` | `str` | ❌ | `None` |
| `limit` | `int` | ❌ | `20` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "get_notable_events",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "earliest_time": "string",
    "latest_time": "string",
    "urgency": "string",
    "owner": "string",
    "limit": 0
  }
}
```

#### `get_search_job`
**Description:** Get search job status

**Category:** `search`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `job_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "get_search_job",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "job_id": "string"
  }
}
```

#### `get_search_results`
**Description:** Get search job results

**Category:** `search`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `job_id` | `str` | ✅ | `None` |
| `count` | `int` | ❌ | `100` |
| `offset` | `int` | ❌ | `0` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "get_search_results",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "job_id": "string",
    "count": 0,
    "offset": 0
  }
}
```

#### `get_server_info`
**Description:** Get server info

**Category:** `system`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "get_server_info",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `list_apps`
**Description:** List installed apps

**Category:** `system`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "list_apps",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `list_dashboards`
**Description:** List dashboards

**Category:** `ui`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `app` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "list_dashboards",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "app": "string"
  }
}
```

#### `list_indexes`
**Description:** List all indexes

**Category:** `data`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "list_indexes",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `list_reports`
**Description:** List scheduled reports

**Category:** `reports`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "list_reports",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `list_saved_searches`
**Description:** List saved searches

**Category:** `search`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `app` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "list_saved_searches",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "app": "string"
  }
}
```

#### `run_saved_search`
**Description:** Dispatch a saved search

**Category:** `search`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `saved_search_name` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "run_saved_search",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "saved_search_name": "string"
  }
}
```

#### `search`
**Description:** Run a Splunk search job

**Category:** `search`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `query` | `str` | ✅ | `None` |
| `earliest_time` | `str` | ❌ | `-24h` |
| `latest_time` | `str` | ❌ | `now` |
| `max_results` | `int` | ❌ | `100` |
| `mode` | `str` | ❌ | `normal` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "search",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "query": "string",
    "earliest_time": "string",
    "latest_time": "string",
    "max_results": 0,
    "mode": "string"
  }
}
```

#### `search_oneshot`
**Description:** Run a blocking oneshot search

**Category:** `search`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `query` | `str` | ✅ | `None` |
| `earliest_time` | `str` | ❌ | `-1h` |
| `latest_time` | `str` | ❌ | `now` |
| `max_results` | `int` | ❌ | `100` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "search_oneshot",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "query": "string",
    "earliest_time": "string",
    "latest_time": "string",
    "max_results": 0
  }
}
```

#### `send_event_hec`
**Description:** Send single event to HEC

**Category:** `ingest`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `event` | `dict` | ✅ | `None` |
| `index` | `str` | ❌ | `None` |
| `source` | `str` | ❌ | `soar-connector` |
| `sourcetype` | `str` | ❌ | `json` |
| `host` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "send_event_hec",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "event": {},
    "index": "string",
    "source": "string",
    "sourcetype": "string",
    "host": "string"
  }
}
```

#### `send_events_batch_hec`
**Description:** Send batch of events to HEC

**Category:** `ingest`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `events` | `list` | ✅ | `None` |
| `index` | `str` | ❌ | `None` |
| `sourcetype` | `str` | ❌ | `json` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "send_events_batch_hec",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "events": [],
    "index": "string",
    "sourcetype": "string"
  }
}
```

#### `send_raw_hec`
**Description:** Send raw string to HEC

**Category:** `ingest`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `raw_text` | `str` | ✅ | `None` |
| `index` | `str` | ❌ | `None` |
| `sourcetype` | `str` | ❌ | `_raw` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "send_raw_hec",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "raw_text": "string",
    "index": "string",
    "sourcetype": "string"
  }
}
```

#### `update_notable_status`
**Description:** Update notable event status

**Category:** `es`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `event_ids` | `list` | ✅ | `None` |
| `status` | `str` | ✅ | `None` |
| `comment` | `str` | ❌ | `None` |
| `owner` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "splunk",
  "action": "update_notable_status",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "event_ids": [],
    "status": "string",
    "comment": "string",
    "owner": "string"
  }
}
```

---

## 🔌 virustotal (v1.0.0)
> VirusTotal v3 API connector for threat intelligence and scanning.

### Available Actions

#### `add_comment`
**Description:** Add a comment to an object

**Category:** `community`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `object_type` | `str` | ✅ | `None` |
| `object_id` | `str` | ✅ | `None` |
| `comment` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "virustotal",
  "action": "add_comment",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "object_type": "string",
    "object_id": "string",
    "comment": "string"
  }
}
```

#### `create_livehunt_ruleset`
**Description:** Create a YARA LiveHunt ruleset (Enterprise)

**Category:** `hunting`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | `str` | ✅ | `None` |
| `rules` | `str` | ✅ | `None` |
| `enabled` | `bool` | ❌ | `True` |

**Execution Payload Example:**
```json
{
  "connector": "virustotal",
  "action": "create_livehunt_ruleset",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "name": "string",
    "rules": "string",
    "enabled": true
  }
}
```

#### `download_file`
**Description:** Download a file sample (Enterprise API)

**Category:** `file`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `hash` | `str` | ✅ | `None` |
| `output_path` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "virustotal",
  "action": "download_file",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "hash": "string",
    "output_path": "string"
  }
}
```

#### `get_analysis`
**Description:** Get analysis status

**Category:** `scanning`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `analysis_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "virustotal",
  "action": "get_analysis",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "analysis_id": "string"
  }
}
```

#### `get_comments`
**Description:** Get comments for an object

**Category:** `community`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `object_type` | `str` | ✅ | `None` |
| `object_id` | `str` | ✅ | `None` |
| `limit` | `int` | ❌ | `10` |

**Execution Payload Example:**
```json
{
  "connector": "virustotal",
  "action": "get_comments",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "object_type": "string",
    "object_id": "string",
    "limit": 0
  }
}
```

#### `get_domain_report`
**Description:** Get full domain report

**Category:** `intelligence`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `domain` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "virustotal",
  "action": "get_domain_report",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "domain": "string"
  }
}
```

#### `get_file_behaviour`
**Description:** Get sandbox behaviour report for a file hash

**Category:** `intelligence`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `hash` | `str` | ✅ | `None` |
| `sandbox` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "virustotal",
  "action": "get_file_behaviour",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "hash": "string",
    "sandbox": "string"
  }
}
```

#### `get_file_report`
**Description:** Get full file report by hash

**Category:** `intelligence`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `resource` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "virustotal",
  "action": "get_file_report",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "resource": "string"
  }
}
```

#### `get_ip_report`
**Description:** Get full IP address report

**Category:** `intelligence`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `ip` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "virustotal",
  "action": "get_ip_report",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "ip": "string"
  }
}
```

#### `get_livehunt_rulesets`
**Description:** Get YARA LiveHunt rulesets (Enterprise)

**Category:** `hunting`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `limit` | `int` | ❌ | `10` |

**Execution Payload Example:**
```json
{
  "connector": "virustotal",
  "action": "get_livehunt_rulesets",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "limit": 0
  }
}
```

#### `get_object_relationships`
**Description:** Get related entities for a given object

**Category:** `intelligence`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `object_type` | `str` | ✅ | `None` |
| `object_id` | `str` | ✅ | `None` |
| `relationship` | `str` | ✅ | `None` |
| `limit` | `int` | ❌ | `10` |

**Execution Payload Example:**
```json
{
  "connector": "virustotal",
  "action": "get_object_relationships",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "object_type": "string",
    "object_id": "string",
    "relationship": "string",
    "limit": 0
  }
}
```

#### `get_url_report`
**Description:** Get full URL report

**Category:** `intelligence`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `url` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "virustotal",
  "action": "get_url_report",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "url": "string"
  }
}
```

#### `scan_file`
**Description:** Upload a file for scanning by VirusTotal

**Category:** `scanning`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `file_path` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "virustotal",
  "action": "scan_file",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "file_path": "string"
  }
}
```

#### `scan_url`
**Description:** Submit a URL for scanning by VirusTotal

**Category:** `scanning`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `url` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "virustotal",
  "action": "scan_url",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "url": "string"
  }
}
```

#### `search`
**Description:** VT Intelligence search (Enterprise)

**Category:** `search`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `query` | `str` | ✅ | `None` |
| `limit` | `int` | ❌ | `20` |
| `cursor` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "virustotal",
  "action": "search",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "query": "string",
    "limit": 0,
    "cursor": "string"
  }
}
```

---

## 🔌 wazuh (v1.0.0)
> Wazuh REST API v4.x connector for SIEM and XDR.

### Available Actions

#### `add_agent_to_group`
**Description:** Add an agent to a group

**Category:** `inventory`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |
| `group_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "add_agent_to_group",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string",
    "group_id": "string"
  }
}
```

#### `create_group`
**Description:** Create an agent group

**Category:** `inventory`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `group_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "create_group",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "group_id": "string"
  }
}
```

#### `delete_agent`
**Description:** Delete an agent

**Category:** `inventory`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |
| `purge` | `bool` | ❌ | `False` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "delete_agent",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string",
    "purge": true
  }
}
```

#### `get_agent_info`
**Description:** Get detailed agent info

**Category:** `inventory`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_agent_info",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string"
  }
}
```

#### `get_agent_key`
**Description:** Get agent registration key

**Category:** `inventory`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_agent_key",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string"
  }
}
```

#### `get_agents`
**Description:** Get a list of agents

**Category:** `inventory`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `limit` | `int` | ❌ | `20` |
| `offset` | `int` | ❌ | `0` |
| `status` | `str` | ❌ | `None` |
| `name` | `str` | ❌ | `None` |
| `os_platform` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_agents",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "limit": 0,
    "offset": 0,
    "status": "string",
    "name": "string",
    "os_platform": "string"
  }
}
```

#### `get_alert`
**Description:** Get a specific alert by ID

**Category:** `monitoring`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `alert_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_alert",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "alert_id": "string"
  }
}
```

#### `get_alerts`
**Description:** Get security alerts

**Category:** `monitoring`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `limit` | `int` | ❌ | `20` |
| `offset` | `int` | ❌ | `0` |
| `level` | `str` | ❌ | `None` |
| `rule_id` | `str` | ❌ | `None` |
| `agent_id` | `str` | ❌ | `None` |
| `sort` | `str` | ❌ | `-timestamp` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_alerts",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "limit": 0,
    "offset": 0,
    "level": "string",
    "rule_id": "string",
    "agent_id": "string",
    "sort": "string"
  }
}
```

#### `get_cluster_nodes`
**Description:** Get cluster nodes list

**Category:** `inventory`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_cluster_nodes",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `get_decoders`
**Description:** Get Wazuh decoders

**Category:** `configuration`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `limit` | `int` | ❌ | `20` |
| `offset` | `int` | ❌ | `0` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_decoders",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "limit": 0,
    "offset": 0
  }
}
```

#### `get_fim_events`
**Description:** Get File Integrity Monitoring events

**Category:** `monitoring`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |
| `limit` | `int` | ❌ | `20` |
| `file` | `str` | ❌ | `None` |
| `type_` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_fim_events",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string",
    "limit": 0,
    "file": "string",
    "type_": "string"
  }
}
```

#### `get_groups`
**Description:** Get list of agent groups

**Category:** `inventory`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `limit` | `int` | ❌ | `20` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_groups",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "limit": 0
  }
}
```

#### `get_logs`
**Description:** Get Wazuh manager logs

**Category:** `monitoring`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `limit` | `int` | ❌ | `20` |
| `offset` | `int` | ❌ | `0` |
| `level` | `str` | ❌ | `None` |
| `tag` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_logs",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "limit": 0,
    "offset": 0,
    "level": "string",
    "tag": "string"
  }
}
```

#### `get_manager_info`
**Description:** Get Wazuh manager info

**Category:** `inventory`

*No parameters required.*

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_manager_info",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {}
}
```

#### `get_rootcheck_results`
**Description:** Get rootcheck results

**Category:** `monitoring`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_rootcheck_results",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string"
  }
}
```

#### `get_rules`
**Description:** Get Wazuh detection rules

**Category:** `configuration`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `limit` | `int` | ❌ | `20` |
| `offset` | `int` | ❌ | `0` |
| `status` | `str` | ❌ | `enabled` |
| `level` | `str` | ❌ | `None` |
| `group` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_rules",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "limit": 0,
    "offset": 0,
    "status": "string",
    "level": "string",
    "group": "string"
  }
}
```

#### `get_sca_checks`
**Description:** Get SCA checks for a policy

**Category:** `monitoring`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |
| `policy_id` | `str` | ✅ | `None` |
| `result` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_sca_checks",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string",
    "policy_id": "string",
    "result": "string"
  }
}
```

#### `get_sca_results`
**Description:** Get Security Configuration Assessment results

**Category:** `monitoring`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |
| `limit` | `int` | ❌ | `20` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_sca_results",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string",
    "limit": 0
  }
}
```

#### `get_statistics`
**Description:** Get Wazuh manager statistics

**Category:** `monitoring`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `component` | `str` | ❌ | `logcollector` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_statistics",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "component": "string"
  }
}
```

#### `get_vulnerabilities`
**Description:** Get agent vulnerabilities

**Category:** `monitoring`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |
| `limit` | `int` | ❌ | `20` |
| `severity` | `str` | ❌ | `None` |
| `cve` | `str` | ❌ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "get_vulnerabilities",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string",
    "limit": 0,
    "severity": "string",
    "cve": "string"
  }
}
```

#### `remove_agent_from_group`
**Description:** Remove an agent from a group

**Category:** `inventory`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |
| `group_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "remove_agent_from_group",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string",
    "group_id": "string"
  }
}
```

#### `restart_agent`
**Description:** Restart a specific agent

**Category:** `response`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "restart_agent",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string"
  }
}
```

#### `restart_agents_in_group`
**Description:** Restart all agents in a group

**Category:** `response`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `group_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "restart_agents_in_group",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "group_id": "string"
  }
}
```

#### `run_active_response`
**Description:** Run active response command

**Category:** `response`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |
| `command` | `str` | ✅ | `None` |
| `arguments` | `list` | ❌ | `[]` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "run_active_response",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string",
    "command": "string",
    "arguments": []
  }
}
```

#### `run_rootcheck`
**Description:** Run rootcheck on an agent

**Category:** `response`

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| `agent_id` | `str` | ✅ | `None` |

**Execution Payload Example:**
```json
{
  "connector": "wazuh",
  "action": "run_rootcheck",
  "config": {
    "auth_type": "...",
    "auth_config": {}
  },
  "params": {
    "agent_id": "string"
  }
}
```

---

## 🔌 webhook (v1.0.0)
> Generic Webhook Trigger to receive events from any external system.

*No actions exposed yet.*

