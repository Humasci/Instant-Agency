# Phase 3 Setup Guide: Cross-Department Orchestration

**Phase 3** introduces multi-agent collaboration with 6 advanced agents working together to deliver cohesive customer journeys.

## 📋 Overview

Phase 3 delivers:
- **Multi-agent orchestration** for complex workflows
- **RAG-enhanced research** with semantic search
- **Advanced sales strategies** (MEDDIC, objection handling, campaigns)
- **End-to-end marketing campaigns** across multiple channels
- **Customer success management** (health scoring, onboarding, expansion)
- **Analytics & reporting** (ROI, performance, executive dashboards)

**Total Operational Agents**: 15 (2 base + 2 Phase 1 + 5 Phase 2 + 6 Phase 3)

## 🚀 Quick Start

### Prerequisites
```bash
# Completed Phase 1 & Phase 2
# Redis and PostgreSQL running
# Hugging Face API key configured
```

### Start the Service
```bash
cd agents
python main.py
```

Expected output:
```
✓ All agents initialized successfully
  Loaded agents (15): sales_qualification, marketing_prospecting,
  phase1_prospect, phase1_faq, phase2_sales_pitch, phase2_content_writer,
  phase2_intent_classifier, phase2_email_personalizer, phase2_social_media,
  phase3_orchestrator, phase3_rag_research, phase3_sales_strategist,
  phase3_marketing_campaign, phase3_customer_success, phase3_analytics
```

### Run Tests
```bash
cd scripts
python test_phase3_agents.py
```

## 🤖 Phase 3 Agents

### 1. Orchestrator Agent
**Purpose**: Coordinate multi-agent workflows
**Endpoint**: `POST /phase3/orchestrate`

**Workflow Types**:
- `lead_nurture` - Automated lead nurturing with engagement-based routing
- `sales_cycle` - End-to-end sales process management
- `support` - Customer support triage and routing
- `content_marketing` - Content creation and distribution pipeline

**Example**:
```bash
curl -X POST http://localhost:8000/phase3/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "lead_001",
    "workflow_type": "lead_nurture",
    "journey_stage": "consideration",
    "engagement_score": 85,
    "current_state": {
      "name": "Sarah Chen",
      "company": "TechCorp",
      "industry": "SaaS"
    }
  }'
```

**Response**:
```json
{
  "success": true,
  "workflow_type": "lead_nurture",
  "steps_executed": [
    {"agent": "intent_classifier", "action": "classify_intent"}
  ],
  "next_actions": [
    {"agent": "sales_pitch", "action": "generate_personalized_pitch", "priority": "high"},
    {"agent": "human_sales", "action": "schedule_call", "priority": "high"}
  ],
  "human_handoff": false,
  "context": {
    "engagement_score": 85,
    "recommendation": "High engagement - activate sales team"
  }
}
```

---

### 2. RAG Research Agent
**Purpose**: Semantic search and research with context retrieval
**Endpoint**: `POST /phase3/research`
**Model**: `sentence-transformers/all-mpnet-base-v2` (embeddings)

**Features**:
- Semantic similarity search
- Source attribution and citations
- Confidence scoring
- Context compilation for downstream agents

**Example**:
```bash
curl -X POST http://localhost:8000/phase3/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AI automation benefits for small businesses",
    "depth": "standard",
    "max_results": 5,
    "include_citations": true
  }'
```

**Response**:
```json
{
  "success": true,
  "query": "AI automation benefits for small businesses",
  "confidence": 0.82,
  "key_findings": [
    "AI Agent Benefits for Small Business: 40-60%",
    "Lead Qualification Best Practices: 85%+",
    "Content Marketing ROI: 3x"
  ],
  "sources": [
    {
      "title": "AI Agent Benefits for Small Business",
      "source": "Internal Research",
      "relevance_score": 0.95
    }
  ],
  "context_for_generation": {
    "findings": [...],
    "supporting_facts": [...],
    "confidence": 0.82
  }
}
```

---

### 3. Sales Strategist Agent
**Purpose**: Advanced B2B sales workflows (MEDDIC, objections, campaigns)
**Endpoint**: `POST /phase3/sales-strategy`
**Model**: `mistralai/Mistral-7B-Instruct-v0.1`

**Actions**:
- `analyze_deal` - Comprehensive deal health analysis
- `handle_objection` - Objection handling with frameworks
- `plan_campaign` - Multi-touch outreach campaigns
- `qualify` - Advanced qualification (MEDDIC)
- `competitive_battle_card` - Competitive positioning

**Example - Deal Analysis**:
```bash
curl -X POST http://localhost:8000/phase3/sales-strategy \
  -H "Content-Type: application/json" \
  -d '{
    "action": "analyze_deal",
    "deal_data": {
      "value": 50000,
      "stage": "proposal",
      "days_in_stage": 12,
      "budget_confirmed": true
    },
    "prospect_data": {
      "company": "TechCorp Inc",
      "champion_identified": true
    },
    "stakeholders": [
      {"name": "CTO", "role": "champion"},
      {"name": "CFO", "role": "economic_buyer"}
    ]
  }'
```

**Response**:
```json
{
  "success": true,
  "deal_health": {
    "score": 85,
    "status": "healthy",
    "win_probability": 0.72
  },
  "risks": [],
  "next_actions": [
    {
      "action": "Present proposal to stakeholders",
      "priority": "critical",
      "timeline": "Next 3 days"
    }
  ],
  "strategy": "Strong opportunity with TechCorp Inc. Focus on closing..."
}
```

---

### 4. Marketing Campaign Agent
**Purpose**: Multi-channel campaign planning and execution
**Endpoint**: `POST /phase3/marketing-campaign`

**Campaign Types**:
- `awareness` - Brand visibility and reach
- `consideration` - Trust building and engagement
- `conversion` - Lead generation and sales
- `retention` - Customer engagement and upsell
- `advocacy` - Referral and community building

**Example**:
```bash
curl -X POST http://localhost:8000/phase3/marketing-campaign \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_type": "conversion",
    "goal": "Generate 500 qualified leads",
    "target_audience": {
      "industry": "SaaS",
      "company_size": "50-200 employees"
    },
    "budget": 15000,
    "duration_days": 30,
    "channels": ["email", "social_media", "content", "paid_ads"]
  }'
```

**Response**:
```json
{
  "success": true,
  "campaign_type": "conversion",
  "budget_allocation": {
    "email": {"budget": 5250, "percentage": 35},
    "paid_ads": {"budget": 6000, "percentage": 40},
    "content": {"budget": 2250, "percentage": 15}
  },
  "content_calendar": [
    {
      "week": 1,
      "activities": [
        {"channel": "email", "content": "Campaign launch announcement"},
        {"channel": "social_media", "content": "Teaser posts"}
      ]
    }
  ],
  "ab_tests": [
    {
      "channel": "email",
      "element": "subject_line",
      "variant_a": "Question-based",
      "variant_b": "Value proposition"
    }
  ],
  "expected_roi": {
    "investment": 15000,
    "expected_return": 75000,
    "roi_multiplier": "5.0x",
    "roi_percentage": 400
  }
}
```

---

### 5. Customer Success Agent
**Purpose**: Retention, onboarding, health scoring, expansion
**Endpoint**: `POST /phase3/customer-success`

**Actions**:
- `health_check` - Calculate customer health score
- `onboard` - Create onboarding plan
- `intervention` - At-risk customer intervention
- `expansion_opportunity` - Identify upsell/cross-sell
- `renewal` - Renewal strategy and planning

**Example - Health Check**:
```bash
curl -X POST http://localhost:8000/phase3/customer-success \
  -H "Content-Type: application/json" \
  -d '{
    "action": "health_check",
    "customer_id": "cust_001",
    "customer_data": {
      "logins_last_30": 18,
      "nps_score": 75,
      "support_tickets_last_30": 2
    },
    "usage_data": {
      "active_days_last_30": 22,
      "features_used": 8,
      "total_features": 10
    },
    "account_data": {
      "mrr": 1500,
      "mrr_growth_percentage": 15
    }
  }'
```

**Response**:
```json
{
  "success": true,
  "health_score": 82.5,
  "health_status": "healthy",
  "risk_level": "low",
  "breakdown": {
    "product_usage": 85,
    "engagement": 78,
    "support": 90,
    "satisfaction": 75,
    "revenue": 85
  },
  "issues": [],
  "recommended_actions": [
    {
      "action": "Continue standard success cadence",
      "priority": "normal"
    }
  ]
}
```

---

### 6. Analytics Agent
**Purpose**: Data analysis, reporting, ROI calculation
**Endpoint**: `POST /phase3/analytics`

**Report Types**:
- `agent_performance` - Individual agent metrics
- `customer_journey` - Funnel and conversion analytics
- `roi` - ROI calculation and cost analysis
- `executive_summary` - High-level dashboard

**Example - Executive Summary**:
```bash
curl -X POST http://localhost:8000/phase3/analytics \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "executive_summary",
    "time_period": "monthly"
  }'
```

**Response**:
```json
{
  "success": true,
  "key_metrics": {
    "total_interactions": 8126,
    "leads_generated": 423,
    "pipeline_value": 211500,
    "revenue": 420000,
    "roi_percentage": 7852,
    "agent_quality_score": 86.3
  },
  "trends": {
    "interactions": {"current": 8126, "previous": 7450, "change": "+9.1%"},
    "revenue": {"current": 420000, "previous": 380000, "change": "+10.5%"}
  },
  "achievements": [
    "7852% ROI - 80.0x return on investment",
    "423 qualified leads generated",
    "$211,500 in pipeline value created"
  ],
  "alerts": [],
  "recommendations": [
    {
      "area": "Revenue Expansion",
      "action": "Scale successful campaigns to capture 20% more leads",
      "impact": "high",
      "effort": "low"
    }
  ]
}
```

---

## 🔄 Multi-Agent Workflows

### Example 1: Lead-to-Customer Journey
```python
import requests

# Step 1: Orchestrate lead nurture
workflow = requests.post('http://localhost:8000/phase3/orchestrate', json={
    'customer_id': 'lead_001',
    'workflow_type': 'lead_nurture',
    'engagement_score': 85
}).json()

# Step 2: If high engagement, analyze deal
if workflow['data']['context']['engagement_score'] >= 70:
    deal_analysis = requests.post('http://localhost:8000/phase3/sales-strategy', json={
        'action': 'analyze_deal',
        'deal_data': {'value': 30000, 'stage': 'qualification'},
        'prospect_data': {'company': 'TechCorp'}
    }).json()

# Step 3: Create personalized pitch (using Phase 2)
pitch = requests.post('http://localhost:8000/phase2/generate-sales-pitch', json={
    'prospect_name': 'Sarah Chen',
    'company': 'TechCorp',
    'pain_points': 'Manual processes'
}).json()

# Step 4: Send email (using Phase 2)
email = requests.post('http://localhost:8000/phase2/personalize-email', json={
    'recipient_name': 'Sarah Chen',
    'company': 'TechCorp',
    'intent': 'demo'
}).json()
```

### Example 2: Content Marketing Campaign
```python
# Step 1: Research topic
research = requests.post('http://localhost:8000/phase3/research', json={
    'query': 'AI automation for small businesses',
    'depth': 'deep',
    'max_results': 10
}).json()

# Step 2: Write content using research
content = requests.post('http://localhost:8000/phase2/write-content', json={
    'topic': research['data']['query'],
    'key_points': research['data']['key_findings'][:3],
    'word_count': 800
}).json()

# Step 3: Create social posts
social = requests.post('http://localhost:8000/phase2/create-social-posts', json={
    'content': content['data']['content'],
    'platforms': ['linkedin', 'twitter']
}).json()

# Step 4: Plan distribution campaign
campaign = requests.post('http://localhost:8000/phase3/marketing-campaign', json={
    'campaign_type': 'awareness',
    'budget': 5000,
    'channels': ['email', 'social_media', 'content']
}).json()
```

### Example 3: Customer Success Lifecycle
```python
# Step 1: Health check for all customers
for customer in customers:
    health = requests.post('http://localhost:8000/phase3/customer-success', json={
        'action': 'health_check',
        'customer_id': customer['id'],
        'customer_data': customer['data'],
        'usage_data': customer['usage'],
        'account_data': customer['account']
    }).json()

    # Step 2: If at-risk, create intervention plan
    if health['data']['health_status'] == 'at_risk':
        intervention = requests.post('http://localhost:8000/phase3/customer-success', json={
            'action': 'intervention',
            'customer_id': customer['id'],
            'customer_data': customer['data']
        }).json()

    # Step 3: If healthy, identify expansion opportunities
    elif health['data']['health_status'] == 'healthy':
        expansion = requests.post('http://localhost:8000/phase3/customer-success', json={
            'action': 'expansion_opportunity',
            'customer_id': customer['id'],
            'customer_data': customer['data'],
            'usage_data': customer['usage'],
            'account_data': customer['account']
        }).json()
```

---

## 📊 Performance & Architecture

### Agent Collaboration
Phase 3 agents work together through:
- **Shared Context Store**: Agents share customer context via orchestrator
- **Event-Driven Workflows**: Triggers based on customer actions/state
- **Human-in-the-Loop**: Automatic escalation for high-value/complex scenarios

### Escalation Triggers
- Deal size > $10,000
- Customer health score < 60
- AI confidence < 60%
- Urgent/critical keywords detected
- Complex requests (enterprise, custom integration)

### Response Times
| Agent | Avg Response | Use Case |
|-------|--------------|----------|
| Orchestrator | <100ms | Workflow routing (rule-based) |
| RAG Research | 500ms-2s | Semantic search |
| Sales Strategist | 3-8s | Strategy generation |
| Marketing Campaign | 1-3s | Campaign planning (rule-based) |
| Customer Success | 200ms-1s | Health scoring (rule-based) |
| Analytics | 100-500ms | Report generation (aggregation) |

---

## 🔧 Best Practices

1. **Workflow Selection**
   - Use orchestrator for complex multi-step journeys
   - Direct agent calls for simple, single-purpose actions

2. **Context Management**
   - Always provide customer_id for state tracking
   - Include interaction_history for better decisions

3. **Human Handoff**
   - Monitor `human_handoff` flag in responses
   - Escalate high-value deals ($10k+) to humans
   - Review AI-generated content before sending

4. **Performance Optimization**
   - Cache research results for frequently asked queries
   - Batch analytics reports for multiple customers
   - Use webhooks for async long-running workflows

5. **Testing & Validation**
   - A/B test campaign strategies
   - Monitor health scores and intervene early
   - Track ROI metrics continuously

---

## 🚀 Next Steps

**Phase 4 (Months 7-12)** will add:
- Voice-enabled agents (Wav2Vec2 STT, FastSpeech2 TTS)
- Hyper-realistic digital avatars (D-ID, HeyGen)
- Model fine-tuning with custom data
- Multilingual support (mBART)
- Advanced analytics and A/B testing
- Real-time conversation agents

See [IMPLEMENTATION_BLUEPRINT.md](IMPLEMENTATION_BLUEPRINT.md) for Phase 4 details.

---

## 💡 Troubleshooting

**Issue**: "Agent not found" error
**Solution**: Ensure all Phase 3 agents are initialized. Check agent service logs.

**Issue**: Orchestrator not routing correctly
**Solution**: Verify `workflow_type` matches supported types. Provide `journey_stage` and `engagement_score`.

**Issue**: Low research confidence scores
**Solution**: Expand knowledge base or use more specific queries.

**Issue**: Health scores seem inaccurate
**Solution**: Calibrate health score thresholds based on your customer data.

---

**Total Agents**: 15 operational agents
**Test Suite**: `scripts/test_phase3_agents.py`
**API Documentation**: http://localhost:8000/docs

**Phase 3 Complete!** Ready for Phase 4 optimization and scale. 🎉
