"""
Gmail SMTP Integration for Production Email Sending

Use your actual Gmail account (hello@six3.agency) to send real emails.
Requires Gmail App Password for authentication.

Setup:
1. Enable 2-Step Verification in Google Account
2. Generate App Password: Google Account > Security > App Passwords
3. Use the 16-character app password (not your regular Gmail password)
"""

import os
import logging
import smtplib
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

logger = logging.getLogger(__name__)


class GmailIntegration:
    """Gmail SMTP integration for production email sending"""

    def __init__(self,
                 gmail_address: Optional[str] = None,
                 gmail_app_password: Optional[str] = None,
                 from_name: Optional[str] = None):
        """
        Initialize Gmail integration

        Args:
            gmail_address: Your Gmail address (e.g., hello@six3.agency)
            gmail_app_password: Gmail App Password (NOT your regular password)
            from_name: Display name for sender
        """
        self.gmail_address = gmail_address or os.getenv('GMAIL_ADDRESS')
        self.gmail_app_password = gmail_app_password or os.getenv('GMAIL_APP_PASSWORD')
        self.from_name = from_name or os.getenv('GMAIL_FROM_NAME', 'SIX3 Agency')

        if not self.gmail_address:
            raise ValueError("Gmail address required. Set GMAIL_ADDRESS environment variable")

        if not self.gmail_app_password:
            raise ValueError("Gmail app password required. Set GMAIL_APP_PASSWORD environment variable")

        # Gmail SMTP configuration
        self.smtp_host = 'smtp.gmail.com'
        self.smtp_port = 587

        logger.info(f"Gmail integration initialized for: {self.gmail_address}")

    def send_email(self,
                   to_email: Union[str, List[str]],
                   subject: str,
                   html_content: str = None,
                   text_content: str = None,
                   cc: List[str] = None,
                   bcc: List[str] = None,
                   attachments: List[Dict] = None) -> Dict[str, Any]:
        """
        Send an email via Gmail SMTP

        Args:
            to_email: Recipient email address(es)
            subject: Email subject line
            html_content: HTML email content
            text_content: Plain text email content
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of attachment dicts with 'content' and 'filename'

        Returns:
            Dict with success status and response details
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.gmail_address}>"

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

            # Prepare all recipients
            all_recipients = to_email.copy()
            if cc:
                all_recipients.extend(cc)
            if bcc:
                all_recipients.extend(bcc)

            # Send via Gmail SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.gmail_address, self.gmail_app_password)
                server.sendmail(self.gmail_address, all_recipients, msg.as_string())

            logger.info(f"Email sent successfully via Gmail to {len(all_recipients)} recipient(s)")

            return {
                'success': True,
                'message': 'Email sent successfully',
                'to_emails': to_email,
                'subject': subject,
                'from_email': self.gmail_address,
                'timestamp': datetime.utcnow().isoformat()
            }

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Gmail authentication failed: {str(e)}")
            return {
                'success': False,
                'error': 'Authentication failed. Check your Gmail address and App Password.',
                'help': 'Make sure you are using an App Password, not your regular Gmail password.',
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

    def test_connection(self) -> Dict[str, Any]:
        """
        Test the Gmail SMTP connection

        Returns:
            Dict with connection test results
        """
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.gmail_address, self.gmail_app_password)

            return {
                'success': True,
                'connection_status': 'connected',
                'smtp_host': self.smtp_host,
                'smtp_port': self.smtp_port,
                'gmail_address': self.gmail_address,
                'smtp_access': True,
                'timestamp': datetime.utcnow().isoformat()
            }

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Gmail authentication failed: {str(e)}")
            return {
                'success': False,
                'connection_status': 'authentication_failed',
                'error': 'Invalid Gmail address or App Password',
                'help': 'Generate an App Password: Google Account > Security > App Passwords',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Gmail connection test failed: {str(e)}")
            return {
                'success': False,
                'connection_status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


# Usage example
if __name__ == "__main__":
    import os

    if os.getenv('GMAIL_ADDRESS') and os.getenv('GMAIL_APP_PASSWORD'):
        gmail = GmailIntegration()

        # Test connection
        test_result = gmail.test_connection()
        print("Connection test:", test_result)

        # Send test email
        if test_result.get('success'):
            result = gmail.send_email(
                to_email="test@example.com",
                subject="Test from SIX3 Agency",
                html_content="<h1>Hello!</h1><p>This is a test email from hello@six3.agency</p>",
                text_content="Hello! This is a test email from hello@six3.agency"
            )
            print("Email send result:", result)
    else:
        print("Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD environment variables")
