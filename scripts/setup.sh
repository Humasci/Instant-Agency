#!/bin/bash

#==============================================================================
# Instant Agency - Setup Script
# This script initializes the Instant Agency environment
#==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed"
        return 1
    else
        print_success "$1 is installed"
        return 0
    fi
}

#==============================================================================
# BANNER
#==============================================================================
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║              INSTANT AGENCY - SETUP WIZARD                    ║"
echo "║         AI-Powered Virtual Agent Agency Platform              ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

#==============================================================================
# STEP 1: Check Prerequisites
#==============================================================================
print_info "Step 1: Checking prerequisites..."
echo ""

PREREQUISITES_MET=true

check_command docker || PREREQUISITES_MET=false
check_command docker-compose || PREREQUISITES_MET=false
check_command python3 || PREREQUISITES_MET=false
check_command node || PREREQUISITES_MET=false
check_command git || PREREQUISITES_MET=false

echo ""

if [ "$PREREQUISITES_MET" = false ]; then
    print_error "Some prerequisites are missing. Please install them and try again."
    echo ""
    echo "Installation guides:"
    echo "- Docker: https://docs.docker.com/get-docker/"
    echo "- Docker Compose: https://docs.docker.com/compose/install/"
    echo "- Python 3: https://www.python.org/downloads/"
    echo "- Node.js: https://nodejs.org/"
    exit 1
fi

#==============================================================================
# STEP 2: Environment Setup
#==============================================================================
print_info "Step 2: Setting up environment configuration..."
echo ""

if [ ! -f .env ]; then
    print_info "Creating .env file from template..."
    cp .env.example .env
    print_success ".env file created"
    echo ""
    print_info "⚠️  IMPORTANT: Edit .env file and update the following:"
    echo "   - Database passwords"
    echo "   - API keys (Hugging Face, email provider, etc.)"
    echo "   - Admin credentials"
    echo ""
    read -p "Press Enter to continue after you've updated .env file..."
else
    print_success ".env file already exists"
fi

echo ""

#==============================================================================
# STEP 3: Create Required Directories
#==============================================================================
print_info "Step 3: Creating required directories..."
echo ""

mkdir -p logs
mkdir -p data/migrations
mkdir -p data/seeds
mkdir -p models/local
mkdir -p monitoring/prometheus
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources

print_success "Directories created"
echo ""

#==============================================================================
# STEP 4: Install Python Dependencies
#==============================================================================
print_info "Step 4: Installing Python dependencies..."
echo ""

if [ -f agents/requirements.txt ]; then
    if [ ! -d "venv" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi

    print_info "Installing Python packages..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r agents/requirements.txt
    deactivate
    print_success "Python dependencies installed"
else
    print_info "Skipping Python dependencies (requirements.txt not found)"
fi

echo ""

#==============================================================================
# STEP 5: Pull Docker Images
#==============================================================================
print_info "Step 5: Pulling Docker images (this may take a while)..."
echo ""

docker-compose pull

print_success "Docker images pulled"
echo ""

#==============================================================================
# STEP 6: Initialize Database
#==============================================================================
print_info "Step 6: Initializing database..."
echo ""

# Create init SQL if it doesn't exist
if [ ! -f data/migrations/00-init.sql ]; then
    cat > data/migrations/00-init.sql << 'EOF'
-- Initial database setup
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create tables will be added here by each service
EOF
    print_success "Database initialization script created"
fi

echo ""

#==============================================================================
# STEP 7: Create Prometheus Configuration
#==============================================================================
print_info "Step 7: Creating monitoring configuration..."
echo ""

if [ ! -f monitoring/prometheus/prometheus.yml ]; then
    cat > monitoring/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'n8n'
    static_configs:
      - targets: ['n8n:5678']

  - job_name: 'agent-service'
    static_configs:
      - targets: ['agent-service:8000']
EOF
    print_success "Prometheus configuration created"
fi

echo ""

#==============================================================================
# STEP 8: Start Services
#==============================================================================
print_info "Step 8: Starting services..."
echo ""

read -p "Do you want to start all services now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose up -d

    print_success "Services started!"
    echo ""
    print_info "Waiting for services to be ready..."
    sleep 10

    # Check service health
    print_info "Checking service health..."
    echo ""

    if docker-compose ps | grep -q "Up"; then
        print_success "Services are running"
    else
        print_error "Some services failed to start. Check logs with: docker-compose logs"
    fi
fi

echo ""

#==============================================================================
# STEP 9: Display Access Information
#==============================================================================
print_success "Setup completed!"
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    ACCESS INFORMATION                          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 n8n Workflow Editor:     http://localhost:5678"
echo "   Username: admin (check .env for password)"
echo ""
echo "📈 Metabase Analytics:      http://localhost:3000"
echo "   Setup on first access"
echo ""
echo "🎯 SuiteCRM:                http://localhost:8080"
echo "   Username: admin (check .env for password)"
echo ""
echo "📉 Grafana Dashboards:      http://localhost:3001"
echo "   Username: admin / admin"
echo ""
echo "🔍 Prometheus:              http://localhost:9090"
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                      NEXT STEPS                                ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "1. Access n8n and import initial workflows:"
echo "   cd workflows && ./import-workflows.sh"
echo ""
echo "2. Configure CRM and create first contact"
echo ""
echo "3. Set up Metabase connection to PostgreSQL:"
echo "   Host: postgres"
echo "   Database: instant_agency"
echo "   User/Password: check .env file"
echo ""
echo "4. Deploy AI agents:"
echo "   source venv/bin/activate"
echo "   cd agents && python deploy.py"
echo ""
echo "5. Read the documentation:"
echo "   docs/SETUP.md - Detailed setup guide"
echo "   docs/ARCHITECTURE.md - System architecture"
echo "   docs/CONFIGURATION.md - Configuration options"
echo ""
echo "For help and support:"
echo "- Documentation: ./docs/"
echo "- Issues: https://github.com/Humasci/Instant-Agency/issues"
echo ""
print_success "Happy automating! 🚀"
echo ""
