#!/bin/bash

#==============================================================================
# Import n8n Workflows
# This script imports all workflow templates into n8n
#==============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_info() { echo -e "${YELLOW}ℹ${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }

echo ""
echo "n8n Workflow Import"
echo "==================="
echo ""

# Configuration
N8N_URL="${N8N_URL:-http://localhost:5678}"
N8N_USER="${N8N_USER:-admin}"
N8N_PASSWORD="${N8N_PASSWORD:-changeme}"

# Check if n8n is accessible
print_info "Checking n8n connection..."
if ! curl -s "${N8N_URL}/healthz" > /dev/null; then
    print_error "Cannot connect to n8n at ${N8N_URL}"
    print_info "Make sure n8n is running: docker-compose ps n8n"
    exit 1
fi
print_success "Connected to n8n"

echo ""
print_info "Finding workflow files..."

# Find all workflow JSON files
WORKFLOW_FILES=$(find . -name "*.json" -type f)
COUNT=$(echo "$WORKFLOW_FILES" | wc -l)

print_success "Found $COUNT workflow files"
echo ""

# Import each workflow
IMPORTED=0
FAILED=0

for WORKFLOW_FILE in $WORKFLOW_FILES; do
    WORKFLOW_NAME=$(basename "$WORKFLOW_FILE" .json)

    print_info "Importing: $WORKFLOW_NAME"

    # Import via n8n API
    # Note: This requires n8n API access - adjust based on your setup
    # For manual import, workflows can be imported through the UI

    RESPONSE=$(curl -s -X POST \
        -u "${N8N_USER}:${N8N_PASSWORD}" \
        -H "Content-Type: application/json" \
        -d @"$WORKFLOW_FILE" \
        "${N8N_URL}/api/v1/workflows" \
        -w "%{http_code}")

    HTTP_CODE="${RESPONSE: -3}"

    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
        print_success "Imported: $WORKFLOW_NAME"
        ((IMPORTED++))
    else
        print_error "Failed to import: $WORKFLOW_NAME (HTTP $HTTP_CODE)"
        ((FAILED++))
    fi
done

echo ""
echo "==================="
echo "Import Summary:"
echo "  Imported: $IMPORTED"
echo "  Failed: $FAILED"
echo "  Total: $COUNT"
echo ""

if [ $FAILED -eq 0 ]; then
    print_success "All workflows imported successfully!"
    echo ""
    print_info "Next steps:"
    echo "1. Open n8n at ${N8N_URL}"
    echo "2. Configure credentials for each workflow"
    echo "3. Test workflows with sample data"
    echo "4. Activate workflows"
else
    print_info "Some workflows failed to import automatically."
    print_info "You can import them manually through the n8n UI:"
    echo "  1. Open ${N8N_URL}"
    echo "  2. Click 'Import from File'"
    echo "  3. Select workflow JSON file"
fi

echo ""
