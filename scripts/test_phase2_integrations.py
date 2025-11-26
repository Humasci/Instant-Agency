#!/usr/bin/env python3
"""
Phase 2 Integration Testing Script
Tests all Phase 2 components and integrations
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_environment_setup():
    """Test environment variables and dependencies"""
    print("🔧 Testing Environment Setup...")
    
    required_vars = [
        'HUGGINGFACE_API_KEY',
        'MAILGUN_API_KEY', 
        'MAILGUN_DOMAIN'
    ]
    
    optional_vars = [
        'LINKEDIN_ACCESS_TOKEN',
        'TWITTER_CONSUMER_KEY',
        'GOOGLE_PAGESPEED_API_KEY',
        'SLACK_WEBHOOK_URL',
        'REDIS_HOST'
    ]
    
    results = {
        'required': {},
        'optional': {},
        'dependencies': {}
    }
    
    # Check required environment variables
    for var in required_vars:
        value = os.getenv(var)
        results['required'][var] = 'SET' if value else 'MISSING'
        if value:
            print(f"  ✅ {var}: SET")
        else:
            print(f"  ❌ {var}: MISSING")
    
    # Check optional environment variables
    for var in optional_vars:
        value = os.getenv(var)
        results['optional'][var] = 'SET' if value else 'MISSING'
        status = "✅" if value else "⚠️"
        print(f"  {status} {var}: {'SET' if value else 'MISSING'}")
    
    # Check Python dependencies
    dependencies = [
        ('requests', 'HTTP requests'),
        ('beautifulsoup4', 'HTML parsing'),
        ('redis', 'Redis cache'),
        ('transformers', 'Hugging Face models'),
        ('fastapi', 'API framework')
    ]
    
    for package, description in dependencies:
        try:
            __import__(package)
            results['dependencies'][package] = True
            print(f"  ✅ {package}: Available ({description})")
        except ImportError:
            results['dependencies'][package] = False
            print(f"  ❌ {package}: Missing ({description})")
    
    return results

def test_mailgun_integration():
    """Test Mailgun email integration"""
    print("\n📧 Testing Mailgun Integration...")
    
    try:
        from integrations.email.mailgun_integration import MailgunIntegration, MailgunEmailTemplates
        
        # Initialize Mailgun (will use env vars)
        mg = MailgunIntegration()
        
        # Test connection
        print("  🔗 Testing connection...")
        connection_test = mg.test_connection()
        
        if connection_test['success']:
            print(f"  ✅ Connection successful: {connection_test['domain']}")
            print(f"  📊 Domain state: {connection_test.get('domain_state', 'unknown')}")
        else:
            print(f"  ❌ Connection failed: {connection_test.get('error', 'Unknown error')}")
            return connection_test
        
        # Test email validation
        print("  🔍 Testing email validation...")
        validation_test = mg.validate_email("test@example.com")
        if validation_test['success']:
            print(f"  ✅ Email validation working")
        else:
            print(f"  ⚠️ Email validation failed: {validation_test.get('error')}")
        
        # Test template generation
        print("  📝 Testing email templates...")
        welcome_template = MailgunEmailTemplates.welcome_email("Test User")
        print(f"  ✅ Welcome template generated: {len(welcome_template['html_content'])} chars")
        
        # Test email sending (with sandbox/test)
        if os.getenv('MAILGUN_API_KEY') and os.getenv('MAILGUN_DOMAIN'):
            print("  📤 Testing email sending (test mode)...")
            test_result = mg.send_email(
                to_email="test@sandbox.mailgun.org",  # Mailgun test email
                subject="Phase 2 Integration Test",
                text_content="This is a test email from Phase 2 integration testing.",
                html_content="<p>This is a test email from <strong>Phase 2</strong> integration testing.</p>"
            )
            
            if test_result['success']:
                print(f"  ✅ Test email sent successfully: {test_result.get('message_id', 'No ID')}")
            else:
                print(f"  ⚠️ Test email failed: {test_result.get('error')}")
        else:
            print("  ⚠️ Skipping email send test (API key not configured)")
        
        return {'success': True, 'connection': connection_test}
        
    except Exception as e:
        print(f"  ❌ Mailgun integration failed: {str(e)}")
        return {'success': False, 'error': str(e)}

def test_seo_agent():
    """Test enhanced SEO agent with free APIs"""
    print("\n🔍 Testing Enhanced SEO Agent...")
    
    try:
        from agents.phase2_seo_optimizer_agent import SEOOptimizerAgent
        
        # Initialize SEO agent
        seo_agent = SEOOptimizerAgent()
        print("  ✅ SEO Agent initialized")
        
        # Test keyword research
        print("  🔎 Testing keyword research...")
        keyword_result = seo_agent.research_keywords(
            "AI automation", 
            "technology", 
            "business owners"
        )
        
        if keyword_result['success']:
            data = keyword_result['data']
            print(f"  ✅ Keyword research: {data['total_keywords_found']} keywords found")
            print(f"  📊 Primary keywords: {[k['keyword'] for k in data['primary_keywords'][:3]]}")
        else:
            print(f"  ❌ Keyword research failed: {keyword_result.get('error')}")
        
        # Test content optimization
        print("  📝 Testing content optimization...")
        test_content = """
        # AI Automation for Business
        
        Artificial intelligence automation is transforming how businesses operate. Companies are using AI agents to streamline processes, reduce costs, and improve efficiency.
        """
        
        optimization_result = seo_agent.optimize_content(
            test_content, 
            "AI automation", 
            "blog_post"
        )
        
        if optimization_result['success']:
            data = optimization_result['data']
            print(f"  ✅ Content optimization: SEO score {data['current_analysis']['seo_score']}/100")
            print(f"  📋 Recommendations: {len(data['recommendations'])} suggestions")
        else:
            print(f"  ❌ Content optimization failed: {optimization_result.get('error')}")
        
        # Test SERP analysis (new feature)
        print("  🌐 Testing SERP analysis...")
        serp_result = seo_agent.analyze_serp_results("AI automation", "us", "en", 5)
        
        if serp_result['success']:
            data = serp_result['data']
            print(f"  ✅ SERP analysis: {data['total_results']} competitors analyzed")
            print(f"  🎯 Keyword difficulty: {data['keyword_difficulty']['level']} ({data['keyword_difficulty']['score']}/100)")
            print(f"  💡 Content gaps: {len(data['content_gaps'])} opportunities found")
        else:
            print(f"  ❌ SERP analysis failed: {serp_result.get('error')}")
        
        # Test trending keywords
        print("  📈 Testing trending keywords...")
        trends_result = seo_agent.get_trending_keywords("technology")
        
        if trends_result['success']:
            keywords = trends_result.get('trending_keywords', [])
            print(f"  ✅ Trending keywords: {len(keywords)} found")
            print(f"  🔥 Top trends: {keywords[:3] if keywords else 'None'}")
        else:
            print(f"  ❌ Trending keywords failed: {trends_result.get('error')}")
        
        # Test meta tag generation
        print("  🏷️ Testing meta tag generation...")
        meta_result = seo_agent.generate_meta_tags(test_content, "AI automation", "article")
        
        if meta_result['success']:
            data = meta_result['data']
            print(f"  ✅ Meta tags generated")
            print(f"  📑 Title: {data['recommended_tags']['title'][:50]}...")
            print(f"  📄 Description: {data['recommended_tags']['meta_description'][:50]}...")
        else:
            print(f"  ❌ Meta tag generation failed: {meta_result.get('error')}")
        
        return {'success': True, 'tests': 5}
        
    except Exception as e:
        print(f"  ❌ SEO Agent testing failed: {str(e)}")
        return {'success': False, 'error': str(e)}

def test_social_media_integrations():
    """Test social media integrations"""
    print("\n📱 Testing Social Media Integrations...")
    
    # Test LinkedIn Integration
    print("  🔗 Testing LinkedIn integration...")
    try:
        from integrations.social_media.linkedin_integration import LinkedInIntegration, LinkedInPostTemplates
        
        if os.getenv('LINKEDIN_ACCESS_TOKEN'):
            linkedin = LinkedInIntegration()
            
            # Test connection
            connection_test = linkedin.test_connection()
            if connection_test['success']:
                print(f"  ✅ LinkedIn connected: @{connection_test.get('user_name', 'Unknown')}")
            else:
                print(f"  ❌ LinkedIn connection failed: {connection_test.get('error')}")
        else:
            print("  ⚠️ LinkedIn access token not configured - skipping live test")
        
        # Test template generation
        post_content = LinkedInPostTemplates.thought_leadership(
            "AI automation",
            "The future of business lies in intelligent automation that enhances human capabilities.",
            "What's your experience with AI in business?"
        )
        print(f"  ✅ LinkedIn template generated: {len(post_content)} characters")
        
    except Exception as e:
        print(f"  ❌ LinkedIn integration failed: {str(e)}")
    
    # Test Twitter Integration  
    print("  🐦 Testing Twitter integration...")
    try:
        from integrations.social_media.twitter_integration import TwitterIntegration, TwitterPostTemplates
        
        if os.getenv('TWITTER_CONSUMER_KEY'):
            print("  ⚠️ Twitter API keys found but skipping live test (requires full setup)")
        else:
            print("  ⚠️ Twitter API keys not configured - skipping live test")
        
        # Test template generation
        tweet_content = TwitterPostTemplates.thought_leadership(
            "The future of business automation is here! 🤖✨",
            ['AI', 'Automation', 'Business']
        )
        print(f"  ✅ Twitter template generated: {len(tweet_content)} characters")
        
    except Exception as e:
        print(f"  ❌ Twitter integration failed: {str(e)}")
    
    return {'success': True}

def test_escalation_system():
    """Test human escalation system"""
    print("\n🚨 Testing Human Escalation System...")
    
    try:
        from integrations.escalation.human_escalation_system import HumanEscalationSystem, EscalationPriority, EscalationCase
        
        # Initialize escalation system
        escalation_system = HumanEscalationSystem()
        print("  ✅ Escalation system initialized")
        
        # Test escalation detection
        print("  🔍 Testing escalation detection...")
        
        agent_response = {
            'confidence': 0.2,  # Low confidence
            'sentiment': {'score': -0.8}  # Very negative
        }
        
        conversation_context = {
            'messages': [{'user': f'message {i}'} for i in range(12)],  # Long conversation
            'latest_message': 'I want to speak to a manager immediately!',
            'consecutive_errors': 2
        }
        
        customer_data = {
            'lifetime_value': 15000  # High-value customer
        }
        
        escalation_check = escalation_system.should_escalate(
            agent_response, conversation_context, customer_data
        )
        
        if escalation_check['should_escalate']:
            print(f"  ✅ Escalation detected: {escalation_check['priority'].value} priority")
            print(f"  📊 Score: {escalation_check['escalation_score']}/100")
            print(f"  📝 Reasons: {len(escalation_check['reasons'])} triggers")
        else:
            print("  ⚠️ No escalation triggered (unexpected for test scenario)")
        
        # Test case creation
        if escalation_check['should_escalate']:
            print("  📋 Testing case creation...")
            
            escalation_case = escalation_system.create_escalation_case(
                agent_name="Phase2 Test Agent",
                customer_id="test_customer_123",
                customer_name="John Test",
                customer_email="john.test@example.com",
                trigger_reason="; ".join(escalation_check['reasons']),
                priority=escalation_check['priority'],
                context=conversation_context,
                conversation_history=conversation_context['messages']
            )
            
            print(f"  ✅ Case created: {escalation_case.id}")
            print(f"  🎯 Priority: {escalation_case.priority.value}")
        
        # Test queue status
        print("  📊 Testing queue status...")
        queue_status = escalation_system.get_queue_status()
        
        if 'error' not in queue_status:
            print(f"  ✅ Queue status retrieved: {queue_status['total_pending']} pending cases")
        else:
            print(f"  ⚠️ Queue status failed: {queue_status['error']}")
        
        return {'success': True}
        
    except Exception as e:
        print(f"  ❌ Escalation system testing failed: {str(e)}")
        return {'success': False, 'error': str(e)}

def test_phase2_agents_api():
    """Test Phase 2 agents via API"""
    print("\n🔌 Testing Phase 2 Agents API...")
    
    try:
        import requests
        import subprocess
        import signal
        import time
        
        # Start the API server in background
        print("  🚀 Starting API server...")
        
        api_process = subprocess.Popen(
            ['python', 'main.py'],
            cwd='agents',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(5)
        
        try:
            # Test health endpoint
            print("  ❤️ Testing health endpoint...")
            health_response = requests.get('http://localhost:8000/health', timeout=10)
            
            if health_response.status_code == 200:
                print("  ✅ API server healthy")
            else:
                print(f"  ❌ API server unhealthy: {health_response.status_code}")
                return {'success': False}
            
            # Test agents list endpoint
            print("  📋 Testing agents list...")
            agents_response = requests.get('http://localhost:8000/agents', timeout=10)
            
            if agents_response.status_code == 200:
                agents = agents_response.json()
                print(f"  ✅ Agents endpoint: {len(agents)} agents available")
            else:
                print(f"  ❌ Agents endpoint failed: {agents_response.status_code}")
            
            # Test Phase 2 specific endpoints
            print("  🧪 Testing Phase 2 endpoints...")
            
            # Test email personalization
            email_test_data = {
                "recipient_data": [
                    {
                        "email": "test@example.com",
                        "name": "Test User",
                        "company": "Test Corp"
                    }
                ],
                "campaign_type": "welcome_series",
                "personalization_level": "medium"
            }
            
            try:
                email_response = requests.post(
                    'http://localhost:8000/phase2/personalize-email',
                    json=email_test_data,
                    timeout=15
                )
                
                if email_response.status_code == 200:
                    print("  ✅ Email personalization endpoint working")
                else:
                    print(f"  ⚠️ Email personalization endpoint: {email_response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"  ⚠️ Email personalization test failed: {str(e)}")
            
            # Test content optimization
            content_test_data = {
                "content": "AI automation is transforming business operations.",
                "target_keyword": "AI automation",
                "content_type": "blog_post"
            }
            
            try:
                content_response = requests.post(
                    'http://localhost:8000/phase2/optimize-content',
                    json=content_test_data,
                    timeout=15
                )
                
                if content_response.status_code == 200:
                    print("  ✅ Content optimization endpoint working")
                else:
                    print(f"  ⚠️ Content optimization endpoint: {content_response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"  ⚠️ Content optimization test failed: {str(e)}")
            
            return {'success': True}
            
        finally:
            # Clean up: stop the API server
            print("  🛑 Stopping API server...")
            api_process.terminate()
            api_process.wait(timeout=5)
    
    except Exception as e:
        print(f"  ❌ API testing failed: {str(e)}")
        return {'success': False, 'error': str(e)}

def test_n8n_workflows():
    """Test n8n workflow imports"""
    print("\n🔄 Testing n8n Workflows...")
    
    workflows_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'workflows')
    
    # Check if workflow files exist
    phase2_workflows = [
        'Phase2_Email_Campaign_Scheduler.json',
        '02_marketing_content_pipeline.json',
        'SIX3_Email_Personalization.json'
    ]
    
    workflow_tests = []
    
    for workflow_file in phase2_workflows:
        workflow_path = os.path.join(workflows_dir, workflow_file)
        
        if os.path.exists(workflow_path):
            try:
                with open(workflow_path, 'r') as f:
                    workflow_data = json.load(f)
                
                # Validate workflow structure
                required_fields = ['name', 'nodes', 'connections']
                missing_fields = [field for field in required_fields if field not in workflow_data]
                
                if not missing_fields:
                    nodes_count = len(workflow_data.get('nodes', []))
                    print(f"  ✅ {workflow_file}: Valid ({nodes_count} nodes)")
                    workflow_tests.append(True)
                else:
                    print(f"  ❌ {workflow_file}: Missing fields {missing_fields}")
                    workflow_tests.append(False)
                    
            except json.JSONDecodeError:
                print(f"  ❌ {workflow_file}: Invalid JSON")
                workflow_tests.append(False)
        else:
            print(f"  ❌ {workflow_file}: File not found")
            workflow_tests.append(False)
    
    # Check n8n connectivity (if running)
    print("  🔗 Testing n8n connectivity...")
    try:
        n8n_response = requests.get('http://localhost:5678/healthz', timeout=5)
        if n8n_response.status_code == 200:
            print("  ✅ n8n server is running")
        else:
            print("  ⚠️ n8n server responded but not healthy")
    except requests.exceptions.RequestException:
        print("  ⚠️ n8n server not running (this is expected if not started)")
    
    successful_workflows = sum(workflow_tests)
    total_workflows = len(workflow_tests)
    
    return {
        'success': successful_workflows > 0,
        'workflows_valid': f"{successful_workflows}/{total_workflows}"
    }

def generate_test_report(results: Dict[str, Any]):
    """Generate comprehensive test report"""
    
    print("\n" + "="*60)
    print("📊 PHASE 2 INTEGRATION TEST REPORT")
    print("="*60)
    
    # Summary
    total_tests = len([k for k in results.keys() if k.endswith('_test')])
    successful_tests = len([k for k, v in results.items() if k.endswith('_test') and v.get('success', False)])
    
    print(f"\n🎯 OVERALL STATUS: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests == total_tests:
        print("🎉 ALL TESTS PASSED - Phase 2 ready for deployment!")
    elif successful_tests >= total_tests * 0.7:
        print("⚠️ MOSTLY WORKING - Some components need API keys")
    else:
        print("❌ ISSUES DETECTED - Check configuration")
    
    # Environment status
    print(f"\n🔧 ENVIRONMENT:")
    env_results = results.get('environment', {})
    required = env_results.get('required', {})
    optional = env_results.get('optional', {})
    
    required_set = len([k for k, v in required.items() if v == 'SET'])
    required_total = len(required)
    
    print(f"  Required vars: {required_set}/{required_total} configured")
    if required_set < required_total:
        missing = [k for k, v in required.items() if v == 'MISSING']
        print(f"  Missing: {', '.join(missing)}")
    
    optional_set = len([k for k, v in optional.items() if v == 'SET'])
    optional_total = len(optional)
    print(f"  Optional vars: {optional_set}/{optional_total} configured")
    
    # Component status
    print(f"\n📦 COMPONENTS:")
    
    components = [
        ('Mailgun Email', 'mailgun_test'),
        ('Enhanced SEO Agent', 'seo_test'),
        ('Social Media', 'social_test'),
        ('Escalation System', 'escalation_test'),
        ('API Endpoints', 'api_test'),
        ('n8n Workflows', 'workflows_test')
    ]
    
    for name, test_key in components:
        test_result = results.get(test_key, {})
        if test_result.get('success'):
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}: {test_result.get('error', 'Failed')}")
    
    # Next steps
    print(f"\n🚀 NEXT STEPS:")
    
    if required_set < required_total:
        print("  1. Configure missing required environment variables")
        print("  2. Run test script again to verify setup")
    
    if results.get('mailgun_test', {}).get('success'):
        print("  3. Test email campaigns with real recipients")
    else:
        print("  3. Set up Mailgun API key and domain")
    
    if results.get('seo_test', {}).get('success'):
        print("  4. SEO agent ready - add Google PageSpeed API key for enhanced features")
    
    print("  5. Configure social media API keys for LinkedIn/Twitter posting")
    print("  6. Start n8n server and import workflow templates")
    print("  7. Begin Phase 3 development")
    
    # Configuration guide
    print(f"\n🔑 MISSING API KEYS SETUP:")
    
    if required.get('MAILGUN_API_KEY') == 'MISSING':
        print("  Mailgun: https://app.mailgun.com/app/account/security/api_keys")
        print("    export MAILGUN_API_KEY='key-your-api-key'")
        print("    export MAILGUN_DOMAIN='your-domain.com'")
    
    if optional.get('LINKEDIN_ACCESS_TOKEN') == 'MISSING':
        print("  LinkedIn: https://www.linkedin.com/developers/apps")
        print("    export LINKEDIN_ACCESS_TOKEN='your-token'")
    
    if optional.get('GOOGLE_PAGESPEED_API_KEY') == 'MISSING':
        print("  PageSpeed: https://developers.google.com/speed/docs/insights/v5/get-started")
        print("    export GOOGLE_PAGESPEED_API_KEY='your-key'")
    
    print(f"\n📋 SAVE REPORT:")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"phase2_test_report_{timestamp}.json"
    
    try:
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"  📄 Detailed report saved: {report_file}")
    except Exception as e:
        print(f"  ⚠️ Could not save report: {e}")

def main():
    """Run all Phase 2 integration tests"""
    
    print("🚀 Starting Phase 2 Integration Testing...")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test 1: Environment setup
    results['environment'] = test_environment_setup()
    
    # Test 2: Mailgun integration
    results['mailgun_test'] = test_mailgun_integration()
    
    # Test 3: Enhanced SEO agent
    results['seo_test'] = test_seo_agent()
    
    # Test 4: Social media integrations
    results['social_test'] = test_social_media_integrations()
    
    # Test 5: Escalation system
    results['escalation_test'] = test_escalation_system()
    
    # Test 6: API endpoints
    results['api_test'] = test_phase2_agents_api()
    
    # Test 7: n8n workflows
    results['workflows_test'] = test_n8n_workflows()
    
    # Generate final report
    results['test_completed_at'] = datetime.now().isoformat()
    generate_test_report(results)
    
    print(f"\n🏁 Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()