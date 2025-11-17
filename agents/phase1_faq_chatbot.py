"""
Phase 1 - FAQ Chatbot Agent

This agent handles common customer questions using a lightweight
text generation model and knowledge base retrieval.

Models used:
- gpt2 or facebook/blenderbot-400M-distill (text generation)
- sentence-transformers/all-MiniLM-L6-v2 (embeddings for KB search)
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import json
import requests
from datetime import datetime
from loguru import logger


class Phase1FAQChatbot(BaseAgent):
    """
    Phase 1 FAQ Chatbot Agent

    Answers common questions using:
    1. Knowledge base search (semantic similarity)
    2. GPT-2 generation for conversational responses
    3. Escalation to human when confidence is low
    """

    def __init__(self):
        # Create a minimal config for this agent
        config_path = os.path.join(
            os.path.dirname(__file__),
            'support/faq_config.yaml'
        )

        # Create config if it doesn't exist
        if not os.path.exists(os.path.dirname(config_path)):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

        if not os.path.exists(config_path):
            self._create_default_config(config_path)

        super().__init__(config_path)

        # Hugging Face API configuration
        self.hf_api_url = "https://api-inference.huggingface.co/models"
        self.hf_api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.generation_model = "gpt2"  # Or "facebook/blenderbot-400M-distill"

        # Load knowledge base
        self.knowledge_base = self._load_knowledge_base()

        # Escalation threshold
        self.confidence_threshold = 0.7

    def _create_default_config(self, config_path: str):
        """Create a default configuration file"""
        config = {
            'agent': {
                'name': 'FAQ Chatbot Agent',
                'version': '1.0',
                'description': 'Answers common customer questions'
            },
            'model': {
                'provider': 'huggingface',
                'model_name': 'gpt2',
                'temperature': 0.7,
                'max_tokens': 150
            },
            'memory': {
                'type': 'conversation',
                'ttl': 3600
            },
            'monitoring': {
                'log_level': 'INFO',
                'track_metrics': ['response_time', 'confidence_score', 'escalation_rate']
            }
        }

        with open(config_path, 'w') as f:
            import yaml
            yaml.dump(config, f)

    def _load_knowledge_base(self) -> List[Dict[str, str]]:
        """
        Load FAQ knowledge base

        In production, this would be loaded from a database or file
        """
        return [
            {
                'question': 'What is Instant Agency?',
                'answer': 'Instant Agency is an AI-powered virtual agent platform that automates marketing, sales, content creation, and customer support using advanced AI agents and digital avatars.',
                'category': 'product',
                'keywords': ['what', 'instant agency', 'platform', 'about']
            },
            {
                'question': 'How much does it cost?',
                'answer': 'We offer flexible pricing starting at $499/month for the Starter plan, $1,499/month for Professional, and custom Enterprise pricing. Each plan includes different numbers of AI agents and features.',
                'category': 'pricing',
                'keywords': ['price', 'cost', 'pricing', 'how much', 'plans']
            },
            {
                'question': 'What AI models do you use?',
                'answer': 'We use state-of-the-art open-source models from Hugging Face, including Mistral-7B for conversations, DistilBERT for classification, and custom fine-tuned models for specific tasks.',
                'category': 'technical',
                'keywords': ['models', 'ai', 'technology', 'hugging face']
            },
            {
                'question': 'Do you offer a free trial?',
                'answer': 'Yes! We offer a 14-day free trial with full access to all features. No credit card required to start.',
                'category': 'pricing',
                'keywords': ['trial', 'free', 'demo', 'test']
            },
            {
                'question': 'How do I get started?',
                'answer': 'Getting started is easy! Sign up for a free trial, connect your CRM and communication channels, and our team will help you configure your first AI agents. Most customers are up and running within 24 hours.',
                'category': 'onboarding',
                'keywords': ['start', 'setup', 'getting started', 'begin', 'onboarding']
            },
            {
                'question': 'Can I integrate with my existing tools?',
                'answer': 'Absolutely! We integrate with popular CRMs (Salesforce, HubSpot, SuiteCRM), email platforms (Gmail, Outlook), and communication tools (Slack, Microsoft Teams). We also offer a REST API for custom integrations.',
                'category': 'integrations',
                'keywords': ['integrate', 'integration', 'crm', 'tools', 'api']
            },
            {
                'question': 'Is my data secure?',
                'answer': 'Security is our top priority. All data is encrypted at rest and in transit, we\'re SOC 2 compliant, and we offer self-hosted deployment options for maximum control. We never train our models on your data.',
                'category': 'security',
                'keywords': ['security', 'data', 'privacy', 'secure', 'encryption']
            },
            {
                'question': 'What support do you provide?',
                'answer': 'All plans include email support with 24-hour response time. Professional and Enterprise plans include priority support, phone support, and a dedicated success manager.',
                'category': 'support',
                'keywords': ['support', 'help', 'customer service', 'contact']
            }
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a customer question

        Args:
            input_data: Dict with keys:
                - question: The customer's question
                - user_id: (optional) User identifier
                - context: (optional) Additional context

        Returns:
            Dict with answer and metadata
        """
        start_time = datetime.now()

        try:
            question = input_data.get('question', '').strip()
            user_id = input_data.get('user_id', 'anonymous')
            context = input_data.get('context', '')

            if not question:
                return {
                    'error': 'question is required',
                    'success': False
                }

            logger.info(f"Processing FAQ question from user {user_id}")

            # Step 1: Search knowledge base
            kb_match = self._search_knowledge_base(question)

            # Step 2: Determine if we have a good match
            if kb_match and kb_match['confidence'] >= self.confidence_threshold:
                # We have a good KB match - use it
                answer = kb_match['answer']
                confidence = kb_match['confidence']
                source = 'knowledge_base'
                escalate = False

                logger.info(f"KB match found with confidence {confidence:.2f}")

            else:
                # No good KB match - generate response with LLM
                logger.info("No KB match, generating response with LLM")

                generated_response = self._generate_answer(question, context, kb_match)

                answer = generated_response['answer']
                confidence = generated_response['confidence']
                source = 'generated'

                # Escalate if confidence is low
                escalate = confidence < self.confidence_threshold

            # Compile result
            result = {
                'success': True,
                'question': question,
                'answer': answer,
                'confidence': confidence,
                'source': source,
                'escalate_to_human': escalate,
                'kb_match': kb_match,
                'timestamp': datetime.now().isoformat(),
                'agent_version': self.version
            }

            # Log interaction
            self.log_interaction(input_data, result, {
                'confidence': confidence,
                'source': source,
                'escalated': escalate
            })

            # Track metrics
            response_time = (datetime.now() - start_time).total_seconds()
            self.track_metric('response_time', response_time)
            self.track_metric('confidence_score', confidence)

            if escalate:
                self.track_metric('escalation_rate', 1)

            logger.info(f"FAQ response generated: {source}, confidence={confidence:.2f}, escalate={escalate}")

            return result

        except Exception as e:
            logger.error(f"FAQ processing failed: {e}")
            return {
                'error': str(e),
                'success': False
            }

    def _search_knowledge_base(self, question: str) -> Optional[Dict[str, Any]]:
        """
        Search knowledge base for matching FAQ

        Uses simple keyword matching (in production, use semantic search with embeddings)
        """
        question_lower = question.lower()

        best_match = None
        best_score = 0.0

        for faq in self.knowledge_base:
            # Calculate match score based on keyword overlap
            keywords = faq['keywords']
            matches = sum(1 for kw in keywords if kw in question_lower)

            # Also check if question words appear in FAQ question
            question_words = set(question_lower.split())
            faq_words = set(faq['question'].lower().split())
            word_overlap = len(question_words & faq_words)

            score = (matches * 0.6) + (word_overlap * 0.4)

            if score > best_score:
                best_score = score
                best_match = faq

        if best_match:
            # Normalize score to 0-1
            confidence = min(1.0, best_score / 5.0)

            return {
                'question': best_match['question'],
                'answer': best_match['answer'],
                'category': best_match['category'],
                'confidence': confidence
            }

        return None

    def _generate_answer(
        self,
        question: str,
        context: str = '',
        kb_match: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate answer using Hugging Face LLM

        Args:
            question: User's question
            context: Additional context
            kb_match: Best KB match (if any) for reference

        Returns:
            Dict with generated answer and confidence
        """
        try:
            # Build prompt
            prompt = self._build_prompt(question, context, kb_match)

            # Call Hugging Face API
            url = f"{self.hf_api_url}/{self.generation_model}"
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}

            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 150,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "do_sample": True
                }
            }

            logger.debug(f"Calling HF API for generation: {url}")

            response = requests.post(url, headers=headers, json=payload, timeout=15)

            if response.status_code == 200:
                result = response.json()

                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')

                    # Extract just the answer part (after the prompt)
                    answer = generated_text.replace(prompt, '').strip()

                    # Clean up the answer
                    answer = self._clean_generated_answer(answer)

                    # Estimate confidence based on length and coherence
                    confidence = self._estimate_confidence(answer, question)

                    return {
                        'answer': answer,
                        'confidence': confidence
                    }

            # Fallback
            logger.warning(f"Generation API failed: {response.status_code}")
            return self._fallback_answer(question, kb_match)

        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return self._fallback_answer(question, kb_match)

    def _build_prompt(
        self,
        question: str,
        context: str,
        kb_match: Optional[Dict]
    ) -> str:
        """Build prompt for LLM generation"""

        prompt = f"""You are a helpful customer support agent for Instant Agency, an AI automation platform.

Customer question: {question}
"""

        if context:
            prompt += f"\nContext: {context}\n"

        if kb_match:
            prompt += f"\nRelated FAQ: {kb_match['answer']}\n"

        prompt += "\nProvide a helpful, concise answer:\n"

        return prompt

    def _clean_generated_answer(self, answer: str) -> str:
        """Clean up generated answer"""

        # Remove extra whitespace
        answer = ' '.join(answer.split())

        # Truncate if too long
        if len(answer) > 500:
            answer = answer[:497] + '...'

        # Ensure it ends with punctuation
        if answer and answer[-1] not in '.!?':
            answer += '.'

        return answer

    def _estimate_confidence(self, answer: str, question: str) -> float:
        """
        Estimate confidence in generated answer

        Simple heuristic based on:
        - Answer length
        - Presence of key question words in answer
        """
        confidence = 0.5  # Base confidence

        # Longer answers (up to a point) are better
        length_score = min(1.0, len(answer.split()) / 50)
        confidence += length_score * 0.2

        # Check if question keywords appear in answer
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())
        word_overlap = len(question_words & answer_words)

        overlap_score = min(1.0, word_overlap / max(1, len(question_words)))
        confidence += overlap_score * 0.3

        return min(1.0, confidence)

    def _fallback_answer(
        self,
        question: str,
        kb_match: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Provide fallback answer when generation fails
        """
        if kb_match:
            # Use KB match even if confidence was low
            return {
                'answer': kb_match['answer'],
                'confidence': 0.5
            }
        else:
            # Generic fallback
            return {
                'answer': "I'm not sure about that. Let me connect you with a human team member who can help. They'll get back to you within 24 hours.",
                'confidence': 0.3
            }


if __name__ == "__main__":
    """Test the Phase 1 FAQ Chatbot"""

    # Initialize agent
    agent = Phase1FAQChatbot()

    # Test cases
    test_cases = [
        {'question': 'What is Instant Agency and how does it work?'},
        {'question': 'How much do your plans cost?'},
        {'question': 'Can I try it before buying?'},
        {'question': 'Do you integrate with Salesforce?'},
        {'question': 'How do I configure my first agent?'},  # Not in KB
        {'question': 'Can you help me with quantum physics?'},  # Completely off-topic
    ]

    print("=" * 70)
    print("PHASE 1 - FAQ CHATBOT AGENT TEST")
    print("=" * 70)
    print()

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Question {i}: {test_case['question']}")
        print(f"{'='*70}")

        result = agent.process(test_case)

        if result.get('success'):
            print(f"\n📝 Answer: {result['answer']}")
            print(f"\n📊 Confidence: {result['confidence']:.2f}")
            print(f"🔍 Source: {result['source']}")

            if result.get('kb_match'):
                print(f"📚 KB Match: {result['kb_match']['question']} ({result['kb_match']['confidence']:.2f})")

            if result['escalate_to_human']:
                print(f"⚠️  ESCALATE TO HUMAN (low confidence)")
            else:
                print(f"✅ Answered by AI")
        else:
            print(f"❌ Error: {result.get('error')}")

    print("\n" + "=" * 70)
    print("Testing complete!")
    print("=" * 70)
