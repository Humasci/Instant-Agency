"""
AI Project Manager Agent
Senior project management specialist with expertise in AI/marketing project delivery
Handles project planning, coordination, tracking, and client delivery management
"""

import os
import sys
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

sys.path.append(os.path.dirname(__file__))
from base_agent import BaseAgent

class ProjectStatus(Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    AT_RISK = "at_risk"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"

@dataclass
class ProjectContext:
    project_id: str
    client_id: str
    project_name: str
    service_types: List[str]
    project_manager: str
    team_members: List[str]
    start_date: datetime
    target_completion: datetime
    budget: float
    priority: str
    status: ProjectStatus

@dataclass
class TaskItem:
    task_id: str
    title: str
    description: str
    assignee: str
    status: TaskStatus
    priority: str
    estimated_hours: float
    actual_hours: float
    dependencies: List[str]
    due_date: datetime
    completion_date: Optional[datetime]

class AIProjectManager(BaseAgent):
    """
    AI Project Manager Agent
    
    Capabilities:
    - Multi-service project planning and coordination
    - Resource allocation and team management
    - Timeline management and milestone tracking
    - Risk identification and mitigation
    - Quality assurance and deliverable management
    - Client communication and expectation management
    - Performance monitoring and reporting
    - Cross-functional team coordination
    """
    
    def __init__(self):
        super().__init__(
            agent_name="ai_project_manager",
            agent_type="project_coordinator",
            model_name="gpt-4"
        )
        
        # Project management expertise
        self.service_templates = {
            'search_marketing': {
                'typical_duration': 12,  # weeks
                'key_phases': ['Strategy', 'Setup', 'Launch', 'Optimization', 'Scaling'],
                'critical_dependencies': ['Account access', 'Tracking setup', 'Creative assets'],
                'team_roles': ['Search Strategist', 'Campaign Manager', 'Analyst'],
                'deliverables': ['Strategy document', 'Campaign setup', 'Performance reports'],
                'risk_factors': ['Platform changes', 'Competition', 'Budget constraints']
            },
            'generative_ai_media': {
                'typical_duration': 4,  # weeks
                'key_phases': ['Discovery', 'Concept', 'Production', 'Review', 'Delivery'],
                'critical_dependencies': ['Brand assets', 'Content approval', 'Technical specs'],
                'team_roles': ['Creative Director', 'AI Specialist', 'Producer'],
                'deliverables': ['Creative brief', 'Content assets', 'Usage guidelines'],
                'risk_factors': ['Creative approval', 'Technical limitations', 'Brand alignment']
            },
            'ml_model_tuning': {
                'typical_duration': 8,  # weeks
                'key_phases': ['Data Analysis', 'Model Design', 'Training', 'Testing', 'Deployment'],
                'critical_dependencies': ['Data access', 'Infrastructure', 'Model requirements'],
                'team_roles': ['ML Engineer', 'Data Scientist', 'DevOps Engineer'],
                'deliverables': ['Technical spec', 'Trained model', 'Deployment guide'],
                'risk_factors': ['Data quality', 'Model performance', 'Integration complexity']
            }
        }
        
        self.project_methodologies = {
            'agile': {
                'sprint_duration': 2,  # weeks
                'ceremonies': ['Sprint Planning', 'Daily Standups', 'Sprint Review', 'Retrospective'],
                'artifacts': ['Product Backlog', 'Sprint Backlog', 'Burndown Charts'],
                'roles': ['Product Owner', 'Scrum Master', 'Development Team'],
                'best_for': ['Iterative projects', 'Evolving requirements', 'Quick feedback cycles']
            },
            'waterfall': {
                'phase_gates': ['Requirements', 'Design', 'Implementation', 'Testing', 'Deployment'],
                'documentation': ['Project Charter', 'Requirements Doc', 'Design Specs', 'Test Plans'],
                'approvals': ['Phase gate reviews', 'Stakeholder signoffs', 'Quality gates'],
                'best_for': ['Fixed scope', 'Regulated environments', 'Predictable outcomes']
            },
            'hybrid': {
                'combines': ['Agile execution', 'Waterfall planning'],
                'planning_horizon': '3-6 months',
                'execution_cycles': '2-4 week sprints',
                'best_for': ['Complex projects', 'Multiple stakeholders', 'Mixed requirements']
            }
        }
        
        self.risk_categories = {
            'technical': {
                'common_risks': ['Integration challenges', 'Performance issues', 'Data quality', 'Platform limitations'],
                'mitigation_strategies': ['Proof of concepts', 'Technical reviews', 'Fallback plans', 'Expert consultation'],
                'monitoring_indicators': ['Technical debt', 'Bug rates', 'Performance metrics', 'System stability']
            },
            'resource': {
                'common_risks': ['Team availability', 'Skill gaps', 'Budget overruns', 'Vendor dependencies'],
                'mitigation_strategies': ['Resource planning', 'Cross-training', 'Budget buffers', 'Vendor SLAs'],
                'monitoring_indicators': ['Utilization rates', 'Skill assessments', 'Budget variance', 'Vendor performance']
            },
            'business': {
                'common_risks': ['Scope creep', 'Stakeholder changes', 'Market shifts', 'Regulatory changes'],
                'mitigation_strategies': ['Change control', 'Stakeholder management', 'Market monitoring', 'Compliance tracking'],
                'monitoring_indicators': ['Scope variance', 'Stakeholder satisfaction', 'Market indicators', 'Regulatory updates']
            }
        }
        
        print(f"✓ AI Project Manager initialized with {len(self.service_templates)} service templates")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process project management request
        
        Args:
            input_data: {
                'action': 'plan_project' | 'track_progress' | 'manage_resources' | 'handle_escalation' | 'coordinate_delivery',
                'project_context': dict,
                'project_requirements': dict,
                'team_status': dict,
                'client_feedback': dict
            }
        """
        try:
            action = input_data.get('action', 'plan_project')
            
            if action == 'plan_project':
                return self._plan_comprehensive_project(input_data)
            elif action == 'track_progress':
                return self._track_project_progress(input_data)
            elif action == 'manage_resources':
                return self._manage_project_resources(input_data)
            elif action == 'handle_escalation':
                return self._handle_project_escalation(input_data)
            elif action == 'coordinate_delivery':
                return self._coordinate_project_delivery(input_data)
            elif action == 'assess_risks':
                return self._assess_project_risks(input_data)
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            self.logger.error(f"Project management processing error: {e}")
            return {'success': False, 'error': str(e)}

    def _plan_comprehensive_project(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Plan comprehensive multi-service project"""
        try:
            project_requirements = input_data.get('project_requirements', {})
            client_context = input_data.get('client_context', {})
            service_scopes = input_data.get('service_scopes', {})
            
            # Create project charter
            project_charter = self._create_project_charter(project_requirements, client_context)
            
            # Design project structure
            project_structure = self._design_project_structure(service_scopes, project_requirements)
            
            # Create work breakdown structure
            work_breakdown = self._create_work_breakdown_structure(service_scopes, project_structure)
            
            # Develop project timeline
            project_timeline = self._develop_project_timeline(work_breakdown, project_requirements)
            
            # Plan resource allocation
            resource_allocation = self._plan_resource_allocation(work_breakdown, project_timeline)
            
            # Identify dependencies and constraints
            dependencies_analysis = self._analyze_dependencies_and_constraints(work_breakdown, service_scopes)
            
            # Assess risks and mitigation
            risk_assessment = self._assess_comprehensive_risks(project_requirements, service_scopes)
            
            # Setup communication plan
            communication_plan = self._create_communication_plan(client_context, project_structure)
            
            # Define quality assurance
            quality_assurance = self._design_quality_assurance_framework(service_scopes, project_requirements)
            
            return {
                'success': True,
                'project_overview': {
                    'project_name': project_charter.get('project_name'),
                    'total_duration': project_timeline.get('total_duration_weeks'),
                    'team_size': resource_allocation.get('total_team_members'),
                    'service_count': len(service_scopes),
                    'complexity_rating': self._rate_project_complexity(work_breakdown, dependencies_analysis),
                    'success_probability': self._calculate_success_probability(risk_assessment, resource_allocation)
                },
                'project_charter': project_charter,
                'project_structure': project_structure,
                'work_breakdown': work_breakdown,
                'project_timeline': project_timeline,
                'resource_allocation': resource_allocation,
                'dependencies_analysis': dependencies_analysis,
                'risk_assessment': risk_assessment,
                'communication_plan': communication_plan,
                'quality_assurance': quality_assurance,
                'success_metrics': self._define_project_success_metrics(project_requirements, service_scopes),
                'governance_framework': self._establish_governance_framework(client_context, project_structure)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Project planning failed: {str(e)}'}

    def _track_project_progress(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track comprehensive project progress across all services"""
        try:
            project_context = input_data.get('project_context', {})
            current_status = input_data.get('current_status', {})
            team_updates = input_data.get('team_updates', {})
            
            # Analyze overall progress
            progress_analysis = self._analyze_overall_progress(project_context, current_status, team_updates)
            
            # Track milestone completion
            milestone_tracking = self._track_milestone_completion(project_context, current_status)
            
            # Monitor resource utilization
            resource_monitoring = self._monitor_resource_utilization(project_context, team_updates)
            
            # Identify blockers and issues
            blocker_analysis = self._identify_blockers_and_issues(current_status, team_updates)
            
            # Assess timeline impact
            timeline_analysis = self._assess_timeline_impact(progress_analysis, blocker_analysis)
            
            # Generate status reports
            status_reports = self._generate_comprehensive_status_reports(
                progress_analysis, milestone_tracking, resource_monitoring, blocker_analysis
            )
            
            # Recommend corrective actions
            corrective_actions = self._recommend_corrective_actions(blocker_analysis, timeline_analysis)
            
            # Update stakeholder communications
            stakeholder_updates = self._prepare_stakeholder_updates(
                status_reports, timeline_analysis, corrective_actions
            )
            
            return {
                'success': True,
                'progress_overview': {
                    'overall_completion': progress_analysis.get('overall_percentage'),
                    'on_track_status': timeline_analysis.get('on_track_status'),
                    'active_blockers': len(blocker_analysis.get('critical_blockers', [])),
                    'team_utilization': resource_monitoring.get('average_utilization'),
                    'next_milestone': milestone_tracking.get('next_milestone')
                },
                'progress_analysis': progress_analysis,
                'milestone_tracking': milestone_tracking,
                'resource_monitoring': resource_monitoring,
                'blocker_analysis': blocker_analysis,
                'timeline_analysis': timeline_analysis,
                'status_reports': status_reports,
                'corrective_actions': corrective_actions,
                'stakeholder_updates': stakeholder_updates,
                'trend_analysis': self._analyze_progress_trends(progress_analysis, timeline_analysis),
                'predictive_insights': self._generate_predictive_insights(progress_analysis, resource_monitoring)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Progress tracking failed: {str(e)}'}

    def _coordinate_project_delivery(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate comprehensive project delivery across all services"""
        try:
            project_context = input_data.get('project_context', {})
            deliverable_status = input_data.get('deliverable_status', {})
            quality_metrics = input_data.get('quality_metrics', {})
            
            # Assess delivery readiness
            delivery_readiness = self._assess_delivery_readiness(project_context, deliverable_status, quality_metrics)
            
            # Coordinate cross-service dependencies
            dependency_coordination = self._coordinate_cross_service_dependencies(project_context, deliverable_status)
            
            # Manage quality assurance
            quality_management = self._manage_comprehensive_quality_assurance(deliverable_status, quality_metrics)
            
            # Prepare client handover
            client_handover = self._prepare_client_handover(project_context, deliverable_status)
            
            # Setup post-delivery support
            post_delivery_support = self._setup_post_delivery_support(project_context, client_handover)
            
            # Document lessons learned
            lessons_learned = self._document_lessons_learned(project_context, deliverable_status)
            
            # Plan project closure
            project_closure = self._plan_project_closure(project_context, client_handover)
            
            return {
                'success': True,
                'delivery_overview': {
                    'delivery_readiness_score': delivery_readiness.get('readiness_score'),
                    'quality_gate_status': quality_management.get('overall_quality_status'),
                    'client_satisfaction_prediction': client_handover.get('satisfaction_prediction'),
                    'on_time_delivery_probability': delivery_readiness.get('on_time_probability'),
                    'post_delivery_plan_ready': bool(post_delivery_support)
                },
                'delivery_readiness': delivery_readiness,
                'dependency_coordination': dependency_coordination,
                'quality_management': quality_management,
                'client_handover': client_handover,
                'post_delivery_support': post_delivery_support,
                'lessons_learned': lessons_learned,
                'project_closure': project_closure,
                'success_celebration': self._plan_success_celebration(project_context, quality_management),
                'continuous_improvement': self._identify_continuous_improvement_opportunities(lessons_learned)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Project delivery coordination failed: {str(e)}'}

    def _create_project_charter(self, requirements: Dict[str, Any], client_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive project charter"""
        
        return {
            'project_identification': {
                'project_name': requirements.get('project_name', 'Multi-Service AI Marketing Project'),
                'project_code': f"SIX3-{datetime.now().strftime('%Y%m%d')}-{client_context.get('client_id', 'UNKNOWN')[:4].upper()}",
                'client': client_context.get('company_name', 'Unknown Client'),
                'project_manager': 'AI Project Manager',
                'sponsor': client_context.get('primary_contact', 'Client Sponsor'),
                'start_date': datetime.now().isoformat(),
                'target_end_date': (datetime.now() + timedelta(weeks=16)).isoformat()
            },
            'project_purpose': {
                'business_case': self._define_business_case(requirements, client_context),
                'objectives': requirements.get('objectives', []),
                'success_criteria': requirements.get('success_metrics', []),
                'deliverables': self._identify_high_level_deliverables(requirements),
                'assumptions': self._document_key_assumptions(requirements, client_context),
                'constraints': self._identify_project_constraints(requirements, client_context)
            },
            'scope_definition': {
                'in_scope': self._define_in_scope_items(requirements),
                'out_of_scope': self._define_out_of_scope_items(requirements),
                'boundaries': self._establish_project_boundaries(requirements, client_context),
                'interfaces': self._identify_external_interfaces(client_context)
            },
            'stakeholder_analysis': {
                'primary_stakeholders': self._identify_primary_stakeholders(client_context),
                'secondary_stakeholders': self._identify_secondary_stakeholders(client_context),
                'influence_impact_matrix': self._create_influence_impact_matrix(client_context),
                'communication_requirements': self._define_stakeholder_communication_needs(client_context)
            },
            'authorization': {
                'approval_authority': client_context.get('decision_maker', 'Client Executive'),
                'budget_authority': requirements.get('budget_range', 'TBD'),
                'change_control_authority': 'Project Steering Committee',
                'escalation_path': self._define_escalation_path(client_context)
            }
        }

    def _design_project_structure(self, service_scopes: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Design optimal project structure for multi-service delivery"""
        
        services = list(service_scopes.keys())
        project_complexity = self._assess_structural_complexity(service_scopes, requirements)
        
        if project_complexity == 'high' or len(services) > 2:
            structure_type = 'matrix'
        elif len(services) == 1:
            structure_type = 'functional'
        else:
            structure_type = 'project'
        
        return {
            'structure_type': structure_type,
            'service_organization': {
                service: {
                    'lead': f"{service.replace('_', ' ').title()} Expert",
                    'team_size': self._estimate_team_size(service, service_scopes[service]),
                    'reporting_structure': self._define_reporting_structure(structure_type, service),
                    'coordination_needs': self._identify_coordination_needs(service, services)
                }
                for service in services
            },
            'integration_mechanisms': {
                'steering_committee': self._setup_steering_committee(requirements),
                'coordination_meetings': self._plan_coordination_meetings(services),
                'shared_deliverables': self._identify_shared_deliverables(service_scopes),
                'communication_protocols': self._establish_communication_protocols(structure_type)
            },
            'governance_structure': {
                'decision_making': self._define_decision_making_authority(structure_type),
                'escalation_procedures': self._establish_escalation_procedures(structure_type),
                'change_management': self._setup_change_management_process(structure_type),
                'quality_assurance': self._integrate_quality_assurance(structure_type)
            }
        }

    def _create_work_breakdown_structure(self, service_scopes: Dict[str, Any], project_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive work breakdown structure"""
        
        wbs = {
            'project_management': {
                'initiation': {
                    'tasks': [
                        'Project charter creation',
                        'Stakeholder identification',
                        'Initial risk assessment',
                        'Team assembly'
                    ],
                    'duration_weeks': 1,
                    'dependencies': [],
                    'resources': ['Project Manager', 'Business Analyst']
                },
                'planning': {
                    'tasks': [
                        'Detailed project planning',
                        'Resource allocation',
                        'Risk mitigation planning',
                        'Communication plan'
                    ],
                    'duration_weeks': 2,
                    'dependencies': ['initiation'],
                    'resources': ['Project Manager', 'Technical Leads']
                },
                'monitoring_control': {
                    'tasks': [
                        'Progress tracking',
                        'Quality monitoring',
                        'Risk management',
                        'Change control'
                    ],
                    'duration_weeks': 'ongoing',
                    'dependencies': ['planning'],
                    'resources': ['Project Manager', 'Quality Analyst']
                }
            },
            'service_delivery': {}
        }
        
        # Add service-specific work breakdown
        for service, scope in service_scopes.items():
            service_template = self.service_templates.get(service, {})
            
            wbs['service_delivery'][service] = {
                phase: {
                    'tasks': self._generate_phase_tasks(service, phase, scope),
                    'duration_weeks': self._estimate_phase_duration(service, phase),
                    'dependencies': self._identify_phase_dependencies(service, phase, service_scopes),
                    'resources': self._assign_phase_resources(service, phase),
                    'deliverables': self._define_phase_deliverables(service, phase, scope),
                    'quality_gates': self._establish_phase_quality_gates(service, phase)
                }
                for phase in service_template.get('key_phases', ['Planning', 'Execution', 'Delivery'])
            }
        
        return wbs

    # Helper methods for project management
    def _assess_structural_complexity(self, service_scopes: Dict[str, Any], requirements: Dict[str, Any]) -> str:
        """Assess structural complexity of multi-service project"""
        
        complexity_factors = {
            'service_count': len(service_scopes),
            'integration_needs': self._count_integration_points(service_scopes),
            'stakeholder_count': len(requirements.get('stakeholders', [])),
            'timeline_constraints': 1 if requirements.get('tight_timeline') else 0,
            'budget_constraints': 1 if requirements.get('budget_limited') else 0
        }
        
        complexity_score = (
            complexity_factors['service_count'] * 2 +
            complexity_factors['integration_needs'] * 3 +
            complexity_factors['stakeholder_count'] * 1 +
            complexity_factors['timeline_constraints'] * 2 +
            complexity_factors['budget_constraints'] * 1
        )
        
        if complexity_score > 15:
            return 'high'
        elif complexity_score > 8:
            return 'medium'
        else:
            return 'low'

    def _rate_project_complexity(self, work_breakdown: Dict, dependencies_analysis: Dict) -> str:
        """Rate overall project complexity"""
        
        factors = {
            'total_tasks': sum(len(phase.get('tasks', [])) for service in work_breakdown.get('service_delivery', {}).values() for phase in service.values()),
            'dependency_count': len(dependencies_analysis.get('critical_dependencies', [])),
            'resource_types': len(set(resource for service in work_breakdown.get('service_delivery', {}).values() for phase in service.values() for resource in phase.get('resources', []))),
            'integration_complexity': dependencies_analysis.get('integration_complexity_score', 0)
        }
        
        complexity_score = (
            min(factors['total_tasks'] / 10, 10) +
            min(factors['dependency_count'] / 5, 10) +
            min(factors['resource_types'] / 3, 10) +
            factors['integration_complexity']
        )
        
        if complexity_score > 25:
            return 'Very High'
        elif complexity_score > 20:
            return 'High'
        elif complexity_score > 15:
            return 'Medium'
        elif complexity_score > 10:
            return 'Low'
        else:
            return 'Very Low'

    # Additional helper methods would continue here...

if __name__ == "__main__":
    print("\n" + "="*80)
    print("Testing AI Project Manager Agent")
    print("="*80)
    
    manager = AIProjectManager()
    
    # Test project planning
    result = manager.process({
        'action': 'plan_project',
        'project_requirements': {
            'project_name': 'TechFlow Digital Transformation',
            'objectives': [
                'Increase qualified leads by 300%',
                'Establish thought leadership content',
                'Implement AI-driven customer insights'
            ],
            'success_metrics': [
                'Lead generation > 150/month',
                'Content engagement rate > 5%',
                'Customer insights accuracy > 85%'
            ],
            'timeline': '16 weeks',
            'budget_range': '$75,000-100,000'
        },
        'client_context': {
            'client_id': 'techflow_001',
            'company_name': 'TechFlow Solutions',
            'industry': 'SaaS',
            'company_size': '50-200 employees',
            'primary_contact': 'Sarah Chen',
            'decision_maker': 'Sarah Chen (CEO)',
            'stakeholders': ['Sarah Chen (CEO)', 'Mike Rodriguez (CTO)', 'Lisa Wang (CMO)']
        },
        'service_scopes': {
            'search_marketing': {
                'platforms': ['Google Ads', 'LinkedIn Ads'],
                'budget': 25000,
                'objectives': ['Lead generation', 'Brand awareness']
            },
            'generative_ai_media': {
                'content_types': ['Product demos', 'Thought leadership'],
                'deliverables': 5,
                'timeline': '6 weeks'
            },
            'ml_model_tuning': {
                'model_type': 'customer_insights',
                'data_sources': ['CRM', 'Website analytics'],
                'objectives': ['Segmentation', 'Propensity scoring']
            }
        }
    })
    
    print(f"✅ Project Planning: {result.get('success')}")
    if result.get('success'):
        print(f"   Project: {result.get('project_overview', {}).get('project_name')}")
        print(f"   Duration: {result.get('project_overview', {}).get('total_duration_weeks')} weeks")
        print(f"   Complexity: {result.get('project_overview', {}).get('complexity_rating')}")
        print(f"   Success Probability: {result.get('project_overview', {}).get('success_probability')}")
    
    print("\n" + "="*80)
    print("AI Project Manager Tests Complete!")
    print("="*80)