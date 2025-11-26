"""
LinkedIn API Integration for SIX3 Agency

Handles:
- Publishing posts to LinkedIn company pages and personal profiles
- Scheduling posts for optimal engagement
- Analytics and engagement tracking
- Lead generation activities
- Connection management

Requirements:
- LinkedIn API access (Developer account)
- linkedin-api or requests for API calls
- Valid LinkedIn access tokens
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import requests
import base64

logger = logging.getLogger(__name__)


class LinkedInIntegration:
    """LinkedIn API integration for automated posting and engagement"""
    
    def __init__(self, access_token: Optional[str] = None, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialize LinkedIn integration
        
        Args:
            access_token: LinkedIn access token (if not provided, reads from LINKEDIN_ACCESS_TOKEN env var)
            client_id: LinkedIn client ID (if not provided, reads from LINKEDIN_CLIENT_ID env var)
            client_secret: LinkedIn client secret (if not provided, reads from LINKEDIN_CLIENT_SECRET env var)
        """
        self.access_token = access_token or os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.client_id = client_id or os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('LINKEDIN_CLIENT_SECRET')
        
        if not self.access_token:
            raise ValueError("LinkedIn access token required. Set LINKEDIN_ACCESS_TOKEN environment variable or pass access_token parameter")
        
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        # Cache for user profile info
        self._user_info = None
        self._company_pages = None
        
        logger.info("LinkedIn integration initialized")
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        Get current user profile information
        
        Returns:
            Dict with user profile data
        """
        if self._user_info:
            return self._user_info
        
        try:
            url = f"{self.base_url}/me"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            user_data = response.json()
            self._user_info = {
                'id': user_data.get('id'),
                'first_name': user_data.get('localizedFirstName'),
                'last_name': user_data.get('localizedLastName'),
                'headline': user_data.get('headline'),
                'success': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return self._user_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get user info: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_company_pages(self) -> Dict[str, Any]:
        """
        Get company pages that the user can manage
        
        Returns:
            Dict with list of company pages
        """
        if self._company_pages:
            return self._company_pages
        
        try:
            url = f"{self.base_url}/organizationAcls"
            params = {'q': 'roleAssignee'}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            pages_data = response.json()
            companies = []
            
            for element in pages_data.get('elements', []):
                if element.get('state') == 'APPROVED':
                    org_id = element.get('organization')
                    if org_id:
                        # Get company details
                        org_url = f"{self.base_url}/organizations/{org_id}"
                        org_response = requests.get(org_url, headers=self.headers)
                        if org_response.status_code == 200:
                            org_data = org_response.json()
                            companies.append({
                                'id': org_id,
                                'name': org_data.get('localizedName'),
                                'role': element.get('role')
                            })
            
            self._company_pages = {
                'success': True,
                'companies': companies,
                'total': len(companies),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return self._company_pages
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get company pages: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def create_text_post(self, 
                        text: str, 
                        visibility: str = "PUBLIC",
                        as_company: str = None) -> Dict[str, Any]:
        """
        Create a text post on LinkedIn
        
        Args:
            text: Post content (max 3000 characters)
            visibility: Post visibility ("PUBLIC", "CONNECTIONS", "LOGGED_IN_MEMBERS")
            as_company: Company page ID to post as (if None, posts as personal profile)
            
        Returns:
            Dict with post creation response
        """
        try:
            if len(text) > 3000:
                text = text[:2997] + "..."
            
            # Determine author URN
            if as_company:
                author_urn = f"urn:li:organization:{as_company}"
            else:
                user_info = self.get_user_info()
                if not user_info.get('success'):
                    return user_info
                author_urn = f"urn:li:person:{user_info['id']}"
            
            post_data = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }
            
            url = f"{self.base_url}/ugcPosts"
            response = requests.post(url, headers=self.headers, json=post_data)
            response.raise_for_status()
            
            post_response = response.json()
            
            return {
                'success': True,
                'post_id': post_response.get('id'),
                'post_url': f"https://www.linkedin.com/feed/update/{post_response.get('id')}",
                'text': text,
                'author': author_urn,
                'visibility': visibility,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create LinkedIn post: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': text,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def create_article_post(self, 
                           text: str, 
                           title: str,
                           description: str,
                           article_url: str,
                           image_url: str = None,
                           visibility: str = "PUBLIC",
                           as_company: str = None) -> Dict[str, Any]:
        """
        Share an article with commentary
        
        Args:
            text: Commentary text
            title: Article title
            description: Article description
            article_url: URL to the article
            image_url: Optional image URL for the article
            visibility: Post visibility
            as_company: Company page ID to post as
            
        Returns:
            Dict with post creation response
        """
        try:
            # Determine author URN
            if as_company:
                author_urn = f"urn:li:organization:{as_company}"
            else:
                user_info = self.get_user_info()
                if not user_info.get('success'):
                    return user_info
                author_urn = f"urn:li:person:{user_info['id']}"
            
            # Build media content
            media_content = {
                "status": "READY",
                "description": {
                    "text": description
                },
                "originalUrl": article_url,
                "title": {
                    "text": title
                }
            }
            
            if image_url:
                media_content["thumbnails"] = [{"url": image_url}]
            
            post_data = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "ARTICLE",
                        "media": [media_content]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }
            
            url = f"{self.base_url}/ugcPosts"
            response = requests.post(url, headers=self.headers, json=post_data)
            response.raise_for_status()
            
            post_response = response.json()
            
            return {
                'success': True,
                'post_id': post_response.get('id'),
                'post_url': f"https://www.linkedin.com/feed/update/{post_response.get('id')}",
                'text': text,
                'article_title': title,
                'article_url': article_url,
                'author': author_urn,
                'visibility': visibility,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create LinkedIn article post: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """
        Get analytics for a specific post
        
        Args:
            post_id: LinkedIn post ID
            
        Returns:
            Dict with post analytics
        """
        try:
            url = f"{self.base_url}/socialActions/{post_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            analytics_data = response.json()
            
            return {
                'success': True,
                'post_id': post_id,
                'likes': analytics_data.get('numLikes', 0),
                'comments': analytics_data.get('numComments', 0),
                'shares': analytics_data.get('numShares', 0),
                'clicks': analytics_data.get('numClicks', 0),
                'impressions': analytics_data.get('numImpressions', 0),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get post analytics for {post_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'post_id': post_id,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def search_companies(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for companies on LinkedIn
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Dict with search results
        """
        try:
            url = f"{self.base_url}/companySearch"
            params = {
                'keywords': query,
                'count': limit
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            search_data = response.json()
            companies = []
            
            for company in search_data.get('companies', {}).get('values', []):
                companies.append({
                    'id': company.get('id'),
                    'name': company.get('name'),
                    'industry': company.get('industry'),
                    'size': company.get('size'),
                    'website': company.get('websiteUrl'),
                    'description': company.get('description')
                })
            
            return {
                'success': True,
                'query': query,
                'companies': companies,
                'total': len(companies),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to search companies: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def send_message(self, recipient_id: str, subject: str, message: str) -> Dict[str, Any]:
        """
        Send a direct message to a LinkedIn connection
        
        Args:
            recipient_id: LinkedIn member ID
            subject: Message subject
            message: Message content
            
        Returns:
            Dict with message send response
        """
        try:
            user_info = self.get_user_info()
            if not user_info.get('success'):
                return user_info
            
            message_data = {
                "recipients": [f"urn:li:person:{recipient_id}"],
                "subject": subject,
                "body": message,
                "sender": f"urn:li:person:{user_info['id']}"
            }
            
            url = f"{self.base_url}/messages"
            response = requests.post(url, headers=self.headers, json=message_data)
            response.raise_for_status()
            
            return {
                'success': True,
                'recipient_id': recipient_id,
                'subject': subject,
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send LinkedIn message: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'recipient_id': recipient_id,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_connections(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get user's LinkedIn connections
        
        Args:
            limit: Maximum number of connections to return
            
        Returns:
            Dict with connections list
        """
        try:
            url = f"{self.base_url}/connections"
            params = {'count': limit}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            connections_data = response.json()
            connections = []
            
            for conn in connections_data.get('values', []):
                connections.append({
                    'id': conn.get('id'),
                    'first_name': conn.get('firstName'),
                    'last_name': conn.get('lastName'),
                    'headline': conn.get('headline'),
                    'industry': conn.get('industry'),
                    'location': conn.get('location', {}).get('name')
                })
            
            return {
                'success': True,
                'connections': connections,
                'total': len(connections),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get connections: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the LinkedIn API connection
        
        Returns:
            Dict with connection test results
        """
        try:
            user_info = self.get_user_info()
            
            if user_info.get('success'):
                return {
                    'success': True,
                    'connection_status': 'connected',
                    'user_name': f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip(),
                    'user_id': user_info.get('id'),
                    'api_access': True,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'success': False,
                    'connection_status': 'failed',
                    'error': user_info.get('error', 'Unknown error'),
                    'api_access': False,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"LinkedIn connection test failed: {str(e)}")
            return {
                'success': False,
                'connection_status': 'failed',
                'error': str(e),
                'api_access': False,
                'timestamp': datetime.utcnow().isoformat()
            }


class LinkedInPostTemplates:
    """Pre-built LinkedIn post templates for common business use cases"""
    
    @staticmethod
    def company_announcement(company_name: str, announcement: str) -> str:
        """Generate company announcement post"""
        return f"""🎉 Exciting news from {company_name}!

{announcement}

We're grateful for the continued support from our community and look forward to what's ahead.

#CompanyNews #{company_name.replace(' ', '')} #Growth #Innovation"""
    
    @staticmethod
    def thought_leadership(topic: str, insight: str, call_to_action: str = None) -> str:
        """Generate thought leadership post"""
        cta = call_to_action or "What are your thoughts on this?"
        
        return f"""💡 Thoughts on {topic}:

{insight}

In my experience, this approach has proven effective because it focuses on genuine value creation rather than short-term gains.

{cta}

#ThoughtLeadership #{topic.replace(' ', '')} #BusinessStrategy #Leadership"""
    
    @staticmethod
    def product_feature(feature_name: str, benefits: List[str], demo_url: str = None) -> str:
        """Generate product feature announcement"""
        benefits_text = '\n'.join([f"✅ {benefit}" for benefit in benefits])
        demo_text = f"\n\n🎯 See it in action: {demo_url}" if demo_url else ""
        
        return f"""🚀 Introducing {feature_name}!

We're excited to share this new capability that helps our customers:

{benefits_text}
{demo_text}

Ready to learn more? Drop a comment or send me a DM.

#ProductUpdate #Innovation #AI #Automation"""
    
    @staticmethod
    def industry_insights(industry: str, trend: str, prediction: str) -> str:
        """Generate industry insights post"""
        return f"""📈 {industry} Industry Trend Alert:

{trend}

My prediction: {prediction}

This shift represents both challenges and opportunities for businesses in our space. The key is to adapt quickly while maintaining focus on customer value.

What trends are you seeing in your industry?

#{industry.replace(' ', '')} #IndustryTrends #BusinessIntelligence #FutureOfWork"""


# Usage example
if __name__ == "__main__":
    # Example usage (requires LINKEDIN_ACCESS_TOKEN environment variable)
    import os
    
    if os.getenv('LINKEDIN_ACCESS_TOKEN'):
        linkedin = LinkedInIntegration()
        
        # Test connection
        test_result = linkedin.test_connection()
        print("Connection test:", test_result)
        
        # Create a test post
        if test_result.get('success'):
            post_content = LinkedInPostTemplates.thought_leadership(
                "AI Automation",
                "The future of business operations lies in intelligent automation that enhances human capabilities rather than replacing them.",
                "How is your company approaching AI integration?"
            )
            
            result = linkedin.create_text_post(post_content)
            print("Post creation result:", result)
    else:
        print("Set LINKEDIN_ACCESS_TOKEN environment variable to test integration")