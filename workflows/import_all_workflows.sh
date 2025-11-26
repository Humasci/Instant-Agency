#!/bin/bash
"""
Import All n8n Workflows Script for SIX3 Agency
Imports all workflow templates into n8n instance
"""

# Configuration
N8N_API_URL="${N8N_API_URL:-http://localhost:5678/api/v1}"
N8N_AUTH_TOKEN="${N8N_AUTH_TOKEN}"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 SIX3 Agency - n8n Workflow Import Script${NC}"
echo "=" * 50

# Check if n8n is running
echo -e "${YELLOW}📡 Checking n8n connection...${NC}"
if curl -s "$N8N_API_URL/workflows" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ n8n is accessible at $N8N_API_URL${NC}"
else
    echo -e "${RED}❌ n8n is not accessible at $N8N_API_URL${NC}"
    echo "Please ensure n8n is running and accessible."
    exit 1
fi

# Function to import a workflow
import_workflow() {
    local workflow_file="$1"
    local workflow_name=$(basename "$workflow_file" .json)
    
    echo -e "${YELLOW}📥 Importing: $workflow_name${NC}"
    
    # Check if file exists
    if [ ! -f "$workflow_file" ]; then
        echo -e "${RED}❌ File not found: $workflow_file${NC}"
        return 1
    fi
    
    # Import workflow via n8n API
    if [ -n "$N8N_AUTH_TOKEN" ]; then
        response=$(curl -s -X POST "$N8N_API_URL/workflows/import" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $N8N_AUTH_TOKEN" \
            -d @"$workflow_file")
    else
        response=$(curl -s -X POST "$N8N_API_URL/workflows/import" \
            -H "Content-Type: application/json" \
            -d @"$workflow_file")
    fi
    
    # Check response
    if echo "$response" | grep -q '"id"'; then
        workflow_id=$(echo "$response" | grep -o '"id":[^,]*' | cut -d':' -f2 | tr -d ' "')
        echo -e "${GREEN}✅ Successfully imported: $workflow_name (ID: $workflow_id)${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to import: $workflow_name${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Import all workflow files
echo -e "\n${BLUE}📂 Importing Workflow Templates...${NC}"

# Array of workflow files in import order
workflows=(
    "01_sales_lead_qualification.json"
    "02_marketing_content_pipeline.json"
    "03_customer_success_monitoring.json"
    "04_complete_customer_lifecycle.json"
    "05_linkedin_outreach_sequence.json"
    "06_cold_email_campaign.json"
    "07_content_driven_lead_gen.json"
    "08_event_webinar_follow_up.json"
    "SIX3_Lead_Qualification.json"
    "SIX3_AI_Avatar_Production.json"
    "SIX3_Client_Onboarding.json"
    "SIX3_Email_Personalization.json"
    "SIX3_Generative_AI_Video_Production.json"
    "SIX3_ML_Model_FineTuning.json"
    "SIX3_Search_Marketing_Campaign.json"
    "Phase2_Email_Campaign_Scheduler.json"
)

# Track import results
imported_count=0
failed_count=0

# Import each workflow
for workflow in "${workflows[@]}"; do
    if import_workflow "$workflow"; then
        ((imported_count++))
    else
        ((failed_count++))
    fi
    echo # Add blank line
done

# Import summary
echo -e "${BLUE}📊 Import Summary:${NC}"
echo -e "${GREEN}✅ Successfully imported: $imported_count workflows${NC}"
if [ $failed_count -gt 0 ]; then
    echo -e "${RED}❌ Failed to import: $failed_count workflows${NC}"
fi

# Check for additional workflow files
echo -e "\n${YELLOW}🔍 Checking for additional workflow files...${NC}"
additional_files=$(find . -name "*.json" -not -name "package*.json" | grep -v -E "$(IFS="|"; echo "${workflows[*]}")")

if [ -n "$additional_files" ]; then
    echo -e "${YELLOW}Found additional workflow files:${NC}"
    echo "$additional_files"
    echo -e "${YELLOW}To import these, add them to the workflows array in this script.${NC}"
else
    echo -e "${GREEN}✅ All workflow files have been processed.${NC}"
fi

# Setup verification
echo -e "\n${BLUE}🔧 Setup Verification:${NC}"

# Check if workflows are active
echo -e "${YELLOW}📊 Checking workflow status...${NC}"
if [ -n "$N8N_AUTH_TOKEN" ]; then
    workflow_list=$(curl -s "$N8N_API_URL/workflows" -H "Authorization: Bearer $N8N_AUTH_TOKEN")
else
    workflow_list=$(curl -s "$N8N_API_URL/workflows")
fi

if echo "$workflow_list" | grep -q '"data"'; then
    active_count=$(echo "$workflow_list" | grep -o '"active":true' | wc -l)
    total_count=$(echo "$workflow_list" | grep -o '"id":' | wc -l)
    echo -e "${GREEN}📈 Total workflows: $total_count${NC}"
    echo -e "${GREEN}🟢 Active workflows: $active_count${NC}"
else
    echo -e "${RED}❌ Could not retrieve workflow status${NC}"
fi

# Environment setup reminders
echo -e "\n${BLUE}⚙️ Environment Setup Reminders:${NC}"
echo -e "${YELLOW}1. Configure API keys in n8n credentials:${NC}"
echo "   - OPENAI_API_KEY (for AI agents)"
echo "   - ATTIO_API_KEY (for CRM integration)"
echo "   - MAILGUN_API_KEY (for email campaigns)"
echo "   - LINKEDIN_ACCESS_TOKEN (for LinkedIn outreach)"
echo "   - TWITTER_BEARER_TOKEN (for Twitter posting)"

echo -e "\n${YELLOW}2. Set environment variables in n8n:${NC}"
echo "   - AGENT_API_URL (http://localhost:8000)"
echo "   - N8N_WEBHOOK_URL (your n8n webhook URL)"
echo "   - CMS_API_URL (your website CMS API)"

echo -e "\n${YELLOW}3. Test webhook endpoints:${NC}"
echo "   - /webhook/sales-lead-intake"
echo "   - /webhook/customer-lifecycle-start"
echo "   - /webhook/linkedin-outreach-start"
echo "   - /webhook/cold-email-campaign"
echo "   - /webhook/content-lead-gen"
echo "   - /webhook/event-follow-up"

echo -e "\n${BLUE}🎯 Next Steps:${NC}"
echo "1. Activate important workflows in n8n interface"
echo "2. Configure webhook URLs in your forms/integrations"
echo "3. Test each workflow with sample data"
echo "4. Set up monitoring and alerts"
echo "5. Train team on workflow usage"

echo -e "\n${GREEN}🚀 Workflow import completed!${NC}"
echo -e "${GREEN}Access n8n at: $N8N_API_URL${NC}"

# Create import log
log_file="workflow_import_$(date +%Y%m%d_%H%M%S).log"
echo "Import Summary - $(date)" > "$log_file"
echo "Imported: $imported_count workflows" >> "$log_file"
echo "Failed: $failed_count workflows" >> "$log_file"
echo "Log saved to: $log_file"

exit 0