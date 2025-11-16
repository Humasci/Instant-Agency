"""
Main Agent Service API
FastAPI server that exposes all agents via REST API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import uvicorn
import os

# Import agents
from sales.qualification.agent import SalesQualificationAgent
from marketing.prospecting.agent import MarketingProspectingAgent

# Import Phase 1 agents
from phase1_prospect_agent import Phase1ProspectAgent
from phase1_faq_chatbot import Phase1FAQChatbot

# Import Phase 2 agents
from phase2_sales_pitch_agent import Phase2SalesPitchAgent
from phase2_content_writer_agent import Phase2ContentWriterAgent
from phase2_intent_classifier_agent import Phase2IntentClassifierAgent
from phase2_email_personalizer_agent import Phase2EmailPersonalizerAgent
from phase2_social_media_agent import Phase2SocialMediaAgent

# Import Phase 3 agents
from phase3_orchestrator_agent import Phase3OrchestratorAgent
from phase3_rag_research_agent import Phase3RAGResearchAgent
from phase3_sales_strategist_agent import Phase3SalesStrategistAgent
from phase3_marketing_campaign_agent import Phase3MarketingCampaignAgent
from phase3_customer_success_agent import Phase3CustomerSuccessAgent
from phase3_analytics_agent import Phase3AnalyticsAgent

# Import Phase 4 agents
from phase4_digital_avatar_agent import Phase4DigitalAvatarAgent
from phase4_voice_conversation_agent import Phase4VoiceConversationAgent
from phase4_multilingual_agent import Phase4MultilingualAgent
from phase4_realtime_conversation_agent import Phase4RealTimeConversationAgent
from phase4_advanced_personalization_agent import Phase4AdvancedPersonalizationAgent

# Initialize FastAPI app
app = FastAPI(
    title="Instant Agency - AI Agent Service",
    description="REST API for AI agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
agents = {}


@app.on_event("startup")
async def startup_event():
    """Initialize all agents on startup"""
    try:
        # Existing agents
        agents['sales_qualification'] = SalesQualificationAgent()
        agents['marketing_prospecting'] = MarketingProspectingAgent()

        # Phase 1 agents
        agents['phase1_prospect'] = Phase1ProspectAgent()
        agents['phase1_faq'] = Phase1FAQChatbot()

        # Phase 2 agents
        agents['phase2_sales_pitch'] = Phase2SalesPitchAgent()
        agents['phase2_content_writer'] = Phase2ContentWriterAgent()
        agents['phase2_intent_classifier'] = Phase2IntentClassifierAgent()
        agents['phase2_email_personalizer'] = Phase2EmailPersonalizerAgent()
        agents['phase2_social_media'] = Phase2SocialMediaAgent()

        # Phase 3 agents
        agents['phase3_orchestrator'] = Phase3OrchestratorAgent()
        agents['phase3_rag_research'] = Phase3RAGResearchAgent()
        agents['phase3_sales_strategist'] = Phase3SalesStrategistAgent()
        agents['phase3_marketing_campaign'] = Phase3MarketingCampaignAgent()
        agents['phase3_customer_success'] = Phase3CustomerSuccessAgent()
        agents['phase3_analytics'] = Phase3AnalyticsAgent()

        # Phase 4 agents
        agents['phase4_digital_avatar'] = Phase4DigitalAvatarAgent()
        agents['phase4_voice_conversation'] = Phase4VoiceConversationAgent()
        agents['phase4_multilingual'] = Phase4MultilingualAgent()
        agents['phase4_realtime_conversation'] = Phase4RealTimeConversationAgent()
        agents['phase4_advanced_personalization'] = Phase4AdvancedPersonalizationAgent()

        print("✓ All agents initialized successfully")
        print(f"  Loaded agents ({len(agents)}): {', '.join(agents.keys())}")
    except Exception as e:
        print(f"✗ Agent initialization failed: {e}")


# Request/Response models
class AgentRequest(BaseModel):
    agent_name: str
    input_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agents_loaded": len(agents),
        "agents": list(agents.keys())
    }


# List available agents
@app.get("/agents")
async def list_agents():
    """List all available agents"""
    agent_info = []

    for name, agent in agents.items():
        agent_info.append({
            "name": name,
            "display_name": agent.agent_name,
            "version": agent.version,
            "department": agent.config.get('agent', {}).get('department', 'unknown')
        })

    return {
        "agents": agent_info,
        "count": len(agent_info)
    }


# Process request with specific agent
@app.post("/agent/{agent_name}/process")
async def process_with_agent(agent_name: str, input_data: Dict[str, Any]):
    """
    Process input with a specific agent

    Args:
        agent_name: Name of the agent to use
        input_data: Input data for the agent

    Returns:
        Agent processing result
    """
    if agent_name not in agents:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found. Available agents: {list(agents.keys())}"
        )

    try:
        agent = agents[agent_name]
        result = agent.process(input_data)

        return {
            "success": True,
            "agent": agent_name,
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent processing failed: {str(e)}"
        )


# Sales endpoints
@app.post("/sales/qualify")
async def qualify_lead(lead_data: Dict[str, Any]):
    """Qualify a sales lead"""
    return await process_with_agent('sales_qualification', lead_data)


# Marketing endpoints
@app.post("/marketing/research-prospect")
async def research_prospect(prospect_data: Dict[str, Any]):
    """Research a prospect"""
    return await process_with_agent('marketing_prospecting', prospect_data)


# Phase 1 endpoints
@app.post("/phase1/qualify-lead")
async def phase1_qualify_lead(lead_data: Dict[str, Any]):
    """
    Phase 1: Qualify a lead using sentiment analysis

    Request body:
    {
        "lead_name": "John Smith",
        "lead_email": "john@example.com",
        "company": "Acme Corp",
        "industry": "Technology",
        "lead_message": "I'm interested in your product..."
    }
    """
    return await process_with_agent('phase1_prospect', lead_data)


@app.post("/phase1/faq")
async def phase1_faq(question_data: Dict[str, Any]):
    """
    Phase 1: Answer FAQ question

    Request body:
    {
        "question": "What is Instant Agency?",
        "user_id": "user_123",
        "context": "Optional context"
    }
    """
    return await process_with_agent('phase1_faq', question_data)


# Phase 2 endpoints
@app.post("/phase2/generate-sales-pitch")
async def phase2_sales_pitch(pitch_data: Dict[str, Any]):
    """
    Phase 2: Generate personalized sales pitch

    Request body:
    {
        "prospect_name": "John Smith",
        "company": "Acme Corp",
        "industry": "Technology",
        "pain_points": "Manual processes, slow sales cycle",
        "company_size": "50-100 employees",
        "trigger_event": "Recent funding",
        "current_solutions": "Spreadsheets and basic CRM"
    }
    """
    return await process_with_agent('phase2_sales_pitch', pitch_data)


@app.post("/phase2/write-content")
async def phase2_content(content_data: Dict[str, Any]):
    """
    Phase 2: Generate blog post or article

    Request body:
    {
        "topic": "AI Automation for Small Business",
        "content_type": "blog_post",
        "audience": "small business owners",
        "tone": "conversational",
        "word_count": 600,
        "keywords": ["AI", "automation", "productivity"],
        "key_points": ["Benefits", "Use cases", "Getting started"]
    }
    """
    return await process_with_agent('phase2_content_writer', content_data)


@app.post("/phase2/classify-intent")
async def phase2_intent(message_data: Dict[str, Any]):
    """
    Phase 2: Classify user message intent

    Request body:
    {
        "message": "How much does your platform cost?",
        "user_id": "user_123"
    }
    """
    return await process_with_agent('phase2_intent_classifier', message_data)


@app.post("/phase2/personalize-email")
async def phase2_email(email_data: Dict[str, Any]):
    """
    Phase 2: Generate personalized email

    Request body:
    {
        "recipient_name": "Sarah Johnson",
        "recipient_email": "sarah@company.com",
        "company": "TechCorp",
        "intent": "pricing",
        "original_message": "Can you send pricing info?",
        "email_type": "response"
    }
    """
    return await process_with_agent('phase2_email_personalizer', email_data)


@app.post("/phase2/create-social-posts")
async def phase2_social(social_data: Dict[str, Any]):
    """
    Phase 2: Create platform-specific social media posts

    Request body:
    {
        "content": "Your blog post or article content...",
        "topic": "AI Automation",
        "platforms": ["linkedin", "twitter", "facebook"],
        "target_audience": "business professionals",
        "cta": "Learn more",
        "link": "https://example.com/blog"
    }
    """
    return await process_with_agent('phase2_social_media', social_data)


# Generic agent execution endpoint
@app.post("/execute")
async def execute_agent(request: AgentRequest):
    """
    Execute any agent with input data

    Request body:
    {
        "agent_name": "sales_qualification",
        "input_data": {...},
        "context": {...}
    }
    """
    input_with_context = request.input_data.copy()
    if request.context:
        input_with_context['context'] = request.context

    return await process_with_agent(request.agent_name, input_with_context)


# Metrics endpoint
@app.get("/metrics/{agent_name}")
async def get_agent_metrics(agent_name: str):
    """Get metrics for a specific agent"""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    agent = agents[agent_name]

    # Get metrics from Redis
    if not agent.cache:
        return {"error": "Metrics not available - Redis not connected"}

    metrics = {}
    tracked_metrics = agent.config.get('monitoring', {}).get('track_metrics', [])

    for metric_name in tracked_metrics:
        key = f"metrics:{agent.agent_name}:{metric_name}"
        try:
            values = agent.cache.lrange(key, 0, 99)
            if values:
                # Parse timestamp:value format
                parsed_values = []
                for v in values:
                    if ':' in v:
                        timestamp, value = v.split(':', 1)
                        parsed_values.append({
                            'timestamp': timestamp,
                            'value': float(value)
                        })

                metrics[metric_name] = parsed_values
        except Exception as e:
            metrics[metric_name] = {"error": str(e)}

    return {
        "agent": agent_name,
        "metrics": metrics
    }


# Phase 3 endpoints
@app.post("/phase3/orchestrate")
async def phase3_orchestrate(workflow_data: Dict[str, Any]):
    """
    Phase 3: Orchestrate multi-agent workflow

    Request body:
    {
        "customer_id": "cust_001",
        "workflow_type": "lead_nurture" | "sales_cycle" | "support" | "content_marketing",
        "journey_stage": "awareness" | "consideration" | "decision",
        "engagement_score": 75,
        "current_state": {...}
    }
    """
    return await process_with_agent('phase3_orchestrator', workflow_data)


@app.post("/phase3/research")
async def phase3_research(research_data: Dict[str, Any]):
    """
    Phase 3: RAG-enhanced research

    Request body:
    {
        "query": "AI automation benefits for small businesses",
        "depth": "quick" | "standard" | "deep",
        "max_results": 5,
        "include_citations": true
    }
    """
    return await process_with_agent('phase3_rag_research', research_data)


@app.post("/phase3/sales-strategy")
async def phase3_sales_strategy(strategy_data: Dict[str, Any]):
    """
    Phase 3: Advanced sales strategy

    Request body:
    {
        "action": "analyze_deal" | "handle_objection" | "plan_campaign" | "qualify",
        "deal_data": {...},
        "prospect_data": {...},
        "stakeholders": [...]
    }
    """
    return await process_with_agent('phase3_sales_strategist', strategy_data)


@app.post("/phase3/marketing-campaign")
async def phase3_marketing_campaign(campaign_data: Dict[str, Any]):
    """
    Phase 3: Marketing campaign planning

    Request body:
    {
        "campaign_type": "awareness" | "consideration" | "conversion",
        "goal": "Generate 500 qualified leads",
        "target_audience": {...},
        "budget": 15000,
        "duration_days": 30,
        "channels": ["email", "social_media", "content"]
    }
    """
    return await process_with_agent('phase3_marketing_campaign', campaign_data)


@app.post("/phase3/customer-success")
async def phase3_customer_success(cs_data: Dict[str, Any]):
    """
    Phase 3: Customer success management

    Request body:
    {
        "action": "health_check" | "onboard" | "intervention" | "expansion_opportunity",
        "customer_id": "cust_001",
        "customer_data": {...},
        "usage_data": {...},
        "account_data": {...}
    }
    """
    return await process_with_agent('phase3_customer_success', cs_data)


@app.post("/phase3/analytics")
async def phase3_analytics(analytics_data: Dict[str, Any]):
    """
    Phase 3: Analytics and reporting

    Request body:
    {
        "report_type": "agent_performance" | "customer_journey" | "roi" | "executive_summary",
        "time_period": "daily" | "weekly" | "monthly" | "quarterly",
        "filters": {...}
    }
    """
    return await process_with_agent('phase3_analytics', analytics_data)


# Phase 4 endpoints
@app.post("/phase4/digital-avatar")
async def phase4_digital_avatar(avatar_data: Dict[str, Any]):
    """
    Phase 4: Digital Avatar Generation

    Request body:
    {
        "action": "create_video" | "start_stream" | "list_personas" | "get_video_status",
        "persona": "sarah" | "marcus" | "priya",
        "script": "Text for avatar to speak",
        "options": {
            "provider": "d-id" | "heygen" | "synthesia",
            "format": "mp4" | "webm",
            "quality": "standard" | "high"
        }
    }
    """
    return await process_with_agent('phase4_digital_avatar', avatar_data)


@app.post("/phase4/voice-conversation")
async def phase4_voice_conversation(voice_data: Dict[str, Any]):
    """
    Phase 4: Voice-Enabled Conversation

    Request body:
    {
        "action": "transcribe" | "synthesize" | "conversation_turn" | "list_voices",
        "audio_data": "base64 encoded audio" (for transcription),
        "text": "Text to synthesize" (for TTS),
        "voice": "professional" | "friendly" | "authoritative",
        "language": "en" | "es" | "fr" | "de"
    }
    """
    return await process_with_agent('phase4_voice_conversation', voice_data)


@app.post("/phase4/multilingual")
async def phase4_multilingual(multilingual_data: Dict[str, Any]):
    """
    Phase 4: Multilingual Translation

    Request body:
    {
        "action": "translate" | "detect_language" | "generate_multilingual" | "list_languages",
        "text": "Text to translate",
        "source_language": "en" (optional, auto-detect),
        "target_language": "es" (for single translation),
        "target_languages": ["es", "fr", "de"] (for multi-language)
    }
    """
    return await process_with_agent('phase4_multilingual', multilingual_data)


@app.post("/phase4/realtime-conversation")
async def phase4_realtime_conversation(conversation_data: Dict[str, Any]):
    """
    Phase 4: Real-Time Conversation (Avatar + Voice + AI)

    Request body:
    {
        "action": "start_session" | "process_turn" | "end_session" | "get_session_info",
        "session_id": "session_xyz" (for existing sessions),
        "persona": "sarah" | "marcus" | "priya",
        "input_type": "audio" | "text",
        "input_data": "User message or audio",
        "video_enabled": true | false,
        "language": "en" | "es" | "fr"
    }
    """
    return await process_with_agent('phase4_realtime_conversation', conversation_data)


@app.post("/phase4/personalization")
async def phase4_personalization(personalization_data: Dict[str, Any]):
    """
    Phase 4: Advanced Personalization

    Request body:
    {
        "action": "personalize_content" | "update_profile" | "get_profile" | "ab_test" | "segment_user" | "recommend",
        "user_id": "user_123",
        "content_type": "email" | "landing_page" | "product_recommendation",
        "context": {...},
        "behavior_data": {
            "email_opened": true,
            "link_clicked": true,
            "page_viewed": "/pricing",
            "purchase": {"amount": 999}
        },
        "test_id": "test_xyz" (for A/B testing)
    }
    """
    return await process_with_agent('phase4_advanced_personalization', personalization_data)


# ============================================================================
# CONTROL PANEL & MONITORING ENDPOINTS
# ============================================================================

@app.get("/control-panel/dashboard")
async def get_dashboard():
    """
    Get centralized control panel dashboard with all system metrics

    Returns comprehensive overview of all agents, activities, and system health
    """
    from central_logger import get_central_logger
    logger = get_central_logger()

    # Get all agent statuses
    agent_statuses = logger.get_all_agent_status()

    # Get system statistics
    stats_24h = logger.get_statistics('24h')
    stats_1h = logger.get_statistics('1h')

    # Get recent system events
    events = logger.get_system_events(limit=50)
    critical_events = logger.get_system_events(severity='critical', limit=10)
    warnings = logger.get_system_events(severity='warning', unacknowledged_only=True)

    # Get real-time metrics
    real_time = logger.get_real_time_metrics()

    return {
        'success': True,
        'dashboard': {
            'agent_statuses': agent_statuses,
            'statistics_24h': stats_24h,
            'statistics_1h': stats_1h,
            'recent_events': events[:20],
            'critical_events': critical_events,
            'unacknowledged_warnings': warnings,
            'real_time_metrics': real_time,
            'system_health': {
                'total_agents': len(agent_statuses),
                'active_agents': sum(1 for a in agent_statuses if a['status'] == 'active'),
                'error_count_24h': stats_24h.get('error_count', 0),
                'avg_success_rate': stats_24h.get('success_rate', 0),
                'total_interactions_24h': stats_24h.get('total_interactions', 0)
            }
        },
        'timestamp': datetime.now().isoformat()
    }


@app.get("/control-panel/agents")
async def get_all_agents():
    """Get status and metrics for all agents"""
    from central_logger import get_central_logger
    logger = get_central_logger()

    agent_statuses = logger.get_all_agent_status()
    real_time = logger.get_real_time_metrics()

    # Combine status and real-time metrics
    combined = []
    for status in agent_statuses:
        agent_name = status['agent_name']
        combined.append({
            **status,
            'real_time': real_time.get(agent_name, {})
        })

    return {
        'success': True,
        'total_agents': len(combined),
        'agents': combined,
        'timestamp': datetime.now().isoformat()
    }


@app.get("/control-panel/agent/{agent_name}")
async def get_agent_detail(agent_name: str, limit: int = 100):
    """Get detailed information for a specific agent"""
    from central_logger import get_central_logger
    logger = get_central_logger()

    # Get recent activities
    activities = logger.get_recent_activities(agent_name=agent_name, limit=limit)

    # Get agent status
    all_statuses = logger.get_all_agent_status()
    agent_status = next((a for a in all_statuses if a['agent_name'] == agent_name), None)

    # Get real-time metrics
    real_time = logger.get_real_time_metrics(agent_name)

    if not agent_status:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    return {
        'success': True,
        'agent_name': agent_name,
        'status': agent_status,
        'real_time_metrics': real_time,
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
    from central_logger import get_central_logger
    logger = get_central_logger()

    activities = logger.get_recent_activities(
        agent_name=agent_name,
        workflow_id=workflow_id,
        limit=limit,
        offset=offset
    )

    return {
        'success': True,
        'activities': activities,
        'count': len(activities),
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
    from central_logger import get_central_logger
    logger = get_central_logger()

    trace = logger.get_workflow_trace(workflow_id)

    return {
        'success': True,
        'workflow_trace': trace,
        'timestamp': datetime.now().isoformat()
    }


@app.get("/control-panel/events")
async def get_system_events(
    severity: Optional[str] = None,
    limit: int = 100,
    unacknowledged_only: bool = False
):
    """Get system events and alerts"""
    from central_logger import get_central_logger
    logger = get_central_logger()

    events = logger.get_system_events(
        severity=severity,
        limit=limit,
        unacknowledged_only=unacknowledged_only
    )

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
    from central_logger import get_central_logger
    logger = get_central_logger()

    stats = logger.get_statistics(time_period)

    return {
        'success': True,
        'statistics': stats,
        'timestamp': datetime.now().isoformat()
    }


@app.get("/control-panel/inter-agent-messages")
async def get_inter_agent_messages(agent_name: Optional[str] = None):
    """Get inter-agent communication messages"""
    from central_logger import get_central_logger
    logger = get_central_logger()

    if agent_name:
        messages = logger.get_unprocessed_messages(agent_name)
        return {
            'success': True,
            'agent_name': agent_name,
            'unprocessed_messages': messages,
            'count': len(messages),
            'timestamp': datetime.now().isoformat()
        }
    else:
        # Get all messages from database
        import sqlite3
        conn = sqlite3.connect(logger.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, timestamp, from_agent, to_agent, message_type, processed
            FROM inter_agent_messages
            ORDER BY timestamp DESC
            LIMIT 100
        """)

        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'timestamp': row[1],
                'from_agent': row[2],
                'to_agent': row[3],
                'message_type': row[4],
                'processed': bool(row[5])
            })

        conn.close()

        return {
            'success': True,
            'all_messages': messages,
            'count': len(messages),
            'timestamp': datetime.now().isoformat()
        }


if __name__ == "__main__":
    port = int(os.getenv("AGENT_SERVICE_PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
