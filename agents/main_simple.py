"""
Simplified Agent Service for Testing Control Panel
This version runs without AI dependencies to test the control panel UI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uvicorn
import os
import random
import json
from local_database import db
from n8n_integration import n8n

# Initialize FastAPI app
app = FastAPI(
    title="SIX3 Agency - AI Agent Service (Test Mode)",
    description="Simplified test version for control panel testing",
    version="1.0.0-test"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add route to serve control panel
@app.get("/control-panel.html")
async def get_control_panel():
    """Serve the control panel HTML file"""
    control_panel_path = os.path.join(os.path.dirname(__file__), "..", "control-panel.html")
    if os.path.exists(control_panel_path):
        return FileResponse(control_panel_path)
    else:
        raise HTTPException(status_code=404, detail="Control panel not found")

@app.get("/control-panel-visual.html")
async def get_visual_control_panel():
    """Serve the enhanced visual control panel"""
    control_panel_path = os.path.join(os.path.dirname(__file__), "..", "control-panel-visual.html")
    if os.path.exists(control_panel_path):
        return FileResponse(control_panel_path)
    else:
        raise HTTPException(status_code=404, detail="Visual control panel not found")

# Mock agent data
MOCK_AGENTS = [
    {
        "agent_name": "phase1_prospect",
        "display_name": "Phase 1 Prospect Agent",
        "version": "1.0.0",
        "department": "Marketing",
        "status": "active",
        "total_interactions": random.randint(800, 1500),
        "success_rate": random.uniform(0.75, 0.95),
        "avg_response_time": random.uniform(200, 800)
    },
    {
        "agent_name": "phase1_faq",
        "display_name": "Phase 1 FAQ Chatbot",
        "version": "1.0.0", 
        "department": "Support",
        "status": "active",
        "total_interactions": random.randint(1200, 2000),
        "success_rate": random.uniform(0.85, 0.98),
        "avg_response_time": random.uniform(150, 400)
    },
    {
        "agent_name": "phase2_sales_pitch",
        "display_name": "Phase 2 Sales Pitch Agent",
        "version": "1.0.0",
        "department": "Sales", 
        "status": "active",
        "total_interactions": random.randint(500, 900),
        "success_rate": random.uniform(0.70, 0.88),
        "avg_response_time": random.uniform(800, 1500)
    },
    {
        "agent_name": "phase2_content_writer",
        "display_name": "Phase 2 Content Writer",
        "version": "1.0.0",
        "department": "Content",
        "status": "active",
        "total_interactions": random.randint(300, 600),
        "success_rate": random.uniform(0.80, 0.92),
        "avg_response_time": random.uniform(1200, 2500)
    },
    {
        "agent_name": "phase2_intent_classifier",
        "display_name": "Phase 2 Intent Classifier",
        "version": "1.0.0",
        "department": "Operations",
        "status": "active",
        "total_interactions": random.randint(2000, 3500),
        "success_rate": random.uniform(0.88, 0.96),
        "avg_response_time": random.uniform(80, 200)
    },
    {
        "agent_name": "phase2_email_personalizer",
        "display_name": "Phase 2 Email Personalizer",
        "version": "1.0.0",
        "department": "Marketing",
        "status": "active",
        "total_interactions": random.randint(400, 800),
        "success_rate": random.uniform(0.75, 0.89),
        "avg_response_time": random.uniform(300, 700)
    },
    {
        "agent_name": "phase2_social_media",
        "display_name": "Phase 2 Social Media Agent", 
        "version": "1.0.0",
        "department": "Marketing",
        "status": "active",
        "total_interactions": random.randint(600, 1100),
        "success_rate": random.uniform(0.78, 0.91),
        "avg_response_time": random.uniform(400, 900)
    },
    {
        "agent_name": "phase3_orchestrator",
        "display_name": "Phase 3 Orchestrator",
        "version": "1.0.0",
        "department": "Operations",
        "status": "active",
        "total_interactions": random.randint(200, 400),
        "success_rate": random.uniform(0.82, 0.94),
        "avg_response_time": random.uniform(150, 350)
    },
    {
        "agent_name": "phase3_rag_research",
        "display_name": "Phase 3 RAG Research Agent",
        "version": "1.0.0",
        "department": "Research",
        "status": "active",
        "total_interactions": random.randint(150, 300),
        "success_rate": random.uniform(0.85, 0.95),
        "avg_response_time": random.uniform(800, 1800)
    },
    {
        "agent_name": "phase3_sales_strategist",
        "display_name": "Phase 3 Sales Strategist",
        "version": "1.0.0",
        "department": "Sales",
        "status": "active", 
        "total_interactions": random.randint(100, 250),
        "success_rate": random.uniform(0.88, 0.96),
        "avg_response_time": random.uniform(1000, 2200)
    },
    {
        "agent_name": "phase3_marketing_campaign",
        "display_name": "Phase 3 Marketing Campaign Agent",
        "version": "1.0.0",
        "department": "Marketing",
        "status": "active",
        "total_interactions": random.randint(80, 180),
        "success_rate": random.uniform(0.78, 0.90),
        "avg_response_time": random.uniform(1500, 3000)
    },
    {
        "agent_name": "phase3_customer_success",
        "display_name": "Phase 3 Customer Success Agent",
        "version": "1.0.0",
        "department": "Support",
        "status": "active",
        "total_interactions": random.randint(120, 280),
        "success_rate": random.uniform(0.85, 0.94),
        "avg_response_time": random.uniform(400, 800)
    },
    {
        "agent_name": "phase4_digital_avatar",
        "display_name": "Phase 4 Digital Avatar",
        "version": "1.0.0",
        "department": "Innovation", 
        "status": "active",
        "total_interactions": random.randint(30, 80),
        "success_rate": random.uniform(0.70, 0.85),
        "avg_response_time": random.uniform(2000, 5000)
    },
    {
        "agent_name": "phase4_voice_conversation",
        "display_name": "Phase 4 Voice Conversation Agent",
        "version": "1.0.0",
        "department": "Innovation",
        "status": "active",
        "total_interactions": random.randint(20, 60),
        "success_rate": random.uniform(0.75, 0.88),
        "avg_response_time": random.uniform(1200, 2800)
    },
    {
        "agent_name": "phase4_multilingual",
        "display_name": "Phase 4 Multilingual Agent", 
        "version": "1.0.0",
        "department": "Operations",
        "status": "active",
        "total_interactions": random.randint(40, 100),
        "success_rate": random.uniform(0.80, 0.93),
        "avg_response_time": random.uniform(600, 1200)
    }
]

def generate_mock_events():
    """Generate mock system events"""
    events = []
    event_types = [
        ("Agent started successfully", "info"),
        ("High response time detected", "warning"), 
        ("API rate limit approaching", "warning"),
        ("Memory usage optimal", "info"),
        ("New workflow initiated", "info"),
        ("Error in agent processing", "error"),
        ("System backup completed", "info")
    ]
    
    for i in range(10):
        event_text, severity = random.choice(event_types)
        events.append({
            "id": f"event_{i+1}",
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat(),
            "message": f"{event_text} ({random.choice(MOCK_AGENTS)['agent_name']})",
            "severity": severity,
            "acknowledged": random.choice([True, False])
        })
    
    return sorted(events, key=lambda x: x['timestamp'], reverse=True)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mode": "test",
        "agents_loaded": len(MOCK_AGENTS),
        "agents": [agent["agent_name"] for agent in MOCK_AGENTS]
    }

# List available agents
@app.get("/agents")
async def list_agents():
    """List all available agents"""
    agents = db.get_agents()
    return {
        "agents": agents,
        "count": len(agents)
    }

# Control panel endpoints
@app.get("/control-panel/dashboard")
async def get_dashboard():
    """Get centralized control panel dashboard"""
    
    # Get real metrics from database
    metrics = db.get_dashboard_metrics()
    recent_events = db.get_recent_events(20)
    
    # Format events for the response
    formatted_events = []
    for event in recent_events:
        formatted_events.append({
            "id": f"event_{event['id']}",
            "timestamp": event['timestamp'],
            "message": f"{event['event_message']} ({event['agent_name'] or 'System'})",
            "severity": event['severity'],
            "acknowledged": event['acknowledged']
        })
    
    critical_events = [e for e in formatted_events if e["severity"] == "critical"]
    unacknowledged_warnings = [e for e in formatted_events if e["severity"] == "warning" and not e["acknowledged"]]
    
    return {
        'success': True,
        'dashboard': {
            'agent_statuses': db.get_agents(),
            'statistics_24h': {
                'total_interactions': metrics.get('total_interactions', 0),
                'successful_interactions': int(metrics.get('total_interactions', 0) * metrics.get('avg_success_rate', 0) / 100),
                'success_rate': metrics.get('avg_success_rate', 0),
                'error_count': int(metrics.get('total_interactions', 0) * (100 - metrics.get('avg_success_rate', 0)) / 100),
                'avg_response_time_ms': metrics.get('avg_response_time', 0),
                'active_workflows': random.randint(30, 60)
            },
            'statistics_1h': {
                'total_interactions': int(metrics.get('total_interactions', 0) * 0.05),
                'successful_interactions': int(metrics.get('total_interactions', 0) * metrics.get('avg_success_rate', 0) / 100 * 0.05),
                'success_rate': metrics.get('avg_success_rate', 0),
                'error_count': int(metrics.get('total_interactions', 0) * (100 - metrics.get('avg_success_rate', 0)) / 100 * 0.05)
            },
            'recent_events': formatted_events[:20],
            'critical_events': critical_events,
            'unacknowledged_warnings': unacknowledged_warnings,
            'real_time_metrics': {
                agent["agent_name"]: {
                    "total_interactions": agent["total_interactions"],
                    "successful": int(agent["total_interactions"] * agent["success_rate"]),
                    "failed": int(agent["total_interactions"] * (1 - agent["success_rate"])),
                    "avg_response_time": agent["avg_response_time"],
                    "last_activity": (datetime.now() - timedelta(seconds=random.randint(10, 300))).isoformat()
                }
                for agent in MOCK_AGENTS
            },
            'system_health': {
                'total_agents': len(MOCK_AGENTS),
                'active_agents': len([a for a in MOCK_AGENTS if a["status"] == "active"]),
                'error_count_24h': metrics.get('error_count', 0),
                'avg_success_rate': metrics.get('avg_success_rate', 0),
                'total_interactions_24h': metrics.get('total_interactions', 0)
            }
        },
        'timestamp': datetime.now().isoformat()
    }

@app.get("/control-panel/agents")
async def get_all_agents():
    """Get status and metrics for all agents"""
    return {
        'success': True,
        'total_agents': len(MOCK_AGENTS),
        'agents': MOCK_AGENTS,
        'timestamp': datetime.now().isoformat()
    }

@app.get("/control-panel/agent/{agent_name}")
async def get_agent_detail(agent_name: str, limit: int = 100):
    """Get detailed information for a specific agent"""
    agent = next((a for a in MOCK_AGENTS if a["agent_name"] == agent_name), None)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    # Generate mock recent activities
    activities = []
    for i in range(min(limit, 20)):
        activities.append({
            "id": f"activity_{i+1}",
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 120))).isoformat(),
            "agent_name": agent_name,
            "event_type": "interaction",
            "input_data": {"test": "mock_input"},
            "output_data": {"result": "mock_output"},
            "success": random.choice([True, True, True, False]),  # 75% success rate
            "response_time_ms": random.uniform(agent["avg_response_time"] * 0.5, agent["avg_response_time"] * 1.5),
            "workflow_id": f"wf_{random.randint(100, 999)}"
        })
    
    return {
        'success': True,
        'agent_name': agent_name,
        'status': agent,
        'real_time_metrics': {
            "total_interactions": agent["total_interactions"],
            "successful": int(agent["total_interactions"] * agent["success_rate"]),
            "failed": int(agent["total_interactions"] * (1 - agent["success_rate"])),
            "avg_response_time": agent["avg_response_time"],
            "last_activity": (datetime.now() - timedelta(minutes=random.randint(1, 30))).isoformat()
        },
        'recent_activities': activities,
        'activity_count': len(activities),
        'timestamp': datetime.now().isoformat()
    }

@app.get("/control-panel/activities")
async def get_activities(
    agent_name: Optional[str] = None,
    workflow_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get recent activities across all or specific agents"""
    
    # Generate mock activities
    activities = []
    target_agents = [agent_name] if agent_name else [agent["agent_name"] for agent in MOCK_AGENTS[:5]]
    
    for agent in target_agents:
        for i in range(random.randint(3, 8)):
            activities.append({
                "id": f"activity_{len(activities)+1}",
                "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 180))).isoformat(),
                "agent_name": agent,
                "event_type": random.choice(["interaction", "startup", "error", "warning"]),
                "success": random.choice([True, True, True, False]),
                "response_time_ms": random.uniform(100, 2000),
                "workflow_id": f"wf_{random.randint(100, 999)}" if workflow_id is None else workflow_id
            })
    
    # Sort by timestamp and apply pagination
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    paginated_activities = activities[offset:offset+limit]
    
    return {
        'success': True,
        'activities': paginated_activities,
        'count': len(paginated_activities),
        'filters': {
            'agent_name': agent_name,
            'workflow_id': workflow_id,
            'limit': limit,
            'offset': offset
        },
        'timestamp': datetime.now().isoformat()
    }

@app.get("/control-panel/workflow/{workflow_id}")
async def get_workflow_trace(workflow_id: str):
    """Get complete trace of a workflow across all agents"""
    
    # Generate mock workflow trace
    involved_agents = random.sample([agent["agent_name"] for agent in MOCK_AGENTS], random.randint(3, 6))
    timeline = []
    
    start_time = datetime.now() - timedelta(minutes=random.randint(5, 60))
    
    for i, agent in enumerate(involved_agents):
        step_time = start_time + timedelta(seconds=i * random.randint(5, 30))
        timeline.append({
            "timestamp": step_time.isoformat(),
            "agent_name": agent,
            "event_type": "interaction",
            "success": random.choice([True, True, True, False]),
            "response_time_ms": random.uniform(200, 1500),
            "step_number": i + 1
        })
    
    end_time = timeline[-1]["timestamp"] if timeline else start_time.isoformat()
    total_duration = (datetime.fromisoformat(end_time.replace('Z', '')) - start_time).total_seconds() * 1000
    successful_steps = sum(1 for step in timeline if step["success"])
    
    return {
        'success': True,
        'workflow_trace': {
            'workflow_id': workflow_id,
            'start_time': start_time.isoformat(),
            'end_time': end_time,
            'total_duration_ms': total_duration,
            'agents_involved': involved_agents,
            'total_steps': len(timeline),
            'successful_steps': successful_steps,
            'success_rate': successful_steps / len(timeline) if timeline else 0,
            'timeline': timeline,
            'inter_agent_messages': random.randint(2, 8)
        },
        'timestamp': datetime.now().isoformat()
    }

@app.get("/control-panel/events")
async def get_system_events(
    severity: Optional[str] = None,
    limit: int = 100,
    unacknowledged_only: bool = False
):
    """Get system events and alerts"""
    
    events = generate_mock_events()
    
    # Apply filters
    if severity:
        events = [e for e in events if e["severity"] == severity]
    
    if unacknowledged_only:
        events = [e for e in events if not e["acknowledged"]]
    
    events = events[:limit]
    
    return {
        'success': True,
        'events': events,
        'count': len(events),
        'filters': {
            'severity': severity,
            'unacknowledged_only': unacknowledged_only
        },
        'timestamp': datetime.now().isoformat()
    }

@app.get("/control-panel/statistics")
async def get_statistics(time_period: str = '24h'):
    """Get system-wide statistics for a time period"""
    
    multiplier = {'1h': 0.04, '24h': 1.0, '7d': 7.0}.get(time_period, 1.0)
    
    base_stats = {
        'total_interactions': int(sum(agent["total_interactions"] for agent in MOCK_AGENTS) * multiplier),
        'successful_interactions': int(sum(agent["total_interactions"] * agent["success_rate"] for agent in MOCK_AGENTS) * multiplier),
        'error_count': int(sum(agent["total_interactions"] * (1 - agent["success_rate"]) for agent in MOCK_AGENTS) * multiplier),
        'avg_response_time_ms': sum(agent["avg_response_time"] for agent in MOCK_AGENTS) / len(MOCK_AGENTS),
        'active_workflows': int(random.randint(20, 50) * multiplier),
        'agents_used': len(MOCK_AGENTS)
    }
    
    base_stats['success_rate'] = (base_stats['successful_interactions'] / base_stats['total_interactions'] * 100) if base_stats['total_interactions'] > 0 else 0
    
    return {
        'success': True,
        'statistics': base_stats,
        'time_period': time_period,
        'timestamp': datetime.now().isoformat()
    }

# Agent Processing Endpoints for n8n Integration
class LeadData(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    message: Optional[str] = None

class AgentRequest(BaseModel):
    lead_data: Optional[Dict[str, Any]] = None
    source: Optional[str] = "api"
    timestamp: Optional[str] = None

@app.post("/agents/prospect-research/process")
async def process_prospect_research(request: AgentRequest):
    """Process lead through Prospect Research Agent"""
    try:
        lead_data = request.lead_data or {}
        
        # Simulate prospect research processing
        qualification_score = random.uniform(0.3, 0.95)
        qualified = qualification_score > 0.7
        
        # Get agent info from database
        agent = db.get_agent_by_id(1)  # Prospect Research Agent
        if agent:
            db.add_interaction(1, qualified)
        
        result = {
            "agent_name": "Prospect Research Agent",
            "lead_id": lead_data.get('email', f"lead_{random.randint(1000, 9999)}"),
            "qualified": qualified,
            "score": round(qualification_score, 2),
            "company": lead_data.get('company', 'Unknown Company'),
            "industry": random.choice(['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail']),
            "pain_points": random.choice([
                ['Lead Generation', 'Sales Automation'],
                ['Customer Support', 'Process Optimization'],
                ['Marketing Efficiency', 'Data Analytics']
            ]),
            "disqualification_reason": "Low budget fit" if not qualified else None,
            "processing_time": round(random.uniform(0.5, 2.0), 1),
            "timestamp": datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prospect research failed: {str(e)}")

@app.post("/agents/sales-pitch/generate")
async def generate_sales_pitch(request: Dict[str, Any]):
    """Generate personalized sales pitch"""
    try:
        lead_profile = request.get('lead_profile', {})
        personalization_data = request.get('personalization_data', {})
        
        # Get agent info from database
        agent = db.get_agent_by_id(3)  # Sales Pitch Agent
        if agent:
            db.add_interaction(3, True)
        
        # Generate mock sales pitch
        company = personalization_data.get('company', 'your company')
        industry = personalization_data.get('industry', 'your industry')
        pain_points = personalization_data.get('pain_points', ['efficiency', 'automation'])
        
        pitch = f"""
        Hi {lead_profile.get('name', 'there')},

        I noticed {company} is in the {industry} space, and many companies like yours struggle with {', '.join(pain_points)}.

        SIX3 Agency has helped similar companies achieve:
        • 40% reduction in manual processes
        • 3x faster lead qualification
        • 85% improvement in response times

        Would you be interested in a 15-minute demo to see how we could help {company} achieve similar results?

        Best regards,
        SIX3 Agency AI Team
        """
        
        result = {
            "agent_name": "Sales Pitch Agent",
            "pitch_content": pitch.strip(),
            "personalization_score": round(random.uniform(0.7, 0.95), 2),
            "tone": "professional",
            "call_to_action": "Schedule 15-minute demo",
            "estimated_conversion_rate": f"{random.randint(12, 28)}%",
            "processing_time": round(random.uniform(1.0, 3.0), 1),
            "timestamp": datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sales pitch generation failed: {str(e)}")

@app.post("/agents/email-personalizer/create")
async def create_personalized_email(request: Dict[str, Any]):
    """Create personalized email"""
    try:
        lead_data = request.get('lead_data', {})
        sales_pitch = request.get('sales_pitch', {})
        email_template = request.get('email_template', 'default')
        
        # Get agent info from database
        agent = db.get_agent_by_id(5)  # Email Personalizer
        if agent:
            db.add_interaction(5, True)
        
        # Generate personalized email
        subject_lines = [
            f"Quick question about {lead_data.get('company', 'your company')}'s automation goals",
            f"15-minute efficiency boost for {lead_data.get('company', 'your team')}?",
            f"How {lead_data.get('company', 'companies like yours')} are saving 40% time",
        ]
        
        result = {
            "agent_name": "Email Personalizer",
            "email_subject": random.choice(subject_lines),
            "email_body": sales_pitch.get('pitch_content', 'Personalized content here'),
            "send_time": "optimal",
            "estimated_open_rate": f"{random.randint(22, 38)}%",
            "estimated_click_rate": f"{random.randint(3, 12)}%",
            "personalization_score": round(random.uniform(0.75, 0.95), 2),
            "processing_time": round(random.uniform(0.8, 2.5), 1),
            "timestamp": datetime.now().isoformat(),
            "scheduled": True,
            "send_at": (datetime.now() + timedelta(hours=2)).isoformat()
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email personalization failed: {str(e)}")

# Workflow Management Endpoints
@app.get("/workflows")
async def list_workflows():
    """List all SIX3 workflows from n8n"""
    workflows = n8n.get_workflows()
    return {
        "success": True,
        "workflows": workflows,
        "count": len(workflows)
    }

@app.post("/workflows/{workflow_name}/trigger")
async def trigger_workflow(workflow_name: str, data: Dict[str, Any]):
    """Trigger a specific workflow"""
    result = n8n.trigger_workflow(workflow_name, data)
    return result

@app.get("/workflows/templates")
async def get_workflow_templates():
    """Get available workflow templates"""
    templates = n8n.get_six3_workflow_templates()
    return {
        "success": True,
        "templates": templates,
        "count": len(templates)
    }

# Webhook endpoints for n8n integration testing
@app.post("/webhook/lead-qualification")
async def webhook_lead_qualification(request: Dict[str, Any]):
    """Webhook endpoint for testing lead qualification workflow"""
    # This simulates what n8n would call - it processes the entire workflow
    lead_data = request
    
    try:
        # Step 1: Prospect Research
        prospect_result = await process_prospect_research(AgentRequest(lead_data=lead_data, source="webhook"))
        
        if prospect_result["qualified"]:
            # Step 2: Generate Sales Pitch
            sales_pitch = await generate_sales_pitch({
                "lead_profile": lead_data,
                "personalization_data": {
                    "company": prospect_result["company"],
                    "industry": prospect_result["industry"],
                    "pain_points": prospect_result["pain_points"]
                }
            })
            
            # Step 3: Create Personalized Email
            email_result = await create_personalized_email({
                "lead_data": lead_data,
                "sales_pitch": sales_pitch,
                "email_template": "lead_qualification_followup"
            })
            
            return {
                "status": "lead_qualified",
                "lead_id": prospect_result["lead_id"],
                "qualification_score": prospect_result["score"],
                "next_action": "personalized_email_sent",
                "sales_pitch_generated": True,
                "email_scheduled": True,
                "email_details": email_result,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "lead_not_qualified",
                "lead_id": prospect_result["lead_id"],
                "qualification_score": prospect_result["score"],
                "reason": prospect_result["disqualification_reason"],
                "next_action": "nurture_campaign",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

@app.post("/webhook/email-personalization")
async def webhook_email_personalization(request: Dict[str, Any]):
    """Webhook endpoint for email campaign personalization"""
    try:
        campaign_data = request.get("campaign_data", {})
        contacts = request.get("contacts", [])
        
        results = []
        
        for contact in contacts:
            # Generate personalized email for each contact
            email_result = await create_personalized_email({
                "lead_data": contact,
                "sales_pitch": {"pitch_content": campaign_data.get("base_content", "")},
                "email_template": "campaign_email"
            })
            
            # Determine send schedule
            send_immediately = request.get("send_immediately", False)
            if send_immediately:
                status = "sent"
                send_info = {"sent_at": datetime.now().isoformat()}
            else:
                status = "scheduled"
                send_info = {"scheduled_for": (datetime.now() + timedelta(hours=2)).isoformat()}
            
            results.append({
                "status": status,
                "recipient": contact.get("email"),
                "subject": email_result["email_subject"],
                "campaign_id": campaign_data.get("id", f"campaign_{random.randint(1000, 9999)}"),
                **send_info
            })
        
        return {
            "success": True,
            "campaign_summary": {
                "total_emails": len(results),
                "sent_immediately": len([r for r in results if r["status"] == "sent"]),
                "scheduled": len([r for r in results if r["status"] == "scheduled"]),
                "estimated_total_open_rate": "28%",
                "estimated_total_click_rate": "7%"
            },
            "email_details": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email campaign processing failed: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("AGENT_SERVICE_PORT", 8000))
    print("🚀 Starting SIX3 Agency Test Agent Service")
    print(f"📊 Control Panel: Open /home/buntu/Instant-Agency/control-panel.html in browser")
    print(f"📝 API Docs: http://localhost:{port}/docs")
    print(f"💚 Health Check: http://localhost:{port}/health")
    print("🔄 n8n Workflows: https://n8n.six3.cloud")
    print("📧 n8n Login: ppc.fka@gmail.com | Password: PPCppc()()0024")
    print("📋 Workflow Naming: Prefix all workflows with 'SIX3'")
    
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )