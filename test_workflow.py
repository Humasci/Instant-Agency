#!/usr/bin/env python3
"""
SIX3 Agency Workflow Test Script
Simulates end-to-end lead qualification process
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000"
WEBHOOK_URL = f"{API_BASE}/webhook/lead-qualification"  # This would be the n8n webhook

# Test lead data
test_leads = [
    {
        "name": "Alice Johnson", 
        "email": "alice@innovate.com", 
        "company": "InnovateTech", 
        "phone": "+1555000001",
        "source": "website_form",
        "message": "Interested in automation solutions"
    },
    {
        "name": "Bob Chen", 
        "email": "bob@growth.co", 
        "company": "Growth Corp", 
        "phone": "+1555000002",
        "source": "linkedin",
        "message": "Looking to improve our sales process"
    },
    {
        "name": "Carol Davis", 
        "email": "carol@startup.io", 
        "company": "StartupIO", 
        "phone": "+1555000003",
        "source": "referral",
        "message": "Need help with lead qualification"
    }
]

def test_prospect_research(lead_data):
    """Test the prospect research agent"""
    print(f"🔍 Testing Prospect Research for {lead_data['name']}...")
    
    response = requests.post(
        f"{API_BASE}/agents/prospect-research/process",
        json={"lead_data": lead_data, "source": "test"},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Qualification Score: {result['score']}")
        print(f"✅ Qualified: {result['qualified']}")
        print(f"✅ Industry: {result['industry']}")
        print(f"✅ Pain Points: {result['pain_points']}")
        return result
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

def test_sales_pitch(lead_profile, qualification_data):
    """Test sales pitch generation"""
    print(f"📝 Generating sales pitch for {lead_profile['company']}...")
    
    response = requests.post(
        f"{API_BASE}/agents/sales-pitch/generate",
        json={
            "lead_profile": lead_profile,
            "personalization_data": {
                "company": qualification_data.get('company'),
                "industry": qualification_data.get('industry'),
                "pain_points": qualification_data.get('pain_points')
            }
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Personalization Score: {result['personalization_score']}")
        print(f"✅ Estimated Conversion: {result['estimated_conversion_rate']}")
        print(f"✅ Call to Action: {result['call_to_action']}")
        return result
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

def test_email_personalization(lead_data, sales_pitch):
    """Test email personalization"""
    print(f"📧 Creating personalized email...")
    
    response = requests.post(
        f"{API_BASE}/agents/email-personalizer/create",
        json={
            "lead_data": lead_data,
            "sales_pitch": sales_pitch,
            "email_template": "lead_qualification_followup"
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Email Subject: {result['email_subject']}")
        print(f"✅ Estimated Open Rate: {result['estimated_open_rate']}")
        print(f"✅ Scheduled: {result['scheduled']}")
        return result
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

def simulate_workflow(lead_data):
    """Simulate the complete SIX3 lead qualification workflow"""
    print(f"\n🚀 Starting SIX3 Lead Qualification Workflow")
    print(f"👤 Lead: {lead_data['name']} from {lead_data['company']}")
    print("=" * 60)
    
    # Step 1: Prospect Research
    qualification_result = test_prospect_research(lead_data)
    if not qualification_result:
        return False
    
    time.sleep(1)  # Simulate processing time
    
    # Step 2: Check qualification
    if qualification_result['qualified']:
        print(f"\n✅ Lead QUALIFIED! Score: {qualification_result['score']}")
        
        # Step 3: Generate sales pitch
        sales_pitch = test_sales_pitch(lead_data, qualification_result)
        if not sales_pitch:
            return False
        
        time.sleep(1)
        
        # Step 4: Create personalized email
        email_result = test_email_personalization(lead_data, sales_pitch)
        if not email_result:
            return False
        
        print(f"\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
        print(f"📈 Next Action: Personalized email scheduled")
        
    else:
        print(f"\n❌ Lead NOT QUALIFIED. Score: {qualification_result['score']}")
        print(f"📋 Reason: {qualification_result['disqualification_reason']}")
        print(f"📧 Next Action: Add to nurture campaign")
    
    return True

def test_workflow_endpoints():
    """Test workflow management endpoints"""
    print("\n🔄 Testing Workflow Management Endpoints")
    print("=" * 60)
    
    # Test templates endpoint
    print("📋 Fetching workflow templates...")
    response = requests.get(f"{API_BASE}/workflows/templates")
    if response.status_code == 200:
        templates = response.json()
        print(f"✅ Found {templates['count']} workflow templates")
        for template in templates['templates']:
            print(f"   • {template['name']} (Phase {template['phase']}) - {template['category']}")
    else:
        print(f"❌ Error fetching templates: {response.status_code}")
    
    # Test workflows endpoint
    print(f"\n🔗 Checking n8n workflows...")
    response = requests.get(f"{API_BASE}/workflows")
    if response.status_code == 200:
        workflows = response.json()
        print(f"✅ Found {workflows['count']} SIX3 workflows in n8n")
        if workflows['workflows']:
            for workflow in workflows['workflows']:
                print(f"   • {workflow.get('name', 'Unnamed')}")
    else:
        print(f"❌ Error fetching workflows: {response.status_code}")

def main():
    """Run all workflow tests"""
    print("🤖 SIX3 AGENCY WORKFLOW TESTING")
    print("=" * 60)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test workflow endpoints first
    test_workflow_endpoints()
    
    # Test each lead through the workflow
    for i, lead in enumerate(test_leads, 1):
        print(f"\n\n🧪 TEST {i}/{len(test_leads)}")
        success = simulate_workflow(lead)
        if not success:
            print(f"❌ Workflow failed for {lead['name']}")
        
        if i < len(test_leads):
            print("\n⏱️  Waiting 2 seconds before next test...")
            time.sleep(2)
    
    print(f"\n\n🏁 ALL TESTS COMPLETED")
    print("=" * 60)
    print(f"📊 API Documentation: {API_BASE}/docs")
    print(f"🔗 n8n Workflows: https://n8n.six3.cloud")
    print(f"📋 Import workflow: /home/buntu/Instant-Agency/workflows/SIX3_Lead_Qualification.json")

if __name__ == "__main__":
    main()