"""
SendGrid Email Integration for SIX3 Agency

Handles:
- Automated email campaigns
- Transactional emails
- Template-based emails
- Email tracking and analytics
- Contact list management

Requirements:
- SendGrid API key
- sendgrid Python package
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, From, To, Subject, PlainTextContent, HtmlContent, Attachment, FileContent, FileName, FileType, Disposition
    from sendgrid.helpers.mail.mail import MailSettings, SandBoxMode
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

logger = logging.getLogger(__name__)


class SendGridIntegration:
    """SendGrid email integration for automated campaigns and transactional emails"""
    
    def __init__(self, api_key: Optional[str] = None, sandbox_mode: bool = False):
        """
        Initialize SendGrid integration
        
        Args:
            api_key: SendGrid API key (if not provided, reads from SENDGRID_API_KEY env var)
            sandbox_mode: If True, emails won't be sent (for testing)
        """
        if not SENDGRID_AVAILABLE:
            raise ImportError("SendGrid package not installed. Run: pip install sendgrid")
        
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')
        if not self.api_key:
            raise ValueError("SendGrid API key required. Set SENDGRID_API_KEY environment variable or pass api_key parameter")
        
        self.sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
        self.sandbox_mode = sandbox_mode
        
        # Default sender information
        self.default_from_email = os.getenv('SENDGRID_FROM_EMAIL', 'hello@six3.agency')
        self.default_from_name = os.getenv('SENDGRID_FROM_NAME', 'SIX3 Agency')
        
        logger.info(f"SendGrid integration initialized (sandbox_mode: {sandbox_mode})")
    
    def send_email(self, 
                   to_email: str, 
                   subject: str, 
                   html_content: str = None, 
                   plain_text_content: str = None,
                   from_email: str = None,
                   from_name: str = None,
                   template_id: str = None,
                   dynamic_template_data: Dict = None,
                   attachments: List[Dict] = None) -> Dict[str, Any]:
        """
        Send a single email
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML email content
            plain_text_content: Plain text email content
            from_email: Sender email (defaults to configured sender)
            from_name: Sender name (defaults to configured name)
            template_id: SendGrid template ID (for template-based emails)
            dynamic_template_data: Data for template substitution
            attachments: List of attachment dictionaries
            
        Returns:
            Dict with success status and response details
        """
        try:
            # Set up sender
            from_email = from_email or self.default_from_email
            from_name = from_name or self.default_from_name
            from_sender = From(from_email, from_name)
            
            # Set up recipient
            to_recipient = To(to_email)
            
            # Create mail object
            if template_id:
                # Template-based email
                mail = Mail(from_sender, to_recipient)
                mail.template_id = template_id
                if dynamic_template_data:
                    mail.dynamic_template_data = dynamic_template_data
            else:
                # Regular email with content
                mail = Mail(
                    from_email=from_sender,
                    to_emails=to_recipient,
                    subject=Subject(subject)
                )
                
                if html_content:
                    mail.content = HtmlContent(html_content)
                elif plain_text_content:
                    mail.content = PlainTextContent(plain_text_content)
                else:
                    raise ValueError("Either html_content, plain_text_content, or template_id must be provided")
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    mail.attachment = Attachment(
                        FileContent(attachment.get('content')),
                        FileName(attachment.get('filename')),
                        FileType(attachment.get('type', 'application/octet-stream')),
                        Disposition('attachment')
                    )
            
            # Enable sandbox mode if configured
            if self.sandbox_mode:
                mail.mail_settings = MailSettings()
                mail.mail_settings.sandbox_mode = SandBoxMode(True)
            
            # Send email
            response = self.sg.send(mail)
            
            return {
                'success': True,
                'status_code': response.status_code,
                'message_id': response.headers.get('X-Message-Id'),
                'to_email': to_email,
                'subject': subject,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'to_email': to_email,
                'subject': subject,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def send_bulk_emails(self, 
                        recipients: List[Dict[str, str]], 
                        subject: str,
                        html_content: str = None,
                        plain_text_content: str = None,
                        template_id: str = None) -> Dict[str, Any]:
        """
        Send emails to multiple recipients
        
        Args:
            recipients: List of recipient dicts with 'email' and optional 'name'
            subject: Email subject line
            html_content: HTML email content
            plain_text_content: Plain text email content
            template_id: SendGrid template ID
            
        Returns:
            Dict with summary of sent emails
        """
        results = []
        successful = 0
        failed = 0
        
        for recipient in recipients:
            email = recipient.get('email')
            name = recipient.get('name', '')
            dynamic_data = recipient.get('dynamic_data', {})
            
            if not email:
                failed += 1
                continue
            
            result = self.send_email(
                to_email=email,
                subject=subject.format(name=name) if name else subject,
                html_content=html_content,
                plain_text_content=plain_text_content,
                template_id=template_id,
                dynamic_template_data=dynamic_data
            )
            
            results.append(result)
            if result['success']:
                successful += 1
            else:
                failed += 1
        
        return {
            'total_sent': len(recipients),
            'successful': successful,
            'failed': failed,
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def create_campaign(self, 
                       name: str,
                       subject: str,
                       sender_id: int,
                       list_ids: List[int],
                       html_content: str = None,
                       plain_content: str = None) -> Dict[str, Any]:
        """
        Create an email campaign
        
        Args:
            name: Campaign name
            subject: Email subject
            sender_id: SendGrid sender ID
            list_ids: List of contact list IDs
            html_content: HTML content
            plain_content: Plain text content
            
        Returns:
            Dict with campaign creation response
        """
        try:
            campaign_data = {
                "name": name,
                "subject": subject,
                "sender_id": sender_id,
                "list_ids": list_ids,
                "html_content": html_content or "",
                "plain_content": plain_content or ""
            }
            
            response = self.sg.client.campaigns.post(request_body=campaign_data)
            
            return {
                'success': True,
                'campaign_id': json.loads(response.body)['id'],
                'status_code': response.status_code,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create campaign '{name}': {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def schedule_campaign(self, campaign_id: int, send_at: datetime) -> Dict[str, Any]:
        """
        Schedule a campaign for future sending
        
        Args:
            campaign_id: Campaign ID
            send_at: When to send the campaign
            
        Returns:
            Dict with scheduling response
        """
        try:
            schedule_data = {
                "send_at": int(send_at.timestamp())
            }
            
            response = self.sg.client.campaigns._(campaign_id).schedules.post(
                request_body=schedule_data
            )
            
            return {
                'success': True,
                'campaign_id': campaign_id,
                'scheduled_for': send_at.isoformat(),
                'status_code': response.status_code,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to schedule campaign {campaign_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def add_contact_to_list(self, email: str, list_id: int, first_name: str = None, last_name: str = None) -> Dict[str, Any]:
        """
        Add a contact to a mailing list
        
        Args:
            email: Contact email
            list_id: List ID to add contact to
            first_name: Contact first name
            last_name: Contact last name
            
        Returns:
            Dict with operation result
        """
        try:
            contact_data = {
                "list_ids": [list_id],
                "contacts": [
                    {
                        "email": email,
                        "first_name": first_name or "",
                        "last_name": last_name or ""
                    }
                ]
            }
            
            response = self.sg.client.marketing.contacts.put(request_body=contact_data)
            
            return {
                'success': True,
                'email': email,
                'list_id': list_id,
                'status_code': response.status_code,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to add contact {email} to list {list_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_email_stats(self, start_date: datetime, end_date: datetime = None) -> Dict[str, Any]:
        """
        Get email delivery statistics
        
        Args:
            start_date: Start date for stats
            end_date: End date for stats (defaults to now)
            
        Returns:
            Dict with email statistics
        """
        try:
            end_date = end_date or datetime.utcnow()
            
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
            
            response = self.sg.client.stats.get(query_params=params)
            stats_data = json.loads(response.body)
            
            # Aggregate stats
            total_stats = {
                'delivered': 0,
                'opens': 0,
                'clicks': 0,
                'bounces': 0,
                'spam_reports': 0,
                'unsubscribes': 0
            }
            
            for day_stats in stats_data:
                for stat in day_stats.get('stats', []):
                    for metric in stat.get('metrics', {}):
                        if metric in total_stats:
                            total_stats[metric] += stat['metrics'][metric]
            
            # Calculate rates
            delivered = total_stats['delivered']
            if delivered > 0:
                open_rate = (total_stats['opens'] / delivered) * 100
                click_rate = (total_stats['clicks'] / delivered) * 100
                bounce_rate = (total_stats['bounces'] / delivered) * 100
            else:
                open_rate = click_rate = bounce_rate = 0
            
            return {
                'success': True,
                'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                'totals': total_stats,
                'rates': {
                    'open_rate': round(open_rate, 2),
                    'click_rate': round(click_rate, 2),
                    'bounce_rate': round(bounce_rate, 2)
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get email stats: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the SendGrid API connection
        
        Returns:
            Dict with connection test results
        """
        try:
            # Test by sending a test email to sender address
            test_result = self.send_email(
                to_email=self.default_from_email,
                subject="SendGrid Integration Test",
                plain_text_content="This is a test email to verify SendGrid integration is working.",
                html_content="<p>This is a test email to verify SendGrid integration is working.</p>"
            )
            
            return {
                'success': test_result['success'],
                'api_key_valid': True,
                'connection_status': 'connected' if test_result['success'] else 'failed',
                'test_email_sent': test_result['success'],
                'sandbox_mode': self.sandbox_mode,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"SendGrid connection test failed: {str(e)}")
            return {
                'success': False,
                'api_key_valid': False,
                'connection_status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


# Email template helpers
class EmailTemplates:
    """Pre-built email templates for common use cases"""
    
    @staticmethod
    def welcome_email(name: str, company_name: str = "SIX3 Agency") -> Dict[str, str]:
        """Generate welcome email content"""
        return {
            'subject': f"Welcome to {company_name}, {name}!",
            'html_content': f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2c5aa0;">Welcome to {company_name}!</h1>
                    <p>Hi {name},</p>
                    <p>Thank you for joining {company_name}! We're excited to help you automate and scale your business with AI-powered agents.</p>
                    <p>Here's what you can expect next:</p>
                    <ul>
                        <li>Setup assistance from our team</li>
                        <li>Training resources and documentation</li>
                        <li>24/7 support for any questions</li>
                    </ul>
                    <p>If you have any questions, feel free to reach out to us.</p>
                    <p>Best regards,<br>The {company_name} Team</p>
                </div>
            </body>
            </html>
            """,
            'plain_content': f"""
            Welcome to {company_name}!
            
            Hi {name},
            
            Thank you for joining {company_name}! We're excited to help you automate and scale your business with AI-powered agents.
            
            Here's what you can expect next:
            - Setup assistance from our team
            - Training resources and documentation
            - 24/7 support for any questions
            
            If you have any questions, feel free to reach out to us.
            
            Best regards,
            The {company_name} Team
            """
        }
    
    @staticmethod
    def lead_follow_up(name: str, company: str, interest: str) -> Dict[str, str]:
        """Generate lead follow-up email content"""
        return {
            'subject': f"Following up on your interest in AI automation, {name}",
            'html_content': f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2c5aa0;">Thank you for your interest!</h1>
                    <p>Hi {name},</p>
                    <p>Thanks for reaching out about {interest}. We'd love to show you how SIX3 Agency can help {company} with AI automation.</p>
                    <p><strong>Would you like to schedule a 15-minute demo?</strong></p>
                    <p>During our call, we'll:</p>
                    <ul>
                        <li>Review your current processes</li>
                        <li>Identify automation opportunities</li>
                        <li>Show you relevant AI agents in action</li>
                        <li>Discuss potential ROI</li>
                    </ul>
                    <p><a href="https://calendly.com/six3agency/demo" style="background: #2c5aa0; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px;">Schedule Demo</a></p>
                    <p>Best regards,<br>SIX3 Agency Team</p>
                </div>
            </body>
            </html>
            """,
            'plain_content': f"""
            Thank you for your interest!
            
            Hi {name},
            
            Thanks for reaching out about {interest}. We'd love to show you how SIX3 Agency can help {company} with AI automation.
            
            Would you like to schedule a 15-minute demo?
            
            During our call, we'll:
            - Review your current processes
            - Identify automation opportunities
            - Show you relevant AI agents in action
            - Discuss potential ROI
            
            Schedule Demo: https://calendly.com/six3agency/demo
            
            Best regards,
            SIX3 Agency Team
            """
        }


# Usage example
if __name__ == "__main__":
    # Example usage (requires SENDGRID_API_KEY environment variable)
    import os
    
    if os.getenv('SENDGRID_API_KEY'):
        sg = SendGridIntegration(sandbox_mode=True)  # Use sandbox for testing
        
        # Test connection
        test_result = sg.test_connection()
        print("Connection test:", test_result)
        
        # Send welcome email
        welcome_template = EmailTemplates.welcome_email("John Doe")
        result = sg.send_email(
            to_email="test@example.com",
            subject=welcome_template['subject'],
            html_content=welcome_template['html_content'],
            plain_text_content=welcome_template['plain_content']
        )
        print("Email send result:", result)
    else:
        print("Set SENDGRID_API_KEY environment variable to test integration")