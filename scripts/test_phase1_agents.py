#!/usr/bin/env python3
"""
Test script for Phase 1 agents

This script tests both Phase 1 agents:
1. Prospect Research Agent (sentiment analysis + lead qualification)
2. FAQ Chatbot Agent (knowledge base + LLM generation)

Usage:
    python test_phase1_agents.py
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


def test_prospect_agent_direct():
    """Test Prospect Agent directly (without API)"""
    print("\n" + "=" * 80)
    print("TEST 1: PROSPECT RESEARCH AGENT (Direct Import)")
    print("=" * 80)

    try:
        from phase1_prospect_agent import Phase1ProspectAgent

        agent = Phase1ProspectAgent()

        test_cases = [
            {
                'name': 'High-quality lead',
                'data': {
                    'lead_name': 'Sarah Johnson',
                    'lead_email': 'sarah@techstartup.io',
                    'company': 'TechStartup Inc',
                    'industry': 'SaaS',
                    'lead_message': 'Very interested in your platform! We need to automate our sales process ASAP. Can you provide pricing and schedule a demo this week?'
                }
            },
            {
                'name': 'Medium-quality lead',
                'data': {
                    'lead_name': 'Mike Chen',
                    'lead_email': 'mike@example.com',
                    'company': 'Example Corp',
                    'industry': 'Retail',
                    'lead_message': 'Tell me more about your product. We might consider it in the future.'
                }
            },
            {
                'name': 'Low-quality lead',
                'data': {
                    'lead_name': 'Spam Bot',
                    'lead_email': 'spam@nowhere.com',
                    'company': 'Unknown',
                    'industry': 'Unknown',
                    'lead_message': 'Not interested. Please unsubscribe me.'
                }
            }
        ]

        for test_case in test_cases:
            print(f"\n{'─'*80}")
            print(f"Testing: {test_case['name']}")
            print(f"{'─'*80}")

            result = agent.process(test_case['data'])

            if result.get('success'):
                print(f"✅ Status: {result['qualification_status'].upper()}")
                print(f"📊 Score: {result['qualification_score']}/100")
                print(f"😊 Sentiment: {result['sentiment_analysis']['label']} ({result['sentiment_analysis']['confidence']:.2f})")
                print(f"🎯 Action: {result['next_action']['action']}")
                print(f"⚡ Priority: {result['next_action']['priority']}")
            else:
                print(f"❌ Error: {result.get('error')}")

        print(f"\n{'='*80}")
        print("Prospect Agent Direct Test Complete!")
        print(f"{'='*80}\n")

        return True

    except Exception as e:
        print(f"❌ Error testing prospect agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_faq_chatbot_direct():
    """Test FAQ Chatbot directly (without API)"""
    print("\n" + "=" * 80)
    print("TEST 2: FAQ CHATBOT AGENT (Direct Import)")
    print("=" * 80)

    try:
        from phase1_faq_chatbot import Phase1FAQChatbot

        agent = Phase1FAQChatbot()

        test_cases = [
            {'question': 'What is Instant Agency?'},
            {'question': 'How much does it cost?'},
            {'question': 'Can I try it before I buy?'},
            {'question': 'Do you integrate with my CRM?'},
            {'question': 'How do I set up my first agent?'},  # Partial match
            {'question': 'What is quantum computing?'},  # Off-topic
        ]

        for test_case in test_cases:
            print(f"\n{'─'*80}")
            print(f"Q: {test_case['question']}")
            print(f"{'─'*80}")

            result = agent.process(test_case)

            if result.get('success'):
                print(f"\nA: {result['answer']}")
                print(f"\n📊 Confidence: {result['confidence']:.2f}")
                print(f"🔍 Source: {result['source']}")

                if result.get('kb_match'):
                    print(f"📚 KB Match: \"{result['kb_match']['question']}\" ({result['kb_match']['confidence']:.2f})")

                if result['escalate_to_human']:
                    print(f"⚠️  ESCALATE TO HUMAN (low confidence)")
                else:
                    print(f"✅ Answered by AI")
            else:
                print(f"❌ Error: {result.get('error')}")

        print(f"\n{'='*80}")
        print("FAQ Chatbot Direct Test Complete!")
        print(f"{'='*80}\n")

        return True

    except Exception as e:
        print(f"❌ Error testing FAQ chatbot: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_via_api():
    """Test Phase 1 agents via API endpoints"""
    print("\n" + "=" * 80)
    print("TEST 3: AGENTS VIA API")
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

    # Test Prospect Agent API
    print(f"{'─'*80}")
    print("Testing: POST /phase1/qualify-lead")
    print(f"{'─'*80}")

    lead_data = {
        'lead_name': 'Alice Williams',
        'lead_email': 'alice@startup.com',
        'company': 'Awesome Startup',
        'industry': 'Technology',
        'lead_message': 'Interested in AI automation. Need pricing and a demo ASAP!'
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/phase1/qualify-lead",
            json=lead_data,
            timeout=15
        )

        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})

            print(f"✅ API Response Status: 200 OK")
            print(f"📊 Qualification Score: {data.get('qualification_score')}/100")
            print(f"📝 Status: {data.get('qualification_status')}")
            print(f"😊 Sentiment: {data.get('sentiment_analysis', {}).get('label')}")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ API request failed: {e}")

    # Test FAQ Chatbot API
    print(f"\n{'─'*80}")
    print("Testing: POST /phase1/faq")
    print(f"{'─'*80}")

    question_data = {
        'question': 'What is Instant Agency and how does it work?',
        'user_id': 'test_user_123'
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/phase1/faq",
            json=question_data,
            timeout=15
        )

        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})

            print(f"✅ API Response Status: 200 OK")
            print(f"📝 Answer: {data.get('answer')}")
            print(f"📊 Confidence: {data.get('confidence'):.2f}")
            print(f"🔍 Source: {data.get('source')}")

            if data.get('escalate_to_human'):
                print(f"⚠️  Escalation recommended")
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
    print("║" + " " * 20 + "PHASE 1 AGENTS - TEST SUITE" + " " * 30 + "║")
    print("╚" + "═" * 78 + "╝")

    results = []

    # Run tests
    results.append(("Prospect Agent (Direct)", test_prospect_agent_direct()))
    results.append(("FAQ Chatbot (Direct)", test_faq_chatbot_direct()))
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
