"""
n8n Integration for SIX3 Agency
Connects to hosted n8n instance at https://n8n.six3.cloud
"""

import os
import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class N8nIntegration:
    def __init__(self):
        self.base_url = os.getenv('N8N_HOST', 'https://n8n.six3.cloud')
        self.api_key = os.getenv('N8N_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNGJiOTNhOS1lMDhhLTQ1NjMtODI4MS1jMDc4MjZjZTg4MWMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzNDAwMTg0fQ.JyJFZkyhTuIX43TZ2LtRaJATSDDnGxCS6okaVExHfEY')
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def get_workflows(self) -> List[Dict[str, Any]]:
        """Get all workflows from n8n instance"""
        try:
            response = requests.get(f'{self.base_url}/api/v1/workflows', headers=self.headers)
            if response.status_code == 200:
                workflows = response.json()['data']
                # Filter for SIX3 workflows
                six3_workflows = [w for w in workflows if w['name'].startswith('SIX3')]
                return six3_workflows
            return []
        except Exception as e:
            print(f"Error fetching workflows: {e}")
            return []
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get specific workflow by ID"""
        try:
            response = requests.get(f'{self.base_url}/api/v1/workflows/{workflow_id}', headers=self.headers)
            if response.status_code == 200:
                return response.json()['data']
            return None
        except Exception as e:
            print(f"Error fetching workflow {workflow_id}: {e}")
            return None
    
    def trigger_workflow(self, workflow_name: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Trigger a workflow execution"""
        try:
            # Find workflow by name
            workflows = self.get_workflows()
            workflow = next((w for w in workflows if w['name'] == workflow_name), None)
            
            if not workflow:
                return {'success': False, 'error': f'Workflow {workflow_name} not found'}
            
            # Trigger execution
            payload = data or {}
            response = requests.post(
                f'{self.base_url}/api/v1/workflows/{workflow["id"]}/execute',
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                return {'success': True, 'execution': response.json()['data']}
            else:
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_executions(self, workflow_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get workflow executions"""
        try:
            params = {'limit': limit}
            if workflow_id:
                params['workflowId'] = workflow_id
                
            response = requests.get(
                f'{self.base_url}/api/v1/executions',
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()['data']
            return []
        except Exception as e:
            print(f"Error fetching executions: {e}")
            return []
    
    def create_six3_workflow(self, name: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new SIX3 workflow"""
        try:
            # Ensure name starts with SIX3
            if not name.startswith('SIX3'):
                name = f'SIX3 {name}'
            
            workflow_payload = {
                'name': name,
                'nodes': workflow_data.get('nodes', []),
                'connections': workflow_data.get('connections', {}),
                'settings': workflow_data.get('settings', {})
            }
            
            response = requests.post(
                f'{self.base_url}/api/v1/workflows',
                headers=self.headers,
                json=workflow_payload
            )
            
            if response.status_code in [200, 201]:
                # Check if response has workflow data (successful creation)
                workflow_data = response.json()
                if 'id' in workflow_data:
                    return {'success': True, 'workflow': workflow_data}
                else:
                    return {'success': False, 'error': response.text}
            else:
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_six3_workflow_templates(self) -> List[Dict[str, Any]]:
        """Get available SIX3 workflow templates"""
        templates = [
            {
                'name': 'SIX3 Lead Qualification',
                'description': 'Automatically qualify incoming leads using AI',
                'category': 'Sales',
                'phase': 1,
                'agents': ['Prospect Research Agent', 'Lead Qualification Agent']
            },
            {
                'name': 'SIX3 Email Campaign Personalization',
                'description': 'Personalize email campaigns using customer data',
                'category': 'Marketing',
                'phase': 2,
                'agents': ['Email Personalizer', 'Content Writer Agent']
            },
            {
                'name': 'SIX3 Customer Support Automation',
                'description': 'Automate customer support with AI triage',
                'category': 'Support',
                'phase': 2,
                'agents': ['FAQ Chatbot', 'Customer Success Agent']
            },
            {
                'name': 'SIX3 Content Creation Pipeline',
                'description': 'Automated content creation and publishing',
                'category': 'Content',
                'phase': 2,
                'agents': ['Content Writer Agent', 'Social Media Agent']
            },
            {
                'name': 'SIX3 Sales Orchestration',
                'description': 'Multi-agent sales process coordination',
                'category': 'Sales',
                'phase': 3,
                'agents': ['Orchestrator Agent', 'Sales Strategist', 'Discovery Agent']
            },
            {
                'name': 'SIX3 Avatar Sales Call',
                'description': 'AI avatar-led sales presentations',
                'category': 'Advanced',
                'phase': 4,
                'agents': ['Digital Avatar Agent', 'Voice Conversation Agent']
            }
        ]
        return templates
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get n8n dashboard data for control panel"""
        try:
            workflows = self.get_workflows()
            executions = self.get_executions(limit=50)
            
            # Calculate metrics
            total_workflows = len(workflows)
            active_workflows = len([w for w in workflows if w.get('active', False)])
            recent_executions = len([e for e in executions if e.get('startedAt')])
            
            success_rate = 0
            if executions:
                successful = len([e for e in executions if e.get('finished') and not e.get('stoppedAt')])
                success_rate = (successful / len(executions)) * 100
            
            return {
                'success': True,
                'data': {
                    'total_workflows': total_workflows,
                    'active_workflows': active_workflows,
                    'recent_executions': recent_executions,
                    'success_rate': success_rate,
                    'workflows': workflows,
                    'recent_executions_detail': executions[:10]
                },
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': {
                    'total_workflows': 0,
                    'active_workflows': 0,
                    'recent_executions': 0,
                    'success_rate': 0,
                    'workflows': [],
                    'recent_executions_detail': []
                }
            }

# Global n8n instance
n8n = N8nIntegration()

if __name__ == "__main__":
    # Test the n8n connection
    print("🔄 Testing n8n connection...")
    workflows = n8n.get_workflows()
    print(f"✅ Found {len(workflows)} SIX3 workflows")
    
    dashboard_data = n8n.get_dashboard_data()
    if dashboard_data['success']:
        print(f"✅ n8n Dashboard: {dashboard_data['data']['total_workflows']} workflows, {dashboard_data['data']['success_rate']:.1f}% success rate")
    else:
        print(f"❌ n8n Connection failed: {dashboard_data['error']}")
    
    templates = n8n.get_six3_workflow_templates()
    print(f"✅ {len(templates)} workflow templates available")