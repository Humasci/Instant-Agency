"""
Marketing Prospecting Agent
Researches and identifies qualified prospects
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from base_agent import BaseAgent
from typing import Dict, Any, List
import json
from datetime import datetime


class MarketingProspectingAgent(BaseAgent):
    """
    Agent that researches and qualifies prospects for outreach campaigns
    """

    def __init__(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            'config.yaml'
        )
        super().__init__(config_path)

        # Load configuration
        self.segmentation = self.config.get('segmentation', {})
        self.scoring_config = self.config.get('scoring', {})
        self.outreach_config = self.config.get('outreach', {})

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Research a prospect or company

        Args:
            input_data: Dict with keys:
                - company_name: Company to research
                - industry: Optional industry filter
                - additional_context: Any additional context

        Returns:
            Research results with ICP fit score and outreach recommendations
        """
        start_time = datetime.now()

        try:
            company_name = input_data.get('company_name')
            industry = input_data.get('industry')

            # Check if already in CRM
            existing = self._check_crm(company_name)
            if existing:
                return {
                    'status': 'already_in_crm',
                    'crm_record': existing,
                    'message': f'{company_name} already exists in CRM'
                }

            # Check cache
            cache_key = f"prospect_research:{company_name.lower()}"
            cached_result = self.cache_get(cache_key)
            if cached_result:
                return cached_result

            # Gather company data
            company_data = self._research_company(company_name)

            # Find decision makers
            decision_makers = self._find_decision_makers(company_name)

            # Calculate ICP fit score
            icp_score = self._calculate_icp_fit(company_data)

            # Determine if prospect qualifies
            qualifies = icp_score >= self.scoring_config.get('thresholds', {}).get('fair', 4.0)

            # Generate outreach strategy
            outreach_strategy = None
            if qualifies:
                outreach_strategy = self._generate_outreach_strategy(
                    company_data,
                    decision_makers
                )

            # Compile result
            result = {
                'company_name': company_name,
                'company_data': company_data,
                'decision_makers': decision_makers,
                'icp_fit_score': icp_score,
                'qualifies_for_outreach': qualifies,
                'outreach_strategy': outreach_strategy,
                'timestamp': datetime.now().isoformat(),
                'agent_version': self.version
            }

            # Cache result
            self.cache_set(cache_key, result, ttl=7200)

            # Log interaction
            self.log_interaction(input_data, result)

            # Track metrics
            research_time = (datetime.now() - start_time).total_seconds()
            self.track_metric('research_time', research_time)
            self.track_metric('icp_fit_score', icp_score)
            self.track_metric('prospects_researched', 1)

            return result

        except Exception as e:
            self.logger.error(f"Prospect research failed: {e}")
            return {
                'error': str(e),
                'success': False
            }

    def _check_crm(self, company_name: str) -> Dict[str, Any]:
        """Check if company already exists in CRM"""
        try:
            query = """
                SELECT *
                FROM crm_accounts
                WHERE LOWER(name) = LOWER(%s)
            """
            results = self.db_query(query, (company_name,))

            if results:
                return dict(results[0])
        except Exception as e:
            self.logger.warning(f"CRM check failed: {e}")

        return None

    def _research_company(self, company_name: str) -> Dict[str, Any]:
        """
        Research company information
        In production, this would call Clearbit, Apollo, etc.
        """
        # Placeholder implementation
        return {
            'name': company_name,
            'industry': 'Technology',
            'employees': 250,
            'revenue_estimate': 25000000,
            'location': 'San Francisco, CA',
            'website': f'www.{company_name.lower().replace(" ", "")}.com',
            'founded': 2015,
            'funding': 'Series B',
            'tech_stack': ['AWS', 'React', 'PostgreSQL'],
            'recent_news': [
                {
                    'title': f'{company_name} expands to new markets',
                    'date': '2025-10-15',
                    'source': 'TechCrunch'
                }
            ]
        }

    def _find_decision_makers(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Find key decision makers at the company
        In production, this would use LinkedIn Sales Navigator API
        """
        # Placeholder implementation
        return [
            {
                'name': 'John Smith',
                'title': 'VP of Marketing',
                'linkedin': 'linkedin.com/in/johnsmith',
                'recent_activity': ['Posted about marketing automation'],
                'engagement_score': 8
            },
            {
                'name': 'Jane Doe',
                'title': 'CMO',
                'linkedin': 'linkedin.com/in/janedoe',
                'recent_activity': ['Changed jobs recently'],
                'engagement_score': 9
            }
        ]

    def _calculate_icp_fit(self, company_data: Dict[str, Any]) -> float:
        """Calculate how well the company fits our ICP"""

        criteria = self.scoring_config.get('icp_fit_criteria', [])
        total_score = 0.0

        for criterion in criteria:
            name = criterion['name']
            weight = criterion['weight']
            score = self._score_criterion(name, company_data)
            total_score += score * weight

        # Normalize to 0-10 scale
        return round(total_score * 10, 2)

    def _score_criterion(self, criterion: str, company_data: Dict[str, Any]) -> float:
        """Score a specific ICP criterion (0-1 scale)"""

        if criterion == 'industry_match':
            allowed_industries = self.segmentation.get('criteria', {}).get('industries', [])
            industry = company_data.get('industry', '')
            return 1.0 if industry in allowed_industries else 0.5

        elif criterion == 'company_size':
            size_criteria = self.segmentation.get('criteria', {}).get('company_size', {})
            employees = company_data.get('employees', 0)
            min_emp = size_criteria.get('min_employees', 0)
            max_emp = size_criteria.get('max_employees', 10000)

            if min_emp <= employees <= max_emp:
                return 1.0
            elif employees < min_emp:
                return max(0.0, employees / min_emp)
            else:
                return 0.5

        elif criterion == 'technology_stack':
            # Score based on technology match
            tech_stack = company_data.get('tech_stack', [])
            relevant_tech = ['AWS', 'Azure', 'React', 'Node.js']
            matches = len(set(tech_stack) & set(relevant_tech))
            return min(1.0, matches / 3)

        elif criterion == 'growth_indicators':
            # Check for growth signals
            recent_news = company_data.get('recent_news', [])
            funding = company_data.get('funding', '')

            score = 0.0
            if recent_news:
                score += 0.4
            if funding in ['Series B', 'Series C', 'Series D']:
                score += 0.6

            return min(1.0, score)

        elif criterion == 'budget_signals':
            # Estimate budget capacity
            revenue = company_data.get('revenue_estimate', 0)
            if revenue >= 10000000:  # $10M+
                return 1.0
            elif revenue >= 5000000:  # $5M+
                return 0.7
            else:
                return 0.3

        return 0.5  # Default score

    def _generate_outreach_strategy(
        self,
        company_data: Dict[str, Any],
        decision_makers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate personalized outreach strategy"""

        # Build context for LLM
        context = f"""
Company: {company_data.get('name')}
Industry: {company_data.get('industry')}
Size: {company_data.get('employees')} employees
Recent News: {', '.join([n['title'] for n in company_data.get('recent_news', [])])}

Decision Makers:
{json.dumps(decision_makers, indent=2)}

Generate a personalized outreach strategy including:
1. Best contact to reach out to first
2. Recommended channel (email, LinkedIn, phone)
3. Key personalization points to mention
4. Suggested subject line / message hook
5. Value proposition angle
"""

        # Get LLM recommendation
        try:
            strategy_text = self.llm(context)

            return {
                'strategy': strategy_text,
                'primary_contact': decision_makers[0] if decision_makers else None,
                'recommended_channel': 'email',
                'personalization_points': [
                    'Recent company expansion',
                    'Technology stack alignment',
                    'Industry expertise'
                ]
            }
        except Exception as e:
            self.logger.warning(f"Strategy generation failed: {e}")
            return {
                'strategy': 'Generic outreach',
                'primary_contact': decision_makers[0] if decision_makers else None,
                'recommended_channel': 'email'
            }


if __name__ == "__main__":
    # Test the agent
    agent = MarketingProspectingAgent()

    test_input = {
        'company_name': 'Acme Corp',
        'industry': 'Technology'
    }

    result = agent.process(test_input)
    print(json.dumps(result, indent=2))
