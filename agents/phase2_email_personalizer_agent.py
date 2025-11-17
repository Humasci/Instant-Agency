"""
Phase 2 - Email Personalization Agent

Generates personalized email responses based on user intent and context.
Works in conjunction with Intent Classification Agent.

Models used:
- EleutherAI/gpt-neo-2.7B or mistralai/Mistral-7B-v0.1
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from base_agent import BaseAgent
from typing import Dict, Any, Optional
import requests
from datetime import datetime
from loguru import logger


class Phase2EmailPersonalizerAgent(BaseAgent):
    """
    Phase 2 Email Personalization Agent

    Generates personalized email responses based on:
    - Detected intent (from Intent Classification Agent)
    - User context (name, company, history)
    - Email type (response, follow-up, nurture)

    Creates contextually appropriate, personalized emails.
    """

    def __init__(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            'email/personalizer_config.yaml'
        )

        if not os.path.exists(os.path.dirname(config_path)):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

        if not os.path.exists(config_path):
            self._create_default_config(config_path)

        super().__init__(config_path)

        # Hugging Face configuration
        self.hf_api_url = "https://api-inference.huggingface.co/models"
        self.hf_api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.model = "EleutherAI/gpt-neo-2.7B"

        # Email templates for different intents
        self.email_templates = self._load_email_templates()

    def _create_default_config(self, config_path: str):
        """Create default configuration"""
        config = {
            'agent': {
                'name': 'Email Personalization Agent',
                'version': '2.0',
                'department': 'marketing',
                'description': 'Generates personalized email responses'
            },
            'model': {
                'provider': 'huggingface',
                'model_name': 'EleutherAI/gpt-neo-2.7B',
                'temperature': 0.7,
                'max_tokens': 400
            },
            'memory': {
                'type': 'conversation',
                'ttl': 3600
            },
            'monitoring': {
                'log_level': 'INFO',
                'track_metrics': ['generation_time', 'personalization_score', 'emails_generated']
            }
        }

        with open(config_path, 'w') as f:
            import yaml
            yaml.dump(config, f)

    def _load_email_templates(self) -> Dict[str, Dict[str, str]]:
        """Load email templates for different intents"""

        return {
            'pricing': {
                'subject_template': 'Instant Agency pricing for {company}',
                'tone': 'professional, helpful',
                'key_points': ['pricing tiers', 'ROI', 'flexible plans', 'free trial']
            },
            'demo': {
                'subject_template': 'Let\'s schedule your Instant Agency demo',
                'tone': 'enthusiastic, accommodating',
                'key_points': ['calendar link', 'what to expect', 'preparation', 'duration']
            },
            'support': {
                'subject_template': 'Re: Your support request',
                'tone': 'empathetic, solution-focused',
                'key_points': ['acknowledgment', 'next steps', 'timeline', 'resources']
            },
            'meeting': {
                'subject_template': 'Scheduling our call',
                'tone': 'professional, efficient',
                'key_points': ['availability', 'agenda', 'dial-in details', 'preparation']
            },
            'integration': {
                'subject_template': 'Integration guidance for {company}',
                'tone': 'technical, clear',
                'key_points': ['documentation', 'API access', 'support channels', 'examples']
            },
            'general_inquiry': {
                'subject_template': 'Re: Your question about Instant Agency',
                'tone': 'friendly, informative',
                'key_points': ['answer', 'additional resources', 'next steps', 'availability']
            },
            'follow_up': {
                'subject_template': 'Following up on our conversation',
                'tone': 'casual professional, persistent but not pushy',
                'key_points': ['recap', 'value reminder', 'easy next step', 'timeline']
            }
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized email

        Args:
            input_data: Dict with keys:
                - recipient_name: Recipient's name
                - recipient_email: Recipient's email
                - company: Recipient's company
                - intent: Detected intent (from Intent Classifier)
                - original_message: (optional) Original message from user
                - context: (optional) Additional context
                - email_type: 'response', 'follow_up', 'nurture'

        Returns:
            Dict with generated email
        """
        start_time = datetime.now()

        try:
            # Validate inputs
            required_fields = ['recipient_name', 'recipient_email', 'intent']
            for field in required_fields:
                if field not in input_data:
                    return {'error': f'Missing required field: {field}', 'success': False}

            recipient_name = input_data['recipient_name']
            recipient_email = input_data['recipient_email']
            company = input_data.get('company', '')
            intent = input_data['intent']
            original_message = input_data.get('original_message', '')
            context = input_data.get('context', {})
            email_type = input_data.get('email_type', 'response')

            logger.info(f"Generating {email_type} email for {recipient_name} (intent: {intent})")

            # Check cache
            cache_key = f"email:{recipient_email}:{intent}:{email_type}"
            cached_result = self.cache_get(cache_key)
            if cached_result:
                logger.info(f"Returning cached email for {recipient_email}")
                return cached_result

            # Build prompt
            prompt = self._build_email_prompt(
                recipient_name=recipient_name,
                company=company,
                intent=intent,
                original_message=original_message,
                context=context,
                email_type=email_type
            )

            # Generate email
            generated = self._generate_email(prompt)

            if not generated['success']:
                # Fallback to template
                generated = self._template_based_email(input_data)

            # Parse email components
            parsed = self._parse_email(generated['text'])

            # Add personalization touches
            personalized = self._add_personalization(parsed, input_data)

            # Calculate personalization score
            personalization_score = self._calculate_personalization_score(personalized, input_data)

            # Compile result
            result = {
                'success': True,
                'recipient_info': {
                    'name': recipient_name,
                    'email': recipient_email,
                    'company': company
                },
                'email_subject': personalized['subject'],
                'email_body': personalized['body'],
                'email_type': email_type,
                'intent': intent,
                'personalization_score': personalization_score,
                'recommended_send_time': self._get_optimal_send_time(context),
                'follow_up_days': self._get_follow_up_timing(intent),
                'timestamp': datetime.now().isoformat(),
                'agent_version': self.version
            }

            # Cache result
            self.cache_set(cache_key, result, ttl=3600)

            # Log interaction
            self.log_interaction(input_data, result, {
                'intent': intent,
                'personalization_score': personalization_score
            })

            # Track metrics
            generation_time = (datetime.now() - start_time).total_seconds()
            self.track_metric('generation_time', generation_time)
            self.track_metric('personalization_score', personalization_score)
            self.track_metric('emails_generated', 1)

            logger.info(f"Email generated: intent={intent}, personalization={personalization_score:.2f}")

            return result

        except Exception as e:
            logger.error(f"Email generation failed: {e}")
            return {'error': str(e), 'success': False}

    def _build_email_prompt(
        self,
        recipient_name: str,
        company: str,
        intent: str,
        original_message: str,
        context: Dict[str, Any],
        email_type: str
    ) -> str:
        """Build prompt for email generation"""

        template_config = self.email_templates.get(intent, self.email_templates['general_inquiry'])

        prompt = f"""You are a professional email writer for Instant Agency.

Write a personalized {email_type} email with the following details:

Recipient: {recipient_name}
Company: {company}
Intent: {intent}
Email Type: {email_type}
Tone: {template_config['tone']}

"""

        if original_message:
            prompt += f"They wrote: \"{original_message}\"\n\n"

        prompt += f"""Key points to address:
"""
        for point in template_config['key_points']:
            prompt += f"- {point}\n"

        prompt += f"""
Requirements:
1. Personalized subject line referencing {company if company else recipient_name}
2. Warm, professional greeting using their name
3. Acknowledge their specific situation/request
4. Provide clear, helpful information
5. Include a specific call-to-action
6. Professional signature
7. Length: 150-200 words
8. Tone: {template_config['tone']}

Output format:
Subject: [subject]

Body:
[email body]

Write the complete email now:
"""

        return prompt

    def _generate_email(self, prompt: str) -> Dict[str, Any]:
        """Generate email using Hugging Face API"""

        try:
            url = f"{self.hf_api_url}/{self.model}"
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}

            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 400,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "do_sample": True,
                    "return_full_text": False
                }
            }

            response = requests.post(url, headers=headers, json=payload, timeout=20)

            if response.status_code == 200:
                result = response.json()

                if isinstance(result, list) and len(result) > 0:
                    return {
                        'success': True,
                        'text': result[0].get('generated_text', '')
                    }

            return {'success': False}

        except Exception as e:
            logger.error(f"Email generation failed: {e}")
            return {'success': False}

    def _template_based_email(self, input_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate email using templates (fallback)"""

        intent = input_data['intent']
        name = input_data['recipient_name']
        company = input_data.get('company', 'your company')

        templates = {
            'pricing': f"""Subject: Instant Agency Pricing for {company}

Body:
Hi {name},

Thanks for your interest in Instant Agency's pricing!

We offer flexible plans starting at $499/month for our Starter plan, which includes 2 AI agents and basic automation. Our Professional plan at $1,499/month includes 7 agents and advanced features.

I'd love to understand your specific needs and find the perfect fit. Would you be open to a quick 15-minute call this week to discuss?

Best regards,
Instant Agency Team""",

            'demo': f"""Subject: Let's schedule your Instant Agency demo

Body:
Hi {name},

Great to hear you'd like to see Instant Agency in action!

I can walk you through our platform and show you how companies like {company} use AI agents to automate their sales and marketing processes.

Here's my calendar link to book a time that works for you: [calendar link]

The demo typically takes 20-30 minutes, and I'll customize it to your specific use case.

Looking forward to it!

Best,
Instant Agency Team""",

            'support': f"""Subject: Re: Your support request

Body:
Hi {name},

Thank you for reaching out! I'm sorry you're experiencing issues.

I've escalated your request to our technical team and they'll get back to you within 2 hours with a solution. In the meantime, here are some resources that might help: [link to docs]

We're committed to getting this resolved quickly for you.

Best regards,
Instant Agency Support"""
        }

        default_template = f"""Subject: Re: Your inquiry

Body:
Hi {name},

Thank you for reaching out to Instant Agency!

I've received your message and want to make sure I address your question properly. Could you provide a bit more detail about what you're looking to accomplish?

I'm here to help and want to make sure I give you the most relevant information.

Best regards,
Instant Agency Team"""

        email_text = templates.get(intent, default_template)

        return {'success': True, 'text': email_text}

    def _parse_email(self, generated_text: str) -> Dict[str, str]:
        """Parse generated email into subject and body"""

        lines = generated_text.split('\n')

        subject = ''
        body_lines = []
        in_body = False

        for line in lines:
            if 'subject:' in line.lower():
                subject = line.split(':', 1)[1].strip()
            elif 'body:' in line.lower():
                in_body = True
            elif in_body:
                body_lines.append(line)

        if not subject and lines:
            subject = lines[0].strip()
            body_lines = lines[1:]

        body = '\n'.join(body_lines).strip()

        return {
            'subject': subject.replace('Subject:', '').strip(),
            'body': body.replace('Body:', '').strip()
        }

    def _add_personalization(self, email: Dict[str, str], input_data: Dict[str, Any]) -> Dict[str, str]:
        """Add final personalization touches"""

        name = input_data['recipient_name']
        company = input_data.get('company', '')

        # Ensure greeting uses first name
        if name:
            first_name = name.split()[0]
            body = email['body']

            if not body.startswith('Hi ') and not body.startswith('Hello '):
                body = f"Hi {first_name},\n\n{body}"

            email['body'] = body

        # Add company reference to subject if not already there
        if company and company.lower() not in email['subject'].lower():
            email['subject'] = email['subject'].replace('your', company + "'s")

        return email

    def _calculate_personalization_score(self, email: Dict[str, str], input_data: Dict[str, Any]) -> float:
        """Calculate how personalized the email is (0-100)"""

        score = 0.0
        body_lower = email['body'].lower()

        # Uses recipient name (30 points)
        name = input_data['recipient_name'].lower()
        if name in body_lower:
            score += 30

        # Mentions company (25 points)
        company = input_data.get('company', '').lower()
        if company and company in body_lower:
            score += 25

        # References original message/context (20 points)
        original = input_data.get('original_message', '').lower()
        if original:
            # Check for keyword overlap
            original_words = set(original.split())
            body_words = set(body_lower.split())
            overlap = len(original_words & body_words)
            score += min(20, overlap * 2)
        else:
            score += 10  # Some credit if no original message

        # Has specific CTA (15 points)
        cta_indicators = ['calendar', 'schedule', 'book', 'link', 'click', 'reply', 'let me know']
        if any(cta in body_lower for cta in cta_indicators):
            score += 15

        # Professional length (10 points)
        word_count = len(email['body'].split())
        if 100 <= word_count <= 250:
            score += 10
        elif 80 <= word_count <= 300:
            score += 5

        return round(min(100, score), 2)

    def _get_optimal_send_time(self, context: Dict[str, Any]) -> str:
        """Get optimal time to send email based on context"""

        # Simple heuristic: Tuesday-Thursday 10 AM - 2 PM
        return "Tuesday-Thursday, 10 AM - 2 PM local time"

    def _get_follow_up_timing(self, intent: str) -> int:
        """Get recommended follow-up timing in days"""

        timing = {
            'pricing': 3,
            'demo': 2,
            'support': 1,
            'meeting': 1,
            'integration': 5,
            'general_inquiry': 7,
            'follow_up': 5
        }

        return timing.get(intent, 5)


if __name__ == "__main__":
    """Test the Email Personalization Agent"""

    agent = Phase2EmailPersonalizerAgent()

    test_cases = [
        {
            'recipient_name': 'Sarah Johnson',
            'recipient_email': 'sarah@techscale.io',
            'company': 'TechScale',
            'intent': 'pricing',
            'original_message': 'Can you send me your pricing information? We have a team of about 20 people.',
            'email_type': 'response'
        },
        {
            'recipient_name': 'Mike Chen',
            'recipient_email': 'mike@shopfast.com',
            'company': 'ShopFast',
            'intent': 'demo',
            'original_message': 'I\'d love to see a demo of your platform.',
            'email_type': 'response'
        },
        {
            'recipient_name': 'Alex Rivera',
            'recipient_email': 'alex@startup.io',
            'company': 'Startup Inc',
            'intent': 'general_inquiry',
            'email_type': 'follow_up',
            'context': {'previous_contact': '2 weeks ago'}
        }
    ]

    print("=" * 80)
    print("PHASE 2 - EMAIL PERSONALIZATION AGENT TEST")
    print("=" * 80)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"Test {i}: {test_case['email_type'].upper()} email for {test_case['intent']} intent")
        print(f"Recipient: {test_case['recipient_name']} at {test_case.get('company', 'N/A')}")
        print(f"{'─'*80}")

        result = agent.process(test_case)

        if result.get('success'):
            print(f"\n📧 SUBJECT: {result['email_subject']}")
            print(f"\n📝 BODY:\n{result['email_body']}")
            print(f"\n📊 Personalization Score: {result['personalization_score']}/100")
            print(f"⏰ Best send time: {result['recommended_send_time']}")
            print(f"📅 Follow-up in: {result['follow_up_days']} days")
        else:
            print(f"❌ Error: {result.get('error')}")

    print(f"\n{'='*80}")
    print("Testing complete!")
    print("=" * 80)
