"""
Phase 2 - Sales Pitch Generation Agent

Generates personalized B2B sales email pitches using advanced LLMs.

Models used:
- mistralai/Mistral-7B-v0.1 (preferred) or EleutherAI/gpt-neo-2.7B
- Leverages prompt templates from agents/prompts/sales/pitch_generation.py
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from base_agent import BaseAgent
from typing import Dict, Any, Optional
import json
import requests
from datetime import datetime
from loguru import logger


class Phase2SalesPitchAgent(BaseAgent):
    """
    Phase 2 Sales Pitch Generation Agent

    Generates highly personalized sales email pitches based on:
    - Prospect information (name, company, industry)
    - Pain points and trigger events
    - Company size and current solutions

    Uses advanced LLMs (Mistral-7B or GPT-Neo-2.7B) for human-like writing.
    """

    def __init__(self):
        # Create minimal config
        config_path = os.path.join(
            os.path.dirname(__file__),
            'sales/pitch_config.yaml'
        )

        if not os.path.exists(os.path.dirname(config_path)):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

        if not os.path.exists(config_path):
            self._create_default_config(config_path)

        super().__init__(config_path)

        # Hugging Face API configuration
        self.hf_api_url = "https://api-inference.huggingface.co/models"
        self.hf_api_key = os.getenv('HUGGINGFACE_API_KEY')

        # Try Mistral first, fallback to GPT-Neo
        self.primary_model = "mistralai/Mistral-7B-Instruct-v0.1"
        self.fallback_model = "EleutherAI/gpt-neo-2.7B"

    def _create_default_config(self, config_path: str):
        """Create default configuration"""
        config = {
            'agent': {
                'name': 'Sales Pitch Generation Agent',
                'version': '2.0',
                'department': 'sales',
                'description': 'Generates personalized B2B sales email pitches'
            },
            'model': {
                'provider': 'huggingface',
                'model_name': 'mistralai/Mistral-7B-Instruct-v0.1',
                'temperature': 0.7,
                'max_tokens': 500
            },
            'memory': {
                'type': 'conversation',
                'ttl': 7200
            },
            'monitoring': {
                'log_level': 'INFO',
                'track_metrics': ['generation_time', 'pitch_quality_score', 'pitches_generated']
            }
        }

        with open(config_path, 'w') as f:
            import yaml
            yaml.dump(config, f)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized sales pitch

        Args:
            input_data: Dict with keys:
                - prospect_name: Name of the prospect
                - company: Company name
                - industry: Industry sector
                - pain_points: Known pain points (string or list)
                - company_size: Optional company size
                - trigger_event: Optional recent event/news
                - current_solutions: Optional current tools they use

        Returns:
            Dict with generated pitch and metadata
        """
        start_time = datetime.now()

        try:
            # Validate required fields
            required_fields = ['prospect_name', 'company', 'industry', 'pain_points']
            for field in required_fields:
                if field not in input_data:
                    return {
                        'error': f'Missing required field: {field}',
                        'success': False
                    }

            prospect_name = input_data['prospect_name']
            company = input_data['company']
            industry = input_data['industry']
            pain_points = input_data['pain_points']

            # Optional fields
            company_size = input_data.get('company_size', 'Unknown')
            trigger_event = input_data.get('trigger_event', 'Recent company growth')
            current_solutions = input_data.get('current_solutions', 'Manual processes')

            logger.info(f"Generating sales pitch for {prospect_name} at {company}")

            # Check cache
            cache_key = f"sales_pitch:{company.lower().replace(' ', '_')}:{prospect_name.lower().replace(' ', '_')}"
            cached_result = self.cache_get(cache_key)
            if cached_result:
                logger.info(f"Returning cached pitch for {prospect_name}")
                return cached_result

            # Build prompt using template
            prompt = self._build_sales_pitch_prompt(
                prospect_name=prospect_name,
                company=company,
                industry=industry,
                pain_points=pain_points,
                company_size=company_size,
                trigger_event=trigger_event,
                current_solutions=current_solutions
            )

            # Generate pitch
            pitch_result = self._generate_pitch(prompt)

            if not pitch_result['success']:
                return pitch_result

            # Parse the generated pitch
            parsed_pitch = self._parse_pitch(pitch_result['generated_text'])

            # Calculate quality score
            quality_score = self._calculate_quality_score(parsed_pitch, input_data)

            # Compile result
            result = {
                'success': True,
                'prospect_info': {
                    'name': prospect_name,
                    'company': company,
                    'industry': industry
                },
                'email_subject': parsed_pitch['subject'],
                'email_body': parsed_pitch['body'],
                'primary_cta': parsed_pitch.get('cta', 'Schedule a call'),
                'estimated_value': parsed_pitch.get('value_prop', 'Automate and scale operations'),
                'quality_score': quality_score,
                'model_used': pitch_result['model'],
                'timestamp': datetime.now().isoformat(),
                'agent_version': self.version
            }

            # Cache result
            self.cache_set(cache_key, result, ttl=7200)  # 2 hours

            # Log interaction
            self.log_interaction(input_data, result, {
                'quality_score': quality_score,
                'model': pitch_result['model']
            })

            # Track metrics
            generation_time = (datetime.now() - start_time).total_seconds()
            self.track_metric('generation_time', generation_time)
            self.track_metric('pitch_quality_score', quality_score)
            self.track_metric('pitches_generated', 1)

            logger.info(f"Sales pitch generated: quality={quality_score:.2f}, model={pitch_result['model']}")

            return result

        except Exception as e:
            logger.error(f"Sales pitch generation failed: {e}")
            return {
                'error': str(e),
                'success': False
            }

    def _build_sales_pitch_prompt(
        self,
        prospect_name: str,
        company: str,
        industry: str,
        pain_points: str,
        company_size: str,
        trigger_event: str,
        current_solutions: str
    ) -> str:
        """Build prompt for sales pitch generation"""

        # Import the template from prompts library
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), 'prompts'))
            from sales.pitch_generation import SALES_PITCH_PROMPT

            return SALES_PITCH_PROMPT.format(
                prospect_name=prospect_name,
                company=company,
                industry=industry,
                company_size=company_size,
                pain_points=pain_points,
                trigger_event=trigger_event,
                current_solutions=current_solutions
            )
        except:
            # Fallback inline prompt
            return f"""You are an expert B2B sales professional for Instant Agency, an AI-powered virtual agent platform.

Generate a personalized sales email pitch for:

Prospect: {prospect_name}
Company: {company}
Industry: {industry}
Company Size: {company_size}
Pain Points: {pain_points}
Trigger Event: {trigger_event}
Current Solutions: {current_solutions}

Requirements:
1. Personalized subject line (max 60 characters)
2. Opening that references their situation
3. Value proposition tied to their pain points
4. Specific industry example or case study
5. Soft call-to-action
6. Professional, conversational tone
7. Length: 150-200 words

Output format:
Subject: [subject line]

Body:
[email body]

CTA: [primary call to action]
Value: [brief value statement]
"""

    def _generate_pitch(self, prompt: str) -> Dict[str, Any]:
        """Generate pitch using Hugging Face API"""

        # Try primary model (Mistral-7B)
        result = self._call_hf_model(self.primary_model, prompt)

        if result['success']:
            result['model'] = 'mistral-7b'
            return result

        # Fallback to GPT-Neo
        logger.warning(f"Primary model failed, trying fallback: {self.fallback_model}")
        result = self._call_hf_model(self.fallback_model, prompt)

        if result['success']:
            result['model'] = 'gpt-neo-2.7b'
            return result

        # Ultimate fallback: template-based generation
        logger.warning("All models failed, using template-based generation")
        return self._template_based_pitch(prompt)

    def _call_hf_model(self, model_name: str, prompt: str) -> Dict[str, Any]:
        """Call Hugging Face model API"""

        try:
            url = f"{self.hf_api_url}/{model_name}"
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}

            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "do_sample": True,
                    "return_full_text": False
                }
            }

            logger.debug(f"Calling HF API: {model_name}")

            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()

                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')

                    return {
                        'success': True,
                        'generated_text': generated_text
                    }

            logger.warning(f"HF API error: {response.status_code} - {response.text[:200]}")
            return {'success': False, 'error': f"API error: {response.status_code}"}

        except Exception as e:
            logger.error(f"HF API call failed: {e}")
            return {'success': False, 'error': str(e)}

    def _template_based_pitch(self, prompt: str) -> Dict[str, Any]:
        """Generate pitch using simple templates (fallback)"""

        # Extract info from prompt
        lines = prompt.split('\n')
        info = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip().lower().replace(' ', '_')] = value.strip()

        company = info.get('company', 'your company')
        industry = info.get('industry', 'your industry')
        pain_points = info.get('pain_points', 'operational challenges')

        pitch = f"""Subject: Helping {company} automate {industry} operations

Body:
Hi,

I noticed {company}'s growth in the {industry} space - congratulations!

Many companies at your stage struggle with {pain_points}. We recently helped a similar-sized {industry} company automate 70% of their processes, freeing their team to focus on strategic work.

Our AI platform handles everything from lead qualification to customer support, so your team can scale without growing headcount.

Would a quick 15-minute call to discuss how this could work for {company} be valuable?

Best regards,
Instant Agency Sales Team

CTA: Schedule 15-minute discovery call
Value: Automate 70% of manual processes
"""

        return {
            'success': True,
            'generated_text': pitch,
            'model': 'template'
        }

    def _parse_pitch(self, generated_text: str) -> Dict[str, str]:
        """Parse generated pitch into components"""

        pitch = {
            'subject': '',
            'body': '',
            'cta': '',
            'value_prop': ''
        }

        # Split by sections
        sections = generated_text.split('\n\n')

        for section in sections:
            section_lower = section.lower()

            if 'subject:' in section_lower:
                pitch['subject'] = section.split(':', 1)[1].strip()
            elif 'body:' in section_lower:
                pitch['body'] = section.split(':', 1)[1].strip()
            elif 'cta:' in section_lower:
                pitch['cta'] = section.split(':', 1)[1].strip()
            elif 'value:' in section_lower:
                pitch['value_prop'] = section.split(':', 1)[1].strip()

        # If body wasn't explicitly labeled, use the main content
        if not pitch['body'] and sections:
            # Find the largest section (likely the body)
            pitch['body'] = max(sections, key=len).strip()

        # Clean up
        for key in pitch:
            # Remove common prefixes
            pitch[key] = pitch[key].replace('Subject:', '').replace('Body:', '').replace('CTA:', '').replace('Value:', '').strip()

        # Ensure we have a subject
        if not pitch['subject']:
            # Extract first line from body as subject
            lines = pitch['body'].split('\n')
            if lines:
                pitch['subject'] = lines[0][:60]
                pitch['body'] = '\n'.join(lines[1:]).strip()

        return pitch

    def _calculate_quality_score(self, pitch: Dict[str, str], input_data: Dict[str, Any]) -> float:
        """
        Calculate quality score for generated pitch (0-100)

        Based on:
        - Presence of required elements (40%)
        - Personalization (30%)
        - Length appropriateness (20%)
        - Professional tone indicators (10%)
        """
        score = 0.0

        # 1. Required elements (40 points)
        if pitch['subject'] and len(pitch['subject']) > 10:
            score += 10
        if pitch['body'] and len(pitch['body']) > 100:
            score += 15
        if pitch['cta']:
            score += 10
        if pitch['value_prop']:
            score += 5

        # 2. Personalization (30 points)
        body_lower = pitch['body'].lower()
        company = input_data.get('company', '').lower()
        industry = input_data.get('industry', '').lower()
        prospect_name = input_data.get('prospect_name', '').lower().split()[0]  # First name

        if company and company in body_lower:
            score += 10
        if industry and industry in body_lower:
            score += 10
        if prospect_name and prospect_name in body_lower:
            score += 10

        # 3. Length appropriateness (20 points)
        word_count = len(pitch['body'].split())
        if 100 <= word_count <= 250:
            score += 20
        elif 80 <= word_count <= 300:
            score += 15
        elif 50 <= word_count <= 350:
            score += 10

        # 4. Professional tone (10 points)
        professional_indicators = [
            'congratulations', 'growth', 'recently', 'helped',
            'automate', 'scale', 'team', 'would', 'valuable'
        ]
        spam_words = ['free', 'click here', 'limited time', 'act now', '!!!']

        pro_count = sum(1 for word in professional_indicators if word in body_lower)
        spam_count = sum(1 for word in spam_words if word in body_lower)

        score += min(10, pro_count * 2)
        score -= spam_count * 5

        return round(max(0, min(100, score)), 2)


if __name__ == "__main__":
    """Test the Sales Pitch Generation Agent"""

    agent = Phase2SalesPitchAgent()

    test_cases = [
        {
            'name': 'SaaS Startup',
            'data': {
                'prospect_name': 'Sarah Johnson',
                'company': 'TechScale Inc',
                'industry': 'SaaS',
                'company_size': '50-100 employees',
                'pain_points': 'Manual lead qualification, slow sales cycle, team overwhelmed with repetitive tasks',
                'trigger_event': 'Recently raised Series A funding',
                'current_solutions': 'Spreadsheets and basic CRM'
            }
        },
        {
            'name': 'E-commerce Company',
            'data': {
                'prospect_name': 'Mike Chen',
                'company': 'ShopFast',
                'industry': 'E-commerce',
                'company_size': '200+ employees',
                'pain_points': 'Customer support backlog, high cart abandonment, difficulty personalizing at scale',
                'trigger_event': 'Expanding to new markets',
                'current_solutions': 'Zendesk and Mailchimp'
            }
        }
    ]

    print("=" * 80)
    print("PHASE 2 - SALES PITCH GENERATION AGENT TEST")
    print("=" * 80)

    for test_case in test_cases:
        print(f"\n{'─'*80}")
        print(f"Test: {test_case['name']}")
        print(f"Prospect: {test_case['data']['prospect_name']} at {test_case['data']['company']}")
        print(f"{'─'*80}")

        result = agent.process(test_case['data'])

        if result.get('success'):
            print(f"\n📧 SUBJECT: {result['email_subject']}")
            print(f"\n📝 BODY:\n{result['email_body']}")
            print(f"\n🎯 CTA: {result['primary_cta']}")
            print(f"💎 Value: {result['estimated_value']}")
            print(f"\n📊 Quality Score: {result['quality_score']}/100")
            print(f"🤖 Model: {result['model_used']}")
        else:
            print(f"❌ Error: {result.get('error')}")

    print(f"\n{'='*80}")
    print("Testing complete!")
    print("=" * 80)
