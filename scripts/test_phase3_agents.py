#!/usr/bin/env python3
"""
Test script for Phase 3 agents

This script tests all Phase 3 collaborative agents:
1. Orchestrator Agent (multi-agent workflow coordination)
2. RAG Research Agent (retrieval-augmented research)
3. Sales Strategist Agent (advanced sales workflows)
4. Marketing Campaign Agent (end-to-end campaign planning)
5. Customer Success Agent (retention and expansion)
6. Analytics Agent (reporting and insights)

Usage:
    python test_phase3_agents.py
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


def test_orchestrator_agent():
    """Test Orchestrator Agent"""
    print("\n" + "=" * 80)
    print("TEST 1: ORCHESTRATOR AGENT")
    print("=" * 80)

    try:
        from phase3_orchestrator_agent import Phase3OrchestratorAgent
        agent = Phase3OrchestratorAgent()

        # Test high-engagement lead nurture workflow
        print("\n" + "-" * 80)
        print("Test 1a: High Engagement Lead Nurture Workflow")
        print("-" * 80)

        result = agent.process({
            'customer_id': 'lead_001',
            'workflow_type': 'lead_nurture',
            'journey_stage': 'consideration',
            'engagement_score': 85,
            'current_state': {
                'name': 'Sarah Chen',
                'company': 'TechCorp',
                'industry': 'SaaS'
            }
        })

        if result.get('success'):
            print(f"✅ Workflow: {result['workflow_type']}")
            print(f"📊 Steps Executed: {len(result.get('steps_executed', []))}")
            print(f"🎯 Next Actions: {len(result.get('next_actions', []))}")
            print(f"🚨 Human Handoff: {result.get('human_handoff')}")
            print(f"💡 Recommendation: {result.get('context', {}).get('recommendation')}")
        else:
            print(f"❌ Error: {result.get('error')}")

        # Test high-value sales cycle
        print("\n" + "-" * 80)
        print("Test 1b: High Value Sales Cycle Workflow")
        print("-" * 80)

        result = agent.process({
            'customer_id': 'prospect_002',
            'workflow_type': 'sales_cycle',
            'journey_stage': 'decision',
            'deal_size': 25000,
            'current_state': {
                'name': 'John Smith',
                'company': 'Enterprise Inc'
            }
        })

        if result.get('success'):
            print(f"✅ Deal Size: ${result['context']['deal_size']:,}")
            print(f"🔥 High Value? {result.get('human_handoff')}")
            print(f"📋 Next Actions: {len(result.get('next_actions', []))}")

        print("\n✓ Orchestrator Agent Tests Complete")
        return True

    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_research_agent():
    """Test RAG Research Agent"""
    print("\n" + "=" * 80)
    print("TEST 2: RAG RESEARCH AGENT")
    print("=" * 80)

    try:
        from phase3_rag_research_agent import Phase3RAGResearchAgent
        agent = Phase3RAGResearchAgent()

        test_queries = [
            "AI automation benefits for small businesses",
            "How can AI accelerate sales cycles",
            "email personalization and engagement"
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"\n{'-'*80}")
            print(f"Test 2{chr(96+i)}: Research - {query}")
            print(f"{'-'*80}")

            result = agent.process({
                'query': query,
                'depth': 'standard',
                'max_results': 3,
                'include_citations': True
            })

            if result.get('success'):
                print(f"✅ Query: {result['query']}")
                print(f"📊 Results Found: {result['results_count']}")
                print(f"💡 Confidence: {result['confidence']:.2%}")
                print(f"🔍 Key Findings: {len(result['key_findings'])}")
                for finding in result['key_findings'][:2]:
                    print(f"   • {finding}")
            else:
                print(f"❌ Error: {result.get('error')}")

        print("\n✓ RAG Research Agent Tests Complete")
        return True

    except Exception as e:
        print(f"❌ RAG Research test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sales_strategist_agent():
    """Test Sales Strategist Agent"""
    print("\n" + "=" * 80)
    print("TEST 3: SALES STRATEGIST AGENT")
    print("=" * 80)

    try:
        from phase3_sales_strategist_agent import Phase3SalesStrategistAgent
        agent = Phase3SalesStrategistAgent()

        # Test deal analysis
        print(f"\n{'-'*80}")
        print("Test 3a: Deal Analysis")
        print(f"{'-'*80}")

        result = agent.process({
            'action': 'analyze_deal',
            'deal_data': {
                'value': 50000,
                'stage': 'proposal',
                'days_in_stage': 12,
                'budget_confirmed': True
            },
            'prospect_data': {
                'company': 'TechCorp Inc',
                'champion_identified': True
            },
            'stakeholders': [
                {'name': 'CTO', 'role': 'champion'},
                {'name': 'CFO', 'role': 'economic_buyer'}
            ]
        })

        if result.get('success'):
            health = result.get('deal_health', {})
            print(f"✅ Deal Health: {health.get('score')}/100 ({health.get('status')})")
            print(f"🎯 Win Probability: {health.get('win_probability', 0):.0%}")
            print(f"⚠️  Risks: {len(result.get('risks', []))}")
            print(f"📋 Recommended Actions: {len(result.get('next_actions', []))}")

        # Test objection handling
        print(f"\n{'-'*80}")
        print("Test 3b: Objection Handling")
        print(f"{'-'*80}")

        result = agent.process({
            'action': 'handle_objection',
            'objection': "Your solution seems too expensive",
            'prospect_data': {'company': 'Startup Inc'},
            'deal_data': {'value': 30000}
        })

        if result.get('success'):
            print(f"✅ Objection Type: {result.get('objection_type')}")
            print(f"💬 Response Strategy: {result.get('response_strategy')[:100]}...")
            print(f"🎯 Confidence: {result.get('confidence', 0):.0%}")

        print("\n✓ Sales Strategist Agent Tests Complete")
        return True

    except Exception as e:
        print(f"❌ Sales Strategist test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_marketing_campaign_agent():
    """Test Marketing Campaign Agent"""
    print("\n" + "=" * 80)
    print("TEST 4: MARKETING CAMPAIGN AGENT")
    print("=" * 80)

    try:
        from phase3_marketing_campaign_agent import Phase3MarketingCampaignAgent
        agent = Phase3MarketingCampaignAgent()

        print(f"\n{'-'*80}")
        print("Test 4: Conversion Campaign Planning")
        print(f"{'-'*80}")

        result = agent.process({
            'campaign_type': 'conversion',
            'goal': 'Generate 500 qualified leads',
            'target_audience': {
                'industry': 'SaaS',
                'company_size': '50-200 employees',
                'role': 'Marketing Director'
            },
            'budget': 15000,
            'duration_days': 30,
            'channels': ['email', 'social_media', 'content', 'paid_ads']
        })

        if result.get('success'):
            print(f"✅ Campaign Type: {result.get('campaign_type')}")
            print(f"💰 Budget: ${result.get('budget_allocation', {}).get('email', {}).get('budget', 0):,.0f} (email)")
            print(f"📅 Content Calendar: {len(result.get('content_calendar', []))} weeks")
            print(f"👥 Audience Segments: {len(result.get('audience_segments', []))}")
            print(f"🧪 A/B Tests Planned: {len(result.get('ab_tests', []))}")
            print(f"📈 Expected ROI: {result.get('expected_roi', {}).get('roi_multiplier')}")

        print("\n✓ Marketing Campaign Agent Tests Complete")
        return True

    except Exception as e:
        print(f"❌ Marketing Campaign test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_customer_success_agent():
    """Test Customer Success Agent"""
    print("\n" + "=" * 80)
    print("TEST 5: CUSTOMER SUCCESS AGENT")
    print("=" * 80)

    try:
        from phase3_customer_success_agent import Phase3CustomerSuccessAgent
        agent = Phase3CustomerSuccessAgent()

        # Test health check
        print(f"\n{'-'*80}")
        print("Test 5a: Customer Health Check")
        print(f"{'-'*80}")

        result = agent.process({
            'action': 'health_check',
            'customer_id': 'cust_001',
            'customer_data': {
                'logins_last_30': 18,
                'meetings_attended': 2,
                'nps_score': 75,
                'support_tickets_last_30': 2
            },
            'usage_data': {
                'active_days_last_30': 22,
                'features_used': 8,
                'total_features': 10,
                'usage_percentage': 85
            },
            'account_data': {
                'mrr': 1500,
                'mrr_growth_percentage': 15
            }
        })

        if result.get('success'):
            print(f"✅ Health Score: {result.get('health_score')}/100")
            print(f"🎯 Status: {result.get('health_status')}")
            print(f"⚠️  Risk Level: {result.get('risk_level')}")
            print(f"🔍 Issues: {len(result.get('issues', []))}")
            print(f"📋 Recommended Actions: {len(result.get('recommended_actions', []))}")

        # Test expansion opportunities
        print(f"\n{'-'*80}")
        print("Test 5b: Expansion Opportunities")
        print(f"{'-'*80}")

        result = agent.process({
            'action': 'expansion_opportunity',
            'customer_id': 'cust_002',
            'customer_data': {'satisfaction': 9},
            'usage_data': {
                'usage_percentage': 85,
                'active_users': 9,
                'seat_limit': 10
            },
            'account_data': {'mrr': 2000, 'plan': 'professional'}
        })

        if result.get('success'):
            print(f"✅ Current MRR: ${result.get('current_mrr'):,}")
            print(f"💰 Total Opportunity: ${result.get('total_opportunity_value'):,}")
            print(f"🎯 Opportunities Found: {result.get('opportunity_count')}")

        print("\n✓ Customer Success Agent Tests Complete")
        return True

    except Exception as e:
        print(f"❌ Customer Success test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analytics_agent():
    """Test Analytics Agent"""
    print("\n" + "=" * 80)
    print("TEST 6: ANALYTICS AGENT")
    print("=" * 80)

    try:
        from phase3_analytics_agent import Phase3AnalyticsAgent
        agent = Phase3AnalyticsAgent()

        # Test executive summary
        print(f"\n{'-'*80}")
        print("Test 6a: Executive Summary Report")
        print(f"{'-'*80}")

        result = agent.process({
            'report_type': 'executive_summary',
            'time_period': 'monthly'
        })

        if result.get('success'):
            metrics = result.get('key_metrics', {})
            print(f"✅ Total Interactions: {metrics.get('total_interactions'):,}")
            print(f"🎯 Leads Generated: {metrics.get('leads_generated'):,}")
            print(f"💰 Pipeline Value: ${metrics.get('pipeline_value'):,}")
            print(f"📈 ROI: {metrics.get('roi_percentage')}%")
            print(f"⭐ Quality Score: {metrics.get('agent_quality_score')}")
            print(f"🚨 Alerts: {len(result.get('alerts', []))}")
            print(f"💡 Recommendations: {len(result.get('recommendations', []))}")

        # Test ROI report
        print(f"\n{'-'*80}")
        print("Test 6b: ROI Report")
        print(f"{'-'*80}")

        result = agent.process({
            'report_type': 'roi',
            'time_period': 'monthly'
        })

        if result.get('success'):
            roi = result.get('roi_metrics', {})
            print(f"✅ Investment: ${roi.get('total_investment'):,}")
            print(f"💰 Value Generated: ${roi.get('total_value_generated'):,}")
            print(f"📈 ROI: {roi.get('roi_percentage')}% ({roi.get('roi_multiplier')})")
            print(f"⏱️  Payback: {roi.get('payback_period_months')} months")

        print("\n✓ Analytics Agent Tests Complete")
        return True

    except Exception as e:
        print(f"❌ Analytics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_via_api():
    """Test Phase 3 agents via API"""
    print("\n" + "=" * 80)
    print("TEST 7: PHASE 3 AGENTS VIA API")
    print("=" * 80)

    # Check if API is available
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"⚠️  API not available at {API_BASE_URL}")
            print(f"   Skipping API tests. Start the service with: cd agents && python main.py")
            return True
    except Exception as e:
        print(f"⚠️  API not available: {e}")
        print(f"   Skipping API tests.")
        return True

    print(f"✅ API available at {API_BASE_URL}\n")

    # Test orchestrator via API
    print(f"{'-'*80}")
    print("Testing: POST /phase3/orchestrate")
    print(f"{'-'*80}")

    try:
        response = requests.post(
            f"{API_BASE_URL}/phase3/orchestrate",
            json={
                'customer_id': 'lead_api_test',
                'workflow_type': 'lead_nurture',
                'engagement_score': 90,
                'journey_stage': 'consideration'
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            print(f"✅ API Response: 200 OK")
            print(f"🎯 Workflow: {data.get('workflow_type')}")
            print(f"📋 Actions: {len(data.get('next_actions', []))}")
        else:
            print(f"❌ API Error: {response.status_code}")

    except Exception as e:
        print(f"❌ API request failed: {e}")

    # Test research via API
    print(f"\n{'-'*80}")
    print("Testing: POST /phase3/research")
    print(f"{'-'*80}")

    try:
        response = requests.post(
            f"{API_BASE_URL}/phase3/research",
            json={
                'query': 'AI automation for business',
                'depth': 'quick',
                'max_results': 3
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            print(f"✅ API Response: 200 OK")
            print(f"🔍 Confidence: {data.get('confidence', 0):.0%}")
            print(f"📊 Results: {data.get('results_count')}")
        else:
            print(f"❌ API Error: {response.status_code}")

    except Exception as e:
        print(f"❌ API request failed: {e}")

    print(f"\n✓ API Tests Complete")
    return True


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "PHASE 3 AGENTS - TEST SUITE" + " " * 30 + "║")
    print("╚" + "═" * 78 + "╝")

    results = []

    # Run tests
    results.append(("Orchestrator Agent", test_orchestrator_agent()))
    results.append(("RAG Research Agent", test_rag_research_agent()))
    results.append(("Sales Strategist Agent", test_sales_strategist_agent()))
    results.append(("Marketing Campaign Agent", test_marketing_campaign_agent()))
    results.append(("Customer Success Agent", test_customer_success_agent()))
    results.append(("Analytics Agent", test_analytics_agent()))
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
