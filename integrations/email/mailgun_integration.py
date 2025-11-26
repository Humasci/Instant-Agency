"""
Mailgun Email Integration for SIX3 Agency

Handles:
- Automated email campaigns
- Transactional emails
- Email validation and verification
- Email tracking and analytics
- Mailing lists management
- Template-based emails

Requirements:
- Mailgun API key
- Mailgun domain
- requests Python package

Advantages of Mailgun:
- Free 100 emails/day forever
- Excellent deliverability
- Simple API
- Great for transactional emails
- Email validation API included
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import json
import base64

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests not available. Install with: pip install requests")

logger = logging.getLogger(__name__)


class MailgunIntegration:
    """Mailgun email integration for automated campaigns and transactional emails"""
    
    def __init__(self, api_key: Optional[str] = None, domain: Optional[str] = None, region: str = "us"):
        """
        Initialize Mailgun integration
        
        Args:
            api_key: Mailgun API key (if not provided, reads from MAILGUN_API_KEY env var)
            domain: Mailgun domain (if not provided, reads from MAILGUN_DOMAIN env var)
            region: Mailgun region ("us" or "eu")
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("Requests package not installed. Run: pip install requests")
        
        self.api_key = api_key or os.getenv('MAILGUN_API_KEY')
        self.domain = domain or os.getenv('MAILGUN_DOMAIN')
        
        if not self.api_key:
            raise ValueError("Mailgun API key required. Set MAILGUN_API_KEY environment variable or pass api_key parameter")
        
        if not self.domain:
            raise ValueError("Mailgun domain required. Set MAILGUN_DOMAIN environment variable or pass domain parameter")
        
        # Set API endpoint based on region
        if region == "eu":
            self.base_url = "https://api.eu.mailgun.net/v3"
        else:
            self.base_url = "https://api.mailgun.net/v3"
        
        # Prepare auth for requests
        self.auth = ("api", self.api_key)
        
        # Default sender information
        self.default_from_email = os.getenv('MAILGUN_FROM_EMAIL', f'hello@{self.domain}')
        self.default_from_name = os.getenv('MAILGUN_FROM_NAME', 'SIX3 Agency')
        
        logger.info(f"Mailgun integration initialized for domain: {self.domain}")
    
    def send_email(self, 
                   to_email: Union[str, List[str]], 
                   subject: str, 
                   html_content: str = None, 
                   text_content: str = None,
                   from_email: str = None,
                   from_name: str = None,
                   cc: List[str] = None,
                   bcc: List[str] = None,
                   attachments: List[Dict] = None,
                   tags: List[str] = None,
                   variables: Dict[str, Any] = None,
                   template: str = None,
                   tracking: bool = True) -> Dict[str, Any]:
        """
        Send a single email or to multiple recipients
        
        Args:
            to_email: Recipient email address(es)
            subject: Email subject line
            html_content: HTML email content
            text_content: Plain text email content
            from_email: Sender email (defaults to configured sender)
            from_name: Sender name (defaults to configured name)
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of attachment dictionaries
            tags: List of tags for tracking
            variables: Variables for template substitution
            template: Template name for template-based emails
            tracking: Enable click and open tracking
            
        Returns:
            Dict with success status and response details
        """
        try:
            # Set up sender
            from_email = from_email or self.default_from_email
            from_name = from_name or self.default_from_name
            from_field = f"{from_name} <{from_email}>"
            
            # Prepare recipients
            if isinstance(to_email, str):
                to_email = [to_email]
            
            # Build email data
            data = {
                'from': from_field,
                'to': to_email,
                'subject': subject
            }
            
            # Add content
            if template:
                data['template'] = template
                if variables:
                    data.update({f'h:X-Mailgun-Variables': json.dumps(variables)})
            else:
                if html_content:
                    data['html'] = html_content
                if text_content:
                    data['text'] = text_content
                
                if not html_content and not text_content:
                    raise ValueError("Either html_content, text_content, or template must be provided")
            
            # Add optional fields
            if cc:
                data['cc'] = cc
            if bcc:
                data['bcc'] = bcc
            if tags:
                for tag in tags:
                    data[f'o:tag'] = tag
            
            # Tracking settings
            if tracking:
                data['o:tracking'] = 'yes'
                data['o:tracking-clicks'] = 'yes'
                data['o:tracking-opens'] = 'yes'
            
            # Prepare files for attachments
            files = []
            if attachments:
                for i, attachment in enumerate(attachments):
                    if 'content' in attachment and 'filename' in attachment:
                        files.append(('attachment', (
                            attachment['filename'],
                            attachment['content'],
                            attachment.get('content_type', 'application/octet-stream')
                        )))
            
            # Send email
            url = f"{self.base_url}/{self.domain}/messages"
            
            if files:
                response = requests.post(url, auth=self.auth, data=data, files=files)
            else:
                response = requests.post(url, auth=self.auth, data=data)
            
            response.raise_for_status()
            response_data = response.json()
            
            return {
                'success': True,
                'message_id': response_data.get('id'),
                'message': response_data.get('message', 'Queued. Thank you.'),
                'to_emails': to_email,
                'subject': subject,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send email via Mailgun: {str(e)}")
            error_detail = ""
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json().get('message', str(e))
                except:
                    error_detail = str(e)
            
            return {
                'success': False,
                'error': error_detail or str(e),
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
                        text_content: str = None,
                        template: str = None) -> Dict[str, Any]:
        """
        Send emails to multiple recipients with personalization
        
        Args:
            recipients: List of recipient dicts with 'email' and optional personalization data
            subject: Email subject line (can include variables like %recipient.name%)
            html_content: HTML email content (can include variables)
            text_content: Plain text email content (can include variables)
            template: Template name for template-based emails
            
        Returns:
            Dict with summary of sent emails
        """
        try:
            # Prepare recipient variables for batch sending
            recipient_variables = {}
            to_emails = []
            
            for recipient in recipients:
                email = recipient.get('email')
                if email:
                    to_emails.append(email)
                    # Store personalization data for each recipient
                    recipient_variables[email] = {
                        'name': recipient.get('name', ''),
                        'company': recipient.get('company', ''),
                        **recipient.get('variables', {})
                    }
            
            if not to_emails:
                return {
                    'success': False,
                    'error': 'No valid email addresses provided',
                    'total_sent': 0
                }
            
            # Build email data for batch sending
            data = {
                'from': f"{self.default_from_name} <{self.default_from_email}>",
                'to': to_emails,
                'subject': subject,
                'recipient-variables': json.dumps(recipient_variables),
                'o:tracking': 'yes',
                'o:tracking-clicks': 'yes',
                'o:tracking-opens': 'yes'
            }
            
            if template:
                data['template'] = template
            else:
                if html_content:
                    data['html'] = html_content
                if text_content:
                    data['text'] = text_content
            
            # Send batch email
            url = f"{self.base_url}/{self.domain}/messages"
            response = requests.post(url, auth=self.auth, data=data)
            response.raise_for_status()
            
            response_data = response.json()
            
            return {
                'success': True,
                'message_id': response_data.get('id'),
                'message': response_data.get('message', 'Queued. Thank you.'),
                'total_sent': len(to_emails),
                'recipients': to_emails,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send bulk emails: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'total_sent': 0,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def validate_email(self, email: str) -> Dict[str, Any]:
        """
        Validate an email address using Mailgun's validation API
        
        Args:
            email: Email address to validate
            
        Returns:
            Dict with validation results
        """
        try:
            url = f"{self.base_url.replace('/v3', '')}/v4/address/validate"
            response = requests.get(
                url,
                auth=self.auth,
                params={'address': email}
            )
            response.raise_for_status()
            
            validation_data = response.json()
            
            return {
                'success': True,
                'email': email,
                'is_valid': validation_data.get('is_valid', False),
                'is_disposable': validation_data.get('is_disposable_address', False),
                'is_role_based': validation_data.get('is_role_address', False),
                'reason': validation_data.get('reason', []),
                'risk': validation_data.get('risk', 'unknown'),
                'result': validation_data.get('result', 'unknown'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to validate email {email}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'email': email,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_email_stats(self, 
                       start_date: datetime = None, 
                       end_date: datetime = None,
                       event_type: str = None) -> Dict[str, Any]:
        """
        Get email delivery statistics
        
        Args:
            start_date: Start date for stats (defaults to 30 days ago)
            end_date: End date for stats (defaults to now)
            event_type: Filter by event type (accepted, delivered, failed, opened, clicked, etc.)
            
        Returns:
            Dict with email statistics
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            url = f"{self.base_url}/{self.domain}/stats/total"
            params = {
                'start': start_date.strftime('%a, %d %b %Y %H:%M:%S %z') or start_date.isoformat(),
                'end': end_date.strftime('%a, %d %b %Y %H:%M:%S %z') or end_date.isoformat()
            }
            
            if event_type:
                params['event'] = event_type
            
            response = requests.get(url, auth=self.auth, params=params)
            response.raise_for_status()
            
            stats_data = response.json()
            
            # Process stats
            stats = stats_data.get('stats', [])
            if stats:
                # Aggregate the stats
                aggregated = {
                    'accepted': 0,
                    'delivered': 0,
                    'failed': 0,
                    'opened': 0,
                    'clicked': 0,
                    'unsubscribed': 0,
                    'complained': 0
                }
                
                for stat_period in stats:
                    for key in aggregated.keys():
                        aggregated[key] += stat_period.get(key, {}).get('total', 0)
                
                # Calculate rates
                delivered = aggregated['delivered']
                if delivered > 0:
                    open_rate = (aggregated['opened'] / delivered) * 100
                    click_rate = (aggregated['clicked'] / delivered) * 100
                else:
                    open_rate = click_rate = 0
                
                return {
                    'success': True,
                    'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                    'totals': aggregated,
                    'rates': {
                        'delivery_rate': round((delivered / max(aggregated['accepted'], 1)) * 100, 2),
                        'open_rate': round(open_rate, 2),
                        'click_rate': round(click_rate, 2),
                        'unsubscribe_rate': round((aggregated['unsubscribed'] / max(delivered, 1)) * 100, 2),
                        'complaint_rate': round((aggregated['complained'] / max(delivered, 1)) * 100, 2)
                    },
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'success': True,
                    'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                    'totals': {},
                    'message': 'No data available for the specified period',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Failed to get email stats: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def create_mailing_list(self, 
                          list_address: str, 
                          list_name: str = None,
                          description: str = None,
                          access_level: str = "readonly") -> Dict[str, Any]:
        """
        Create a mailing list
        
        Args:
            list_address: Mailing list address (e.g., newsletter@yourdomain.com)
            list_name: Display name for the list
            description: List description
            access_level: Access level ("readonly", "members", "everyone")
            
        Returns:
            Dict with list creation response
        """
        try:
            url = f"{self.base_url}/lists"
            data = {
                'address': list_address,
                'access_level': access_level
            }
            
            if list_name:
                data['name'] = list_name
            if description:
                data['description'] = description
            
            response = requests.post(url, auth=self.auth, data=data)
            response.raise_for_status()
            
            list_data = response.json()
            
            return {
                'success': True,
                'list_address': list_data.get('list', {}).get('address'),
                'list_name': list_data.get('list', {}).get('name'),
                'members_count': list_data.get('list', {}).get('members_count', 0),
                'message': list_data.get('message'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create mailing list {list_address}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'list_address': list_address,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def add_to_mailing_list(self, 
                           list_address: str, 
                           member_email: str,
                           member_name: str = None,
                           variables: Dict[str, Any] = None,
                           subscribed: bool = True) -> Dict[str, Any]:
        """
        Add a member to a mailing list
        
        Args:
            list_address: Mailing list address
            member_email: Member's email address
            member_name: Member's name
            variables: Additional member variables
            subscribed: Whether the member is subscribed
            
        Returns:
            Dict with operation result
        """
        try:
            url = f"{self.base_url}/lists/{list_address}/members"
            data = {
                'address': member_email,
                'subscribed': 'yes' if subscribed else 'no'
            }
            
            if member_name:
                data['name'] = member_name
            if variables:
                data['vars'] = json.dumps(variables)
            
            response = requests.post(url, auth=self.auth, data=data)
            response.raise_for_status()
            
            member_data = response.json()
            
            return {
                'success': True,
                'list_address': list_address,
                'member_email': member_email,
                'member_name': member_name,
                'subscribed': subscribed,
                'message': member_data.get('message'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to add {member_email} to list {list_address}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'list_address': list_address,
                'member_email': member_email,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_events(self, 
                  begin: datetime = None,
                  end: datetime = None,
                  event_type: str = None,
                  limit: int = 100) -> Dict[str, Any]:
        """
        Get email events (opens, clicks, bounces, etc.)
        
        Args:
            begin: Start time for events
            end: End time for events  
            event_type: Filter by event type
            limit: Maximum number of events to return
            
        Returns:
            Dict with event data
        """
        try:
            url = f"{self.base_url}/{self.domain}/events"
            params = {'limit': limit}
            
            if begin:
                params['begin'] = begin.strftime('%a, %d %b %Y %H:%M:%S %z') or begin.isoformat()
            if end:
                params['end'] = end.strftime('%a, %d %b %Y %H:%M:%S %z') or end.isoformat()
            if event_type:
                params['event'] = event_type
            
            response = requests.get(url, auth=self.auth, params=params)
            response.raise_for_status()
            
            events_data = response.json()
            
            return {
                'success': True,
                'events': events_data.get('items', []),
                'total_events': len(events_data.get('items', [])),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get events: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the Mailgun API connection
        
        Returns:
            Dict with connection test results
        """
        try:
            # Test by getting domain info
            url = f"{self.base_url}/domains/{self.domain}"
            response = requests.get(url, auth=self.auth)
            
            if response.status_code == 200:
                domain_data = response.json()
                domain_info = domain_data.get('domain', {})
                
                return {
                    'success': True,
                    'connection_status': 'connected',
                    'domain': self.domain,
                    'domain_state': domain_info.get('state', 'unknown'),
                    'domain_type': domain_info.get('type', 'unknown'),
                    'smtp_login': domain_info.get('smtp_login'),
                    'api_access': True,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'success': False,
                    'connection_status': 'failed',
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'api_access': False,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Mailgun connection test failed: {str(e)}")
            return {
                'success': False,
                'connection_status': 'failed',
                'error': str(e),
                'api_access': False,
                'timestamp': datetime.utcnow().isoformat()
            }


# Email template helpers for Mailgun
class MailgunEmailTemplates:
    """Pre-built email templates for common use cases"""
    
    @staticmethod
    def welcome_email(name: str, company_name: str = "SIX3 Agency") -> Dict[str, str]:
        """Generate welcome email content"""
        return {
            'subject': f"Welcome to {company_name}, %recipient.name%!",
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
                            <li>📋 <strong>Setup consultation</strong> - We'll schedule a call to understand your needs</li>
                            <li>🔧 <strong>Custom configuration</strong> - We'll tailor our AI agents to your workflow</li>
                            <li>📚 <strong>Training & documentation</strong> - Complete guides and video tutorials</li>
                            <li>🎯 <strong>Go live!</strong> - Start automating your business processes</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://calendly.com/six3agency/setup-consultation" 
                           style="background: #2c5aa0; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                            Schedule Your Setup Call
                        </a>
                    </div>
                    
                    <p>Questions? Just reply to this email - we're here to help!</p>
                    
                    <p>Best regards,<br>
                    The {company_name} Team<br>
                    <a href="mailto:hello@six3.agency">hello@six3.agency</a></p>
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
            
            Schedule your setup call: https://calendly.com/six3agency/setup-consultation
            
            Questions? Just reply to this email - we're here to help!
            
            Best regards,
            The {company_name} Team
            hello@six3.agency
            """
        }
    
    @staticmethod
    def lead_follow_up(opportunity_type: str = "AI automation") -> Dict[str, str]:
        """Generate lead follow-up email content"""
        return {
            'subject': f"Following up on your %recipient.company% {opportunity_type} inquiry",
            'html_content': f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
                <div style="padding: 20px;">
                    <h2 style="color: #2c5aa0;">Thanks for your interest in {opportunity_type}!</h2>
                    
                    <p>Hi %recipient.name%,</p>
                    
                    <p>Thanks for reaching out about {opportunity_type} for %recipient.company%. I wanted to follow up personally to see how we can help.</p>
                    
                    <div style="background: #f0f8ff; padding: 20px; border-left: 4px solid #2c5aa0; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Here's what we can do for you:</h3>
                        <ul>
                            <li>🤖 <strong>AI Call Center:</strong> Automated lead screening and qualification</li>
                            <li>📧 <strong>Email Automation:</strong> Personalized campaigns that convert</li>
                            <li>📱 <strong>Social Media AI:</strong> Automated posting and engagement</li>
                            <li>📊 <strong>Lead Scoring:</strong> Identify your best prospects automatically</li>
                            <li>🔗 <strong>CRM Integration:</strong> Seamless workflow automation</li>
                        </ul>
                    </div>
                    
                    <p><strong>Would you like to see this in action?</strong></p>
                    <p>I can show you a personalized demo based on %recipient.company%'s specific needs. It only takes 15 minutes.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://calendly.com/six3agency/demo?company=%recipient.company%" 
                           style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                            Book Your Demo
                        </a>
                    </div>
                    
                    <p>Or if you have any questions, just reply to this email.</p>
                    
                    <p>Best regards,<br>
                    SIX3 Agency Team<br>
                    <a href="tel:+1234567890">+1 (234) 567-890</a> | <a href="mailto:hello@six3.agency">hello@six3.agency</a></p>
                </div>
            </body>
            </html>
            """,
            'text_content': f"""
            Thanks for your interest in {opportunity_type}!
            
            Hi %recipient.name%,
            
            Thanks for reaching out about {opportunity_type} for %recipient.company%. I wanted to follow up personally to see how we can help.
            
            Here's what we can do for you:
            - AI Call Center: Automated lead screening and qualification
            - Email Automation: Personalized campaigns that convert  
            - Social Media AI: Automated posting and engagement
            - Lead Scoring: Identify your best prospects automatically
            - CRM Integration: Seamless workflow automation
            
            Would you like to see this in action?
            I can show you a personalized demo based on %recipient.company%'s specific needs. It only takes 15 minutes.
            
            Book your demo: https://calendly.com/six3agency/demo?company=%recipient.company%
            
            Or if you have any questions, just reply to this email.
            
            Best regards,
            SIX3 Agency Team
            +1 (234) 567-890 | hello@six3.agency
            """
        }
    
    @staticmethod 
    def appointment_reminder(appointment_time: str, meeting_link: str) -> Dict[str, str]:
        """Generate appointment reminder email"""
        return {
            'subject': "Reminder: Your SIX3 Agency consultation is tomorrow at %recipient.appointment_time%",
            'html_content': f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
                <div style="padding: 20px;">
                    <div style="text-align: center; background: #2c5aa0; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h2 style="margin: 0;">⏰ Meeting Reminder</h2>
                        <p style="margin: 10px 0 0 0; font-size: 18px;">Tomorrow at %recipient.appointment_time%</p>
                    </div>
                    
                    <p>Hi %recipient.name%,</p>
                    
                    <p>Just a friendly reminder that we have our consultation call scheduled for:</p>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                        <h3 style="margin: 0; color: #2c5aa0;">📅 %recipient.appointment_time%</h3>
                        <p style="margin: 10px 0;"><strong>Duration:</strong> 30 minutes</p>
                        <p style="margin: 10px 0;"><strong>Topic:</strong> AI Automation Strategy for %recipient.company%</p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="%recipient.meeting_link%" 
                           style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                            Join Meeting
                        </a>
                    </div>
                    
                    <div style="background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 20px 0;">
                        <h4 style="margin: 0 0 10px 0;">📋 What to prepare:</h4>
                        <ul style="margin: 0; padding-left: 20px;">
                            <li>Current workflow challenges you'd like to automate</li>
                            <li>Your lead generation and follow-up process</li>
                            <li>Any specific questions about AI automation</li>
                        </ul>
                    </div>
                    
                    <p>Need to reschedule? No problem - just reply to this email.</p>
                    
                    <p>Looking forward to speaking with you!</p>
                    
                    <p>Best regards,<br>
                    SIX3 Agency Team</p>
                </div>
            </body>
            </html>
            """,
            'text_content': f"""
            Meeting Reminder - Tomorrow at %recipient.appointment_time%
            
            Hi %recipient.name%,
            
            Just a friendly reminder that we have our consultation call scheduled for:
            
            📅 %recipient.appointment_time%
            Duration: 30 minutes  
            Topic: AI Automation Strategy for %recipient.company%
            
            Join meeting: %recipient.meeting_link%
            
            What to prepare:
            - Current workflow challenges you'd like to automate
            - Your lead generation and follow-up process  
            - Any specific questions about AI automation
            
            Need to reschedule? No problem - just reply to this email.
            
            Looking forward to speaking with you!
            
            Best regards,
            SIX3 Agency Team
            """
        }


# Usage example
if __name__ == "__main__":
    # Example usage (requires MAILGUN_API_KEY and MAILGUN_DOMAIN environment variables)
    import os
    
    if os.getenv('MAILGUN_API_KEY') and os.getenv('MAILGUN_DOMAIN'):
        mg = MailgunIntegration()
        
        # Test connection
        test_result = mg.test_connection()
        print("Connection test:", test_result)
        
        # Send welcome email
        if test_result.get('success'):
            welcome_template = MailgunEmailTemplates.welcome_email("John Doe")
            result = mg.send_email(
                to_email="test@example.com",
                subject=welcome_template['subject'],
                html_content=welcome_template['html_content'],
                text_content=welcome_template['text_content'],
                variables={'name': 'John Doe', 'company': 'Test Corp'}
            )
            print("Email send result:", result)
    else:
        print("Set MAILGUN_API_KEY and MAILGUN_DOMAIN environment variables to test integration")