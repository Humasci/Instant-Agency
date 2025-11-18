# n8n Community Edition Self-Hosted Setup (FREE)

## 🎯 Why Use n8n Community Edition?
- ✅ **100% FREE** - No monthly subscription fees
- ✅ **Full workflow automation** - All the features you need
- ✅ **Self-hosted control** - Your data, your server
- ✅ **Custom domains** - Use workflows.six3agency.com
- ✅ **No vendor lock-in** - Complete ownership

## 📋 Server Requirements for n8n Community Edition

### Minimum Requirements:
- **CPU**: 1 vCPU (2+ recommended for better performance)
- **RAM**: 1GB (2GB+ recommended)
- **Storage**: 10GB SSD (20GB+ recommended)
- **OS**: Ubuntu 20.04+ / Docker support
- **Network**: HTTP/HTTPS access (ports 80, 443)

### Recommended Production Setup:
- **CPU**: 2 vCPUs
- **RAM**: 2GB 
- **Storage**: 20GB SSD
- **Database**: PostgreSQL (can share with main API)
- **Reverse Proxy**: Nginx or Traefik for SSL

## 🎯 Updated Architecture (All Free Tiers Possible!)

### Option 1: Maximum Free Tier Usage
```
Frontend: Vercel Pro ($20/month - you already have)
API Server: Google Cloud Free Tier (FREE - $300 credit)
n8n: Google Cloud Free Tier (FREE - same instance)
Database: PostgreSQL on Google Cloud Free Tier (FREE)
```

### Option 2: AWS Free Tier
```
Frontend: Vercel Pro ($20/month - you already have)  
API Server: AWS EC2 t2.micro (FREE for 12 months)
n8n: Same AWS instance (FREE)
Database: AWS RDS PostgreSQL t2.micro (FREE for 12 months)
```

### Option 3: Hybrid Approach
```
Frontend: Vercel Pro ($20/month - you already have)
API Server: Railway ($10/month - simplest setup)
n8n: Google Cloud Free Tier (FREE)
Database: Railway PostgreSQL ($5/month)
```

## 🆓 Google Cloud Free Tier Details

### What's Included (Always Free):
- **Compute Engine**: 1 f1-micro instance (0.2 vCPU, 0.6GB RAM)
- **Cloud SQL**: 1 shared-core instance (PostgreSQL)
- **Storage**: 30GB standard disk
- **Network**: 1GB egress per month
- **$300 credit** for 90 days for any additional resources

### Perfect for SIX3 Agency:
- ✅ Enough for API server + n8n on single instance
- ✅ PostgreSQL database included
- ✅ External IP address included
- ✅ SSL certificates via Let's Encrypt

## 🆓 AWS Free Tier Details

### What's Included (12 months free):
- **EC2**: t2.micro instance (1 vCPU, 1GB RAM) - 750 hours/month
- **RDS**: t2.micro database (1 vCPU, 1GB RAM) - 750 hours/month  
- **S3**: 5GB storage
- **Elastic Load Balancer**: 750 hours/month
- **Data Transfer**: 15GB outbound per month

### Perfect for SIX3 Agency:
- ✅ Separate API server and database instances
- ✅ Load balancer for high availability
- ✅ S3 for file storage
- ✅ CloudFront CDN included

## 🐳 Docker Setup for n8n + API Server

### Single Instance Deployment (Google Cloud f1-micro):
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: six3_agency
      POSTGRES_USER: six3user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USERNAME}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://workflows.six3agency.com
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=six3user
      - DB_POSTGRESDB_PASSWORD=${DB_PASSWORD}
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://six3user:${DB_PASSWORD}@postgres:5432/six3_agency
      - API_ENV=production
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - postgres
    volumes:
      - ./agents:/app/agents

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - n8n
      - api

volumes:
  postgres_data:
  n8n_data:
```

## ☁️ Google Cloud Free Tier Setup (Recommended)

### Step 1: Create VM Instance
```bash
# Create f1-micro instance (always free)
gcloud compute instances create six3-agency-server \
  --zone=us-central1-a \
  --machine-type=f1-micro \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=30GB \
  --boot-disk-type=pd-standard \
  --tags=http-server,https-server
```

### Step 2: Install Dependencies
```bash
# SSH into the instance
gcloud compute ssh six3-agency-server

# Install Docker and Docker Compose
sudo apt update
sudo apt install -y docker.io docker-compose nginx certbot python3-certbot-nginx
sudo usermod -aG docker $USER
```

### Step 3: Deploy Services
```bash
# Clone your repository
git clone https://github.com/your-username/Instant-Agency.git
cd Instant-Agency

# Set environment variables
echo "DB_PASSWORD=your-secure-password
N8N_USERNAME=admin
N8N_PASSWORD=your-n8n-password
N8N_HOST=workflows.six3agency.com
SECRET_KEY=your-secret-key" > .env

# Deploy with Docker Compose
sudo docker-compose up -d
```

### Step 4: Configure SSL and Domains
```bash
# Install SSL certificates
sudo certbot --nginx -d api.six3agency.com -d workflows.six3agency.com
```

## 💰 Cost Comparison (Updated)

### Google Cloud Free Tier:
- **VM Instance**: FREE (f1-micro always free)
- **PostgreSQL**: FREE (shared-core always free)
- **SSL Certificates**: FREE (Let's Encrypt)
- **External IP**: FREE (1 static IP included)
- **Total**: $0/month (after $300 credit)

### AWS Free Tier (12 months):
- **EC2 Instance**: FREE (t2.micro)
- **RDS PostgreSQL**: FREE (t2.micro)  
- **Load Balancer**: FREE (750 hours)
- **Total**: $0/month for first year

### Railway (Paid but Simple):
- **API Service**: $5-10/month
- **PostgreSQL**: $5/month
- **n8n Service**: $5/month
- **Total**: $15-20/month

## 🎯 My Recommendation (Corrected)

### For Maximum Savings: Google Cloud Free Tier
1. **Single VM** running API + n8n + PostgreSQL
2. **Docker Compose** setup for easy management
3. **Nginx** reverse proxy for SSL termination
4. **Let's Encrypt** for free SSL certificates
5. **Total Cost**: $0/month (FREE!)

### For Simplicity: Railway
1. **Managed services** - less setup required
2. **Auto-scaling** and monitoring included
3. **One-click deployments**
4. **Total Cost**: $15-20/month

## 📋 Updated Server Requirements Summary

### Single Server (API + n8n + Database):
- **CPU**: 1-2 vCPUs (f1-micro works!)
- **RAM**: 1-2GB (0.6GB works for light usage)
- **Storage**: 20-30GB SSD
- **OS**: Ubuntu 20.04+
- **Network**: 1GB/month transfer (Google Cloud includes)

### Separate Services:
- **API Server**: 1 vCPU, 1GB RAM
- **n8n Instance**: 1 vCPU, 512MB RAM
- **Database**: Shared-core, 1GB RAM
- **Total**: Fits in free tier limits

You were absolutely right to question my initial recommendation. n8n Community Edition is FREE and perfect for your needs!