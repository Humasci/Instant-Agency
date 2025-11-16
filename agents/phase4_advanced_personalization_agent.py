"""
Phase 4: Advanced Personalization Agent

Creates hyper-personalized experiences by analyzing user behavior, preferences, and context.
Dynamically adapts content, messaging, and interactions for each individual.

Key Features:
- Behavioral analysis and pattern recognition
- Dynamic user profiling
- Real-time personalization
- A/B testing and variant selection
- Cross-agent personalization consistency

Use Cases:
- Personalized email campaigns
- Dynamic website content
- Tailored product recommendations
- Custom conversation flows
- Adaptive pricing and offers
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from base_agent import BaseAgent


class Phase4AdvancedPersonalizationAgent(BaseAgent):
    """
    Advanced Personalization Agent
    Delivers hyper-personalized experiences across all touchpoints
    """

    def __init__(self):
        super().__init__(
            agent_name="phase4_advanced_personalization",
            agent_type="personalization",
            model_name="behavioral_analysis"
        )

        # User profiles storage (in production, would use Redis/database)
        self.user_profiles = {}

        # Active A/B tests
        self.ab_tests = {}

        # Personalization rules
        self.personalization_rules = self._load_personalization_rules()

        # Behavioral segments
        self.segments = {
            'high_value': {'min_ltv': 10000, 'min_engagement': 80},
            'engaged': {'min_engagement': 60, 'min_activity_days': 7},
            'at_risk': {'max_engagement': 30, 'days_since_activity': 30},
            'new_user': {'account_age_days': 7},
            'champion': {'min_ltv': 20000, 'min_nps': 9}
        }

        print(f"✓ Advanced Personalization Agent initialized")
        print(f"  Behavioral segments: {len(self.segments)}")
        print(f"  Personalization rules: {len(self.personalization_rules)}")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process personalization request

        Args:
            input_data: {
                'action': 'personalize_content' | 'update_profile' | 'get_profile' | 'ab_test',
                'user_id': str,
                'content_type': str (for personalize_content),
                'context': dict,
                'behavior_data': dict (for update_profile),
                'test_id': str (for ab_test)
            }

        Returns:
            Personalized content or profile data
        """
        try:
            action = input_data.get('action', 'personalize_content')

            if action == 'personalize_content':
                return self._personalize_content(input_data)
            elif action == 'update_profile':
                return self._update_profile(input_data)
            elif action == 'get_profile':
                return self._get_profile(input_data)
            elif action == 'ab_test':
                return self._run_ab_test(input_data)
            elif action == 'segment_user':
                return self._segment_user(input_data)
            elif action == 'recommend':
                return self._generate_recommendations(input_data)
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            self.logger.error(f"Personalization error: {e}")
            return {'success': False, 'error': str(e)}

    def _personalize_content(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Personalize content based on user profile"""
        user_id = input_data.get('user_id')
        content_type = input_data.get('content_type', 'email')
        context = input_data.get('context', {})

        if not user_id:
            return {'success': False, 'error': 'user_id required'}

        # Get or create user profile
        profile = self._get_or_create_profile(user_id)

        # Determine user segment
        segment = self._determine_segment(profile)

        # Select personalization strategy
        strategy = self._select_strategy(content_type, segment, context)

        # Generate personalized content
        personalized_content = self._generate_personalized_content(
            content_type,
            profile,
            segment,
            strategy,
            context
        )

        # Track personalization
        self._track_personalization(user_id, content_type, strategy)

        return {
            'success': True,
            'user_id': user_id,
            'segment': segment,
            'strategy': strategy,
            'personalized_content': personalized_content,
            'confidence': self._calculate_confidence(profile),
            'timestamp': datetime.now().isoformat()
        }

    def _update_profile(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile with new behavior data"""
        user_id = input_data.get('user_id')
        behavior_data = input_data.get('behavior_data', {})

        if not user_id:
            return {'success': False, 'error': 'user_id required'}

        # Get or create profile
        profile = self._get_or_create_profile(user_id)

        # Update behavioral data
        profile['last_updated'] = datetime.now().isoformat()
        profile['total_interactions'] += behavior_data.get('interactions', 0)

        # Update engagement metrics
        if 'email_opened' in behavior_data:
            profile['email_opens'] = profile.get('email_opens', 0) + 1

        if 'link_clicked' in behavior_data:
            profile['link_clicks'] = profile.get('link_clicks', 0) + 1

        if 'page_viewed' in behavior_data:
            profile['page_views'] = profile.get('page_views', 0) + 1
            profile['pages_viewed'] = profile.get('pages_viewed', [])
            profile['pages_viewed'].append(behavior_data['page_viewed'])
            # Keep only last 50 pages
            profile['pages_viewed'] = profile['pages_viewed'][-50:]

        if 'purchase' in behavior_data:
            profile['total_purchases'] = profile.get('total_purchases', 0) + 1
            profile['total_revenue'] = profile.get('total_revenue', 0) + behavior_data['purchase']['amount']

        # Calculate engagement score
        profile['engagement_score'] = self._calculate_engagement_score(profile)

        # Update interests based on behavior
        profile['interests'] = self._extract_interests(profile)

        # Save profile
        self.user_profiles[user_id] = profile

        return {
            'success': True,
            'user_id': user_id,
            'profile': profile,
            'engagement_score': profile['engagement_score'],
            'segment': self._determine_segment(profile),
            'timestamp': datetime.now().isoformat()
        }

    def _get_profile(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get user profile"""
        user_id = input_data.get('user_id')

        if not user_id:
            return {'success': False, 'error': 'user_id required'}

        profile = self._get_or_create_profile(user_id)

        return {
            'success': True,
            'user_id': user_id,
            'profile': profile,
            'segment': self._determine_segment(profile),
            'recommendations': self._generate_simple_recommendations(profile),
            'timestamp': datetime.now().isoformat()
        }

    def _run_ab_test(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run A/B test and select variant"""
        user_id = input_data.get('user_id')
        test_id = input_data.get('test_id')

        if not user_id or not test_id:
            return {'success': False, 'error': 'user_id and test_id required'}

        # Get or create A/B test
        if test_id not in self.ab_tests:
            # Create new test (in production, would load from database)
            self.ab_tests[test_id] = {
                'test_id': test_id,
                'variants': ['A', 'B'],
                'assignments': {},
                'results': {'A': {'conversions': 0, 'views': 0}, 'B': {'conversions': 0, 'views': 0}}
            }

        test = self.ab_tests[test_id]

        # Check if user already assigned
        if user_id in test['assignments']:
            variant = test['assignments'][user_id]
        else:
            # Assign variant (50/50 split)
            import random
            variant = random.choice(test['variants'])
            test['assignments'][user_id] = variant

        # Track view
        test['results'][variant]['views'] += 1

        return {
            'success': True,
            'user_id': user_id,
            'test_id': test_id,
            'variant': variant,
            'test_stats': {
                'total_users': len(test['assignments']),
                'variant_stats': test['results']
            },
            'timestamp': datetime.now().isoformat()
        }

    def _segment_user(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine user segment"""
        user_id = input_data.get('user_id')

        if not user_id:
            return {'success': False, 'error': 'user_id required'}

        profile = self._get_or_create_profile(user_id)
        segment = self._determine_segment(profile)
        segment_attributes = self._get_segment_attributes(segment)

        return {
            'success': True,
            'user_id': user_id,
            'segment': segment,
            'segment_attributes': segment_attributes,
            'profile_summary': {
                'engagement_score': profile.get('engagement_score', 0),
                'total_revenue': profile.get('total_revenue', 0),
                'total_purchases': profile.get('total_purchases', 0),
                'account_age_days': profile.get('account_age_days', 0)
            },
            'timestamp': datetime.now().isoformat()
        }

    def _generate_recommendations(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized recommendations"""
        user_id = input_data.get('user_id')
        recommendation_type = input_data.get('recommendation_type', 'product')

        if not user_id:
            return {'success': False, 'error': 'user_id required'}

        profile = self._get_or_create_profile(user_id)
        segment = self._determine_segment(profile)

        # Generate recommendations based on profile and segment
        recommendations = self._create_recommendations(profile, segment, recommendation_type)

        return {
            'success': True,
            'user_id': user_id,
            'recommendation_type': recommendation_type,
            'recommendations': recommendations,
            'segment': segment,
            'personalization_factors': {
                'interests': profile.get('interests', []),
                'past_purchases': profile.get('total_purchases', 0),
                'engagement_level': 'high' if profile.get('engagement_score', 0) >= 70 else 'medium'
            },
            'timestamp': datetime.now().isoformat()
        }

    # Helper methods

    def _get_or_create_profile(self, user_id: str) -> Dict[str, Any]:
        """Get existing profile or create new one"""
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]

        # Create new profile
        profile = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'total_interactions': 0,
            'email_opens': 0,
            'link_clicks': 0,
            'page_views': 0,
            'pages_viewed': [],
            'total_purchases': 0,
            'total_revenue': 0,
            'engagement_score': 50,  # Default neutral
            'interests': [],
            'preferences': {},
            'account_age_days': 0
        }

        self.user_profiles[user_id] = profile
        return profile

    def _determine_segment(self, profile: Dict[str, Any]) -> str:
        """Determine which segment user belongs to"""
        engagement = profile.get('engagement_score', 0)
        ltv = profile.get('total_revenue', 0)
        account_age = profile.get('account_age_days', 0)
        days_since_activity = 0  # Would calculate from last_activity timestamp

        # Check segments in priority order
        if ltv >= self.segments['champion']['min_ltv']:
            return 'champion'
        elif ltv >= self.segments['high_value']['min_ltv'] and engagement >= self.segments['high_value']['min_engagement']:
            return 'high_value'
        elif engagement >= self.segments['engaged']['min_engagement']:
            return 'engaged'
        elif account_age <= self.segments['new_user']['account_age_days']:
            return 'new_user'
        elif engagement <= self.segments['at_risk']['max_engagement']:
            return 'at_risk'
        else:
            return 'standard'

    def _calculate_engagement_score(self, profile: Dict[str, Any]) -> int:
        """Calculate engagement score (0-100)"""
        # Weighted scoring
        email_score = min(profile.get('email_opens', 0) * 5, 25)
        click_score = min(profile.get('link_clicks', 0) * 10, 25)
        page_score = min(profile.get('page_views', 0) * 2, 25)
        purchase_score = min(profile.get('total_purchases', 0) * 25, 25)

        total_score = email_score + click_score + page_score + purchase_score
        return min(100, int(total_score))

    def _extract_interests(self, profile: Dict[str, Any]) -> List[str]:
        """Extract user interests from behavior"""
        interests = []
        pages = profile.get('pages_viewed', [])

        # Simple keyword extraction from pages viewed
        for page in pages:
            if 'pricing' in page.lower():
                interests.append('pricing')
            elif 'demo' in page.lower():
                interests.append('product_demo')
            elif 'feature' in page.lower():
                interests.append('features')
            elif 'integration' in page.lower():
                interests.append('integrations')

        # Return unique interests
        return list(set(interests))[:5]

    def _select_strategy(self, content_type: str, segment: str, context: Dict) -> str:
        """Select personalization strategy"""
        # Strategy selection based on segment and content type
        strategies = {
            'champion': 'vip_treatment',
            'high_value': 'premium_offers',
            'engaged': 'feature_highlights',
            'new_user': 'onboarding_focus',
            'at_risk': 'win_back',
            'standard': 'value_demonstration'
        }

        return strategies.get(segment, 'standard_personalization')

    def _generate_personalized_content(
        self,
        content_type: str,
        profile: Dict,
        segment: str,
        strategy: str,
        context: Dict
    ) -> Dict[str, Any]:
        """Generate personalized content"""

        if content_type == 'email':
            return self._personalize_email(profile, segment, strategy)
        elif content_type == 'landing_page':
            return self._personalize_landing_page(profile, segment, strategy)
        elif content_type == 'product_recommendation':
            return self._personalize_recommendations(profile, segment)
        else:
            return self._personalize_generic(profile, segment, strategy)

    def _personalize_email(self, profile: Dict, segment: str, strategy: str) -> Dict:
        """Personalize email content"""
        templates = {
            'champion': {
                'subject': 'Exclusive VIP Update Just For You',
                'greeting': 'Dear Valued Partner,',
                'tone': 'exclusive',
                'cta': 'Access Your VIP Benefits'
            },
            'high_value': {
                'subject': 'Premium Features You\'ll Love',
                'greeting': 'Hi there,',
                'tone': 'premium',
                'cta': 'Explore Premium Features'
            },
            'engaged': {
                'subject': 'New Features Based on Your Activity',
                'greeting': 'Hello,',
                'tone': 'friendly',
                'cta': 'Try These New Features'
            },
            'new_user': {
                'subject': 'Welcome! Here\'s How to Get Started',
                'greeting': 'Welcome aboard!',
                'tone': 'helpful',
                'cta': 'Complete Your Setup'
            },
            'at_risk': {
                'subject': 'We Miss You - Special Offer Inside',
                'greeting': 'We\'ve missed you!',
                'tone': 'concerned',
                'cta': 'Come Back and Save 20%'
            }
        }

        template = templates.get(segment, templates['engaged'])

        return {
            'subject': template['subject'],
            'greeting': template['greeting'],
            'body': f"Personalized content for {segment} segment with {strategy} strategy",
            'cta': template['cta'],
            'tone': template['tone']
        }

    def _personalize_landing_page(self, profile: Dict, segment: str, strategy: str) -> Dict:
        """Personalize landing page content"""
        return {
            'headline': self._get_segment_headline(segment),
            'hero_image': f'hero_{segment}.jpg',
            'primary_cta': self._get_segment_cta(segment),
            'social_proof': segment in ['new_user', 'at_risk'],
            'urgency': segment == 'at_risk',
            'personalized_offers': self._get_segment_offers(segment)
        }

    def _personalize_recommendations(self, profile: Dict, segment: str) -> Dict:
        """Personalize product recommendations"""
        return {
            'recommendations': self._create_recommendations(profile, segment, 'product'),
            'reasoning': f'Based on your {segment} profile',
            'confidence': self._calculate_confidence(profile)
        }

    def _personalize_generic(self, profile: Dict, segment: str, strategy: str) -> Dict:
        """Generic personalization"""
        return {
            'personalized': True,
            'segment': segment,
            'strategy': strategy,
            'user_interests': profile.get('interests', []),
            'engagement_level': 'high' if profile.get('engagement_score', 0) >= 70 else 'medium'
        }

    def _get_segment_headline(self, segment: str) -> str:
        """Get segment-specific headline"""
        headlines = {
            'champion': 'Welcome Back, Valued Partner',
            'high_value': 'Premium Solutions for Your Business',
            'engaged': 'Take Your Results to the Next Level',
            'new_user': 'Get Started in Minutes',
            'at_risk': 'We Want You Back - Here\'s Why',
            'standard': 'Transform Your Business with AI'
        }
        return headlines.get(segment, headlines['standard'])

    def _get_segment_cta(self, segment: str) -> str:
        """Get segment-specific CTA"""
        ctas = {
            'champion': 'Access VIP Dashboard',
            'high_value': 'Upgrade to Enterprise',
            'engaged': 'Unlock Advanced Features',
            'new_user': 'Start Free Trial',
            'at_risk': 'Reactivate with 20% Off',
            'standard': 'Get Started Free'
        }
        return ctas.get(segment, ctas['standard'])

    def _get_segment_offers(self, segment: str) -> List[str]:
        """Get segment-specific offers"""
        offers = {
            'champion': ['Priority Support', 'Beta Access', 'Custom Integration'],
            'high_value': ['Advanced Analytics', 'API Access', 'Dedicated Manager'],
            'engaged': ['Premium Features', 'Integrations', 'Advanced Reports'],
            'new_user': ['Free Trial', 'Quick Setup', 'Training Resources'],
            'at_risk': ['20% Discount', 'Free Consultation', 'Migration Help']
        }
        return offers.get(segment, ['Free Trial', 'Support', 'Documentation'])

    def _create_recommendations(self, profile: Dict, segment: str, rec_type: str) -> List[Dict]:
        """Create personalized recommendations"""
        recommendations = []

        interests = profile.get('interests', [])

        # Base recommendations on segment and interests
        if 'pricing' in interests:
            recommendations.append({
                'type': 'content',
                'title': 'ROI Calculator',
                'reason': 'Based on your interest in pricing',
                'priority': 'high'
            })

        if 'product_demo' in interests:
            recommendations.append({
                'type': 'action',
                'title': 'Schedule Demo',
                'reason': 'Continue your product exploration',
                'priority': 'high'
            })

        if segment == 'new_user':
            recommendations.append({
                'type': 'guide',
                'title': 'Getting Started Guide',
                'reason': 'Perfect for new users',
                'priority': 'critical'
            })

        # Ensure at least 3 recommendations
        while len(recommendations) < 3:
            recommendations.append({
                'type': 'content',
                'title': 'Customer Success Stories',
                'reason': 'See how others succeed',
                'priority': 'medium'
            })

        return recommendations[:5]  # Max 5 recommendations

    def _generate_simple_recommendations(self, profile: Dict) -> List[str]:
        """Generate simple recommendation list"""
        segment = self._determine_segment(profile)
        recs = self._create_recommendations(profile, segment, 'general')
        return [rec['title'] for rec in recs]

    def _get_segment_attributes(self, segment: str) -> Dict[str, Any]:
        """Get attributes for a segment"""
        return self.segments.get(segment, {})

    def _calculate_confidence(self, profile: Dict) -> float:
        """Calculate confidence in personalization"""
        # More interactions = higher confidence
        interactions = profile.get('total_interactions', 0)

        if interactions >= 50:
            return 0.95
        elif interactions >= 20:
            return 0.85
        elif interactions >= 10:
            return 0.75
        elif interactions >= 5:
            return 0.65
        else:
            return 0.50

    def _track_personalization(self, user_id: str, content_type: str, strategy: str):
        """Track personalization event"""
        # Would log to central logger in production
        self.logger.info(f"Personalization: user={user_id}, type={content_type}, strategy={strategy}")

    def _load_personalization_rules(self) -> Dict[str, Any]:
        """Load personalization rules"""
        # In production, would load from configuration
        return {
            'email_frequency': {
                'champion': 'weekly',
                'high_value': 'bi-weekly',
                'engaged': 'weekly',
                'new_user': 'daily',
                'at_risk': 'monthly'
            },
            'content_depth': {
                'champion': 'advanced',
                'high_value': 'advanced',
                'engaged': 'intermediate',
                'new_user': 'beginner',
                'at_risk': 'beginner'
            }
        }


if __name__ == "__main__":
    print("\n" + "="*80)
    print("Testing Phase 4 Advanced Personalization Agent")
    print("="*80 + "\n")

    agent = Phase4AdvancedPersonalizationAgent()

    # Test 1: Create and update profile
    print("Test 1: Profile creation and behavior tracking")
    print("-"*80)

    result = agent.process({
        'action': 'update_profile',
        'user_id': 'user_123',
        'behavior_data': {
            'email_opened': True,
            'link_clicked': True,
            'page_viewed': '/features',
            'interactions': 1
        }
    })

    print(f"✓ Profile updated: {result['user_id']}")
    print(f"  Engagement score: {result['engagement_score']}")
    print(f"  Segment: {result['segment']}")

    # Test 2: Personalize content
    print("\nTest 2: Content personalization")
    print("-"*80)

    result = agent.process({
        'action': 'personalize_content',
        'user_id': 'user_123',
        'content_type': 'email',
        'context': {}
    })

    print(f"✓ Content personalized")
    print(f"  Strategy: {result['strategy']}")
    print(f"  Email subject: {result['personalized_content']['subject']}")
    print(f"  CTA: {result['personalized_content']['cta']}")

    # Test 3: A/B testing
    print("\nTest 3: A/B testing")
    print("-"*80)

    result = agent.process({
        'action': 'ab_test',
        'user_id': 'user_456',
        'test_id': 'homepage_hero_test'
    })

    print(f"✓ A/B test variant assigned: {result['variant']}")
    print(f"  Test stats: {result['test_stats']}")

    # Test 4: Recommendations
    print("\nTest 4: Personalized recommendations")
    print("-"*80)

    result = agent.process({
        'action': 'recommend',
        'user_id': 'user_123',
        'recommendation_type': 'content'
    })

    print(f"✓ Recommendations generated: {len(result['recommendations'])}")
    for rec in result['recommendations']:
        print(f"  - {rec['title']} ({rec['priority']})")

    print("\n" + "="*80)
    print("Advanced Personalization Agent Tests Complete!")
    print("="*80)
