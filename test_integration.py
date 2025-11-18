#!/usr/bin/env python3
"""
SIX3 Agency Integration Test Suite
Complete end-to-end testing of all components
"""

import requests
import json
import time
from datetime import datetime
from agents.n8n_integration import n8n

def test_local_api():
    """Test the local agent API is running"""
    print("🔄 Testing Local Agent API...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Local Agent API is running")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Local API unavailable: {e}")
        return False

def test_n8n_connection():
    """Test n8n cloud connection and workflows"""
    print("\n🌐 Testing n8n Cloud Connection...")
    try:
        workflows = n8n.get_workflows()
        print(f"✅ Connected to n8n at {n8n.base_url}")
        print(f"✅ Found {len(workflows)} SIX3 workflows:")
        for wf in workflows:
            status = "🟢 Active" if wf.get('active') else "🔴 Inactive"
            print(f"   • {wf.get('name')} - {status}")
        return len(workflows) > 0
    except Exception as e:
        print(f"❌ n8n connection failed: {e}")
        return False

def test_lead_qualification_endpoint():
    """Test the lead qualification agent endpoint"""
    print("\n👤 Testing Lead Qualification Agent...")
    try:
        test_lead = {
            "name": "Test User",
            "email": "test@example.com",
            "company": "Test Corp",
            "phone": "+1555000000",
            "source": "integration_test",
            "message": "Testing integration"
        }
        
        response = requests.post(
            "http://localhost:8000/agents/prospect-research/process",
            json={"lead_data": test_lead, "source": "test"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Qualification Score: {result.get('score', 'N/A')}")
            print(f"✅ Qualified: {result.get('qualified', 'N/A')}")
            return result
        else:
            print(f"❌ Lead qualification failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Lead qualification error: {e}")
        return None

def test_sales_pitch_endpoint():
    """Test the sales pitch generation endpoint"""
    print("\n📝 Testing Sales Pitch Generation...")
    try:
        test_data = {
            "lead_profile": {
                "name": "Test User",
                "email": "test@example.com", 
                "company": "Test Corp"
            },
            "personalization_data": {
                "company": "Test Corp",
                "industry": "Software",
                "pain_points": ["automation", "efficiency"]
            }
        }
        
        response = requests.post(
            "http://localhost:8000/agents/sales-pitch/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Personalization Score: {result.get('personalization_score', 'N/A')}")
            print(f"✅ Conversion Rate: {result.get('estimated_conversion_rate', 'N/A')}")
            return result
        else:
            print(f"❌ Sales pitch generation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Sales pitch error: {e}")
        return None

def test_email_personalization_endpoint():
    """Test the email personalization endpoint"""
    print("\n📧 Testing Email Personalization...")
    try:
        test_data = {
            "lead_data": {
                "name": "Test User",
                "email": "test@example.com",
                "company": "Test Corp"
            },
            "sales_pitch": {
                "pitch": "Test pitch content",
                "call_to_action": "Schedule a demo"
            },
            "email_template": "integration_test"
        }
        
        response = requests.post(
            "http://localhost:8000/agents/email-personalizer/create",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Email Subject: {result.get('email_subject', 'N/A')}")
            print(f"✅ Open Rate: {result.get('estimated_open_rate', 'N/A')}")
            return result
        else:
            print(f"❌ Email personalization failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Email personalization error: {e}")
        return None

def test_webhook_endpoints():
    """Test the webhook endpoints for n8n integration"""
    print("\n🔗 Testing Webhook Endpoints...")
    
    # Test lead qualification webhook
    try:
        test_lead = {
            "name": "Webhook Test User",
            "email": "webhook@test.com",
            "company": "Webhook Corp",
            "source": "webhook_test"
        }
        
        response = requests.post(
            "http://localhost:8000/webhook/lead-qualification",
            json=test_lead,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Lead qualification webhook working")
        else:
            print(f"❌ Lead qualification webhook failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Webhook test error: {e}")

def test_control_panel():
    """Test the control panel dashboard"""
    print("\n📊 Testing Control Panel Dashboard...")
    try:
        response = requests.get("http://localhost:8000/control-panel/dashboard")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('dashboard', {}).get('statistics_24h', {})
            print(f"✅ Control Panel accessible")
            print(f"✅ Total interactions: {stats.get('total_interactions', 0)}")
            print(f"✅ Success rate: {stats.get('success_rate', 0)}%")
            return True
        else:
            print(f"❌ Control panel failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Control panel error: {e}")
        return False

def main():
    """Run complete integration test suite"""
    print("🚀 SIX3 AGENCY INTEGRATION TEST SUITE")
    print("=" * 60)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Component tests
    tests = [
        ("Local Agent API", test_local_api),
        ("n8n Cloud Connection", test_n8n_connection),
        ("Lead Qualification", test_lead_qualification_endpoint),
        ("Sales Pitch Generation", test_sales_pitch_endpoint),
        ("Email Personalization", test_email_personalization_endpoint),
        ("Webhook Endpoints", test_webhook_endpoints),
        ("Control Panel", test_control_panel),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result is not False and result is not None
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
        
        print()  # Add space between tests
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for passed in results.values() if passed)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("\n🌟 SIX3 Agency Platform Status:")
        print(f"   • Local Agent API: http://localhost:8000")
        print(f"   • Control Panel: http://localhost:8000/control-panel.html")
        print(f"   • API Documentation: http://localhost:8000/docs")
        print(f"   • n8n Workflows: https://n8n.six3.cloud")
        print(f"   • Webhook Endpoints: /webhook/lead-qualification, /webhook/email-personalization")
    else:
        print(f"⚠️  {total_tests - passed_tests} components need attention")

if __name__ == "__main__":
    main()