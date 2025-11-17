# n8n Integration Guide

This guide shows how to connect your n8n instance to the AI agents and Attio CRM.

## Quick Setup

### 1. Start the Agent API

```bash
# Run locally
cd agents
python main.py

# Agent API now running on http://localhost:8000
```

### 2. Expose to Internet (For Testing)

**Option A: Using ngrok (Easiest)**
```bash
# In a new terminal
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

**Option B: Deploy to Server**
```bash
# SSH to your server
ssh user@your-server.com

# Clone repo and start agents
git clone <your-repo>
cd Instant-Agency/agents
python3 main.py

# Access via http://your-server-ip:8000
```

### 3. Configure Environment Variables in n8n

In your n8n instance, go to **Settings → Environment Variables** and add:

```bash
AGENT_API_URL=https://your-ngrok-url.ngrok.io
# or
AGENT_API_URL=http://your-server-ip:8000

ATTIO_API_KEY=your_attio_api_key_here
```

### 4. Import Workflow

1. Copy the content of `lead_capture_to_attio.json`
2. In n8n, go to **Workflows → Import from File**
3. Paste the JSON
4. Click **Import**

### 5. Get Webhook URL

1. Open the workflow in n8n
2. Click the **Webhook** node
3. Click **Execute Node** to activate it
4. Copy the **Production URL** (e.g., `https://your-n8n.com/webhook/lead-capture`)

## How It Works

```
Website Form
    ↓
    POST to n8n Webhook
    ↓
    n8n calls Agent API (/phase1/qualify-and-create-in-crm)
    ↓
    Agent analyzes lead with AI (sentiment analysis)
    ↓
    Agent creates lead in Attio CRM
    ↓
    IF lead is "hot" → notify sales team
    ↓
    Return success response
```

## Testing the Workflow

### Test with curl

```bash
curl -X POST https://your-n8n.com/webhook/lead-capture \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "company": "Acme Corp",
    "industry": "Technology",
    "phone": "+1-555-1234",
    "jobTitle": "CEO",
    "message": "Very interested in your AI automation platform. Would love to schedule a demo!"
  }'
```

### Expected Response

```json
{
  "message": "Lead captured and qualified successfully",
  "status": "hot",
  "score": 8.5,
  "crm_id": "person_abc123"
}
```

## Agent API Endpoints Available

### Qualify Lead Only
```bash
POST /phase1/qualify-lead

{
  "lead_name": "John Doe",
  "lead_email": "john@example.com",
  "company": "Acme Corp",
  "lead_message": "Interested in your product"
}
```

### Qualify + Create in CRM (Recommended)
```bash
POST /phase1/qualify-and-create-in-crm

{
  "lead_name": "John Doe",
  "lead_email": "john@example.com",
  "company": "Acme Corp",
  "lead_message": "Interested in your product",
  "phone": "+1-555-1234",
  "job_title": "CEO"
}
```

### FAQ Chatbot
```bash
POST /phase1/faq

{
  "question": "What is SIX3 Agency?",
  "user_id": "visitor_123"
}
```

### All 20 Agents
See API docs: http://your-api-url:8000/docs

## Common n8n Workflow Patterns

### Pattern 1: Lead Capture from Form

```
Webhook
  → HTTP Request (qualify-and-create-in-crm)
  → IF (check score)
    → [High Score] Send Email to Sales
    → [Low Score] Add to Nurture Campaign
```

### Pattern 2: Chatbot to CRM

```
Webhook (chat message)
  → HTTP Request (phase1/faq)
  → IF (intent = 'contact_sales')
    → HTTP Request (qualify-and-create-in-crm)
    → Email notification
```

### Pattern 3: Scheduled Lead Enrichment

```
Schedule Trigger (daily)
  → Attio: Get New Leads
  → Loop
    → HTTP Request (phase2/generate-sales-pitch)
    → Attio: Add Note to Lead
```

### Pattern 4: Multi-Language Support

```
Webhook (international form)
  → HTTP Request (phase4/multilingual - detect language)
  → HTTP Request (phase4/multilingual - translate to English)
  → HTTP Request (qualify-and-create-in-crm)
  → HTTP Request (phase4/multilingual - translate response back)
  → Respond to Webhook
```

## Troubleshooting

### Error: "Cannot connect to agent API"
- Check AGENT_API_URL is correct in n8n environment variables
- Test manually: `curl http://your-api-url:8000/health`
- If using ngrok, make sure it's still running

### Error: "ATTIO_API_KEY not set"
- The API key must be set where the agents run
- If running locally: `export ATTIO_API_KEY=your_key`
- If in Docker: Add to `.env` file
- The n8n environment variable is just for reference

### Error: "Webhook timeout"
- Agent processing takes 2-5 seconds
- Increase n8n timeout: Workflow Settings → Timeout (set to 30 seconds)

### Webhook not receiving data
- Check webhook is activated (Execute Node)
- Test with curl first
- Check n8n logs for errors

## Next Steps

1. **Add More Workflows**
   - Email follow-ups
   - Task creation
   - Calendar booking
   - Slack notifications

2. **Connect More Agents**
   - Phase 2: Content generation, social media
   - Phase 3: Multi-agent orchestration
   - Phase 4: Voice calls, avatars

3. **Production Deployment**
   - Deploy agents to permanent server
   - Set up SSL/HTTPS
   - Configure domain
   - Add monitoring

## Resources

- n8n Docs: https://docs.n8n.io
- Attio API: https://developers.attio.com
- Agent API Docs: http://your-api-url:8000/docs

## Need Help?

Once you share your n8n URL, I can:
- Create custom workflows for your use case
- Help debug connection issues
- Add more agent integrations
