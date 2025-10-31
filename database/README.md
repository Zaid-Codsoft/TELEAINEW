# Tele-AI PostgreSQL Database Setup

This folder contains the complete PostgreSQL database setup for the Tele-AI system, based on the provided ERD.

## Structure

- `schema.sql` - Complete database schema with all tables
- `seed_data.sql` - Dummy/initial data for testing
- `docker-compose.yml` - PostgreSQL container setup
- `.env.example` - Environment variables template
- `init.sh` - Quick initialization script

## Quick Start

### Option 1: Using Docker (Recommended)

```bash
cd database
cp .env.example .env
# Edit .env with your preferred settings
docker-compose up -d
```

### Option 2: Manual Setup

```bash
# Create database
createdb teleai_db

# Run schema
psql teleai_db < schema.sql

# Load dummy data
psql teleai_db < seed_data.sql
```

## Database Structure

The database includes the following tables:

1. **USER** - End users of the system
2. **ADMIN** - Administrative users
3. **AGENT** - AI agents configuration
4. **DIALOGUE** - Conversation sessions
5. **AUTO_SESSION** - Automated session tracking
6. **KNOWLEDGE_BASE** - Knowledge base articles
7. **WORKFLOW** - Automated workflows
8. **CRM_ENTITY** - CRM integration
9. **CRM_LOG** - CRM activity logs
10. **WEBHOOK_EVENT** - Webhook event tracking
11. **SYSTEM_LOG** - System-wide logs
12. **PERMISSION** - User permissions
13. **AGENT_PERMISSION_MAP** - Agent-permission mapping
14. **INTERACTION_INSTANCE** - User interaction instances
15. **ANALYTICS_EVENT** - Analytics tracking
16. **TRANSCRIPTION** - Voice transcriptions
17. **ESCALATE** - Escalation management

## Connection Details

- **Host:** localhost
- **Port:** 5432
- **Database:** TELEE
- **Username:** postgres
- **Password:** postgres

## Notes

This database setup is **separate** from the existing project and is not configured with the current system yet. It can be integrated later as needed.

