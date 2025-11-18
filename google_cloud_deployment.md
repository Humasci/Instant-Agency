# Google Cloud Free Tier Deployment Guide

## 🆓 **Google Cloud Always Free Tier Details**

### **What You Get Forever (No Expiration):**
- ✅ **1 f1-micro VM instance** (0.2 vCPU, 0.6GB RAM)
- ✅ **30GB standard persistent disk**
- ✅ **5GB snapshot storage**
- ✅ **1GB network egress per month** (within North America)
- ✅ **Cloud SQL**: 1 shared-core instance
- ✅ **Cloud Storage**: 5GB regional storage
- ✅ **Cloud Build**: 120 build-minutes per day

### **Perfect for SIX3 Agency API Server:**
- API server uses ~200-400MB RAM
- Database can run on Cloud SQL shared-core
- 30GB storage plenty for logs and files
- 1GB monthly egress sufficient for API calls

---

## 🚀 **Quick Setup Commands**

### **Step 1: Install Google Cloud CLI**
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Or use Cloud Shell (no installation needed)
# Go to console.cloud.google.com → click Cloud Shell icon
```

### **Step 2: Create Project and VM**
```bash
# Create new project
gcloud projects create six3-agency-$(date +%s) --name="SIX3 Agency"
gcloud config set project six3-agency-$(date +%s)

# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable sql-admin.googleapis.com

# Create firewall rules
gcloud compute firewall-rules create default-allow-http \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTP"

gcloud compute firewall-rules create default-allow-https \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTPS"

# Create VM instance (always free)
gcloud compute instances create six3-api-server \
    --zone=us-central1-a \
    --machine-type=f1-micro \
    --boot-disk-size=30GB \
    --boot-disk-type=pd-standard \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --tags=http-server,https-server \
    --metadata=startup-script='#!/bin/bash
apt update
apt install -y python3-pip python3-venv nginx git
systemctl enable nginx
systemctl start nginx'

# Get external IP address
gcloud compute instances describe six3-api-server \
    --zone=us-central1-a \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

### **Step 3: Setup Database (Cloud SQL Free Tier)**
```bash
# Create Cloud SQL instance (shared-core is free)
gcloud sql instances create six3-db \
    --database-version=POSTGRES_13 \
    --cpu=1 \
    --memory=1.7GB \
    --storage-size=10GB \
    --storage-type=SSD \
    --authorized-networks=0.0.0.0/0 \
    --region=us-central1

# Create database
gcloud sql databases create six3_agency --instance=six3-db

# Create user
gcloud sql users create six3user --instance=six3-db --password=your_secure_password

# Get connection details
gcloud sql instances describe six3-db --format='get(connectionName)'
gcloud sql instances describe six3-db --format='get(ipAddresses[0].ipAddress)'
```

### **Step 4: Deploy Application**
```bash
# SSH into your VM
gcloud compute ssh six3-api-server --zone=us-central1-a

# Clone repository
git clone https://github.com/your-username/Instant-Agency.git
cd Instant-Agency

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r railway_deployment/requirements.txt

# Create environment file
cat > .env << EOF
DATABASE_URL=postgresql://six3user:your_secure_password@VM_EXTERNAL_IP/six3_agency
API_ENV=production
SECRET_KEY=$(openssl rand -base64 32)
CORS_ORIGINS=https://six3.agency,https://www.six3.agency
# Add your other API keys from existing .env
EOF

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
sudo systemctl status six3-api

# Configure nginx reverse proxy
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
    
    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/six3-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Install SSL certificate
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.six3.agency --non-interactive --agree-tos --email your-email@gmail.com
```

---

## 🔧 **Alternative: Simpler Setup with Docker**

### **Docker Deployment (Easier)**
```bash
# SSH into VM
gcloud compute ssh six3-api-server --zone=us-central1-a

# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker

# Clone and setup
git clone https://github.com/your-username/Instant-Agency.git
cd Instant-Agency

# Create docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=your_database_url
      - API_ENV=production
    restart: always
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - api
    restart: always
EOF

# Deploy
docker-compose up -d
```

---

## 📊 **Resource Monitoring**

### **Check Free Tier Usage**
```bash
# Monitor VM usage
gcloud compute instances list
gcloud compute disks list

# Monitor SQL usage
gcloud sql instances list

# Check billing (should be $0)
gcloud billing projects describe your-project-id
```

### **Performance Optimization**
```bash
# Optimize for f1-micro (limited resources)
# 1. Use lightweight Python packages
# 2. Enable gzip compression in nginx
# 3. Use connection pooling for database
# 4. Cache static responses
```

---

## 🌍 **Domain Setup**

### **Configure DNS (Cloudflare Recommended)**
```
# Add these DNS records:
A     api.six3.agency    VM_EXTERNAL_IP
A     six3.agency        WEBFLOW_IP
CNAME www.six3.agency    six3.agency
```

### **Test Deployment**
```bash
# Test API health
curl https://api.six3.agency/health

# Test specific endpoints
curl -X POST https://api.six3.agency/agents/search-marketing-expert/analyze \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

---

## ⚡ **Cost Monitoring & Alerts**

### **Set Billing Alerts**
```bash
# Create billing budget
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="SIX3 Agency Budget" \
  --budget-amount=10USD \
  --threshold-rule=percent=90
```

### **Expected Costs**
- **VM f1-micro**: $0 (always free)
- **Cloud SQL shared-core**: $0 (always free)  
- **Storage 30GB**: $0 (always free)
- **Network egress 1GB**: $0 (always free)
- **Total Monthly**: $0

---

## 🎯 **Production Checklist**

- [ ] VM instance created and running
- [ ] Database connected and schema applied
- [ ] API server responding to health checks
- [ ] SSL certificate installed and working
- [ ] DNS records pointing to correct IPs
- [ ] Environment variables configured
- [ ] Monitoring and alerts set up
- [ ] Backup strategy implemented
- [ ] Security rules configured

**Your Google Cloud backend will be production-ready and completely free!**