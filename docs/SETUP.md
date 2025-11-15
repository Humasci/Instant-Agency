# Instant Agency - Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Phase 1: Core Setup](#phase-1-core-setup)
3. [Phase 2: Department Foundations](#phase-2-department-foundations)
4. [Phase 3: Orchestration](#phase-3-orchestration)
5. [Phase 4: Optimization](#phase-4-optimization)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Minimum**:
- 4 CPU cores
- 8 GB RAM
- 50 GB storage
- Linux/macOS/Windows with WSL2

**Recommended**:
- 8+ CPU cores
- 16+ GB RAM
- 200 GB SSD storage
- Linux server or macOS

### Software Requirements

1. **Docker & Docker Compose**
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Node.js 18+**
   ```bash
   # Using nvm (recommended)
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   nvm install 18
   nvm use 18
   ```

3. **Python 3.10+**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.10 python3.10-venv python3-pip

   # macOS
   brew install python@3.10
   ```

4. **Git**
   ```bash
   # Ubuntu/Debian
   sudo apt install git

   # macOS
   brew install git
   ```

### API Keys & Accounts

Create accounts and obtain API keys for:

1. **Hugging Face** (Required)
   - Sign up at https://huggingface.co
   - Generate API token at https://huggingface.co/settings/tokens
   - Free tier available

2. **Email Service** (Choose one)
   - SendGrid (free tier: 100 emails/day)
   - Mailgun (free tier: 5,000 emails/month)
   - Gmail API (free)

3. **Social Media APIs** (Optional, Phase 2+)
   - LinkedIn API
   - Twitter/X API
   - Facebook/Meta API

4. **Calendar Integration** (Optional)
   - Google Calendar API
   - Microsoft Graph API (Outlook)

## Phase 1: Core Setup

**Timeline**: Weeks 1-2
**Goal**: Get the foundational infrastructure running

### Step 1: Clone and Initialize

```bash
# Clone repository
git clone https://github.com/Humasci/Instant-Agency.git
cd Instant-Agency

# Create environment configuration
cp .env.example .env

# Edit .env with your API keys and settings
nano .env
```

### Step 2: Configure Environment Variables

Edit `.env` file:

```bash
# Core Settings
NODE_ENV=production
DOMAIN=instant-agency.local

# n8n Configuration
N8N_HOST=0.0.0.0
N8N_PORT=5678
N8N_PROTOCOL=http
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=change_this_password

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=instant_agency
POSTGRES_USER=instant_agency
POSTGRES_PASSWORD=change_this_password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=change_this_password

# Hugging Face
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxx
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# Email
EMAIL_PROVIDER=sendgrid  # or mailgun, gmail
EMAIL_API_KEY=your_email_api_key
EMAIL_FROM=noreply@instant-agency.ai

# CRM (choose one)
CRM_TYPE=suitecrm  # or odoo, vtiger
CRM_URL=http://crm:8080
CRM_API_KEY=your_crm_api_key

# Analytics
ANALYTICS_TYPE=metabase  # or plausible, matomo
METABASE_PORT=3000
```

### Step 3: Launch Core Services

```bash
# Start infrastructure
docker-compose up -d

# Verify all services are running
docker-compose ps

# Expected output:
# NAME                COMMAND             STATUS
# n8n                 ...                 Up
# postgres            ...                 Up
# redis               ...                 Up
# crm                 ...                 Up
# metabase            ...                 Up
```

### Step 4: Access Dashboards

1. **n8n Workflow Editor**
   - URL: http://localhost:5678
   - Login with credentials from `.env`
   - Create owner account on first access

2. **CRM (SuiteCRM)**
   - URL: http://localhost:8080
   - Default: admin / password
   - Change immediately after first login

3. **Metabase (Analytics)**
   - URL: http://localhost:3000
   - Set up admin account on first access
   - Connect to PostgreSQL database

### Step 5: Import Initial Workflows

```bash
# Import n8n workflows
cd workflows/
./import-workflows.sh

# Verify workflows imported
# In n8n, you should see:
# - Lead Capture Workflow
# - Email Response Bot
# - Support Ticket Triage
```

### Step 6: Test Basic Automation

```bash
# Test webhook endpoint
curl -X POST http://localhost:5678/webhook-test/new-lead \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "source": "website"
  }'

# Check n8n executions to verify workflow ran
# Check CRM to verify contact was created
```

### Step 7: Initialize AI Agents

```bash
# Install Python dependencies
cd agents/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Test basic agent
python test_agent.py

# Expected output:
# ✓ Hugging Face connection successful
# ✓ Basic agent responding correctly
# ✓ Vector database initialized
```

## Phase 2: Department Foundations

**Timeline**: Weeks 3-6
**Goal**: Deploy specialized agents for each department

### Marketing Department Setup

```bash
# Navigate to marketing agents
cd agents/marketing/

# Configure marketing agents
cp config.example.yaml config.yaml
nano config.yaml

# Deploy marketing agents
python deploy.py --department marketing

# Import marketing workflows
cd ../../workflows/marketing/
./import-marketing-workflows.sh
```

**Marketing Workflows**:
- Prospect Research & Enrichment
- Automated Email Campaigns
- Social Media Monitoring
- Lead Scoring & Segmentation

**Test Marketing Automation**:
```bash
# Trigger prospect research
curl -X POST http://localhost:5678/webhook/marketing/research-prospect \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Acme Corp",
    "industry": "SaaS"
  }'
```

### Sales Department Setup

```bash
# Deploy sales agents
cd agents/sales/
python deploy.py --department sales

# Import sales workflows
cd ../../workflows/sales/
./import-sales-workflows.sh
```

**Sales Workflows**:
- Lead Qualification
- Discovery Call Preparation
- Proposal Generation
- Follow-up Sequences

**Test Sales Agent**:
```bash
# Test qualification agent
curl -X POST http://localhost:5678/webhook/sales/qualify-lead \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": 12345,
    "responses": {
      "budget": "50000",
      "timeline": "Q1 2025",
      "decision_maker": true
    }
  }'
```

### Content Department Setup

```bash
# Deploy content agents
cd agents/content/
python deploy.py --department content

# Import content workflows
cd ../../workflows/content/
./import-content-workflows.sh
```

**Content Workflows**:
- Blog Post Generation
- Social Media Content Calendar
- SEO Optimization
- Multi-Channel Distribution

**Test Content Agent**:
```bash
# Generate blog post
curl -X POST http://localhost:5678/webhook/content/generate-blog \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI in Marketing",
    "keywords": ["AI marketing", "automation", "personalization"],
    "length": 1500
  }'
```

### Support Department Setup

```bash
# Deploy support agents
cd agents/support/
python deploy.py --department support

# Import support workflows
cd ../../workflows/support/
./import-support-workflows.sh
```

**Support Workflows**:
- Ticket Triage & Routing
- Automated Resolution
- Escalation Management
- Customer Satisfaction Surveys

**Test Support Agent**:
```bash
# Submit support ticket
curl -X POST http://localhost:5678/webhook/support/new-ticket \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 67890,
    "subject": "Cannot access dashboard",
    "description": "Getting 404 error when trying to log in",
    "priority": "high"
  }'
```

### Operations & Analytics Setup

```bash
# Deploy operations agents
cd agents/operations/
python deploy.py --department operations

# Set up analytics dashboards
cd ../../analytics/
./setup-dashboards.sh
```

**Operations Workflows**:
- Daily KPI Reporting
- Data Quality Monitoring
- Performance Optimization
- Alert Management

## Phase 3: Orchestration

**Timeline**: Weeks 7-10
**Goal**: Connect all departments with multi-agent workflows

### Multi-Agent Orchestration Setup

```bash
# Install orchestration framework
cd orchestration/
pip install -r requirements.txt

# Configure CrewAI
cp crew_config.example.yaml crew_config.yaml
nano crew_config.yaml
```

### Example: End-to-End Lead Journey

```yaml
# orchestration/journeys/lead-to-customer.yaml
journey: "lead_to_customer"
trigger: "new_lead"

stages:
  - name: "Research & Enrichment"
    agent: "marketing/prospecting_agent"
    output: "enriched_lead_data"

  - name: "Initial Outreach"
    agent: "marketing/engagement_agent"
    input: "enriched_lead_data"
    output: "outreach_response"

  - name: "Qualification"
    agent: "sales/qualification_agent"
    input: "outreach_response"
    decision:
      qualified: "next_stage"
      not_qualified: "nurture_sequence"

  - name: "Discovery"
    agent: "sales/discovery_agent"
    output: "discovery_notes"

  - name: "Proposal"
    agent: "sales/proposal_agent"
    input: "discovery_notes"
    output: "proposal_document"

  - name: "Closing"
    agent: "sales/closing_agent"
    input: "proposal_document"
    decision:
      closed_won: "onboarding"
      closed_lost: "end"
      needs_followup: "followup_sequence"

  - name: "Onboarding"
    agent: "support/onboarding_agent"
    output: "onboarding_complete"

escalation_rules:
  - condition: "deal_value > 100000"
    action: "notify_human_sales_rep"

  - condition: "stuck_in_stage > 7_days"
    action: "escalate_to_manager"
```

### Deploy Orchestration

```bash
# Deploy the journey
python deploy_journey.py --journey lead-to-customer

# Test the journey
python test_journey.py --journey lead-to-customer --test-data test_lead.json
```

### Human-in-the-Loop Checkpoints

Configure approval workflows:

```yaml
# orchestration/approvals.yaml
approval_points:
  - stage: "proposal_generation"
    requires_approval: true
    approvers: ["sales_manager"]
    timeout: 24h
    fallback: "auto_approve"

  - stage: "content_publication"
    requires_approval: true
    approvers: ["content_manager", "brand_manager"]
    timeout: 12h
    fallback: "reject"
```

## Phase 4: Optimization

**Timeline**: Weeks 11+
**Goal**: Continuous improvement and advanced features

### A/B Testing Framework

```bash
# Set up experimentation
cd optimization/
pip install -r requirements.txt

# Create experiment
python create_experiment.py \
  --name "email_subject_test" \
  --variants "variant_a.json,variant_b.json" \
  --metric "open_rate" \
  --duration 7d
```

### Model Fine-tuning

```bash
# Collect training data
python scripts/collect_training_data.py \
  --agent "sales/qualification_agent" \
  --start-date "2025-01-01" \
  --end-date "2025-03-31"

# Fine-tune model
python scripts/fine_tune.py \
  --base-model "mistralai/Mistral-7B-Instruct-v0.2" \
  --training-data "data/qualification_training.jsonl" \
  --output-model "qualification_agent_v2"

# Deploy fine-tuned model
python scripts/deploy_model.py \
  --model "qualification_agent_v2" \
  --agent "sales/qualification_agent"
```

### Performance Monitoring

Set up Prometheus metrics:

```bash
# Start monitoring stack
cd monitoring/
docker-compose up -d

# Access dashboards
# Grafana: http://localhost:3001 (admin/admin)
# Prometheus: http://localhost:9090
```

### Avatar Integration

```bash
# Install avatar dependencies
cd features/avatars/
pip install -r requirements.txt

# Configure avatar service
cp config.example.yaml config.yaml
nano config.yaml  # Add D-ID or HeyGen API key

# Test avatar generation
python test_avatar.py --script "Hello, I'm your AI sales representative"
```

## Troubleshooting

### Common Issues

**1. n8n Workflows Not Executing**

```bash
# Check n8n logs
docker-compose logs -f n8n

# Verify webhooks are accessible
curl http://localhost:5678/webhook-test/ping

# Restart n8n
docker-compose restart n8n
```

**2. AI Agents Not Responding**

```bash
# Check Hugging Face API key
python -c "import os; from huggingface_hub import login; login(os.getenv('HUGGINGFACE_API_KEY'))"

# Test agent directly
cd agents/
python test_agent.py --agent marketing/prospecting_agent

# Check agent logs
tail -f logs/agents.log
```

**3. Database Connection Errors**

```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U instant_agency -d instant_agency

# Check credentials in .env
grep POSTGRES .env
```

**4. CRM Integration Issues**

```bash
# Test CRM API
curl -X GET http://localhost:8080/api/v8/modules \
  -H "Authorization: Bearer YOUR_API_KEY"

# Verify CRM credentials
cd integrations/crm/
python test_connection.py
```

**5. Out of Memory Errors**

```bash
# Check Docker memory limits
docker stats

# Increase Docker memory allocation
# Docker Desktop: Settings > Resources > Memory > 8GB+

# Or use smaller models
# In .env: HUGGINGFACE_MODEL=TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

### Getting Help

- **Documentation**: Check `/docs` directory
- **Logs**: `docker-compose logs -f [service_name]`
- **Issues**: https://github.com/Humasci/Instant-Agency/issues
- **Community**: https://github.com/Humasci/Instant-Agency/discussions

### Health Checks

```bash
# Run comprehensive health check
./scripts/health-check.sh

# Expected output:
# ✓ Docker running
# ✓ All services up
# ✓ Database accessible
# ✓ n8n workflows active
# ✓ AI agents responding
# ✓ CRM connected
# ✓ Analytics available
```

## Next Steps

After completing setup:

1. **Customize Agents**: Edit prompts and configurations in `agents/*/config.yaml`
2. **Create Workflows**: Build custom n8n workflows for your use cases
3. **Train Models**: Fine-tune on your domain-specific data
4. **Monitor Performance**: Set up alerts and dashboards
5. **Scale**: Add more worker nodes as load increases

---

**Document Version**: 1.0
**Last Updated**: November 2025
