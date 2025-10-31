-- Tele-AI PostgreSQL Database Schema
-- Based on provided ERD
-- Created: 2024

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables (for clean setup)
DROP TABLE IF EXISTS agent_permission_map CASCADE;
DROP TABLE IF EXISTS transcription CASCADE;
DROP TABLE IF EXISTS escalate CASCADE;
DROP TABLE IF EXISTS analytics_event CASCADE;
DROP TABLE IF EXISTS interaction_instance CASCADE;
DROP TABLE IF EXISTS webhook_event CASCADE;
DROP TABLE IF EXISTS crm_log CASCADE;
DROP TABLE IF EXISTS system_log CASCADE;
DROP TABLE IF EXISTS workflow_action_log CASCADE;
DROP TABLE IF EXISTS workflow CASCADE;
DROP TABLE IF EXISTS knowledge_base CASCADE;
DROP TABLE IF EXISTS auto_session CASCADE;
DROP TABLE IF EXISTS dialogue CASCADE;
DROP TABLE IF EXISTS agent CASCADE;
DROP TABLE IF EXISTS permission CASCADE;
DROP TABLE IF EXISTS crm_entity CASCADE;
DROP TABLE IF EXISTS admin CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- USER Table
CREATE TABLE "user" (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(50) DEFAULT 'user',
    status VARCHAR(50) DEFAULT 'active',
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_user_email ON "user"(email);
CREATE INDEX idx_user_status ON "user"(status);

-- ADMIN Table
CREATE TABLE admin (
    admin_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_admin_email ON admin(email);

-- PERMISSION Table
CREATE TABLE permission (
    permission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- AGENT_PERMISSION_MAP Table (Junction table)
CREATE TABLE agent_permission_map (
    admin_id UUID NOT NULL,
    permission_id UUID NOT NULL,
    PRIMARY KEY (admin_id, permission_id),
    FOREIGN KEY (admin_id) REFERENCES admin(admin_id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permission(permission_id) ON DELETE CASCADE
);

-- ============================================================================
-- CRM & ENTITY TABLES
-- ============================================================================

-- CRM_ENTITY Table
CREATE TABLE crm_entity (
    crm_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crm_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    rating_score FLOAT,
    safety_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_crm_name ON crm_entity(crm_name);

-- ============================================================================
-- AGENT & SESSION TABLES
-- ============================================================================

-- AGENT Table
CREATE TABLE agent (
    agent_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    admin_id UUID,
    assigned_agent UUID,
    status VARCHAR(50) DEFAULT 'active',
    channel_type VARCHAR(50),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    summary TEXT,
    escalated BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (admin_id) REFERENCES admin(admin_id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_agent) REFERENCES agent(agent_id) ON DELETE SET NULL
);

CREATE INDEX idx_agent_status ON agent(status);
CREATE INDEX idx_agent_admin ON agent(admin_id);

-- AUTO_SESSION Table
CREATE TABLE auto_session (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    crm_id UUID,
    admin_id UUID,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    session_type VARCHAR(50),
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON DELETE SET NULL,
    FOREIGN KEY (crm_id) REFERENCES crm_entity(crm_id) ON DELETE SET NULL,
    FOREIGN KEY (admin_id) REFERENCES admin(admin_id) ON DELETE SET NULL
);

CREATE INDEX idx_session_user ON auto_session(user_id);
CREATE INDEX idx_session_crm ON auto_session(crm_id);
CREATE INDEX idx_session_started ON auto_session(started_at);

-- DIALOGUE Table
CREATE TABLE dialogue (
    dialogue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    crm_id UUID,
    session_id UUID,
    assigned_agent UUID,
    status VARCHAR(50) DEFAULT 'active',
    channel_type VARCHAR(50),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    summary TEXT,
    escalated BOOLEAN DEFAULT FALSE,
    text TEXT,
    FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON DELETE SET NULL,
    FOREIGN KEY (crm_id) REFERENCES crm_entity(crm_id) ON DELETE SET NULL,
    FOREIGN KEY (session_id) REFERENCES auto_session(session_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_agent) REFERENCES agent(agent_id) ON DELETE SET NULL
);

CREATE INDEX idx_dialogue_user ON dialogue(user_id);
CREATE INDEX idx_dialogue_session ON dialogue(session_id);
CREATE INDEX idx_dialogue_started ON dialogue(started_at);

-- TRANSCRIPTION Table
CREATE TABLE transcription (
    transcription_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dialogue_id UUID,
    channel VARCHAR(50),
    text TEXT NOT NULL,
    speaker_label VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence FLOAT,
    FOREIGN KEY (dialogue_id) REFERENCES dialogue(dialogue_id) ON DELETE CASCADE
);

CREATE INDEX idx_transcription_dialogue ON transcription(dialogue_id);
CREATE INDEX idx_transcription_created ON transcription(created_at);

-- ============================================================================
-- ESCALATION TABLE
-- ============================================================================

-- ESCALATE Table
CREATE TABLE escalate (
    escalate_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crm_id UUID,
    user_id UUID,
    assigned_agent UUID,
    assigned_admin UUID,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    description TEXT,
    FOREIGN KEY (crm_id) REFERENCES crm_entity(crm_id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_agent) REFERENCES agent(agent_id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_admin) REFERENCES admin(admin_id) ON DELETE SET NULL
);

CREATE INDEX idx_escalate_status ON escalate(status);
CREATE INDEX idx_escalate_user ON escalate(user_id);

-- ============================================================================
-- KNOWLEDGE BASE & WORKFLOW TABLES
-- ============================================================================

-- KNOWLEDGE_BASE Table
CREATE TABLE knowledge_base (
    kb_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT[],
    active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (created_by) REFERENCES admin(admin_id) ON DELETE SET NULL
);

CREATE INDEX idx_kb_category ON knowledge_base(category);
CREATE INDEX idx_kb_created ON knowledge_base(created_at);
CREATE INDEX idx_kb_active ON knowledge_base(active);

-- WORKFLOW Table
CREATE TABLE workflow (
    workflow_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    trigger_type VARCHAR(100),
    actions_json JSONB,
    created_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    FOREIGN KEY (created_by) REFERENCES admin(admin_id) ON DELETE SET NULL
);

CREATE INDEX idx_workflow_trigger ON workflow(trigger_type);
CREATE INDEX idx_workflow_status ON workflow(status);

-- WORKFLOW_ACTION_LOG Table
CREATE TABLE workflow_action_log (
    action_log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wf_id UUID,
    action_type VARCHAR(100),
    status VARCHAR(50),
    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    result TEXT,
    FOREIGN KEY (wf_id) REFERENCES workflow(workflow_id) ON DELETE CASCADE
);

CREATE INDEX idx_workflow_log_wf ON workflow_action_log(wf_id);
CREATE INDEX idx_workflow_log_time ON workflow_action_log(action_time);

-- ============================================================================
-- INTERACTION & ANALYTICS TABLES
-- ============================================================================

-- INTERACTION_INSTANCE Table
CREATE TABLE interaction_instance (
    instance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    crm_id UUID,
    workflow_id UUID,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON DELETE SET NULL,
    FOREIGN KEY (crm_id) REFERENCES crm_entity(crm_id) ON DELETE SET NULL,
    FOREIGN KEY (workflow_id) REFERENCES workflow(workflow_id) ON DELETE SET NULL
);

CREATE INDEX idx_instance_user ON interaction_instance(user_id);
CREATE INDEX idx_instance_workflow ON interaction_instance(workflow_id);

-- ANALYTICS_EVENT Table
CREATE TABLE analytics_event (
    analytics_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crm_name VARCHAR(255),
    external_id VARCHAR(255),
    instance_user UUID,
    event_name VARCHAR(255) NOT NULL,
    context JSONB,
    status VARCHAR(50),
    event_type VARCHAR(100),
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instance_user) REFERENCES "user"(user_id) ON DELETE SET NULL
);

CREATE INDEX idx_analytics_event_name ON analytics_event(event_name);
CREATE INDEX idx_analytics_event_time ON analytics_event(event_time);
CREATE INDEX idx_analytics_event_type ON analytics_event(event_type);

-- ============================================================================
-- LOGGING TABLES
-- ============================================================================

-- CRM_LOG Table
CREATE TABLE crm_log (
    crm_log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crm_id UUID,
    user_id UUID,
    action VARCHAR(255),
    status VARCHAR(50),
    error_message TEXT,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (crm_id) REFERENCES crm_entity(crm_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON DELETE SET NULL
);

CREATE INDEX idx_crm_log_crm ON crm_log(crm_id);
CREATE INDEX idx_crm_log_time ON crm_log(log_time);

-- WEBHOOK_EVENT Table
CREATE TABLE webhook_event (
    webhook_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100),
    initiator VARCHAR(255),
    payload JSONB,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50),
    response_code INTEGER
);

CREATE INDEX idx_webhook_event_type ON webhook_event(event_type);
CREATE INDEX idx_webhook_received ON webhook_event(received_at);

-- SYSTEM_LOG Table
CREATE TABLE system_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    log_type VARCHAR(100),
    log_message TEXT,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(255)
);

CREATE INDEX idx_system_log_type ON system_log(log_type);
CREATE INDEX idx_system_log_time ON system_log(log_time);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE "user" IS 'End users of the Tele-AI system';
COMMENT ON TABLE admin IS 'Administrative users with elevated privileges';
COMMENT ON TABLE agent IS 'AI agents configuration and status';
COMMENT ON TABLE dialogue IS 'Conversation sessions between users and agents';
COMMENT ON TABLE auto_session IS 'Automated session tracking';
COMMENT ON TABLE knowledge_base IS 'Knowledge base articles for AI training';
COMMENT ON TABLE workflow IS 'Automated workflow definitions';
COMMENT ON TABLE crm_entity IS 'CRM entities and integrations';
COMMENT ON TABLE transcription IS 'Voice conversation transcriptions';
COMMENT ON TABLE escalate IS 'Escalated issues requiring human intervention';
COMMENT ON TABLE analytics_event IS 'Analytics and tracking events';
COMMENT ON TABLE webhook_event IS 'Webhook event logs';
COMMENT ON TABLE system_log IS 'System-wide logging';

-- ============================================================================
-- INITIAL SETUP COMPLETE
-- ============================================================================

-- Create default admin user (password: admin123 - CHANGE IN PRODUCTION!)
-- Password hash for 'admin123' using bcrypt
-- In production, generate proper hash using bcrypt

COMMENT ON DATABASE teleai_db IS 'Tele-AI Voice AI System Database - Comprehensive schema based on ERD';

