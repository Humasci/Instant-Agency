-- Instant Agency Database Schema
-- PostgreSQL 15+

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- LEADS & CONTACTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),

    -- Contact Information
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    company VARCHAR(255),
    title VARCHAR(100),

    -- Lead Details
    source VARCHAR(100),  -- website, referral, linkedin, etc.
    status VARCHAR(50) DEFAULT 'new',  -- new, contacted, qualified, converted, lost
    message TEXT,

    -- AI Scoring
    lead_score DECIMAL(3,2) DEFAULT 0.00,  -- 0.00 to 10.00
    qualification_data JSONB,  -- Store BANT scores and other data

    -- Tracking
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_contacted_at TIMESTAMP,

    -- CRM Sync
    crm_id VARCHAR(100),
    crm_synced_at TIMESTAMP,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    INDEX idx_email (email),
    INDEX idx_status (status),
    INDEX idx_lead_score (lead_score DESC),
    INDEX idx_created_at (created_at DESC)
);

-- ============================================================================
-- AGENT INTERACTIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS agent_interactions (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),

    -- Agent Info
    agent_name VARCHAR(100) NOT NULL,
    agent_version VARCHAR(20),

    -- Interaction Data
    input_data JSONB NOT NULL,
    output_data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Performance
    response_time_ms INTEGER,
    tokens_used INTEGER,

    -- Status
    status VARCHAR(50) DEFAULT 'success',  -- success, error, timeout
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_agent_name (agent_name),
    INDEX idx_created_at (created_at DESC),
    INDEX idx_status (status)
);

-- ============================================================================
-- AGENT METRICS
-- ============================================================================

CREATE TABLE IF NOT EXISTS agent_metrics (
    id SERIAL PRIMARY KEY,

    -- Agent Info
    agent_name VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,

    -- Metric Value
    value DECIMAL(10,4),
    unit VARCHAR(50),

    -- Context
    context JSONB DEFAULT '{}'::jsonb,

    -- Timestamp
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_agent_metric (agent_name, metric_name),
    INDEX idx_timestamp (timestamp DESC)
);

-- ============================================================================
-- WORKFLOWS
-- ============================================================================

CREATE TABLE IF NOT EXISTS workflow_executions (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),

    -- Workflow Info
    workflow_id VARCHAR(100) NOT NULL,
    workflow_name VARCHAR(255),

    -- Execution
    status VARCHAR(50) DEFAULT 'running',  -- running, completed, failed
    trigger_type VARCHAR(100),  -- webhook, schedule, manual

    -- Data
    input_data JSONB,
    output_data JSONB,
    error_data JSONB,

    -- Performance
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER,

    INDEX idx_workflow_id (workflow_id),
    INDEX idx_status (status),
    INDEX idx_started_at (started_at DESC)
);

-- ============================================================================
-- CAMPAIGNS
-- ============================================================================

CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),

    -- Campaign Info
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),  -- email, linkedin, content, etc.
    status VARCHAR(50) DEFAULT 'draft',  -- draft, active, paused, completed

    -- Targeting
    target_audience JSONB,

    -- Content
    content JSONB,  -- Templates, messages, etc.

    -- Performance
    sent_count INTEGER DEFAULT 0,
    opened_count INTEGER DEFAULT 0,
    clicked_count INTEGER DEFAULT 0,
    converted_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    INDEX idx_status (status),
    INDEX idx_type (type)
);

-- ============================================================================
-- CONTENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS content_items (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),

    -- Content Info
    title VARCHAR(500) NOT NULL,
    type VARCHAR(50),  -- blog_post, social_post, email, case_study
    status VARCHAR(50) DEFAULT 'draft',  -- draft, review, approved, published

    -- Content
    content TEXT,
    summary TEXT,

    -- SEO
    seo_title VARCHAR(255),
    seo_description VARCHAR(500),
    keywords TEXT[],

    -- Quality Scores
    readability_score DECIMAL(5,2),
    seo_score DECIMAL(5,2),
    ai_score DECIMAL(5,2),

    -- Publishing
    published_at TIMESTAMP,
    published_url VARCHAR(500),

    -- AI Generation
    generated_by_agent VARCHAR(100),
    generation_prompt TEXT,

    -- Approval
    requires_approval BOOLEAN DEFAULT true,
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,

    -- Performance
    views INTEGER DEFAULT 0,
    engagement_score DECIMAL(5,2),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_type (type),
    INDEX idx_status (status),
    INDEX idx_published_at (published_at DESC)
);

-- ============================================================================
-- SUPPORT TICKETS
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_tickets (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),

    -- Ticket Info
    subject VARCHAR(500) NOT NULL,
    description TEXT,
    priority VARCHAR(50) DEFAULT 'medium',  -- low, medium, high, urgent
    status VARCHAR(50) DEFAULT 'new',  -- new, assigned, in_progress, resolved, closed
    category VARCHAR(100),

    -- Customer
    customer_email VARCHAR(255),
    customer_name VARCHAR(255),

    -- Assignment
    assigned_to VARCHAR(100),
    assigned_at TIMESTAMP,

    -- AI Handling
    ai_handled BOOLEAN DEFAULT false,
    ai_confidence DECIMAL(3,2),
    requires_human BOOLEAN DEFAULT false,
    escalated_at TIMESTAMP,

    -- Resolution
    resolved_at TIMESTAMP,
    resolution TEXT,
    satisfaction_score INTEGER,  -- 1-5

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_customer_email (customer_email),
    INDEX idx_created_at (created_at DESC)
);

-- ============================================================================
-- ANALYTICS EVENTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics_events (
    id SERIAL PRIMARY KEY,

    -- Event Info
    event_name VARCHAR(100) NOT NULL,
    event_category VARCHAR(100),

    -- User/Session
    user_id VARCHAR(100),
    session_id VARCHAR(100),

    -- Event Data
    properties JSONB DEFAULT '{}'::jsonb,

    -- Context
    user_agent TEXT,
    ip_address INET,
    referrer TEXT,

    -- Timestamp
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_event_name (event_name),
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp DESC)
);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add update timestamp triggers
CREATE TRIGGER update_leads_timestamp
    BEFORE UPDATE ON leads
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_campaigns_timestamp
    BEFORE UPDATE ON campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_content_items_timestamp
    BEFORE UPDATE ON content_items
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_support_tickets_timestamp
    BEFORE UPDATE ON support_tickets
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Hot leads view
CREATE OR REPLACE VIEW hot_leads AS
SELECT
    id,
    first_name,
    last_name,
    email,
    company,
    lead_score,
    status,
    created_at
FROM leads
WHERE lead_score >= 7.0
    AND status IN ('new', 'contacted', 'qualified')
ORDER BY lead_score DESC, created_at DESC;

-- Agent performance view
CREATE OR REPLACE VIEW agent_performance AS
SELECT
    agent_name,
    DATE(created_at) as date,
    COUNT(*) as total_interactions,
    COUNT(*) FILTER (WHERE status = 'success') as successful,
    COUNT(*) FILTER (WHERE status = 'error') as errors,
    AVG(response_time_ms) as avg_response_time,
    SUM(tokens_used) as total_tokens
FROM agent_interactions
GROUP BY agent_name, DATE(created_at)
ORDER BY date DESC, agent_name;

-- Campaign performance view
CREATE OR REPLACE VIEW campaign_performance AS
SELECT
    id,
    name,
    type,
    status,
    sent_count,
    CASE WHEN sent_count > 0
        THEN ROUND((opened_count::DECIMAL / sent_count * 100), 2)
        ELSE 0
    END as open_rate,
    CASE WHEN sent_count > 0
        THEN ROUND((clicked_count::DECIMAL / sent_count * 100), 2)
        ELSE 0
    END as click_rate,
    CASE WHEN sent_count > 0
        THEN ROUND((converted_count::DECIMAL / sent_count * 100), 2)
        ELSE 0
    END as conversion_rate,
    created_at
FROM campaigns
ORDER BY created_at DESC;

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================

-- Insert sample lead
INSERT INTO leads (first_name, last_name, email, company, source, lead_score, status)
VALUES
    ('John', 'Doe', 'john.doe@example.com', 'Acme Corp', 'website', 8.5, 'new'),
    ('Jane', 'Smith', 'jane.smith@techco.com', 'TechCo', 'linkedin', 7.2, 'contacted')
ON CONFLICT (email) DO NOTHING;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO instant_agency;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO instant_agency;
