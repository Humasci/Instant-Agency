"""
Mailtrap Email Integration for SIX3 Agency

Mailtrap is a safe email testing service that captures all emails
in a test inbox without sending them to real recipients. Perfect for
development, staging, and testing environments.

Handles:
- Email testing and previewing
- Email capture and inspection
- Safe development environment
- Email rendering across clients
- Spam score checking
- Email HTML/CSS validation

Requirements:
- Mailtrap API token
- Mailtrap inbox ID
- requests Python package

Advantages of Mailtrap:
- Free tier with 500 emails/month
- Safe testing - no emails sent to real addresses
- Email preview across 100+ email clients
- Spam score analysis
- HTML/CSS validation
- Email forwarding for testing
- Clean, developer-friendly interface
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests not available. Install with: pip install requests")

logger = logging.getLogger(__name__)


class MailtrapIntegration:
    """Mailtrap email integration for safe email testing"""

    def __init__(self,
                 api_token: Optional[str] = None,
                 inbox_id: Optional[str] = None,
                 smtp_username: Optional[str] = None,
                 smtp_password: Optional[str] = None):
        """
        Initialize Mailtrap integration

        Args:
            api_token: Mailtrap API token (if not provided, reads from MAILTRAP_API_TOKEN env var)
            inbox_id: Mailtrap inbox ID (if not provided, reads from MAILTRAP_INBOX_ID env var)
            smtp_username: SMTP username (if not provided, reads from MAILTRAP_SMTP_USERNAME env var)
            smtp_password: SMTP password (if not provided, reads from MAILTRAP_SMTP_PASSWORD env var)
        """
        # API credentials for reading emails and stats
        self.api_token = api_token or os.getenv('MAILTRAP_API_TOKEN')
        self.inbox_id = inbox_id or os.getenv('MAILTRAP_INBOX_ID')

        # SMTP credentials for sending emails
        self.smtp_username = smtp_username or os.getenv('MAILTRAP_SMTP_USERNAME')
        self.smtp_password = smtp_password or os.getenv('MAILTRAP_SMTP_PASSWORD')

        # Mailtrap SMTP server configuration
        self.smtp_host = os.getenv('MAILTRAP_SMTP_HOST', 'sandbox.smtp.mailtrap.io')
        self.smtp_port = int(os.getenv('MAILTRAP_SMTP_PORT', '2525'))

        # Mailtrap API configuration
        self.api_base_url = 'https://mailtrap.io/api/v1'

        # Default sender information
        self.default_from_email = os.getenv('MAILTRAP_FROM_EMAIL', 'hello@six3.agency')
        self.default_from_name = os.getenv('MAILTRAP_FROM_NAME', 'SIX3 Agency')

        logger.info(f"Mailtrap integration initialized for inbox: {self.inbox_id}")

    def send_email(self,
                   to_email: Union[str, List[str]],
                   subject: str,
                   html_content: str = None,
                   text_content: str = None,
                   from_email: str = None,
                   from_name: str = None,
                   cc: List[str] = None,
                   bcc: List[str] = None,
                   attachments: List[Dict] = None) -> Dict[str, Any]:
        """
        Send an email via Mailtrap SMTP

        Args:
            to_email: Recipient email address(es)
            subject: Email subject line
            html_content: HTML email content
            text_content: Plain text email content
            from_email: Sender email (defaults to configured sender)
            from_name: Sender name (defaults to configured name)
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of attachment dictionaries with 'content' and 'filename'

        Returns:
            Dict with success status and response details
        """
        try:
            if not self.smtp_username or not self.smtp_password:
                return {
                    'success': False,
                    'error': 'SMTP credentials not configured. Set MAILTRAP_SMTP_USERNAME and MAILTRAP_SMTP_PASSWORD',
                    'timestamp': datetime.utcnow().isoformat()
                }

            # Set up sender
            from_email = from_email or self.default_from_email
            from_name = from_name or self.default_from_name

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{from_name} <{from_email}>"

            # Prepare recipients
            if isinstance(to_email, str):
                to_email = [to_email]
            msg['To'] = ', '.join(to_email)

            if cc:
                msg['Cc'] = ', '.join(cc)

            # Add content
            if not html_content and not text_content:
                return {
                    'success': False,
                    'error': 'Either html_content or text_content must be provided',
                    'timestamp': datetime.utcnow().isoformat()
                }

            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)

            if html_content:
                part2 = MIMEText(html_content, 'html')
                msg.attach(part2)

            # Add attachments
            if attachments:
                for attachment in attachments:
                    if 'content' in attachment and 'filename' in attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment['content'])
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {attachment["filename"]}'
                        )
                        msg.attach(part)

            # Prepare all recipients for SMTP
            all_recipients = to_email.copy()
            if cc:
                all_recipients.extend(cc)
            if bcc:
                all_recipients.extend(bcc)

            # Send via Mailtrap SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(from_email, all_recipients, msg.as_string())

            logger.info(f"Email sent successfully via Mailtrap to {len(all_recipients)} recipient(s)")

            return {
                'success': True,
                'message': 'Email sent to Mailtrap inbox',
                'to_emails': to_email,
                'subject': subject,
                'smtp_host': self.smtp_host,
                'timestamp': datetime.utcnow().isoformat()
            }

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {str(e)}")
            return {
                'success': False,
                'error': f'SMTP error: {str(e)}',
                'to_emails': to_email if isinstance(to_email, list) else [to_email],
                'subject': subject,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def send_bulk_emails(self,
                        recipients: List[Dict[str, Any]],
                        subject: str,
                        html_content: str = None,
                        text_content: str = None) -> Dict[str, Any]:
        """
        Send emails to multiple recipients

        Args:
            recipients: List of recipient dicts with 'email' and optional data
            subject: Email subject line
            html_content: HTML email content
            text_content: Plain text email content

        Returns:
            Dict with summary of sent emails
        """
        results = []
        success_count = 0

        for recipient in recipients:
            email = recipient.get('email')
            if not email:
                continue

            # Personalize content if variables provided
            personalized_html = html_content
            personalized_text = text_content

            if recipient.get('name'):
                if personalized_html:
                    personalized_html = personalized_html.replace('%recipient.name%', recipient['name'])
                if personalized_text:
                    personalized_text = personalized_text.replace('%recipient.name%', recipient['name'])

            if recipient.get('company'):
                if personalized_html:
                    personalized_html = personalized_html.replace('%recipient.company%', recipient['company'])
                if personalized_text:
                    personalized_text = personalized_text.replace('%recipient.company%', recipient['company'])

            # Send individual email
            result = self.send_email(
                to_email=email,
                subject=subject,
                html_content=personalized_html,
                text_content=personalized_text
            )

            results.append(result)
            if result.get('success'):
                success_count += 1

        return {
            'success': True,
            'total_recipients': len(recipients),
            'total_sent': success_count,
            'total_failed': len(recipients) - success_count,
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_inbox_messages(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get messages from Mailtrap inbox using API

        Args:
            limit: Maximum number of messages to retrieve

        Returns:
            Dict with inbox messages
        """
        if not REQUESTS_AVAILABLE:
            return {
                'success': False,
                'error': 'requests package not installed',
                'timestamp': datetime.utcnow().isoformat()
            }

        if not self.api_token or not self.inbox_id:
            return {
                'success': False,
                'error': 'API token or inbox ID not configured',
                'timestamp': datetime.utcnow().isoformat()
            }

        try:
            url = f"{self.api_base_url}/inboxes/{self.inbox_id}/messages"
            headers = {
                'Api-Token': self.api_token,
                'Content-Type': 'application/json'
            }
            params = {'page': 1, 'limit': limit}

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            messages = response.json()

            return {
                'success': True,
                'inbox_id': self.inbox_id,
                'message_count': len(messages),
                'messages': messages,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get inbox messages: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def get_message_details(self, message_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific message

        Args:
            message_id: Mailtrap message ID

        Returns:
            Dict with message details
        """
        if not REQUESTS_AVAILABLE or not self.api_token or not self.inbox_id:
            return {
                'success': False,
                'error': 'API not configured or requests not available',
                'timestamp': datetime.utcnow().isoformat()
            }

        try:
            url = f"{self.api_base_url}/inboxes/{self.inbox_id}/messages/{message_id}"
            headers = {
                'Api-Token': self.api_token,
                'Content-Type': 'application/json'
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            message = response.json()

            return {
                'success': True,
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get message details: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def delete_all_messages(self) -> Dict[str, Any]:
        """
        Delete all messages from the inbox

        Returns:
            Dict with operation result
        """
        if not REQUESTS_AVAILABLE or not self.api_token or not self.inbox_id:
            return {
                'success': False,
                'error': 'API not configured or requests not available',
                'timestamp': datetime.utcnow().isoformat()
            }

        try:
            url = f"{self.api_base_url}/inboxes/{self.inbox_id}/clean"
            headers = {
                'Api-Token': self.api_token,
                'Content-Type': 'application/json'
            }

            response = requests.patch(url, headers=headers)
            response.raise_for_status()

            return {
                'success': True,
                'message': 'All messages deleted from inbox',
                'inbox_id': self.inbox_id,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to delete messages: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def test_connection(self) -> Dict[str, Any]:
        """
        Test the Mailtrap SMTP connection

        Returns:
            Dict with connection test results
        """
        try:
            if not self.smtp_username or not self.smtp_password:
                return {
                    'success': False,
                    'connection_status': 'failed',
                    'error': 'SMTP credentials not configured',
                    'smtp_access': False,
                    'timestamp': datetime.utcnow().isoformat()
                }

            # Test SMTP connection
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)

            # Test API connection if configured
            api_access = False
            if REQUESTS_AVAILABLE and self.api_token and self.inbox_id:
                try:
                    url = f"{self.api_base_url}/inboxes/{self.inbox_id}"
                    headers = {'Api-Token': self.api_token}
                    response = requests.get(url, headers=headers, timeout=10)
                    api_access = response.status_code == 200
                except:
                    api_access = False

            return {
                'success': True,
                'connection_status': 'connected',
                'smtp_host': self.smtp_host,
                'smtp_port': self.smtp_port,
                'smtp_access': True,
                'api_access': api_access,
                'inbox_id': self.inbox_id,
                'timestamp': datetime.utcnow().isoformat()
            }

        except smtplib.SMTPException as e:
            logger.error(f"Mailtrap SMTP connection test failed: {str(e)}")
            return {
                'success': False,
                'connection_status': 'failed',
                'error': f'SMTP error: {str(e)}',
                'smtp_access': False,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Mailtrap connection test failed: {str(e)}")
            return {
                'success': False,
                'connection_status': 'failed',
                'error': str(e),
                'smtp_access': False,
                'timestamp': datetime.utcnow().isoformat()
            }


# Email template helpers (reusable from Mailgun)
class MailtrapEmailTemplates:
    """Pre-built email templates for common use cases"""

    @staticmethod
    def welcome_email(name: str, company_name: str = "SIX3 Agency") -> Dict[str, str]:
        """Generate welcome email content"""
        return {
            'subject': f"Welcome to {company_name}!",
            'html_content': f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
                <div style="padding: 20px;">
                    <h1 style="color: #2c5aa0; text-align: center;">Welcome to {company_name}!</h1>
                    <p>Hi %recipient.name%,</p>
                    <p>Thank you for joining {company_name}! We're excited to help you automate and scale your business with AI-powered solutions.</p>

                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #2c5aa0;">What happens next?</h3>
                        <ul style="padding-left: 20px;">
                            <li>Setup consultation - We'll schedule a call to understand your needs</li>
                            <li>Custom configuration - We'll tailor our AI agents to your workflow</li>
                            <li>Training & documentation - Complete guides and video tutorials</li>
                            <li>Go live! - Start automating your business processes</li>
                        </ul>
                    </div>

                    <p>Questions? Just reply to this email - we're here to help!</p>

                    <p>Best regards,<br>
                    The {company_name} Team</p>
                </div>
            </body>
            </html>
            """,
            'text_content': f"""
            Welcome to {company_name}!

            Hi %recipient.name%,

            Thank you for joining {company_name}! We're excited to help you automate and scale your business with AI-powered solutions.

            What happens next?
            - Setup consultation - We'll schedule a call to understand your needs
            - Custom configuration - We'll tailor our AI agents to your workflow
            - Training & documentation - Complete guides and video tutorials
            - Go live! - Start automating your business processes

            Questions? Just reply to this email - we're here to help!

            Best regards,
            The {company_name} Team
            """
        }

    @staticmethod
    def test_email() -> Dict[str, str]:
        """Generate a simple test email"""
        return {
            'subject': 'Test Email from SIX3 Agency',
            'html_content': """
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #2c5aa0;">Test Email</h2>
                <p>This is a test email sent via Mailtrap integration.</p>
                <p>If you're reading this, the email system is working correctly!</p>
                <p>Timestamp: {timestamp}</p>
            </body>
            </html>
            """.format(timestamp=datetime.utcnow().isoformat()),
            'text_content': f"""
            Test Email

            This is a test email sent via Mailtrap integration.
            If you're reading this, the email system is working correctly!

            Timestamp: {datetime.utcnow().isoformat()}
            """
        }


# Usage example
if __name__ == "__main__":
    # Example usage (requires Mailtrap credentials in environment variables)
    import os

    if os.getenv('MAILTRAP_SMTP_USERNAME') and os.getenv('MAILTRAP_SMTP_PASSWORD'):
        mt = MailtrapIntegration()

        # Test connection
        test_result = mt.test_connection()
        print("Connection test:", json.dumps(test_result, indent=2))

        # Send test email
        if test_result.get('success'):
            test_template = MailtrapEmailTemplates.test_email()
            result = mt.send_email(
                to_email="test@example.com",
                subject=test_template['subject'],
                html_content=test_template['html_content'],
                text_content=test_template['text_content']
            )
            print("\nEmail send result:", json.dumps(result, indent=2))

            # Get inbox messages (if API configured)
            if mt.api_token and mt.inbox_id:
                messages = mt.get_inbox_messages(limit=10)
                print("\nInbox messages:", json.dumps(messages, indent=2))
    else:
        print("Set MAILTRAP_SMTP_USERNAME and MAILTRAP_SMTP_PASSWORD environment variables to test integration")
        print("\nTo get your Mailtrap credentials:")
        print("1. Sign up at https://mailtrap.io/")
        print("2. Go to Email Testing > Inboxes")
        print("3. Select your inbox")
        print("4. Copy SMTP credentials from the Integration dropdown")
