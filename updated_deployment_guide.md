# SIX3 Agency Complete Deployment Guide

## 🎯 Your Current Setup
- **Vercel Pro**: Status dashboard and frontend
- **n8n**: Need to set up workflows (you don't have Pro subscription yet)
- **API Server**: Need hosting provider for FastAPI backend

---

## 🚀 Recommended Architecture

### Frontend: Vercel Pro ✅
```
Primary Domain: six3agency.com
Dashboard: dashboard.six3agency.com
- Status dashboard (status_dashboard.html)
- Control panel (control-panel-visual.html) 
- Marketing website
```

### Backend API: Railway (Recommended)
```
API Domain: api.six3agency.com
- FastAPI server with expert agents
- PostgreSQL database
- File storage for work products
Cost: ~$10-25/month
```

### Workflows: n8n Cloud or Self-Hosted
```
Workflow Domain: workflows.six3agency.com
- 7 SIX3 workflows
- Webhook endpoints
Options:
- n8n Cloud Pro: $50/month (managed)
- Self-hosted on Railway: ~$5/month (requires setup)
```

---

## 📋 Step-by-Step Deployment Plan

### Phase 1: Vercel Pro Deployment (10 minutes)

#### 1.1 Deploy Status Dashboard to Vercel
```bash
# In your project root
cp status_dashboard.html vercel_deployment/
cp control-panel-visual.html vercel_deployment/
cd vercel_deployment/

# Deploy to Vercel
vercel --prod
```

#### 1.2 Configure Custom Domains
In Vercel dashboard:
1. Add domain: `six3agency.com`
2. Add subdomain: `dashboard.six3agency.com` 
3. Configure DNS records as instructed
4. SSL certificates auto-provision

### Phase 2: API Server Deployment (30 minutes)

#### 2.1 Deploy to Railway
1. **Create Railway Account**: [railway.app](https://railway.app)
2. **Connect GitHub**: Link your repository
3. **Deploy Project**: 
   - Select "Deploy from GitHub repo"
   - Choose your SIX3 Agency repo
   - Railway auto-detects Python and deploys

#### 2.2 Add Database
1. Click "New" → "Database" → "PostgreSQL"
2. Railway auto-generates `DATABASE_URL`
3. Database ready in ~2 minutes

#### 2.3 Configure Environment Variables
Add these in Railway Settings → Variables:
```
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
API_ENV=production
CORS_ORIGINS=https://six3agency.com,https://dashboard.six3agency.com
```

#### 2.4 Set Custom Domain
1. Settings → Domains → Custom Domain
2. Enter: `api.six3agency.com`
3. Update DNS records as instructed
4. SSL auto-provisions

### Phase 3: n8n Workflow Setup (Choose One Option)

#### Option A: n8n Cloud (Easiest - $50/month)
1. Sign up at [n8n.cloud](https://n8n.cloud)
2. Choose Pro plan for custom domains
3. Import workflows using the guide: `n8n_workflow_import_guide.md`
4. Set custom domain: `workflows.six3agency.com`

#### Option B: Self-Hosted n8n on Railway ($5/month)
1. Create separate Railway project for n8n
2. Use Docker image: `n8nio/n8n:latest`
3. Add PostgreSQL database for n8n data
4. Set environment variables for n8n configuration
5. Deploy and import workflows manually

---

## 💰 Cost Breakdown

### With n8n Cloud:
- **Vercel Pro**: $20/month (you already have)
- **Railway API**: $15/month (API + DB)
- **n8n Cloud Pro**: $50/month
- **Total**: ~$85/month

### With Self-Hosted n8n:
- **Vercel Pro**: $20/month (you already have)
- **Railway API**: $15/month (API + DB)  
- **Railway n8n**: $5/month (n8n instance)
- **Total**: ~$40/month

### Budget Option (Start Here):
- **Vercel Pro**: $20/month (you already have)
- **Railway API**: $10/month (smaller instance)
- **Skip n8n**: Use direct API calls initially
- **Total**: ~$30/month

---

## 🎯 Immediate Next Steps (What to do now)

### 1. Deploy Status Dashboard to Vercel (10 minutes)
```bash
# Quick deployment
cd /home/buntu/Instant-Agency
vercel init
vercel --prod
```

### 2. Set Up Railway for API (20 minutes)
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "Deploy from GitHub repo"
4. Select your repository
5. Add PostgreSQL database
6. Set environment variables

### 3. Update Workflow URLs (5 minutes)
Since you don't have n8n running yet, temporarily update the workflows to call Railway directly:
```
# Instead of localhost:8000
https://api.six3agency.com/agents/[endpoint]
```

### 4. Test the Setup
1. Check API health: `https://api.six3agency.com/health`
2. Check dashboard: `https://dashboard.six3agency.com`
3. Test agent endpoints manually

---

## 🔧 Alternative: Start Simple and Scale

### Phase 1: Basic Setup ($30/month)
1. ✅ Vercel Pro for frontend
2. ✅ Railway for API server
3. ❌ Skip n8n initially - use direct API calls

### Phase 2: Add Automation ($85/month)
1. Add n8n Cloud when you need workflow automation
2. Import all 7 workflows
3. Full automation pipeline

### Phase 3: Enterprise ($40/month optimized)
1. Self-host n8n on Railway to reduce costs
2. Add monitoring and alerts
3. Scale based on usage

---

## 🚨 Urgent Setup Guide (Start in 30 minutes)

### Quick Railway Deployment
```bash
# 1. Create these files in your project root
echo 'fastapi==0.104.1
uvicorn[standard]==0.24.0
psycopg2-binary==2.9.7
sqlalchemy==2.0.23
pydantic==2.5.0
openai==1.3.7
anthropic==0.3.11' > requirements.txt

# 2. Create simple FastAPI server
cat > main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SIX3 Agency API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://six3agency.com", "https://dashboard.six3agency.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "six3-agency-api"}

@app.get("/")
def root():
    return {"message": "SIX3 Agency API Server", "version": "1.0.0"}

# Add your agent endpoints here
@app.post("/agents/search-marketing-expert/analyze")
def search_marketing_analyze(request: dict):
    return {"status": "success", "analysis": "Campaign analysis complete"}

EOF

# 3. Push to GitHub and deploy to Railway
git add .
git commit -m "Add FastAPI server for Railway deployment"
git push origin main
```

Then:
1. Go to Railway → Deploy from GitHub → Select repo
2. Railway automatically deploys Python apps
3. Add PostgreSQL database
4. Set custom domain: `api.six3agency.com`

### Quick Vercel Deployment
```bash
# Deploy dashboard to Vercel
cd /home/buntu/Instant-Agency
npx vercel --prod
```

**You'll have a working system in 30 minutes!**

This gives you the foundation to build upon. Add expert agents and n8n workflows incrementally as you develop the business logic.