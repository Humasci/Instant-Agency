# SIX3 Agency Service Delivery Platform

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- n8n instance running
- Required API keys (see Environment Setup)

### Installation
```bash
# Clone and navigate to repository
git clone <repository-url>
cd Instant-Agency

# Install dependencies
pip install -r requirements_api.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Import workflows to n8n
python import_workflows.py

# Start the API server
python api_server.py
```

### Environment Variables
```bash
# n8n Configuration
N8N_HOST=https://n8n.six3.cloud
N8N_API_KEY=your_n8n_api_key

# AI Services
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
HUGGINGFACE_API_KEY=your_huggingface_key

# Database (optional for local development)
DATABASE_URL=postgresql://user:password@localhost:5432/six3_agency

# Authentication
JWT_SECRET_KEY=your_jwt_secret
API_SECRET_KEY=your_api_secret
```

## 🏗 Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client APIs   │    │   n8n Workflows │    │   AI Agents     │
│                 │    │                 │    │                 │
│ • REST Endpoints│    │ • Lead Qual.    │    │ • Orchestrator  │
│ • Webhooks      │◄──►│ • Campaign Opt. │◄──►│ • Search Spec.  │
│ • Auth Layer    │    │ • Media Prod.   │    │ • Media Spec.   │
│ • Rate Limiting │    │ • Model Tuning  │    │ • ML Specialist │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Databases     │    │   External APIs │    │   Monitoring    │
│                 │    │                 │    │                 │
│ • Client Data   │    │ • Google Ads    │    │ • Performance   │
│ • Projects      │    │ • Meta Ads      │    │ • Alerting      │
│ • Analytics     │    │ • OpenAI        │    │ • Logging       │
│ • Audit Logs    │    │ • HuggingFace   │    │ • Dashboards    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Service Endpoints

### Client Management
- `POST /clients/onboard` - Onboard new client
- `GET /clients/{client_id}/status` - Get client status
- `GET /clients/{client_id}/projects` - List client projects

### Search Marketing
- `POST /services/search-marketing/campaigns` - Create campaign
- `GET /services/search-marketing/performance` - Get performance data
- `PUT /services/search-marketing/optimize` - Trigger optimization

### AI Media Production
- `POST /services/ai-media/content` - Create AI content
- `GET /services/ai-media/status/{production_id}` - Check production status
- `GET /services/ai-media/download/{asset_id}` - Download assets

### ML Model Services
- `POST /services/ml-tuning/models` - Start model training
- `GET /services/ml-tuning/progress/{model_id}` - Check training progress
- `POST /services/ml-tuning/deploy/{model_id}` - Deploy model

### Analytics & Reporting
- `GET /analytics/dashboard` - Main dashboard data
- `GET /reports/performance` - Performance reports
- `GET /reports/roi` - ROI analysis

## 🔄 Workflow Integration

### n8n Workflows Available
1. **SIX3 Lead Qualification** - Automated lead scoring and routing
2. **SIX3 Email Personalization** - AI-powered email customization
3. **SIX3 Search Marketing Campaign** - Multi-platform campaign optimization
4. **SIX3 AI Avatar Production** - Automated video content generation
5. **SIX3 ML Model FineTuning** - Custom model training pipeline
6. **SIX3 Generative AI Video Production** - Complete media production
7. **SIX3 Client Onboarding** - End-to-end client setup

### Workflow Triggers
- **HTTP Webhooks**: External system integration
- **Schedule-based**: Automated optimization cycles
- **Event-driven**: Performance threshold triggers
- **Manual**: On-demand execution

## 🤖 AI Agent System

### Service Delivery Orchestrator
Central coordination for all service delivery activities.

**Key Functions:**
- Client onboarding coordination
- Service request routing
- Resource allocation
- Progress tracking

### Search Marketing Specialist
Handles end-to-end search marketing campaign management.

**Capabilities:**
- Campaign strategy development
- Multi-platform setup and optimization
- Performance analysis and reporting
- AI-driven bid management

### Generative AI Media Specialist
Manages AI-powered content production.

**Features:**
- AI avatar creation
- Voice cloning and synthesis
- Video content generation
- Brand compliance verification

## 🛡 Security & Compliance

### Authentication
- JWT-based API authentication
- Role-based access control
- API key management
- Session management

### Data Protection
- End-to-end encryption
- Secure data storage
- PII handling compliance
- GDPR/CCPA compliance

### Monitoring
- Real-time performance monitoring
- Security event logging
- Anomaly detection
- Automated alerting

## 📊 Performance Metrics

### System Metrics
- API response times
- Workflow execution success rates
- Agent performance scores
- Resource utilization

### Business Metrics
- Client satisfaction scores
- Revenue per client
- Service delivery timelines
- ROI performance

## 🧪 Testing

### Unit Tests
```bash
pytest agents/test_*.py -v
```

### Integration Tests
```bash
pytest tests/integration/ -v
```

### API Testing
```bash
# Start test server
python api_server.py --env=test

# Run API tests
pytest tests/api/ -v
```

### Load Testing
```bash
# Install load testing tools
pip install locust

# Run load tests
locust -f tests/load_test.py --host=http://localhost:8000
```

## 🚀 Deployment

### Local Development
```bash
python api_server.py
# Server starts at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Docker Deployment
```bash
# Build image
docker build -t six3-agency-api .

# Run container
docker run -p 8000:8000 --env-file .env six3-agency-api
```

### Production Deployment
```bash
# Use gunicorn for production
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🔧 Configuration

### API Configuration
```python
# api_config.py
class Settings:
    n8n_host: str = "https://n8n.six3.cloud"
    n8n_api_key: str = "your_key"
    openai_api_key: str = "your_key"
    max_concurrent_requests: int = 100
    rate_limit_per_minute: int = 1000
```

### Service Configuration
Services are configured in `services_config.py` with detailed specifications for each offering.

## 📈 Monitoring & Observability

### Health Checks
- `/health` - Basic health status
- `/health/detailed` - Comprehensive system status
- `/metrics` - Prometheus metrics

### Logging
- Structured JSON logging
- Log aggregation via Loguru
- Centralized error tracking
- Performance metrics logging

### Alerting
- Threshold-based alerts
- Anomaly detection
- Service degradation notifications
- Client impact alerts

## 🤝 Contributing

### Development Workflow
1. Create feature branch
2. Implement changes with tests
3. Run quality checks
4. Submit pull request
5. Code review and merge

### Code Quality
```bash
# Format code
black . && isort .

# Type checking
mypy .

# Run all tests
pytest
```

## 📞 Support

### Technical Support
- **Email**: support@six3.agency
- **Documentation**: https://docs.six3.agency
- **Status Page**: https://status.six3.agency

### Emergency Contact
- **24/7 Hotline**: emergency@six3.agency
- **Escalation**: cto@six3.agency

---

## 📋 Service Delivery Checklist

### Pre-Launch Checklist
- [ ] n8n workflows imported and active
- [ ] API server running and responsive
- [ ] Authentication configured
- [ ] Monitoring systems operational
- [ ] Test client onboarding successful

### Daily Operations
- [ ] System health checks
- [ ] Performance monitoring review
- [ ] Client project status updates
- [ ] Error log analysis
- [ ] Capacity planning review

### Weekly Reviews
- [ ] Service performance analysis
- [ ] Client satisfaction metrics
- [ ] Workflow optimization opportunities
- [ ] Team performance review
- [ ] Technology updates assessment

---

*Last updated: November 2024*
*Next review: February 2025*