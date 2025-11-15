# Instant Agency - Configuration Guide

## Table of Contents
1. [Overview](#overview)
2. [Environment Variables](#environment-variables)
3. [Agent Configuration](#agent-configuration)
4. [Workflow Configuration](#workflow-configuration)
5. [Integration Settings](#integration-settings)
6. [Performance Tuning](#performance-tuning)

## Overview

Instant Agency uses a layered configuration approach:
- **Environment variables** (`.env`): Infrastructure and secrets
- **YAML files**: Agent behaviors and workflows
- **Database settings**: Runtime configurations and user preferences
- **UI dashboards**: Real-time adjustments

## Environment Variables

### Core Settings

```bash
# Application
NODE_ENV=production                    # development | production | staging
DOMAIN=instant-agency.local           # Your domain
DEBUG=false                           # Enable verbose logging

# Timezone & Locale
TZ=America/New_York
LOCALE=en-US
```

### n8n Configuration

```bash
# Basic
N8N_HOST=0.0.0.0
N8N_PORT=5678
N8N_PROTOCOL=https                    # http | https
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=secure_password_here

# Execution
N8N_EXECUTION_MODE=queue              # regular | queue
N8N_WORKERS=4                         # Number of worker processes
N8N_QUEUE_BULL_REDIS_HOST=redis
N8N_QUEUE_BULL_REDIS_PORT=6379
N8N_QUEUE_BULL_REDIS_PASSWORD=redis_password

# Webhooks
WEBHOOK_URL=https://workflows.instant-agency.ai

# Timezone
GENERIC_TIMEZONE=America/New_York

# Security
N8N_JWT_SECRET=generate_random_secret_here
```

### Database Configuration

```bash
# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=instant_agency
POSTGRES_USER=instant_agency_user
POSTGRES_PASSWORD=strong_password_here
POSTGRES_SSL=false                    # true for production

# Connection Pool
DB_POOL_MIN=2
DB_POOL_MAX=10

# n8n Database
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=${POSTGRES_HOST}
DB_POSTGRESDB_PORT=${POSTGRES_PORT}
DB_POSTGRESDB_DATABASE=${POSTGRES_DB}
DB_POSTGRESDB_USER=${POSTGRES_USER}
DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
```

### Redis Configuration

```bash
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_secure_password
REDIS_DB=0
REDIS_MAX_CONNECTIONS=50
```

### AI & ML Configuration

```bash
# Hugging Face
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxx
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2
HUGGINGFACE_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
HUGGINGFACE_ENDPOINT=https://api-inference.huggingface.co

# Alternative: Local model hosting
# LOCAL_MODEL_PATH=/models/mistral-7b
# USE_LOCAL_MODELS=true

# Model Parameters
LLM_TEMPERATURE=0.7                   # 0.0 (deterministic) to 1.0 (creative)
LLM_MAX_TOKENS=2048
LLM_TOP_P=0.9
LLM_FREQUENCY_PENALTY=0.0
LLM_PRESENCE_PENALTY=0.0

# Vector Database
VECTOR_DB_TYPE=chroma                 # chroma | qdrant | pinecone
CHROMA_HOST=chroma
CHROMA_PORT=8000
CHROMA_PERSIST_DIRECTORY=/data/chroma
```

### Email Configuration

```bash
# Provider (choose one)
EMAIL_PROVIDER=sendgrid               # sendgrid | mailgun | smtp | gmail

# SendGrid
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@instant-agency.ai
SENDGRID_FROM_NAME=Instant Agency

# Mailgun
MAILGUN_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
MAILGUN_DOMAIN=mg.instant-agency.ai
MAILGUN_FROM_EMAIL=noreply@instant-agency.ai

# SMTP (Generic)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SECURE=true
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Email Settings
EMAIL_RATE_LIMIT=100                  # Emails per hour
EMAIL_RETRY_ATTEMPTS=3
EMAIL_BATCH_SIZE=50
```

### CRM Configuration

```bash
# CRM Type
CRM_TYPE=suitecrm                     # suitecrm | odoo | vtiger

# SuiteCRM
SUITECRM_URL=http://crm:8080
SUITECRM_USERNAME=admin
SUITECRM_PASSWORD=admin_password
SUITECRM_API_KEY=xxxxxxxxxxxxxxxx

# Odoo
ODOO_URL=http://odoo:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin_password

# VTiger
VTIGER_URL=http://vtiger:8080
VTIGER_USERNAME=admin
VTIGER_ACCESS_KEY=xxxxxxxxxxxxxxxx
```

### Analytics Configuration

```bash
# Metabase
METABASE_PORT=3000
METABASE_DB_FILE=/data/metabase/metabase.db
MB_DB_TYPE=postgres
MB_DB_HOST=${POSTGRES_HOST}
MB_DB_PORT=${POSTGRES_PORT}
MB_DB_DBNAME=metabase
MB_DB_USER=metabase_user
MB_DB_PASS=metabase_password

# Matomo (alternative)
MATOMO_URL=http://matomo:8080
MATOMO_SITE_ID=1
MATOMO_TOKEN_AUTH=xxxxxxxxxxxxxxxx

# Google Analytics (optional)
GA_TRACKING_ID=UA-XXXXXXXXX-X
GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

### Social Media APIs

```bash
# LinkedIn
LINKEDIN_CLIENT_ID=xxxxxxxxxxxxxxxx
LINKEDIN_CLIENT_SECRET=xxxxxxxxxxxxxxxx
LINKEDIN_ACCESS_TOKEN=xxxxxxxxxxxxxxxx

# Twitter/X
TWITTER_API_KEY=xxxxxxxxxxxxxxxx
TWITTER_API_SECRET=xxxxxxxxxxxxxxxx
TWITTER_ACCESS_TOKEN=xxxxxxxxxxxxxxxx
TWITTER_ACCESS_SECRET=xxxxxxxxxxxxxxxx
TWITTER_BEARER_TOKEN=xxxxxxxxxxxxxxxx

# Facebook/Meta
FACEBOOK_APP_ID=xxxxxxxxxxxxxxxx
FACEBOOK_APP_SECRET=xxxxxxxxxxxxxxxx
FACEBOOK_PAGE_ACCESS_TOKEN=xxxxxxxxxxxxxxxx
```

### Monitoring & Logging

```bash
# Logging Level
LOG_LEVEL=info                        # debug | info | warn | error

# Sentry (Error Tracking)
SENTRY_DSN=https://xxxxxxxxxxxxxxxx@sentry.io/xxxxxxx
SENTRY_ENVIRONMENT=production

# Prometheus
PROMETHEUS_PORT=9090
PROMETHEUS_RETENTION=15d

# Grafana
GRAFANA_PORT=3001
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin_password
```

## Agent Configuration

Each agent has a `config.yaml` file in its directory.

### Example: Sales Qualification Agent

**File**: `agents/sales/qualification/config.yaml`

```yaml
agent:
  name: "Sales Qualification Agent"
  version: "1.0.0"
  description: "Assesses lead fit and readiness to buy"

model:
  provider: "huggingface"
  model_name: "mistralai/Mistral-7B-Instruct-v0.2"
  temperature: 0.5              # Lower for more consistent scoring
  max_tokens: 1024

system_prompt: |
  You are an expert sales qualification agent. Your role is to assess
  whether a lead is a good fit for our product and ready to buy.

  Use the BANT framework:
  - Budget: Do they have budget allocated?
  - Authority: Are they a decision maker?
  - Need: Do they have a clear need?
  - Timeline: When do they need a solution?

  Score each dimension 0-10 and provide an overall qualification score.

tools:
  - name: "crm_lookup"
    description: "Look up lead information in CRM"
    enabled: true

  - name: "company_research"
    description: "Research company information"
    enabled: true
    api_keys:
      - "clearbit"
      - "apollo"

  - name: "email_sender"
    description: "Send follow-up emails"
    enabled: true
    rate_limit: 50  # per hour

memory:
  type: "conversation"
  max_history: 10              # Last 10 interactions
  ttl: 86400                   # 24 hours in seconds

  vector_store:
    enabled: true
    collection: "qualification_history"
    similarity_threshold: 0.7

escalation:
  rules:
    - condition: "score < 5"
      action: "nurture_campaign"

    - condition: "score >= 5 and score < 7"
      action: "schedule_call"

    - condition: "score >= 7"
      action: "assign_to_sales_rep"
      notify: true

    - condition: "deal_value > 100000"
      action: "escalate_to_senior_rep"
      notify: true

performance:
  response_timeout: 30         # seconds
  retry_attempts: 3
  cache_results: true
  cache_ttl: 3600             # 1 hour

monitoring:
  log_level: "info"
  track_metrics:
    - "response_time"
    - "qualification_score"
    - "escalation_rate"
  alerts:
    - metric: "response_time"
      threshold: 45
      action: "notify_ops"
```

### Example: Content Creation Agent

**File**: `agents/content/writer/config.yaml`

```yaml
agent:
  name: "Content Writing Agent"
  version: "1.0.0"
  description: "Generates blog posts, articles, and marketing copy"

model:
  provider: "huggingface"
  model_name: "mistralai/Mistral-7B-Instruct-v0.2"
  temperature: 0.8              # Higher for more creative content
  max_tokens: 4096

system_prompt: |
  You are an expert content writer specializing in B2B SaaS marketing.

  Your writing style:
  - Clear and conversational
  - Data-driven with examples
  - SEO-optimized without keyword stuffing
  - Engaging and educational

  Always include:
  1. Compelling headline
  2. Clear introduction with hook
  3. Well-structured body with subheadings
  4. Actionable takeaways
  5. Strong call-to-action

tools:
  - name: "research"
    description: "Research topics using web search"
    enabled: true

  - name: "seo_analyzer"
    description: "Analyze and optimize for SEO"
    enabled: true

  - name: "plagiarism_checker"
    description: "Check content originality"
    enabled: true

  - name: "image_generator"
    description: "Generate featured images"
    enabled: false  # Enable in Phase 4

templates:
  blog_post:
    min_words: 1000
    max_words: 2500
    include_toc: true
    include_images: true

  social_post:
    platforms:
      linkedin:
        max_chars: 3000
        include_hashtags: true
        hashtag_count: 3
      twitter:
        max_chars: 280
        include_hashtags: true
      facebook:
        max_chars: 5000

approval:
  required: true
  approvers:
    - "content_manager"
    - "brand_manager"
  timeout: "24h"
  auto_publish_on_timeout: false

quality_checks:
  - name: "readability"
    tool: "flesch_kincaid"
    min_score: 60

  - name: "grammar"
    tool: "languagetool"

  - name: "brand_voice"
    tool: "custom_classifier"
    confidence_threshold: 0.8
```

## Workflow Configuration

Workflows are defined in n8n, but can be configured via JSON/YAML.

### Example: Lead Nurture Workflow

**File**: `workflows/marketing/lead-nurture.json`

```json
{
  "name": "Lead Nurture Campaign",
  "nodes": [
    {
      "type": "n8n-nodes-base.trigger",
      "name": "New Unqualified Lead",
      "parameters": {
        "event": "lead.created",
        "conditions": {
          "qualification_score": { "lt": 5 }
        }
      }
    },
    {
      "type": "n8n-nodes-base.wait",
      "name": "Wait 1 Day",
      "parameters": {
        "duration": "1d"
      }
    },
    {
      "type": "n8n-nodes-base.function",
      "name": "Personalize Email",
      "parameters": {
        "code": "// Call content agent to personalize"
      }
    },
    {
      "type": "n8n-nodes-base.sendEmail",
      "name": "Send Email 1",
      "parameters": {
        "template": "nurture_day1"
      }
    }
  ],
  "settings": {
    "executionOrder": "v1",
    "saveExecutionProgress": true,
    "saveDataSuccessExecution": "all",
    "saveDataErrorExecution": "all"
  }
}
```

## Integration Settings

### CRM Integration

**File**: `integrations/crm/config.yaml`

```yaml
integration:
  name: "SuiteCRM"
  type: "crm"

connection:
  url: ${SUITECRM_URL}
  api_version: "v8"
  authentication:
    type: "oauth2"
    client_id: ${SUITECRM_CLIENT_ID}
    client_secret: ${SUITECRM_CLIENT_SECRET}

sync:
  enabled: true
  direction: "bidirectional"    # to_crm | from_crm | bidirectional
  frequency: "5m"               # Sync every 5 minutes

  entities:
    contacts:
      enabled: true
      fields:
        - first_name
        - last_name
        - email
        - phone
        - company
        - custom_ai_score

    leads:
      enabled: true
      auto_convert: true
      convert_threshold: 7      # Qualification score

    opportunities:
      enabled: true
      fields:
        - name
        - amount
        - stage
        - close_date
        - ai_insights

mapping:
  instant_agency_to_crm:
    qualification_score: "custom_ai_score"
    engagement_level: "custom_engagement"

webhooks:
  enabled: true
  events:
    - "contact.created"
    - "contact.updated"
    - "opportunity.stage_changed"
```

## Performance Tuning

### Resource Limits

**File**: `docker-compose.override.yml`

```yaml
version: '3.8'

services:
  n8n:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G

  postgres:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Caching Strategy

**File**: `config/cache.yaml`

```yaml
cache:
  default_ttl: 3600           # 1 hour

  layers:
    - name: "memory"
      type: "in-process"
      max_size: "100MB"
      ttl: 60               # 1 minute

    - name: "redis"
      type: "redis"
      host: ${REDIS_HOST}
      ttl: 3600             # 1 hour

    - name: "database"
      type: "postgres"
      ttl: null             # No expiration

  strategies:
    agent_responses:
      enabled: true
      ttl: 300              # 5 minutes
      cache_key: "agent_{name}_input_{hash}"

    crm_lookups:
      enabled: true
      ttl: 600              # 10 minutes

    model_embeddings:
      enabled: true
      ttl: 86400            # 24 hours
```

### Rate Limiting

**File**: `config/rate-limits.yaml`

```yaml
rate_limits:
  global:
    requests_per_second: 100
    burst: 200

  per_agent:
    marketing_outreach:
      emails_per_hour: 500
      api_calls_per_minute: 60

    content_writer:
      generations_per_hour: 100

    sales_qualification:
      assessments_per_hour: 200

  external_apis:
    huggingface:
      requests_per_second: 10
      retry_after: 429          # HTTP status code
      backoff: "exponential"

    crm:
      requests_per_second: 20

    email_provider:
      emails_per_hour: 1000
```

---

**Document Version**: 1.0
**Last Updated**: November 2025
