"""
Client Communication Manager
Manages all client interactions, call scheduling, and communication workflows
Handles client meetings, presentations, and ongoing relationship management
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

sys.path.append(os.path.dirname(__file__))
from base_agent import BaseAgent

class CommunicationType(Enum):
    INITIAL_CONSULTATION = "initial_consultation"
    STRATEGY_PRESENTATION = "strategy_presentation"
    PROGRESS_UPDATE = "progress_update"
    PERFORMANCE_REVIEW = "performance_review"
    CRISIS_MANAGEMENT = "crisis_management"
    TECHNICAL_DISCUSSION = "technical_discussion"
    CREATIVE_REVIEW = "creative_review"
    CONTRACT_NEGOTIATION = "contract_negotiation"

@dataclass
class ClientProfile:
    client_id: str
    company: str
    primary_contact: str
    contact_details: Dict[str, Any]
    industry: str
    company_size: str
    decision_makers: List[str]
    communication_preferences: Dict[str, Any]
    timezone: str
    relationship_stage: str
    services_engaged: List[str]

@dataclass
class MeetingContext:
    meeting_type: CommunicationType
    participants: List[str]
    duration: int
    agenda_items: List[str]
    preparation_materials: List[str]
    success_criteria: List[str]
    follow_up_actions: List[str]

class ClientCommunicationManager(BaseAgent):
    """
    Client Communication Manager Agent
    
    Capabilities:
    - Meeting scheduling and calendar coordination
    - Client call preparation and agenda creation
    - Real-time meeting participation and note-taking
    - Follow-up communication and action item tracking
    - Relationship stage management and progression
    - Multi-service coordination for complex clients
    - Crisis communication and issue resolution
    - Client satisfaction monitoring and improvement
    """
    
    def __init__(self):
        super().__init__(
            agent_name="client_communication_manager",
            agent_type="communication_specialist",
            model_name="gpt-4"
        )
        
        # Communication expertise database
        self.meeting_templates = {
            CommunicationType.INITIAL_CONSULTATION: {
                'duration': 60,
                'preparation_time': 30,
                'agenda_template': [
                    'Introductions and company overview',
                    'Current situation and challenges',
                    'Goals and success metrics',
                    'Budget and timeline discussion',
                    'Service overview and fit assessment',
                    'Next steps and proposal timeline'
                ],
                'materials_needed': ['Company research', 'Service overview deck', 'Pricing framework'],
                'success_metrics': ['Clear requirements gathered', 'Budget range confirmed', 'Timeline established'],
                'follow_up_timeline': '24 hours'
            },
            CommunicationType.STRATEGY_PRESENTATION: {
                'duration': 90,
                'preparation_time': 60,
                'agenda_template': [
                    'Executive summary recap',
                    'Market analysis and opportunities',
                    'Strategic recommendations',
                    'Implementation roadmap',
                    'Investment and ROI projections',
                    'Risk assessment and mitigation',
                    'Q&A and decision framework'
                ],
                'materials_needed': ['Strategy deck', 'Market research', 'Case studies', 'ROI calculator'],
                'success_metrics': ['Strategy approved', 'Budget confirmed', 'Timeline agreed'],
                'follow_up_timeline': '48 hours'
            },
            CommunicationType.PROGRESS_UPDATE: {
                'duration': 30,
                'preparation_time': 15,
                'agenda_template': [
                    'Performance metrics review',
                    'Recent optimizations and results',
                    'Upcoming initiatives',
                    'Budget and timeline status',
                    'Questions and concerns'
                ],
                'materials_needed': ['Performance dashboard', 'Metrics report', 'Optimization summary'],
                'success_metrics': ['Client satisfaction maintained', 'Issues addressed', 'Approval for next phase'],
                'follow_up_timeline': '24 hours'
            }
        }
        
        self.communication_preferences = {
            'executive_level': {
                'communication_style': 'High-level, results-focused, time-efficient',
                'preferred_formats': ['Executive summaries', 'Dashboard reviews', 'ROI reports'],
                'meeting_frequency': 'Monthly or quarterly',
                'response_expectations': 'Same-day for urgent, 24-48 hours standard'
            },
            'manager_level': {
                'communication_style': 'Detailed, collaborative, solution-oriented',
                'preferred_formats': ['Detailed reports', 'Strategy discussions', 'Implementation planning'],
                'meeting_frequency': 'Bi-weekly or monthly',
                'response_expectations': '24 hours for urgent, 2-3 days standard'
            },
            'technical_level': {
                'communication_style': 'Technical, detailed, implementation-focused',
                'preferred_formats': ['Technical specifications', 'Implementation guides', 'Troubleshooting'],
                'meeting_frequency': 'Weekly during implementation, monthly maintenance',
                'response_expectations': '4-8 hours for technical issues, 24 hours standard'
            }
        }
        
        self.relationship_stages = {
            'prospect': {
                'communication_goals': ['Build trust', 'Understand needs', 'Demonstrate value'],
                'key_activities': ['Discovery calls', 'Proposal presentation', 'Reference calls'],
                'success_metrics': ['Engagement level', 'Response rate', 'Proposal acceptance'],
                'escalation_triggers': ['No response for 1 week', 'Budget concerns', 'Competitor evaluation']
            },
            'onboarding': {
                'communication_goals': ['Ensure smooth setup', 'Set expectations', 'Build confidence'],
                'key_activities': ['Kickoff meeting', 'Setup walkthroughs', 'Initial training'],
                'success_metrics': ['Onboarding completion', 'Team adoption', 'Early wins'],
                'escalation_triggers': ['Setup delays', 'Stakeholder concerns', 'Scope creep']
            },
            'active_delivery': {
                'communication_goals': ['Maintain satisfaction', 'Drive results', 'Identify opportunities'],
                'key_activities': ['Regular reviews', 'Performance discussions', 'Optimization planning'],
                'success_metrics': ['Performance targets', 'Client satisfaction', 'Service adoption'],
                'escalation_triggers': ['Performance issues', 'Budget concerns', 'Team changes']
            },
            'expansion': {
                'communication_goals': ['Identify new opportunities', 'Deepen relationship', 'Increase investment'],
                'key_activities': ['Strategic planning', 'Service expansion discussions', 'Executive presentations'],
                'success_metrics': ['Additional services', 'Budget increases', 'Referrals'],
                'escalation_triggers': ['Competitor threats', 'Budget cuts', 'Strategy changes']
            }
        }
        
        print(f"✓ Client Communication Manager initialized with {len(self.meeting_templates)} meeting types")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process client communication request
        
        Args:
            input_data: {
                'action': 'schedule_meeting' | 'prepare_meeting' | 'conduct_meeting' | 'follow_up' | 'manage_relationship',
                'client_profile': dict,
                'meeting_context': dict,
                'communication_history': list,
                'urgency_level': str
            }
        """
        try:
            action = input_data.get('action', 'schedule_meeting')
            
            if action == 'schedule_meeting':
                return self._schedule_client_meeting(input_data)
            elif action == 'prepare_meeting':
                return self._prepare_meeting_materials(input_data)
            elif action == 'conduct_meeting':
                return self._facilitate_client_meeting(input_data)
            elif action == 'follow_up':
                return self._manage_follow_up_communication(input_data)
            elif action == 'manage_relationship':
                return self._manage_client_relationship(input_data)
            elif action == 'escalate_issue':
                return self._handle_escalation(input_data)
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            self.logger.error(f"Client communication processing error: {e}")
            return {'success': False, 'error': str(e)}

    def _schedule_client_meeting(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule and coordinate client meetings"""
        try:
            client_profile = self._parse_client_profile(input_data.get('client_profile', {}))
            meeting_type = CommunicationType(input_data.get('meeting_type', 'initial_consultation'))
            urgency = input_data.get('urgency_level', 'normal')
            
            # Get meeting template
            meeting_template = self.meeting_templates.get(meeting_type, {})
            
            # Determine optimal scheduling
            scheduling_options = self._generate_scheduling_options(client_profile, meeting_template, urgency)
            
            # Create meeting agenda
            meeting_agenda = self._create_meeting_agenda(client_profile, meeting_type, meeting_template)
            
            # Prepare attendee list
            attendee_recommendations = self._recommend_attendees(client_profile, meeting_type)
            
            # Generate meeting materials checklist
            materials_checklist = self._create_materials_checklist(client_profile, meeting_type, meeting_template)
            
            # Setup meeting logistics
            meeting_logistics = self._setup_meeting_logistics(client_profile, meeting_template)
            
            return {
                'success': True,
                'meeting_details': {
                    'meeting_type': meeting_type.value,
                    'recommended_duration': meeting_template.get('duration', 60),
                    'preparation_time_needed': meeting_template.get('preparation_time', 30),
                    'optimal_timeframes': scheduling_options.get('optimal_timeframes'),
                    'timezone_considerations': scheduling_options.get('timezone_considerations')
                },
                'scheduling_options': scheduling_options,
                'meeting_agenda': meeting_agenda,
                'attendee_recommendations': attendee_recommendations,
                'materials_checklist': materials_checklist,
                'meeting_logistics': meeting_logistics,
                'preparation_timeline': self._create_preparation_timeline(meeting_template),
                'success_criteria': meeting_template.get('success_metrics', []),
                'follow_up_requirements': self._define_follow_up_requirements(meeting_type)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Meeting scheduling failed: {str(e)}'}

    def _prepare_meeting_materials(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare comprehensive meeting materials and talking points"""
        try:
            client_profile = self._parse_client_profile(input_data.get('client_profile', {}))
            meeting_context = input_data.get('meeting_context', {})
            expert_insights = input_data.get('expert_insights', {})
            
            meeting_type = CommunicationType(meeting_context.get('meeting_type', 'progress_update'))
            
            # Generate talking points
            talking_points = self._generate_talking_points(client_profile, meeting_type, expert_insights)
            
            # Prepare presentation materials
            presentation_materials = self._prepare_presentation_materials(client_profile, meeting_type, expert_insights)
            
            # Create supporting documents
            supporting_documents = self._create_supporting_documents(client_profile, meeting_type, expert_insights)
            
            # Anticipate questions and prepare responses
            qa_preparation = self._prepare_qa_responses(client_profile, meeting_type, expert_insights)
            
            # Setup interactive elements
            interactive_elements = self._setup_interactive_elements(meeting_type, expert_insights)
            
            # Create meeting flow
            meeting_flow = self._create_meeting_flow(meeting_type, talking_points, interactive_elements)
            
            return {
                'success': True,
                'preparation_overview': {
                    'meeting_type': meeting_type.value,
                    'client': client_profile.company,
                    'total_materials': len(presentation_materials) + len(supporting_documents),
                    'key_messages': len(talking_points.get('key_messages', [])),
                    'anticipated_questions': len(qa_preparation.get('prepared_responses', []))
                },
                'talking_points': talking_points,
                'presentation_materials': presentation_materials,
                'supporting_documents': supporting_documents,
                'qa_preparation': qa_preparation,
                'interactive_elements': interactive_elements,
                'meeting_flow': meeting_flow,
                'contingency_plans': self._create_contingency_plans(meeting_type, client_profile),
                'success_optimization': self._optimize_for_success(client_profile, meeting_type)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Meeting preparation failed: {str(e)}'}

    def _facilitate_client_meeting(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide real-time meeting facilitation support"""
        try:
            meeting_context = input_data.get('meeting_context', {})
            real_time_notes = input_data.get('real_time_notes', [])
            client_reactions = input_data.get('client_reactions', {})
            
            # Process real-time meeting dynamics
            meeting_dynamics = self._analyze_meeting_dynamics(real_time_notes, client_reactions)
            
            # Generate real-time recommendations
            real_time_recommendations = self._generate_real_time_recommendations(meeting_dynamics)
            
            # Track agenda progress
            agenda_progress = self._track_agenda_progress(meeting_context, real_time_notes)
            
            # Identify action items
            action_items = self._identify_action_items(real_time_notes)
            
            # Monitor success criteria
            success_tracking = self._monitor_success_criteria(meeting_context, client_reactions)
            
            # Generate meeting summary
            meeting_summary = self._generate_meeting_summary(meeting_context, real_time_notes, action_items)
            
            return {
                'success': True,
                'meeting_facilitation': {
                    'meeting_status': agenda_progress.get('overall_status'),
                    'client_engagement_level': meeting_dynamics.get('engagement_score'),
                    'objectives_met': success_tracking.get('objectives_achieved'),
                    'time_management': agenda_progress.get('time_tracking')
                },
                'real_time_recommendations': real_time_recommendations,
                'meeting_dynamics': meeting_dynamics,
                'agenda_progress': agenda_progress,
                'action_items': action_items,
                'success_tracking': success_tracking,
                'meeting_summary': meeting_summary,
                'next_steps': self._determine_next_steps(action_items, success_tracking),
                'relationship_impact': self._assess_relationship_impact(client_reactions, success_tracking)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Meeting facilitation failed: {str(e)}'}

    def _manage_follow_up_communication(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage comprehensive follow-up communication"""
        try:
            meeting_summary = input_data.get('meeting_summary', {})
            action_items = input_data.get('action_items', [])
            client_profile = self._parse_client_profile(input_data.get('client_profile', {}))
            
            # Create follow-up timeline
            follow_up_timeline = self._create_follow_up_timeline(action_items, client_profile)
            
            # Generate follow-up communications
            follow_up_communications = self._generate_follow_up_communications(
                meeting_summary, action_items, client_profile
            )
            
            # Setup tracking and reminders
            tracking_system = self._setup_follow_up_tracking(action_items, follow_up_timeline)
            
            # Monitor client satisfaction
            satisfaction_monitoring = self._setup_satisfaction_monitoring(client_profile, meeting_summary)
            
            # Plan next engagement
            next_engagement = self._plan_next_engagement(client_profile, meeting_summary)
            
            return {
                'success': True,
                'follow_up_overview': {
                    'total_action_items': len(action_items),
                    'immediate_actions': len([item for item in action_items if item.get('urgency') == 'high']),
                    'follow_up_communications': len(follow_up_communications),
                    'next_meeting_recommended': next_engagement.get('recommended_timeframe')
                },
                'follow_up_timeline': follow_up_timeline,
                'follow_up_communications': follow_up_communications,
                'tracking_system': tracking_system,
                'satisfaction_monitoring': satisfaction_monitoring,
                'next_engagement': next_engagement,
                'relationship_maintenance': self._plan_relationship_maintenance(client_profile),
                'escalation_protocols': self._setup_escalation_protocols(action_items, client_profile)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Follow-up management failed: {str(e)}'}

    def _manage_client_relationship(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage overall client relationship and progression"""
        try:
            client_profile = self._parse_client_profile(input_data.get('client_profile', {}))
            communication_history = input_data.get('communication_history', [])
            performance_data = input_data.get('performance_data', {})
            
            # Assess relationship health
            relationship_health = self._assess_relationship_health(client_profile, communication_history, performance_data)
            
            # Identify relationship opportunities
            relationship_opportunities = self._identify_relationship_opportunities(client_profile, performance_data)
            
            # Plan relationship development
            relationship_development = self._plan_relationship_development(client_profile, relationship_health)
            
            # Setup proactive communication
            proactive_communication = self._setup_proactive_communication(client_profile, relationship_opportunities)
            
            # Monitor relationship risks
            risk_monitoring = self._monitor_relationship_risks(client_profile, communication_history)
            
            return {
                'success': True,
                'relationship_overview': {
                    'client': client_profile.company,
                    'relationship_stage': client_profile.relationship_stage,
                    'health_score': relationship_health.get('overall_score'),
                    'satisfaction_level': relationship_health.get('satisfaction_level'),
                    'growth_potential': relationship_opportunities.get('growth_potential')
                },
                'relationship_health': relationship_health,
                'relationship_opportunities': relationship_opportunities,
                'relationship_development': relationship_development,
                'proactive_communication': proactive_communication,
                'risk_monitoring': risk_monitoring,
                'success_strategies': self._recommend_success_strategies(client_profile, relationship_health),
                'escalation_prevention': self._plan_escalation_prevention(risk_monitoring)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Relationship management failed: {str(e)}'}

    # Helper methods for client communication
    def _parse_client_profile(self, profile_data: Dict[str, Any]) -> ClientProfile:
        """Parse client profile data into structured format"""
        return ClientProfile(
            client_id=profile_data.get('client_id', 'unknown'),
            company=profile_data.get('company', 'Unknown Company'),
            primary_contact=profile_data.get('primary_contact', 'Unknown Contact'),
            contact_details=profile_data.get('contact_details', {}),
            industry=profile_data.get('industry', 'General'),
            company_size=profile_data.get('company_size', 'Unknown'),
            decision_makers=profile_data.get('decision_makers', []),
            communication_preferences=profile_data.get('communication_preferences', {}),
            timezone=profile_data.get('timezone', 'UTC'),
            relationship_stage=profile_data.get('relationship_stage', 'prospect'),
            services_engaged=profile_data.get('services_engaged', [])
        )

    def _generate_scheduling_options(self, client_profile: ClientProfile, meeting_template: Dict, urgency: str) -> Dict[str, Any]:
        """Generate optimal scheduling options for client meetings"""
        
        # Base scheduling logic
        base_duration = meeting_template.get('duration', 60)
        preparation_time = meeting_template.get('preparation_time', 30)
        
        # Adjust for urgency
        urgency_adjustments = {
            'urgent': {'max_wait_days': 1, 'extend_hours': True},
            'high': {'max_wait_days': 3, 'extend_hours': True},
            'normal': {'max_wait_days': 7, 'extend_hours': False},
            'low': {'max_wait_days': 14, 'extend_hours': False}
        }
        
        adjustment = urgency_adjustments.get(urgency, urgency_adjustments['normal'])
        
        return {
            'optimal_timeframes': self._calculate_optimal_timeframes(client_profile, adjustment),
            'timezone_considerations': self._handle_timezone_coordination(client_profile),
            'preparation_requirements': {
                'minimum_prep_time': f"{preparation_time} minutes",
                'materials_needed': meeting_template.get('materials_needed', []),
                'team_coordination': self._identify_team_coordination_needs(meeting_template)
            },
            'scheduling_constraints': {
                'max_wait_time': f"{adjustment['max_wait_days']} days",
                'extended_hours_ok': adjustment['extend_hours'],
                'preferred_duration': f"{base_duration} minutes"
            }
        }

    def _create_meeting_agenda(self, client_profile: ClientProfile, meeting_type: CommunicationType, meeting_template: Dict) -> Dict[str, Any]:
        """Create customized meeting agenda"""
        
        base_agenda = meeting_template.get('agenda_template', [])
        
        return {
            'meeting_objective': self._define_meeting_objective(meeting_type, client_profile),
            'agenda_items': [
                {
                    'item': item,
                    'estimated_time': self._estimate_agenda_item_time(item, meeting_template),
                    'key_points': self._generate_key_points_for_item(item, client_profile),
                    'materials_needed': self._identify_materials_for_item(item, meeting_template)
                }
                for item in base_agenda
            ],
            'buffer_time': '10 minutes for overrun and additional questions',
            'success_criteria': meeting_template.get('success_metrics', []),
            'client_preparation': self._recommend_client_preparation(meeting_type, client_profile)
        }

    # Additional helper methods would continue here...

if __name__ == "__main__":
    print("\n" + "="*80)
    print("Testing Client Communication Manager Agent")
    print("="*80)
    
    manager = ClientCommunicationManager()
    
    # Test meeting scheduling
    result = manager.process({
        'action': 'schedule_meeting',
        'meeting_type': 'initial_consultation',
        'urgency_level': 'normal',
        'client_profile': {
            'client_id': 'client_001',
            'company': 'TechFlow Solutions',
            'primary_contact': 'Sarah Chen',
            'contact_details': {
                'email': 'sarah.chen@techflow.com',
                'phone': '+1-555-0123',
                'preferred_method': 'email'
            },
            'industry': 'SaaS',
            'company_size': '50-200 employees',
            'decision_makers': ['Sarah Chen (CEO)', 'Mike Rodriguez (CTO)', 'Lisa Wang (CMO)'],
            'communication_preferences': {
                'meeting_style': 'collaborative',
                'detail_level': 'high',
                'follow_up_preference': 'email_summary'
            },
            'timezone': 'America/Los_Angeles',
            'relationship_stage': 'prospect',
            'services_engaged': []
        }
    })
    
    print(f"✅ Meeting Scheduling: {result.get('success')}")
    if result.get('success'):
        print(f"   Meeting Type: {result.get('meeting_details', {}).get('meeting_type')}")
        print(f"   Duration: {result.get('meeting_details', {}).get('recommended_duration')} minutes")
        print(f"   Agenda Items: {len(result.get('meeting_agenda', {}).get('agenda_items', []))}")
        print(f"   Success Criteria: {len(result.get('success_criteria', []))}")
    
    print("\n" + "="*80)
    print("Client Communication Manager Tests Complete!")
    print("="*80)