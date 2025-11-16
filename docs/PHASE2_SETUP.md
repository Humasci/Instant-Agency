# Phase 2 Setup Guide: Department Foundations

**Phase 2** deploys 5 specialized AI agents with advanced language generation and understanding capabilities using state-of-the-art Hugging Face models.

## 📋 Overview

Phase 2 agents provide:
- **Personalized B2B sales pitches** using Mistral-7B or GPT-Neo-2.7B
- **Professional content writing** for blogs and articles
- **Zero-shot intent classification** with BART
- **Context-aware email personalization**
- **Platform-specific social media content** (LinkedIn, Twitter, Facebook)

## 🚀 Quick Start (5 minutes)

### 1. Prerequisites

```bash
# Ensure you have completed Phase 1 setup
# You should already have:
# - Python 3.9+
# - Redis running
# - PostgreSQL running
# - Hugging Face API key set
```

### 2. Verify Environment

```bash
# Check your Hugging Face API key
echo $HUGGINGFACE_API_KEY

# If not set:
export HUGGINGFACE_API_KEY="your_hf_api_key_here"
```

### 3. Start the Agent Service

```bash
cd agents
python main.py
```

You should see:
```
✓ All agents initialized successfully
  Loaded agents (9): sales_qualification, marketing_prospecting,
  phase1_prospect, phase1_faq, phase2_sales_pitch, phase2_content_writer,
  phase2_intent_classifier, phase2_email_personalizer, phase2_social_media
```

### 4. Test the Agents

```bash
cd scripts
python test_phase2_agents.py
```

Expected output:
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PHASE 2 AGENTS - TEST SUITE                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

...

🎉 All tests passed!
```

## 🎯 Phase 2 Agents

### 1. Sales Pitch Generation Agent

**Purpose**: Generate personalized B2B sales pitches
**Model**: `mistralai/Mistral-7B-Instruct-v0.1` (primary), `EleutherAI/gpt-neo-2.7B` (fallback)
**Endpoint**: `POST /phase2/generate-sales-pitch`

**Example Request**:
```bash
curl -X POST http://localhost:8000/phase2/generate-sales-pitch \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_name": "Sarah Johnson",
    "company": "TechCorp",
    "industry": "SaaS",
    "pain_points": "Manual lead qualification, slow follow-up",
    "company_size": "50-100 employees",
    "trigger_event": "Series A funding",
    "current_solutions": "Basic CRM"
  }'
```

**Example Response**:
```json
{
  "success": true,
  "agent": "phase2_sales_pitch",
  "data": {
    "subject": "Transform TechCorp's Sales Process with AI Automation",
    "pitch": "Hi Sarah,\n\nCongratulations on your Series A funding...",
    "quality_score": 85,
    "model_used": "mistralai/Mistral-7B-Instruct-v0.1",
    "personalization_elements": [
      "prospect_name",
      "company_name",
      "trigger_event",
      "pain_points"
    ],
    "timestamp": "2025-01-15T10:30:00"
  }
}
```

**Quality Metrics**:
- Personalization (40%): Uses prospect name, company, pain points
- Professional tone (30%): Business-appropriate language
- Length (20%): 200-500 words optimal
- Call-to-action (10%): Clear next step

---

### 2. Content Writer Agent

**Purpose**: Generate blog posts and marketing articles
**Model**: `EleutherAI/gpt-neo-2.7B`
**Endpoint**: `POST /phase2/write-content`

**Example Request**:
```bash
curl -X POST http://localhost:8000/phase2/write-content \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "How AI Automation Transforms Small Businesses",
    "content_type": "blog_post",
    "audience": "small business owners",
    "tone": "conversational",
    "word_count": 600,
    "keywords": ["AI", "automation", "productivity"],
    "key_points": [
      "Benefits of AI automation",
      "Common use cases",
      "Getting started"
    ]
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "title": "How AI Automation Transforms Small Business Operations",
    "content": "In today's competitive landscape...",
    "word_count": 612,
    "quality_score": 82,
    "seo_metadata": {
      "meta_description": "Discover how AI automation can transform...",
      "keywords": ["AI", "automation", "small business", "productivity"],
      "tags": ["AI", "Business", "Technology", "Productivity"]
    },
    "timestamp": "2025-01-15T10:35:00"
  }
}
```

**Quality Metrics**:
- Structure (30%): Intro, body paragraphs, conclusion
- Length (25%): Matches target word count
- Keyword usage (25%): Natural keyword integration
- Readability (20%): Clear, engaging writing

---

### 3. Intent Classification Agent

**Purpose**: Classify user message intent using zero-shot learning
**Model**: `facebook/bart-large-mnli`
**Endpoint**: `POST /phase2/classify-intent`

**Supported Intents**:
- `pricing` - Pricing questions
- `demo` - Demo/trial requests
- `support` - Technical support
- `meeting` - Meeting/call scheduling
- `integration` - Integration questions
- `general` - General information
- `complaint` - Complaints/issues
- `feedback` - Feedback/suggestions

**Example Request**:
```bash
curl -X POST http://localhost:8000/phase2/classify-intent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can we schedule a demo for next week?",
    "user_id": "user_123"
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "primary_intent": {
      "intent": "demo",
      "confidence": 0.89
    },
    "all_intents": [
      {"intent": "demo", "confidence": 0.89},
      {"intent": "meeting", "confidence": 0.76},
      {"intent": "general", "confidence": 0.12}
    ],
    "urgency": "medium",
    "requires_response": true,
    "suggested_action": "Send calendar scheduling link and demo preparation materials",
    "timestamp": "2025-01-15T10:40:00"
  }
}
```

**Urgency Levels**:
- `high` - Complaints, urgent support (confidence > 0.8)
- `medium` - Demos, meetings, pricing
- `low` - General info, feedback

---

### 4. Email Personalizer Agent

**Purpose**: Generate personalized email responses based on intent
**Model**: `EleutherAI/gpt-neo-2.7B`
**Endpoint**: `POST /phase2/personalize-email`

**Example Request**:
```bash
curl -X POST http://localhost:8000/phase2/personalize-email \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_name": "Michael Chen",
    "recipient_email": "michael@startup.io",
    "company": "Innovation Startup",
    "intent": "pricing",
    "original_message": "What are your pricing options?",
    "email_type": "response"
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "subject": "Instant Agency Pricing Options for Innovation Startup",
    "body": "Hi Michael,\n\nThank you for your interest in Instant Agency...",
    "personalization_score": 88,
    "intent": "pricing",
    "personalization_elements": [
      "recipient_first_name",
      "company_name",
      "intent_specific_content"
    ],
    "timestamp": "2025-01-15T10:45:00"
  }
}
```

**Personalization Scoring**:
- Name usage (30%): Uses first name in greeting
- Company mentions (30%): References recipient's company
- Intent-specific content (40%): Relevant to their question

---

### 5. Social Media Manager Agent

**Purpose**: Create platform-specific social media posts
**Model**: `EleutherAI/gpt-neo-2.7B`
**Endpoint**: `POST /phase2/create-social-posts`

**Supported Platforms**:
- **LinkedIn**: Professional, 150-300 words, 3-5 hashtags
- **Twitter**: Concise, 120-180 chars, 1-2 hashtags
- **Facebook**: Conversational, 100-250 words, 2-3 hashtags

**Example Request**:
```bash
curl -X POST http://localhost:8000/phase2/create-social-posts \
  -H "Content-Type: application/json" \
  -d '{
    "content": "AI automation is transforming small businesses...",
    "topic": "AI Automation Benefits",
    "platforms": ["linkedin", "twitter", "facebook"],
    "target_audience": "small business owners",
    "cta": "Start your free trial",
    "link": "https://instant-agency.ai/trial"
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "platform": "linkedin",
        "content": "🚀 AI automation is revolutionizing...",
        "hashtags": ["#AIAutomation", "#SmallBusiness", "#ProductivityTools"],
        "character_count": 245,
        "engagement_score": 82,
        "best_posting_time": "Tuesday-Thursday, 8-10 AM"
      },
      {
        "platform": "twitter",
        "content": "AI automation = more time for growth...",
        "hashtags": ["#AI", "#SmallBiz"],
        "character_count": 156,
        "engagement_score": 78,
        "best_posting_time": "Weekdays, 12-1 PM"
      }
    ],
    "posts_generated": 3,
    "timestamp": "2025-01-15T10:50:00"
  }
}
```

**Engagement Scoring**:
- Platform optimization (35%): Follows platform best practices
- Hashtag relevance (25%): Appropriate hashtags
- CTA clarity (20%): Clear call-to-action
- Length optimization (20%): Ideal length for platform

---

## 🔄 Typical Workflow Examples

### Example 1: Lead Response Automation

```python
import requests

# Step 1: Classify intent
intent_response = requests.post(
    'http://localhost:8000/phase2/classify-intent',
    json={'message': 'What are your pricing plans?', 'user_id': 'lead_456'}
)
intent = intent_response.json()['data']['primary_intent']['intent']

# Step 2: Generate personalized email
email_response = requests.post(
    'http://localhost:8000/phase2/personalize-email',
    json={
        'recipient_name': 'John Smith',
        'recipient_email': 'john@company.com',
        'company': 'Acme Corp',
        'intent': intent,
        'original_message': 'What are your pricing plans?',
        'email_type': 'response'
    }
)

email = email_response.json()['data']
print(f"Subject: {email['subject']}")
print(f"Body: {email['body']}")
```

### Example 2: Content Marketing Pipeline

```python
# Step 1: Generate blog post
content_response = requests.post(
    'http://localhost:8000/phase2/write-content',
    json={
        'topic': 'AI Sales Automation for SaaS Companies',
        'content_type': 'blog_post',
        'audience': 'SaaS founders',
        'tone': 'professional',
        'word_count': 800,
        'keywords': ['AI', 'sales automation', 'SaaS'],
        'key_points': ['Benefits', 'Use cases', 'ROI']
    }
)

content = content_response.json()['data']['content']

# Step 2: Create social media posts from blog
social_response = requests.post(
    'http://localhost:8000/phase2/create-social-posts',
    json={
        'content': content,
        'topic': 'AI Sales Automation',
        'platforms': ['linkedin', 'twitter'],
        'target_audience': 'SaaS founders',
        'cta': 'Read the full article',
        'link': 'https://blog.instant-agency.ai/ai-sales-automation'
    }
)

posts = social_response.json()['data']['posts']
for post in posts:
    print(f"\n{post['platform'].upper()}:")
    print(post['content'])
```

### Example 3: Sales Outreach Campaign

```python
prospects = [
    {
        'name': 'Sarah Chen',
        'company': 'DataFlow',
        'industry': 'SaaS',
        'pain_points': 'Manual processes',
        'company_size': '25-50',
        'trigger_event': 'Series A funding',
        'current_solutions': 'Basic CRM'
    },
    # ... more prospects
]

for prospect in prospects:
    # Generate personalized pitch
    pitch_response = requests.post(
        'http://localhost:8000/phase2/generate-sales-pitch',
        json=prospect
    )

    pitch = pitch_response.json()['data']

    # Only send if quality score is high
    if pitch['quality_score'] >= 75:
        print(f"High-quality pitch for {prospect['name']}: {pitch['quality_score']}")
        # Send email via your email service
    else:
        print(f"Low quality, needs human review: {prospect['name']}")
```

---

## 📊 Performance & Cost Estimates

### Response Times (Hugging Face Inference API)

| Agent | Model | Avg Response Time | Cold Start |
|-------|-------|-------------------|------------|
| Sales Pitch | Mistral-7B-Instruct | 3-8 seconds | 10-15s |
| Content Writer | GPT-Neo-2.7B | 5-12 seconds | 8-12s |
| Intent Classifier | BART-large-mnli | 1-3 seconds | 3-5s |
| Email Personalizer | GPT-Neo-2.7B | 3-6 seconds | 8-12s |
| Social Media | GPT-Neo-2.7B | 4-8 seconds | 8-12s |

**Note**: Cold starts occur when model hasn't been used recently. Subsequent calls are faster.

### Cost Estimates (Hugging Face Inference API)

Free tier: **30,000 requests/month**

Paid tier: **$9/month** for 100,000 requests
- Sales pitch: ~$0.0009 per pitch
- Content generation: ~$0.001 per article
- Intent classification: ~$0.0003 per message
- Email personalization: ~$0.0006 per email
- Social posts: ~$0.0008 per post set

**Example monthly costs** (Pro plan usage):
- 500 sales pitches: $0.45
- 200 blog posts: $0.20
- 5,000 intent classifications: $1.50
- 1,000 personalized emails: $0.60
- 100 social post sets: $0.08
- **Total**: ~$2.83/month (well within free tier!)

---

## 🔧 Troubleshooting

### Issue: "Model is loading" error

**Cause**: Hugging Face cold start
**Solution**: Wait 10-20 seconds and retry. First call loads the model.

```python
import time
import requests

def call_with_retry(url, data, max_retries=3):
    for attempt in range(max_retries):
        response = requests.post(url, json=data, timeout=30)

        if response.status_code == 200:
            return response.json()

        if 'loading' in response.text.lower():
            print(f"Model loading, waiting... (attempt {attempt + 1}/{max_retries})")
            time.sleep(10)
        else:
            raise Exception(f"Error: {response.text}")

    raise Exception("Max retries exceeded")
```

### Issue: Low quality scores

**Cause**: Insufficient input data or poor prompt context
**Solution**: Provide more detailed input

```python
# Bad
pitch_data = {
    'prospect_name': 'John',
    'company': 'ABC'
}

# Good
pitch_data = {
    'prospect_name': 'John Smith',
    'company': 'ABC Technologies Inc',
    'industry': 'SaaS',
    'pain_points': 'Manual lead qualification taking 2+ hours daily',
    'company_size': '50-100 employees',
    'trigger_event': 'Just hired new VP of Sales',
    'current_solutions': 'Using basic CRM with manual processes'
}
```

### Issue: API timeout errors

**Cause**: Large generation requests (e.g., 2000-word articles)
**Solution**: Break into smaller requests or increase timeout

```python
# For large content, request in sections
sections = [
    {'key_points': ['Introduction', 'Problem statement']},
    {'key_points': ['Solution overview', 'Benefits']},
    {'key_points': ['Implementation', 'Conclusion']}
]

full_content = []
for section in sections:
    response = requests.post(url, json={**base_data, **section}, timeout=60)
    full_content.append(response.json()['data']['content'])

article = '\n\n'.join(full_content)
```

### Issue: Inappropriate content generated

**Cause**: Lack of tone/audience specification
**Solution**: Always specify tone and audience

```python
# Add these fields to every request
{
    'tone': 'professional',  # or 'conversational', 'friendly', 'formal'
    'audience': 'enterprise decision makers',  # be specific
    'content_type': 'business_email'  # helps set expectations
}
```

---

## 🚀 Next Steps

### Integrate with Your Systems

**CRM Integration** (Salesforce, HubSpot):
```python
# When new lead comes in
lead = get_new_lead_from_crm()

# Classify their message
intent = classify_intent(lead.message)

# Generate personalized response
email = personalize_email(
    recipient_name=lead.name,
    company=lead.company,
    intent=intent,
    original_message=lead.message
)

# Send via your email system
send_email(to=lead.email, subject=email['subject'], body=email['body'])

# Log to CRM
update_crm_activity(lead.id, 'ai_email_sent', email)
```

**Marketing Automation** (n8n, Zapier):
```
Trigger: New blog topic in Notion
↓
Action: Call /phase2/write-content
↓
Action: Call /phase2/create-social-posts
↓
Action: Schedule posts in Buffer
↓
Action: Notify marketing team in Slack
```

### Move to Phase 3

Phase 3 adds:
- **Multi-agent collaboration** (agents working together)
- **Advanced RAG** (retrieval-augmented generation)
- **Custom model fine-tuning**
- **Real-time conversation agents**

See [IMPLEMENTATION_BLUEPRINT.md](IMPLEMENTATION_BLUEPRINT.md) for Phase 3 details.

---

## 📚 Additional Resources

- [Phase 2 Test Suite](../scripts/test_phase2_agents.py) - Comprehensive testing examples
- [Hugging Face Models](https://huggingface.co/models) - Browse available models
- [Model Fine-Tuning Guide](MODEL_FINE_TUNING.md) - Customize models for your use case
- [n8n Workflow Examples](../workflows/examples/) - Automation templates

---

## 💡 Best Practices

1. **Always validate quality scores** before sending automated content
2. **Use intent classification** to route messages appropriately
3. **Combine agents** for powerful workflows (classify → personalize → send)
4. **Monitor performance** via `/metrics/{agent_name}` endpoint
5. **Provide detailed context** for better generation quality
6. **Implement human review** for high-stakes communications
7. **Cache frequent responses** to reduce API calls
8. **A/B test** different generation parameters for your audience

---

**Questions or issues?** Open an issue on GitHub or consult the [Implementation Blueprint](IMPLEMENTATION_BLUEPRINT.md).
