"""
Phase 3: Customer Success Agent

Manages customer lifecycle from onboarding through expansion, focusing on
retention, satisfaction, and revenue growth.

Key Features:
- Automated onboarding workflows
- Health score monitoring
- Proactive intervention for at-risk customers
- Upsell/cross-sell identification
- Customer satisfaction tracking

Model: GPT-Neo-2.7B
Collaborates with: Support, Sales, Analytics
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from base_agent import BaseAgent


class Phase3CustomerSuccessAgent(BaseAgent):
    """
    Customer Success Agent for retention and growth
    """

    def __init__(self):
        super().__init__(
            agent_name="phase3_customer_success",
            agent_type="customer_success",
            model_name="EleutherAI/gpt-neo-2.7B"
        )

        # Customer lifecycle stages
        self.lifecycle_stages = [
            'onboarding', 'adoption', 'value_realization',
            'expansion', 'renewal', 'advocacy', 'at_risk', 'churned'
        ]

        # Health score factors
        self.health_factors = {
            'product_usage': 0.30,
            'engagement': 0.25,
            'support_tickets': 0.15,
            'nps_score': 0.15,
            'revenue_trend': 0.15
        }

        print(f"✓ Customer Success Agent initialized")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process customer success action

        Args:
            input_data: {
                'action': str,  # 'health_check', 'onboard', 'intervention', 'expansion_opportunity'
                'customer_id': str,
                'customer_data': dict,
                'usage_data': dict,
                'account_data': dict
            }

        Returns:
            Success plan with recommendations and actions
        """
        try:
            action = input_data.get('action', 'health_check')

            if action == 'health_check':
                return self._calculate_customer_health(input_data)
            elif action == 'onboard':
                return self._create_onboarding_plan(input_data)
            elif action == 'intervention':
                return self._create_intervention_plan(input_data)
            elif action == 'expansion_opportunity':
                return self._identify_expansion_opportunities(input_data)
            elif action == 'renewal':
                return self._create_renewal_strategy(input_data)
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            self.logger.error(f"Customer success error: {e}")
            return {'success': False, 'error': str(e)}

    def _calculate_customer_health(self, input_data: Dict) -> Dict:
        """Calculate customer health score"""
        customer_data = input_data.get('customer_data', {})
        usage_data = input_data.get('usage_data', {})
        account_data = input_data.get('account_data', {})

        # Calculate individual scores
        usage_score = self._score_product_usage(usage_data)
        engagement_score = self._score_engagement(customer_data)
        support_score = self._score_support_health(customer_data)
        satisfaction_score = customer_data.get('nps_score', 50)
        revenue_score = self._score_revenue_trend(account_data)

        # Weighted health score
        health_score = (
            usage_score * self.health_factors['product_usage'] +
            engagement_score * self.health_factors['engagement'] +
            support_score * self.health_factors['support_tickets'] +
            satisfaction_score * self.health_factors['nps_score'] +
            revenue_score * self.health_factors['revenue_trend']
        )

        # Determine health status
        if health_score >= 80:
            status = 'healthy'
            risk_level = 'low'
        elif health_score >= 60:
            status = 'moderate'
            risk_level = 'medium'
        else:
            status = 'at_risk'
            risk_level = 'high'

        # Identify issues
        issues = []
        if usage_score < 60:
            issues.append('Low product adoption')
        if engagement_score < 50:
            issues.append('Decreasing engagement')
        if support_score < 50:
            issues.append('High support burden')

        # Recommend actions
        actions = self._recommend_health_actions(health_score, issues)

        return {
            'success': True,
            'customer_id': input_data.get('customer_id'),
            'health_score': round(health_score, 1),
            'health_status': status,
            'risk_level': risk_level,
            'breakdown': {
                'product_usage': usage_score,
                'engagement': engagement_score,
                'support': support_score,
                'satisfaction': satisfaction_score,
                'revenue': revenue_score
            },
            'issues': issues,
            'recommended_actions': actions,
            'timestamp': datetime.now().isoformat()
        }

    def _create_onboarding_plan(self, input_data: Dict) -> Dict:
        """Create customer onboarding plan"""
        customer_data = input_data.get('customer_data', {})
        account_data = input_data.get('account_data', {})

        plan = {
            'week_1': {
                'goal': 'Account setup and initial configuration',
                'activities': [
                    'Kickoff call with success manager',
                    'Complete account setup',
                    'Import existing data',
                    'Configure first workflow',
                    'Schedule training session'
                ],
                'success_criteria': 'Account configured, first workflow live'
            },
            'week_2': {
                'goal': 'Team onboarding and adoption',
                'activities': [
                    'Team training session',
                    'Create 3+ agents',
                    'Integrate with existing tools',
                    'Set up reporting dashboard',
                    'Review progress check-in'
                ],
                'success_criteria': '3+ team members active, 3+ agents deployed'
            },
            'week_3_4': {
                'goal': 'Value realization',
                'activities': [
                    'Measure initial ROI',
                    'Optimize workflows based on data',
                    'Expand to additional use cases',
                    'Collect stakeholder feedback',
                    '30-day success review'
                ],
                'success_criteria': 'Measurable business impact, stakeholder satisfaction >8/10'
            }
        }

        milestones = [
            {'milestone': 'First agent deployed', 'target_day': 3, 'critical': True},
            {'milestone': 'Team trained', 'target_day': 10, 'critical': True},
            {'milestone': 'ROI demonstrated', 'target_day': 30, 'critical': True}
        ]

        return {
            'success': True,
            'customer_id': input_data.get('customer_id'),
            'onboarding_plan': plan,
            'milestones': milestones,
            'duration': '30 days',
            'success_criteria': '80% feature adoption, positive stakeholder feedback',
            'timestamp': datetime.now().isoformat()
        }

    def _create_intervention_plan(self, input_data: Dict) -> Dict:
        """Create plan for at-risk customer intervention"""
        customer_data = input_data.get('customer_data', {})
        health_data = self._calculate_customer_health(input_data)

        issues = health_data.get('issues', [])
        health_score = health_data.get('health_score', 50)

        # Determine urgency
        if health_score < 40:
            urgency = 'critical'
            timeline = 'Immediate action required'
        elif health_score < 60:
            urgency = 'high'
            timeline = 'Address within 72 hours'
        else:
            urgency = 'medium'
            timeline = 'Address within 1 week'

        # Create intervention steps
        intervention_steps = []

        if 'Low product adoption' in issues:
            intervention_steps.append({
                'step': 'Schedule product adoption workshop',
                'owner': 'CSM',
                'timeline': '48 hours',
                'outcome': 'Identify blockers, create adoption plan'
            })

        if 'Decreasing engagement' in issues:
            intervention_steps.append({
                'step': 'Executive business review',
                'owner': 'CSM + Account Executive',
                'timeline': '1 week',
                'outcome': 'Realign on business objectives'
            })

        if 'High support burden' in issues:
            intervention_steps.append({
                'step': 'Dedicated support session',
                'owner': 'Support Team',
                'timeline': '24 hours',
                'outcome': 'Resolve outstanding issues'
            })

        # Add standard steps
        intervention_steps.append({
            'step': 'Customer satisfaction survey',
            'owner': 'CSM',
            'timeline': '24 hours',
            'outcome': 'Understand customer sentiment'
        })

        intervention_steps.append({
            'step': 'Create success plan',
            'owner': 'CSM',
            'timeline': '1 week',
            'outcome': 'Document path to health'
        })

        return {
            'success': True,
            'customer_id': input_data.get('customer_id'),
            'urgency': urgency,
            'timeline': timeline,
            'current_health': health_score,
            'target_health': 75,
            'issues': issues,
            'intervention_steps': intervention_steps,
            'escalation': 'Escalate to VP Customer Success' if health_score < 40 else None,
            'timestamp': datetime.now().isoformat()
        }

    def _identify_expansion_opportunities(self, input_data: Dict) -> Dict:
        """Identify upsell/cross-sell opportunities"""
        customer_data = input_data.get('customer_data', {})
        usage_data = input_data.get('usage_data', {})
        account_data = input_data.get('account_data', {})

        current_plan = account_data.get('plan', 'starter')
        current_mrr = account_data.get('mrr', 0)
        usage_trend = usage_data.get('trend', 'stable')

        opportunities = []

        # Usage-based expansion
        if usage_data.get('usage_percentage', 0) > 80:
            opportunities.append({
                'type': 'plan_upgrade',
                'recommendation': 'Upgrade to next tier',
                'rationale': 'Customer at 80%+ capacity',
                'potential_value': current_mrr * 2,
                'confidence': 0.85,
                'timing': 'This month'
            })

        # Feature adoption
        unused_features = usage_data.get('unused_premium_features', [])
        if len(unused_features) > 0:
            opportunities.append({
                'type': 'feature_adoption',
                'recommendation': f'Activate {len(unused_features)} premium features',
                'rationale': 'Has access but not using valuable features',
                'potential_value': 0,  # Already paying
                'confidence': 0.70,
                'timing': 'Next QBR'
            })

        # Team expansion
        if usage_data.get('active_users', 0) >= usage_data.get('seat_limit', 999) * 0.9:
            opportunities.append({
                'type': 'seat_expansion',
                'recommendation': 'Add 5+ seats',
                'rationale': 'Team near seat capacity',
                'potential_value': current_mrr * 0.5,
                'confidence': 0.90,
                'timing': 'This quarter'
            })

        # Cross-sell
        if customer_data.get('satisfaction', 0) > 8:
            opportunities.append({
                'type': 'cross_sell',
                'recommendation': 'Introduce advanced analytics module',
                'rationale': 'High satisfaction, good expansion candidate',
                'potential_value': 500,
                'confidence': 0.60,
                'timing': 'Next quarter'
            })

        # Calculate total opportunity value
        total_opportunity = sum(opp.get('potential_value', 0) for opp in opportunities)

        return {
            'success': True,
            'customer_id': input_data.get('customer_id'),
            'current_mrr': current_mrr,
            'expansion_opportunities': opportunities,
            'total_opportunity_value': total_opportunity,
            'opportunity_count': len(opportunities),
            'recommended_next_step': opportunities[0]['recommendation'] if opportunities else 'Continue nurturing',
            'timestamp': datetime.now().isoformat()
        }

    def _create_renewal_strategy(self, input_data: Dict) -> Dict:
        """Create renewal strategy"""
        customer_data = input_data.get('customer_data', {})
        account_data = input_data.get('account_data', {})

        renewal_date = account_data.get('renewal_date', (datetime.now() + timedelta(days=90)).isoformat())
        days_to_renewal = (datetime.fromisoformat(renewal_date) - datetime.now()).days

        health_data = self._calculate_customer_health(input_data)
        health_score = health_data.get('health_score', 70)

        # Determine renewal risk
        if health_score >= 75 and days_to_renewal > 60:
            risk = 'low'
            strategy = 'Standard renewal process with expansion discussion'
        elif health_score >= 60:
            risk = 'medium'
            strategy = 'Proactive engagement to strengthen relationship'
        else:
            risk = 'high'
            strategy = 'Urgent intervention required - schedule executive review'

        # Create renewal timeline
        timeline = []

        if days_to_renewal > 90:
            timeline.append({
                'milestone': 'Initial check-in',
                'days_before_renewal': 90,
                'action': 'Schedule QBR to review value'
            })

        timeline.append({
            'milestone': 'Value review',
            'days_before_renewal': 60,
            'action': 'Document ROI and business impact'
        })

        timeline.append({
            'milestone': 'Renewal discussion',
            'days_before_renewal': 45,
            'action': 'Present renewal proposal with expansion opportunities'
        })

        timeline.append({
            'milestone': 'Finalize terms',
            'days_before_renewal': 30,
            'action': 'Negotiate and close renewal'
        })

        return {
            'success': True,
            'customer_id': input_data.get('customer_id'),
            'renewal_date': renewal_date,
            'days_to_renewal': days_to_renewal,
            'renewal_risk': risk,
            'renewal_probability': 0.95 if risk == 'low' else 0.75 if risk == 'medium' else 0.50,
            'strategy': strategy,
            'timeline': timeline,
            'current_health': health_score,
            'timestamp': datetime.now().isoformat()
        }

    # Helper methods

    def _score_product_usage(self, usage_data: Dict) -> int:
        """Score product usage (0-100)"""
        active_days = usage_data.get('active_days_last_30', 0)
        features_used = usage_data.get('features_used', 0)
        total_features = usage_data.get('total_features', 10)

        day_score = min((active_days / 20) * 100, 100)  # 20+ days = 100
        feature_score = (features_used / total_features) * 100

        return int((day_score * 0.6) + (feature_score * 0.4))

    def _score_engagement(self, customer_data: Dict) -> int:
        """Score customer engagement (0-100)"""
        logins_last_30 = customer_data.get('logins_last_30', 0)
        meetings_attended = customer_data.get('meetings_attended', 0)
        resources_accessed = customer_data.get('resources_accessed', 0)

        login_score = min((logins_last_30 / 15) * 100, 100)
        meeting_score = min(meetings_attended * 25, 100)
        resource_score = min(resources_accessed * 10, 100)

        return int((login_score * 0.5) + (meeting_score * 0.3) + (resource_score * 0.2))

    def _score_support_health(self, customer_data: Dict) -> int:
        """Score support health (0-100) - fewer tickets = better"""
        tickets_last_30 = customer_data.get('support_tickets_last_30', 0)
        avg_resolution_time = customer_data.get('avg_resolution_hours', 24)

        # Fewer tickets = higher score
        ticket_score = max(100 - (tickets_last_30 * 10), 0)

        # Faster resolution = higher score
        resolution_score = max(100 - (avg_resolution_time - 24), 50)

        return int((ticket_score * 0.7) + (resolution_score * 0.3))

    def _score_revenue_trend(self, account_data: Dict) -> int:
        """Score revenue trend (0-100)"""
        mrr_growth = account_data.get('mrr_growth_percentage', 0)

        if mrr_growth >= 20:
            return 100
        elif mrr_growth >= 10:
            return 85
        elif mrr_growth >= 0:
            return 70
        elif mrr_growth >= -10:
            return 50
        else:
            return 30

    def _recommend_health_actions(self, health_score: int, issues: List) -> List:
        """Recommend actions based on health"""
        actions = []

        if health_score < 60:
            actions.append({
                'action': 'Schedule urgent intervention meeting',
                'priority': 'critical',
                'timeline': '48 hours'
            })

        if 'Low product adoption' in issues:
            actions.append({
                'action': 'Conduct adoption workshop',
                'priority': 'high',
                'timeline': '1 week'
            })

        if 'Decreasing engagement' in issues:
            actions.append({
                'action': 'Executive business review',
                'priority': 'high',
                'timeline': '1 week'
            })

        if not actions:
            actions.append({
                'action': 'Continue standard success cadence',
                'priority': 'normal',
                'timeline': 'Ongoing'
            })

        return actions


if __name__ == "__main__":
    print("\n" + "="*80)
    print("Testing Phase 3 Customer Success Agent")
    print("="*80 + "\n")

    agent = Phase3CustomerSuccessAgent()

    # Test: Health check
    result = agent.process({
        'action': 'health_check',
        'customer_id': 'cust_001',
        'customer_data': {
            'logins_last_30': 18,
            'meetings_attended': 2,
            'resources_accessed': 5,
            'support_tickets_last_30': 2,
            'avg_resolution_hours': 12,
            'nps_score': 75
        },
        'usage_data': {
            'active_days_last_30': 22,
            'features_used': 8,
            'total_features': 10,
            'usage_percentage': 85
        },
        'account_data': {
            'mrr': 1500,
            'mrr_growth_percentage': 15,
            'plan': 'professional'
        }
    })

    print(json.dumps(result, indent=2))
    print("\n" + "="*80)
