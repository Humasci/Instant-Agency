"""
Human Escalation System for SIX3 Agency

Handles:
- Automatic detection of escalation triggers
- Real-time notifications to human agents
- Queue management for escalated cases
- Context preservation during handoff
- Performance tracking and analytics
- Integration with multiple notification channels

Notification Channels:
- Slack alerts
- Email notifications
- SMS alerts (Twilio)
- Dashboard alerts
- Webhook notifications
"""

import os
import sys
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import asyncio
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: Redis not available. Install with: pip install redis")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests not available. Install with: pip install requests")

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("Warning: Twilio not available. Install with: pip install twilio")


logger = logging.getLogger(__name__)


class EscalationPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EscalationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class NotificationChannel(Enum):
    SLACK = "slack"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"


@dataclass
class EscalationCase:
    """Data class for escalation cases"""
    id: str
    agent_name: str
    customer_id: str
    customer_name: str
    customer_email: str
    priority: EscalationPriority
    status: EscalationStatus
    trigger_reason: str
    context: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    created_at: datetime
    assigned_human: Optional[str] = None
    escalated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    satisfaction_score: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with JSON-serializable values"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['escalated_at'] = self.escalated_at.isoformat() if self.escalated_at else None
        data['resolved_at'] = self.resolved_at.isoformat() if self.resolved_at else None
        # Convert enums to strings
        data['priority'] = self.priority.value if self.priority else None
        data['status'] = self.status.value if self.status else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EscalationCase':
        """Create from dictionary"""
        # Convert ISO strings back to datetime objects
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        if data.get('escalated_at'):
            data['escalated_at'] = datetime.fromisoformat(data['escalated_at'].replace('Z', '+00:00'))
        if data.get('resolved_at'):
            data['resolved_at'] = datetime.fromisoformat(data['resolved_at'].replace('Z', '+00:00'))
        
        # Convert strings to enums
        if data.get('priority'):
            data['priority'] = EscalationPriority(data['priority'])
        if data.get('status'):
            data['status'] = EscalationStatus(data['status'])
        
        return cls(**data)


class HumanEscalationSystem:
    """Human escalation system for AI agents"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the human escalation system
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Initialize Redis for real-time queue management
        if REDIS_AVAILABLE:
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', '6379'))
            redis_db = int(os.getenv('REDIS_DB', '0'))
            
            try:
                self.redis_client = redis.Redis(
                    host=redis_host, 
                    port=redis_port, 
                    db=redis_db,
                    decode_responses=True
                )
                self.redis_client.ping()  # Test connection
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                self.redis_client = None
        else:
            self.redis_client = None
        
        # Notification configuration
        self.notification_config = {
            'slack_webhook': os.getenv('SLACK_WEBHOOK_URL'),
            'email_api': os.getenv('SENDGRID_API_KEY'),
            'twilio_sid': os.getenv('TWILIO_ACCOUNT_SID'),
            'twilio_token': os.getenv('TWILIO_AUTH_TOKEN'),
            'twilio_from': os.getenv('TWILIO_FROM_NUMBER')
        }
        
        # Escalation triggers configuration
        self.escalation_triggers = {
            'sentiment_threshold': -0.7,  # Very negative sentiment
            'confidence_threshold': 0.3,   # Low AI confidence
            'conversation_length': 10,      # Too many back-and-forth messages
            'keywords': ['manager', 'supervisor', 'cancel', 'refund', 'complaint', 'angry'],
            'response_time': 300,           # 5 minutes without response
            'error_count': 3,               # 3 consecutive AI errors
            'customer_value': 10000,        # High-value customers ($10k+)
            'escalation_requests': ['human', 'agent', 'representative', 'person']
        }
        
        # Response time SLAs by priority
        self.sla_targets = {
            EscalationPriority.CRITICAL: timedelta(minutes=5),
            EscalationPriority.HIGH: timedelta(minutes=15),
            EscalationPriority.MEDIUM: timedelta(hours=1),
            EscalationPriority.LOW: timedelta(hours=4)
        }
        
        # Queue keys for Redis
        self.queue_keys = {
            EscalationPriority.CRITICAL: 'escalation:queue:critical',
            EscalationPriority.HIGH: 'escalation:queue:high',
            EscalationPriority.MEDIUM: 'escalation:queue:medium',
            EscalationPriority.LOW: 'escalation:queue:low'
        }
        
        logger.info("Human Escalation System initialized")
    
    def should_escalate(self, 
                       agent_response: Dict[str, Any],
                       conversation_context: Dict[str, Any],
                       customer_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Determine if a conversation should be escalated to a human
        
        Args:
            agent_response: The AI agent's response data
            conversation_context: Current conversation context
            customer_data: Customer information
            
        Returns:
            Dict with escalation decision and reasoning
        """
        try:
            escalation_reasons = []
            escalation_score = 0
            priority = EscalationPriority.LOW
            
            # Check sentiment threshold
            sentiment_score = agent_response.get('sentiment', {}).get('score', 0)
            if sentiment_score < self.escalation_triggers['sentiment_threshold']:
                escalation_reasons.append(f"Negative sentiment detected: {sentiment_score}")
                escalation_score += 30
                priority = max(priority, EscalationPriority.HIGH, key=lambda x: x.value)
            
            # Check AI confidence
            confidence = agent_response.get('confidence', 1.0)
            if confidence < self.escalation_triggers['confidence_threshold']:
                escalation_reasons.append(f"Low AI confidence: {confidence}")
                escalation_score += 25
                priority = max(priority, EscalationPriority.MEDIUM, key=lambda x: x.value)
            
            # Check conversation length
            conversation_length = len(conversation_context.get('messages', []))
            if conversation_length >= self.escalation_triggers['conversation_length']:
                escalation_reasons.append(f"Long conversation: {conversation_length} messages")
                escalation_score += 20
                priority = max(priority, EscalationPriority.MEDIUM, key=lambda x: x.value)
            
            # Check for escalation keywords
            message_text = conversation_context.get('latest_message', '').lower()
            found_keywords = [kw for kw in self.escalation_triggers['keywords'] if kw in message_text]
            if found_keywords:
                escalation_reasons.append(f"Escalation keywords found: {found_keywords}")
                escalation_score += 35
                priority = max(priority, EscalationPriority.HIGH, key=lambda x: x.value)
            
            # Check for direct escalation requests
            escalation_requests = [req for req in self.escalation_triggers['escalation_requests'] if req in message_text]
            if escalation_requests:
                escalation_reasons.append(f"Direct escalation request: {escalation_requests}")
                escalation_score += 40
                priority = EscalationPriority.HIGH
            
            # Check customer value
            if customer_data:
                customer_value = customer_data.get('lifetime_value', 0)
                if customer_value >= self.escalation_triggers['customer_value']:
                    escalation_reasons.append(f"High-value customer: ${customer_value}")
                    escalation_score += 15
                    # Boost priority for high-value customers
                    if priority == EscalationPriority.LOW:
                        priority = EscalationPriority.MEDIUM
            
            # Check error count
            error_count = conversation_context.get('consecutive_errors', 0)
            if error_count >= self.escalation_triggers['error_count']:
                escalation_reasons.append(f"Multiple AI errors: {error_count}")
                escalation_score += 30
                priority = max(priority, EscalationPriority.HIGH, key=lambda x: x.value)
            
            # Determine if escalation is needed
            should_escalate = escalation_score >= 50 or len(escalation_reasons) >= 2
            
            # Override for critical situations
            if any(keyword in message_text for keyword in ['emergency', 'urgent', 'critical', 'legal']):
                should_escalate = True
                priority = EscalationPriority.CRITICAL
                escalation_reasons.append("Critical situation keywords detected")
            
            return {
                'should_escalate': should_escalate,
                'escalation_score': escalation_score,
                'priority': priority,
                'reasons': escalation_reasons,
                'estimated_sla': self.sla_targets[priority].total_seconds() / 60,  # minutes
                'recommended_channels': self._get_notification_channels(priority),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in escalation check: {str(e)}")
            return {
                'should_escalate': True,  # Fail-safe: escalate on error
                'escalation_score': 100,
                'priority': EscalationPriority.HIGH,
                'reasons': [f"Escalation system error: {str(e)}"],
                'error': True
            }
    
    def create_escalation_case(self,
                              agent_name: str,
                              customer_id: str,
                              customer_name: str,
                              customer_email: str,
                              trigger_reason: str,
                              priority: EscalationPriority,
                              context: Dict[str, Any],
                              conversation_history: List[Dict[str, Any]]) -> EscalationCase:
        """
        Create a new escalation case
        
        Args:
            agent_name: Name of the AI agent
            customer_id: Customer identifier
            customer_name: Customer name
            customer_email: Customer email
            trigger_reason: Reason for escalation
            priority: Escalation priority
            context: Additional context data
            conversation_history: Full conversation history
            
        Returns:
            EscalationCase object
        """
        case_id = str(uuid.uuid4())
        
        escalation_case = EscalationCase(
            id=case_id,
            agent_name=agent_name,
            customer_id=customer_id,
            customer_name=customer_name,
            customer_email=customer_email,
            priority=priority,
            status=EscalationStatus.PENDING,
            trigger_reason=trigger_reason,
            context=context,
            conversation_history=conversation_history,
            created_at=datetime.utcnow()
        )
        
        # Store in Redis queue
        if self.redis_client:
            try:
                queue_key = self.queue_keys[priority]
                self.redis_client.lpush(queue_key, json.dumps(escalation_case.to_dict()))
                
                # Store case details with expiration (30 days)
                case_key = f"escalation:case:{case_id}"
                self.redis_client.setex(
                    case_key, 
                    timedelta(days=30), 
                    json.dumps(escalation_case.to_dict())
                )
                
                # Update statistics
                self.redis_client.incr(f"escalation:stats:total")
                self.redis_client.incr(f"escalation:stats:priority:{priority.value}")
                
            except Exception as e:
                logger.error(f"Failed to store escalation case in Redis: {e}")
        
        logger.info(f"Created escalation case {case_id} with priority {priority.value}")
        return escalation_case
    
    def send_notifications(self, 
                          escalation_case: EscalationCase,
                          channels: List[NotificationChannel] = None) -> Dict[str, Any]:
        """
        Send notifications about the escalation case
        
        Args:
            escalation_case: The escalation case
            channels: List of notification channels to use
            
        Returns:
            Dict with notification results
        """
        if channels is None:
            channels = self._get_notification_channels(escalation_case.priority)
        
        notification_results = {}
        
        for channel in channels:
            try:
                if channel == NotificationChannel.SLACK:
                    result = self._send_slack_notification(escalation_case)
                elif channel == NotificationChannel.EMAIL:
                    result = self._send_email_notification(escalation_case)
                elif channel == NotificationChannel.SMS:
                    result = self._send_sms_notification(escalation_case)
                elif channel == NotificationChannel.WEBHOOK:
                    result = self._send_webhook_notification(escalation_case)
                elif channel == NotificationChannel.DASHBOARD:
                    result = self._send_dashboard_notification(escalation_case)
                else:
                    result = {'success': False, 'error': f'Unknown channel: {channel}'}
                
                notification_results[channel.value] = result
                
            except Exception as e:
                logger.error(f"Failed to send {channel.value} notification: {e}")
                notification_results[channel.value] = {
                    'success': False,
                    'error': str(e)
                }
        
        return notification_results
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current escalation queue status
        
        Returns:
            Dict with queue statistics
        """
        if not self.redis_client:
            return {'error': 'Redis not available'}
        
        try:
            queue_status = {}
            total_pending = 0
            
            for priority in EscalationPriority:
                queue_key = self.queue_keys[priority]
                count = self.redis_client.llen(queue_key)
                queue_status[priority.value] = count
                total_pending += count
            
            # Get statistics
            total_cases = self.redis_client.get("escalation:stats:total") or 0
            
            # Calculate average response times
            avg_response_times = {}
            for priority in EscalationPriority:
                avg_key = f"escalation:stats:avg_response:{priority.value}"
                avg_time = self.redis_client.get(avg_key) or 0
                avg_response_times[priority.value] = float(avg_time)
            
            return {
                'queue_counts': queue_status,
                'total_pending': total_pending,
                'total_cases': int(total_cases),
                'average_response_times': avg_response_times,
                'sla_targets': {p.value: int(self.sla_targets[p].total_seconds() / 60) for p in EscalationPriority},
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get queue status: {e}")
            return {'error': str(e)}
    
    def assign_case(self, case_id: str, human_agent_id: str) -> Dict[str, Any]:
        """
        Assign an escalation case to a human agent
        
        Args:
            case_id: Case ID
            human_agent_id: Human agent identifier
            
        Returns:
            Dict with assignment result
        """
        if not self.redis_client:
            return {'success': False, 'error': 'Redis not available'}
        
        try:
            case_key = f"escalation:case:{case_id}"
            case_data = self.redis_client.get(case_key)
            
            if not case_data:
                return {'success': False, 'error': 'Case not found'}
            
            case_dict = json.loads(case_data)
            escalation_case = EscalationCase.from_dict(case_dict)
            
            # Update case
            escalation_case.assigned_human = human_agent_id
            escalation_case.status = EscalationStatus.IN_PROGRESS
            escalation_case.escalated_at = datetime.utcnow()
            
            # Save updated case
            self.redis_client.setex(
                case_key,
                timedelta(days=30),
                json.dumps(escalation_case.to_dict())
            )
            
            # Remove from queue
            queue_key = self.queue_keys[escalation_case.priority]
            self._remove_from_queue(queue_key, case_id)
            
            # Track assignment metrics
            self.redis_client.incr(f"escalation:stats:assigned")
            
            logger.info(f"Assigned case {case_id} to human agent {human_agent_id}")
            
            return {
                'success': True,
                'case_id': case_id,
                'assigned_to': human_agent_id,
                'status': escalation_case.status.value,
                'escalated_at': escalation_case.escalated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to assign case {case_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def resolve_case(self, 
                    case_id: str, 
                    resolution_notes: str,
                    satisfaction_score: Optional[int] = None) -> Dict[str, Any]:
        """
        Mark an escalation case as resolved
        
        Args:
            case_id: Case ID
            resolution_notes: Notes about the resolution
            satisfaction_score: Customer satisfaction score (1-5)
            
        Returns:
            Dict with resolution result
        """
        if not self.redis_client:
            return {'success': False, 'error': 'Redis not available'}
        
        try:
            case_key = f"escalation:case:{case_id}"
            case_data = self.redis_client.get(case_key)
            
            if not case_data:
                return {'success': False, 'error': 'Case not found'}
            
            case_dict = json.loads(case_data)
            escalation_case = EscalationCase.from_dict(case_dict)
            
            # Update case
            escalation_case.status = EscalationStatus.RESOLVED
            escalation_case.resolved_at = datetime.utcnow()
            escalation_case.resolution_notes = resolution_notes
            escalation_case.satisfaction_score = satisfaction_score
            
            # Calculate response time
            if escalation_case.escalated_at:
                response_time = escalation_case.resolved_at - escalation_case.escalated_at
                response_minutes = response_time.total_seconds() / 60
                
                # Update average response time
                avg_key = f"escalation:stats:avg_response:{escalation_case.priority.value}"
                current_avg = float(self.redis_client.get(avg_key) or 0)
                resolved_count = int(self.redis_client.get("escalation:stats:resolved") or 0) + 1
                new_avg = (current_avg * (resolved_count - 1) + response_minutes) / resolved_count
                self.redis_client.set(avg_key, new_avg)
            
            # Save updated case
            self.redis_client.setex(
                case_key,
                timedelta(days=30),
                json.dumps(escalation_case.to_dict())
            )
            
            # Track resolution metrics
            self.redis_client.incr("escalation:stats:resolved")
            if satisfaction_score:
                self.redis_client.incr(f"escalation:stats:satisfaction:{satisfaction_score}")
            
            logger.info(f"Resolved case {case_id}")
            
            return {
                'success': True,
                'case_id': case_id,
                'status': escalation_case.status.value,
                'resolved_at': escalation_case.resolved_at.isoformat(),
                'resolution_notes': resolution_notes,
                'satisfaction_score': satisfaction_score
            }
            
        except Exception as e:
            logger.error(f"Failed to resolve case {case_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_next_case(self, human_agent_id: str) -> Optional[EscalationCase]:
        """
        Get the next case from the queue for a human agent
        
        Args:
            human_agent_id: Human agent identifier
            
        Returns:
            Next escalation case or None
        """
        if not self.redis_client:
            return None
        
        try:
            # Check queues by priority (critical first)
            for priority in [EscalationPriority.CRITICAL, EscalationPriority.HIGH, 
                           EscalationPriority.MEDIUM, EscalationPriority.LOW]:
                queue_key = self.queue_keys[priority]
                case_data = self.redis_client.rpop(queue_key)
                
                if case_data:
                    case_dict = json.loads(case_data)
                    escalation_case = EscalationCase.from_dict(case_dict)
                    
                    # Auto-assign to requesting agent
                    self.assign_case(escalation_case.id, human_agent_id)
                    
                    return escalation_case
            
            return None  # No cases in queue
            
        except Exception as e:
            logger.error(f"Failed to get next case for {human_agent_id}: {e}")
            return None
    
    # Helper methods
    
    def _get_notification_channels(self, priority: EscalationPriority) -> List[NotificationChannel]:
        """Get appropriate notification channels for priority level"""
        if priority == EscalationPriority.CRITICAL:
            return [NotificationChannel.SLACK, NotificationChannel.EMAIL, NotificationChannel.SMS]
        elif priority == EscalationPriority.HIGH:
            return [NotificationChannel.SLACK, NotificationChannel.EMAIL]
        elif priority == EscalationPriority.MEDIUM:
            return [NotificationChannel.SLACK]
        else:
            return [NotificationChannel.DASHBOARD]
    
    def _send_slack_notification(self, case: EscalationCase) -> Dict[str, Any]:
        """Send Slack notification"""
        if not self.notification_config['slack_webhook'] or not REQUESTS_AVAILABLE:
            return {'success': False, 'error': 'Slack webhook not configured or requests unavailable'}
        
        try:
            priority_emoji = {
                EscalationPriority.CRITICAL: "🚨",
                EscalationPriority.HIGH: "⚠️",
                EscalationPriority.MEDIUM: "⚡",
                EscalationPriority.LOW: "📝"
            }
            
            message = {
                "text": f"{priority_emoji[case.priority]} Escalation Alert - {case.priority.value.upper()}",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{priority_emoji[case.priority]} Customer Escalation - {case.priority.value.upper()}"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Customer:* {case.customer_name}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Case ID:* {case.id}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Agent:* {case.agent_name}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Priority:* {case.priority.value}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Reason:* {case.trigger_reason}"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Take Case"
                                },
                                "value": case.id,
                                "url": f"https://dashboard.six3.agency/escalations/{case.id}"
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                self.notification_config['slack_webhook'],
                json=message,
                timeout=10
            )
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response': response.text if response.status_code != 200 else None
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _send_email_notification(self, case: EscalationCase) -> Dict[str, Any]:
        """Send email notification"""
        # This would integrate with the SendGrid integration we created earlier
        from integrations.email.sendgrid_integration import SendGridIntegration
        
        try:
            sg = SendGridIntegration()
            
            subject = f"🚨 Customer Escalation - {case.priority.value.upper()} - {case.customer_name}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #d93025;">Customer Escalation Alert</h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Case ID:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{case.id}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Customer:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{case.customer_name}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Email:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{case.customer_email}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Priority:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{case.priority.value}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Agent:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{case.agent_name}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Reason:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{case.trigger_reason}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Created:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{case.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</td></tr>
                </table>
                <p><a href="https://dashboard.six3.agency/escalations/{case.id}" style="background: #1a73e8; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">View Case</a></p>
            </body>
            </html>
            """
            
            # Send to configured support email
            support_email = os.getenv('SUPPORT_EMAIL', 'support@six3.agency')
            
            result = sg.send_email(
                to_email=support_email,
                subject=subject,
                html_content=html_content
            )
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _send_sms_notification(self, case: EscalationCase) -> Dict[str, Any]:
        """Send SMS notification"""
        if not TWILIO_AVAILABLE or not self.notification_config['twilio_sid']:
            return {'success': False, 'error': 'Twilio not configured'}
        
        try:
            client = TwilioClient(
                self.notification_config['twilio_sid'],
                self.notification_config['twilio_token']
            )
            
            message_body = f"🚨 SIX3 Agency Escalation\n\nCustomer: {case.customer_name}\nPriority: {case.priority.value.upper()}\nReason: {case.trigger_reason}\n\nCase ID: {case.id}\nView: https://dashboard.six3.agency/escalations/{case.id}"
            
            # Send to configured support phone
            support_phone = os.getenv('SUPPORT_PHONE')
            if not support_phone:
                return {'success': False, 'error': 'Support phone not configured'}
            
            message = client.messages.create(
                body=message_body,
                from_=self.notification_config['twilio_from'],
                to=support_phone
            )
            
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _send_webhook_notification(self, case: EscalationCase) -> Dict[str, Any]:
        """Send webhook notification"""
        webhook_url = os.getenv('ESCALATION_WEBHOOK_URL')
        if not webhook_url or not REQUESTS_AVAILABLE:
            return {'success': False, 'error': 'Webhook URL not configured'}
        
        try:
            payload = {
                'event': 'escalation_created',
                'case': case.to_dict(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response': response.text if response.status_code != 200 else None
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _send_dashboard_notification(self, case: EscalationCase) -> Dict[str, Any]:
        """Send dashboard notification (store in Redis for real-time display)"""
        if not self.redis_client:
            return {'success': False, 'error': 'Redis not available'}
        
        try:
            # Store notification for dashboard
            notification = {
                'id': str(uuid.uuid4()),
                'type': 'escalation',
                'case_id': case.id,
                'customer_name': case.customer_name,
                'priority': case.priority.value,
                'trigger_reason': case.trigger_reason,
                'created_at': case.created_at.isoformat(),
                'read': False
            }
            
            # Store in dashboard notifications list
            self.redis_client.lpush(
                'dashboard:notifications',
                json.dumps(notification)
            )
            
            # Keep only last 100 notifications
            self.redis_client.ltrim('dashboard:notifications', 0, 99)
            
            # Set notification expiry (7 days)
            self.redis_client.expire('dashboard:notifications', timedelta(days=7))
            
            return {'success': True, 'notification_id': notification['id']}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _remove_from_queue(self, queue_key: str, case_id: str) -> bool:
        """Remove a specific case from the queue"""
        if not self.redis_client:
            return False
        
        try:
            # Get all items from queue
            queue_items = self.redis_client.lrange(queue_key, 0, -1)
            
            for item in queue_items:
                case_data = json.loads(item)
                if case_data.get('id') == case_id:
                    # Remove this specific item
                    self.redis_client.lrem(queue_key, 1, item)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove case {case_id} from queue {queue_key}: {e}")
            return False
    
    def get_case_details(self, case_id: str) -> Optional[EscalationCase]:
        """Get detailed information about a case"""
        if not self.redis_client:
            return None
        
        try:
            case_key = f"escalation:case:{case_id}"
            case_data = self.redis_client.get(case_key)
            
            if case_data:
                case_dict = json.loads(case_data)
                return EscalationCase.from_dict(case_dict)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get case details for {case_id}: {e}")
            return None
    
    def get_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get escalation analytics for the specified period"""
        if not self.redis_client:
            return {'error': 'Redis not available'}
        
        try:
            # This would typically query a time-series database
            # For now, return current statistics
            
            total_cases = int(self.redis_client.get("escalation:stats:total") or 0)
            resolved_cases = int(self.redis_client.get("escalation:stats:resolved") or 0)
            
            # Calculate resolution rate
            resolution_rate = (resolved_cases / total_cases * 100) if total_cases > 0 else 0
            
            # Get priority breakdown
            priority_breakdown = {}
            for priority in EscalationPriority:
                count = int(self.redis_client.get(f"escalation:stats:priority:{priority.value}") or 0)
                priority_breakdown[priority.value] = count
            
            # Get average response times
            avg_response_times = {}
            for priority in EscalationPriority:
                avg_time = float(self.redis_client.get(f"escalation:stats:avg_response:{priority.value}") or 0)
                avg_response_times[priority.value] = avg_time
            
            # Calculate satisfaction scores
            satisfaction_scores = {}
            total_satisfaction_responses = 0
            total_satisfaction_score = 0
            
            for score in range(1, 6):
                count = int(self.redis_client.get(f"escalation:stats:satisfaction:{score}") or 0)
                satisfaction_scores[str(score)] = count
                total_satisfaction_responses += count
                total_satisfaction_score += score * count
            
            avg_satisfaction = (total_satisfaction_score / total_satisfaction_responses) if total_satisfaction_responses > 0 else 0
            
            return {
                'period_days': days,
                'total_cases': total_cases,
                'resolved_cases': resolved_cases,
                'resolution_rate': round(resolution_rate, 1),
                'priority_breakdown': priority_breakdown,
                'average_response_times': avg_response_times,
                'satisfaction_scores': satisfaction_scores,
                'average_satisfaction': round(avg_satisfaction, 2),
                'current_queue': self.get_queue_status()['queue_counts'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return {'error': str(e)}


def test_escalation_system():
    """Test the Human Escalation System"""
    print("Testing Human Escalation System...")
    
    # Initialize system
    escalation_system = HumanEscalationSystem()
    
    # Test escalation detection
    print("\n1. Testing escalation detection...")
    
    # Mock agent response and context
    agent_response = {
        'confidence': 0.2,  # Low confidence
        'sentiment': {'score': -0.8}  # Very negative
    }
    
    conversation_context = {
        'messages': [{'user': 'message'} for _ in range(12)],  # Long conversation
        'latest_message': 'I want to speak to a human representative immediately!',
        'consecutive_errors': 1
    }
    
    customer_data = {
        'lifetime_value': 15000  # High-value customer
    }
    
    escalation_check = escalation_system.should_escalate(
        agent_response, conversation_context, customer_data
    )
    
    print(f"Should escalate: {escalation_check['should_escalate']}")
    print(f"Priority: {escalation_check['priority'].value if 'priority' in escalation_check else 'N/A'}")
    print(f"Reasons: {escalation_check['reasons']}")
    
    # Test case creation
    if escalation_check['should_escalate']:
        print("\n2. Testing case creation...")
        
        escalation_case = escalation_system.create_escalation_case(
            agent_name="Customer Support Agent",
            customer_id="cust_12345",
            customer_name="John Doe",
            customer_email="john.doe@example.com",
            trigger_reason="; ".join(escalation_check['reasons']),
            priority=escalation_check['priority'],
            context=conversation_context,
            conversation_history=conversation_context['messages']
        )
        
        print(f"Created case: {escalation_case.id}")
        print(f"Priority: {escalation_case.priority.value}")
        print(f"Status: {escalation_case.status.value}")
        
        # Test notifications
        print("\n3. Testing notifications...")
        notification_results = escalation_system.send_notifications(escalation_case)
        
        for channel, result in notification_results.items():
            print(f"{channel}: {'✓' if result['success'] else '✗'} {result.get('error', '')}")
        
        # Test queue status
        print("\n4. Testing queue status...")
        queue_status = escalation_system.get_queue_status()
        if 'error' not in queue_status:
            print(f"Queue status: {queue_status['queue_counts']}")
            print(f"Total pending: {queue_status['total_pending']}")
        else:
            print(f"Queue status error: {queue_status['error']}")
        
        # Test case assignment
        print("\n5. Testing case assignment...")
        assignment_result = escalation_system.assign_case(escalation_case.id, "human_agent_001")
        print(f"Assignment success: {assignment_result['success']}")
        
        if assignment_result['success']:
            # Test case resolution
            print("\n6. Testing case resolution...")
            resolution_result = escalation_system.resolve_case(
                escalation_case.id,
                "Customer concern addressed and resolved through direct consultation.",
                satisfaction_score=4
            )
            print(f"Resolution success: {resolution_result['success']}")
        
        # Test analytics
        print("\n7. Testing analytics...")
        analytics = escalation_system.get_analytics()
        if 'error' not in analytics:
            print(f"Total cases: {analytics['total_cases']}")
            print(f"Resolution rate: {analytics['resolution_rate']}%")
        else:
            print(f"Analytics error: {analytics['error']}")
    
    print("\nHuman Escalation System testing completed!")


if __name__ == "__main__":
    test_escalation_system()