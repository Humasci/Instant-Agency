#!/usr/bin/env python3
"""
SIX3 Agency Self-Service Customer Portal
FastAPI application with authentication, dashboard, and AI chatbot integration.
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import uuid

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# FastAPI and web framework imports
from fastapi import FastAPI, Depends, HTTPException, Request, Form, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.sessions import SessionMiddleware

# Authentication and security
from passlib.context import CryptContext
from jose import JWTError, jwt
import secrets

# Database
import sqlite3
from contextlib import contextmanager

# Import our agents
from agents.base_agent import BaseAgent
from agents.phase1_faq_chatbot import FAQChatbot
from agents.phase3_customer_success_agent import CustomerSuccessAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="SIX3 Agency Customer Portal",
    description="Self-service customer portal with AI assistance",
    version="1.0.0"
)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

# Templates and static files
templates = Jinja2Templates(directory="customer_portal/templates")
app.mount("/static", StaticFiles(directory="customer_portal/static"), name="static")

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Database setup
DATABASE_PATH = "customer_portal/portal.db"

def init_database():
    """Initialize the customer portal database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            company_name TEXT,
            phone TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    
    # Customer data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            service_type TEXT,
            subscription_status TEXT DEFAULT 'active',
            monthly_value DECIMAL(10,2),
            health_score INTEGER DEFAULT 75,
            onboarding_stage TEXT DEFAULT 'welcome',
            last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            csm_assigned TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Support tickets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            ticket_number TEXT UNIQUE,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            priority TEXT DEFAULT 'medium',
            category TEXT,
            assigned_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP
        )
    """)
    
    # Chat sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            session_id TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    """)
    
    # Chat messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT REFERENCES chat_sessions(session_id),
            message_type TEXT NOT NULL, -- 'user' or 'bot'
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            agent_name TEXT,
            confidence_score REAL
        )
    """)
    
    # Knowledge base articles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kb_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT,
            tags TEXT, -- JSON array
            views INTEGER DEFAULT 0,
            helpful_votes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_published BOOLEAN DEFAULT TRUE
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Initialize AI agents
faq_bot = FAQChatbot()
cs_agent = CustomerSuccessAgent()

# Authentication functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")

def get_current_user(email: str = Depends(verify_token)):
    """Get current user from database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))
        user = cursor.fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(user)

# Routes

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Landing page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    """Login endpoint"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))
        user = cursor.fetchone()
        
        if user and verify_password(password, user['hashed_password']):
            # Update last login
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user['id'],))
            conn.commit()
            
            # Create access token
            access_token = create_access_token(data={"sub": email})
            
            # Set session
            request.session["access_token"] = access_token
            request.session["user_email"] = email
            
            return RedirectResponse(url="/dashboard", status_code=303)
        else:
            return templates.TemplateResponse(
                "login.html", 
                {"request": request, "error": "Invalid email or password"}
            )

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    company_name: str = Form(None),
    phone: str = Form(None)
):
    """Registration endpoint"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return templates.TemplateResponse(
                    "register.html",
                    {"request": request, "error": "Email already registered"}
                )
            
            # Create user
            hashed_password = get_password_hash(password)
            cursor.execute("""
                INSERT INTO users (email, hashed_password, full_name, company_name, phone)
                VALUES (?, ?, ?, ?, ?)
            """, (email, hashed_password, full_name, company_name, phone))
            
            user_id = cursor.lastrowid
            
            # Create customer data record
            cursor.execute("""
                INSERT INTO customer_data (user_id, service_type, subscription_status)
                VALUES (?, ?, ?)
            """, (user_id, "standard", "active"))
            
            conn.commit()
            
            # Auto-login after registration
            access_token = create_access_token(data={"sub": email})
            request.session["access_token"] = access_token
            request.session["user_email"] = email
            
            return RedirectResponse(url="/dashboard", status_code=303)
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Registration failed. Please try again."}
        )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Customer dashboard"""
    # Check session
    if "access_token" not in request.session:
        return RedirectResponse(url="/login")
    
    try:
        # Verify token and get user
        email = request.session.get("user_email")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.*, cd.* FROM users u
                LEFT JOIN customer_data cd ON u.id = cd.user_id
                WHERE u.email = ? AND u.is_active = 1
            """, (email,))
            user_data = cursor.fetchone()
            
            if not user_data:
                return RedirectResponse(url="/login")
            
            # Get recent tickets
            cursor.execute("""
                SELECT * FROM support_tickets 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 5
            """, (user_data['id'],))
            recent_tickets = cursor.fetchall()
            
            # Get dashboard data
            dashboard_data = {
                "user": dict(user_data),
                "recent_tickets": [dict(ticket) for ticket in recent_tickets],
                "health_score": user_data['health_score'] or 75,
                "subscription_status": user_data['subscription_status'] or 'active',
                "onboarding_stage": user_data['onboarding_stage'] or 'welcome'
            }
            
            return templates.TemplateResponse(
                "dashboard.html",
                {"request": request, "data": dashboard_data}
            )
            
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return RedirectResponse(url="/login")

@app.get("/support", response_class=HTMLResponse)
async def support_page(request: Request):
    """Support page with ticket creation"""
    if "access_token" not in request.session:
        return RedirectResponse(url="/login")
    
    try:
        email = request.session.get("user_email")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            # Get user's tickets
            cursor.execute("""
                SELECT * FROM support_tickets 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            """, (user['id'],))
            tickets = cursor.fetchall()
            
            return templates.TemplateResponse(
                "support.html",
                {
                    "request": request, 
                    "user": dict(user),
                    "tickets": [dict(ticket) for ticket in tickets]
                }
            )
            
    except Exception as e:
        logger.error(f"Support page error: {e}")
        return RedirectResponse(url="/login")

@app.post("/support/create-ticket")
async def create_ticket(
    request: Request,
    subject: str = Form(...),
    description: str = Form(...),
    priority: str = Form("medium"),
    category: str = Form("general")
):
    """Create support ticket"""
    if "access_token" not in request.session:
        return RedirectResponse(url="/login")
    
    try:
        email = request.session.get("user_email")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            # Generate ticket number
            ticket_number = f"SIX3-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
            
            cursor.execute("""
                INSERT INTO support_tickets 
                (user_id, ticket_number, subject, description, priority, category)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user['id'], ticket_number, subject, description, priority, category))
            
            conn.commit()
            
            return RedirectResponse(url="/support?created=true", status_code=303)
            
    except Exception as e:
        logger.error(f"Ticket creation error: {e}")
        return RedirectResponse(url="/support?error=true", status_code=303)

@app.get("/knowledge-base", response_class=HTMLResponse)
async def knowledge_base(request: Request):
    """Knowledge base page"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM kb_articles 
                WHERE is_published = 1 
                ORDER BY views DESC, created_at DESC
            """, )
            articles = cursor.fetchall()
            
            return templates.TemplateResponse(
                "knowledge_base.html",
                {"request": request, "articles": [dict(article) for article in articles]}
            )
            
    except Exception as e:
        logger.error(f"Knowledge base error: {e}")
        return templates.TemplateResponse("knowledge_base.html", {"request": request, "articles": []})

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """AI chat interface"""
    if "access_token" not in request.session:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("chat.html", {"request": request})

# API Endpoints

@app.post("/api/chat/start")
async def start_chat_session(current_user: dict = Depends(get_current_user)):
    """Start a new chat session"""
    try:
        session_id = str(uuid.uuid4())
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_sessions (user_id, session_id)
                VALUES (?, ?)
            """, (current_user['id'], session_id))
            conn.commit()
            
            return {"session_id": session_id, "status": "started"}
            
    except Exception as e:
        logger.error(f"Chat session start error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start chat session")

@app.post("/api/chat/message")
async def send_chat_message(
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Send message to AI chatbot"""
    try:
        session_id = request.get("session_id")
        message = request.get("message")
        
        if not session_id or not message:
            raise HTTPException(status_code=400, detail="Missing session_id or message")
        
        # Save user message
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_messages (session_id, message_type, content)
                VALUES (?, ?, ?)
            """, (session_id, "user", message))
            
            # Get user context for better responses
            cursor.execute("""
                SELECT cd.* FROM customer_data cd
                JOIN users u ON cd.user_id = u.id
                WHERE u.id = ?
            """, (current_user['id'],))
            customer_data = cursor.fetchone()
            
            conn.commit()
        
        # Process with AI agent
        context = {
            "user_id": current_user['id'],
            "user_name": current_user['full_name'],
            "company": current_user['company_name'],
            "subscription_status": customer_data['subscription_status'] if customer_data else 'unknown',
            "health_score": customer_data['health_score'] if customer_data else 75
        }
        
        # Determine which agent to use
        if any(keyword in message.lower() for keyword in ['support', 'help', 'problem', 'issue']):
            agent = cs_agent
            agent_name = "Customer Success"
        else:
            agent = faq_bot
            agent_name = "FAQ Bot"
        
        # Get AI response
        ai_response = agent.process_request({
            "message": message,
            "context": context
        })
        
        bot_message = ai_response.get("response", "I'm sorry, I couldn't process your request right now.")
        confidence = ai_response.get("confidence", 0.8)
        
        # Save bot response
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_messages (session_id, message_type, content, agent_name, confidence_score)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, "bot", bot_message, agent_name, confidence))
            conn.commit()
        
        return {
            "response": bot_message,
            "agent": agent_name,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Chat message error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message")

@app.get("/api/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get chat history for session"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cm.* FROM chat_messages cm
                JOIN chat_sessions cs ON cm.session_id = cs.session_id
                WHERE cs.session_id = ? AND cs.user_id = ?
                ORDER BY cm.timestamp ASC
            """, (session_id, current_user['id']))
            
            messages = cursor.fetchall()
            
            return {
                "session_id": session_id,
                "messages": [dict(msg) for msg in messages]
            }
            
    except Exception as e:
        logger.error(f"Chat history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat history")

@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics(current_user: dict = Depends(get_current_user)):
    """Get dashboard metrics for current user"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get customer data
            cursor.execute("""
                SELECT * FROM customer_data WHERE user_id = ?
            """, (current_user['id'],))
            customer_data = cursor.fetchone()
            
            # Get ticket counts
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM support_tickets 
                WHERE user_id = ?
                GROUP BY status
            """, (current_user['id'],))
            ticket_counts = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Get recent activity
            cursor.execute("""
                SELECT 'ticket' as type, subject as description, created_at
                FROM support_tickets 
                WHERE user_id = ?
                UNION ALL
                SELECT 'chat' as type, 'Chat session started' as description, created_at
                FROM chat_sessions 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 10
            """, (current_user['id'], current_user['id']))
            recent_activity = [dict(row) for row in cursor.fetchall()]
            
            metrics = {
                "health_score": customer_data['health_score'] if customer_data else 75,
                "subscription_status": customer_data['subscription_status'] if customer_data else 'active',
                "ticket_counts": ticket_counts,
                "recent_activity": recent_activity,
                "onboarding_progress": {
                    "current_stage": customer_data['onboarding_stage'] if customer_data else 'welcome',
                    "completion_percentage": 75
                }
            }
            
            return metrics
            
    except Exception as e:
        logger.error(f"Dashboard metrics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard metrics")

@app.post("/logout")
async def logout(request: Request):
    """Logout endpoint"""
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and seed data"""
    init_database()
    
    # Seed some knowledge base articles
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM kb_articles")
        if cursor.fetchone()['count'] == 0:
            sample_articles = [
                {
                    "title": "Getting Started with SIX3 Agency Services",
                    "content": "Welcome to SIX3 Agency! This guide will help you get started with our AI-powered business solutions...",
                    "category": "Getting Started",
                    "tags": '["onboarding", "getting-started", "basics"]'
                },
                {
                    "title": "How to Submit a Support Ticket",
                    "content": "If you need help with any of our services, you can submit a support ticket through the portal...",
                    "category": "Support",
                    "tags": '["support", "tickets", "help"]'
                },
                {
                    "title": "Understanding Your Health Score",
                    "content": "Your customer health score is calculated based on usage, satisfaction, and engagement metrics...",
                    "category": "Account Management",
                    "tags": '["health-score", "metrics", "account"]'
                }
            ]
            
            for article in sample_articles:
                cursor.execute("""
                    INSERT INTO kb_articles (title, content, category, tags)
                    VALUES (?, ?, ?, ?)
                """, (article["title"], article["content"], article["category"], article["tags"]))
            
            conn.commit()
            logger.info("Seeded knowledge base articles")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)