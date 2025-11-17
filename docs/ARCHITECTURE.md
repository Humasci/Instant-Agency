# SIX3 Agency - System Architecture

## Table of Contents
1. [Overview](#overview)
2. [System Components](#system-components)
3. [Data Flow](#data-flow)
4. [Agent Architecture](#agent-architecture)
5. [Integration Patterns](#integration-patterns)
6. [Scalability & Performance](#scalability--performance)
7. [Security Architecture](#security-architecture)

## Overview

SIX3 Agency follows a microservices-based architecture with event-driven communication between components. The system is designed for:

- **Modularity**: Each component can be developed, deployed, and scaled independently
- **Resilience**: Failures in one component don't cascade to others
- **Flexibility**: Easy to swap or upgrade individual components
- **Observability**: Comprehensive logging, monitoring, and tracing

## System Components

### 1. Workflow Orchestration Layer (n8n)

**Purpose**: Central nervous system connecting all components

**Responsibilities**:
- Route requests to appropriate agents
- Manage workflow state and execution
- Handle retries and error recovery
- Coordinate multi-step processes
- Trigger scheduled tasks

**Configuration**:
```yaml
n8n:
  deployment: docker
  persistence: postgres
  execution_mode: queue
  workers: 4
  webhook_url: https://workflows.six3.agency
```

### 2. AI Agent Layer

**Purpose**: Intelligent automation and decision-making

**Components**:

#### a) Marketing Agents
- **Prospecting Agent**: Research and identify leads
- **Engagement Agent**: Personalize and send outreach
- **Nurture Agent**: Follow-up sequences and relationship building
- **Analytics Agent**: Campaign performance analysis

#### b) Sales Agents
- **Qualification Agent**: Assess lead fit and readiness
- **Discovery Agent**: Extract needs and pain points
- **Proposal Agent**: Generate customized proposals
- **Closing Agent**: Handle objections and finalize deals

#### c) Content Agents
- **Research Agent**: Topic research and trend analysis
- **Writing Agent**: Content generation and optimization
- **Social Media Agent**: Platform-specific content adaptation
- **SEO Agent**: Keyword optimization and meta-data

#### d) Support Agents
- **Triage Agent**: Categorize and route support requests
- **Resolution Agent**: Solve common issues autonomously
- **Escalation Agent**: Identify complex cases for human handoff
- **Feedback Agent**: Collect and analyze customer satisfaction

#### e) Operations Agents
- **Data Agent**: ETL and data quality management
- **Reporting Agent**: Generate insights and dashboards
- **Optimization Agent**: A/B testing and performance tuning
- **Monitoring Agent**: System health and alerting

**Tech Stack**:
- **LLM Provider**: Hugging Face Inference API
- **Agent Framework**: CrewAI for orchestration, LangChain for chains
- **Vector Database**: Chroma/Qdrant for embeddings
- **Memory**: Redis for short-term, PostgreSQL for long-term

### 3. Data Layer

**Purpose**: Centralized data storage and management

**Components**:

#### a) CRM (SuiteCRM/Odoo)
- Contact and company management
- Deal pipeline and stages
- Activity tracking
- Custom fields and entities

#### b) Database (PostgreSQL)
- Agent conversation history
- Workflow execution logs
- Analytics data warehouse
- Configuration and settings

#### c) Vector Database (Chroma)
- Document embeddings
- Semantic search
- RAG (Retrieval Augmented Generation)

#### d) Cache (Redis)
- Session management
- Rate limiting
- Real-time agent state
- Job queues

### 4. Integration Layer

**Purpose**: Connect with external services and APIs

**Integrations**:
- Email (SMTP/IMAP, Gmail API, SendGrid)
- Calendar (Google Calendar, Outlook)
- Social Media (LinkedIn, Twitter, Facebook APIs)
- Communication (Slack, Discord, Telegram)
- Payment (Stripe, PayPal)
- Analytics (Google Analytics, Mixpanel)

**Pattern**: Adapter pattern for consistent interface

### 5. Analytics & Monitoring Layer

**Purpose**: Observability and business intelligence

**Components**:

#### a) Business Analytics (Metabase)
- KPI dashboards
- Revenue analytics
- Customer journey analysis
- Agent performance metrics

#### b) Web Analytics (Matomo)
- Website traffic and behavior
- Conversion tracking
- Attribution modeling

#### c) Application Monitoring (Prometheus + Grafana)
- System metrics (CPU, memory, disk)
- Application performance (response times, error rates)
- Custom agent metrics

#### d) Logging (ELK Stack - Elasticsearch, Logstash, Kibana)
- Centralized log aggregation
- Full-text search
- Error tracking and debugging

### 6. User Interface Layer

**Purpose**: Human oversight and control

**Components**:
- **Admin Dashboard**: System configuration and monitoring
- **Agent Control Panel**: Start/stop agents, adjust parameters
- **Analytics Dashboard**: Business metrics and insights
- **CRM Interface**: Customer data and pipeline management

## Data Flow

### 1. Inbound Lead Flow

```
External Source → n8n Webhook → Lead Classification Agent → CRM
                                         ↓
                                  Enrichment Agent → External APIs
                                         ↓
                                  Qualification Agent → Score & Route
                                         ↓
                      Marketing Nurture Agent ← OR → Sales Engagement Agent
```

### 2. Support Request Flow

```
Customer → Support Channel (Email/Chat/Phone) → n8n Workflow
                                                      ↓
                                                Triage Agent
                                                      ↓
                                    ┌─────────────────┴─────────────────┐
                                    ↓                                   ↓
                            Resolution Agent                    Escalation Agent
                            (Auto-resolve)                    (Human handoff)
                                    ↓                                   ↓
                            Close Ticket                        Create Task
                                    ↓                                   ↓
                            Feedback Agent                      Notify Team
```

### 3. Content Creation Flow

```
Content Request → n8n Trigger → Research Agent → Gather Sources
                                        ↓
                                 Writing Agent → Generate Draft
                                        ↓
                                   SEO Agent → Optimize
                                        ↓
                            Human Approval (Optional)
                                        ↓
                              Social Media Agent → Publish
                                        ↓
                              Analytics Agent → Track Performance
```

## Agent Architecture

### Agent Anatomy

Each agent follows a consistent structure:

```python
class Agent:
    """Base agent class"""

    def __init__(self, config):
        self.llm = self._init_llm(config)
        self.memory = self._init_memory(config)
        self.tools = self._init_tools(config)
        self.prompts = self._load_prompts(config)

    def process(self, input_data):
        """Main processing logic"""
        # 1. Retrieve context from memory
        context = self.memory.retrieve(input_data)

        # 2. Build prompt with context
        prompt = self.prompts.build(input_data, context)

        # 3. Execute LLM call
        response = self.llm.generate(prompt)

        # 4. Use tools if needed
        if self._needs_tools(response):
            response = self._execute_tools(response)

        # 5. Store in memory
        self.memory.store(input_data, response)

        # 6. Return result
        return self._format_output(response)

    def _needs_tools(self, response):
        """Determine if tools are needed"""
        pass

    def _execute_tools(self, response):
        """Execute required tools"""
        pass
```

### Agent Communication

Agents communicate via:
1. **Direct**: Synchronous function calls (within same workflow)
2. **Async**: Message queue (Redis/RabbitMQ) for long-running tasks
3. **Event-driven**: Publish/subscribe for notifications
4. **Orchestrated**: n8n workflows for complex multi-agent scenarios

### Memory Management

**Short-term Memory** (Redis):
- Current conversation context
- Recent actions and outcomes
- Active workflow state
- TTL: 24 hours

**Long-term Memory** (PostgreSQL):
- Historical interactions
- Learned preferences
- Performance metrics
- Indefinite retention with archival

**Semantic Memory** (Vector DB):
- Company knowledge base
- Product documentation
- Past successful interactions
- Retrieved via similarity search

## Integration Patterns

### 1. Webhook-based Integration

```javascript
// n8n webhook node
{
  "method": "POST",
  "path": "/webhook/new-lead",
  "responseMode": "onReceived",
  "authentication": "apiKey"
}
```

### 2. API Polling

```javascript
// n8n schedule trigger + HTTP request
{
  "schedule": "*/5 * * * *", // Every 5 minutes
  "endpoint": "https://api.example.com/leads",
  "method": "GET"
}
```

### 3. Database Trigger

```sql
-- PostgreSQL trigger for new CRM entries
CREATE TRIGGER new_contact_trigger
AFTER INSERT ON contacts
FOR EACH ROW
EXECUTE FUNCTION notify_n8n_webhook();
```

### 4. Event Streaming

```python
# Redis pub/sub for real-time events
redis_client.publish('agent-events', {
    'type': 'lead_qualified',
    'lead_id': 12345,
    'score': 85,
    'timestamp': datetime.now()
})
```

## Scalability & Performance

### Horizontal Scaling

**n8n Workers**:
- Multiple worker containers
- Queue-based execution
- Load balancing via Redis

**AI Agents**:
- Stateless design
- Container-based deployment
- Auto-scaling based on queue depth

**Databases**:
- PostgreSQL: Read replicas
- Redis: Cluster mode
- Vector DB: Distributed setup

### Performance Optimization

**Caching Strategy**:
```
L1: In-memory cache (Agent-level) - 1s TTL
L2: Redis (Cross-agent) - 5min TTL
L3: PostgreSQL (Persistent) - No TTL
```

**Rate Limiting**:
- Per-agent API quotas
- Token bucket algorithm
- Graceful degradation

**Batch Processing**:
- Bulk operations for CRM updates
- Batch embeddings generation
- Scheduled report generation

### Load Distribution

```
                    Load Balancer
                         |
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
    n8n Worker 1    n8n Worker 2    n8n Worker 3
        ↓                ↓                ↓
    ┌───┴────────────────┴────────────────┴───┐
    │          Redis Job Queue                 │
    └───┬────────────────┬────────────────┬───┘
        ↓                ↓                ↓
   Agent Pool 1     Agent Pool 2     Agent Pool 3
```

## Security Architecture

### Authentication & Authorization

**Layers**:
1. **External**: OAuth2, API keys
2. **Internal**: JWT tokens, service accounts
3. **Agent**: Role-based access control

**Implementation**:
```yaml
agent_permissions:
  marketing_agent:
    - read:contacts
    - write:campaigns
    - read:analytics

  sales_agent:
    - read:contacts
    - write:deals
    - read:proposals
    - send:emails

  support_agent:
    - read:tickets
    - write:tickets
    - read:knowledge_base
```

### Data Protection

**Encryption**:
- At rest: AES-256
- In transit: TLS 1.3
- Secrets: HashiCorp Vault / Docker Secrets

**PII Handling**:
- Anonymization for analytics
- Encryption for storage
- Access logging and auditing
- GDPR compliance (right to deletion)

**Network Security**:
- VPC isolation
- Private subnets for databases
- API gateway for external access
- WAF for web protection

### Audit & Compliance

**Logging**:
- All agent actions logged
- User access tracking
- Data modification history
- Anomaly detection

**Compliance Features**:
- Data retention policies
- Automated data deletion
- Consent management
- Export capabilities

## Deployment Architecture

### Development Environment

```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    environment:
      - NODE_ENV=development

  postgres:
    image: postgres:15

  redis:
    image: redis:7-alpine

  # ... other services
```

### Production Environment

**Infrastructure**:
- Kubernetes for orchestration
- Docker for containerization
- Terraform for IaC
- ArgoCD for GitOps

**High Availability**:
- Multi-zone deployment
- Automated failover
- Backup and disaster recovery
- Zero-downtime deployments

**Monitoring**:
- Health checks
- Liveness probes
- Resource alerts
- Performance profiling

## Digital Avatar Layer

**Purpose**: Human-like visual AI agents for client-facing interactions

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Client Browser/App                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  WebRTC Video Stream (Avatar Video + Audio)      │   │
│  │  Microphone Input (Client Speech)                │   │
│  └────────────────┬─────────────────────────────────┘   │
└───────────────────┼──────────────────────────────────────┘
                    │
┌───────────────────▼──────────────────────────────────────┐
│         Avatar Interaction Service (Real-Time)           │
│                                                           │
│  ┌────────────┐  ┌──────────┐  ┌─────────┐  ┌────────┐ │
│  │ Speech-to- │→ │   LLM    │→ │ Text-to-│→ │ Avatar │ │
│  │   Text     │  │ (Mistral)│  │ Speech  │  │ Video  │ │
│  │ (Wav2Vec2) │  │          │  │ (11Labs)│  │ (D-ID) │ │
│  └────────────┘  └──────────┘  └─────────┘  └────────┘ │
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Context Manager (Conversation History, CRM Data)│  │
│  └───────────────────────────────────────────────────┘  │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
      ┌────────────────┐
      │  n8n Workflow  │ → Triggers, logging, escalation
      │  Orchestration │
      └────────────────┘
```

### Components

#### 1. Avatar Video Service
- **Provider**: D-ID, HeyGen, or self-hosted (SadTalker)
- **Function**: Generate lifelike talking avatar videos in real-time
- **Models**: Pre-built avatar personas (Sarah, Marcus, Priya)
- **Customization**: Brand-specific avatars possible

#### 2. Voice Synthesis
- **Provider**: ElevenLabs (recommended) or Hugging Face TTS
- **Function**: Convert LLM text responses to natural speech
- **Features**: Voice cloning, emotion control, multilingual

#### 3. Speech Recognition
- **Model**: `facebook/wav2vec2-large-960h-lv60-self`
- **Function**: Transcribe client speech in real-time
- **Latency**: <500ms for responsive conversation

#### 4. Conversational AI
- **Model**: Fine-tuned Mistral-7B or GPT-Neo-2.7B
- **Prompts**: Persona-specific (see `agents/prompts/avatar/`)
- **Context**: Full CRM history, previous interactions
- **Escalation**: Automatic handoff to human when needed

#### 5. WebRTC Streaming
- **Platform**: Jitsi Meet (open-source) or Daily.co (cloud)
- **Function**: Stream avatar video to client browser
- **Features**: Screen sharing, recording, multi-party calls

### Avatar Personas

1. **Sarah Williams** - Senior Sales Consultant
   - Discovery calls, demos, closing
   - Warm, consultative, empathetic

2. **Marcus Rodriguez** - Technical Solutions Architect
   - Technical deep-dives, implementation
   - Knowledgeable, patient, detail-oriented

3. **Priya Sharma** - Customer Success Manager
   - Onboarding, training, relationship nurturing
   - Supportive, enthusiastic, proactive

### Integration Points

```yaml
avatar_service:
  endpoints:
    - POST /api/avatar/start-call
    - POST /api/avatar/request-takeover
    - GET /api/avatar/call-status/{call_id}
    - POST /api/avatar/end-call

  n8n_integration:
    - Trigger on calendar event
    - Webhook for call progress updates
    - Escalation notifications to Slack
    - Post-call CRM logging

  crm_integration:
    - Fetch contact data pre-call
    - Update contact with call notes
    - Create follow-up tasks
    - Log call summary
```

### Performance Metrics

- **Latency**: <1 second response time
- **Uptime**: >99.5% availability
- **Escalation Rate**: <20% of calls
- **Satisfaction**: Target >4.2/5 rating

See [DIGITAL_AVATARS.md](DIGITAL_AVATARS.md) for complete implementation guide.

---

## Future Enhancements

1. **Real-time Collaboration**: WebSocket-based agent monitoring
2. **Mobile Access**: Progressive Web App for on-the-go management
3. **Multi-Avatar Team Calls**: Coordinated presentations with multiple avatars
4. **Advanced ML**: Custom model fine-tuning and deployment
5. **Multi-tenancy**: Support for multiple organizations
6. **Marketplace**: Community-contributed agents and workflows
7. **Emotion AI**: Advanced sentiment detection and empathetic responses

---

**Document Version**: 1.0
**Last Updated**: November 2025
**Maintained By**: SIX3 Agency Team
