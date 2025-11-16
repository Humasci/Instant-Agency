# Centralized Control Panel & Agent Linking Guide

This guide explains how all 15 agents are linked together, how to monitor them, and how to use the centralized control panel.

## 📊 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CENTRALIZED CONTROL PANEL                         │
│                  (Real-time Monitoring Dashboard)                    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CENTRAL ACTIVITY LOGGER                           │
│  ┌──────────────┬────────────────┬──────────────┬─────────────────┐ │
│  │ Activity Log │ Agent Status   │ Metrics DB   │ Message Queue   │ │
│  │  (All Events)│ (Real-time)    │ (Time-series)│ (Inter-agent)   │ │
│  └──────────────┴────────────────┴──────────────┴─────────────────┘ │
└───────────────────────────┬──────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  ORCHESTRATOR   │  │   15 AGENTS     │  │  WORKFLOWS      │
│   (Routing &    │◄─┤   (Execution)   │─►│  (Multi-step)   │
│  Coordination)  │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
              ┌───────────────────────┐
              │   SHARED CONTEXT      │
              │   (Customer Data,     │
              │    Workflow State)    │
              └───────────────────────┘
```

## 🔗 How Agents Are Linked

### 1. **Centralized Activity Logger**
All 15 agents log their activities to a **unified database** (`central_activity.db`):

**Schema**:
- `agent_activities` - Every interaction, input/output, success/failure
- `agent_status` - Real-time status of each agent
- `agent_metrics` - Performance metrics over time
- `inter_agent_messages` - Agent-to-agent communication
- `system_events` - Alerts, warnings, errors

**Location**: `agents/central_logger.py`

### 2. **Orchestrator-Based Linking**
The **Orchestrator Agent** (`phase3_orchestrator`) coordinates multi-agent workflows:

```python
# Example: Lead Nurture Workflow
Orchestrator receives request
  ├─► Classify Intent (phase2_intent_classifier)
  ├─► Qualify Lead (phase1_prospect)
  ├─► Generate Pitch (phase2_sales_pitch)
  ├─► Send Email (phase2_email_personalizer)
  └─► Log to Central Logger
```

### 3. **Inter-Agent Messaging**
Agents can send messages to each other through the Central Logger:

```python
from central_logger import get_central_logger

logger = get_central_logger()

# Agent A sends message to Agent B
logger.send_inter_agent_message(
    from_agent="phase3_orchestrator",
    to_agent="phase2_sales_pitch",
    message_type="generate_pitch",
    payload={'prospect_id': '123'},
    workflow_id="wf_001"
)

# Agent B retrieves messages
messages = logger.get_unprocessed_messages("phase2_sales_pitch")
```

### 4. **Shared Context Store**
The Orchestrator maintains a **shared context** for workflows:
- Customer data
- Journey stage
- Previous interactions
- Escalation triggers

This context is passed between agents in a workflow.

---

## 🖥️ Control Panel API Endpoints

### **Dashboard (Main Overview)**
```bash
GET /control-panel/dashboard
```

**Response**:
```json
{
  "success": true,
  "dashboard": {
    "agent_statuses": [
      {
        "agent_name": "phase1_prospect",
        "status": "active",
        "total_interactions": 1247,
        "success_rate": 0.87,
        "avg_response_time": 234.5
      }
    ],
    "statistics_24h": {
      "total_interactions": 8126,
      "successful_interactions": 7150,
      "success_rate": 88.0,
      "avg_response_time_ms": 1234.5,
      "error_count": 976,
      "active_workflows": 45
    },
    "system_health": {
      "total_agents": 15,
      "active_agents": 15,
      "error_count_24h": 976,
      "avg_success_rate": 88.0
    },
    "recent_events": [...],
    "critical_events": [...],
    "real_time_metrics": {...}
  }
}
```

---

### **All Agents Status**
```bash
GET /control-panel/agents
```

Returns status and metrics for all 15 agents.

---

### **Single Agent Detail**
```bash
GET /control-panel/agent/{agent_name}?limit=100
```

**Example**:
```bash
curl http://localhost:8000/control-panel/agent/phase2_sales_pitch
```

**Response**:
```json
{
  "success": true,
  "agent_name": "phase2_sales_pitch",
  "status": {
    "status": "active",
    "total_interactions": 892,
    "success_rate": 0.79,
    "avg_response_time": 5678.2
  },
  "real_time_metrics": {
    "total_interactions": 892,
    "successful": 705,
    "failed": 187,
    "avg_response_time": 5678.2,
    "last_activity": "2025-01-15T14:30:00"
  },
  "recent_activities": [
    {
      "timestamp": "2025-01-15T14:30:00",
      "event_type": "interaction",
      "input_data": {...},
      "output_data": {...},
      "success": true,
      "response_time_ms": 5234.1
    }
  ]
}
```

---

### **Activity Log (All Agents)**
```bash
GET /control-panel/activities?agent_name=phase1_prospect&limit=100&offset=0
```

**Filters**:
- `agent_name` - Filter by specific agent
- `workflow_id` - Filter by workflow
- `limit` - Number of results
- `offset` - Pagination

---

### **Workflow Trace (Cross-Agent Journey)**
```bash
GET /control-panel/workflow/{workflow_id}
```

**Example**:
```bash
curl http://localhost:8000/control-panel/workflow/wf_001
```

**Response**:
```json
{
  "success": true,
  "workflow_trace": {
    "workflow_id": "wf_001",
    "start_time": "2025-01-15T14:00:00",
    "end_time": "2025-01-15T14:05:23",
    "total_duration_ms": 323000,
    "agents_involved": [
      "phase3_orchestrator",
      "phase2_intent_classifier",
      "phase1_prospect",
      "phase2_sales_pitch",
      "phase2_email_personalizer"
    ],
    "total_steps": 5,
    "successful_steps": 5,
    "success_rate": 1.0,
    "timeline": [
      {
        "timestamp": "2025-01-15T14:00:00",
        "agent_name": "phase3_orchestrator",
        "event_type": "interaction",
        "success": true
      },
      {
        "timestamp": "2025-01-15T14:00:02",
        "agent_name": "phase2_intent_classifier",
        "event_type": "interaction",
        "success": true
      }
    ],
    "inter_agent_messages": 4
  }
}
```

This shows the **complete journey** of a workflow across multiple agents!

---

### **System Events & Alerts**
```bash
GET /control-panel/events?severity=critical&unacknowledged_only=true
```

**Severity Levels**: `info`, `warning`, `error`, `critical`

---

### **Statistics**
```bash
GET /control-panel/statistics?time_period=24h
```

**Time Periods**: `1h`, `24h`, `7d`

---

### **Inter-Agent Messages**
```bash
GET /control-panel/inter-agent-messages?agent_name=phase2_sales_pitch
```

Shows communication between agents.

---

## 🎯 Example Use Cases

### Use Case 1: Monitor All Agents
```bash
# Get dashboard
curl http://localhost:8000/control-panel/dashboard

# View key metrics:
# - 15 agents status
# - Total interactions: 8,126
# - Success rate: 88%
# - Active workflows: 45
```

### Use Case 2: Debug a Failed Workflow
```bash
# 1. Get workflow trace
curl http://localhost:8000/control-panel/workflow/wf_123

# 2. See which agent failed
# Response shows: phase2_sales_pitch failed at step 3

# 3. Get agent details
curl http://localhost:8000/control-panel/agent/phase2_sales_pitch

# 4. View recent activities to see errors
curl http://localhost:8000/control-panel/activities?agent_name=phase2_sales_pitch&limit=10
```

### Use Case 3: Track Customer Journey
```bash
# Get all activities for a workflow
curl http://localhost:8000/control-panel/workflow/wf_customer_001

# See complete timeline:
# 14:00:00 - Orchestrator started workflow
# 14:00:02 - Intent classified as "demo"
# 14:00:05 - Lead qualified (score: 85)
# 14:00:12 - Sales pitch generated
# 14:00:15 - Email sent
# Total duration: 15 seconds
# Agents involved: 5
```

### Use Case 4: Monitor Agent Performance
```bash
# Get statistics
curl http://localhost:8000/control-panel/statistics?time_period=24h

# By agent breakdown:
{
  "phase1_prospect": {
    "total": 1247,
    "successful": 1085,
    "success_rate": 0.87
  },
  "phase2_sales_pitch": {
    "total": 892,
    "successful": 705,
    "success_rate": 0.79  // ⚠️ Needs attention
  }
}
```

### Use Case 5: View Inter-Agent Communication
```bash
# See messages between agents
curl http://localhost:8000/control-panel/inter-agent-messages

# Response:
{
  "all_messages": [
    {
      "from_agent": "phase3_orchestrator",
      "to_agent": "phase2_sales_pitch",
      "message_type": "generate_pitch",
      "processed": true
    },
    {
      "from_agent": "phase2_sales_pitch",
      "to_agent": "phase2_email_personalizer",
      "message_type": "send_email",
      "processed": false  // ⚠️ Not yet processed
    }
  ]
}
```

---

## 📈 Real-Time Monitoring

The control panel provides **real-time metrics** through in-memory caching:

```python
# Real-time metrics (updated on every interaction)
{
  "phase1_prospect": {
    "total_interactions": 1247,
    "successful": 1085,
    "failed": 162,
    "avg_response_time": 234.5,
    "last_activity": "2025-01-15T14:30:00"
  }
}
```

These metrics are **instantly updated** without database queries.

---

## 🎨 Building a Custom Dashboard

### Simple HTML Dashboard

Create `dashboard.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>AI Agent Control Panel</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        .agent-card {
            border: 1px solid #ccc;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .status-active { background: #d4edda; }
        .status-error { background: #f8d7da; }
        .metric { display: inline-block; margin-right: 20px; }
    </style>
</head>
<body>
    <h1>🤖 AI Agent Control Panel</h1>
    <div id="dashboard"></div>

    <script>
        async function loadDashboard() {
            const response = await fetch('http://localhost:8000/control-panel/dashboard');
            const data = await response.json();

            const dashboard = data.dashboard;
            let html = '<h2>System Health</h2>';
            html += `<p>Total Agents: ${dashboard.system_health.total_agents}</p>`;
            html += `<p>Active: ${dashboard.system_health.active_agents}</p>`;
            html += `<p>Success Rate: ${dashboard.statistics_24h.success_rate.toFixed(1)}%</p>`;
            html += `<p>Total Interactions (24h): ${dashboard.statistics_24h.total_interactions}</p>`;

            html += '<h2>Agents</h2>';
            dashboard.agent_statuses.forEach(agent => {
                const statusClass = agent.status === 'active' ? 'status-active' : 'status-error';
                html += `
                    <div class="agent-card ${statusClass}">
                        <h3>${agent.agent_name}</h3>
                        <div class="metric">Status: ${agent.status}</div>
                        <div class="metric">Interactions: ${agent.total_interactions}</div>
                        <div class="metric">Success Rate: ${(agent.success_rate * 100).toFixed(1)}%</div>
                        <div class="metric">Avg Response: ${agent.avg_response_time.toFixed(1)}ms</div>
                    </div>
                `;
            });

            document.getElementById('dashboard').innerHTML = html;
        }

        // Load dashboard
        loadDashboard();

        // Refresh every 10 seconds
        setInterval(loadDashboard, 10000);
    </script>
</body>
</html>
```

Open in browser: `file:///path/to/dashboard.html`

---

## 🔧 Integration Examples

### Example 1: Python Monitoring Script

```python
import requests
import time

def monitor_agents():
    """Monitor agents and alert on failures"""
    while True:
        # Get dashboard
        response = requests.get('http://localhost:8000/control-panel/dashboard')
        data = response.json()['dashboard']

        # Check for errors
        for agent in data['agent_statuses']:
            if agent['success_rate'] < 0.80:
                print(f"⚠️  ALERT: {agent['agent_name']} success rate: {agent['success_rate']:.1%}")

        # Check critical events
        if data['critical_events']:
            print(f"🚨 CRITICAL: {len(data['critical_events'])} critical events!")
            for event in data['critical_events'][:3]:
                print(f"   - {event['message']}")

        time.sleep(60)  # Check every minute

monitor_agents()
```

### Example 2: Slack Alerts

```python
import requests

def send_slack_alert(webhook_url, message):
    requests.post(webhook_url, json={'text': message})

# Monitor and alert to Slack
response = requests.get('http://localhost:8000/control-panel/events?severity=critical')
events = response.json()['events']

for event in events:
    if not event['acknowledged']:
        send_slack_alert(
            'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
            f"🚨 Critical Event: {event['message']}"
        )
```

### Example 3: Export to CSV

```python
import requests
import csv

# Get activities
response = requests.get('http://localhost:8000/control-panel/activities?limit=1000')
activities = response.json()['activities']

# Export to CSV
with open('agent_activities.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'agent_name', 'event_type', 'success'])
    writer.writeheader()
    for activity in activities:
        writer.writerow({
            'timestamp': activity['timestamp'],
            'agent_name': activity['agent_name'],
            'event_type': activity['event_type'],
            'success': activity['success']
        })
```

---

## 🚀 Quick Start

### 1. Start the Agent Service
```bash
cd agents
python main.py
```

### 2. Access Control Panel
```bash
# Dashboard
curl http://localhost:8000/control-panel/dashboard | jq

# All agents
curl http://localhost:8000/control-panel/agents | jq

# Specific agent
curl http://localhost:8000/control-panel/agent/phase1_prospect | jq
```

### 3. View in Browser
Open: http://localhost:8000/docs

Navigate to **Control Panel** section to see all monitoring endpoints.

---

## 📊 Metrics Tracked

### Per-Agent Metrics
- **Total interactions** - Count of all requests
- **Success rate** - % of successful interactions
- **Average response time** - Mean latency in ms
- **Error count** - Number of failures
- **Current load** - Active requests
- **Uptime** - Seconds since agent started

### System-Wide Metrics
- **Total agents** - 15
- **Active agents** - Currently processing
- **Total interactions (24h)** - Volume
- **Average success rate** - Across all agents
- **Active workflows** - Multi-agent workflows in progress
- **Error count (24h)** - System-wide failures

### Workflow Metrics
- **Total duration** - End-to-end time
- **Agents involved** - Which agents participated
- **Success rate** - % of successful steps
- **Inter-agent messages** - Communication count

---

## 🎯 Benefits of Centralized Control

### ✅ **Unified Monitoring**
- Single dashboard for all 15 agents
- Real-time status updates
- Historical trend analysis

### ✅ **Cross-Agent Visibility**
- Track workflows across multiple agents
- See agent-to-agent communication
- Understand complete customer journeys

### ✅ **Proactive Alerting**
- Critical events surfaced immediately
- Warning thresholds configurable
- Integration with Slack/email/PagerDuty

### ✅ **Performance Optimization**
- Identify slow agents
- Track success rates
- Find bottlenecks in workflows

### ✅ **Debugging & Troubleshooting**
- Complete workflow traces
- Input/output logging
- Error tracking with context

---

## 🔐 Security Note

The control panel endpoints provide **read-only** access to logs and metrics. In production:
- Add authentication (API keys, OAuth)
- Implement role-based access control
- Limit sensitive data exposure
- Add rate limiting

---

**Control Panel Complete!** All 15 agents are now linked, logged, and monitorable through a centralized system. 🎉

**Next Steps**: Build custom visualizations, set up alerts, integrate with your monitoring stack (Grafana, Datadog, etc.)
