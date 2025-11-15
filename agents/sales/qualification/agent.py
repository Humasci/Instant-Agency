"""
Sales Qualification Agent
Assesses lead fit and readiness using BANT framework
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from base_agent import BaseAgent
from typing import Dict, Any
import json
from datetime import datetime


class SalesQualificationAgent(BaseAgent):
    """
    Agent that qualifies sales leads using BANT framework
    """

    def __init__(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            'config.yaml'
        )
        super().__init__(config_path)

        # Load scoring configuration
        self.scoring_config = self.config.get('scoring', {})
        self.weights = self.scoring_config.get('weights', {})
        self.thresholds = self.scoring_config.get('thresholds', {})

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Qualify a lead based on provided information

        Args:
            input_data: Dict with keys:
                - lead_id: CRM lead ID
                - responses: Dict of lead responses/information
                - context: Optional additional context

        Returns:
            Qualification result with scores and recommendations
        """
        start_time = datetime.now()

        try:
            # Extract input
            lead_id = input_data.get('lead_id')
            responses = input_data.get('responses', {})
            context = input_data.get('context', {})

            # Check cache first
            cache_key = f"qualification:{lead_id}"
            cached_result = self.cache_get(cache_key)
            if cached_result:
                self.track_metric('response_time', 0.1)  # Cache hit
                return cached_result

            # Enrich with CRM data
            crm_data = self._lookup_crm_data(lead_id)
            if crm_data:
                responses.update(crm_data)

            # Enrich with company research
            if 'company' in responses:
                company_data = self._research_company(responses['company'])
                context['company_data'] = company_data

            # Build prompt for LLM
            prompt = self._build_qualification_prompt(responses, context)

            # Get LLM assessment
            llm_response = self.llm(prompt)

            # Parse LLM response
            qualification_result = self._parse_llm_response(llm_response)

            # Calculate weighted score
            overall_score = self._calculate_overall_score(
                qualification_result.get('bant_scores', {})
            )
            qualification_result['overall_score'] = overall_score

            # Determine qualification status
            qualification_result['qualification_status'] = \
                self._determine_status(overall_score)

            # Check for escalation
            escalation = self.should_escalate({
                'overall_score': overall_score,
                'deal_value': responses.get('deal_value', 0)
            })

            if escalation:
                qualification_result['escalation'] = escalation

            # Add metadata
            qualification_result['lead_id'] = lead_id
            qualification_result['timestamp'] = datetime.now().isoformat()
            qualification_result['agent_version'] = self.version

            # Cache result
            self.cache_set(cache_key, qualification_result)

            # Log interaction
            self.log_interaction(input_data, qualification_result)

            # Track metrics
            response_time = (datetime.now() - start_time).total_seconds()
            self.track_metric('response_time', response_time)
            self.track_metric('qualification_score', overall_score)

            return qualification_result

        except Exception as e:
            self.logger.error(f"Qualification failed: {e}")
            return {
                'error': str(e),
                'success': False
            }

    def _build_qualification_prompt(
        self,
        responses: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Build the qualification prompt for the LLM"""

        system_prompt = self.get_system_prompt()

        # Format responses
        responses_text = "\n".join([
            f"- {key}: {value}"
            for key, value in responses.items()
        ])

        # Format context
        context_text = ""
        if context:
            context_text = "\nAdditional Context:\n" + "\n".join([
                f"- {key}: {value}"
                for key, value in context.items()
            ])

        prompt = f"""{system_prompt}

Lead Information:
{responses_text}
{context_text}

Please provide a qualification assessment in JSON format.
"""

        return prompt

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate LLM response"""
        try:
            # Try to extract JSON from response
            # LLM might add extra text before/after JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                return result
            else:
                raise ValueError("No JSON found in response")

        except Exception as e:
            self.logger.warning(f"Failed to parse LLM response: {e}")

            # Return default structure
            return {
                'bant_scores': {
                    'budget': 5,
                    'authority': 5,
                    'need': 5,
                    'timeline': 5
                },
                'reasoning': 'Failed to parse detailed assessment',
                'missing_info': ['Unable to assess - need more information']
            }

    def _calculate_overall_score(self, bant_scores: Dict[str, float]) -> float:
        """Calculate weighted overall BANT score"""
        total_score = 0.0

        for dimension, weight in self.weights.items():
            score = bant_scores.get(dimension, 0)
            total_score += score * weight

        return round(total_score, 2)

    def _determine_status(self, score: float) -> str:
        """Determine qualification status based on score"""
        if score >= self.thresholds.get('hot', 8):
            return 'hot'
        elif score >= self.thresholds.get('warm', 6):
            return 'warm'
        elif score >= self.thresholds.get('cold', 3):
            return 'cold'
        else:
            return 'disqualified'

    def _lookup_crm_data(self, lead_id: int) -> Dict[str, Any]:
        """Look up lead data from CRM"""
        try:
            query = """
                SELECT *
                FROM crm_leads
                WHERE id = %s
            """
            results = self.db_query(query, (lead_id,))

            if results:
                return dict(results[0])
        except Exception as e:
            self.logger.warning(f"CRM lookup failed: {e}")

        return {}

    def _research_company(self, company_name: str) -> Dict[str, Any]:
        """Research company using external APIs"""
        # Placeholder - implement with Clearbit, Apollo, etc.
        return {
            'industry': 'Technology',
            'size': 'Mid-market',
            'revenue_estimate': '10M-50M'
        }


if __name__ == "__main__":
    # Test the agent
    agent = SalesQualificationAgent()

    test_input = {
        'lead_id': 12345,
        'responses': {
            'budget': '50000',
            'timeline': 'Q1 2025',
            'decision_maker': True,
            'pain_point': 'Manual processes taking too much time',
            'company': 'Acme Corp',
            'deal_value': 75000
        }
    }

    result = agent.process(test_input)
    print(json.dumps(result, indent=2))
