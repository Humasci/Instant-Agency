# Instant Agency - Workflow Templates

This directory contains n8n workflow templates for each department.

## Directory Structure

```
workflows/
├── marketing/          # Marketing automation workflows
├── sales/              # Sales process workflows
├── content/            # Content creation workflows
├── support/            # Customer support workflows
├── operations/         # Operations and analytics workflows
└── orchestration/      # Multi-agent orchestration workflows
```

## Importing Workflows

### Method 1: Via n8n UI

1. Open n8n at http://localhost:5678
2. Click "Import from File"
3. Select a workflow JSON file
4. Configure credentials and webhook URLs
5. Activate the workflow

### Method 2: Via Script

```bash
cd workflows/
./import-workflows.sh
```

## Workflow Categories

### Marketing Workflows

- **lead-capture.json**: Capture leads from website forms
- **prospect-research.json**: Automated prospect research
- **email-campaign.json**: Multi-touch email campaigns
- **lead-scoring.json**: Automated lead scoring
- **social-listening.json**: Monitor social media mentions

### Sales Workflows

- **lead-qualification.json**: Qualify inbound leads
- **discovery-scheduler.json**: Schedule discovery calls
- **proposal-generator.json**: Generate custom proposals
- **follow-up-sequence.json**: Automated follow-up emails
- **deal-alerts.json**: Notifications for deal changes

### Content Workflows

- **blog-post-generator.json**: Generate blog content
- **social-publisher.json**: Multi-platform social posting
- **seo-optimizer.json**: SEO optimization workflow
- **content-calendar.json**: Manage content calendar
- **newsletter-automation.json**: Automated newsletters

### Support Workflows

- **ticket-triage.json**: Auto-route support tickets
- **chatbot-escalation.json**: Chatbot to human handoff
- **satisfaction-survey.json**: Send NPS surveys
- **onboarding-automation.json**: Customer onboarding sequence

### Operations Workflows

- **daily-report.json**: Daily KPI reports
- **data-sync.json**: Sync data between systems
- **alert-manager.json**: System health alerts
- **backup-automation.json**: Automated backups

## Workflow Best Practices

1. **Use Descriptive Names**: Name nodes clearly
2. **Add Notes**: Document complex logic
3. **Error Handling**: Always include error handling nodes
4. **Testing**: Test with sample data before activating
5. **Monitoring**: Enable execution logging
6. **Credentials**: Use environment variables for secrets

## Common Nodes

- **Webhook**: Trigger workflows via HTTP
- **Schedule**: Time-based triggers
- **HTTP Request**: Call external APIs
- **Function**: Custom JavaScript logic
- **IF**: Conditional branching
- **Set**: Transform data
- **Split in Batches**: Process large datasets

## Credentials Setup

Required credentials for workflows:

- **PostgreSQL**: Database connection
- **Redis**: Cache connection
- **Hugging Face API**: AI model access
- **Email Provider**: SendGrid/Mailgun
- **CRM**: SuiteCRM/Odoo API
- **Social Media**: LinkedIn, Twitter, Facebook

Configure these in n8n Settings > Credentials.

## Troubleshooting

### Workflow Not Triggering

- Check webhook URL is correct
- Verify authentication settings
- Check execution logs

### API Errors

- Verify API credentials
- Check rate limits
- Review API endpoint URLs

### Data Issues

- Check data mapping in Set nodes
- Verify field names match
- Review Function node logic

## Contributing

When creating new workflows:

1. Follow naming convention: `department-action.json`
2. Add description and documentation
3. Test thoroughly
4. Document required credentials
5. Add to appropriate category folder
