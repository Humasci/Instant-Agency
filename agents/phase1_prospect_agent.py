"""
Phase 1 - Prospect Research Agent with Hugging Face Sentiment Analysis

This agent qualifies leads using sentiment analysis on their inquiry messages
and scores them for outreach prioritization.

Models used:
- distilbert-base-uncased-finetuned-sst-2-english (sentiment analysis)
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from base_agent import BaseAgent
from typing import Dict, Any
import json
import requests
from datetime import datetime
from loguru import logger


class Phase1ProspectAgent(BaseAgent):
    """
    Phase 1 Prospect Research Agent

    Qualifies leads using HuggingFace sentiment analysis to assess
    interest level from initial inquiry messages.
    """

    def __init__(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            'marketing/prospecting/config.yaml'
        )
        super().__init__(config_path)

        # Hugging Face API configuration
        self.hf_api_url = "https://api-inference.huggingface.co/models"
        self.hf_api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.sentiment_model = "distilbert-base-uncased-finetuned-sst-2-english"

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Qualify a lead based on their inquiry message sentiment

        Args:
            input_data: Dict with keys:
                - lead_name: Name of the lead
                - lead_email: Email address
                - company: Company name
                - lead_message: The inquiry message to analyze
                - industry: (optional) Company industry

        Returns:
            Dict with qualification results and sentiment analysis
        """
        start_time = datetime.now()

        try:
            lead_name = input_data.get('lead_name', 'Unknown')
            lead_email = input_data.get('lead_email')
            company = input_data.get('company', 'Unknown')
            lead_message = input_data.get('lead_message', '')
            industry = input_data.get('industry', 'General')

            if not lead_message:
                return {
                    'error': 'lead_message is required',
                    'success': False
                }

            logger.info(f"Processing lead qualification for {lead_name} from {company}")

            # Check cache first
            cache_key = f"lead_qualification:{lead_email}"
            cached_result = self.cache_get(cache_key)
            if cached_result:
                logger.info(f"Returning cached result for {lead_email}")
                return cached_result

            # Step 1: Sentiment Analysis via Hugging Face
            sentiment_result = self._analyze_sentiment(lead_message)

            # Step 2: Calculate qualification score
            qualification_score = self._calculate_qualification_score(
                sentiment_result,
                input_data
            )

            # Step 3: Determine qualification status
            qualification_status = self._determine_status(qualification_score)

            # Step 4: Generate next action
            next_action = self._get_next_action(qualification_status, sentiment_result)

            # Compile result
            result = {
                'success': True,
                'lead_info': {
                    'name': lead_name,
                    'email': lead_email,
                    'company': company,
                    'industry': industry
                },
                'sentiment_analysis': sentiment_result,
                'qualification_score': qualification_score,
                'qualification_status': qualification_status,
                'next_action': next_action,
                'timestamp': datetime.now().isoformat(),
                'agent_version': self.version
            }

            # Cache result
            self.cache_set(cache_key, result, ttl=3600)

            # Log to database
            self.log_interaction(input_data, result, {
                'qualification_score': qualification_score,
                'sentiment': sentiment_result.get('label')
            })

            # Track metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.track_metric('processing_time', processing_time)
            self.track_metric('qualification_score', qualification_score)
            self.track_metric('leads_processed', 1)

            if qualification_status == 'qualified':
                self.track_metric('leads_qualified', 1)

            logger.info(f"Lead {lead_name} qualification complete: {qualification_status} ({qualification_score})")

            return result

        except Exception as e:
            logger.error(f"Lead qualification failed: {e}")
            return {
                'error': str(e),
                'success': False
            }

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using Hugging Face API

        Args:
            text: Text to analyze

        Returns:
            Dict with sentiment analysis results
        """
        try:
            url = f"{self.hf_api_url}/{self.sentiment_model}"
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}

            payload = {"inputs": text}

            logger.debug(f"Calling Hugging Face API: {url}")

            response = requests.post(url, headers=headers, json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()

                # HF returns list of classification results
                # Format: [{'label': 'POSITIVE', 'score': 0.9998}]
                if isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], list):
                        # Sometimes returns nested list
                        sentiment = result[0][0]
                    else:
                        sentiment = result[0]

                    return {
                        'label': sentiment['label'],
                        'score': sentiment['score'],
                        'confidence': sentiment['score']
                    }
            else:
                logger.error(f"HF API error: {response.status_code} - {response.text}")

                # Fallback to simple keyword analysis
                return self._fallback_sentiment_analysis(text)

        except Exception as e:
            logger.warning(f"Sentiment analysis failed, using fallback: {e}")
            return self._fallback_sentiment_analysis(text)

    def _fallback_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """
        Fallback sentiment analysis using simple keyword matching
        """
        text_lower = text.lower()

        # Positive keywords
        positive_keywords = [
            'interested', 'great', 'excited', 'amazing', 'perfect',
            'looking forward', 'love', 'excellent', 'need', 'want',
            'ready', 'soon', 'urgent', 'asap', 'budget', 'buy'
        ]

        # Negative keywords
        negative_keywords = [
            'not interested', 'no thanks', 'unsubscribe', 'stop',
            'expensive', 'too much', 'cannot', "can't", 'unable'
        ]

        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        negative_count = sum(1 for kw in negative_keywords if kw in text_lower)

        if positive_count > negative_count:
            return {
                'label': 'POSITIVE',
                'score': 0.75,
                'confidence': 0.75,
                'fallback': True
            }
        elif negative_count > positive_count:
            return {
                'label': 'NEGATIVE',
                'score': 0.75,
                'confidence': 0.75,
                'fallback': True
            }
        else:
            return {
                'label': 'NEUTRAL',
                'score': 0.5,
                'confidence': 0.5,
                'fallback': True
            }

    def _calculate_qualification_score(
        self,
        sentiment_result: Dict[str, Any],
        input_data: Dict[str, Any]
    ) -> float:
        """
        Calculate overall qualification score (0-100)

        Based on:
        - Sentiment of message (40% weight)
        - Presence of buying signals (30% weight)
        - Company/industry fit (30% weight)
        """
        score = 0.0

        # 1. Sentiment score (40% weight)
        sentiment_label = sentiment_result.get('label', 'NEUTRAL')
        sentiment_confidence = sentiment_result.get('confidence', 0.5)

        if sentiment_label == 'POSITIVE':
            sentiment_score = 100 * sentiment_confidence
        elif sentiment_label == 'NEGATIVE':
            sentiment_score = 0
        else:  # NEUTRAL
            sentiment_score = 50

        score += sentiment_score * 0.4

        # 2. Buying signals (30% weight)
        message = input_data.get('lead_message', '').lower()
        buying_signals = [
            'pricing', 'cost', 'budget', 'demo', 'trial',
            'purchase', 'buy', 'contract', 'quote', 'proposal'
        ]

        signal_count = sum(1 for signal in buying_signals if signal in message)
        buying_score = min(100, signal_count * 25)  # Max 100
        score += buying_score * 0.3

        # 3. Company/industry fit (30% weight)
        # Simple scoring based on industry (can be enhanced)
        industry = input_data.get('industry', '').lower()
        target_industries = ['technology', 'saas', 'software', 'fintech', 'e-commerce']

        if any(ind in industry for ind in target_industries):
            fit_score = 100
        elif industry:
            fit_score = 70
        else:
            fit_score = 50

        score += fit_score * 0.3

        return round(score, 2)

    def _determine_status(self, qualification_score: float) -> str:
        """
        Determine qualification status based on score

        Returns: qualified, potential, or unqualified
        """
        if qualification_score >= 70:
            return 'qualified'
        elif qualification_score >= 40:
            return 'potential'
        else:
            return 'unqualified'

    def _get_next_action(
        self,
        status: str,
        sentiment_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine next action based on qualification status
        """
        if status == 'qualified':
            return {
                'action': 'send_personalized_outreach',
                'priority': 'high',
                'channel': 'email',
                'delay_minutes': 0,
                'follow_up_days': 3,
                'assign_to': 'sales_team',
                'message': 'High-quality lead - send personalized sales pitch immediately'
            }
        elif status == 'potential':
            return {
                'action': 'nurture_sequence',
                'priority': 'medium',
                'channel': 'email',
                'delay_minutes': 60,
                'follow_up_days': 7,
                'assign_to': 'marketing_automation',
                'message': 'Add to nurture sequence with educational content'
            }
        else:
            return {
                'action': 'low_priority_nurture',
                'priority': 'low',
                'channel': 'email',
                'delay_minutes': 1440,  # 24 hours
                'follow_up_days': 30,
                'assign_to': 'marketing_automation',
                'message': 'Low priority - add to general newsletter list'
            }


if __name__ == "__main__":
    """Test the Phase 1 Prospect Agent"""

    # Initialize agent
    agent = Phase1ProspectAgent()

    # Test cases
    test_cases = [
        {
            'lead_name': 'John Smith',
            'lead_email': 'john@acmecorp.com',
            'company': 'Acme Corp',
            'industry': 'Technology',
            'lead_message': 'I\'m very interested in your AI automation platform. We\'re looking to streamline our sales process and would love to see a demo. What\'s the pricing?'
        },
        {
            'lead_name': 'Jane Doe',
            'lead_email': 'jane@startup.io',
            'company': 'Startup Inc',
            'industry': 'SaaS',
            'lead_message': 'Can you tell me more about your product? We might need something like this in the future.'
        },
        {
            'lead_name': 'Bob Johnson',
            'lead_email': 'bob@example.com',
            'company': 'Example LLC',
            'industry': 'Retail',
            'lead_message': 'Not interested, please remove me from your list.'
        }
    ]

    print("=" * 70)
    print("PHASE 1 - PROSPECT RESEARCH AGENT TEST")
    print("=" * 70)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test Case {i}: {test_case['lead_name']} from {test_case['company']}")
        print(f"{'='*70}")
        print(f"Message: \"{test_case['lead_message'][:100]}...\"")
        print()

        result = agent.process(test_case)

        if result.get('success'):
            print(f"✅ Status: {result['qualification_status'].upper()}")
            print(f"📊 Score: {result['qualification_score']}/100")
            print(f"😊 Sentiment: {result['sentiment_analysis']['label']} ({result['sentiment_analysis']['confidence']:.2f})")
            print(f"🎯 Next Action: {result['next_action']['action']}")
            print(f"⚡ Priority: {result['next_action']['priority']}")
        else:
            print(f"❌ Error: {result.get('error')}")

        print()

    print("=" * 70)
    print("Testing complete!")
    print("=" * 70)
