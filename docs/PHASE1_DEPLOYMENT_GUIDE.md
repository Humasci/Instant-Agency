# Phase 1: Complete Deployment & Development Guide

This guide covers everything needed to deploy Phase 1: Core stack, CRM integration, AI agents, n8n workflows, and production setup.

---

## Table of Contents

1. [Quick Start (10 minutes)](#quick-start)
2. [Docker Deployment (Production)](#docker-deployment)
3. [AI Agent Configuration](#ai-agent-configuration)
4. [CRM Integration & Data Schemas](#crm-integration)
5. [n8n Workflow Templates](#n8n-workflows)
6. [Analytics & Monitoring](#analytics-monitoring)
7. [Testing Framework](#testing-framework)
8. [Escalation & Human-in-the-Loop](#escalation-workflows)
9. [Deployment Scripts](#deployment-scripts)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Option 1: Local Development (No Docker)

```bash
# 1. Clone repository
git clone <your-repo>
cd Instant-Agency

# 2. Set up Python environment
cd agents
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp ../.env.example ../.env
# Edit .env and set:
#   - HUGGINGFACE_API_KEY (required)
#   - ATTIO_API_KEY (required)

# 4. Start agents
python main.py

# ✅ Agents running at http://localhost:8000
# ✅ API docs at http://localhost:8000/docs
```

### Option 2: Docker Deployment (Production)

```bash
# 1. Configure environment
cp .env.example .env
nano .env  # Set all required API keys

# 2. Start all services
docker-compose up -d

# 3. Verify services
docker-compose ps

# ✅ n8n: http://localhost:5678
# ✅ Agents: http://localhost:8000
# ✅ Metabase: http://localhost:3000
# ✅ Grafana: http://localhost:3001
```

---

## Docker Deployment

### Architecture

```
┌─────────────────────────────────────────┐
│  User / Website Forms                   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  n8n Workflow Automation                │
│  Port: 5678                             │
│  - Webhooks                             │
│  - Scheduled tasks                      │
│  - API orchestration                    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  AI Agent Service                       │
│  Port: 8000                             │
│  - 20 AI agents                         │
│  - REST API                             │
│  - Control panel                        │
└───┬─────────────────────────┬───────────┘
    │                         │
    ▼                         ▼
┌──────────────┐      ┌──────────────────┐
│  PostgreSQL  │      │  Redis Cache     │
│  Port: 5432  │      │  Port: 6379      │
└──────────────┘      └──────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Metabase Analytics                     │
│  Port: 3000                             │
│  - Dashboards                           │
│  - Reports                              │
└─────────────────────────────────────────┘
```

### Services Overview

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| **agent-service** | 8000 | AI agents API | Required |
| **n8n** | 5678 | Workflow automation | Required |
| **postgres** | 5432 | Database | Required |
| **redis** | 6379 | Cache & queue | Required |
| **metabase** | 3000 | Analytics | Optional |
| **prometheus** | 9090 | Monitoring | Optional |
| **grafana** | 3001 | Dashboards | Optional |

### Start Services

```bash
# Start core services only
docker-compose up -d agent-service n8n postgres redis

# Start all services (including monitoring)
docker-compose --profile monitoring up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f agent-service

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Environment Variables

**Required:**
```bash
# API Keys
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxx
ATTIO_API_KEY=sk_xxxxxxxxxxxxx

# Database
POSTGRES_PASSWORD=change_to_secure_password
REDIS_PASSWORD=change_to_secure_password

# n8n
N8N_PASSWORD=change_to_secure_password
```

**Optional (Phase 4 features):**
```bash
# Digital Avatars
DID_API_KEY=your_did_key
HEYGEN_API_KEY=your_heygen_key

# Voice
ELEVENLABS_API_KEY=your_elevenlabs_key
AZURE_SPEECH_KEY=your_azure_key
AZURE_SPEECH_REGION=eastus
```

---

## AI Agent Configuration

### Agent Structure

```
agents/
├── base_agent.py              # Base class for all agents
├── main.py                    # FastAPI server
│
├── Phase 1 (Basic)
│   ├── phase1_prospect_agent.py      # Lead qualification
│   └── phase1_faq_chatbot.py         # FAQ responses
│
├── Phase 2 (Advanced)
│   ├── phase2_sales_pitch_agent.py   # Sales pitches
│   ├── phase2_content_writer_agent.py # Content generation
│   ├── phase2_intent_classifier_agent.py # Intent detection
│   ├── phase2_email_personalizer_agent.py # Email personalization
│   └── phase2_social_media_agent.py  # Social media posts
│
├── Phase 3 (Orchestration)
│   ├── phase3_orchestrator_agent.py  # Multi-agent coordination
│   ├── phase3_rag_research_agent.py  # Research with RAG
│   ├── phase3_sales_strategist_agent.py # Sales strategy
│   ├── phase3_marketing_campaign_agent.py # Campaign planning
│   ├── phase3_customer_success_agent.py # CS management
│   └── phase3_analytics_agent.py     # Analytics & reporting
│
└── Phase 4 (Scale & Optimization)
    ├── phase4_digital_avatar_agent.py # Video avatars
    ├── phase4_voice_conversation_agent.py # Voice interactions
    ├── phase4_multilingual_agent.py  # Translation
    ├── phase4_realtime_conversation_agent.py # Real-time chat
    └── phase4_advanced_personalization_agent.py # Personalization
```

### Agent Configuration Files

**Base Configuration** (`agents/config/base.yaml`):
```yaml
agent:
  name: "Base Agent"
  version: "1.0.0"
  department: "operations"

huggingface:
  api_url: "https://api-inference.huggingface.co/models"
  default_model: "mistralai/Mistral-7B-Instruct-v0.2"
  timeout: 30

cache:
  enabled: true
  ttl: 3600  # 1 hour

monitoring:
  track_metrics: true
  log_level: "info"
```

### Creating Custom Agents

**1. Create agent file:**
```python
# agents/custom_my_agent.py
from base_agent import BaseAgent
from typing import Dict, Any

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="my_custom_agent",
            agent_type="custom",
            model_name="gpt-neo-2.7B"
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return result"""
        try:
            # Your custom logic here
            result = self._do_something(input_data)

            return {
                'success': True,
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
```

**2. Register in main.py:**
```python
# Import
from custom_my_agent import MyCustomAgent

# Initialize
agents['my_custom'] = MyCustomAgent()

# Add endpoint
@app.post("/custom/my-agent")
async def my_custom_endpoint(data: Dict[str, Any]):
    return await process_with_agent('my_custom', data)
```

---

## CRM Integration

### Attio CRM Data Schema

**People (Leads & Customers):**
```json
{
  "id": "person_abc123",
  "attributes": {
    "email_addresses": ["john@example.com"],
    "name": "John Doe",
    "job_title": "CEO",
    "phone_numbers": ["+1-555-1234"],
    "tags": ["lead", "hot", "ai_qualified"],
    "ai_score": 8.5,
    "qualification_status": "hot",
    "lead_source": "website",
    "last_interaction": "2024-01-15T10:30:00Z"
  },
  "relationships": {
    "company": "company_xyz789"
  }
}
```

**Companies:**
```json
{
  "id": "company_xyz789",
  "attributes": {
    "name": "Acme Corp",
    "domains": ["acme.com"],
    "industry": "Technology",
    "employee_count": 50,
    "tags": ["prospect", "enterprise"]
  }
}
```

**Notes:**
```json
{
  "id": "note_123456",
  "parent_object": "people",
  "parent_record_id": "person_abc123",
  "title": "AI Qualification Analysis",
  "content": {
    "format": "plaintext",
    "content": "Score: 8.5/10\nStatus: Hot\nSentiment: Positive"
  }
}
```

### Custom Attio Attributes

**Setup in Attio:**
1. Go to Settings → Workspace → Attributes
2. Create custom attributes:

| Attribute Name | Type | Description |
|---------------|------|-------------|
| `ai_score` | Number | AI qualification score (0-10) |
| `qualification_status` | Select | hot, warm, cold |
| `lead_source` | Text | Where lead came from |
| `sentiment_score` | Number | Sentiment analysis (-1 to 1) |
| `last_ai_check` | Date | Last AI analysis |
| `interaction_count` | Number | Total interactions |

### Integration Usage

```python
from integrations.crm.attio_integration import AttioCRMIntegration

# Initialize
crm = AttioCRMIntegration()

# Create person from lead form
person = crm.create_person({
    'email': 'john@example.com',
    'first_name': 'John',
    'last_name': 'Doe',
    'job_title': 'CEO',
    'tags': ['lead', 'hot'],
    'custom_attributes': {
        'ai_score': 8.5,
        'qualification_status': 'hot'
    }
})

# Add note with AI analysis
crm.create_note({
    'parent_object': 'people',
    'parent_record_id': person['id'],
    'title': 'AI Qualification',
    'content': 'High-value lead identified...'
})

# Create follow-up task
crm.create_task({
    'content': 'Call John Doe - hot lead',
    'deadline': '2024-01-20',
    'linked_records': [
        {'object': 'people', 'record_id': person['id']}
    ]
})
```

---

## n8n Workflows

### Available Templates

```
workflows/
├── 01_sales_lead_qualification.json     # Lead capture → AI → CRM
├── 02_marketing_content_pipeline.json   # Content generation & distribution
├── 03_customer_success_monitoring.json  # Health checks & interventions
└── N8N_INTEGRATION_GUIDE.md            # Setup instructions
```

### Import Workflows

**Via n8n UI:**
1. Open n8n: `http://localhost:5678`
2. Login with credentials from `.env`
3. Click "Workflows" → "Import from File"
4. Select JSON file from `workflows/`
5. Click "Import"
6. Configure credentials
7. Activate workflow

**Via CLI:**
```bash
# Copy to n8n container
docker cp workflows/01_sales_lead_qualification.json instant-agency-n8n:/workflows/

# Import via n8n CLI (inside container)
docker exec instant-agency-n8n n8n import:workflow --input=/workflows/01_sales_lead_qualification.json
```

### Workflow Variables

**Set in n8n Environment Variables:**
```bash
# Settings → Variables
AGENT_API_URL=http://agent-service:8000
ATTIO_API_KEY=sk_xxxxxxxxxxxxx
GOOGLE_SHEET_ID=your_sheet_id
WORDPRESS_WORKSPACE=your_workspace
```

### Creating Custom Workflows

**Template Structure:**
```json
{
  "name": "My Custom Workflow",
  "nodes": [
    {
      "name": "Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "my-webhook"
      },
      "position": [250, 300]
    },
    {
      "name": "AI Agent",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.AGENT_API_URL}}/phase1/qualify-lead",
        "method": "POST",
        "sendBody": true,
        "jsonBody": "={{$json}}"
      },
      "position": [450, 300]
    }
  ],
  "connections": {
    "Trigger": {
      "main": [[{"node": "AI Agent", "type": "main", "index": 0}]]
    }
  }
}
```

---

## Analytics & Monitoring

### Metabase Setup

**1. Initial Setup:**
```bash
# Access Metabase
open http://localhost:3000

# First time:
# 1. Create admin account
# 2. Connect to PostgreSQL database
#    Host: postgres
#    Port: 5432
#    Database: instant_agency
#    User: instant_agency
#    Password: (from .env)
```

**2. Create Dashboards:**

**Lead Performance Dashboard:**
- Total leads (this month)
- Qualification rate (hot/warm/cold)
- Average AI score
- Conversion funnel
- Lead source breakdown

**Agent Performance Dashboard:**
- API calls per agent
- Average response time
- Success rate
- Error rate
- Cache hit rate

**Customer Health Dashboard:**
- Total customers
- Health score distribution
- At-risk customers
- Upsell opportunities
- Churn rate

### Grafana Setup (Optional)

**1. Configure Prometheus:**
```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'agent-service'
    static_configs:
      - targets: ['agent-service:8000']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
```

**2. Access Grafana:**
```bash
open http://localhost:3001
# Login: admin / (from .env)
```

**3. Add Data Sources:**
- Prometheus: http://prometheus:9090
- PostgreSQL: postgres:5432

### Control Panel API

**Built-in monitoring endpoints:**

```bash
# System dashboard
curl http://localhost:8000/control-panel/dashboard

# All agents status
curl http://localhost:8000/control-panel/agents

# Specific agent details
curl http://localhost:8000/control-panel/agent/phase1_prospect

# Recent activities
curl http://localhost:8000/control-panel/activities?limit=100

# Workflow trace
curl http://localhost:8000/control-panel/workflow/workflow_123

# System events
curl http://localhost:8000/control-panel/events?severity=critical
```

---

## Testing Framework

### Automated Tests

**Run all tests:**
```bash
# Phase 1-3 agents
python scripts/test_phase3_agents.py

# Phase 4 agents
python scripts/test_phase4_agents.py

# Attio integration
python integrations/crm/attio_integration.py

# API endpoints
pytest tests/test_api.py
```

### Manual Testing

**1. Test AI Agent:**
```bash
curl -X POST http://localhost:8000/phase1/qualify-lead \
  -H "Content-Type: application/json" \
  -d '{
    "lead_name": "Test Lead",
    "lead_email": "test@example.com",
    "company": "Test Corp",
    "lead_message": "Very interested in your AI platform!"
  }'
```

**2. Test CRM Integration:**
```bash
curl -X POST http://localhost:8000/phase1/qualify-and-create-in-crm \
  -H "Content-Type: application/json" \
  -d '{
    "lead_name": "Test Lead",
    "lead_email": "test@example.com",
    "company": "Test Corp",
    "lead_message": "Interested in demo"
  }'
```

**3. Test n8n Workflow:**
```bash
# Get webhook URL from n8n workflow
curl -X POST https://your-n8n.com/webhook/sales-lead-intake \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "company": "Acme Corp",
    "message": "Want to learn more"
  }'
```

### Load Testing

```bash
# Install tool
pip install locust

# Create load test
cat > locustfile.py <<EOF
from locust import HttpUser, task, between

class AgentUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def qualify_lead(self):
        self.client.post("/phase1/qualify-lead", json={
            "lead_name": "Load Test",
            "lead_email": "test@example.com",
            "company": "Test Corp",
            "lead_message": "Test message"
        })
EOF

# Run load test
locust -f locustfile.py --host=http://localhost:8000
# Open http://localhost:8089 to start test
```

---

## Escalation Workflows

### Human-in-the-Loop Triggers

**Automatic Escalation Rules:**

```python
# agents/escalation_rules.py
ESCALATION_TRIGGERS = {
    'low_confidence': {
        'threshold': 0.6,
        'action': 'human_review',
        'priority': 'medium'
    },
    'high_value_lead': {
        'ai_score': 9.0,
        'action': 'immediate_notification',
        'priority': 'high'
    },
    'negative_sentiment': {
        'sentiment': -0.5,
        'action': 'cs_intervention',
        'priority': 'high'
    },
    'api_error': {
        'error_count': 3,
        'action': 'alert_devops',
        'priority': 'critical'
    }
}
```

### Escalation Workflow Example

```
AI Agent Decision
    ↓
IF confidence < 60%
    ↓
Create Task in Attio
    ↓
Email Team Lead
    ↓
Slack Notification
    ↓
Await Human Review
    ↓
Resume Workflow
```

### Implementation in n8n

**Add to any workflow:**
```json
{
  "name": "Check Confidence",
  "type": "n8n-nodes-base.if",
  "parameters": {
    "conditions": {
      "number": [{
        "value1": "={{$json.confidence}}",
        "operation": "smaller",
        "value2": 0.6
      }]
    }
  }
},
{
  "name": "Escalate to Human",
  "type": "n8n-nodes-base.attio",
  "parameters": {
    "operation": "createTask",
    "content": "Manual review needed - Low confidence",
    "priority": "high"
  }
}
```

---

## Deployment Scripts

### Production Deployment

**1. Server Setup Script:**
```bash
#!/bin/bash
# scripts/deploy_production.sh

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone <your-repo> /opt/instant-agency
cd /opt/instant-agency

# Configure environment
cp .env.example .env
nano .env  # Set production values

# Start services
docker-compose up -d

# Install SSL (Let's Encrypt)
sudo apt-get install -y certbot
sudo certbot --nginx -d your-domain.com
```

**2. Backup Script:**
```bash
#!/bin/bash
# scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/$DATE"

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker exec instant-agency-postgres pg_dump -U instant_agency instant_agency > $BACKUP_DIR/database.sql

# Backup n8n workflows
docker cp instant-agency-n8n:/home/node/.n8n $BACKUP_DIR/n8n

# Backup .env
cp .env $BACKUP_DIR/

# Compress
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "Backup complete: $BACKUP_DIR.tar.gz"
```

**3. Update Script:**
```bash
#!/bin/bash
# scripts/update.sh

# Pull latest code
git pull origin main

# Rebuild containers
docker-compose build --no-cache

# Restart services with zero downtime
docker-compose up -d --force-recreate

# Run migrations
docker exec instant-agency-agents python migrations/run.py

echo "Update complete"
```

### Health Checks

```bash
# scripts/health_check.sh
#!/bin/bash

echo "Checking services..."

# Check agents
curl -f http://localhost:8000/health || echo "❌ Agents down"

# Check n8n
curl -f http://localhost:5678 || echo "❌ n8n down"

# Check Metabase
curl -f http://localhost:3000/api/health || echo "❌ Metabase down"

# Check Attio API
curl -f -H "Authorization: Bearer $ATTIO_API_KEY" \
  https://api.attio.com/v2/self || echo "❌ Attio API issue"

echo "Health check complete"
```

---

## Troubleshooting

### Common Issues

**1. Agents won't start**
```bash
# Check logs
docker-compose logs agent-service

# Common causes:
# - Missing HUGGINGFACE_API_KEY
# - Port 8000 already in use
# - Requirements not installed

# Solution:
docker-compose down
docker-compose up --build agent-service
```

**2. n8n can't reach agents**
```bash
# Inside n8n container, test:
docker exec instant-agency-n8n curl http://agent-service:8000/health

# If fails, check network:
docker network inspect instant-agency-network

# Solution: Ensure AGENT_API_URL=http://agent-service:8000
```

**3. Attio API rate limit**
```bash
# Check usage
curl -H "Authorization: Bearer $ATTIO_API_KEY" \
  https://api.attio.com/v2/usage

# Solution: Implement caching or upgrade plan
```

**4. Database connection errors**
```bash
# Check PostgreSQL
docker-compose logs postgres

# Test connection
docker exec instant-agency-postgres psql -U instant_agency -c "SELECT 1"

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

### Debug Mode

```bash
# Enable verbose logging
LOG_LEVEL=debug docker-compose up agent-service

# Or in Python:
export LOG_LEVEL=debug
python agents/main.py
```

### Reset Everything

```bash
# Nuclear option - fresh start
docker-compose down -v
rm -rf data/
docker-compose up --build
```

---

## Next Steps

✅ **Phase 1 Complete!** You now have:
- 20 AI agents running
- Attio CRM integration
- 3 n8n workflow templates
- Analytics dashboard
- Monitoring system
- Testing framework
- Deployment scripts

**What's Next:**
1. Customize workflows for your use case
2. Add your domain and SSL
3. Configure email notifications
4. Set up monitoring alerts
5. Train team on n8n interface
6. Start capturing real leads!

**Resources:**
- API Docs: http://localhost:8000/docs
- Control Panel: http://localhost:8000/control-panel/dashboard
- n8n: http://localhost:5678
- Metabase: http://localhost:3000

**Support:**
- Check logs: `docker-compose logs -f`
- Test endpoints: `curl http://localhost:8000/health`
- Review workflows: n8n execution history
