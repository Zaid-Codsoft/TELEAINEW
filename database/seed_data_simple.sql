-- Simplified Seed Data for TELEE Database
-- Uses database-generated UUIDs

-- Clean up existing data (if any)
TRUNCATE TABLE system_log, webhook_event, crm_log, analytics_event, 
               interaction_instance, workflow_action_log, workflow, 
               knowledge_base, escalate, transcription, dialogue, 
               auto_session, agent, crm_entity, agent_permission_map, 
               permission, admin, "user" CASCADE;

-- ============================================================================
-- ADMIN USERS
-- ============================================================================

INSERT INTO admin (name, email, password_hash, role, created_at, last_login) VALUES
('Super Admin', 'admin@teleai.com', '$2b$10$rU8vZ8K5xQxQxQxQxQxQxOYxQxQxQxQxQxQxQxQxQxQxQxQxQx', 'super_admin', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('John Manager', 'john.manager@teleai.com', '$2b$10$rU8vZ8K5xQxQxQxQxQxQxOYxQxQxQxQxQxQxQxQxQxQxQxQxQx', 'manager', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Sarah Support', 'sarah.support@teleai.com', '$2b$10$rU8vZ8K5xQxQxQxQxQxQxOYxQxQxQxQxQxQxQxQxQxQxQxQxQx', 'support', CURRENT_TIMESTAMP, NULL);

-- ============================================================================
-- PERMISSIONS
-- ============================================================================

INSERT INTO permission (name, description) VALUES
('view_analytics', 'Can view analytics dashboards'),
('manage_agents', 'Can create and manage AI agents'),
('manage_users', 'Can manage user accounts'),
('manage_knowledge_base', 'Can edit knowledge base'),
('manage_workflows', 'Can create and manage workflows'),
('view_logs', 'Can view system logs'),
('manage_escalations', 'Can handle escalated issues');

-- ============================================================================
-- END USERS
-- ============================================================================

INSERT INTO "user" (name, email, phone, role, status, date_joined, last_login) VALUES
('Alice Johnson', 'alice.johnson@example.com', '+1-555-0101', 'user', 'active', CURRENT_TIMESTAMP - INTERVAL '30 days', CURRENT_TIMESTAMP - INTERVAL '1 day'),
('Bob Smith', 'bob.smith@example.com', '+1-555-0102', 'user', 'active', CURRENT_TIMESTAMP - INTERVAL '25 days', CURRENT_TIMESTAMP - INTERVAL '2 days'),
('Carol White', 'carol.white@example.com', '+1-555-0103', 'premium', 'active', CURRENT_TIMESTAMP - INTERVAL '20 days', CURRENT_TIMESTAMP),
('David Brown', 'david.brown@example.com', '+1-555-0104', 'user', 'active', CURRENT_TIMESTAMP - INTERVAL '15 days', CURRENT_TIMESTAMP - INTERVAL '5 days'),
('Eva Green', 'eva.green@example.com', '+1-555-0105', 'user', 'inactive', CURRENT_TIMESTAMP - INTERVAL '60 days', CURRENT_TIMESTAMP - INTERVAL '45 days');

-- ============================================================================
-- CRM ENTITIES
-- ============================================================================

INSERT INTO crm_entity (crm_name, industry, rating_score, safety_type, status, created_at) VALUES
('TechCorp Inc.', 'Technology', 4.5, 'high', 'active', CURRENT_TIMESTAMP - INTERVAL '90 days'),
('HealthPlus LLC', 'Healthcare', 4.8, 'high', 'active', CURRENT_TIMESTAMP - INTERVAL '80 days'),
('FinanceFirst', 'Finance', 4.2, 'medium', 'active', CURRENT_TIMESTAMP - INTERVAL '70 days'),
('EduLearn Platform', 'Education', 4.6, 'high', 'active', CURRENT_TIMESTAMP - INTERVAL '60 days'),
('RetailMax', 'Retail', 3.9, 'medium', 'active', CURRENT_TIMESTAMP - INTERVAL '50 days');

-- ============================================================================
-- AI AGENTS  
-- ============================================================================

INSERT INTO agent (name, status, channel_type, started_at, summary) VALUES
('Customer Support Bot', 'active', 'voice', CURRENT_TIMESTAMP - INTERVAL '30 days', 'General customer support agent'),
('Sales Assistant', 'active', 'chat', CURRENT_TIMESTAMP - INTERVAL '25 days', 'Sales and product inquiry agent'),
('Technical Support', 'active', 'voice', CURRENT_TIMESTAMP - INTERVAL '20 days', 'Technical troubleshooting agent'),
('Billing Assistant', 'active', 'chat', CURRENT_TIMESTAMP - INTERVAL '15 days', 'Billing and payment queries agent');

-- ============================================================================
-- KNOWLEDGE BASE
-- ============================================================================

INSERT INTO knowledge_base (category, title, content, created_at, updated_at, tags, active) VALUES
('Product', 'Getting Started Guide', 'This comprehensive guide helps new users get started with our platform...', CURRENT_TIMESTAMP - INTERVAL '60 days', CURRENT_TIMESTAMP - INTERVAL '10 days', ARRAY['onboarding', 'tutorial', 'basics'], TRUE),
('Billing', 'Payment Methods', 'We accept various payment methods including credit cards, PayPal, and bank transfers...', CURRENT_TIMESTAMP - INTERVAL '55 days', CURRENT_TIMESTAMP - INTERVAL '15 days', ARRAY['billing', 'payment', 'finance'], TRUE),
('Technical', 'API Documentation', 'Our API allows you to integrate with your existing systems. Here are the endpoints...', CURRENT_TIMESTAMP - INTERVAL '50 days', CURRENT_TIMESTAMP - INTERVAL '5 days', ARRAY['api', 'integration', 'developer'], TRUE),
('Support', 'Troubleshooting Common Issues', 'This article covers the most common issues users face and how to resolve them...', CURRENT_TIMESTAMP - INTERVAL '45 days', CURRENT_TIMESTAMP - INTERVAL '3 days', ARRAY['support', 'troubleshooting', 'faq'], TRUE);

-- ============================================================================
-- WORKFLOWS
-- ============================================================================

INSERT INTO workflow (name, trigger_type, actions_json, created_at, status) VALUES
('New User Welcome', 'user_registered', '{"actions": [{"type": "send_email", "template": "welcome"}, {"type": "assign_agent"}]}'::jsonb, CURRENT_TIMESTAMP - INTERVAL '40 days', 'active'),
('Escalation Notification', 'issue_escalated', '{"actions": [{"type": "notify_admin", "priority": "high"}, {"type": "create_ticket"}]}'::jsonb, CURRENT_TIMESTAMP - INTERVAL '35 days', 'active'),
('Idle Session Cleanup', 'session_idle', '{"actions": [{"type": "end_session"}, {"type": "send_feedback_request"}]}'::jsonb, CURRENT_TIMESTAMP - INTERVAL '30 days', 'active');

-- ============================================================================
-- SYSTEM LOGS
-- ============================================================================

INSERT INTO system_log (log_type, log_message, log_time, source) VALUES
('INFO', 'Database initialization completed successfully', CURRENT_TIMESTAMP - INTERVAL '90 days', 'database'),
('INFO', 'New agent deployed: Customer Support Bot', CURRENT_TIMESTAMP - INTERVAL '30 days', 'agent_manager'),
('WARNING', 'High session volume detected', CURRENT_TIMESTAMP - INTERVAL '5 hours', 'monitoring'),
('INFO', 'Scheduled maintenance completed', CURRENT_TIMESTAMP - INTERVAL '1 day', 'system'),
('ERROR', 'Failed webhook delivery attempt (retry scheduled)', CURRENT_TIMESTAMP - INTERVAL '3 hours', 'webhook_service');

-- ============================================================================
-- VERIFICATION
-- ============================================================================

SELECT 'Seed data inserted successfully!' AS status,
       (SELECT COUNT(*) FROM "user") AS total_users,
       (SELECT COUNT(*) FROM admin) AS total_admins,
       (SELECT COUNT(*) FROM agent) AS total_agents,
       (SELECT COUNT(*) FROM knowledge_base) AS total_kb_articles,
       (SELECT COUNT(*) FROM workflow) AS total_workflows;

