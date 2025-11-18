# SIX3 Agency n8n Workflow Import Guide

## 📋 Quick Import Instructions

### Method 1: Manual Import via n8n Interface (Recommended)

1. **Access your n8n instance** (you mentioned you have a Pro subscription)
   - Go to your n8n instance URL
   - Log in to your dashboard

2. **Import each workflow manually:**
   - Click "+" to create a new workflow
   - Click the three dots menu → "Import"
   - Copy and paste the JSON content from each file below:

#### 🚀 Workflow Files to Import:

1. **Lead Qualification Workflow**
   - File: `/workflows/SIX3_Lead_Qualification.json`
   - Webhook URL: `https://your-n8n-instance.app.n8n.cloud/webhook/six3-lead-qualification`

2. **Search Marketing Campaign Optimizer**
   - File: `/workflows/SIX3_Search_Marketing_Campaign.json`
   - Webhook URL: `https://your-n8n-instance.app.n8n.cloud/webhook/six3-search-marketing`

3. **AI Avatar Production**
   - File: `/workflows/SIX3_AI_Avatar_Production.json`
   - Webhook URL: `https://your-n8n-instance.app.n8n.cloud/webhook/six3-avatar-production`

4. **ML Model Fine-tuning Pipeline**
   - File: `/workflows/SIX3_ML_Model_FineTuning.json`
   - Webhook URL: `https://your-n8n-instance.app.n8n.cloud/webhook/six3-ml-tuning`

5. **Email Campaign Personalization**
   - File: `/workflows/SIX3_Email_Personalization.json`
   - Webhook URL: `https://your-n8n-instance.app.n8n.cloud/webhook/six3-email-personalization`

6. **Client Onboarding & Service Delivery**
   - File: `/workflows/SIX3_Client_Onboarding.json`
   - Webhook URL: `https://your-n8n-instance.app.n8n.cloud/webhook/six3-client-onboarding`

7. **Generative AI Video & Audio Production**
   - File: `/workflows/SIX3_Generative_AI_Video_Production.json`
   - Webhook URL: `https://your-n8n-instance.app.n8n.cloud/webhook/six3-generative-ai-media`

### Method 2: API Import via Python Script

```bash
# Install required dependencies
pip install requests

# Run the import script
python3 import_workflows.py
```

When prompted, enter:
- Your n8n instance URL (e.g., `https://your-instance.app.n8n.cloud`)
- Your n8n API key (get from Settings → Personal Access Tokens in n8n)

## ⚙️ Post-Import Configuration

### 1. Update API Endpoints
After import, verify that all HTTP Request nodes point to your production API:
```
https://api.six3agency.com/agents/[agent-endpoint]
```

### 2. Configure Credentials
You may need to set up credentials for:
- Database connections
- External API integrations
- Email services
- Cloud storage

### 3. Test Webhooks
Test each webhook endpoint to ensure proper connectivity:
```bash
curl -X POST "https://your-n8n-instance.app.n8n.cloud/webhook/six3-lead-qualification" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### 4. Activate Workflows
- Review each workflow
- Enable/activate when ready for production use
- Monitor execution logs for any issues

## 🔧 Troubleshooting

### Common Issues:
1. **Invalid JSON Format**: Ensure no extra characters when copying workflow JSON
2. **Missing Credentials**: Set up required credentials before activating
3. **API Endpoints**: Verify your API server is deployed and accessible
4. **Webhook URLs**: Replace with your actual n8n instance URL

### Validation Checklist:
- [ ] All 7 workflows imported successfully
- [ ] API endpoints point to production server
- [ ] Webhook URLs are correct for your n8n instance
- [ ] Required credentials are configured
- [ ] Test executions complete without errors
- [ ] Workflows are activated and monitoring is enabled

## 📞 Support

If you encounter issues during import:
1. Check the n8n execution logs
2. Verify API server connectivity
3. Ensure webhook URLs are accessible
4. Review workflow node configurations