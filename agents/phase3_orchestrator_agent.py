"""
Phase 3: Multi-Agent Orchestrator

The Orchestrator Agent coordinates multiple AI agents to deliver cohesive
customer journeys, manages handoffs, and determines optimal agent routing.

Key Features:
- Multi-agent workflow coordination
- Context sharing and memory management
- Human-in-the-loop escalation triggers
- Intelligent routing based on customer state
- Parallel and sequential agent execution

Model: Rule-based + GPT-Neo-2.7B for decision-making
Framework: Custom orchestration with agent registry
"""

import os
import json
import time
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from base_agent import BaseAgent


class Phase3OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent for coordinating multiple AI agents in customer journeys
    """

    def __init__(self):
        super().__init__(
            agent_name="phase3_orchestrator",
            agent_type="orchestrator",
            model_name="EleutherAI/gpt-neo-2.7B"
        )

        # Agent registry: maps agent capabilities to agent names
        self.agent_registry = {
            'lead_qualification': 'phase1_prospect',
            'faq': 'phase1_faq',
            'sales_pitch': 'phase2_sales_pitch',
            'content_creation': 'phase2_content_writer',
            'intent_classification': 'phase2_intent_classifier',
            'email_personalization': 'phase2_email_personalizer',
            'social_media': 'phase2_social_media',
        }

        # Journey stages
        self.journey_stages = [
            'awareness',      # Just discovered us
            'consideration',  # Evaluating options
            'decision',       # Ready to buy
            'onboarding',     # New customer
            'active',         # Using product
            'expansion',      # Upgrading/expanding
            'retention',      # Risk of churn
        ]

        # Escalation thresholds
        self.escalation_config = {
            'high_value_threshold': 10000,  # Deal size in USD
            'low_confidence_threshold': 0.6,  # AI confidence below this
            'complex_request': ['custom', 'enterprise', 'integration'],
            'urgency_keywords': ['urgent', 'asap', 'immediately', 'critical'],
        }

        # Shared context store (in-memory for now, could be Redis)
        self.context_store = {}

        print(f"✓ Orchestrator initialized with {len(self.agent_registry)} registered agents")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate multi-agent workflow based on customer state

        Args:
            input_data: {
                'customer_id': str,
                'journey_stage': str,
                'current_state': dict,
                'intent': str (optional),
                'message': str (optional),
                'engagement_score': int (optional),
                'workflow_type': str (e.g., 'lead_nurture', 'sales_cycle', 'support')
            }

        Returns:
            {
                'success': bool,
                'workflow_id': str,
                'steps_executed': list,
                'next_actions': list,
                'human_handoff': bool,
                'handoff_reason': str,
                'context': dict
            }
        """
        try:
            customer_id = input_data.get('customer_id', 'unknown')
            workflow_type = input_data.get('workflow_type', 'general')

            # Create workflow ID
            workflow_id = f"wf_{customer_id}_{int(time.time())}"

            # Store context
            self._store_context(workflow_id, input_data)

            # Determine workflow path
            if workflow_type == 'lead_nurture':
                result = self._execute_lead_nurture_workflow(workflow_id, input_data)
            elif workflow_type == 'sales_cycle':
                result = self._execute_sales_cycle_workflow(workflow_id, input_data)
            elif workflow_type == 'support':
                result = self._execute_support_workflow(workflow_id, input_data)
            elif workflow_type == 'content_marketing':
                result = self._execute_content_marketing_workflow(workflow_id, input_data)
            else:
                result = self._execute_general_workflow(workflow_id, input_data)

            # Check escalation triggers
            should_escalate, reason = self._check_escalation(input_data, result)

            result['human_handoff'] = should_escalate
            result['handoff_reason'] = reason if should_escalate else None
            result['workflow_id'] = workflow_id
            result['success'] = True

            # Log orchestration
            self._log_orchestration(workflow_id, input_data, result)

            return result

        except Exception as e:
            self.logger.error(f"Orchestration error: {e}")
            return {
                'success': False,
                'error': str(e),
                'human_handoff': True,
                'handoff_reason': f'Orchestration failure: {str(e)}'
            }

    def _execute_lead_nurture_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute lead nurture workflow"""
        steps_executed = []
        next_actions = []

        engagement_score = input_data.get('engagement_score', 0)
        journey_stage = input_data.get('journey_stage', 'awareness')

        # Step 1: Classify intent if message provided
        if input_data.get('message'):
            steps_executed.append({
                'agent': 'intent_classifier',
                'action': 'classify_intent',
                'status': 'simulated'
            })

        # Step 2: Based on engagement and stage, determine actions
        if engagement_score < 30:
            # Low engagement - send educational content
            next_actions.append({
                'agent': 'content_creation',
                'action': 'create_educational_content',
                'priority': 'medium',
                'timing': 'within 24 hours'
            })
            next_actions.append({
                'agent': 'email_personalization',
                'action': 'send_nurture_email',
                'priority': 'medium',
                'timing': 'within 24 hours'
            })

        elif 30 <= engagement_score < 70:
            # Medium engagement - provide value
            next_actions.append({
                'agent': 'content_creation',
                'action': 'create_case_study',
                'priority': 'medium',
                'timing': 'within 12 hours'
            })
            next_actions.append({
                'agent': 'social_media',
                'action': 'engage_on_social',
                'priority': 'low',
                'timing': 'within 48 hours'
            })

        else:  # engagement_score >= 70
            # High engagement - sales activation
            steps_executed.append({
                'agent': 'lead_qualification',
                'action': 'assess_fit',
                'status': 'simulated'
            })
            next_actions.append({
                'agent': 'sales_pitch',
                'action': 'generate_personalized_pitch',
                'priority': 'high',
                'timing': 'immediate'
            })
            next_actions.append({
                'agent': 'human_sales',
                'action': 'schedule_call',
                'priority': 'high',
                'timing': 'within 4 hours'
            })

        return {
            'workflow_type': 'lead_nurture',
            'steps_executed': steps_executed,
            'next_actions': next_actions,
            'context': {
                'engagement_score': engagement_score,
                'journey_stage': journey_stage,
                'recommendation': 'High engagement - activate sales team' if engagement_score >= 70 else 'Continue nurturing'
            }
        }

    def _execute_sales_cycle_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute sales cycle workflow"""
        steps_executed = []
        next_actions = []

        journey_stage = input_data.get('journey_stage', 'consideration')
        deal_size = input_data.get('deal_size', 0)
        current_state = input_data.get('current_state', {})

        # Step 1: Qualify if not already done
        if journey_stage == 'consideration':
            steps_executed.append({
                'agent': 'lead_qualification',
                'action': 'deep_qualification',
                'status': 'simulated'
            })

            # Generate personalized pitch
            next_actions.append({
                'agent': 'sales_pitch',
                'action': 'generate_pitch',
                'priority': 'high',
                'timing': 'immediate',
                'input': {
                    'prospect_name': current_state.get('name'),
                    'company': current_state.get('company'),
                    'industry': current_state.get('industry'),
                    'pain_points': current_state.get('pain_points')
                }
            })

        # Step 2: Decision stage - provide proof
        elif journey_stage == 'decision':
            next_actions.append({
                'agent': 'content_creation',
                'action': 'create_roi_calculator',
                'priority': 'high',
                'timing': 'within 2 hours'
            })
            next_actions.append({
                'agent': 'content_creation',
                'action': 'compile_case_studies',
                'priority': 'high',
                'timing': 'within 2 hours'
            })

            # High value deal? Escalate to human
            if deal_size >= self.escalation_config['high_value_threshold']:
                next_actions.append({
                    'agent': 'human_sales',
                    'action': 'executive_briefing',
                    'priority': 'critical',
                    'timing': 'immediate',
                    'note': f'High value deal (${deal_size:,})'
                })

        return {
            'workflow_type': 'sales_cycle',
            'steps_executed': steps_executed,
            'next_actions': next_actions,
            'context': {
                'journey_stage': journey_stage,
                'deal_size': deal_size,
                'recommendation': 'Human involvement recommended' if deal_size >= self.escalation_config['high_value_threshold'] else 'AI-driven process'
            }
        }

    def _execute_support_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute support workflow"""
        steps_executed = []
        next_actions = []

        message = input_data.get('message', '')
        urgency = self._detect_urgency(message)

        # Step 1: Classify intent
        steps_executed.append({
            'agent': 'intent_classifier',
            'action': 'classify_support_intent',
            'status': 'simulated'
        })

        # Step 2: Route based on urgency
        if urgency == 'high':
            # Immediate human escalation
            next_actions.append({
                'agent': 'human_support',
                'action': 'immediate_response',
                'priority': 'critical',
                'timing': 'immediate'
            })
        else:
            # Try FAQ agent first
            next_actions.append({
                'agent': 'faq',
                'action': 'find_answer',
                'priority': 'high',
                'timing': 'immediate'
            })
            next_actions.append({
                'agent': 'email_personalization',
                'action': 'send_support_response',
                'priority': 'medium',
                'timing': 'within 1 hour'
            })

        return {
            'workflow_type': 'support',
            'steps_executed': steps_executed,
            'next_actions': next_actions,
            'context': {
                'urgency': urgency,
                'recommendation': 'Immediate escalation' if urgency == 'high' else 'AI-handled'
            }
        }

    def _execute_content_marketing_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute content marketing workflow"""
        steps_executed = []
        next_actions = []

        topic = input_data.get('topic')
        platforms = input_data.get('platforms', ['linkedin', 'twitter'])

        # Step 1: Create content
        steps_executed.append({
            'agent': 'content_creation',
            'action': 'write_blog_post',
            'status': 'simulated'
        })

        # Step 2: Optimize for SEO
        next_actions.append({
            'agent': 'content_creation',
            'action': 'seo_optimization',
            'priority': 'medium',
            'timing': 'within 2 hours'
        })

        # Step 3: Create social posts
        next_actions.append({
            'agent': 'social_media',
            'action': 'create_platform_posts',
            'priority': 'medium',
            'timing': 'within 4 hours',
            'input': {
                'platforms': platforms,
                'topic': topic
            }
        })

        # Step 4: Schedule distribution
        next_actions.append({
            'agent': 'marketing_automation',
            'action': 'schedule_distribution',
            'priority': 'low',
            'timing': 'within 24 hours'
        })

        return {
            'workflow_type': 'content_marketing',
            'steps_executed': steps_executed,
            'next_actions': next_actions,
            'context': {
                'topic': topic,
                'platforms': platforms,
                'recommendation': 'Full content pipeline activated'
            }
        }

    def _execute_general_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute general workflow when type not specified"""
        steps_executed = []
        next_actions = []

        # Classify intent if message provided
        if input_data.get('message'):
            steps_executed.append({
                'agent': 'intent_classifier',
                'action': 'classify_intent',
                'status': 'simulated'
            })

            # Based on simulated intent, suggest actions
            next_actions.append({
                'agent': 'email_personalization',
                'action': 'send_response',
                'priority': 'medium',
                'timing': 'within 2 hours'
            })

        return {
            'workflow_type': 'general',
            'steps_executed': steps_executed,
            'next_actions': next_actions,
            'context': {
                'recommendation': 'General workflow - consider specifying workflow_type'
            }
        }

    def _check_escalation(
        self,
        input_data: Dict[str, Any],
        result: Dict[str, Any]
    ) -> tuple:
        """
        Check if human escalation is needed

        Returns:
            (should_escalate: bool, reason: str)
        """
        # Check deal size
        if input_data.get('deal_size', 0) >= self.escalation_config['high_value_threshold']:
            return True, f"High value deal: ${input_data['deal_size']:,}"

        # Check urgency
        message = input_data.get('message', '')
        if self._detect_urgency(message) == 'high':
            return True, "Urgent request detected"

        # Check complex requests
        for keyword in self.escalation_config['complex_request']:
            if keyword in message.lower():
                return True, f"Complex request detected: {keyword}"

        # Check AI confidence (simulated for now)
        confidence = input_data.get('ai_confidence', 1.0)
        if confidence < self.escalation_config['low_confidence_threshold']:
            return True, f"Low AI confidence: {confidence:.2%}"

        return False, None

    def _detect_urgency(self, message: str) -> str:
        """Detect urgency level from message"""
        message_lower = message.lower()

        for keyword in self.escalation_config['urgency_keywords']:
            if keyword in message_lower:
                return 'high'

        if any(word in message_lower for word in ['soon', 'today', 'need help']):
            return 'medium'

        return 'low'

    def _store_context(self, workflow_id: str, context: Dict[str, Any]):
        """Store context for workflow"""
        self.context_store[workflow_id] = {
            'data': context,
            'timestamp': datetime.now().isoformat(),
            'ttl': 3600  # 1 hour
        }

    def _get_context(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve context for workflow"""
        return self.context_store.get(workflow_id)

    def _log_orchestration(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        result: Dict[str, Any]
    ):
        """Log orchestration event"""
        log_entry = {
            'workflow_id': workflow_id,
            'workflow_type': input_data.get('workflow_type'),
            'customer_id': input_data.get('customer_id'),
            'steps_executed': len(result.get('steps_executed', [])),
            'next_actions': len(result.get('next_actions', [])),
            'human_handoff': result.get('human_handoff'),
            'handoff_reason': result.get('handoff_reason'),
            'timestamp': datetime.now().isoformat()
        }

        self.logger.info(f"Orchestration: {json.dumps(log_entry)}")

        # Could also log to database
        if self.db:
            try:
                self.db.log_interaction(
                    agent_name=self.agent_name,
                    interaction_type='orchestration',
                    input_data=input_data,
                    output_data=result
                )
            except Exception as e:
                self.logger.error(f"Failed to log to database: {e}")

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a workflow"""
        context = self._get_context(workflow_id)

        if not context:
            return {
                'success': False,
                'error': 'Workflow not found'
            }

        return {
            'success': True,
            'workflow_id': workflow_id,
            'context': context,
            'status': 'active' if time.time() - context['timestamp'] < context['ttl'] else 'expired'
        }


if __name__ == "__main__":
    # Test the orchestrator
    print("\n" + "="*80)
    print("Testing Phase 3 Orchestrator Agent")
    print("="*80 + "\n")

    agent = Phase3OrchestratorAgent()

    # Test 1: Lead nurture workflow (high engagement)
    print("Test 1: High engagement lead nurture")
    print("-"*80)
    result = agent.process({
        'customer_id': 'lead_001',
        'workflow_type': 'lead_nurture',
        'journey_stage': 'consideration',
        'engagement_score': 85,
        'current_state': {
            'name': 'Sarah Chen',
            'company': 'TechCorp',
            'industry': 'SaaS'
        }
    })
    print(json.dumps(result, indent=2))

    # Test 2: Sales cycle workflow (high value)
    print("\n\nTest 2: High value sales cycle")
    print("-"*80)
    result = agent.process({
        'customer_id': 'prospect_002',
        'workflow_type': 'sales_cycle',
        'journey_stage': 'decision',
        'deal_size': 25000,
        'current_state': {
            'name': 'John Smith',
            'company': 'Enterprise Inc',
            'industry': 'Finance'
        }
    })
    print(json.dumps(result, indent=2))

    # Test 3: Urgent support request
    print("\n\nTest 3: Urgent support request")
    print("-"*80)
    result = agent.process({
        'customer_id': 'customer_003',
        'workflow_type': 'support',
        'message': 'URGENT: Our system is down and we need help immediately!',
        'journey_stage': 'active'
    })
    print(json.dumps(result, indent=2))

    print("\n" + "="*80)
    print("Orchestrator Agent Tests Complete!")
    print("="*80)
