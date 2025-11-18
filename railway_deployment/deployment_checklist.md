# SIX3 Agency Railway Deployment Checklist

## 🚀 Pre-Deployment Preparation

### 1. Code Preparation
- [ ] Ensure all workflow localhost URLs updated to `https://api.six3agency.com`
- [ ] Create FastAPI main.py with all agent endpoints
- [ ] Add database schema and migrations
- [ ] Test locally with PostgreSQL

### 2. Repository Setup
- [ ] Push all code to GitHub repository
- [ ] Include railway_deployment/ files in root directory
- [ ] Verify Dockerfile and requirements.txt are present
- [ ] Add .gitignore for sensitive files

## 🛠 Railway Deployment Steps

### Step 1: Create Railway Project
1. Go to [railway.app](https://railway.app)
2. Sign up/login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your SIX3 Agency repository

### Step 2: Add Database
1. In your Railway project dashboard
2. Click "New" → "Database" → "PostgreSQL"
3. Wait for database to provision
4. Note the generated `DATABASE_URL`

### Step 3: Configure Environment Variables
1. Go to your API service → Settings → Variables
2. Add all variables from `environment_variables.md`
3. Required minimum variables:
   ```
   SECRET_KEY=your-secret-key
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   API_ENV=production
   ```

### Step 4: Configure Custom Domain
1. Go to Settings → Domains
2. Click "Custom Domain"
3. Enter: `api.six3agency.com`
4. Follow DNS configuration instructions
5. Wait for SSL certificate provisioning (5-10 minutes)

### Step 5: Deploy
1. Railway automatically builds and deploys on git push
2. Monitor deployment logs for errors
3. Check health endpoint: `https://api.six3agency.com/health`
4. Test agent endpoints: `https://api.six3agency.com/agents/search-marketing-expert/analyze`

## 🔧 Post-Deployment Configuration

### 1. Database Setup
- [ ] Run database migrations
- [ ] Create initial admin user
- [ ] Verify database connectivity

### 2. n8n Workflow Updates
- [ ] Update all workflow HTTP nodes to use `https://api.six3agency.com`
- [ ] Test webhook endpoints
- [ ] Activate workflows in n8n

### 3. Status Dashboard Deployment
- [ ] Deploy `status_dashboard.html` to Vercel
- [ ] Connect to `dashboard.six3agency.com`
- [ ] Update API endpoints in dashboard to pull real data

## 🧪 Testing Checklist

### API Endpoints
- [ ] `GET /health` - Health check
- [ ] `POST /agents/search-marketing-expert/analyze` - Marketing analysis
- [ ] `POST /agents/ai-media-expert/create-avatar` - Avatar creation
- [ ] `POST /agents/ml-ai-expert/fine-tune` - ML model training
- [ ] `GET /clients` - Client management
- [ ] `GET /status/clients` - Status tracking

### n8n Integration
- [ ] Lead qualification workflow
- [ ] Search marketing campaign workflow
- [ ] AI avatar production workflow
- [ ] ML model fine-tuning workflow
- [ ] Email personalization workflow
- [ ] Client onboarding workflow
- [ ] Generative AI video production workflow

### Performance
- [ ] Response times < 2 seconds
- [ ] Database connections stable
- [ ] No memory leaks
- [ ] Error handling working properly

## 📊 Monitoring Setup

### Railway Built-in Monitoring
- [ ] Enable metrics collection
- [ ] Set up uptime monitoring
- [ ] Configure alert notifications

### Custom Monitoring
- [ ] Application logging configured
- [ ] Error tracking setup
- [ ] Performance metrics collection

## 🔒 Security Verification

- [ ] HTTPS enabled and working
- [ ] Environment variables secure
- [ ] Database access restricted
- [ ] API rate limiting configured
- [ ] CORS properly configured

## 💰 Cost Optimization

### Railway Pricing (as of 2024)
- **Starter**: $5/month per service
- **Pro**: $20/month per service (more resources)
- **Database**: $5/month for PostgreSQL

### Expected Monthly Costs
- API Service: $5-20
- PostgreSQL: $5
- **Total**: $10-25/month

### Cost Monitoring
- [ ] Set up billing alerts
- [ ] Monitor resource usage
- [ ] Optimize container size if needed

## 🚨 Troubleshooting Common Issues

### Deployment Fails
1. Check build logs for Python dependency errors
2. Verify Dockerfile syntax
3. Ensure requirements.txt includes all dependencies

### Database Connection Errors
1. Verify `DATABASE_URL` environment variable
2. Check PostgreSQL service status in Railway
3. Test connection from Railway console

### API Timeouts
1. Check uvicorn configuration
2. Increase Railway service memory if needed
3. Optimize database queries

### n8n Webhook Errors
1. Verify API endpoints are accessible
2. Check CORS configuration
3. Ensure proper HTTP status codes returned

## ✅ Success Criteria

Deployment is successful when:
- [ ] All API endpoints respond correctly
- [ ] n8n workflows execute without errors
- [ ] Database operations complete successfully
- [ ] Status dashboard displays real data
- [ ] Custom domain SSL certificate is active
- [ ] Application performance meets requirements
- [ ] Monitoring and alerts are functional

## 📞 Support Resources

- **Railway Docs**: https://docs.railway.app/
- **Railway Discord**: https://railway.app/discord
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **n8n Docs**: https://docs.n8n.io/

## 🎯 Next Steps After Deployment

1. **Load Testing**: Test with realistic traffic
2. **Backup Setup**: Configure automated backups
3. **CDN Setup**: Consider CloudFlare for global performance
4. **Monitoring Enhancement**: Add custom metrics and dashboards
5. **Documentation**: Create API documentation with Swagger/OpenAPI