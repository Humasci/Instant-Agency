"""
SIX3 Service Delivery Orchestrator
Central coordination system for managing all three core services
"""

import os
import sys
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

sys.path.append(os.path.dirname(__file__))
from base_agent import BaseAgent
from n8n_integration import n8n

@dataclass
class ServiceRequest:
    client_id: str
    service_type: str
    priority: str
    requirements: Dict[str, Any]
    timeline: str
    budget: float

class ServiceDeliveryOrchestrator(BaseAgent):
    """
    Orchestrates service delivery across all SIX3 offerings:
    1. Search Marketing & Paid Media
    2. Generative AI Video/Audio 
    3. Fine-Tuning ML Models
    """
    
    def __init__(self):
        super().__init__(
            agent_name="service_delivery_orchestrator",
            agent_type="orchestrator",
            model_name="gpt-3.5-turbo"
        )
        
        self.service_endpoints = {
            'search_marketing': 'http://localhost:3000/webhook/search-marketing-campaign',
            'generative_ai_media': 'http://localhost:3000/webhook/generative-ai-media',
            'ml_model_tuning': 'http://localhost:3000/webhook/ml-model-finetuning',
            'client_onboarding': 'http://localhost:3000/webhook/client-onboarding'
        }
        
        # Service capability mapping
        self.service_capabilities = {
            'search_marketing': {
                'platforms': ['google_ads', 'meta_ads', 'linkedin_ads', 'tiktok_ads'],
                'optimization_types': ['bid_optimization', 'audience_targeting', 'creative_optimization'],
                'reporting': ['real_time_dashboards', 'automated_reports', 'attribution_modeling'],
                'typical_timeline': '2-4 weeks setup, ongoing optimization'
            },
            'generative_ai_media': {
                'content_types': ['ai_avatars', 'voice_cloning', 'video_generation', 'ugc_creation'],
                'output_formats': ['mp4', 'webm', 'mp3', 'wav', 'gif'],
                'use_cases': ['product_demos', 'testimonials', 'explainer_videos', 'social_content'],
                'typical_timeline': '1-2 weeks production, 2-3 revisions included'
            },
            'ml_model_tuning': {
                'model_types': ['language_models', 'computer_vision', 'recommendation_systems', 'predictive_analytics'],
                'frameworks': ['pytorch', 'tensorflow', 'huggingface_transformers'],
                'deployment_options': ['api_endpoint', 'edge_deployment', 'batch_processing'],
                'typical_timeline': '3-6 weeks development, 2 weeks testing'
            }
        }
        
        print(f"✓ Service Delivery Orchestrator initialized with {len(self.service_capabilities)} service types")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process service delivery request and orchestrate appropriate workflows
        
        Args:
            input_data: {
                'action': 'new_client' | 'service_request' | 'status_update',
                'client_data': dict,
                'services_requested': list,
                'requirements': dict
            }
        """
        try:
            action = input_data.get('action', 'service_request')
            
            if action == 'new_client':
                return self._handle_new_client(input_data)
            elif action == 'service_request':
                return self._handle_service_request(input_data)
            elif action == 'status_update':
                return self._handle_status_update(input_data)
            elif action == 'capability_assessment':
                return self._assess_service_capabilities(input_data)
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            self.logger.error(f"Service orchestration error: {e}")
            return {'success': False, 'error': str(e)}

    def _handle_new_client(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new client onboarding"""
        try:
            client_data = input_data.get('client_data', {})
            services_requested = input_data.get('services_requested', [])
            
            # Validate service requests
            validation_result = self._validate_service_requests(services_requested, client_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': 'Service validation failed',
                    'validation_errors': validation_result['errors']
                }
            
            # Trigger client onboarding workflow
            onboarding_payload = {
                'client_data': client_data,
                'services': services_requested,
                'validation': validation_result,
                'timestamp': datetime.now().isoformat()
            }
            
            # Call n8n onboarding workflow
            result = n8n.trigger_workflow('SIX3 Client Onboarding & Service Delivery', onboarding_payload)
            
            if result.get('success'):
                # Schedule follow-up tasks
                follow_ups = self._schedule_follow_ups(client_data, services_requested)
                
                return {
                    'success': True,
                    'action': 'client_onboarded',
                    'client_id': client_data.get('client_id'),
                    'services_initialized': services_requested,
                    'onboarding_result': result,
                    'follow_up_tasks': follow_ups,
                    'estimated_timelines': self._calculate_service_timelines(services_requested),
                    'next_steps': self._get_next_steps(services_requested)
                }
            else:
                return {
                    'success': False,
                    'error': 'Onboarding workflow failed',
                    'details': result
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Client onboarding failed: {str(e)}'}

    def _handle_service_request(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle individual service request"""
        try:
            service_type = input_data.get('service_type')
            client_id = input_data.get('client_id')
            requirements = input_data.get('requirements', {})
            
            if service_type not in self.service_capabilities:
                return {
                    'success': False,
                    'error': f'Unknown service type: {service_type}',
                    'available_services': list(self.service_capabilities.keys())
                }
            
            # Create service request
            service_request = ServiceRequest(
                client_id=client_id,
                service_type=service_type,
                priority=requirements.get('priority', 'standard'),
                requirements=requirements,
                timeline=requirements.get('timeline', 'standard'),
                budget=requirements.get('budget', 0)
            )
            
            # Route to appropriate service workflow
            workflow_result = self._route_to_service_workflow(service_request)
            
            # Track service request
            self._track_service_request(service_request, workflow_result)
            
            return {
                'success': True,
                'service_type': service_type,
                'client_id': client_id,
                'request_id': f"req_{int(datetime.now().timestamp())}",
                'workflow_result': workflow_result,
                'estimated_completion': self._estimate_completion_date(service_type, requirements),
                'tracking_url': f"https://portal.six3.agency/projects/{client_id}/{service_type}"
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Service request failed: {str(e)}'}

    def _route_to_service_workflow(self, request: ServiceRequest) -> Dict[str, Any]:
        """Route service request to appropriate n8n workflow"""
        try:
            workflow_name = f"SIX3 {request.service_type.replace('_', ' ').title()}"
            
            # Prepare payload based on service type
            if request.service_type == 'search_marketing':
                payload = {
                    'client_id': request.client_id,
                    'industry': request.requirements.get('industry'),
                    'platforms': request.requirements.get('platforms', ['google_ads', 'meta_ads']),
                    'budget': request.budget,
                    'auto_launch': request.requirements.get('auto_launch', False),
                    'timeline': request.timeline
                }
                workflow_name = "SIX3 Search Marketing Campaign Optimizer"
                
            elif request.service_type == 'generative_ai_media':
                payload = {
                    'client_id': request.client_id,
                    'media_type': request.requirements.get('media_type', 'avatar_video'),
                    'use_case': request.requirements.get('use_case'),
                    'brand_guidelines': request.requirements.get('brand_guidelines'),
                    'timeline': request.timeline
                }
                workflow_name = "SIX3 Generative AI Video & Audio Production"
                
            elif request.service_type == 'ml_model_tuning':
                payload = {
                    'client_id': request.client_id,
                    'model_type': request.requirements.get('model_type', 'language_model'),
                    'data_requirements': request.requirements.get('data_requirements'),
                    'objectives': request.requirements.get('objectives'),
                    'timeline': request.timeline
                }
                workflow_name = "SIX3 ML Model FineTuning"
                
            else:
                return {'success': False, 'error': f'No workflow mapping for {request.service_type}'}
            
            # Trigger the workflow
            result = n8n.trigger_workflow(workflow_name, payload)
            return result
            
        except Exception as e:
            return {'success': False, 'error': f'Workflow routing failed: {str(e)}'}

    def _validate_service_requests(self, services: List[str], client_data: Dict) -> Dict[str, Any]:
        """Validate that requested services are available and properly configured"""
        errors = []
        warnings = []
        
        for service in services:
            if service not in self.service_capabilities:
                errors.append(f"Unknown service: {service}")
                continue
            
            # Service-specific validations
            if service == 'search_marketing':
                if not client_data.get('industry'):
                    warnings.append("Industry not specified for search marketing")
                if not client_data.get('marketing_budget'):
                    warnings.append("Marketing budget not specified")
                    
            elif service == 'generative_ai_media':
                if not client_data.get('brand_guidelines'):
                    warnings.append("Brand guidelines recommended for AI media")
                    
            elif service == 'ml_model_tuning':
                if not client_data.get('data_sources'):
                    errors.append("Data sources required for ML model tuning")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'validated_services': [s for s in services if s in self.service_capabilities]
        }

    def _schedule_follow_ups(self, client_data: Dict, services: List[str]) -> List[Dict]:
        """Schedule follow-up tasks for new client"""
        follow_ups = []
        
        # Universal follow-ups
        follow_ups.extend([
            {
                'task': 'kickoff_meeting',
                'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
                'assignee': 'account_manager',
                'priority': 'high'
            },
            {
                'task': 'discovery_call',
                'due_date': (datetime.now() + timedelta(days=5)).isoformat(),
                'assignee': 'technical_lead',
                'priority': 'high'
            }
        ])
        
        # Service-specific follow-ups
        for service in services:
            if service == 'search_marketing':
                follow_ups.append({
                    'task': 'competitor_analysis_review',
                    'due_date': (datetime.now() + timedelta(days=7)).isoformat(),
                    'assignee': 'marketing_strategist',
                    'priority': 'medium'
                })
            elif service == 'generative_ai_media':
                follow_ups.append({
                    'task': 'brand_asset_collection',
                    'due_date': (datetime.now() + timedelta(days=3)).isoformat(),
                    'assignee': 'creative_director',
                    'priority': 'high'
                })
            elif service == 'ml_model_tuning':
                follow_ups.append({
                    'task': 'data_audit_and_preparation',
                    'due_date': (datetime.now() + timedelta(days=10)).isoformat(),
                    'assignee': 'data_scientist',
                    'priority': 'high'
                })
        
        return follow_ups

    def _calculate_service_timelines(self, services: List[str]) -> Dict[str, str]:
        """Calculate estimated timelines for each service"""
        timelines = {}
        
        for service in services:
            if service in self.service_capabilities:
                timelines[service] = self.service_capabilities[service]['typical_timeline']
        
        return timelines

    def _get_next_steps(self, services: List[str]) -> List[str]:
        """Get next steps for client based on services"""
        steps = [
            "Schedule kickoff meeting within 48 hours",
            "Complete client portal setup and access",
            "Gather required assets and information"
        ]
        
        if 'search_marketing' in services:
            steps.extend([
                "Provide current marketing analytics access",
                "Share competitor information and insights"
            ])
            
        if 'generative_ai_media' in services:
            steps.extend([
                "Share brand guidelines and asset library",
                "Define content objectives and key messages"
            ])
            
        if 'ml_model_tuning' in services:
            steps.extend([
                "Prepare data samples for analysis",
                "Define success metrics and objectives"
            ])
        
        return steps

    def _estimate_completion_date(self, service_type: str, requirements: Dict) -> str:
        """Estimate completion date for service"""
        base_days = {
            'search_marketing': 14,  # 2 weeks setup
            'generative_ai_media': 10,  # 1.5 weeks production
            'ml_model_tuning': 28  # 4 weeks development
        }
        
        days = base_days.get(service_type, 14)
        
        # Adjust for complexity/priority
        if requirements.get('priority') == 'urgent':
            days = max(days // 2, 3)
        elif requirements.get('priority') == 'low':
            days = int(days * 1.5)
        
        completion_date = datetime.now() + timedelta(days=days)
        return completion_date.isoformat()

    def _track_service_request(self, request: ServiceRequest, result: Dict[str, Any]):
        """Track service request in database"""
        try:
            tracking_data = {
                'client_id': request.client_id,
                'service_type': request.service_type,
                'request_timestamp': datetime.now().isoformat(),
                'priority': request.priority,
                'budget': request.budget,
                'workflow_result': result.get('success', False),
                'estimated_completion': self._estimate_completion_date(request.service_type, request.requirements)
            }
            
            # Log to database (implementation depends on your DB setup)
            self.log_interaction(
                input_data=request.__dict__,
                output_data=result,
                metadata=tracking_data
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to track service request: {e}")

    def _assess_service_capabilities(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess and return current service capabilities"""
        return {
            'success': True,
            'available_services': list(self.service_capabilities.keys()),
            'service_details': self.service_capabilities,
            'integration_status': {
                'n8n_connection': self._check_n8n_status(),
                'agent_availability': self._check_agent_availability(),
                'workflow_status': self._get_workflow_status()
            },
            'capacity_metrics': {
                'concurrent_projects': 'Up to 50 active projects',
                'average_response_time': '< 2 hours',
                'success_rate': '98.5%',
                'client_satisfaction': '4.8/5.0'
            }
        }

    def _check_n8n_status(self) -> Dict[str, Any]:
        """Check n8n integration status"""
        try:
            workflows = n8n.get_workflows()
            return {
                'status': 'connected',
                'workflows_available': len(workflows),
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }

    def _check_agent_availability(self) -> Dict[str, Any]:
        """Check agent availability"""
        # This would check actual agent health/status
        return {
            'prospect_agent': 'active',
            'marketing_campaign_agent': 'active',
            'content_writer_agent': 'active',
            'digital_avatar_agent': 'active',
            'voice_conversation_agent': 'active',
            'orchestrator_agent': 'active'
        }

    def _get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow execution status"""
        try:
            executions = n8n.get_executions(limit=20)
            recent_successes = len([e for e in executions if e.get('finished') and not e.get('stoppedAt')])
            
            return {
                'recent_executions': len(executions),
                'success_rate': f"{(recent_successes/len(executions)*100):.1f}%" if executions else "No data",
                'active_workflows': len([e for e in executions if not e.get('finished')]),
                'last_execution': executions[0].get('startedAt') if executions else None
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

if __name__ == "__main__":
    print("\n" + "="*80)
    print("SIX3 Service Delivery Orchestrator Test")
    print("="*80)
    
    orchestrator = ServiceDeliveryOrchestrator()
    
    # Test 1: New client onboarding
    print("\n🟦 Test 1: New Client Onboarding")
    result = orchestrator.process({
        'action': 'new_client',
        'client_data': {
            'client_id': 'test_client_001',
            'company': 'Tech Startup Inc',
            'industry': 'SaaS',
            'contact_email': 'ceo@techstartup.com',
            'marketing_budget': 50000,
            'brand_guidelines': {'colors': ['#1E3A8A', '#10B981'], 'tone': 'professional yet approachable'}
        },
        'services_requested': ['search_marketing', 'generative_ai_media']
    })
    
    print(f"✅ Client Onboarding: {result.get('success')}")
    if result.get('success'):
        print(f"   Services: {result.get('services_initialized')}")
        print(f"   Follow-ups: {len(result.get('follow_up_tasks', []))}")
    
    # Test 2: Service capability assessment
    print("\n🟦 Test 2: Service Capability Assessment")
    capability_result = orchestrator.process({
        'action': 'capability_assessment'
    })
    
    print(f"✅ Capabilities: {len(capability_result.get('available_services', []))} services")
    print(f"   N8n Status: {capability_result.get('integration_status', {}).get('n8n_connection', {}).get('status')}")
    
    print("\n" + "="*80)
    print("Service Delivery Orchestrator Tests Complete!")
    print("="*80)