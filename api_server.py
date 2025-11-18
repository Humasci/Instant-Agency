"""
SIX3 Agency API Server
FastAPI server providing endpoints for service delivery orchestration
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from service_delivery_orchestrator import ServiceDeliveryOrchestrator
from search_marketing_specialist import SearchMarketingSpecialist
from generative_ai_media_specialist import GenerativeAIMediaSpecialist
from n8n_integration import n8n

app = FastAPI(
    title="SIX3 Agency Service API",
    description="AI-powered digital marketing service delivery platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize service agents
orchestrator = ServiceDeliveryOrchestrator()
search_specialist = SearchMarketingSpecialist()
media_specialist = GenerativeAIMediaSpecialist()

# Pydantic models for request/response
class ClientData(BaseModel):
    client_id: Optional[str] = None
    company: str
    industry: str
    contact_email: str
    website: Optional[str] = None
    marketing_budget: Optional[float] = None
    target_audience: Optional[Dict[str, Any]] = None
    brand_guidelines: Optional[Dict[str, Any]] = None

class ServiceRequest(BaseModel):
    client_data: ClientData
    services_requested: List[str]
    requirements: Optional[Dict[str, Any]] = None
    priority: Optional[str] = "standard"
    timeline: Optional[str] = "standard"

class SearchMarketingRequest(BaseModel):
    client_id: str
    industry: str
    platforms: List[str] = ["google_ads", "meta_ads"]
    budget: float
    campaign_requirements: Dict[str, Any]
    auto_launch: bool = False

class AIMediaRequest(BaseModel):
    client_id: str
    media_type: str = "avatar_video"
    use_case: str
    brand_guidelines: Dict[str, Any]
    content_requirements: Dict[str, Any]
    timeline: str = "standard"

class MLModelRequest(BaseModel):
    client_id: str
    model_type: str = "language_model"
    data_requirements: Dict[str, Any]
    objectives: List[str]
    timeline: str = "standard"

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple token validation - in production, use proper JWT validation"""
    # For demo purposes, accept any token starting with 'six3_'
    if not credentials.credentials.startswith('six3_'):
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return {"user_id": credentials.credentials}

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "orchestrator": "active",
            "search_marketing": "active", 
            "ai_media": "active",
            "n8n_integration": "active"
        }
    }

# Service capability endpoints
@app.get("/capabilities")
async def get_service_capabilities():
    """Get available service capabilities"""
    result = orchestrator.process({'action': 'capability_assessment'})
    return result

@app.get("/services")
async def list_services():
    """List available services"""
    return {
        "available_services": [
            {
                "id": "search_marketing",
                "name": "Search Marketing & Paid Media",
                "description": "AI-driven search marketing with advanced algorithm optimization",
                "typical_timeline": "2-4 weeks setup, ongoing optimization",
                "min_budget": 1000
            },
            {
                "id": "generative_ai_media", 
                "name": "Generative AI Video & Audio",
                "description": "AI avatars and generative models for unique multimedia content",
                "typical_timeline": "1-2 weeks production",
                "min_budget": 2000
            },
            {
                "id": "ml_model_tuning",
                "name": "Fine-Tuning ML Models", 
                "description": "Custom AI models tailored to client data and objectives",
                "typical_timeline": "3-6 weeks development",
                "min_budget": 5000
            }
        ]
    }

# Client management endpoints
@app.post("/clients/onboard")
async def onboard_client(request: ServiceRequest, user: dict = Depends(get_current_user)):
    """Onboard new client with requested services"""
    try:
        # Generate client ID if not provided
        if not request.client_data.client_id:
            request.client_data.client_id = f"client_{int(datetime.now().timestamp())}"
        
        # Process through orchestrator
        result = orchestrator.process({
            'action': 'new_client',
            'client_data': request.client_data.dict(),
            'services_requested': request.services_requested,
            'requirements': request.requirements or {}
        })
        
        if result.get('success'):
            return {
                "success": True,
                "client_id": request.client_data.client_id,
                "message": "Client successfully onboarded",
                "services_initialized": result.get('services_initialized', []),
                "follow_up_tasks": result.get('follow_up_tasks', []),
                "estimated_timelines": result.get('estimated_timelines', {}),
                "portal_url": f"https://portal.six3.agency/clients/{request.client_data.client_id}"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Onboarding failed'))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Onboarding error: {str(e)}")

@app.get("/clients/{client_id}/status")
async def get_client_status(client_id: str, user: dict = Depends(get_current_user)):
    """Get client service status"""
    # In production, this would query a database
    return {
        "client_id": client_id,
        "status": "active",
        "services": {
            "search_marketing": {"status": "active", "performance": "exceeding_targets"},
            "ai_media": {"status": "in_production", "completion": "75%"},
            "ml_tuning": {"status": "data_processing", "completion": "30%"}
        },
        "last_updated": datetime.now().isoformat()
    }

# Service-specific endpoints
@app.post("/services/search-marketing/campaigns")
async def create_search_campaign(
    request: SearchMarketingRequest, 
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Create and launch search marketing campaign"""
    try:
        result = search_specialist.process({
            'action': 'campaign_setup',
            'client_data': {'client_id': request.client_id, 'industry': request.industry},
            'campaign_requirements': request.campaign_requirements,
            'platforms': request.platforms,
            'budget': request.budget
        })
        
        if result.get('success'):
            # Trigger n8n workflow in background
            background_tasks.add_task(
                trigger_n8n_workflow,
                "SIX3 Search Marketing Campaign Optimizer",
                request.dict()
            )
            
            return {
                "success": True,
                "campaign_id": f"camp_{int(datetime.now().timestamp())}",
                "message": "Search marketing campaign created successfully",
                "setup_details": result,
                "go_live_date": result.get('go_live_date'),
                "tracking_url": f"https://dashboard.six3.agency/campaigns/{request.client_id}"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error'))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign creation failed: {str(e)}")

@app.post("/services/ai-media/content")
async def create_ai_media(
    request: AIMediaRequest,
    background_tasks: BackgroundTasks, 
    user: dict = Depends(get_current_user)
):
    """Create AI-generated media content"""
    try:
        result = media_specialist.process({
            'action': 'content_production',
            'client_data': {'client_id': request.client_id},
            'content_requirements': request.content_requirements,
            'media_type': request.media_type,
            'timeline': request.timeline
        })
        
        if result.get('success'):
            # Trigger n8n workflow in background
            background_tasks.add_task(
                trigger_n8n_workflow,
                "SIX3 Generative AI Video & Audio Production",
                request.dict()
            )
            
            return {
                "success": True,
                "production_id": f"prod_{int(datetime.now().timestamp())}",
                "message": "AI media production started successfully",
                "production_details": result,
                "estimated_delivery": result.get('estimated_delivery'),
                "preview_url": f"https://portal.six3.agency/productions/{request.client_id}"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error'))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Media production failed: {str(e)}")

@app.post("/services/ml-tuning/models")
async def create_ml_model(
    request: MLModelRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Create and train custom ML model"""
    try:
        # For now, return a simulated response since ML tuning agent is complex
        # In production, this would use the actual ML tuning specialist
        
        # Trigger n8n workflow in background
        background_tasks.add_task(
            trigger_n8n_workflow,
            "SIX3 ML Model FineTuning",
            request.dict()
        )
        
        return {
            "success": True,
            "model_id": f"model_{int(datetime.now().timestamp())}",
            "message": "ML model training initiated successfully",
            "model_details": {
                "model_type": request.model_type,
                "objectives": request.objectives,
                "estimated_training_time": "3-4 weeks",
                "data_processing_status": "initiated"
            },
            "estimated_completion": (datetime.now().strftime('%Y-%m-%d')),
            "tracking_url": f"https://portal.six3.agency/models/{request.client_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML model creation failed: {str(e)}")

# Webhook endpoints for n8n integration
@app.post("/webhooks/lead-qualification")
async def webhook_lead_qualification(lead_data: Dict[str, Any]):
    """Webhook endpoint for lead qualification workflow"""
    try:
        # Process lead through orchestrator
        result = orchestrator.process({
            'action': 'service_request',
            'service_type': 'lead_qualification',
            'client_id': 'prospect',
            'requirements': lead_data
        })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lead qualification failed: {str(e)}")

@app.post("/webhooks/campaign-optimization")
async def webhook_campaign_optimization(campaign_data: Dict[str, Any]):
    """Webhook endpoint for campaign optimization"""
    try:
        result = search_specialist.process({
            'action': 'optimization',
            'campaign_data': campaign_data
        })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign optimization failed: {str(e)}")

# Analytics and reporting endpoints
@app.get("/analytics/dashboard")
async def get_dashboard_analytics(user: dict = Depends(get_current_user)):
    """Get dashboard analytics data"""
    try:
        n8n_data = n8n.get_dashboard_data()
        
        return {
            "success": True,
            "data": {
                "active_clients": 25,
                "active_campaigns": 48,
                "total_workflows": n8n_data.get('data', {}).get('total_workflows', 0),
                "success_rate": n8n_data.get('data', {}).get('success_rate', 0),
                "monthly_revenue": 125000,
                "client_satisfaction": 4.8,
                "service_performance": {
                    "search_marketing": {"active": 15, "avg_roas": "4.2x"},
                    "ai_media": {"in_production": 8, "completion_rate": "98%"},
                    "ml_tuning": {"active": 5, "success_rate": "100%"}
                }
            },
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/reports/performance")
async def get_performance_report(
    client_id: Optional[str] = None,
    service_type: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """Get detailed performance report"""
    # In production, this would generate actual reports from data
    return {
        "report_id": f"report_{int(datetime.now().timestamp())}",
        "filters": {"client_id": client_id, "service_type": service_type},
        "summary": {
            "total_campaigns": 15,
            "total_spend": 75000,
            "total_revenue": 285000,
            "overall_roas": "3.8x",
            "active_projects": 12
        },
        "generated_at": datetime.now().isoformat()
    }

# Background tasks
async def trigger_n8n_workflow(workflow_name: str, data: Dict[str, Any]):
    """Trigger n8n workflow in background"""
    try:
        result = n8n.trigger_workflow(workflow_name, data)
        print(f"Triggered workflow {workflow_name}: {result.get('success', False)}")
    except Exception as e:
        print(f"Failed to trigger workflow {workflow_name}: {e}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting SIX3 Agency API Server...")
    print("📊 Service endpoints available:")
    print("   • Client onboarding: POST /clients/onboard")
    print("   • Search marketing: POST /services/search-marketing/campaigns")
    print("   • AI media: POST /services/ai-media/content")
    print("   • ML tuning: POST /services/ml-tuning/models")
    print("   • Analytics: GET /analytics/dashboard")
    print("   • Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )