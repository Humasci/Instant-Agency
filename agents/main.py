"""
Main Agent Service API
FastAPI server that exposes all agents via REST API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
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


if __name__ == "__main__":
    port = int(os.getenv("AGENT_SERVICE_PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
