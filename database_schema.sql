-- SIX3 Agency Expert Agents Database Schema
-- Tracks all agent work products, interactions, and client data

-- Client information and project tracking
CREATE TABLE IF NOT EXISTS clients (
    client_id VARCHAR(50) PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100),
    company_size VARCHAR(50),
    primary_contact VARCHAR(200),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    timezone VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    relationship_stage VARCHAR(50) DEFAULT 'prospect',
    communication_preferences JSONB,
    metadata JSONB
);

-- Projects for each client
CREATE TABLE IF NOT EXISTS projects (
    project_id VARCHAR(50) PRIMARY KEY,
    client_id VARCHAR(50) REFERENCES clients(client_id),
    project_name VARCHAR(200) NOT NULL,
    service_types TEXT[], -- Array of services (search_marketing, ai_media, ml_ai)
    project_manager VARCHAR(100),
    team_members TEXT[],
    start_date DATE,
    target_completion DATE,
    actual_completion DATE,
    budget DECIMAL(12,2),
    priority VARCHAR(20) DEFAULT 'normal',
    status VARCHAR(20) DEFAULT 'planning', -- planning, active, on_hold, at_risk, completed, cancelled
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    project_metadata JSONB
);

-- Agent work products storage tracking
CREATE TABLE IF NOT EXISTS agent_work_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id VARCHAR(50) REFERENCES clients(client_id),
    project_id VARCHAR(50) REFERENCES projects(project_id),
    agent_type VARCHAR(50) NOT NULL, -- search_marketing_expert, ai_media_expert, etc.
    work_product_type VARCHAR(100) NOT NULL, -- market_analysis, campaign_strategy, etc.
    file_path TEXT NOT NULL,
    file_size_bytes INTEGER,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active', -- active, archived, deleted
    version INTEGER DEFAULT 1,
    is_latest BOOLEAN DEFAULT TRUE,
    content_hash VARCHAR(64), -- For integrity checking
    metadata JSONB,
    INDEX idx_client_agent (client_id, agent_type),
    INDEX idx_project_agent (project_id, agent_type),
    INDEX idx_work_product_type (work_product_type),
    INDEX idx_created_date (created_date)
);

-- Agent interactions log (every agent call)
CREATE TABLE IF NOT EXISTS agent_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id VARCHAR(50) REFERENCES clients(client_id),
    project_id VARCHAR(50) REFERENCES projects(project_id),
    agent_name VARCHAR(50) NOT NULL,
    agent_action VARCHAR(100) NOT NULL,
    interaction_type VARCHAR(50), -- consultation, analysis, planning, delivery
    input_data JSONB,
    output_data JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    user_id VARCHAR(50), -- Who initiated the interaction
    session_id VARCHAR(100),
    ip_address INET,
    INDEX idx_client_timestamp (client_id, timestamp),
    INDEX idx_agent_timestamp (agent_name, timestamp),
    INDEX idx_success_timestamp (success, timestamp)
);

-- Client meetings and communications
CREATE TABLE IF NOT EXISTS client_meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id VARCHAR(50) REFERENCES clients(client_id),
    project_id VARCHAR(50) REFERENCES projects(project_id),
    meeting_type VARCHAR(50) NOT NULL, -- initial_consultation, strategy_presentation, etc.
    meeting_title VARCHAR(200),
    scheduled_date TIMESTAMP,
    actual_date TIMESTAMP,
    duration_minutes INTEGER,
    attendees JSONB, -- Array of attendee objects
    agenda JSONB,
    meeting_notes TEXT,
    action_items JSONB,
    outcomes JSONB,
    satisfaction_score INTEGER CHECK (satisfaction_score >= 1 AND satisfaction_score <= 5),
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    created_by VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    meeting_metadata JSONB,
    INDEX idx_client_scheduled (client_id, scheduled_date),
    INDEX idx_meeting_type (meeting_type),
    INDEX idx_follow_up (follow_up_required, follow_up_date)
);

-- Service delivery tracking
CREATE TABLE IF NOT EXISTS service_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id VARCHAR(50) REFERENCES clients(client_id),
    project_id VARCHAR(50) REFERENCES projects(project_id),
    service_type VARCHAR(50) NOT NULL,
    deliverable_name VARCHAR(200),
    deliverable_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'not_started', -- not_started, in_progress, review, completed, delivered
    assigned_expert VARCHAR(50),
    estimated_hours DECIMAL(6,2),
    actual_hours DECIMAL(6,2),
    start_date DATE,
    due_date DATE,
    completion_date DATE,
    delivery_date DATE,
    quality_score INTEGER CHECK (quality_score >= 1 AND quality_score <= 10),
    client_approval_status VARCHAR(20) DEFAULT 'pending', -- pending, approved, revision_required
    client_feedback TEXT,
    deliverable_files JSONB, -- Array of file paths
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_metadata JSONB,
    INDEX idx_client_service (client_id, service_type),
    INDEX idx_status_due_date (status, due_date),
    INDEX idx_assigned_expert (assigned_expert)
);

-- Performance metrics and KPIs
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id VARCHAR(50) REFERENCES clients(client_id),
    project_id VARCHAR(50) REFERENCES projects(project_id),
    service_type VARCHAR(50),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4),
    metric_unit VARCHAR(20),
    measurement_date DATE NOT NULL,
    reporting_period VARCHAR(20), -- daily, weekly, monthly, quarterly
    baseline_value DECIMAL(15,4),
    target_value DECIMAL(15,4),
    variance_percentage DECIMAL(8,4),
    trend_direction VARCHAR(10), -- increasing, decreasing, stable
    data_source VARCHAR(100),
    calculated_by VARCHAR(50), -- which agent calculated this
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metric_metadata JSONB,
    INDEX idx_client_metric_date (client_id, metric_name, measurement_date),
    INDEX idx_service_metric (service_type, metric_name),
    INDEX idx_measurement_date (measurement_date)
);

-- Agent expertise and capabilities tracking
CREATE TABLE IF NOT EXISTS agent_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(50) NOT NULL,
    agent_type VARCHAR(50),
    capability_area VARCHAR(100),
    expertise_level VARCHAR(20), -- beginner, intermediate, advanced, expert
    industry_specialization VARCHAR(100),
    platform_expertise VARCHAR(100),
    certification_level VARCHAR(50),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    performance_rating DECIMAL(3,2) CHECK (performance_rating >= 0 AND performance_rating <= 5),
    success_rate_percentage DECIMAL(5,2),
    total_projects_completed INTEGER DEFAULT 0,
    average_client_satisfaction DECIMAL(3,2),
    capabilities_metadata JSONB,
    UNIQUE(agent_name, capability_area, industry_specialization)
);

-- Research and insights storage
CREATE TABLE IF NOT EXISTS research_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id VARCHAR(50) REFERENCES clients(client_id),
    project_id VARCHAR(50) REFERENCES projects(project_id),
    research_type VARCHAR(50) NOT NULL, -- market_analysis, competitive_intelligence, customer_insights, trend_analysis
    insight_category VARCHAR(100),
    insight_title VARCHAR(200),
    insight_description TEXT,
    confidence_level VARCHAR(20), -- low, medium, high, very_high
    strategic_importance VARCHAR(20), -- low, medium, high, critical
    data_sources JSONB,
    supporting_evidence TEXT,
    actionable_recommendations JSONB,
    impact_assessment TEXT,
    created_by VARCHAR(50), -- research_analyst
    validated_by VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_date DATE, -- When insight becomes stale
    research_metadata JSONB,
    INDEX idx_client_research (client_id, research_type),
    INDEX idx_insight_category (insight_category),
    INDEX idx_strategic_importance (strategic_importance)
);

-- Workflow and process tracking (n8n integration)
CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id VARCHAR(50) REFERENCES clients(client_id),
    project_id VARCHAR(50) REFERENCES projects(project_id),
    workflow_name VARCHAR(100) NOT NULL,
    workflow_id VARCHAR(100), -- n8n workflow ID
    execution_id VARCHAR(100), -- n8n execution ID
    trigger_type VARCHAR(50), -- webhook, schedule, manual
    triggered_by VARCHAR(50),
    status VARCHAR(20) DEFAULT 'running', -- running, completed, failed, cancelled
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    duration_ms INTEGER,
    input_data JSONB,
    output_data JSONB,
    error_details TEXT,
    nodes_executed INTEGER,
    success_rate DECIMAL(5,2),
    workflow_metadata JSONB,
    INDEX idx_client_workflow (client_id, workflow_name),
    INDEX idx_status_start_time (status, start_time),
    INDEX idx_workflow_name (workflow_name)
);

-- Audit log for compliance and security
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(50),
    session_id VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    security_level VARCHAR(20) DEFAULT 'normal', -- normal, sensitive, critical
    compliance_relevant BOOLEAN DEFAULT FALSE,
    retention_years INTEGER DEFAULT 7,
    INDEX idx_timestamp (timestamp),
    INDEX idx_user_action (user_id, action),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_compliance (compliance_relevant, timestamp)
);

-- Views for common queries
CREATE VIEW agent_work_summary AS
SELECT 
    awp.client_id,
    awp.project_id,
    awp.agent_type,
    COUNT(*) as total_work_products,
    COUNT(CASE WHEN awp.status = 'active' THEN 1 END) as active_products,
    MAX(awp.last_modified) as last_activity,
    SUM(awp.file_size_bytes) as total_storage_bytes
FROM agent_work_products awp
GROUP BY awp.client_id, awp.project_id, awp.agent_type;

CREATE VIEW client_project_status AS
SELECT 
    c.client_id,
    c.company_name,
    p.project_id,
    p.project_name,
    p.status as project_status,
    p.service_types,
    COUNT(sd.id) as total_deliverables,
    COUNT(CASE WHEN sd.status = 'completed' THEN 1 END) as completed_deliverables,
    AVG(sd.quality_score) as avg_quality_score,
    MAX(cm.scheduled_date) as last_meeting_date
FROM clients c
LEFT JOIN projects p ON c.client_id = p.client_id
LEFT JOIN service_deliveries sd ON p.project_id = sd.project_id
LEFT JOIN client_meetings cm ON c.client_id = cm.client_id
GROUP BY c.client_id, c.company_name, p.project_id, p.project_name, p.status, p.service_types;

CREATE VIEW agent_performance_metrics AS
SELECT 
    ai.agent_name,
    DATE(ai.timestamp) as activity_date,
    COUNT(*) as total_interactions,
    COUNT(CASE WHEN ai.success THEN 1 END) as successful_interactions,
    ROUND(COUNT(CASE WHEN ai.success THEN 1 END) * 100.0 / COUNT(*), 2) as success_rate,
    AVG(ai.processing_time_ms) as avg_processing_time_ms,
    COUNT(DISTINCT ai.client_id) as unique_clients_served
FROM agent_interactions ai
GROUP BY ai.agent_name, DATE(ai.timestamp);

-- Indexes for optimal performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agent_work_products_composite 
ON agent_work_products(client_id, agent_type, created_date DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agent_interactions_composite 
ON agent_interactions(client_id, agent_name, timestamp DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_composite 
ON performance_metrics(client_id, service_type, measurement_date DESC);

-- Functions for data management
CREATE OR REPLACE FUNCTION update_last_modified_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_clients_timestamp 
    BEFORE UPDATE ON clients 
    FOR EACH ROW EXECUTE FUNCTION update_last_modified_timestamp();

CREATE TRIGGER update_projects_timestamp 
    BEFORE UPDATE ON projects 
    FOR EACH ROW EXECUTE FUNCTION update_last_modified_timestamp();

CREATE TRIGGER update_agent_work_products_timestamp 
    BEFORE UPDATE ON agent_work_products 
    FOR EACH ROW EXECUTE FUNCTION update_last_modified_timestamp();

-- Data retention function for compliance
CREATE OR REPLACE FUNCTION cleanup_old_audit_records()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM audit_log 
    WHERE timestamp < CURRENT_DATE - INTERVAL '7 years'
    AND retention_years <= 7;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;