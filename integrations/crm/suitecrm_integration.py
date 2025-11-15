"""
SuiteCRM Integration Module
Handles all interactions with SuiteCRM
"""

import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from loguru import logger


class SuiteCRMIntegration:
    """
    Integration class for SuiteCRM API v8
    """

    def __init__(self):
        self.base_url = os.getenv('SUITECRM_URL', 'http://localhost:8080')
        self.api_url = f"{self.base_url}/api/v8"
        self.client_id = os.getenv('SUITECRM_CLIENT_ID')
        self.client_secret = os.getenv('SUITECRM_CLIENT_SECRET')
        self.access_token = None
        self.token_expires_at = None

    def authenticate(self) -> bool:
        """
        Authenticate with SuiteCRM and get access token
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/access_token",
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data['access_token']
                self.token_expires_at = datetime.now().timestamp() + data['expires_in']
                logger.info("SuiteCRM authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def _ensure_authenticated(self):
        """Ensure we have a valid access token"""
        if not self.access_token or datetime.now().timestamp() >= self.token_expires_at:
            self.authenticate()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make authenticated API request

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters

        Returns:
            Response data or None on error
        """
        self._ensure_authenticated()

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json'
        }

        url = f"{self.api_url}/{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            )

            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(
                    f"API request failed: {method} {endpoint} - "
                    f"{response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            logger.error(f"API request error: {e}")
            return None

    # =========================================================================
    # LEADS
    # =========================================================================

    def create_lead(self, lead_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new lead in CRM

        Args:
            lead_data: Lead information

        Returns:
            Lead ID if successful, None otherwise
        """
        payload = {
            'data': {
                'type': 'Lead',
                'attributes': {
                    'first_name': lead_data.get('first_name', ''),
                    'last_name': lead_data.get('last_name', ''),
                    'email1': lead_data.get('email', ''),
                    'phone_work': lead_data.get('phone', ''),
                    'account_name': lead_data.get('company', ''),
                    'description': lead_data.get('description', ''),
                    'lead_source': lead_data.get('source', 'Website'),
                    'status': lead_data.get('status', 'New'),
                }
            }
        }

        # Add custom fields
        if 'ai_score' in lead_data:
            payload['data']['attributes']['ai_score_c'] = lead_data['ai_score']

        response = self._make_request('POST', 'module', payload)

        if response and 'data' in response:
            lead_id = response['data']['id']
            logger.info(f"Lead created: {lead_id}")
            return lead_id

        return None

    def get_lead(self, lead_id: str) -> Optional[Dict]:
        """Get lead by ID"""
        response = self._make_request('GET', f'module/Lead/{lead_id}')

        if response and 'data' in response:
            return response['data']

        return None

    def update_lead(self, lead_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a lead

        Args:
            lead_id: Lead ID
            updates: Fields to update

        Returns:
            True if successful, False otherwise
        """
        payload = {
            'data': {
                'type': 'Lead',
                'id': lead_id,
                'attributes': updates
            }
        }

        response = self._make_request('PATCH', f'module/Lead/{lead_id}', payload)
        return response is not None

    def convert_lead(self, lead_id: str) -> Optional[Dict]:
        """
        Convert lead to contact/opportunity

        Returns:
            Dict with contact_id and opportunity_id
        """
        # SuiteCRM lead conversion logic
        # This is a simplified version
        lead = self.get_lead(lead_id)
        if not lead:
            return None

        attrs = lead.get('attributes', {})

        # Create contact
        contact_id = self.create_contact({
            'first_name': attrs.get('first_name'),
            'last_name': attrs.get('last_name'),
            'email': attrs.get('email1'),
            'phone': attrs.get('phone_work')
        })

        # Create opportunity
        opportunity_id = self.create_opportunity({
            'name': f"{attrs.get('account_name')} - Opportunity",
            'amount': attrs.get('opportunity_amount'),
            'sales_stage': 'Prospecting'
        })

        # Mark lead as converted
        self.update_lead(lead_id, {'status': 'Converted'})

        return {
            'contact_id': contact_id,
            'opportunity_id': opportunity_id
        }

    # =========================================================================
    # CONTACTS
    # =========================================================================

    def create_contact(self, contact_data: Dict[str, Any]) -> Optional[str]:
        """Create a new contact"""
        payload = {
            'data': {
                'type': 'Contact',
                'attributes': {
                    'first_name': contact_data.get('first_name', ''),
                    'last_name': contact_data.get('last_name', ''),
                    'email1': contact_data.get('email', ''),
                    'phone_work': contact_data.get('phone', ''),
                    'title': contact_data.get('title', ''),
                    'department': contact_data.get('department', ''),
                }
            }
        }

        response = self._make_request('POST', 'module', payload)

        if response and 'data' in response:
            return response['data']['id']

        return None

    def get_contact(self, contact_id: str) -> Optional[Dict]:
        """Get contact by ID"""
        response = self._make_request('GET', f'module/Contact/{contact_id}')

        if response and 'data' in response:
            return response['data']

        return None

    # =========================================================================
    # OPPORTUNITIES
    # =========================================================================

    def create_opportunity(self, opp_data: Dict[str, Any]) -> Optional[str]:
        """Create a new opportunity"""
        payload = {
            'data': {
                'type': 'Opportunity',
                'attributes': {
                    'name': opp_data.get('name', ''),
                    'amount': opp_data.get('amount', 0),
                    'sales_stage': opp_data.get('sales_stage', 'Prospecting'),
                    'date_closed': opp_data.get('close_date', ''),
                    'description': opp_data.get('description', ''),
                }
            }
        }

        response = self._make_request('POST', 'module', payload)

        if response and 'data' in response:
            return response['data']['id']

        return None

    def get_opportunity(self, opp_id: str) -> Optional[Dict]:
        """Get opportunity by ID"""
        response = self._make_request('GET', f'module/Opportunity/{opp_id}')

        if response and 'data' in response:
            return response['data']

        return None

    def update_opportunity(self, opp_id: str, updates: Dict[str, Any]) -> bool:
        """Update an opportunity"""
        payload = {
            'data': {
                'type': 'Opportunity',
                'id': opp_id,
                'attributes': updates
            }
        }

        response = self._make_request('PATCH', f'module/Opportunity/{opp_id}', payload)
        return response is not None

    # =========================================================================
    # ACTIVITIES
    # =========================================================================

    def create_activity(self, activity_data: Dict[str, Any]) -> Optional[str]:
        """
        Create an activity (call, meeting, task)

        Args:
            activity_data: Activity information with keys:
                - type: 'Call', 'Meeting', 'Task'
                - subject: Activity subject
                - description: Details
                - related_to_type: 'Lead', 'Contact', 'Opportunity'
                - related_to_id: ID of related record
                - due_date: Due date for task
                - date_start: Start time for meeting/call

        Returns:
            Activity ID if successful
        """
        activity_type = activity_data.get('type', 'Task')

        module_map = {
            'Call': 'Calls',
            'Meeting': 'Meetings',
            'Task': 'Tasks'
        }

        module = module_map.get(activity_type, 'Tasks')

        payload = {
            'data': {
                'type': module,
                'attributes': {
                    'name': activity_data.get('subject', ''),
                    'description': activity_data.get('description', ''),
                    'status': activity_data.get('status', 'Not Started'),
                }
            }
        }

        # Add type-specific fields
        if activity_type in ['Call', 'Meeting']:
            payload['data']['attributes']['date_start'] = \
                activity_data.get('date_start', '')

        if activity_type == 'Task':
            payload['data']['attributes']['date_due'] = \
                activity_data.get('due_date', '')

        response = self._make_request('POST', 'module', payload)

        if response and 'data' in response:
            return response['data']['id']

        return None

    # =========================================================================
    # SEARCH & QUERY
    # =========================================================================

    def search(
        self,
        module: str,
        filters: Dict[str, Any],
        fields: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Search for records

        Args:
            module: Module name (Lead, Contact, Opportunity, etc.)
            filters: Search filters
            fields: Fields to return

        Returns:
            List of matching records
        """
        params = {
            'filter[operator]': 'and',
        }

        # Add filters
        for idx, (field, value) in enumerate(filters.items()):
            params[f'filter[{idx}][field]'] = field
            params[f'filter[{idx}][operator]'] = 'eq'
            params[f'filter[{idx}][value]'] = value

        # Add fields
        if fields:
            params['fields[{}]'.format(module)] = ','.join(fields)

        response = self._make_request('GET', f'module/{module}', params=params)

        if response and 'data' in response:
            return response['data']

        return []


if __name__ == "__main__":
    # Test the integration
    crm = SuiteCRMIntegration()

    if crm.authenticate():
        # Test lead creation
        lead_id = crm.create_lead({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'company': 'Acme Corp',
            'phone': '+1-555-1234',
            'source': 'Website',
            'ai_score': 8.5
        })

        if lead_id:
            print(f"✓ Lead created: {lead_id}")

            # Test lead retrieval
            lead = crm.get_lead(lead_id)
            print(f"✓ Lead retrieved: {lead['attributes']['email1']}")

            # Test lead update
            success = crm.update_lead(lead_id, {'status': 'Contacted'})
            print(f"✓ Lead updated: {success}")
        else:
            print("✗ Failed to create lead")
    else:
        print("✗ Authentication failed")
