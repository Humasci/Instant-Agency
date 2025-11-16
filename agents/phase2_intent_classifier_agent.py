"""
Phase 2 - Intent Classification Agent

Classifies user messages into predefined intent categories using zero-shot classification.

Models used:
- facebook/bart-large-mnli (zero-shot classification)
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from base_agent import BaseAgent
from typing import Dict, Any, List
import requests
from datetime import datetime
from loguru import logger


class Phase2IntentClassifierAgent(BaseAgent):
    """
    Phase 2 Intent Classification Agent

    Classifies user messages/emails into intent categories:
    - pricing: Interested in cost/pricing information
    - demo: Wants a product demo or trial
    - support: Needs technical help or customer support
    - meeting: Wants to schedule a call/meeting
    - integration: Questions about integrations
    - general_inquiry: General questions about the product
    - complaint: Has an issue or complaint
    - feedback: Providing feedback or suggestions

    Uses BART zero-shot classification for high accuracy.
    """

    def __init__(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            'classifier/intent_config.yaml'
        )

        if not os.path.exists(os.path.dirname(config_path)):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

        if not os.path.exists(config_path):
            self._create_default_config(config_path)

        super().__init__(config_path)

        # Hugging Face configuration
        self.hf_api_url = "https://api-inference.huggingface.co/models"
        self.hf_api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.model = "facebook/bart-large-mnli"

        # Define intent categories
        self.intent_categories = [
            "pricing and cost information",
            "product demo or trial request",
            "technical support or help",
            "schedule meeting or call",
            "integration questions",
            "general product inquiry",
            "complaint or issue",
            "feedback or suggestion"
        ]

        # Map labels to intent codes
        self.label_to_intent = {
            "pricing and cost information": "pricing",
            "product demo or trial request": "demo",
            "technical support or help": "support",
            "schedule meeting or call": "meeting",
            "integration questions": "integration",
            "general product inquiry": "general_inquiry",
            "complaint or issue": "complaint",
            "feedback or suggestion": "feedback"
        }

    def _create_default_config(self, config_path: str):
        """Create default configuration"""
        config = {
            'agent': {
                'name': 'Intent Classification Agent',
                'version': '2.0',
                'department': 'operations',
                'description': 'Classifies user intent using zero-shot classification'
            },
            'model': {
                'provider': 'huggingface',
                'model_name': 'facebook/bart-large-mnli',
                'temperature': 0.1,
                'max_tokens': 50
            },
            'memory': {
                'type': 'redis',
                'ttl': 1800
            },
            'monitoring': {
                'log_level': 'INFO',
                'track_metrics': ['classification_time', 'confidence_score', 'intents_classified']
            }
        }

        with open(config_path, 'w') as f:
            import yaml
            yaml.dump(config, f)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify intent of user message

        Args:
            input_data: Dict with keys:
                - message: The user message to classify
                - user_id: (optional) User identifier
                - context: (optional) Additional context

        Returns:
            Dict with classification results
        """
        start_time = datetime.now()

        try:
            message = input_data.get('message', '').strip()
            user_id = input_data.get('user_id', 'unknown')

            if not message:
                return {'error': 'message is required', 'success': False}

            logger.info(f"Classifying intent for message from {user_id}")

            # Check cache
            cache_key = f"intent:{message[:100].lower().replace(' ', '_')}"
            cached_result = self.cache_get(cache_key)
            if cached_result:
                logger.info(f"Returning cached classification")
                return cached_result

            # Classify using BART zero-shot
            classification = self._classify_intent(message)

            if not classification['success']:
                # Fallback to keyword-based classification
                classification = self._fallback_classification(message)

            # Get top intent
            top_intent = classification['intents'][0]
            intent_code = self.label_to_intent.get(top_intent['label'], 'general_inquiry')

            # Determine recommended action
            recommended_action = self._get_recommended_action(intent_code, top_intent['score'])

            # Compile result
            result = {
                'success': True,
                'message': message,
                'primary_intent': intent_code,
                'intent_label': top_intent['label'],
                'confidence': top_intent['score'],
                'all_intents': classification['intents'],
                'recommended_action': recommended_action,
                'requires_human': top_intent['score'] < 0.7 or intent_code in ['complaint', 'support'],
                'timestamp': datetime.now().isoformat(),
                'agent_version': self.version
            }

            # Cache result
            self.cache_set(cache_key, result, ttl=1800)  # 30 minutes

            # Log interaction
            self.log_interaction(input_data, result, {
                'intent': intent_code,
                'confidence': top_intent['score']
            })

            # Track metrics
            classification_time = (datetime.now() - start_time).total_seconds()
            self.track_metric('classification_time', classification_time)
            self.track_metric('confidence_score', top_intent['score'])
            self.track_metric('intents_classified', 1)

            logger.info(f"Intent classified: {intent_code} ({top_intent['score']:.2f})")

            return result

        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return {'error': str(e), 'success': False}

    def _classify_intent(self, message: str) -> Dict[str, Any]:
        """Classify intent using BART zero-shot classification"""

        try:
            url = f"{self.hf_api_url}/{self.model}"
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}

            payload = {
                "inputs": message,
                "parameters": {
                    "candidate_labels": self.intent_categories,
                    "multi_label": False
                }
            }

            logger.debug(f"Calling HF API: {self.model}")

            response = requests.post(url, headers=headers, json=payload, timeout=15)

            if response.status_code == 200:
                result = response.json()

                # BART returns: {"sequence": "...", "labels": [...], "scores": [...]}
                labels = result.get('labels', [])
                scores = result.get('scores', [])

                intents = [
                    {'label': label, 'score': score}
                    for label, score in zip(labels, scores)
                ]

                return {
                    'success': True,
                    'intents': intents
                }

            logger.warning(f"HF API error: {response.status_code}")
            return {'success': False}

        except Exception as e:
            logger.error(f"BART classification failed: {e}")
            return {'success': False}

    def _fallback_classification(self, message: str) -> Dict[str, Any]:
        """Fallback keyword-based intent classification"""

        message_lower = message.lower()

        # Define keyword patterns for each intent
        intent_keywords = {
            "pricing and cost information": [
                'price', 'cost', 'pricing', 'how much', 'expensive', 'cheap',
                'plan', 'subscription', 'fee', 'payment', 'budget'
            ],
            "product demo or trial request": [
                'demo', 'trial', 'test', 'try', 'preview', 'show me',
                'see how', 'demonstration', 'sample'
            ],
            "technical support or help": [
                'help', 'issue', 'problem', 'not working', 'broken', 'error',
                'bug', 'support', 'technical', 'troubleshoot'
            ],
            "schedule meeting or call": [
                'meeting', 'call', 'schedule', 'book', 'appointment',
                'talk', 'discuss', 'available', 'calendar'
            ],
            "integration questions": [
                'integrate', 'integration', 'connect', 'api', 'plugin',
                'compatible', 'work with', 'sync'
            ],
            "complaint or issue": [
                'complaint', 'unhappy', 'disappointed', 'frustrated',
                'terrible', 'worst', 'refund', 'cancel'
            ],
            "feedback or suggestion": [
                'feedback', 'suggest', 'recommendation', 'feature request',
                'would be great', 'you should', 'improvement'
            ],
            "general product inquiry": [
                'what is', 'how does', 'tell me', 'information',
                'learn more', 'about', 'features'
            ]
        }

        # Calculate scores for each intent
        intent_scores = []
        for intent_label, keywords in intent_keywords.items():
            matches = sum(1 for kw in keywords if kw in message_lower)
            score = min(1.0, matches / 3)  # Normalize to 0-1
            intent_scores.append({'label': intent_label, 'score': score})

        # Sort by score
        intent_scores.sort(key=lambda x: x['score'], reverse=True)

        # Ensure we have at least some confidence
        if intent_scores[0]['score'] == 0:
            intent_scores[0]['score'] = 0.5  # Default medium confidence

        return {
            'success': True,
            'intents': intent_scores,
            'fallback': True
        }

    def _get_recommended_action(self, intent_code: str, confidence: float) -> Dict[str, Any]:
        """Get recommended action based on intent"""

        actions = {
            'pricing': {
                'action': 'send_pricing_info',
                'agent': 'sales_agent',
                'priority': 'high',
                'response_template': 'pricing_email',
                'escalate_if_confidence_below': 0.8
            },
            'demo': {
                'action': 'schedule_demo',
                'agent': 'sales_agent',
                'priority': 'high',
                'response_template': 'demo_booking',
                'escalate_if_confidence_below': 0.75
            },
            'support': {
                'action': 'create_support_ticket',
                'agent': 'support_agent',
                'priority': 'medium',
                'response_template': 'support_acknowledgment',
                'escalate_if_confidence_below': 0.6
            },
            'meeting': {
                'action': 'send_calendar_link',
                'agent': 'sales_agent',
                'priority': 'high',
                'response_template': 'meeting_scheduler',
                'escalate_if_confidence_below': 0.8
            },
            'integration': {
                'action': 'send_integration_docs',
                'agent': 'technical_agent',
                'priority': 'medium',
                'response_template': 'integration_guide',
                'escalate_if_confidence_below': 0.7
            },
            'complaint': {
                'action': 'escalate_to_manager',
                'agent': 'human_manager',
                'priority': 'critical',
                'response_template': 'complaint_acknowledgment',
                'escalate_if_confidence_below': 1.0  # Always escalate
            },
            'feedback': {
                'action': 'log_feedback',
                'agent': 'product_team',
                'priority': 'low',
                'response_template': 'feedback_thanks',
                'escalate_if_confidence_below': 0.6
            },
            'general_inquiry': {
                'action': 'send_general_info',
                'agent': 'faq_chatbot',
                'priority': 'medium',
                'response_template': 'general_response',
                'escalate_if_confidence_below': 0.7
            }
        }

        action_config = actions.get(intent_code, actions['general_inquiry'])

        # Determine if escalation needed
        needs_escalation = confidence < action_config['escalate_if_confidence_below']

        return {
            **action_config,
            'needs_escalation': needs_escalation,
            'confidence': confidence
        }


if __name__ == "__main__":
    """Test the Intent Classification Agent"""

    agent = Phase2IntentClassifierAgent()

    test_cases = [
        "How much does your platform cost? We're a small team with limited budget.",
        "Can I schedule a demo for next week? I'd love to see how it works.",
        "I'm having trouble integrating with Salesforce. Can you help?",
        "Your service is terrible! I want a refund immediately.",
        "I think you should add a feature for bulk email imports.",
        "What is Instant Agency and what does it do?",
        "I need to talk to someone about a custom enterprise plan.",
        "The system keeps logging me out. This is frustrating!",
    ]

    print("=" * 80)
    print("PHASE 2 - INTENT CLASSIFICATION AGENT TEST")
    print("=" * 80)

    for i, message in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"Test {i}")
        print(f"Message: \"{message}\"")
        print(f"{'─'*80}")

        result = agent.process({'message': message})

        if result.get('success'):
            print(f"\n🎯 Primary Intent: {result['primary_intent'].upper()}")
            print(f"📊 Confidence: {result['confidence']:.2%}")
            print(f"🤖 Recommended Action: {result['recommended_action']['action']}")
            print(f"👤 Assign to: {result['recommended_action']['agent']}")
            print(f"⚡ Priority: {result['recommended_action']['priority']}")

            if result['requires_human']:
                print(f"⚠️  REQUIRES HUMAN ATTENTION")

            if result['recommended_action']['needs_escalation']:
                print(f"🚨 ESCALATION RECOMMENDED (low confidence)")

            # Show top 3 intents
            print(f"\n📋 All detected intents:")
            for intent in result['all_intents'][:3]:
                intent_code = agent.label_to_intent.get(intent['label'], 'unknown')
                print(f"   - {intent_code}: {intent['score']:.2%}")

        else:
            print(f"❌ Error: {result.get('error')}")

    print(f"\n{'='*80}")
    print("Testing complete!")
    print("=" * 80)
