#!/bin/bash

#==============================================================================
# Instant Agency - Health Check Script
# Verifies all services are running correctly
#==============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_info() { echo -e "${YELLOW}ℹ${NC} $1"; }

echo ""
echo "Instant Agency - Health Check"
echo "=============================="
echo ""

FAILED=0

# Check Docker
echo "Docker Services:"
if docker-compose ps | grep -q "Up"; then
    print_success "Docker services are running"
else
    print_error "Docker services are not running"
    FAILED=$((FAILED + 1))
fi

# Check PostgreSQL
echo ""
echo "Database:"
if docker-compose exec -T postgres pg_isready -U instant_agency &> /dev/null; then
    print_success "PostgreSQL is accessible"
else
    print_error "PostgreSQL is not accessible"
    FAILED=$((FAILED + 1))
fi

# Check Redis
echo ""
echo "Cache:"
if docker-compose exec -T redis redis-cli -a "${REDIS_PASSWORD:-changeme}" ping | grep -q "PONG"; then
    print_success "Redis is responding"
else
    print_error "Redis is not responding"
    FAILED=$((FAILED + 1))
fi

# Check n8n
echo ""
echo "Workflow Automation:"
if curl -s http://localhost:5678/healthz &> /dev/null; then
    print_success "n8n is accessible"
else
    print_error "n8n is not accessible"
    FAILED=$((FAILED + 1))
fi

# Check CRM
echo ""
echo "CRM:"
if curl -s http://localhost:8080 &> /dev/null; then
    print_success "SuiteCRM is accessible"
else
    print_error "SuiteCRM is not accessible"
    FAILED=$((FAILED + 1))
fi

# Check Metabase
echo ""
echo "Analytics:"
if curl -s http://localhost:3000 &> /dev/null; then
    print_success "Metabase is accessible"
else
    print_error "Metabase is not accessible"
    FAILED=$((FAILED + 1))
fi

# Check Chroma
echo ""
echo "Vector Database:"
if curl -s http://localhost:8000/api/v1/heartbeat &> /dev/null; then
    print_success "Chroma is accessible"
else
    print_error "Chroma is not accessible"
    FAILED=$((FAILED + 1))
fi

# Check Prometheus
echo ""
echo "Monitoring:"
if curl -s http://localhost:9090/-/healthy &> /dev/null; then
    print_success "Prometheus is healthy"
else
    print_error "Prometheus is not healthy"
    FAILED=$((FAILED + 1))
fi

# Check Grafana
if curl -s http://localhost:3001/api/health &> /dev/null; then
    print_success "Grafana is accessible"
else
    print_error "Grafana is not accessible"
    FAILED=$((FAILED + 1))
fi

# Summary
echo ""
echo "=============================="
if [ $FAILED -eq 0 ]; then
    print_success "All health checks passed!"
    exit 0
else
    print_error "$FAILED health check(s) failed"
    echo ""
    echo "To debug issues:"
    echo "  docker-compose logs [service-name]"
    echo "  docker-compose ps"
    exit 1
fi
