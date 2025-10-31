"""Initial schema - Create all tables from ERD

Revision ID: 001
Revises: 
Create Date: 2024-10-31

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables based on ERD"""
    
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # USER Table
    op.create_table(
        'user',
        sa.Column('user_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('phone', sa.String(20)),
        sa.Column('role', sa.String(50), server_default='user'),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.Column('date_joined', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_login', sa.DateTime),
    )
    op.create_index('idx_user_email', 'user', ['email'])
    op.create_index('idx_user_status', 'user', ['status'])
    
    # ADMIN Table
    op.create_table(
        'admin',
        sa.Column('admin_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), server_default='admin'),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_login', sa.DateTime),
    )
    op.create_index('idx_admin_email', 'admin', ['email'])
    
    # PERMISSION Table
    op.create_table(
        'permission',
        sa.Column('permission_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.Text),
    )
    
    # AGENT_PERMISSION_MAP Table (Junction)
    op.create_table(
        'agent_permission_map',
        sa.Column('admin_id', UUID(as_uuid=True), nullable=False),
        sa.Column('permission_id', UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['admin_id'], ['admin.admin_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permission.permission_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('admin_id', 'permission_id'),
    )
    
    # CRM_ENTITY Table
    op.create_table(
        'crm_entity',
        sa.Column('crm_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('crm_name', sa.String(255), nullable=False),
        sa.Column('industry', sa.String(100)),
        sa.Column('rating_score', sa.Float),
        sa.Column('safety_type', sa.String(50)),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('idx_crm_name', 'crm_entity', ['crm_name'])
    
    # AGENT Table
    op.create_table(
        'agent',
        sa.Column('agent_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('admin_id', UUID(as_uuid=True)),
        sa.Column('assigned_agent', UUID(as_uuid=True)),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.Column('channel_type', sa.String(50)),
        sa.Column('started_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('ended_at', sa.DateTime),
        sa.Column('summary', sa.Text),
        sa.Column('escalated', sa.Boolean, server_default='false'),
        sa.ForeignKeyConstraint(['admin_id'], ['admin.admin_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_agent'], ['agent.agent_id'], ondelete='SET NULL'),
    )
    op.create_index('idx_agent_status', 'agent', ['status'])
    op.create_index('idx_agent_admin', 'agent', ['admin_id'])
    
    # AUTO_SESSION Table
    op.create_table(
        'auto_session',
        sa.Column('session_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True)),
        sa.Column('crm_id', UUID(as_uuid=True)),
        sa.Column('admin_id', UUID(as_uuid=True)),
        sa.Column('started_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('ended_at', sa.DateTime),
        sa.Column('session_type', sa.String(50)),
        sa.Column('ip_address', sa.String(45)),
        sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['crm_id'], ['crm_entity.crm_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['admin_id'], ['admin.admin_id'], ondelete='SET NULL'),
    )
    op.create_index('idx_session_user', 'auto_session', ['user_id'])
    op.create_index('idx_session_crm', 'auto_session', ['crm_id'])
    op.create_index('idx_session_started', 'auto_session', ['started_at'])
    
    # DIALOGUE Table
    op.create_table(
        'dialogue',
        sa.Column('dialogue_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True)),
        sa.Column('crm_id', UUID(as_uuid=True)),
        sa.Column('session_id', UUID(as_uuid=True)),
        sa.Column('assigned_agent', UUID(as_uuid=True)),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.Column('channel_type', sa.String(50)),
        sa.Column('started_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('ended_at', sa.DateTime),
        sa.Column('summary', sa.Text),
        sa.Column('escalated', sa.Boolean, server_default='false'),
        sa.Column('text', sa.Text),
        sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['crm_id'], ['crm_entity.crm_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['session_id'], ['auto_session.session_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_agent'], ['agent.agent_id'], ondelete='SET NULL'),
    )
    op.create_index('idx_dialogue_user', 'dialogue', ['user_id'])
    op.create_index('idx_dialogue_session', 'dialogue', ['session_id'])
    op.create_index('idx_dialogue_started', 'dialogue', ['started_at'])
    
    # TRANSCRIPTION Table
    op.create_table(
        'transcription',
        sa.Column('transcription_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('dialogue_id', UUID(as_uuid=True)),
        sa.Column('channel', sa.String(50)),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('speaker_label', sa.String(100)),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('confidence', sa.Float),
        sa.ForeignKeyConstraint(['dialogue_id'], ['dialogue.dialogue_id'], ondelete='CASCADE'),
    )
    op.create_index('idx_transcription_dialogue', 'transcription', ['dialogue_id'])
    op.create_index('idx_transcription_created', 'transcription', ['created_at'])
    
    # ESCALATE Table
    op.create_table(
        'escalate',
        sa.Column('escalate_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('crm_id', UUID(as_uuid=True)),
        sa.Column('user_id', UUID(as_uuid=True)),
        sa.Column('assigned_agent', UUID(as_uuid=True)),
        sa.Column('assigned_admin', UUID(as_uuid=True)),
        sa.Column('status', sa.String(50), server_default='pending'),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('resolved_at', sa.DateTime),
        sa.Column('description', sa.Text),
        sa.ForeignKeyConstraint(['crm_id'], ['crm_entity.crm_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_agent'], ['agent.agent_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_admin'], ['admin.admin_id'], ondelete='SET NULL'),
    )
    op.create_index('idx_escalate_status', 'escalate', ['status'])
    op.create_index('idx_escalate_user', 'escalate', ['user_id'])
    
    # KNOWLEDGE_BASE Table
    op.create_table(
        'knowledge_base',
        sa.Column('kb_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('category', sa.String(100)),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('tags', sa.ARRAY(sa.Text)),
        sa.Column('active', sa.Boolean, server_default='true'),
        sa.ForeignKeyConstraint(['created_by'], ['admin.admin_id'], ondelete='SET NULL'),
    )
    op.create_index('idx_kb_category', 'knowledge_base', ['category'])
    op.create_index('idx_kb_created', 'knowledge_base', ['created_at'])
    op.create_index('idx_kb_active', 'knowledge_base', ['active'])
    
    # WORKFLOW Table
    op.create_table(
        'workflow',
        sa.Column('workflow_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('trigger_type', sa.String(100)),
        sa.Column('actions_json', JSONB),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.ForeignKeyConstraint(['created_by'], ['admin.admin_id'], ondelete='SET NULL'),
    )
    op.create_index('idx_workflow_trigger', 'workflow', ['trigger_type'])
    op.create_index('idx_workflow_status', 'workflow', ['status'])
    
    # WORKFLOW_ACTION_LOG Table
    op.create_table(
        'workflow_action_log',
        sa.Column('action_log_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('wf_id', UUID(as_uuid=True)),
        sa.Column('action_type', sa.String(100)),
        sa.Column('status', sa.String(50)),
        sa.Column('action_time', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('error_message', sa.Text),
        sa.Column('result', sa.Text),
        sa.ForeignKeyConstraint(['wf_id'], ['workflow.workflow_id'], ondelete='CASCADE'),
    )
    op.create_index('idx_workflow_log_wf', 'workflow_action_log', ['wf_id'])
    op.create_index('idx_workflow_log_time', 'workflow_action_log', ['action_time'])
    
    # INTERACTION_INSTANCE Table
    op.create_table(
        'interaction_instance',
        sa.Column('instance_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True)),
        sa.Column('crm_id', UUID(as_uuid=True)),
        sa.Column('workflow_id', UUID(as_uuid=True)),
        sa.Column('started_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('ended_at', sa.DateTime),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['crm_id'], ['crm_entity.crm_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflow.workflow_id'], ondelete='SET NULL'),
    )
    op.create_index('idx_instance_user', 'interaction_instance', ['user_id'])
    op.create_index('idx_instance_workflow', 'interaction_instance', ['workflow_id'])
    
    # ANALYTICS_EVENT Table
    op.create_table(
        'analytics_event',
        sa.Column('analytics_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('crm_name', sa.String(255)),
        sa.Column('external_id', sa.String(255)),
        sa.Column('instance_user', UUID(as_uuid=True)),
        sa.Column('event_name', sa.String(255), nullable=False),
        sa.Column('context', JSONB),
        sa.Column('status', sa.String(50)),
        sa.Column('event_type', sa.String(100)),
        sa.Column('event_time', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['instance_user'], ['user.user_id'], ondelete='SET NULL'),
    )
    op.create_index('idx_analytics_event_name', 'analytics_event', ['event_name'])
    op.create_index('idx_analytics_event_time', 'analytics_event', ['event_time'])
    op.create_index('idx_analytics_event_type', 'analytics_event', ['event_type'])
    
    # CRM_LOG Table
    op.create_table(
        'crm_log',
        sa.Column('crm_log_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('crm_id', UUID(as_uuid=True)),
        sa.Column('user_id', UUID(as_uuid=True)),
        sa.Column('action', sa.String(255)),
        sa.Column('status', sa.String(50)),
        sa.Column('error_message', sa.Text),
        sa.Column('log_time', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['crm_id'], ['crm_entity.crm_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ondelete='SET NULL'),
    )
    op.create_index('idx_crm_log_crm', 'crm_log', ['crm_id'])
    op.create_index('idx_crm_log_time', 'crm_log', ['log_time'])
    
    # WEBHOOK_EVENT Table
    op.create_table(
        'webhook_event',
        sa.Column('webhook_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('event_type', sa.String(100)),
        sa.Column('initiator', sa.String(255)),
        sa.Column('payload', JSONB),
        sa.Column('received_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('status', sa.String(50)),
        sa.Column('response_code', sa.Integer),
    )
    op.create_index('idx_webhook_event_type', 'webhook_event', ['event_type'])
    op.create_index('idx_webhook_received', 'webhook_event', ['received_at'])
    
    # SYSTEM_LOG Table
    op.create_table(
        'system_log',
        sa.Column('log_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('log_type', sa.String(100)),
        sa.Column('log_message', sa.Text),
        sa.Column('log_time', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('source', sa.String(255)),
    )
    op.create_index('idx_system_log_type', 'system_log', ['log_type'])
    op.create_index('idx_system_log_time', 'system_log', ['log_time'])


def downgrade() -> None:
    """Drop all tables"""
    
    op.drop_table('system_log')
    op.drop_table('webhook_event')
    op.drop_table('crm_log')
    op.drop_table('analytics_event')
    op.drop_table('interaction_instance')
    op.drop_table('workflow_action_log')
    op.drop_table('workflow')
    op.drop_table('knowledge_base')
    op.drop_table('escalate')
    op.drop_table('transcription')
    op.drop_table('dialogue')
    op.drop_table('auto_session')
    op.drop_table('agent')
    op.drop_table('crm_entity')
    op.drop_table('agent_permission_map')
    op.drop_table('permission')
    op.drop_table('admin')
    op.drop_table('user')
    
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')

