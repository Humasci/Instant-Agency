"""
Attio CRM Integration Module
Handles all interactions with Attio CRM API v2

Attio is a modern, flexible CRM with a powerful API.
API Docs: https://developers.attio.com/reference
"""

import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from loguru import logger


class AttioCRMIntegration:
    """
    Integration class for Attio CRM API v2

    Setup:
    1. Get API key from Attio: Settings → Developers → API Keys
    2. Set environment variable: ATTIO_API_KEY=your_key_here
    """

    def __init__(self):
        self.base_url = "https://api.attio.com/v2"
        self.api_key = os.getenv('ATTIO_API_KEY')

        if not self.api_key:
            logger.warning("ATTIO_API_KEY not set. CRM integration will not work.")

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

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
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters

        Returns:
            Response data or None on error
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )

            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 204:
                return {'success': True}
            else:
                logger.error(
                    f"Attio API request failed: {method} {endpoint} - "
                    f"{response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            logger.error(f"Attio API request error: {e}")
            return None

    # =========================================================================
    # PEOPLE (Contacts/Leads)
    # =========================================================================

    def create_person(self, person_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create a new person in Attio

        Args:
            person_data: Person information
                {
                    'email': 'john@example.com',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'phone': '+1-555-1234',
                    'job_title': 'CEO',
                    'linkedin_url': 'https://linkedin.com/in/johndoe',
                    'tags': ['lead', 'hot'],
                    'custom_attributes': {'ai_score': 8.5}
                }

        Returns:
            Created person record or None
        """
        # Attio uses 'values' array for attributes
        values = []

        # Email (required)
        if 'email' in person_data:
            values.append({
                'attribute': 'email_addresses',
                'value': person_data['email']
            })

        # Name
        if 'first_name' in person_data or 'last_name' in person_data:
            name_parts = []
            if 'first_name' in person_data:
                name_parts.append(person_data['first_name'])
            if 'last_name' in person_data:
                name_parts.append(person_data['last_name'])

            values.append({
                'attribute': 'name',
                'value': ' '.join(name_parts)
            })

        # Phone
        if 'phone' in person_data:
            values.append({
                'attribute': 'phone_numbers',
                'value': person_data['phone']
            })

        # Job title
        if 'job_title' in person_data:
            values.append({
                'attribute': 'job_title',
                'value': person_data['job_title']
            })

        # LinkedIn
        if 'linkedin_url' in person_data:
            values.append({
                'attribute': 'linkedin_url',
                'value': person_data['linkedin_url']
            })

        # Tags
        if 'tags' in person_data:
            values.append({
                'attribute': 'tags',
                'value': person_data['tags']
            })

        # Custom attributes
        if 'custom_attributes' in person_data:
            for key, value in person_data['custom_attributes'].items():
                values.append({
                    'attribute': key,
                    'value': value
                })

        payload = {'data': {'values': values}}

        response = self._make_request('POST', 'objects/people/records', payload)

        if response and 'data' in response:
            logger.info(f"Person created: {response['data'].get('id')}")
            return response['data']

        return None

    def get_person(self, person_id: str) -> Optional[Dict]:
        """Get person by ID"""
        response = self._make_request('GET', f'objects/people/records/{person_id}')

        if response and 'data' in response:
            return response['data']

        return None

    def get_person_by_email(self, email: str) -> Optional[Dict]:
        """
        Find person by email address

        Args:
            email: Email address to search for

        Returns:
            Person record or None
        """
        params = {
            'filter': {
                'email_addresses': {
                    '$contains': email
                }
            }
        }

        response = self._make_request('GET', 'objects/people/records/query', params=params)

        if response and 'data' in response and len(response['data']) > 0:
            return response['data'][0]

        return None

    def update_person(self, person_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a person record

        Args:
            person_id: Person ID
            updates: Fields to update (same format as create_person)

        Returns:
            True if successful, False otherwise
        """
        # Convert updates to Attio's values format
        values = []

        for key, value in updates.items():
            if key == 'custom_attributes':
                for attr_key, attr_value in value.items():
                    values.append({'attribute': attr_key, 'value': attr_value})
            else:
                values.append({'attribute': key, 'value': value})

        payload = {'data': {'values': values}}

        response = self._make_request('PATCH', f'objects/people/records/{person_id}', payload)
        return response is not None

    # =========================================================================
    # COMPANIES
    # =========================================================================

    def create_company(self, company_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create a new company in Attio

        Args:
            company_data: Company information
                {
                    'name': 'Acme Corp',
                    'domain': 'acme.com',
                    'industry': 'Technology',
                    'employee_count': 50,
                    'description': 'B2B SaaS company',
                    'linkedin_url': 'https://linkedin.com/company/acme',
                    'tags': ['prospect', 'enterprise']
                }

        Returns:
            Created company record or None
        """
        values = []

        # Name (required)
        if 'name' in company_data:
            values.append({
                'attribute': 'name',
                'value': company_data['name']
            })

        # Domain
        if 'domain' in company_data:
            values.append({
                'attribute': 'domains',
                'value': company_data['domain']
            })

        # Industry
        if 'industry' in company_data:
            values.append({
                'attribute': 'industry',
                'value': company_data['industry']
            })

        # Employee count
        if 'employee_count' in company_data:
            values.append({
                'attribute': 'employee_count',
                'value': company_data['employee_count']
            })

        # Description
        if 'description' in company_data:
            values.append({
                'attribute': 'description',
                'value': company_data['description']
            })

        # LinkedIn
        if 'linkedin_url' in company_data:
            values.append({
                'attribute': 'linkedin_url',
                'value': company_data['linkedin_url']
            })

        # Tags
        if 'tags' in company_data:
            values.append({
                'attribute': 'tags',
                'value': company_data['tags']
            })

        payload = {'data': {'values': values}}

        response = self._make_request('POST', 'objects/companies/records', payload)

        if response and 'data' in response:
            logger.info(f"Company created: {response['data'].get('id')}")
            return response['data']

        return None

    def get_company(self, company_id: str) -> Optional[Dict]:
        """Get company by ID"""
        response = self._make_request('GET', f'objects/companies/records/{company_id}')

        if response and 'data' in response:
            return response['data']

        return None

    def get_company_by_domain(self, domain: str) -> Optional[Dict]:
        """
        Find company by domain

        Args:
            domain: Company domain (e.g., 'acme.com')

        Returns:
            Company record or None
        """
        params = {
            'filter': {
                'domains': {
                    '$contains': domain
                }
            }
        }

        response = self._make_request('GET', 'objects/companies/records/query', params=params)

        if response and 'data' in response and len(response['data']) > 0:
            return response['data'][0]

        return None

    # =========================================================================
    # NOTES
    # =========================================================================

    def create_note(self, note_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create a note attached to a person or company

        Args:
            note_data: Note information
                {
                    'parent_object': 'people' or 'companies',
                    'parent_record_id': 'record_id',
                    'title': 'Note title',
                    'content': 'Note content in markdown',
                    'format': 'plaintext' or 'markdown'
                }

        Returns:
            Created note or None
        """
        payload = {
            'data': {
                'parent_object': note_data.get('parent_object', 'people'),
                'parent_record_id': note_data['parent_record_id'],
                'title': note_data.get('title', ''),
                'content': {
                    'format': note_data.get('format', 'plaintext'),
                    'content': note_data['content']
                }
            }
        }

        response = self._make_request('POST', 'notes', payload)

        if response and 'data' in response:
            logger.info(f"Note created: {response['data'].get('id')}")
            return response['data']

        return None

    # =========================================================================
    # TASKS
    # =========================================================================

    def create_task(self, task_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create a task

        Args:
            task_data: Task information
                {
                    'content': 'Follow up with lead',
                    'deadline': '2024-12-31',
                    'assignee_id': 'user_id',
                    'linked_records': [
                        {'object': 'people', 'record_id': 'person_id'}
                    ]
                }

        Returns:
            Created task or None
        """
        payload = {
            'data': {
                'content': task_data['content'],
                'deadline': task_data.get('deadline'),
                'assignee': task_data.get('assignee_id'),
                'linked_records': task_data.get('linked_records', [])
            }
        }

        response = self._make_request('POST', 'tasks', payload)

        if response and 'data' in response:
            logger.info(f"Task created: {response['data'].get('id')}")
            return response['data']

        return None

    # =========================================================================
    # LISTS (Collections)
    # =========================================================================

    def add_to_list(self, list_id: str, record_id: str) -> bool:
        """
        Add a record to a list

        Args:
            list_id: List ID (e.g., 'hot_leads', 'active_deals')
            record_id: Record ID to add

        Returns:
            True if successful
        """
        payload = {
            'data': {
                'record_id': record_id
            }
        }

        response = self._make_request('POST', f'lists/{list_id}/entries', payload)
        return response is not None

    def remove_from_list(self, list_id: str, record_id: str) -> bool:
        """Remove a record from a list"""
        response = self._make_request('DELETE', f'lists/{list_id}/entries/{record_id}')
        return response is not None

    # =========================================================================
    # WEBHOOKS
    # =========================================================================

    def create_webhook(self, webhook_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create a webhook to receive real-time updates

        Args:
            webhook_data: Webhook configuration
                {
                    'url': 'https://your-server.com/webhook',
                    'subscriptions': [
                        {'object': 'people', 'events': ['created', 'updated']},
                        {'object': 'companies', 'events': ['created']}
                    ]
                }

        Returns:
            Webhook details or None
        """
        payload = {'data': webhook_data}

        response = self._make_request('POST', 'webhooks', payload)

        if response and 'data' in response:
            logger.info(f"Webhook created: {response['data'].get('id')}")
            return response['data']

        return None

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def create_lead_from_agent(self, agent_result: Dict[str, Any]) -> Optional[Dict]:
        """
        Create a lead in Attio from AI agent qualification result

        Args:
            agent_result: Result from Phase 1 Prospect Agent
                {
                    'lead_info': {
                        'name': 'John Doe',
                        'email': 'john@example.com',
                        'company': 'Acme Corp'
                    },
                    'qualification_score': 8.5,
                    'qualification_status': 'hot',
                    'sentiment': {...}
                }

        Returns:
            Created person record
        """
        lead_info = agent_result.get('lead_info', {})

        # Split name
        name_parts = lead_info.get('name', '').split(' ', 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Create person
        person_data = {
            'email': lead_info.get('email'),
            'first_name': first_name,
            'last_name': last_name,
            'tags': [agent_result.get('qualification_status', 'lead')],
            'custom_attributes': {
                'ai_qualification_score': agent_result.get('qualification_score'),
                'sentiment_score': agent_result.get('sentiment', {}).get('score', 0),
                'lead_source': 'AI Agent'
            }
        }

        person = self.create_person(person_data)

        if person and lead_info.get('company'):
            # Create or find company
            company = self.get_company_by_domain(lead_info.get('company', '').lower().replace(' ', ''))

            if not company:
                company = self.create_company({
                    'name': lead_info.get('company'),
                    'tags': ['prospect']
                })

        return person


if __name__ == "__main__":
    # Test the integration
    crm = AttioCRMIntegration()

    print("\n" + "="*60)
    print("Testing Attio CRM Integration")
    print("="*60 + "\n")

    # Test 1: Create person
    print("Test 1: Creating a person...")
    person = crm.create_person({
        'email': 'john.doe@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'job_title': 'CEO',
        'phone': '+1-555-1234',
        'tags': ['lead', 'hot'],
        'custom_attributes': {
            'ai_score': 8.5,
            'lead_source': 'Website'
        }
    })

    if person:
        print(f"✓ Person created: {person.get('id')}")
        person_id = person.get('id')

        # Test 2: Create company
        print("\nTest 2: Creating a company...")
        company = crm.create_company({
            'name': 'Acme Corporation',
            'domain': 'acme.com',
            'industry': 'Technology',
            'employee_count': 50,
            'tags': ['prospect', 'enterprise']
        })

        if company:
            print(f"✓ Company created: {company.get('id')}")

        # Test 3: Create note
        print("\nTest 3: Creating a note...")
        note = crm.create_note({
            'parent_object': 'people',
            'parent_record_id': person_id,
            'title': 'Initial Contact',
            'content': 'Lead showed strong interest in AI automation platform. High qualification score from sentiment analysis.',
            'format': 'plaintext'
        })

        if note:
            print(f"✓ Note created: {note.get('id')}")

        # Test 4: Create task
        print("\nTest 4: Creating a task...")
        task = crm.create_task({
            'content': 'Schedule demo call with John Doe',
            'deadline': '2024-12-31',
            'linked_records': [
                {'object': 'people', 'record_id': person_id}
            ]
        })

        if task:
            print(f"✓ Task created: {task.get('id')}")

    else:
        print("✗ Failed to create person")
        print("Make sure ATTIO_API_KEY is set in your environment")

    print("\n" + "="*60)
    print("Integration test complete!")
    print("="*60 + "\n")
