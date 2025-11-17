# Attio CRM - Free Tier Guide

Complete guide for using Attio CRM with the free tier and integration with our AI agents.

## Attio Free Tier Features

### ✅ What's Included (Free Forever)

**Core Features:**
- ✅ **Unlimited records** - People, companies, deals
- ✅ **Up to 3 users** - Perfect for small teams
- ✅ **API access** - Full API with rate limits
- ✅ **2,000 API calls/month** - Sufficient for testing and small operations
- ✅ **Basic automations** - Limited to 100 automation runs/month
- ✅ **Custom attributes** - Flexible data model
- ✅ **Notes & comments** - Unlimited
- ✅ **Tasks & reminders** - Basic task management
- ✅ **Email sync** - Gmail/Outlook integration
- ✅ **Mobile apps** - iOS & Android

**What This Means:**
- You can store unlimited leads/customers
- Perfect for startups and testing
- Our AI agent integration works fully on free tier
- Ideal for up to ~60-70 leads/month with AI qualification

### ❌ Free Tier Limitations

**API Rate Limits:**
- 2,000 API calls per month (~67 calls/day)
- Rate limit: 10 requests per second
- Webhook events: Limited to 100/month

**Feature Restrictions:**
- Advanced automations: Paid only
- Custom views: Limited to 5
- Data exports: Manual only
- Reporting: Basic only
- Integrations: Limited selection

### 💰 When to Upgrade

**Upgrade to Plus ($29/user/month) when you need:**
- More than 2,000 API calls/month
- More than 3 users
- Advanced reporting
- More automation runs
- Priority support

**Our Integration Usage:**
Each AI-qualified lead = ~3-5 API calls:
1. Create person (1 call)
2. Create company (1 call, if new)
3. Add note (1 call)
4. Update tags (1 call)
5. Get/search records (1 call)

**Free tier = ~400-670 AI-qualified leads/month** ✅

## API Call Optimization

### How Our Integration is Optimized for Free Tier

**1. Batching (Coming Soon)**
```python
# Instead of: 5 calls for 5 leads
# We'll do: 1 batch call for 5 leads
```

**2. Caching**
```python
# Company lookups are cached locally
# Reduces duplicate API calls
```

**3. Conditional Updates**
```python
# Only update if data changed
# Skip unnecessary API calls
```

**4. Local Database**
```python
# SQLite stores local copies
# Reduces read API calls
```

### Monitoring Your Usage

**Check API usage in Attio:**
1. Go to Settings → Developers
2. View "API Usage" dashboard
3. Monitor: Calls used / 2,000 limit

**In our system:**
```bash
# Check usage via control panel
curl http://localhost:8000/control-panel/dashboard

# View Attio-specific stats
curl http://localhost:8000/control-panel/agent/phase1_prospect
```

## Free Tier Workflows

### Recommended Workflows for Free Tier

#### 1. Lead Qualification Only (Most Efficient)
```
Website Form → AI Qualify → Attio CRM
Calls per lead: 3-4
Monthly capacity: ~500-670 leads
```

#### 2. Lead + Customer Success (Balanced)
```
Leads: 300/month = 1,200 calls
Daily CS checks: 50 customers = 800 calls
Total: 2,000 calls ✅
```

#### 3. Full Sales Pipeline (Tight)
```
Leads: 200/month = 800 calls
Deal updates: 100/month = 200 calls
CS checks: 200/month = 1,000 calls
Total: 2,000 calls ✅
```

### What to Avoid on Free Tier

❌ **Don't do:**
- Frequent bulk updates (use scheduled batches instead)
- Real-time syncing every minute (use hourly/daily)
- Duplicate API calls (implement caching)
- Webhook-heavy workflows (100 webhook limit)

✅ **Do instead:**
- Batch operations (update multiple records at once)
- Schedule workflows (daily/weekly vs. real-time)
- Cache frequently accessed data
- Use local database for reads

## Alternative: Hybrid Approach

### Use Attio + Local Database

**Setup:**
```python
# Primary data in SQLite (unlimited, free)
# Sync key records to Attio (within limits)
```

**Benefits:**
- Unlimited local records
- Sync only important leads to Attio
- Stay within free tier forever
- Full analytics via Metabase

**Implementation:**
1. All leads go to local SQLite
2. Hot leads (score > 7) sync to Attio
3. Customer records sync to Attio
4. Archive old leads locally

**API usage:**
- Only ~100-200 Attio API calls/month
- Infinite local storage
- Best of both worlds

## Setup Guide - Free Tier

### Step 1: Sign Up for Attio

```bash
# 1. Go to https://attio.com
# 2. Sign up for free account
# 3. Complete onboarding
```

### Step 2: Get API Key

```bash
# 1. In Attio, go to Settings → Developers
# 2. Click "Create API Key"
# 3. Name it: "SIX3 Agency AI Agents"
# 4. Copy the key (starts with "sk_")
```

### Step 3: Configure Environment

```bash
# Add to your .env file
ATTIO_API_KEY=sk_your_api_key_here

# Or export
export ATTIO_API_KEY="sk_your_api_key_here"
```

### Step 4: Test Integration

```bash
# Start agents
cd agents
python main.py

# Test Attio integration
cd ../integrations/crm
python attio_integration.py

# Should see:
# ✓ Person created: person_abc123
# ✓ Company created: company_xyz789
# ✓ Note created: note_123456
```

### Step 5: Import n8n Workflow

```bash
# 1. Open n8n at http://localhost:5678
# 2. Go to Workflows → Import
# 3. Select: workflows/01_sales_lead_qualification.json
# 4. Configure Attio credentials in workflow
# 5. Activate workflow
```

## Data Model - Free Tier Optimized

### Recommended Attio Structure

**Objects:**
```
People (Leads & Customers)
├── Email (primary identifier)
├── Name
├── Company (linked)
├── Tags (lead, customer, hot, warm, cold)
├── Custom: ai_score (0-10)
├── Custom: qualification_status
├── Custom: lead_source
└── Custom: last_ai_check

Companies
├── Domain (primary identifier)
├── Name
├── Industry
├── Employee Count
└── Tags (prospect, customer)

Notes
├── Attached to People/Companies
└── AI analysis results

Tasks
├── Attached to People/Companies
└── CS follow-ups, sales actions
```

### Why This Structure?

- **Minimal API calls** - Simple, flat structure
- **Email as key** - Easy deduplication
- **Tags over custom objects** - More efficient
- **Notes for AI data** - Better than custom fields

## Migration Path

### From Free to Paid

**When you hit 2,000 API calls/month:**

**Option 1: Upgrade to Plus ($29/user/month)**
- 10,000 API calls/month
- Unlimited automations
- Advanced features

**Option 2: Optimize Further**
- Implement full local database
- Sync only VIP customers to Attio
- Use Attio as CRM UI, SQLite as data store

**Option 3: Alternative CRM**
- PostgreSQL + Metabase (free, unlimited)
- Our agents work with any database
- Build custom CRM interface

### From Other CRMs

**Migrating TO Attio from:**

**HubSpot Free:**
- Attio has better API
- More flexible data model
- Cleaner interface

**Salesforce:**
- Attio is simpler, cheaper
- Better for small teams
- Modern UX

**Google Sheets:**
- Attio adds structure
- Better search & filters
- API > Sheets API

## Best Practices

### 1. Design for Free Tier First

```python
# Always check before API call
if api_calls_today < 67:  # 2000/30 days
    sync_to_attio(lead)
else:
    save_to_local_db(lead)  # Fallback
```

### 2. Monitor Usage Daily

```bash
# Add to cron
0 9 * * * curl https://api.attio.com/v2/usage >> usage.log
```

### 3. Set Alerts

```python
# Alert at 80% usage
if api_calls_this_month > 1600:
    send_alert("Approaching Attio API limit")
```

### 4. Cache Aggressively

```python
# Cache company lookups for 24h
@cache(ttl=86400)
def get_company_by_domain(domain):
    return attio.get_company_by_domain(domain)
```

### 5. Batch Weekend Updates

```bash
# Sync all week's data on Sunday
0 2 * * 0 python scripts/weekly_attio_sync.py
```

## Comparison: Free Tier CRMs

| Feature | Attio Free | HubSpot Free | Salesforce | Sheets |
|---------|------------|--------------|------------|--------|
| Records | Unlimited | 1,000 | Varies | Unlimited |
| Users | 3 | 1 | Varies | Unlimited |
| API Calls | 2,000/mo | 100/day | Pay per use | 100/min |
| API Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Learning Curve | Easy | Medium | Hard | Easy |
| Cost | Free | Free → $50/mo | $25/user | Free |
| Best For | Startups | SMBs | Enterprise | Testing |

**Our Recommendation: Attio Free Tier** ✅

## Support & Resources

**Official Attio Resources:**
- API Docs: https://developers.attio.com
- Help Center: https://help.attio.com
- Community: https://community.attio.com

**Our Resources:**
- Integration code: `/integrations/crm/attio_integration.py`
- Example workflows: `/workflows/`
- Test suite: `python integrations/crm/attio_integration.py`

**Questions?**
- Check API usage in Attio dashboard
- Review our control panel: `http://localhost:8000/control-panel/dashboard`
- Test in simulated mode first (no API calls)

---

**Summary:** Attio's free tier is perfect for our AI agent integration. With smart optimization, you can handle 400-670 AI-qualified leads per month completely free. Upgrade when you grow, or use our hybrid approach for unlimited local storage.
