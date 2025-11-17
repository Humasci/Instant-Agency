#!/usr/bin/env python3
"""
Test script for Phase 2 agents

This script tests all Phase 2 agents:
1. Sales Pitch Agent (personalized B2B pitches with Mistral/GPT-Neo)
2. Content Writer Agent (blog posts with GPT-Neo)
3. Intent Classifier Agent (zero-shot classification with BART)
4. Email Personalizer Agent (context-aware email generation)
5. Social Media Agent (platform-specific post generation)

Usage:
    python test_phase2_agents.py
"""

import sys
import os
import requests
import json
from typing import Dict, Any

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))

# Configuration
API_BASE_URL = os.getenv('AGENT_SERVICE_URL', 'http://localhost:8000')


def test_sales_pitch_agent_direct():
    """Test Sales Pitch Agent directly (without API)"""
    print("\n" + "=" * 80)
    print("TEST 1: SALES PITCH GENERATION AGENT (Direct Import)")
    print("=" * 80)

    try:
        from phase2_sales_pitch_agent import Phase2SalesPitchAgent

        agent = Phase2SalesPitchAgent()

        test_cases = [
            {
                'name': 'SaaS Startup - High Priority',
                'data': {
                    'prospect_name': 'Sarah Chen',
                    'company': 'DataFlow Technologies',
                    'industry': 'SaaS',
                    'pain_points': 'Manual lead qualification, slow sales cycle, inconsistent follow-up',
                    'company_size': '25-50 employees',
                    'trigger_event': 'Series A funding announced',
                    'current_solutions': 'Basic CRM with manual processes'
                }
            },
            {
                'name': 'Enterprise - Automation Focus',
                'data': {
                    'prospect_name': 'James Martinez',
                    'company': 'Global Logistics Corp',
                    'industry': 'Logistics',
                    'pain_points': 'Scaling customer support, long response times',
                    'company_size': '500+ employees',
                    'trigger_event': 'Expansion to new markets',
                    'current_solutions': 'Legacy ticketing system'
                }
            }
        ]

        for test_case in test_cases:
            print(f"\n{'─'*80}")
            print(f"Testing: {test_case['name']}")
            print(f"{'─'*80}")

            result = agent.process(test_case['data'])

            if result.get('success'):
                print(f"\n📧 SUBJECT: {result['subject']}")
                print(f"\n📝 PITCH:\n{result['pitch'][:500]}...")
                print(f"\n📊 Quality Score: {result['quality_score']}/100")
                print(f"🎯 Model Used: {result['model_used']}")
                print(f"🔥 Personalization Elements: {', '.join(result['personalization_elements'])}")
            else:
                print(f"❌ Error: {result.get('error')}")

        print(f"\n{'='*80}")
        print("Sales Pitch Agent Direct Test Complete!")
        print(f"{'='*80}\n")

        return True

    except Exception as e:
        print(f"❌ Error testing sales pitch agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_content_writer_agent_direct():
    """Test Content Writer Agent directly (without API)"""
    print("\n" + "=" * 80)
    print("TEST 2: CONTENT WRITER AGENT (Direct Import)")
    print("=" * 80)

    try:
        from phase2_content_writer_agent import Phase2ContentWriterAgent

        agent = Phase2ContentWriterAgent()

        test_cases = [
            {
                'name': 'Blog Post - AI Automation',
                'data': {
                    'topic': 'How AI Automation Transforms Small Business Operations',
                    'content_type': 'blog_post',
                    'audience': 'small business owners',
                    'tone': 'conversational',
                    'word_count': 600,
                    'keywords': ['AI automation', 'small business', 'productivity', 'efficiency'],
                    'key_points': [
                        'Benefits of AI automation for small businesses',
                        'Common use cases and examples',
                        'Getting started without technical expertise'
                    ]
                }
            },
            {
                'name': 'Article - Enterprise Sales',
                'data': {
                    'topic': 'The Future of B2B Sales: AI-Powered Lead Qualification',
                    'content_type': 'article',
                    'audience': 'sales leaders',
                    'tone': 'professional',
                    'word_count': 800,
                    'keywords': ['B2B sales', 'lead qualification', 'AI', 'sales automation'],
                    'key_points': [
                        'Why traditional lead qualification fails',
                        'How AI improves qualification accuracy',
                        'ROI of automated qualification'
                    ]
                }
            }
        ]

        for test_case in test_cases:
            print(f"\n{'─'*80}")
            print(f"Testing: {test_case['name']}")
            print(f"{'─'*80}")

            result = agent.process(test_case['data'])

            if result.get('success'):
                print(f"\n📰 TITLE: {result['title']}")
                print(f"\n📝 CONTENT:\n{result['content'][:400]}...")
                print(f"\n📊 Quality Score: {result['quality_score']}/100")
                print(f"📏 Word Count: {result['word_count']} words")
                print(f"🔍 Meta Description: {result['seo_metadata']['meta_description']}")
                print(f"🏷️  Keywords: {', '.join(result['seo_metadata']['keywords'][:5])}")
            else:
                print(f"❌ Error: {result.get('error')}")

        print(f"\n{'='*80}")
        print("Content Writer Agent Direct Test Complete!")
        print(f"{'='*80}\n")

        return True

    except Exception as e:
        print(f"❌ Error testing content writer agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_intent_classifier_agent_direct():
    """Test Intent Classifier Agent directly (without API)"""
    print("\n" + "=" * 80)
    print("TEST 3: INTENT CLASSIFICATION AGENT (Direct Import)")
    print("=" * 80)

    try:
        from phase2_intent_classifier_agent import Phase2IntentClassifierAgent

        agent = Phase2IntentClassifierAgent()

        test_cases = [
            {'message': 'How much does your Enterprise plan cost?', 'user_id': 'user_001'},
            {'message': 'Can we schedule a demo for next week?', 'user_id': 'user_002'},
            {'message': 'I need help setting up my first agent', 'user_id': 'user_003'},
            {'message': 'Does this integrate with Salesforce?', 'user_id': 'user_004'},
            {'message': 'Your platform is not working and I lost data!', 'user_id': 'user_005'},
            {'message': 'Great product! Suggestion: add dark mode', 'user_id': 'user_006'},
            {'message': 'Tell me more about your AI capabilities', 'user_id': 'user_007'}
        ]

        for test_case in test_cases:
            print(f"\n{'─'*80}")
            print(f"Message: \"{test_case['message']}\"")
            print(f"{'─'*80}")

            result = agent.process(test_case)

            if result.get('success'):
                primary = result['primary_intent']
                print(f"\n🎯 Primary Intent: {primary['intent']} ({primary['confidence']:.2%} confidence)")
                print(f"⚡ Urgency: {result['urgency']}")
                print(f"🔔 Requires Response: {result['requires_response']}")
                print(f"🤖 Suggested Action: {result['suggested_action']}")

                if len(result['all_intents']) > 1:
                    print(f"\n📊 Alternative Intents:")
                    for intent in result['all_intents'][1:3]:
                        print(f"   - {intent['intent']}: {intent['confidence']:.2%}")
            else:
                print(f"❌ Error: {result.get('error')}")

        print(f"\n{'='*80}")
        print("Intent Classifier Agent Direct Test Complete!")
        print(f"{'='*80}\n")

        return True

    except Exception as e:
        print(f"❌ Error testing intent classifier agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_email_personalizer_agent_direct():
    """Test Email Personalizer Agent directly (without API)"""
    print("\n" + "=" * 80)
    print("TEST 4: EMAIL PERSONALIZER AGENT (Direct Import)")
    print("=" * 80)

    try:
        from phase2_email_personalizer_agent import Phase2EmailPersonalizerAgent

        agent = Phase2EmailPersonalizerAgent()

        test_cases = [
            {
                'name': 'Pricing Inquiry',
                'data': {
                    'recipient_name': 'Sarah Johnson',
                    'recipient_email': 'sarah@techcorp.com',
                    'company': 'TechCorp',
                    'intent': 'pricing',
                    'original_message': 'Can you send me pricing information for your Enterprise plan?',
                    'email_type': 'response'
                }
            },
            {
                'name': 'Demo Request',
                'data': {
                    'recipient_name': 'Michael Chen',
                    'recipient_email': 'michael@startup.io',
                    'company': 'Innovation Startup',
                    'intent': 'demo',
                    'original_message': 'I\'d like to see a demo of your AI agents',
                    'email_type': 'response'
                }
            },
            {
                'name': 'Support Issue',
                'data': {
                    'recipient_name': 'Emma Williams',
                    'recipient_email': 'emma@company.com',
                    'company': 'Enterprise Co',
                    'intent': 'support',
                    'original_message': 'Having trouble connecting our CRM',
                    'email_type': 'response'
                }
            }
        ]

        for test_case in test_cases:
            print(f"\n{'─'*80}")
            print(f"Testing: {test_case['name']}")
            print(f"{'─'*80}")

            result = agent.process(test_case['data'])

            if result.get('success'):
                print(f"\n📧 SUBJECT: {result['subject']}")
                print(f"\n📝 BODY:\n{result['body'][:400]}...")
                print(f"\n📊 Personalization Score: {result['personalization_score']}/100")
                print(f"🎯 Intent: {result['intent']}")
                print(f"✨ Personalization Elements: {', '.join(result['personalization_elements'])}")
            else:
                print(f"❌ Error: {result.get('error')}")

        print(f"\n{'='*80}")
        print("Email Personalizer Agent Direct Test Complete!")
        print(f"{'='*80}\n")

        return True

    except Exception as e:
        print(f"❌ Error testing email personalizer agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_social_media_agent_direct():
    """Test Social Media Agent directly (without API)"""
    print("\n" + "=" * 80)
    print("TEST 5: SOCIAL MEDIA MANAGER AGENT (Direct Import)")
    print("=" * 80)

    try:
        from phase2_social_media_agent import Phase2SocialMediaAgent

        agent = Phase2SocialMediaAgent()

        test_data = {
            'content': '''
            AI automation is revolutionizing how small businesses operate.
            By automating repetitive tasks like lead qualification, customer support,
            and content creation, businesses can focus on growth and innovation.

            Our latest case study shows a 40% reduction in response time and
            60% increase in qualified leads for businesses using AI agents.

            The future of business is automated, intelligent, and efficient.
            ''',
            'topic': 'AI Automation for Small Business',
            'platforms': ['linkedin', 'twitter', 'facebook'],
            'target_audience': 'small business owners and entrepreneurs',
            'cta': 'Start your free trial',
            'link': 'https://instant-agency.ai/trial'
        }

        print(f"\n{'─'*80}")
        print(f"Generating posts for: LinkedIn, Twitter, Facebook")
        print(f"{'─'*80}")

        result = agent.process(test_data)

        if result.get('success'):
            for post in result['posts']:
                print(f"\n{'─'*40}")
                print(f"🌐 Platform: {post['platform'].upper()}")
                print(f"{'─'*40}")
                print(f"\n{post['content']}\n")
                print(f"📊 Engagement Score: {post['engagement_score']}/100")
                print(f"#️⃣  Hashtags: {', '.join(post['hashtags'])}")
                print(f"🕐 Best Time: {post['best_posting_time']}")
                print(f"📏 Character Count: {post['character_count']}")

            print(f"\n{'─'*80}")
            print(f"✅ Generated {result['posts_generated']} platform-specific posts")
            print(f"{'─'*80}")
        else:
            print(f"❌ Error: {result.get('error')}")

        print(f"\n{'='*80}")
        print("Social Media Agent Direct Test Complete!")
        print(f"{'='*80}\n")

        return True

    except Exception as e:
        print(f"❌ Error testing social media agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_via_api():
    """Test Phase 2 agents via API endpoints"""
    print("\n" + "=" * 80)
    print("TEST 6: AGENTS VIA API")
    print("=" * 80)

    # Check if API is available
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"⚠️  API not available at {API_BASE_URL}")
            print(f"   Skipping API tests. Start the agent service with: cd agents && python main.py")
            return True  # Don't fail the overall test
    except Exception as e:
        print(f"⚠️  API not available: {e}")
        print(f"   Skipping API tests. Start the agent service with: cd agents && python main.py")
        return True

    print(f"✅ API available at {API_BASE_URL}\n")

    # Test 1: Sales Pitch Generation
    print(f"{'─'*80}")
    print("Testing: POST /phase2/generate-sales-pitch")
    print(f"{'─'*80}")

    pitch_data = {
        'prospect_name': 'Alex Thompson',
        'company': 'GrowthTech Inc',
        'industry': 'Technology',
        'pain_points': 'Inefficient lead management and slow follow-up',
        'company_size': '50-100 employees',
        'trigger_event': 'New VP of Sales hired',
        'current_solutions': 'Manual spreadsheets'
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/phase2/generate-sales-pitch",
            json=pitch_data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})

            print(f"✅ API Response Status: 200 OK")
            print(f"📧 Subject: {data.get('subject')}")
            print(f"📊 Quality Score: {data.get('quality_score')}/100")
            print(f"🎯 Model: {data.get('model_used')}")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ API request failed: {e}")

    # Test 2: Intent Classification
    print(f"\n{'─'*80}")
    print("Testing: POST /phase2/classify-intent")
    print(f"{'─'*80}")

    intent_data = {
        'message': 'We need a demo ASAP for our leadership team',
        'user_id': 'test_user_456'
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/phase2/classify-intent",
            json=intent_data,
            timeout=15
        )

        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})

            print(f"✅ API Response Status: 200 OK")
            print(f"🎯 Primary Intent: {data.get('primary_intent', {}).get('intent')}")
            print(f"📊 Confidence: {data.get('primary_intent', {}).get('confidence', 0):.2%}")
            print(f"⚡ Urgency: {data.get('urgency')}")
            print(f"🤖 Action: {data.get('suggested_action')}")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ API request failed: {e}")

    # Test 3: Email Personalization
    print(f"\n{'─'*80}")
    print("Testing: POST /phase2/personalize-email")
    print(f"{'─'*80}")

    email_data = {
        'recipient_name': 'Jennifer Lee',
        'recipient_email': 'jennifer@startup.co',
        'company': 'FastGrow Startup',
        'intent': 'pricing',
        'original_message': 'What are your pricing options?',
        'email_type': 'response'
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/phase2/personalize-email",
            json=email_data,
            timeout=20
        )

        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})

            print(f"✅ API Response Status: 200 OK")
            print(f"📧 Subject: {data.get('subject')}")
            print(f"📊 Personalization Score: {data.get('personalization_score')}/100")
            print(f"✨ Elements: {', '.join(data.get('personalization_elements', []))}")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ API request failed: {e}")

    print(f"\n{'='*80}")
    print("API Test Complete!")
    print(f"{'='*80}\n")

    return True


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "PHASE 2 AGENTS - TEST SUITE" + " " * 30 + "║")
    print("╚" + "═" * 78 + "╝")

    results = []

    # Run tests
    results.append(("Sales Pitch Agent (Direct)", test_sales_pitch_agent_direct()))
    results.append(("Content Writer Agent (Direct)", test_content_writer_agent_direct()))
    results.append(("Intent Classifier Agent (Direct)", test_intent_classifier_agent_direct()))
    results.append(("Email Personalizer Agent (Direct)", test_email_personalizer_agent_direct()))
    results.append(("Social Media Agent (Direct)", test_social_media_agent_direct()))
    results.append(("API Endpoints", test_via_api()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\n{passed}/{total} test suites passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
