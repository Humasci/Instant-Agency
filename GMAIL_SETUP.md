# Gmail Integration Setup for hello@six3.agency

This guide shows you how to use your existing Gmail account (hello@six3.agency) to send production emails through the SIX3 Agency platform.

## Overview

**Development/Testing:** Use Mailtrap (emails are captured, not sent)
**Production:** Use Gmail SMTP (real emails sent from hello@six3.agency)

## Setup Steps

### 1. Enable 2-Step Verification (Required)

Gmail requires 2-Step Verification before you can create App Passwords.

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click on **2-Step Verification**
3. Follow the setup process (you'll need your phone)
4. Verify it's enabled (you should see a green checkmark)

### 2. Generate Gmail App Password

**IMPORTANT:** Do NOT use your regular Gmail password. You need to generate an App Password.

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Scroll down to **2-Step Verification** section
3. At the bottom, click **App Passwords**
4. You may need to sign in again
5. Select:
   - App: **Mail**
   - Device: **Other (Custom name)**
   - Enter name: "SIX3 Agency Platform"
6. Click **Generate**
7. Copy the 16-character password (shown in yellow box)
   - Format: `xxxx xxxx xxxx xxxx`
   - You'll use this in your `.env` file

### 3. Configure Environment Variables

Edit your `.env` file and add:

```bash
# For DEVELOPMENT - use Mailtrap (safe testing)
EMAIL_PROVIDER=mailtrap
MAILTRAP_SMTP_USERNAME=your_mailtrap_username
MAILTRAP_SMTP_PASSWORD=your_mailtrap_password

# For PRODUCTION - use Gmail (real emails)
# When ready to send real emails, change EMAIL_PROVIDER to 'gmail'
GMAIL_ADDRESS=hello@six3.agency
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx  # 16-character app password from step 2
GMAIL_FROM_NAME=SIX3 Agency
```

### 4. Test the Connection

```python
from integrations.email.gmail_integration import GmailIntegration

# Initialize Gmail integration
gmail = GmailIntegration()

# Test connection
result = gmail.test_connection()
print(result)
# Should show: {'success': True, 'connection_status': 'connected', ...}
```

If you get an authentication error:
- Double-check you're using the App Password (not your regular Gmail password)
- Make sure 2-Step Verification is enabled
- Regenerate the App Password if needed

### 5. Send a Test Email

```python
from integrations.email.gmail_integration import GmailIntegration

gmail = GmailIntegration()

result = gmail.send_email(
    to_email="your-personal-email@gmail.com",  # Send to yourself for testing
    subject="Test from SIX3 Agency",
    html_content="<h1>Success!</h1><p>Gmail integration is working.</p>",
    text_content="Success! Gmail integration is working."
)

print(result)
```

Check your inbox - you should receive the email from hello@six3.agency!

## Usage Patterns

### Switching Between Test and Production

**During Development:**
```bash
# .env file
EMAIL_PROVIDER=mailtrap
```
All emails go to Mailtrap inbox (safe testing)

**In Production:**
```bash
# .env file
EMAIL_PROVIDER=gmail
```
All emails sent from hello@six3.agency to real recipients

### Sending Emails in Code

The code stays the same! Just change the EMAIL_PROVIDER:

```python
# This works with both Mailtrap AND Gmail!
from integrations.email.gmail_integration import GmailIntegration

email_service = GmailIntegration()

email_service.send_email(
    to_email="customer@example.com",
    subject="Welcome to SIX3 Agency",
    html_content="<h1>Welcome!</h1>",
    text_content="Welcome!"
)
```

### Sending Bulk Emails

```python
recipients = [
    {'email': 'customer1@example.com', 'name': 'John Doe'},
    {'email': 'customer2@example.com', 'name': 'Jane Smith'},
]

result = gmail.send_bulk_emails(
    recipients=recipients,
    subject="Newsletter from SIX3 Agency",
    html_content="<p>Hi %recipient.name%!</p><p>Here's our latest update...</p>"
)

print(f"Sent {result['total_sent']} emails")
```

### With Attachments

```python
# Read a file
with open('report.pdf', 'rb') as f:
    pdf_content = f.read()

gmail.send_email(
    to_email="customer@example.com",
    subject="Your Report",
    html_content="<p>Attached is your report.</p>",
    attachments=[{
        'content': pdf_content,
        'filename': 'report.pdf'
    }]
)
```

## Gmail Sending Limits

**Free Gmail Accounts:**
- 500 emails per day
- 100 recipients per email

**Google Workspace (Paid):**
- 2,000 emails per day
- 2,000 recipients per email

If you need to send more, consider:
- Mailgun (10,000 free emails/month)
- SendGrid (100 free emails/day)

## Troubleshooting

### "Authentication failed"
**Problem:** Gmail rejected your credentials

**Solutions:**
1. Make sure you're using an **App Password**, not your regular Gmail password
2. Check that 2-Step Verification is enabled
3. Regenerate the App Password and try again
4. Remove any spaces from the App Password in `.env`

### "Less secure app access"
**Problem:** Gmail blocked the login attempt

**Solution:** This is why you need an App Password. Regular passwords won't work. Follow steps 1-2 above.

### Emails going to spam
**Problem:** Recipients receive emails in spam folder

**Solutions:**
1. Ask recipients to mark as "Not Spam"
2. Set up SPF/DKIM records for six3.agency domain
3. Build sender reputation gradually (don't send 1000 emails immediately)
4. Avoid spam trigger words in subject/content

### "Daily sending quota exceeded"
**Problem:** You hit Gmail's 500/day limit

**Solutions:**
1. Wait 24 hours for the limit to reset
2. Upgrade to Google Workspace for 2,000/day
3. Switch to Mailgun for higher volumes

### Connection timeout
**Problem:** Can't connect to Gmail SMTP

**Solutions:**
1. Check your internet connection
2. Make sure port 587 isn't blocked by firewall
3. Try using port 465 instead (SSL)

## Best Practices

1. **Start with Mailtrap**
   - Test all your email flows with Mailtrap first
   - Make sure emails look good and links work
   - Only switch to Gmail when ready for production

2. **Warm Up Your Sender Reputation**
   - Start by sending to small groups
   - Gradually increase volume over days/weeks
   - Monitor spam reports

3. **Use Proper Email Formatting**
   - Always include both HTML and text versions
   - Test emails in different clients (Gmail, Outlook, etc.)
   - Include unsubscribe links

4. **Monitor Deliverability**
   - Check bounce rates
   - Watch for spam complaints
   - Keep email list clean

5. **Secure Your Credentials**
   - Never commit `.env` file to git
   - Use App Passwords, not regular passwords
   - Rotate passwords periodically

## Switching to Production Checklist

Before changing `EMAIL_PROVIDER=gmail`:

- [ ] Tested all email flows with Mailtrap
- [ ] Generated Gmail App Password
- [ ] Tested connection with `test_connection()`
- [ ] Sent test email to yourself successfully
- [ ] Verified email doesn't go to spam
- [ ] Set up email templates properly
- [ ] Added unsubscribe functionality
- [ ] Reviewed sending volumes (stay under limits)
- [ ] Backed up Mailtrap configuration (for switching back)

## Support

**Gmail Help:**
- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [App Passwords](https://support.google.com/accounts/answer/185833)
- [2-Step Verification](https://support.google.com/accounts/answer/185839)

**Integration Issues:**
- Check logs in `integrations/email/gmail_integration.py`
- Run connection test: `python integrations/email/gmail_integration.py`

## Next Steps

1. ✅ Complete steps 1-5 above
2. Test with Mailtrap during development
3. Switch to Gmail when ready for production
4. Monitor email deliverability
5. Consider Mailgun if you need higher volumes

You're all set! Your hello@six3.agency Gmail is ready to send real emails through the platform.
