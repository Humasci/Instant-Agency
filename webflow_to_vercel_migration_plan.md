# Webflow → Vercel Migration Architecture Plan

## 🎯 **Perfect Setup for SIX3 Agency**

### Phase 1: Webflow Frontend + Google Cloud Backend
```
Frontend: Webflow (six3.agency)
├── Marketing website
├── Client portal pages
└── Status dashboard (embedded)

Backend: Google Cloud Free Tier (api.six3.agency)
├── FastAPI server
├── Expert agents
├── PostgreSQL database
└── n8n workflows (existing: n8n.six3.cloud)
```

### Phase 2: Migration to Vercel (when ready)
```
Frontend: Vercel Pro (six3.agency) 
├── Exported Webflow code
├── Enhanced with React/Next.js
└── Advanced dashboard features

Backend: Google Cloud (api.six3.agency)
├── Same API server (no changes needed)
├── Zero downtime migration
└── Same endpoints
```

---

## ✅ **Why This Architecture Works Perfectly**

### **Webflow Advantages:**
- ✅ **Visual design** - Perfect for marketing pages
- ✅ **Fast deployment** - Launch beautiful site in hours
- ✅ **SEO optimized** - Built-in best practices
- ✅ **Client-friendly** - Easy content updates
- ✅ **Professional templates** - Agency-focused designs

### **Google Cloud Backend:**
- ✅ **Always free tier** - $0/month for API server
- ✅ **PostgreSQL included** - Managed database
- ✅ **Auto-scaling** - Handle traffic spikes
- ✅ **Global CDN** - Fast API responses

### **Easy Migration Path:**
- ✅ **Same API endpoints** - No backend changes
- ✅ **Webflow export** - Get clean HTML/CSS/JS
- ✅ **Gradual migration** - Move pages one by one
- ✅ **Zero downtime** - Switch DNS when ready

---

## 🚀 **Phase 1: Webflow + Google Cloud Setup**

### **Step 1: Google Cloud Backend (30 minutes)**

#### **1.1 Create VM Instance (Free Tier)**
```bash
# Create always-free f1-micro instance
gcloud compute instances create six3-api \
  --zone=us-central1-a \
  --machine-type=f1-micro \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=30GB \
  --boot-disk-type=pd-standard \
  --tags=http-server,https-server

# Get external IP
gcloud compute instances describe six3-api --zone=us-central1-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

#### **1.2 Deploy FastAPI Server**
```bash
# SSH into instance
gcloud compute ssh six3-api --zone=us-central1-a

# Install dependencies
sudo apt update && sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx git

# Clone repository
git clone https://github.com/your-username/Instant-Agency.git
cd Instant-Agency

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r railway_deployment/requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/six3-api.service > /dev/null <<EOF
[Unit]
Description=SIX3 Agency API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/Instant-Agency
Environment=PATH=/home/$USER/Instant-Agency/venv/bin
ExecStart=/home/$USER/Instant-Agency/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl enable six3-api
sudo systemctl start six3-api

# Configure nginx
sudo tee /etc/nginx/sites-available/six3-api > /dev/null <<EOF
server {
    listen 80;
    server_name api.six3.agency;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/six3-api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d api.six3.agency
```

#### **1.3 Setup Database (Neon Free)**
1. Create database at [neon.tech](https://console.neon.tech)
2. Get connection string
3. Update `.env` file on server
4. Apply schema: `psql "$DATABASE_URL" -f database_schema.sql`

### **Step 2: Webflow Frontend (2 hours)**

#### **2.1 Webflow Site Setup**
1. **Create Webflow account** (if not already)
2. **Choose template** - Agency/SaaS template
3. **Customize design** - Your branding, content
4. **Set custom domain** - `six3.agency`

#### **2.2 Add Status Dashboard**
```html
<!-- Embed code in Webflow -->
<div id="dashboard-container">
  <iframe src="https://your-vercel-dashboard.vercel.app" 
          width="100%" 
          height="800px" 
          frameborder="0">
  </iframe>
</div>
```

#### **2.3 API Integration**
```javascript
<!-- Custom code in Webflow -->
<script>
// Connect to your Google Cloud API
const API_BASE = 'https://api.six3.agency';

async function loadClientData() {
  try {
    const response = await fetch(`${API_BASE}/clients`);
    const clients = await response.json();
    // Update Webflow elements with data
  } catch (error) {
    console.error('API Error:', error);
  }
}

// Load data when page loads
document.addEventListener('DOMContentLoaded', loadClientData);
</script>
```

---

## 🔄 **Phase 2: Migration to Vercel (Future)**

### **Migration Strategy (Zero Downtime)**

#### **Step 1: Export from Webflow**
```bash
# Webflow provides clean HTML/CSS/JS export
# Download and extract to local folder
unzip webflow-export.zip
```

#### **Step 2: Convert to Vercel**
```bash
# Option A: Keep as static HTML
cp -r webflow-export/* vercel-project/

# Option B: Convert to Next.js
npx create-next-app@latest six3-agency --typescript
# Import Webflow styles and components
```

#### **Step 3: Deploy to Vercel**
```bash
# Deploy to staging first
vercel --prod

# Test all functionality
# Update DNS when ready
```

#### **Step 4: Enhanced Features**
- Add React components for dynamic data
- Integrate real-time dashboard updates
- Add client portal functionality
- Implement advanced analytics

---

## 💰 **Cost Breakdown**

### **Phase 1: Webflow + Google Cloud**
- **Webflow**: $14-23/month (Site plan)
- **Google Cloud**: $0/month (free tier)
- **Domain**: $12/year
- **Total**: ~$15-25/month

### **Phase 2: Vercel + Google Cloud**
- **Vercel Pro**: $20/month (you already have)
- **Google Cloud**: $0/month (free tier)
- **Domain**: $12/year
- **Total**: ~$20/month

---

## 📋 **Immediate Action Plan**

### **Today (1 hour):**
1. **Set up Google Cloud VM** - Deploy API server
2. **Create Neon database** - Free PostgreSQL
3. **Configure DNS** - Point `api.six3.agency` to VM

### **This Week:**
1. **Design Webflow site** - Use agency template
2. **Connect API endpoints** - Integrate with backend
3. **Test workflows** - Import to your existing n8n

### **Next Month:**
1. **Optimize Webflow site** - Content, SEO, performance
2. **Plan Vercel migration** - Export and enhance
3. **Add advanced features** - Real-time updates, portal

---

## 🎯 **Key Benefits of This Plan**

✅ **Start Fast**: Webflow site live in hours  
✅ **Cost Effective**: Google Cloud free tier  
✅ **Professional**: Beautiful design without coding  
✅ **Scalable**: Easy migration to Vercel later  
✅ **Flexible**: Best of both worlds approach  

**This gives you a professional agency website immediately, with a clear upgrade path to a fully custom solution when you're ready!**