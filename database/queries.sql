-- Tele-AI Database - Useful Queries
-- Common queries for working with the Tele-AI database

-- ============================================================================
-- USER QUERIES
-- ============================================================================

-- Get all active users
SELECT user_id, name, email, role, date_joined, last_login
FROM "user"
WHERE status = 'active'
ORDER BY date_joined DESC;

-- Get user session statistics
SELECT 
    u.user_id,
    u.name,
    u.email,
    COUNT(DISTINCT s.session_id) as total_sessions,
    COUNT(DISTINCT d.dialogue_id) as total_dialogues,
    AVG(EXTRACT(EPOCH FROM (s.ended_at - s.started_at))/60) as avg_session_duration_minutes
FROM "user" u
LEFT JOIN auto_session s ON u.user_id = s.user_id
LEFT JOIN dialogue d ON u.user_id = d.user_id
GROUP BY u.user_id, u.name, u.email
ORDER BY total_sessions DESC;

-- ============================================================================
-- AGENT QUERIES
-- ============================================================================

-- Get all active agents with their stats
SELECT 
    a.agent_id,
    a.name,
    a.status,
    a.channel_type,
    COUNT(DISTINCT d.dialogue_id) as total_conversations,
    COUNT(DISTINCT CASE WHEN d.escalated = TRUE THEN d.dialogue_id END) as escalated_count,
    ROUND(AVG(CASE WHEN d.ended_at IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (d.ended_at - d.started_at))/60 
        END), 2) as avg_conversation_minutes
FROM agent a
LEFT JOIN dialogue d ON a.agent_id = d.assigned_agent
WHERE a.status = 'active'
GROUP BY a.agent_id, a.name, a.status, a.channel_type
ORDER BY total_conversations DESC;

-- ============================================================================
-- SESSION & DIALOGUE QUERIES
-- ============================================================================

-- Get recent active sessions
SELECT 
    s.session_id,
    u.name as user_name,
    u.email,
    c.crm_name,
    s.session_type,
    s.started_at,
    s.ended_at,
    EXTRACT(EPOCH FROM (COALESCE(s.ended_at, CURRENT_TIMESTAMP) - s.started_at))/60 as duration_minutes
FROM auto_session s
JOIN "user" u ON s.user_id = u.user_id
LEFT JOIN crm_entity c ON s.crm_id = c.crm_id
ORDER BY s.started_at DESC
LIMIT 20;

-- Get dialogues with transcription count
SELECT 
    d.dialogue_id,
    u.name as user_name,
    a.name as agent_name,
    d.channel_type,
    d.status,
    d.started_at,
    d.ended_at,
    COUNT(t.transcription_id) as transcription_count,
    d.escalated
FROM dialogue d
JOIN "user" u ON d.user_id = u.user_id
LEFT JOIN agent a ON d.assigned_agent = a.agent_id
LEFT JOIN transcription t ON d.dialogue_id = t.dialogue_id
GROUP BY d.dialogue_id, u.name, a.name, d.channel_type, d.status, d.started_at, d.ended_at, d.escalated
ORDER BY d.started_at DESC
LIMIT 20;

-- ============================================================================
-- ESCALATION QUERIES
-- ============================================================================

-- Get pending escalations
SELECT 
    e.escalate_id,
    u.name as user_name,
    u.email,
    c.crm_name,
    ag.name as agent_name,
    ad.name as assigned_admin,
    e.status,
    e.created_at,
    e.description
FROM escalate e
JOIN "user" u ON e.user_id = u.user_id
LEFT JOIN crm_entity c ON e.crm_id = c.crm_id
LEFT JOIN agent ag ON e.assigned_agent = ag.agent_id
LEFT JOIN admin ad ON e.assigned_admin = ad.admin_id
WHERE e.status IN ('pending', 'in_progress')
ORDER BY e.created_at DESC;

-- ============================================================================
-- ANALYTICS QUERIES
-- ============================================================================

-- Get analytics summary by event type
SELECT 
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT instance_user) as unique_users,
    DATE_TRUNC('day', event_time) as event_date
FROM analytics_event
WHERE event_time >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY event_type, DATE_TRUNC('day', event_time)
ORDER BY event_date DESC, event_count DESC;

-- Get daily session statistics
SELECT 
    DATE(started_at) as session_date,
    COUNT(*) as total_sessions,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(EXTRACT(EPOCH FROM (ended_at - started_at))/60) as avg_duration_minutes,
    COUNT(CASE WHEN session_type = 'voice_call' THEN 1 END) as voice_sessions,
    COUNT(CASE WHEN session_type = 'chat' THEN 1 END) as chat_sessions
FROM auto_session
WHERE started_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(started_at)
ORDER BY session_date DESC;

-- ============================================================================
-- KNOWLEDGE BASE QUERIES
-- ============================================================================

-- Get most used knowledge base articles
SELECT 
    kb.kb_id,
    kb.title,
    kb.category,
    kb.tags,
    kb.created_at,
    kb.updated_at
FROM knowledge_base kb
WHERE kb.active = TRUE
ORDER BY kb.updated_at DESC
LIMIT 20;

-- ============================================================================
-- WORKFLOW QUERIES
-- ============================================================================

-- Get workflow execution statistics
SELECT 
    w.workflow_id,
    w.name,
    w.trigger_type,
    w.status,
    COUNT(wal.action_log_id) as total_executions,
    COUNT(CASE WHEN wal.status = 'success' THEN 1 END) as successful_executions,
    COUNT(CASE WHEN wal.status = 'error' THEN 1 END) as failed_executions,
    MAX(wal.action_time) as last_execution
FROM workflow w
LEFT JOIN workflow_action_log wal ON w.workflow_id = wal.wf_id
GROUP BY w.workflow_id, w.name, w.trigger_type, w.status
ORDER BY total_executions DESC;

-- ============================================================================
-- SYSTEM MONITORING QUERIES
-- ============================================================================

-- Get recent system errors
SELECT 
    log_id,
    log_type,
    log_message,
    log_time,
    source
FROM system_log
WHERE log_type IN ('ERROR', 'WARNING')
ORDER BY log_time DESC
LIMIT 50;

-- Get webhook delivery statistics
SELECT 
    event_type,
    status,
    COUNT(*) as event_count,
    AVG(response_code) as avg_response_code,
    DATE_TRUNC('hour', received_at) as hour
FROM webhook_event
WHERE received_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY event_type, status, DATE_TRUNC('hour', received_at)
ORDER BY hour DESC, event_count DESC;

-- ============================================================================
-- ADMIN & PERMISSION QUERIES
-- ============================================================================

-- Get admin users with their permissions
SELECT 
    a.admin_id,
    a.name,
    a.email,
    a.role,
    STRING_AGG(p.name, ', ') as permissions
FROM admin a
LEFT JOIN agent_permission_map apm ON a.admin_id = apm.admin_id
LEFT JOIN permission p ON apm.permission_id = p.permission_id
GROUP BY a.admin_id, a.name, a.email, a.role
ORDER BY a.name;

-- ============================================================================
-- CRM QUERIES
-- ============================================================================

-- Get CRM entity activity summary
SELECT 
    c.crm_id,
    c.crm_name,
    c.industry,
    c.rating_score,
    COUNT(DISTINCT s.session_id) as total_sessions,
    COUNT(DISTINCT d.dialogue_id) as total_dialogues,
    COUNT(DISTINCT cl.crm_log_id) as total_log_entries,
    MAX(s.started_at) as last_activity
FROM crm_entity c
LEFT JOIN auto_session s ON c.crm_id = s.crm_id
LEFT JOIN dialogue d ON c.crm_id = d.crm_id
LEFT JOIN crm_log cl ON c.crm_id = cl.crm_id
GROUP BY c.crm_id, c.crm_name, c.industry, c.rating_score
ORDER BY last_activity DESC NULLS LAST;

