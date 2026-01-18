# Mailtrap Email Integration Setup Guide

Mailtrap is a safe email testing service that captures all outgoing emails in a test inbox without sending them to real recipients. This is perfect for development, testing, and staging environments.

## Why Mailtrap?

- **Safe Testing**: Emails never reach real inboxes
- **Email Preview**: See how emails look across 100+ email clients
- **Spam Analysis**: Check spam scores before going to production
- **Free Tier**: 500 emails/month included
- **Easy Setup**: 5-minute configuration
- **HTML/CSS Validation**: Ensure emails render correctly

## Quick Setup

### 1. Create Mailtrap Account

1. Go to [https://mailtrap.io/](https://mailtrap.io/)
2. Sign up for a free account
3. Verify your email address

### 2. Get Your SMTP Credentials

1. Log into Mailtrap
2. Navigate to **Email Testing** > **Inboxes**
3. Select your inbox (or create a new one)
4. Click on **SMTP Settings** or the **Integrations** dropdown
5. Select **Show Credentials**

You'll see:
```
Host: sandbox.smtp.mailtrap.io
Port: 2525 or 25, 465, 587
Username: [your_username]
Password: [your_password]
```

### 3. Get Your API Token (Optional - for reading emails)

1. In Mailtrap, click your profile icon (top right)
2. Go to **Settings** > **API Tokens**
3. Click **Create Token**
4. Name it (e.g., "SIX3 Agency Integration")
5. Copy the token

### 4. Get Your Inbox ID (Optional - for reading emails)

1. In your inbox, look at the URL
2. The inbox ID is in the URL: `https://mailtrap.io/inboxes/YOUR_INBOX_ID/messages`
3. Copy the number

### 5. Configure Environment Variables

Create a `.env` file in the project root (or copy from `.env.example`):

```bash
# Email Provider Selection
EMAIL_PROVIDER=mailtrap

# Mailtrap SMTP Configuration (Required)
MAILTRAP_SMTP_HOST=sandbox.smtp.mailtrap.io
MAILTRAP_SMTP_PORT=2525
MAILTRAP_SMTP_USERNAME=your_username_here
MAILTRAP_SMTP_PASSWORD=your_password_here

# Mailtrap API Configuration (Optional - for reading emails)
MAILTRAP_INBOX_ID=your_inbox_id_here
MAILTRAP_API_TOKEN=your_api_token_here

# Sender Configuration
MAILTRAP_FROM_EMAIL=hello@six3.agency
MAILTRAP_FROM_NAME=SIX3 Agency
```

## Testing the Integration

### Test via Python Script

```python
from integrations.email.mailtrap_integration import MailtrapIntegration, MailtrapEmailTemplates

# Initialize integration
mailtrap = MailtrapIntegration()

# Test connection
result = mailtrap.test_connection()
print(f"Connection test: {result}")

# Send test email
template = MailtrapEmailTemplates.test_email()
send_result = mailtrap.send_email(
    to_email="test@example.com",
    subject=template['subject'],
    html_content=template['html_content'],
    text_content=template['text_content']
)
print(f"Email sent: {send_result}")
```

### Test via Command Line

```bash
cd /home/user/Instant-Agency
python -m integrations.email.mailtrap_integration
```

### Check Your Mailtrap Inbox

1. Go to [https://mailtrap.io/inboxes](https://mailtrap.io/inboxes)
2. Select your inbox
3. You should see your test email!
4. Click on it to:
   - Preview HTML/Text versions
   - Check spam score
   - View email headers
   - See how it looks in different email clients

## Using Mailtrap in Your Code

### Basic Email Sending

```python
from integrations.email.mailtrap_integration import MailtrapIntegration

mailtrap = MailtrapIntegration()

result = mailtrap.send_email(
    to_email="customer@example.com",
    subject="Welcome to SIX3 Agency",
    html_content="<h1>Welcome!</h1><p>Thanks for joining us.</p>",
    text_content="Welcome! Thanks for joining us."
)

if result['success']:
    print("Email sent to Mailtrap inbox!")
else:
    print(f"Error: {result['error']}")
```

### Bulk Email Sending

```python
recipients = [
    {'email': 'user1@example.com', 'name': 'John Doe', 'company': 'Acme Corp'},
    {'email': 'user2@example.com', 'name': 'Jane Smith', 'company': 'XYZ Inc'},
]

result = mailtrap.send_bulk_emails(
    recipients=recipients,
    subject="Newsletter for %recipient.company%",
    html_content="<p>Hi %recipient.name%!</p><p>Latest updates...</p>"
)

print(f"Sent {result['total_sent']} emails")
```

### Using Email Templates

```python
from integrations.email.mailtrap_integration import MailtrapEmailTemplates

# Welcome email
template = MailtrapEmailTemplates.welcome_email("John Doe", "SIX3 Agency")

mailtrap.send_email(
    to_email="john@example.com",
    subject=template['subject'],
    html_content=template['html_content'],
    text_content=template['text_content']
)
```

### Reading Emails from Inbox

```python
# Get recent emails
messages = mailtrap.get_inbox_messages(limit=10)

for message in messages['messages']:
    print(f"Subject: {message['subject']}")
    print(f"From: {message['from_email']}")
    print(f"To: {message['to_email']}")

# Get specific message details
details = mailtrap.get_message_details(message_id='12345')
print(details['message']['html_body'])

# Clean inbox (delete all messages)
mailtrap.delete_all_messages()
```

## Switching to Production (Mailgun)

When you're ready to send real emails in production:

1. Set up Mailgun account at [https://www.mailgun.com/](https://www.mailgun.com/)
2. Get your API key and domain
3. Update `.env`:
   ```bash
   EMAIL_PROVIDER=mailgun
   MAILGUN_API_KEY=your_actual_key
   MAILGUN_DOMAIN=your_verified_domain.com
   ```
4. Your email code remains the same - just swap the provider!

## Troubleshooting

### "SMTP credentials not configured"
- Check that `MAILTRAP_SMTP_USERNAME` and `MAILTRAP_SMTP_PASSWORD` are set in your `.env` file
- Ensure there are no extra spaces in the credentials

### "Connection timeout"
- Verify your internet connection
- Try port 587 or 2525 instead of 25
- Check if your firewall is blocking SMTP connections

### "Authentication failed"
- Double-check your username and password from Mailtrap
- Make sure you're using SMTP credentials, not API token

### Emails not appearing in inbox
- Check you're looking at the correct inbox in Mailtrap
- Refresh the page
- Check the "All Messages" folder

## Features

### Email Preview
Click on any email in Mailtrap to see:
- HTML rendering
- Plain text version
- Raw source
- Email headers
- Spam score
- Preview in 100+ email clients

### Forwarding Emails
You can forward captured emails to your real inbox for testing:
1. Click on the email in Mailtrap
2. Click "Forward"
3. Enter your real email address
4. Check your inbox!

### Email Validation
Mailtrap shows you:
- HTML/CSS validation errors
- Missing alt tags on images
- Broken links
- Spam trigger words
- Authentication issues (SPF, DKIM, DMARC)

## API Documentation

Full Mailtrap API documentation: [https://api-docs.mailtrap.io/](https://api-docs.mailtrap.io/)

## Support

- Mailtrap Support: [https://help.mailtrap.io/](https://help.mailtrap.io/)
- Integration Issues: Check the logs in `integrations/email/mailtrap_integration.py`
- Questions: Contact your development team

## Next Steps

1. Complete the setup above
2. Run the test script
3. Verify emails appear in your Mailtrap inbox
4. Update your agents to use Mailtrap for email sending
5. Test all email workflows
6. Switch to Mailgun for production deployment

Happy testing!
