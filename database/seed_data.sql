-- Tele-AI Database - Seed Data (Dummy Data for Testing)
-- This file populates the database with initial dummy data

-- ============================================================================
-- ADMIN USERS
-- ============================================================================

INSERT INTO admin (admin_id, name, email, password_hash, role, created_at, last_login) VALUES
('11111111-1111-1111-1111-111111111111', 'Super Admin', 'admin@teleai.com', '$2b$10$rU8vZ8K5xQxQxQxQxQxQxOYxQxQxQxQxQxQxQxQxQxQxQxQxQx', 'super_admin', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('22222222-2222-2222-2222-222222222222', 'John Manager', 'john.manager@teleai.com', '$2b$10$rU8vZ8K5xQxQxQxQxQxQxOYxQxQxQxQxQxQxQxQxQxQxQxQxQx', 'manager', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('33333333-3333-3333-3333-333333333333', 'Sarah Support', 'sarah.support@teleai.com', '$2b$10$rU8vZ8K5xQxQxQxQxQxQxOYxQxQxQxQxQxQxQxQxQxQxQxQxQx', 'support', CURRENT_TIMESTAMP, NULL);

-- ============================================================================
-- PERMISSIONS
-- ============================================================================

INSERT INTO permission (permission_id, name, description) VALUES
('a1111111-1111-1111-1111-111111111111', 'view_analytics', 'Can view analytics dashboards'),
('a2222222-2222-2222-2222-222222222222', 'manage_agents', 'Can create and manage AI agents'),
('a3333333-3333-3333-3333-333333333333', 'manage_users', 'Can manage user accounts'),
('a4444444-4444-4444-4444-444444444444', 'manage_knowledge_base', 'Can edit knowledge base'),
('a5555555-5555-5555-5555-555555555555', 'manage_workflows', 'Can create and manage workflows'),
('a6666666-6666-6666-6666-666666666666', 'view_logs', 'Can view system logs'),
('a7777777-7777-7777-7777-777777777777', 'manage_escalations', 'Can handle escalated issues');

-- ============================================================================
-- AGENT-PERMISSION MAPPINGS
-- ============================================================================

-- Super Admin gets all permissions
INSERT INTO agent_permission_map (admin_id, permission_id) VALUES
('11111111-1111-1111-1111-111111111111', 'a1111111-1111-1111-1111-111111111111'),
('11111111-1111-1111-1111-111111111111', 'a2222222-2222-2222-2222-222222222222'),
('11111111-1111-1111-1111-111111111111', 'a3333333-3333-3333-3333-333333333333'),
('11111111-1111-1111-1111-111111111111', 'a4444444-4444-4444-4444-444444444444'),
('11111111-1111-1111-1111-111111111111', 'a5555555-5555-5555-5555-555555555555'),
('11111111-1111-1111-1111-111111111111', 'a6666666-6666-6666-6666-666666666666'),
('11111111-1111-1111-1111-111111111111', 'a7777777-7777-7777-7777-777777777777');

-- Manager gets selected permissions
INSERT INTO agent_permission_map (admin_id, permission_id) VALUES
('22222222-2222-2222-2222-222222222222', 'a1111111-1111-1111-1111-111111111111'),
('22222222-2222-2222-2222-222222222222', 'a2222222-2222-2222-2222-222222222222'),
('22222222-2222-2222-2222-222222222222', 'a6666666-6666-6666-6666-666666666666'),
('22222222-2222-2222-2222-222222222222', 'a7777777-7777-7777-7777-777777777777');

-- Support gets limited permissions
INSERT INTO agent_permission_map (admin_id, permission_id) VALUES
('33333333-3333-3333-3333-333333333333', 'a6666666-6666-6666-6666-666666666666'),
('33333333-3333-3333-3333-333333333333', 'a7777777-7777-7777-7777-777777777777');

-- ============================================================================
-- END USERS
-- ============================================================================

INSERT INTO "user" (user_id, name, email, phone, role, status, date_joined, last_login) VALUES
('u1111111-1111-1111-1111-111111111111', 'Alice Johnson', 'alice.johnson@example.com', '+1-555-0101', 'user', 'active', CURRENT_TIMESTAMP - INTERVAL '30 days', CURRENT_TIMESTAMP - INTERVAL '1 day'),
('u2222222-2222-2222-2222-222222222222', 'Bob Smith', 'bob.smith@example.com', '+1-555-0102', 'user', 'active', CURRENT_TIMESTAMP - INTERVAL '25 days', CURRENT_TIMESTAMP - INTERVAL '2 days'),
('u3333333-3333-3333-3333-333333333333', 'Carol White', 'carol.white@example.com', '+1-555-0103', 'premium', 'active', CURRENT_TIMESTAMP - INTERVAL '20 days', CURRENT_TIMESTAMP),
('u4444444-4444-4444-4444-444444444444', 'David Brown', 'david.brown@example.com', '+1-555-0104', 'user', 'active', CURRENT_TIMESTAMP - INTERVAL '15 days', CURRENT_TIMESTAMP - INTERVAL '5 days'),
('u5555555-5555-5555-5555-555555555555', 'Eva Green', 'eva.green@example.com', '+1-555-0105', 'user', 'inactive', CURRENT_TIMESTAMP - INTERVAL '60 days', CURRENT_TIMESTAMP - INTERVAL '45 days');

-- ============================================================================
-- CRM ENTITIES
-- ============================================================================

INSERT INTO crm_entity (crm_id, crm_name, industry, rating_score, safety_type, status, created_at) VALUES
('c1111111-1111-1111-1111-111111111111', 'TechCorp Inc.', 'Technology', 4.5, 'high', 'active', CURRENT_TIMESTAMP - INTERVAL '90 days'),
('c2222222-2222-2222-2222-222222222222', 'HealthPlus LLC', 'Healthcare', 4.8, 'high', 'active', CURRENT_TIMESTAMP - INTERVAL '80 days'),
('c3333333-3333-3333-3333-333333333333', 'FinanceFirst', 'Finance', 4.2, 'medium', 'active', CURRENT_TIMESTAMP - INTERVAL '70 days'),
('c4444444-4444-4444-4444-444444444444', 'EduLearn Platform', 'Education', 4.6, 'high', 'active', CURRENT_TIMESTAMP - INTERVAL '60 days'),
('c5555555-5555-5555-5555-555555555555', 'RetailMax', 'Retail', 3.9, 'medium', 'active', CURRENT_TIMESTAMP - INTERVAL '50 days');

-- ============================================================================
-- AI AGENTS
-- ============================================================================

INSERT INTO agent (agent_id, name, admin_id, status, channel_type, started_at, summary) VALUES
('ag111111-1111-1111-1111-111111111111', 'Customer Support Bot', '11111111-1111-1111-1111-111111111111', 'active', 'voice', CURRENT_TIMESTAMP - INTERVAL '30 days', 'General customer support agent'),
('ag222222-2222-2222-2222-222222222222', 'Sales Assistant', '22222222-2222-2222-2222-222222222222', 'active', 'chat', CURRENT_TIMESTAMP - INTERVAL '25 days', 'Sales and product inquiry agent'),
('ag333333-3333-3333-3333-333333333333', 'Technical Support', '11111111-1111-1111-1111-111111111111', 'active', 'voice', CURRENT_TIMESTAMP - INTERVAL '20 days', 'Technical troubleshooting agent'),
('ag444444-4444-4444-4444-444444444444', 'Billing Assistant', '22222222-2222-2222-2222-222222222222', 'active', 'chat', CURRENT_TIMESTAMP - INTERVAL '15 days', 'Billing and payment queries agent');

-- ============================================================================
-- AUTO SESSIONS
-- ============================================================================

INSERT INTO auto_session (session_id, user_id, crm_id, admin_id, started_at, ended_at, session_type, ip_address) VALUES
('s1111111-1111-1111-1111-111111111111', 'u1111111-1111-1111-1111-111111111111', 'c1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', CURRENT_TIMESTAMP - INTERVAL '5 hours', CURRENT_TIMESTAMP - INTERVAL '4 hours 45 minutes', 'voice_call', '192.168.1.100'),
('s2222222-2222-2222-2222-222222222222', 'u2222222-2222-2222-2222-222222222222', 'c2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', CURRENT_TIMESTAMP - INTERVAL '3 hours', CURRENT_TIMESTAMP - INTERVAL '2 hours 50 minutes', 'chat', '192.168.1.101'),
('s3333333-3333-3333-3333-333333333333', 'u3333333-3333-3333-3333-333333333333', 'c3333333-3333-3333-3333-333333333333', '11111111-1111-1111-1111-111111111111', CURRENT_TIMESTAMP - INTERVAL '2 hours', CURRENT_TIMESTAMP - INTERVAL '1 hour 40 minutes', 'voice_call', '192.168.1.102'),
('s4444444-4444-4444-4444-444444444444', 'u4444444-4444-4444-4444-444444444444', 'c4444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222222', CURRENT_TIMESTAMP - INTERVAL '1 hour', NULL, 'chat', '192.168.1.103');

-- ============================================================================
-- DIALOGUES
-- ============================================================================

INSERT INTO dialogue (dialogue_id, user_id, crm_id, session_id, assigned_agent, status, channel_type, started_at, ended_at, summary, escalated, text) VALUES
('d1111111-1111-1111-1111-111111111111', 'u1111111-1111-1111-1111-111111111111', 'c1111111-1111-1111-1111-111111111111', 's1111111-1111-1111-1111-111111111111', 'ag111111-1111-1111-1111-111111111111', 'completed', 'voice', CURRENT_TIMESTAMP - INTERVAL '5 hours', CURRENT_TIMESTAMP - INTERVAL '4 hours 45 minutes', 'Product inquiry resolved', FALSE, 'User asked about product features'),
('d2222222-2222-2222-2222-222222222222', 'u2222222-2222-2222-2222-222222222222', 'c2222222-2222-2222-2222-222222222222', 's2222222-2222-2222-2222-222222222222', 'ag222222-2222-2222-2222-222222222222', 'completed', 'chat', CURRENT_TIMESTAMP - INTERVAL '3 hours', CURRENT_TIMESTAMP - INTERVAL '2 hours 50 minutes', 'Billing question answered', FALSE, 'User had question about invoice'),
('d3333333-3333-3333-3333-333333333333', 'u3333333-3333-3333-3333-333333333333', 'c3333333-3333-3333-3333-333333333333', 's3333333-3333-3333-3333-333333333333', 'ag333333-3333-3333-3333-333333333333', 'escalated', 'voice', CURRENT_TIMESTAMP - INTERVAL '2 hours', CURRENT_TIMESTAMP - INTERVAL '1 hour 40 minutes', 'Technical issue - escalated to support', TRUE, 'Complex technical problem requiring human support'),
('d4444444-4444-4444-4444-444444444444', 'u4444444-4444-4444-4444-444444444444', 'c4444444-4444-4444-4444-444444444444', 's4444444-4444-4444-4444-444444444444', 'ag444444-4444-4444-4444-444444444444', 'active', 'chat', CURRENT_TIMESTAMP - INTERVAL '1 hour', NULL, NULL, FALSE, 'Ongoing conversation about billing');

-- ============================================================================
-- TRANSCRIPTIONS
-- ============================================================================

INSERT INTO transcription (transcription_id, dialogue_id, channel, text, speaker_label, created_at, confidence) VALUES
('t1111111-1111-1111-1111-111111111111', 'd1111111-1111-1111-1111-111111111111', 'voice', 'Hello, I would like to know more about your premium features.', 'user', CURRENT_TIMESTAMP - INTERVAL '5 hours', 0.95),
('t2222222-2222-2222-2222-222222222222', 'd1111111-1111-1111-1111-111111111111', 'voice', 'Of course! Our premium features include advanced analytics, priority support, and custom integrations.', 'agent', CURRENT_TIMESTAMP - INTERVAL '5 hours' + INTERVAL '30 seconds', 0.98),
('t3333333-3333-3333-3333-333333333333', 'd2222222-2222-2222-2222-222222222222', 'chat', 'I have a question about my recent invoice.', 'user', CURRENT_TIMESTAMP - INTERVAL '3 hours', 0.99),
('t4444444-4444-4444-4444-444444444444', 'd2222222-2222-2222-2222-222222222222', 'chat', 'I can help you with that. Let me pull up your invoice details.', 'agent', CURRENT_TIMESTAMP - INTERVAL '3 hours' + INTERVAL '15 seconds', 0.97);

-- ============================================================================
-- KNOWLEDGE BASE
-- ============================================================================

INSERT INTO knowledge_base (kb_id, category, title, content, created_by, created_at, updated_at, tags, active) VALUES
('kb111111-1111-1111-1111-111111111111', 'Product', 'Getting Started Guide', 'This comprehensive guide helps new users get started with our platform...', '11111111-1111-1111-1111-111111111111', CURRENT_TIMESTAMP - INTERVAL '60 days', CURRENT_TIMESTAMP - INTERVAL '10 days', ARRAY['onboarding', 'tutorial', 'basics'], TRUE),
('kb222222-2222-2222-2222-222222222222', 'Billing', 'Payment Methods', 'We accept various payment methods including credit cards, PayPal, and bank transfers...', '22222222-2222-2222-2222-222222222222', CURRENT_TIMESTAMP - INTERVAL '55 days', CURRENT_TIMESTAMP - INTERVAL '15 days', ARRAY['billing', 'payment', 'finance'], TRUE),
('kb333333-3333-3333-3333-333333333333', 'Technical', 'API Documentation', 'Our API allows you to integrate with your existing systems. Here are the endpoints...', '11111111-1111-1111-1111-111111111111', CURRENT_TIMESTAMP - INTERVAL '50 days', CURRENT_TIMESTAMP - INTERVAL '5 days', ARRAY['api', 'integration', 'developer'], TRUE),
('kb444444-4444-4444-4444-444444444444', 'Support', 'Troubleshooting Common Issues', 'This article covers the most common issues users face and how to resolve them...', '33333333-3333-3333-3333-333333333333', CURRENT_TIMESTAMP - INTERVAL '45 days', CURRENT_TIMESTAMP - INTERVAL '3 days', ARRAY['support', 'troubleshooting', 'faq'], TRUE);

-- ============================================================================
-- WORKFLOWS
-- ============================================================================

INSERT INTO workflow (workflow_id, name, trigger_type, actions_json, created_by, created_at, status) VALUES
('wf111111-1111-1111-1111-111111111111', 'New User Welcome', 'user_registered', '{"actions": [{"type": "send_email", "template": "welcome"}, {"type": "assign_agent", "agent_id": "ag111111-1111-1111-1111-111111111111"}]}', '11111111-1111-1111-1111-111111111111', CURRENT_TIMESTAMP - INTERVAL '40 days', 'active'),
('wf222222-2222-2222-2222-222222222222', 'Escalation Notification', 'issue_escalated', '{"actions": [{"type": "notify_admin", "priority": "high"}, {"type": "create_ticket"}]}', '22222222-2222-2222-2222-222222222222', CURRENT_TIMESTAMP - INTERVAL '35 days', 'active'),
('wf333333-3333-3333-3333-333333333333', 'Idle Session Cleanup', 'session_idle', '{"actions": [{"type": "end_session"}, {"type": "send_feedback_request"}]}', '11111111-1111-1111-1111-111111111111', CURRENT_TIMESTAMP - INTERVAL '30 days', 'active');

-- ============================================================================
-- WORKFLOW ACTION LOGS
-- ============================================================================

INSERT INTO workflow_action_log (action_log_id, wf_id, action_type, status, action_time, result) VALUES
('wa111111-1111-1111-1111-111111111111', 'wf111111-1111-1111-1111-111111111111', 'send_email', 'success', CURRENT_TIMESTAMP - INTERVAL '5 hours', 'Welcome email sent successfully'),
('wa222222-2222-2222-2222-222222222222', 'wf111111-1111-1111-1111-111111111111', 'assign_agent', 'success', CURRENT_TIMESTAMP - INTERVAL '5 hours' + INTERVAL '30 seconds', 'Agent assigned successfully'),
('wa333333-3333-3333-3333-333333333333', 'wf222222-2222-2222-2222-222222222222', 'notify_admin', 'success', CURRENT_TIMESTAMP - INTERVAL '2 hours', 'Admin notified about escalation');

-- ============================================================================
-- INTERACTION INSTANCES
-- ============================================================================

INSERT INTO interaction_instance (instance_id, user_id, crm_id, workflow_id, started_at, ended_at, status) VALUES
('in111111-1111-1111-1111-111111111111', 'u1111111-1111-1111-1111-111111111111', 'c1111111-1111-1111-1111-111111111111', 'wf111111-1111-1111-1111-111111111111', CURRENT_TIMESTAMP - INTERVAL '5 hours', CURRENT_TIMESTAMP - INTERVAL '4 hours 45 minutes', 'completed'),
('in222222-2222-2222-2222-222222222222', 'u2222222-2222-2222-2222-222222222222', 'c2222222-2222-2222-2222-222222222222', 'wf111111-1111-1111-1111-111111111111', CURRENT_TIMESTAMP - INTERVAL '3 hours', CURRENT_TIMESTAMP - INTERVAL '2 hours 50 minutes', 'completed'),
('in333333-3333-3333-3333-333333333333', 'u3333333-3333-3333-3333-333333333333', 'c3333333-3333-3333-3333-333333333333', 'wf222222-2222-2222-2222-222222222222', CURRENT_TIMESTAMP - INTERVAL '2 hours', CURRENT_TIMESTAMP - INTERVAL '1 hour 40 minutes', 'completed');

-- ============================================================================
-- ANALYTICS EVENTS
-- ============================================================================

INSERT INTO analytics_event (analytics_id, crm_name, external_id, instance_user, event_name, context, status, event_type, event_time) VALUES
('an111111-1111-1111-1111-111111111111', 'TechCorp Inc.', 'ext-001', 'u1111111-1111-1111-1111-111111111111', 'session_started', '{"channel": "voice", "agent": "Customer Support Bot"}', 'success', 'session', CURRENT_TIMESTAMP - INTERVAL '5 hours'),
('an222222-2222-2222-2222-222222222222', 'TechCorp Inc.', 'ext-001', 'u1111111-1111-1111-1111-111111111111', 'session_ended', '{"duration_seconds": 900, "satisfaction": 4}', 'success', 'session', CURRENT_TIMESTAMP - INTERVAL '4 hours 45 minutes'),
('an333333-3333-3333-3333-333333333333', 'HealthPlus LLC', 'ext-002', 'u2222222-2222-2222-2222-222222222222', 'message_sent', '{"message_count": 5}', 'success', 'interaction', CURRENT_TIMESTAMP - INTERVAL '3 hours'),
('an444444-4444-4444-4444-444444444444', 'FinanceFirst', 'ext-003', 'u3333333-3333-3333-3333-333333333333', 'escalation_triggered', '{"reason": "complex_technical_issue"}', 'success', 'escalation', CURRENT_TIMESTAMP - INTERVAL '2 hours');

-- ============================================================================
-- ESCALATIONS
-- ============================================================================

INSERT INTO escalate (escalate_id, crm_id, user_id, assigned_agent, assigned_admin, status, created_at, description) VALUES
('es111111-1111-1111-1111-111111111111', 'c3333333-3333-3333-3333-333333333333', 'u3333333-3333-3333-3333-333333333333', 'ag333333-3333-3333-3333-333333333333', '33333333-3333-3333-3333-333333333333', 'in_progress', CURRENT_TIMESTAMP - INTERVAL '2 hours', 'User experiencing technical difficulties with API integration'),
('es222222-2222-2222-2222-222222222222', 'c1111111-1111-1111-1111-111111111111', 'u1111111-1111-1111-1111-111111111111', 'ag111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 'resolved', CURRENT_TIMESTAMP - INTERVAL '1 day', 'Billing dispute - resolved in favor of customer');

-- ============================================================================
-- CRM LOGS
-- ============================================================================

INSERT INTO crm_log (crm_log_id, crm_id, user_id, action, status, log_time) VALUES
('cl111111-1111-1111-1111-111111111111', 'c1111111-1111-1111-1111-111111111111', 'u1111111-1111-1111-1111-111111111111', 'contact_created', 'success', CURRENT_TIMESTAMP - INTERVAL '5 hours'),
('cl222222-2222-2222-2222-222222222222', 'c2222222-2222-2222-2222-222222222222', 'u2222222-2222-2222-2222-222222222222', 'lead_updated', 'success', CURRENT_TIMESTAMP - INTERVAL '3 hours'),
('cl333333-3333-3333-3333-333333333333', 'c3333333-3333-3333-3333-333333333333', 'u3333333-3333-3333-3333-333333333333', 'opportunity_created', 'success', CURRENT_TIMESTAMP - INTERVAL '2 hours');

-- ============================================================================
-- WEBHOOK EVENTS
-- ============================================================================

INSERT INTO webhook_event (webhook_id, event_type, initiator, payload, received_at, status, response_code) VALUES
('wh111111-1111-1111-1111-111111111111', 'user.created', 'external_system', '{"user_id": "ext-user-001", "email": "newuser@example.com"}', CURRENT_TIMESTAMP - INTERVAL '6 hours', 'processed', 200),
('wh222222-2222-2222-2222-222222222222', 'session.completed', 'agent_system', '{"session_id": "s1111111-1111-1111-1111-111111111111", "duration": 900}', CURRENT_TIMESTAMP - INTERVAL '4 hours 45 minutes', 'processed', 200),
('wh333333-3333-3333-3333-333333333333', 'payment.received', 'billing_system', '{"amount": 99.99, "currency": "USD"}', CURRENT_TIMESTAMP - INTERVAL '2 hours', 'processed', 200);

-- ============================================================================
-- SYSTEM LOGS
-- ============================================================================

INSERT INTO system_log (log_id, log_type, log_message, log_time, source) VALUES
('sl111111-1111-1111-1111-111111111111', 'INFO', 'Database initialization completed successfully', CURRENT_TIMESTAMP - INTERVAL '90 days', 'database'),
('sl222222-2222-2222-2222-222222222222', 'INFO', 'New agent deployed: Customer Support Bot', CURRENT_TIMESTAMP - INTERVAL '30 days', 'agent_manager'),
('sl333333-3333-3333-3333-333333333333', 'WARNING', 'High session volume detected', CURRENT_TIMESTAMP - INTERVAL '5 hours', 'monitoring'),
('sl444444-4444-4444-4444-444444444444', 'INFO', 'Scheduled maintenance completed', CURRENT_TIMESTAMP - INTERVAL '1 day', 'system'),
('sl555555-5555-5555-5555-555555555555', 'ERROR', 'Failed webhook delivery attempt (retry scheduled)', CURRENT_TIMESTAMP - INTERVAL '3 hours', 'webhook_service');

-- ============================================================================
-- SEED DATA COMPLETE
-- ============================================================================

-- Verify data insertion
SELECT 'Seed data inserted successfully!' AS status,
       (SELECT COUNT(*) FROM "user") AS total_users,
       (SELECT COUNT(*) FROM admin) AS total_admins,
       (SELECT COUNT(*) FROM agent) AS total_agents,
       (SELECT COUNT(*) FROM dialogue) AS total_dialogues,
       (SELECT COUNT(*) FROM knowledge_base) AS total_kb_articles,
       (SELECT COUNT(*) FROM workflow) AS total_workflows;

