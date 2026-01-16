# Instant Agency - Complete Feature Guide

**Last Updated**: November 2025
**Version**: 0.1.0-alpha

This guide provides detailed explanations and practical examples for every feature in the Instant Agency platform.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [AI Agents](#ai-agents)
3. [Workflow Automation](#workflow-automation)
4. [CRM Integration](#crm-integration)
5. [Analytics & Reporting](#analytics--reporting)
6. [API Reference](#api-reference)
7. [Use Case Examples](#use-case-examples)

---

## Getting Started

### Initial Setup

**Step 1: Installation**

```bash
# Clone the repository
git clone https://github.com/Humasci/Instant-Agency.git
cd Instant-Agency

# Copy environment template
cp .env.example .env

# Edit configuration with your API keys
nano .env  # or use your preferred editor
```

**Step 2: Configure API Keys**

You'll need the following API keys (see where to get them):

1. **Hugging Face API** (Required - Free)
   - Go to https://huggingface.co/settings/tokens
   - Create new token with "Read" access
   - Copy token to `.env`: `HUGGINGFACE_API_KEY=hf_xxxxx`

2. **Email Service** (Choose one)
   - **SendGrid**: https://signup.sendgrid.com (100 emails/day free)
   - **Mailgun**: https://signup.mailgun.com (5,000 emails/month free)
   - Add credentials to `.env`

3. **CRM Setup** (Included)
   - SuiteCRM runs automatically in Docker
   - Default credentials in `.env.example`
   - Change passwords on first login

**Step 3: Launch Platform**

```bash
# Run automated setup
./scripts/setup.sh

# Or manually start services
docker-compose up -d

# Verify all services are running
./scripts/health-check.sh
```

**Step 4: Access Dashboards**

Once running, access these URLs:

- **n8n Workflows**: http://localhost:5678
  - Create automation workflows
  - Connect agents to external services

- **SuiteCRM**: http://localhost:8080
  - Manage leads, contacts, opportunities
  - View customer data

- **Metabase**: http://localhost:3000
  - Analytics dashboards
  - Business intelligence reports

- **Grafana**: http://localhost:3001
  - System monitoring
  - Agent performance metrics

---

## AI Agents

### Overview

AI agents are autonomous programs that handle specific business tasks. Each agent:
- Uses large language models (LLMs) for intelligence
- Has memory to remember conversations
- Can use tools (email, CRM, web search)
- Escalates complex issues to humans
- Learns from interactions

### Sales Qualification Agent

**Purpose**: Automatically scores and qualifies sales leads using the BANT framework.

**BANT Framework Explained**:
- **Budget**: Does the prospect have money allocated?
- **Authority**: Are they a decision-maker?
- **Need**: Do they have a problem we can solve?
- **Timeline**: When do they need a solution?

**How to Use**:

1. **Via API (Programmatic)**:

```bash
curl -X POST http://localhost:8000/sales/qualify \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": 12345,
    "responses": {
      "budget": "We have $50,000 allocated for this",
      "timeline": "Need solution by Q1 2025",
      "decision_maker": true,
      "pain_point": "Our sales team spends 20 hours/week on manual tasks",
      "company": "Acme Corp",
      "deal_value": 75000
    }
  }'
```

2. **Via n8n Workflow**:

```
Webhook Trigger → Extract Data → Sales Qualification Agent → CRM Update
```

**Response Format**:

```json
{
  "lead_id": 12345,
  "bant_scores": {
    "budget": 8.5,
    "authority": 9.0,
    "need": 8.0,
    "timeline": 7.5
  },
  "overall_score": 8.2,
  "qualification_status": "hot",
  "next_action": "assign_to_sales_rep",
  "reasoning": "Strong budget and clear need. Decision maker engaged. Timeline urgent.",
  "missing_info": [],
  "escalation": {
    "action": "assign_to_sales_rep",
    "notify": true,
    "priority": "high"
  }
}
```

**Understanding Scores**:

| Score | Status | Meaning | Action |
|-------|--------|---------|--------|
| 8-10 | Hot | Ready to buy | Immediate sales contact |
| 6-7.9 | Warm | Interested | Schedule discovery call |
| 3-5.9 | Cold | Needs nurturing | Add to email campaign |
| 0-2.9 | Disqualified | Poor fit | Archive |

**Customization**:

Edit `agents/sales/qualification/config.yaml`:

```yaml
scoring:
  weights:
    budget: 0.3      # Adjust importance (must sum to 1.0)
    authority: 0.25
    need: 0.3
    timeline: 0.15

  thresholds:
    hot: 8.0         # Change qualification levels
    warm: 6.0
    cold: 3.0
```

**Example Use Cases**:

1. **Webform Lead Qualification**
   - User submits contact form
   - Webhook triggers agent
   - Agent analyzes form responses
   - Lead scored and routed automatically

2. **Email Response Qualification**
   - Prospect replies to outreach email
   - Email parsed for BANT signals
   - Agent scores and recommends next step
   - Sales rep notified of hot leads

3. **Chat Qualification**
   - Website chat conversation
   - Agent analyzes chat transcript
   - Real-time qualification score
   - Live handoff to sales if hot

---

### Marketing Prospecting Agent

**Purpose**: Research companies and identify ideal prospects for outreach campaigns.

**How to Use**:

1. **Research a Single Company**:

```bash
curl -X POST http://localhost:8000/marketing/research-prospect \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Acme Corporation",
    "industry": "Technology"
  }'
```

2. **Bulk Prospect Research** (via n8n):

```
Google Sheets (Company List) → Loop → Prospecting Agent → CRM Import
```

**Response Includes**:

```json
{
  "company_name": "Acme Corporation",
  "company_data": {
    "industry": "Technology",
    "employees": 250,
    "revenue_estimate": 25000000,
    "location": "San Francisco, CA",
    "website": "www.acmecorp.com",
    "founded": 2015,
    "funding": "Series B",
    "tech_stack": ["AWS", "React", "PostgreSQL"],
    "recent_news": [
      {
        "title": "Acme Corp expands to new markets",
        "date": "2025-10-15",
        "source": "TechCrunch"
      }
    ]
  },
  "decision_makers": [
    {
      "name": "John Smith",
      "title": "VP of Marketing",
      "linkedin": "linkedin.com/in/johnsmith",
      "recent_activity": ["Posted about marketing automation"],
      "engagement_score": 8
    }
  ],
  "icp_fit_score": 8.5,
  "qualifies_for_outreach": true,
  "outreach_strategy": {
    "strategy": "Personalized email focusing on marketing automation ROI",
    "primary_contact": {
      "name": "John Smith",
      "title": "VP of Marketing"
    },
    "recommended_channel": "email",
    "personalization_points": [
      "Recent company expansion",
      "Technology stack alignment",
      "Industry expertise"
    ]
  }
}
```

**ICP (Ideal Customer Profile) Configuration**:

Edit `agents/marketing/prospecting/config.yaml`:

```yaml
segmentation:
  criteria:
    industries:
      - "Technology"      # Add your target industries
      - "SaaS"
      - "E-commerce"

    company_size:
      min_employees: 50   # Adjust target company size
      max_employees: 5000

    revenue:
      min: 5000000        # $5M minimum
      max: 500000000      # $500M maximum

    locations:
      - "North America"   # Target geographies
      - "Western Europe"

scoring:
  icp_fit_criteria:
    - name: "industry_match"
      weight: 0.25        # Adjust scoring weights
    - name: "company_size"
      weight: 0.20
    - name: "technology_stack"
      weight: 0.20
    - name: "growth_indicators"
      weight: 0.15
    - name: "budget_signals"
      weight: 0.20
```

**Example Workflows**:

1. **LinkedIn Company Research**
   ```
   LinkedIn Sales Navigator → Export Companies → Agent Research →
   High-fit prospects → CRM → Outreach Campaign
   ```

2. **Website Visitor Enrichment**
   ```
   Website Analytics → Identify Companies → Agent Research →
   Score Fit → Add to Prospecting List
   ```

3. **Conference Attendee Research**
   ```
   Event Attendee List → Agent Research → ICP Scoring →
   Prioritize Outreach → Personalized Follow-up
   ```

**Advanced Features**:

**A. Technology Stack Detection**
```yaml
# The agent identifies technologies used by prospects
# Useful for:
- Competitive displacement campaigns
- Technology partnership opportunities
- Integration positioning
```

**B. Trigger Event Detection**
```yaml
# Agent monitors for:
- Funding announcements
- Executive changes
- Company expansions
- Product launches
# Perfect timing for outreach
```

**C. Decision Maker Mapping**
```yaml
# Agent identifies:
- Key stakeholders
- Reporting structures
- Recent role changes
- Social media activity
```

---

### Content Writing Agent

**Purpose**: Generate high-quality blog posts, articles, and marketing copy optimized for SEO and engagement.

**How to Use**:

1. **Generate a Blog Post**:

```bash
curl -X POST http://localhost:8000/content/generate-blog \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI in Marketing Automation",
    "keywords": ["AI marketing", "automation", "personalization"],
    "length": 1500,
    "tone": "professional",
    "target_audience": "marketing managers",
    "include_examples": true
  }'
```

2. **Via n8n Workflow**:

```
Schedule Trigger → Content Calendar → Content Agent →
SEO Check → Human Approval → Publish to WordPress
```

**Configuration Options**:

Edit `agents/content/writing/config.yaml`:

```yaml
templates:
  blog_post:
    min_words: 1000
    max_words: 2500
    include_toc: true          # Table of contents
    include_images: true        # AI image suggestions
    seo_optimized: true        # Keyword optimization

quality_checks:
  - name: "readability"
    tool: "flesch_kincaid"
    min_score: 60              # Readability level

  - name: "seo_score"
    tool: "custom"
    min_score: 70              # SEO optimization

  - name: "plagiarism"
    tool: "copyscape"
    max_similarity: 15         # % similarity threshold

approval:
  required: true               # Require human approval
  approvers:
    - "content_manager"
  timeout: "24h"
  auto_publish_on_timeout: false
```

**Content Types**:

1. **Blog Posts**
   - 1000-2500 words
   - SEO optimized
   - Includes H2/H3 structure
   - Meta descriptions
   - Internal linking suggestions

2. **Social Media Posts**
   ```yaml
   platforms:
     linkedin:
       max_chars: 3000
       include_hashtags: true
       tone: "professional"

     twitter:
       max_chars: 280
       include_hashtags: true
       tone: "casual"

     facebook:
       max_chars: 5000
       tone: "friendly"
   ```

3. **Email Campaigns**
   ```yaml
   types:
     newsletter:
       max_words: 500
       structure: "teaser + value + cta"

     nurture:
       max_words: 300
       structure: "problem + solution + cta"
   ```

**Example: Complete Content Pipeline**

```
Content Calendar → Research Topics → Generate Draft →
SEO Optimization → Readability Check → Plagiarism Check →
Human Approval → Publish → Social Promotion → Track Performance
```

**Step-by-Step Example**:

**Step 1: Content Request**
```json
{
  "topic": "How AI Improves Sales Productivity",
  "keywords": ["AI sales", "productivity", "automation"],
  "length": 1200,
  "audience": "sales managers",
  "cta": "Schedule demo"
}
```

**Step 2: Agent Generates**
- Researches topic using web search
- Creates outline with H2/H3 headings
- Writes compelling introduction
- Adds data points and examples
- Optimizes for target keywords
- Includes strong call-to-action

**Step 3: Quality Checks**
- Flesch-Kincaid score: 65 (✓ Pass - target 60+)
- SEO score: 78 (✓ Pass - target 70+)
- Plagiarism: 8% (✓ Pass - target <15%)
- Grammar: 0 errors (✓ Pass)

**Step 4: Human Review**
- Content manager receives notification
- Reviews in approval dashboard
- Can request edits or approve
- Published automatically upon approval

**Step 5: Distribution**
- Post published to blog
- Social media posts generated automatically
- Email newsletter created
- Analytics tracking enabled

---

## Workflow Automation

### Understanding n8n Workflows

**What is n8n?**
n8n is a workflow automation tool that connects different services together. Think of it as "If This, Then That" (IFTTT) but much more powerful.

**Basic Concepts**:

1. **Nodes**: Individual steps in a workflow
2. **Connections**: Links between nodes
3. **Triggers**: What starts the workflow
4. **Actions**: What the workflow does
5. **Data**: Information passed between nodes

### Pre-built Workflows

#### 1. Lead Capture Workflow

**File**: `workflows/marketing/lead-capture.json`

**What it does**:
```
Website Form → Validate Data → Research Prospect →
Save to Database → Create CRM Lead → Send Welcome Email →
Qualify Lead → Notify Sales (if hot)
```

**Step-by-Step Explanation**:

**Step 1: Webhook Trigger**
- Receives form submissions from your website
- Webhook URL: `http://your-domain.com/webhook/lead-capture`
- Accepts POST requests with JSON data

```javascript
// Example form submission
{
  "name": "John Doe",
  "email": "john@example.com",
  "company": "Acme Corp",
  "phone": "+1-555-1234",
  "message": "Interested in your product"
}
```

**Step 2: Data Validation**
- Checks required fields (name, email)
- Validates email format
- Sanitizes input
- Rejects invalid submissions

**Step 3: Prospect Research**
- Calls Marketing Prospecting Agent
- Enriches with company data
- Calculates ICP fit score
- Identifies decision makers

**Step 4: Save to Database**
- Stores lead in PostgreSQL
- Generates unique ID
- Timestamps created_at
- Stores AI scoring data

**Step 5: Create CRM Lead**
- Creates lead record in SuiteCRM
- Maps fields correctly
- Links related records
- Sets lead source

**Step 6: Welcome Email**
- Sends personalized thank you
- Includes useful resources
- Sets expectations
- Tracks email opens

**Step 7: Qualification**
- Calls Sales Qualification Agent
- Analyzes lead responses
- Generates BANT score
- Determines next action

**Step 8: Sales Notification** (if score >= 7)
- Emails sales team
- Includes qualification summary
- Links to CRM record
- Marks as urgent if score >= 8

**How to Import and Use**:

1. **Import Workflow**:
   ```bash
   # Open n8n
   http://localhost:5678

   # Click "Import from File"
   # Select: workflows/marketing/lead-capture.json
   # Click "Import"
   ```

2. **Configure Credentials**:
   - PostgreSQL: Database connection
   - SMTP: Email sending
   - HTTP Request: Agent API endpoint

3. **Activate Workflow**:
   - Click "Active" toggle in top right
   - Workflow now processes leads automatically

4. **Test Workflow**:
   ```bash
   curl -X POST http://localhost:5678/webhook/lead-capture \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test User",
       "email": "test@example.com",
       "company": "Test Corp",
       "message": "Testing the workflow"
     }'
   ```

5. **Monitor Executions**:
   - Click "Executions" in n8n
   - View each step's input/output
   - Debug any errors
   - See execution time

**Customization Options**:

```javascript
// Change qualification threshold
// In "High Quality Lead?" node
{
  "conditions": {
    "number": [{
      "value1": "={{$json.data.overall_score}}",
      "operation": "largerEqual",
      "value2": 7  // Change this threshold
    }]
  }
}

// Customize welcome email
// In "Send Welcome Email" node
{
  "message": "Your custom email template here..."
}

// Add SMS notification
// Add new node: Twilio → Send SMS
```

### Creating Custom Workflows

**Example: Social Media Monitoring**

**Goal**: Monitor Twitter mentions and respond automatically

**Steps**:

1. **Create New Workflow** in n8n

2. **Add Schedule Trigger**
   ```
   Type: Schedule Trigger
   Run: Every 15 minutes
   ```

3. **Add Twitter Node**
   ```
   Type: Twitter
   Operation: Search
   Search Text: @yourcompany OR #yourproduct
   Max Results: 10
   ```

4. **Add Filter Node**
   ```
   Type: IF
   Condition: Does not contain "ignore" OR "spam"
   ```

5. **Add Agent Node**
   ```
   Type: HTTP Request
   Method: POST
   URL: http://agent-service:8000/phase2/classify-intent
   Body:
   {
     "message": "={{$json.text}}",
     "user_id": "={{$json.user.id}}"
   }
   ```

6. **Add Response Logic**
   ```
   IF intent = "question"
     → Call FAQ Agent → Reply to Tweet

   IF intent = "complaint"
     → Create Support Ticket → Notify Team

   IF intent = "praise"
     → Like Tweet → Thank User → Add to CRM
   ```

7. **Save and Activate**

**Best Practices**:

- **Error Handling**: Add error nodes to catch failures
- **Rate Limiting**: Don't overwhelm external APIs
- **Logging**: Log executions for debugging
- **Testing**: Test with sample data first
- **Monitoring**: Set up alerts for failures

---

## CRM Integration

### SuiteCRM Integration

**Overview**: The platform automatically syncs with SuiteCRM for lead, contact, and opportunity management.

**Accessing SuiteCRM**:

1. Open http://localhost:8080
2. Login with credentials from `.env` file
3. Default: `admin` / `changeme` (change on first login)

**Key Features**:

#### 1. Lead Management

**Create Lead Programmatically**:

```python
from integrations.crm.suitecrm_integration import SuiteCRMIntegration

crm = SuiteCRMIntegration()
crm.authenticate()

# Create lead
lead_id = crm.create_lead({
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john.doe@example.com',
    'company': 'Acme Corp',
    'phone': '+1-555-1234',
    'source': 'Website',
    'ai_score': 8.5,  # From qualification agent
    'description': 'Interested in marketing automation'
})

print(f"Lead created: {lead_id}")
```

**Update Lead Status**:

```python
# Update lead after qualification
crm.update_lead(lead_id, {
    'status': 'Qualified',
    'lead_score_c': 8.5,  # Custom field
    'next_action_c': 'Schedule discovery call'
})
```

**Convert Lead to Opportunity**:

```python
# When lead is qualified
result = crm.convert_lead(lead_id)

print(f"Contact ID: {result['contact_id']}")
print(f"Opportunity ID: {result['opportunity_id']}")
```

#### 2. Contact Management

**Create Contact**:

```python
contact_id = crm.create_contact({
    'first_name': 'Jane',
    'last_name': 'Smith',
    'email': 'jane@techcorp.com',
    'phone': '+1-555-5678',
    'title': 'CMO',
    'department': 'Marketing'
})
```

**Link Contact to Account**:

```python
# In SuiteCRM UI:
# Contacts → Select Contact → "Link to Account" → Select Account
```

#### 3. Opportunity Management

**Create Opportunity**:

```python
opp_id = crm.create_opportunity({
    'name': 'Acme Corp - Marketing Automation',
    'amount': 50000,
    'sales_stage': 'Prospecting',
    'date_closed': '2025-03-31',
    'description': 'Full marketing automation implementation'
})
```

**Update Opportunity Stage**:

```python
# As deal progresses
crm.update_opportunity(opp_id, {
    'sales_stage': 'Qualification',
    'probability': 25
})

# Later...
crm.update_opportunity(opp_id, {
    'sales_stage': 'Proposal',
    'probability': 75
})

# Won!
crm.update_opportunity(opp_id, {
    'sales_stage': 'Closed Won',
    'probability': 100
})
```

#### 4. Activity Tracking

**Log a Call**:

```python
call_id = crm.create_activity({
    'type': 'Call',
    'subject': 'Discovery call with John Doe',
    'description': 'Discussed needs and timeline. Very interested.',
    'date_start': '2025-11-20 14:00:00',
    'related_to_type': 'Lead',
    'related_to_id': lead_id,
    'status': 'Held'
})
```

**Schedule a Meeting**:

```python
meeting_id = crm.create_activity({
    'type': 'Meeting',
    'subject': 'Product demo',
    'description': 'Demo marketing automation features',
    'date_start': '2025-11-25 10:00:00',
    'related_to_type': 'Opportunity',
    'related_to_id': opp_id,
    'status': 'Planned'
})
```

**Create a Task**:

```python
task_id = crm.create_activity({
    'type': 'Task',
    'subject': 'Send proposal',
    'description': 'Customize and send pricing proposal',
    'due_date': '2025-11-22',
    'related_to_type': 'Opportunity',
    'related_to_id': opp_id,
    'status': 'Not Started'
})
```

#### 5. Searching and Filtering

**Find Leads by Email**:

```python
leads = crm.search('Lead', {
    'email1': 'john.doe@example.com'
}, fields=['id', 'name', 'status'])

for lead in leads:
    print(f"Lead: {lead['attributes']['name']}")
    print(f"Status: {lead['attributes']['status']}")
```

**Find Hot Opportunities**:

```python
opportunities = crm.search('Opportunity', {
    'sales_stage': 'Proposal',
    'probability': {'gte': 70}  # >= 70%
})
```

**Custom Field Storage**:

```yaml
# AI data stored in custom fields:
lead_score_c: 8.5                    # Qualification score
qualification_data_c: {...}          # Full BANT analysis
icp_fit_score_c: 9.2                # ICP match score
ai_insights_c: "High intent signals" # Agent insights
next_best_action_c: "Schedule demo"  # Recommended action
```

---

## Analytics & Reporting

### Metabase Dashboards

**Accessing Metabase**:

1. Open http://localhost:3000
2. First time: Create admin account
3. Connect to PostgreSQL database:
   - Host: `postgres`
   - Port: `5432`
   - Database: `instant_agency`
   - Username: From `.env` file
   - Password: From `.env` file

**Pre-built Dashboards**:

#### 1. Lead Performance Dashboard

**What it shows**:
- Total leads by source
- Conversion rates
- Average qualification scores
- Lead velocity (leads per day)
- Top performing channels

**SQL Queries**:

```sql
-- Leads by source (last 30 days)
SELECT
  source,
  COUNT(*) as lead_count,
  AVG(lead_score) as avg_score,
  COUNT(CASE WHEN status = 'converted' THEN 1 END) as converted
FROM leads
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY source
ORDER BY lead_count DESC;
```

```sql
-- Lead qualification funnel
SELECT
  CASE
    WHEN lead_score >= 8 THEN 'Hot'
    WHEN lead_score >= 6 THEN 'Warm'
    WHEN lead_score >= 3 THEN 'Cold'
    ELSE 'Disqualified'
  END as qualification,
  COUNT(*) as count,
  ROUND(AVG(lead_score), 2) as avg_score
FROM leads
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY 1
ORDER BY avg_score DESC;
```

#### 2. Agent Performance Dashboard

**What it shows**:
- Agent activity levels
- Success rates
- Average response times
- Error rates
- Tokens used (cost tracking)

**SQL Queries**:

```sql
-- Agent performance overview
SELECT
  agent_name,
  COUNT(*) as total_interactions,
  COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
  ROUND(100.0 * COUNT(CASE WHEN status = 'success' THEN 1 END) / COUNT(*), 2) as success_rate,
  AVG(response_time_ms) as avg_response_time,
  SUM(tokens_used) as total_tokens
FROM agent_interactions
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY agent_name
ORDER BY total_interactions DESC;
```

```sql
-- Agent response time trend (hourly)
SELECT
  DATE_TRUNC('hour', created_at) as hour,
  agent_name,
  AVG(response_time_ms) as avg_response_time,
  COUNT(*) as interactions
FROM agent_interactions
WHERE created_at >= CURRENT_DATE - INTERVAL '24 hours'
GROUP BY 1, 2
ORDER BY 1 DESC, 2;
```

#### 3. Campaign Performance Dashboard

**What it shows**:
- Campaign metrics (sent, opened, clicked, converted)
- Open rates and click rates
- ROI calculations
- Best performing campaigns

**SQL Queries**:

```sql
-- Campaign performance
SELECT
  name,
  type,
  status,
  sent_count,
  ROUND(100.0 * opened_count / NULLIF(sent_count, 0), 2) as open_rate,
  ROUND(100.0 * clicked_count / NULLIF(sent_count, 0), 2) as click_rate,
  ROUND(100.0 * converted_count / NULLIF(sent_count, 0), 2) as conversion_rate
FROM campaigns
WHERE started_at >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY conversion_rate DESC;
```

### Grafana Monitoring

**Accessing Grafana**:

1. Open http://localhost:3001
2. Login: `admin` / `admin` (change password)
3. Dashboards already configured

**Key Metrics**:

#### System Health
- CPU usage per container
- Memory usage
- Disk I/O
- Network traffic
- Container restart count

#### Agent Metrics
- Requests per second
- Average response time
- Error rate
- Queue depth
- Active connections

#### Business Metrics
- Leads processed
- Qualification rate
- Revenue pipeline
- Customer acquisition cost

**Setting Up Alerts**:

1. **High Error Rate Alert**:
   ```
   Condition: Error rate > 5% for 5 minutes
   Action: Send email to ops@yourcompany.com
   ```

2. **Slow Response Time Alert**:
   ```
   Condition: Avg response time > 3 seconds for 10 minutes
   Action: Slack notification to #ops-alerts
   ```

3. **Agent Down Alert**:
   ```
   Condition: Agent hasn't processed request in 15 minutes
   Action: PagerDuty incident
   ```

---

## API Reference

### Base URL

```
http://localhost:8000  # Development
https://api.your-domain.com  # Production
```

### Authentication

Currently uses basic authentication (production should use API keys):

```bash
curl -u username:password http://localhost:8000/endpoint
```

### Endpoints

#### Health Check

```bash
GET /health

Response:
{
  "status": "healthy",
  "agents_loaded": 2,
  "agents": ["sales_qualification", "marketing_prospecting"]
}
```

#### List Agents

```bash
GET /agents

Response:
{
  "agents": [
    {
      "name": "sales_qualification",
      "display_name": "Sales Qualification Agent",
      "version": "1.0.0",
      "department": "sales"
    },
    {
      "name": "marketing_prospecting",
      "display_name": "Marketing Prospecting Agent",
      "version": "1.0.0",
      "department": "marketing"
    }
  ],
  "count": 2
}
```

#### Process with Agent

```bash
POST /agent/{agent_name}/process

Body:
{
  "input_data": {
    # Agent-specific input
  }
}

Response:
{
  "success": true,
  "agent": "sales_qualification",
  "data": {
    # Agent output
  }
}
```

#### Sales Qualification

```bash
POST /sales/qualify

Body:
{
  "lead_id": 12345,
  "responses": {
    "budget": "50000",
    "timeline": "Q1 2025",
    "decision_maker": true,
    "pain_point": "Manual processes",
    "deal_value": 75000
  }
}

Response:
{
  "success": true,
  "agent": "sales_qualification",
  "data": {
    "lead_id": 12345,
    "bant_scores": {...},
    "overall_score": 8.2,
    "qualification_status": "hot",
    "next_action": "assign_to_sales_rep"
  }
}
```

#### Marketing Prospect Research

```bash
POST /marketing/research-prospect

Body:
{
  "company_name": "Acme Corp",
  "industry": "Technology"
}

Response:
{
  "success": true,
  "agent": "marketing_prospecting",
  "data": {
    "company_name": "Acme Corp",
    "company_data": {...},
    "decision_makers": [...],
    "icp_fit_score": 8.5,
    "qualifies_for_outreach": true,
    "outreach_strategy": {...}
  }
}
```

#### Get Agent Metrics

```bash
GET /metrics/{agent_name}

Response:
{
  "agent": "sales_qualification",
  "metrics": {
    "response_time": [
      {"timestamp": "2025-11-15T10:30:00", "value": 1.2},
      {"timestamp": "2025-11-15T10:45:00", "value": 1.5}
    ],
    "qualification_score": [...],
    "escalation_rate": [...]
  }
}
```

---

## Use Case Examples

### Use Case 1: Automated Lead Qualification Pipeline

**Business Goal**: Qualify 100+ inbound leads per day without human intervention.

**Setup**:

1. **Website Form** → Webhook → n8n
2. **n8n** → Marketing Prospecting Agent (research company)
3. **n8n** → Sales Qualification Agent (score lead)
4. **n8n** → CRM (create lead record)
5. **n8n** → Email (welcome message)
6. **If Hot Lead** → Slack notification to sales team

**Implementation**:

```yaml
# Import workflow: workflows/marketing/lead-capture.json
# Configure webhook on your website:
<form action="https://your-n8n-url/webhook/lead-capture" method="POST">
  <input name="name" required>
  <input name="email" type="email" required>
  <input name="company" required>
  <textarea name="message"></textarea>
  <button type="submit">Submit</button>
</form>
```

**Results**:
- 100% of leads processed automatically
- Hot leads reach sales team in < 2 minutes
- 80% reduction in manual qualification time
- Consistent qualification criteria

---

### Use Case 2: Prospecting Campaign Automation

**Business Goal**: Identify and reach out to 500 qualified prospects per month.

**Setup**:

1. **Google Sheets** with target company list
2. **n8n Schedule**: Run daily at 9 AM
3. **Loop through companies** → Prospecting Agent
4. **Filter ICP score >= 7** → Add to outreach list
5. **Generate personalized email** → Send via SendGrid
6. **Track opens/clicks** → Update CRM

**Implementation**:

```javascript
// n8n Workflow
Schedule Trigger (Daily 9 AM)
  ↓
Read Google Sheet (Companies)
  ↓
Loop (Each Company)
  ↓
Marketing Prospecting Agent
  ↓
IF (icp_fit_score >= 7)
  ↓
Create CRM Lead
  ↓
Generate Personalized Email
  ↓
Send Email (SendGrid)
  ↓
Log Activity in CRM
```

**Results**:
- 500 prospects researched automatically
- 200 high-fit prospects identified (40% hit rate)
- 200 personalized emails sent
- 25% open rate, 5% response rate
- 10 qualified opportunities created

---

### Use Case 3: Content Marketing Automation

**Business Goal**: Publish 2 blog posts per week with social media promotion.

**Setup**:

1. **Content Calendar** in Google Sheets
2. **Monday 8 AM**: Agent generates blog post draft
3. **Slack notification** to content manager for review
4. **Approval** → Publish to WordPress
5. **Auto-generate** social media posts for LinkedIn, Twitter, Facebook
6. **Schedule posts** throughout the week
7. **Track performance** in Metabase

**Implementation**:

```javascript
// n8n Workflow
Schedule Trigger (Monday, Thursday 8 AM)
  ↓
Read Content Calendar (Next Topic)
  ↓
Content Writing Agent (Generate Blog Post)
  ↓
SEO Optimization Check
  ↓
Slack Approval Request
  ↓
IF (Approved)
  ↓
Publish to WordPress
  ↓
Social Media Agent (Generate Posts)
  ↓
Schedule to Buffer/Hootsuite
  ↓
Log to Analytics Database
```

**Results**:
- 8 blog posts per month automatically
- 90% approval rate (minimal edits needed)
- 32 social media posts per month
- 50% reduction in content creation time
- Consistent publishing schedule

---

### Use Case 4: Customer Support Triage

**Business Goal**: Automatically categorize and route 200+ support tickets per day.

**Setup**:

1. **Support Email** → n8n Webhook
2. **Parse email** content
3. **Support Agent** → Classify issue type
4. **If Simple** → Auto-respond with FAQ
5. **If Complex** → Create ticket, assign to specialist
6. **Track resolution** time and customer satisfaction

**Implementation**:

```javascript
// n8n Workflow
Email Trigger (support@yourcompany.com)
  ↓
Extract Email Content
  ↓
Support Triage Agent (Classify)
  ↓
SWITCH (Issue Type)

  CASE: "FAQ" (Can auto-resolve)
    → FAQ Agent (Generate Answer)
    → Send Email Response
    → Close Ticket

  CASE: "Technical" (Needs specialist)
    → Create Ticket in CRM
    → Assign to Technical Support Team
    → Send "Received" Auto-reply

  CASE: "Billing" (Needs accounting)
    → Create Ticket
    → Assign to Billing Team
    → Flag as "Urgent" if contains "refund"

  CASE: "Feature Request"
    → Log to Product Board
    → Send "Thank you" Response
```

**Results**:
- 60% of tickets auto-resolved
- 90% categorization accuracy
- <5 minute initial response time
- 40% reduction in support workload

---

### Use Case 5: Sales Pipeline Optimization

**Business Goal**: Never let a hot lead go cold, automate follow-ups.

**Setup**:

1. **Daily scan** of CRM opportunities
2. **Check for stalled deals** (no activity in 7 days)
3. **Generate personalized** follow-up email
4. **Send email** automatically
5. **If no response** in 3 days → Notify sales rep
6. **Track** re-engagement rates

**Implementation**:

```sql
-- Daily query to find stalled deals
SELECT
  o.id,
  o.name,
  o.amount,
  c.email,
  o.sales_stage,
  CURRENT_DATE - MAX(a.date) as days_stale
FROM opportunities o
JOIN contacts c ON o.contact_id = c.id
LEFT JOIN activities a ON a.related_to_id = o.id
WHERE o.sales_stage IN ('Qualification', 'Proposal', 'Negotiation')
  AND o.status != 'Closed'
GROUP BY o.id, o.name, o.amount, c.email, o.sales_stage
HAVING CURRENT_DATE - MAX(a.date) >= 7;
```

```javascript
// n8n Workflow
Schedule Trigger (Daily 9 AM)
  ↓
Query Database (Stalled Deals)
  ↓
Loop (Each Deal)
  ↓
Sales Qualification Agent (Re-qualify)
  ↓
Generate Follow-up Email
  ↓
Personalize for Deal Stage
  ↓
Send Email
  ↓
Log Activity in CRM
  ↓
Set Reminder (3 days)
  ↓
IF (No Response after 3 days)
  ↓
Notify Sales Rep via Slack
```

**Results**:
- 30% of stalled deals re-engaged
- $500K pipeline saved per quarter
- 15% improvement in close rates
- Zero deals forgotten

---

## Troubleshooting

### Common Issues

#### Agent Not Responding

**Symptom**: API returns timeout or no response

**Solution**:
```bash
# Check agent service is running
docker-compose ps agent-service

# Check agent logs
docker-compose logs -f agent-service

# Restart agent service
docker-compose restart agent-service

# Check Hugging Face API key is valid
curl -H "Authorization: Bearer $HUGGINGFACE_API_KEY" \
  https://huggingface.co/api/whoami
```

#### Workflow Execution Failed

**Symptom**: n8n workflow shows red error node

**Solution**:
1. Click on the failed node
2. View error message in execution panel
3. Common fixes:
   - Invalid credentials: Reconfigure in n8n Settings
   - API rate limit: Add "Wait" node or reduce frequency
   - Invalid data format: Check "Set" node transformation
   - Timeout: Increase execution timeout in workflow settings

#### CRM Connection Error

**Symptom**: Cannot create/update CRM records

**Solution**:
```bash
# Check SuiteCRM is running
curl http://localhost:8080

# Verify API credentials
python integrations/crm/suitecrm_integration.py

# Check database connection
docker-compose exec postgres psql -U instant_agency

# Restart CRM
docker-compose restart suitecrm
```

#### Low Qualification Scores

**Symptom**: All leads getting low scores unexpectedly

**Solution**:
- Review agent configuration
- Check if scoring weights are balanced
- Lower thresholds temporarily
- Add more context to input data
- Review agent prompts
- Check if model API is working correctly

---

## Next Steps

### Getting Started Checklist

- [ ] Complete setup and access all dashboards
- [ ] Import and test lead capture workflow
- [ ] Qualify 5 test leads manually
- [ ] Configure your ICP in prospecting agent
- [ ] Research 10 prospects
- [ ] Generate 3 pieces of content
- [ ] Set up CRM automation
- [ ] Create first analytics dashboard
- [ ] Build custom workflow for your use case

### Learning Resources

- **Video Tutorials**: Coming soon
- **Community Forum**: GitHub Discussions
- **API Documentation**: /docs/api (coming soon)
- **Workflow Library**: /workflows/examples

### Getting Help

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check /docs directory
- **Support Email**: support@instant-agency.ai
- **Community**: Join our Slack (coming soon)

---

**Last Updated**: November 2025
**Version**: 0.1.0-alpha

For the latest updates, visit: https://github.com/Humasci/Instant-Agency
