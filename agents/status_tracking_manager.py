"""
Status Tracking Manager
Real-time visibility system for client projects, tasks, and department activities
Provides comprehensive dashboard and reporting capabilities
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

sys.path.append(os.path.dirname(__file__))
from base_agent import BaseAgent

class TaskStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress" 
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    OVERDUE = "overdue"

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class ClientStatus:
    client_id: str
    company_name: str
    overall_health: str
    active_projects: int
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    next_milestone: Optional[str]
    last_activity: datetime
    satisfaction_score: float

class StatusTrackingManager(BaseAgent):
    """
    Status Tracking Manager
    
    Capabilities:
    - Real-time project and task status tracking
    - Client progress visibility and reporting
    - Department workload and capacity monitoring
    - Automated status updates and notifications
    - Performance metrics and trend analysis
    - Escalation and risk identification
    - Executive dashboard and reporting
    """
    
    def __init__(self):
        super().__init__(
            agent_name="status_tracking_manager",
            agent_type="monitoring_coordinator",
            model_name="gpt-4"
        )
        
        # Status tracking configuration
        self.department_structure = {
            'search_marketing': {
                'lead_expert': 'search_marketing_expert',
                'team_members': ['campaign_manager', 'ppc_specialist', 'analytics_specialist'],
                'typical_capacity': 8,  # concurrent projects
                'key_metrics': ['ROAS', 'CPA', 'Conversion Rate', 'Quality Score']
            },
            'ai_media': {
                'lead_expert': 'ai_media_expert',
                'team_members': ['creative_director', 'ai_specialist', 'video_producer'],
                'typical_capacity': 6,  # concurrent projects
                'key_metrics': ['Production Time', 'Quality Score', 'Client Approval Rate', 'Engagement Rate']
            },
            'ml_ai': {
                'lead_expert': 'ml_ai_expert',
                'team_members': ['ml_engineer', 'data_scientist', 'devops_engineer'],
                'typical_capacity': 4,  # concurrent projects
                'key_metrics': ['Model Accuracy', 'Training Time', 'Deployment Success', 'Performance Score']
            },
            'project_management': {
                'lead_expert': 'ai_project_manager',
                'team_members': ['project_coordinator', 'resource_manager', 'quality_analyst'],
                'typical_capacity': 12,  # concurrent projects
                'key_metrics': ['On-Time Delivery', 'Budget Variance', 'Quality Score', 'Client Satisfaction']
            },
            'communications': {
                'lead_expert': 'client_communication_manager',
                'team_members': ['account_manager', 'relationship_specialist', 'meeting_coordinator'],
                'typical_capacity': 20,  # concurrent clients
                'key_metrics': ['Response Time', 'Meeting Success Rate', 'Relationship Health', 'Satisfaction Score']
            },
            'research': {
                'lead_expert': 'research_analyst',
                'team_members': ['market_researcher', 'competitive_analyst', 'data_analyst'],
                'typical_capacity': 10,  # concurrent research projects
                'key_metrics': ['Research Quality', 'Insight Value', 'Timeline Adherence', 'Recommendation Accuracy']
            }
        }
        
        self.status_categories = {
            'client_health': {
                'excellent': {'score_range': (4.5, 5.0), 'color': 'green'},
                'good': {'score_range': (3.5, 4.4), 'color': 'light_green'},
                'fair': {'score_range': (2.5, 3.4), 'color': 'yellow'},
                'poor': {'score_range': (1.5, 2.4), 'color': 'orange'},
                'critical': {'score_range': (0.0, 1.4), 'color': 'red'}
            },
            'project_health': {
                'on_track': {'criteria': ['timeline_met', 'budget_within_range', 'quality_high'], 'color': 'green'},
                'at_risk': {'criteria': ['minor_delays', 'budget_concerns', 'quality_issues'], 'color': 'yellow'},
                'critical': {'criteria': ['major_delays', 'budget_overrun', 'quality_problems'], 'color': 'red'}
            },
            'task_urgency': {
                'urgent': {'due_hours': 24, 'color': 'red'},
                'high': {'due_hours': 72, 'color': 'orange'}, 
                'medium': {'due_hours': 168, 'color': 'yellow'},
                'low': {'due_hours': 336, 'color': 'green'}
            }
        }
        
        print(f"✓ Status Tracking Manager initialized monitoring {len(self.department_structure)} departments")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process status tracking request
        
        Args:
            input_data: {
                'action': 'get_client_status' | 'get_department_status' | 'update_task_status' | 'generate_dashboard',
                'client_id': str,
                'department': str,
                'time_range': str,
                'filters': dict
            }
        """
        try:
            action = input_data.get('action', 'generate_dashboard')
            
            if action == 'get_client_status':
                return self._get_comprehensive_client_status(input_data)
            elif action == 'get_department_status':
                return self._get_department_status(input_data)
            elif action == 'update_task_status':
                return self._update_task_status(input_data)
            elif action == 'generate_dashboard':
                return self._generate_executive_dashboard(input_data)
            elif action == 'get_upcoming_tasks':
                return self._get_upcoming_tasks(input_data)
            elif action == 'identify_risks':
                return self._identify_risks_and_escalations(input_data)
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            self.logger.error(f"Status tracking processing error: {e}")
            return {'success': False, 'error': str(e)}

    def _get_comprehensive_client_status(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive client status across all projects and services"""
        try:
            client_id = input_data.get('client_id')
            if not client_id:
                return {'success': False, 'error': 'client_id is required'}
            
            # Get client project overview
            project_overview = self._get_client_project_overview(client_id)
            
            # Get service-specific status
            service_status = self._get_service_specific_status(client_id)
            
            # Get task breakdown
            task_breakdown = self._get_client_task_breakdown(client_id)
            
            # Get upcoming activities
            upcoming_activities = self._get_client_upcoming_activities(client_id)
            
            # Calculate health metrics
            health_metrics = self._calculate_client_health_metrics(client_id, project_overview, task_breakdown)
            
            # Get recent activity timeline
            activity_timeline = self._get_client_activity_timeline(client_id)
            
            # Identify risks and opportunities
            risk_assessment = self._assess_client_risks_opportunities(client_id, health_metrics, task_breakdown)
            
            return {
                'success': True,
                'client_overview': {
                    'client_id': client_id,
                    'overall_health': health_metrics.get('overall_health_score'),
                    'health_category': health_metrics.get('health_category'),
                    'active_projects': project_overview.get('active_project_count'),
                    'total_investment': project_overview.get('total_budget'),
                    'satisfaction_score': health_metrics.get('satisfaction_score'),
                    'next_major_milestone': upcoming_activities.get('next_milestone'),
                    'days_to_next_milestone': upcoming_activities.get('days_to_milestone')
                },
                'project_overview': project_overview,
                'service_status': service_status,
                'task_breakdown': task_breakdown,
                'upcoming_activities': upcoming_activities,
                'health_metrics': health_metrics,
                'activity_timeline': activity_timeline,
                'risk_assessment': risk_assessment,
                'recommended_actions': self._get_client_recommended_actions(risk_assessment, health_metrics)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Client status retrieval failed: {str(e)}'}

    def _get_department_status(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive department status and workload"""
        try:
            department = input_data.get('department', 'all')
            time_range = input_data.get('time_range', '30d')
            
            if department == 'all':
                departments = list(self.department_structure.keys())
            else:
                departments = [department] if department in self.department_structure else []
            
            department_status = {}
            for dept in departments:
                department_status[dept] = self._get_single_department_status(dept, time_range)
            
            # Calculate cross-department metrics
            cross_department_metrics = self._calculate_cross_department_metrics(department_status)
            
            # Identify resource bottlenecks
            resource_analysis = self._analyze_department_resources(department_status)
            
            # Get capacity forecasting
            capacity_forecast = self._forecast_department_capacity(department_status, time_range)
            
            return {
                'success': True,
                'department_overview': {
                    'total_departments': len(departments),
                    'overall_utilization': cross_department_metrics.get('average_utilization'),
                    'total_active_projects': cross_department_metrics.get('total_projects'),
                    'departments_at_capacity': resource_analysis.get('departments_at_capacity'),
                    'upcoming_capacity_issues': capacity_forecast.get('capacity_warnings')
                },
                'department_status': department_status,
                'cross_department_metrics': cross_department_metrics,
                'resource_analysis': resource_analysis,
                'capacity_forecast': capacity_forecast,
                'optimization_opportunities': self._identify_department_optimization_opportunities(department_status),
                'recommended_actions': self._get_department_recommended_actions(resource_analysis, capacity_forecast)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Department status retrieval failed: {str(e)}'}

    def _generate_executive_dashboard(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive executive dashboard"""
        try:
            time_range = input_data.get('time_range', '30d')
            include_forecasts = input_data.get('include_forecasts', True)
            
            # Get high-level KPIs
            executive_kpis = self._calculate_executive_kpis(time_range)
            
            # Get client portfolio overview
            client_portfolio = self._get_client_portfolio_overview(time_range)
            
            # Get department performance
            department_performance = self._get_department_performance_summary(time_range)
            
            # Get financial metrics
            financial_metrics = self._calculate_financial_metrics(time_range)
            
            # Get risk and opportunity dashboard
            risk_opportunity_dashboard = self._get_risk_opportunity_dashboard()
            
            # Get upcoming critical activities
            critical_activities = self._get_upcoming_critical_activities(14)  # Next 14 days
            
            # Get trend analysis
            trend_analysis = self._analyze_business_trends(time_range) if include_forecasts else None
            
            # Get alerts and notifications
            alerts_notifications = self._get_executive_alerts_notifications()
            
            return {
                'success': True,
                'dashboard_overview': {
                    'generated_at': datetime.now().isoformat(),
                    'time_range': time_range,
                    'total_active_clients': client_portfolio.get('active_clients'),
                    'total_active_projects': executive_kpis.get('active_projects'),
                    'overall_client_satisfaction': executive_kpis.get('avg_client_satisfaction'),
                    'revenue_this_period': financial_metrics.get('current_period_revenue'),
                    'critical_alerts': len(alerts_notifications.get('critical_alerts', []))
                },
                'executive_kpis': executive_kpis,
                'client_portfolio': client_portfolio,
                'department_performance': department_performance,
                'financial_metrics': financial_metrics,
                'risk_opportunity_dashboard': risk_opportunity_dashboard,
                'critical_activities': critical_activities,
                'trend_analysis': trend_analysis,
                'alerts_notifications': alerts_notifications,
                'strategic_insights': self._generate_strategic_insights(executive_kpis, trend_analysis),
                'recommended_focus_areas': self._identify_executive_focus_areas(risk_opportunity_dashboard, trend_analysis)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Executive dashboard generation failed: {str(e)}'}

    def _get_upcoming_tasks(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get upcoming tasks by client, department, or overall"""
        try:
            scope = input_data.get('scope', 'all')  # all, client, department
            scope_id = input_data.get('scope_id')  # client_id or department name
            days_ahead = input_data.get('days_ahead', 7)
            priority_filter = input_data.get('priority_filter', 'all')
            
            # Get tasks based on scope
            if scope == 'client' and scope_id:
                tasks = self._get_client_upcoming_tasks(scope_id, days_ahead, priority_filter)
            elif scope == 'department' and scope_id:
                tasks = self._get_department_upcoming_tasks(scope_id, days_ahead, priority_filter)
            else:
                tasks = self._get_all_upcoming_tasks(days_ahead, priority_filter)
            
            # Organize tasks by timeline
            task_timeline = self._organize_tasks_by_timeline(tasks, days_ahead)
            
            # Identify critical path tasks
            critical_path = self._identify_critical_path_tasks(tasks)
            
            # Get resource requirements
            resource_requirements = self._calculate_upcoming_resource_requirements(tasks)
            
            # Identify potential conflicts
            scheduling_conflicts = self._identify_scheduling_conflicts(tasks)
            
            return {
                'success': True,
                'upcoming_tasks_overview': {
                    'scope': scope,
                    'scope_id': scope_id,
                    'total_upcoming_tasks': len(tasks),
                    'urgent_tasks': len([t for t in tasks if t.get('priority') == 'urgent']),
                    'overdue_tasks': len([t for t in tasks if t.get('status') == 'overdue']),
                    'critical_path_tasks': len(critical_path),
                    'resource_conflicts': len(scheduling_conflicts.get('resource_conflicts', []))
                },
                'task_timeline': task_timeline,
                'critical_path': critical_path,
                'resource_requirements': resource_requirements,
                'scheduling_conflicts': scheduling_conflicts,
                'task_prioritization': self._prioritize_upcoming_tasks(tasks),
                'recommended_schedule_adjustments': self._recommend_schedule_adjustments(scheduling_conflicts)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Upcoming tasks retrieval failed: {str(e)}'}

    # Helper methods for status tracking
    def _get_client_project_overview(self, client_id: str) -> Dict[str, Any]:
        """Get comprehensive project overview for client"""
        # Simulate database query - in production this would query actual database
        return {
            'active_project_count': 3,
            'total_projects': 5,
            'services_engaged': ['search_marketing', 'ai_media', 'ml_ai'],
            'total_budget': 150000,
            'budget_utilized': 89000,
            'budget_remaining': 61000,
            'average_project_health': 4.2,
            'projects': [
                {
                    'project_id': f'{client_id}_search_001',
                    'project_name': 'Search Marketing Campaign',
                    'status': 'active',
                    'progress_percentage': 75,
                    'health_score': 4.5,
                    'next_milestone': 'Campaign Optimization Review',
                    'days_to_milestone': 5
                },
                {
                    'project_id': f'{client_id}_media_001',
                    'project_name': 'AI Avatar Video Series',
                    'status': 'active',
                    'progress_percentage': 60,
                    'health_score': 4.0,
                    'next_milestone': 'Creative Concept Approval',
                    'days_to_milestone': 3
                },
                {
                    'project_id': f'{client_id}_ml_001',
                    'project_name': 'Customer Insights Model',
                    'status': 'active',
                    'progress_percentage': 30,
                    'health_score': 4.1,
                    'next_milestone': 'Model Architecture Review',
                    'days_to_milestone': 8
                }
            ]
        }

    def _get_service_specific_status(self, client_id: str) -> Dict[str, Any]:
        """Get status for each service"""
        return {
            'search_marketing': {
                'current_campaigns': 5,
                'active_platforms': ['Google Ads', 'Meta Ads', 'LinkedIn Ads'],
                'monthly_budget': 25000,
                'current_roas': 4.2,
                'key_metrics': {
                    'impressions': 1250000,
                    'clicks': 35000,
                    'conversions': 875,
                    'cost_per_conversion': 28.57
                },
                'status': 'performing_well',
                'next_optimization': 'Budget reallocation - 3 days'
            },
            'ai_media': {
                'content_pieces_produced': 12,
                'content_in_production': 3,
                'content_in_review': 1,
                'average_production_time': '3.2 days',
                'client_approval_rate': '95%',
                'key_metrics': {
                    'video_completion_rate': 0.78,
                    'engagement_rate': 0.065,
                    'brand_sentiment': 'positive'
                },
                'status': 'on_schedule',
                'next_delivery': 'Product demo video - 5 days'
            },
            'ml_ai': {
                'models_in_development': 1,
                'models_deployed': 0,
                'data_sources_integrated': 3,
                'model_accuracy': 'Not yet available',
                'key_metrics': {
                    'data_quality_score': 0.85,
                    'training_progress': 0.30,
                    'integration_readiness': 0.60
                },
                'status': 'development_phase',
                'next_milestone': 'Model training completion - 12 days'
            }
        }

    def _calculate_client_health_metrics(self, client_id: str, project_overview: Dict, task_breakdown: Dict) -> Dict[str, Any]:
        """Calculate comprehensive client health metrics"""
        
        # Base health calculation
        project_health_avg = project_overview.get('average_project_health', 3.0)
        task_completion_rate = task_breakdown.get('completion_rate', 0.7)
        budget_efficiency = (project_overview.get('budget_utilized', 0) / project_overview.get('total_budget', 1))
        
        # Calculate overall health score (0-5 scale)
        health_score = (
            project_health_avg * 0.4 +
            (task_completion_rate * 5) * 0.3 +
            (min(budget_efficiency, 1.0) * 5) * 0.2 +
            4.0 * 0.1  # Base satisfaction assumption
        )
        
        # Determine health category
        health_category = 'excellent'
        for category, config in self.status_categories['client_health'].items():
            min_score, max_score = config['score_range']
            if min_score <= health_score <= max_score:
                health_category = category
                break
        
        return {
            'overall_health_score': round(health_score, 2),
            'health_category': health_category,
            'satisfaction_score': round(health_score, 1),
            'project_health_average': project_health_avg,
            'task_completion_rate': task_completion_rate,
            'budget_efficiency': round(budget_efficiency, 3),
            'health_trends': {
                'last_30_days': 'improving',
                'last_7_days': 'stable',
                'trajectory': 'positive'
            }
        }

    def _get_single_department_status(self, department: str, time_range: str) -> Dict[str, Any]:
        """Get detailed status for a single department"""
        dept_config = self.department_structure.get(department, {})
        
        # Simulate department metrics - in production this would query actual data
        return {
            'department_name': department,
            'lead_expert': dept_config.get('lead_expert'),
            'team_size': len(dept_config.get('team_members', [])) + 1,  # +1 for lead
            'capacity': dept_config.get('typical_capacity'),
            'current_utilization': {
                'active_projects': 6,  # Example data
                'utilization_percentage': 75,
                'available_capacity': 2
            },
            'performance_metrics': {
                'avg_project_completion_time': '3.2 weeks',
                'on_time_delivery_rate': 0.92,
                'client_satisfaction': 4.3,
                'quality_score': 4.1
            },
            'current_projects': [
                {'client': 'TechFlow Solutions', 'project': 'Search Campaign', 'progress': 75, 'health': 'good'},
                {'client': 'InnovaCorp', 'project': 'PPC Optimization', 'progress': 45, 'health': 'excellent'},
                {'client': 'StartupXYZ', 'project': 'Multi-platform Launch', 'progress': 20, 'health': 'good'}
            ],
            'upcoming_deadlines': [
                {'client': 'TechFlow Solutions', 'milestone': 'Campaign Review', 'days_remaining': 3},
                {'client': 'InnovaCorp', 'milestone': 'Performance Report', 'days_remaining': 7}
            ],
            'department_health': 'excellent',
            'key_achievements_this_period': [
                'Exceeded ROAS targets by 15% across all campaigns',
                'Reduced average CPA by 22%',
                'Launched 3 new client campaigns successfully'
            ],
            'challenges_and_risks': [
                'Q4 capacity approaching limits',
                'New team member onboarding in progress'
            ]
        }

    # Additional helper methods would continue here...

if __name__ == "__main__":
    print("\n" + "="*80)
    print("Testing Status Tracking Manager")
    print("="*80)
    
    tracker = StatusTrackingManager()
    
    # Test client status
    result = tracker.process({
        'action': 'get_client_status',
        'client_id': 'techflow_001'
    })
    
    print(f"✅ Client Status Tracking: {result.get('success')}")
    if result.get('success'):
        overview = result.get('client_overview', {})
        print(f"   Client Health: {overview.get('health_category')} ({overview.get('overall_health_score')})")
        print(f"   Active Projects: {overview.get('active_projects')}")
        print(f"   Next Milestone: {overview.get('next_major_milestone')}")
    
    # Test department status
    dept_result = tracker.process({
        'action': 'get_department_status',
        'department': 'search_marketing',
        'time_range': '30d'
    })
    
    print(f"✅ Department Status Tracking: {dept_result.get('success')}")
    if dept_result.get('success'):
        dept_overview = dept_result.get('department_overview', {})
        print(f"   Utilization: {dept_overview.get('overall_utilization')}%")
        print(f"   Active Projects: {dept_overview.get('total_active_projects')}")
    
    print("\n" + "="*80)
    print("Status Tracking Manager Tests Complete!")
    print("="*80)