# Tele-AI Database Setup Guide

## 📋 Overview

This database setup provides a complete PostgreSQL database for the Tele-AI system based on the provided ERD diagram. It includes 17 tables with comprehensive relationships and dummy data for testing.

## 🗂️ File Structure

```
database/
├── README.md              # Main documentation
├── SETUP_GUIDE.md        # This file - detailed setup instructions
├── schema.sql            # Complete database schema (17 tables)
├── seed_data.sql         # Dummy/test data
├── queries.sql           # Useful SQL queries
├── docker-compose.yml    # Docker setup for PostgreSQL + PgAdmin
├── init.sh              # Quick initialization script (Linux/Mac)
├── .env.example         # Environment variables template
└── .gitignore           # Git ignore rules
```

## 🚀 Quick Start

### Option 1: Using Docker (Recommended)

**Step 1: Copy environment file**
```bash
cd database
cp .env.example .env
# Edit .env with your preferred settings if needed
```

**Step 2: Start the database**
```bash
docker-compose up -d
```

**Step 3: Verify**
The database will automatically:
- Create PostgreSQL container
- Load schema from `schema.sql`
- Load dummy data from `seed_data.sql`
- Start PgAdmin web interface

Access PgAdmin at: `http://localhost:5050`
- Email: `admin@teleai.com`
- Password: (see `.env` file)

### Option 2: Using Initialization Script (Linux/Mac)

```bash
cd database
./init.sh
```

### Option 3: Manual Setup (Windows without Docker)

**Prerequisites:**
- PostgreSQL 15+ installed locally

**Step 1: Create database**
```bash
psql -U postgres
CREATE DATABASE TELEE;
\q
```

**Step 2: Load schema**
```bash
psql -U postgres -d TELEE -f schema.sql
```

**Step 3: Load dummy data**
```bash
psql -U postgres -d TELEE -f seed_data.sql
```

## 📊 Database Schema

### Core Tables

1. **USER** - End users
   - Tracks user information, role, status
   - Linked to sessions and dialogues

2. **ADMIN** - Administrative users
   - Manages system administrators
   - Linked to permissions and created resources

3. **PERMISSION** - Access control
   - Defines system permissions
   - Mapped to admins via junction table

4. **AGENT_PERMISSION_MAP** - Junction table
   - Links admins to their permissions

### Agent & Session Tables

5. **AGENT** - AI agents
   - Agent configurations and status
   - Linked to dialogues and sessions

6. **AUTO_SESSION** - Session tracking
   - Tracks user sessions
   - Records timing and metadata

7. **DIALOGUE** - Conversations
   - Individual conversation records
   - Linked to users, agents, sessions
   - Tracks escalations

8. **TRANSCRIPTION** - Voice transcripts
   - Stores conversation transcriptions
   - Linked to dialogues
   - Includes confidence scores

### CRM Tables

9. **CRM_ENTITY** - CRM integrations
   - Tracks CRM entities
   - Industry and rating information

10. **CRM_LOG** - CRM activity logs
    - Records CRM-related actions
    - Error tracking

### Escalation

11. **ESCALATE** - Issue escalation
    - Manages escalated issues
    - Assigns to admins
    - Tracks resolution

### Knowledge & Workflow

12. **KNOWLEDGE_BASE** - Knowledge articles
    - Stores help articles
    - Categorized and tagged
    - Version tracking

13. **WORKFLOW** - Automated workflows
    - Workflow definitions
    - Trigger types and actions (JSON)

14. **WORKFLOW_ACTION_LOG** - Workflow execution logs
    - Tracks workflow runs
    - Success/error logging

### Analytics & Interaction

15. **INTERACTION_INSTANCE** - User interactions
    - Tracks user-workflow interactions
    - Status and duration

16. **ANALYTICS_EVENT** - Analytics tracking
    - Event tracking and analytics
    - Context stored as JSON

### Logging

17. **WEBHOOK_EVENT** - Webhook logs
    - Incoming webhook tracking
    - Payload and response codes

18. **SYSTEM_LOG** - System logs
    - General system logging
    - Error and info messages

## 🎲 Dummy Data Included

The `seed_data.sql` file includes:

- **3 Admin Users**
  - Super Admin (all permissions)
  - Manager (selected permissions)
  - Support (limited permissions)

- **7 Permissions**
  - Analytics, Agents, Users, KB, Workflows, Logs, Escalations

- **5 End Users**
  - Mix of active/inactive statuses
  - Various roles

- **5 CRM Entities**
  - Different industries (Tech, Healthcare, Finance, Education, Retail)

- **4 AI Agents**
  - Customer Support, Sales, Technical Support, Billing

- **4 Sessions** with dialogues and transcriptions

- **4 Knowledge Base Articles**
  - Different categories

- **3 Workflows** with action logs

- **Multiple Analytics Events**

- **2 Escalations** (pending and resolved)

- **Webhook Events** and **System Logs**

All with realistic relationships and timestamps!

## 🔌 Connection Details

### PostgreSQL Direct Connection

```
Host: localhost
Port: 5432
Database: TELEE
Username: postgres
Password: postgres
```

### Connection String

```
postgresql://postgres:postgres@localhost:5432/TELEE
```

### PgAdmin Web Interface

```
URL: http://localhost:5050
Email: admin@teleai.com
Password: admin123
```

## 📝 Useful Commands

### Docker Commands

```bash
# Start database
docker-compose up -d

# View logs
docker-compose logs -f postgres

# Stop database
docker-compose down

# Stop and remove all data
docker-compose down -v

# Restart database
docker-compose restart postgres

# Access PostgreSQL CLI
docker exec -it teleai_postgres psql -U postgres -d TELEE
```

### PostgreSQL Commands

```bash
# Connect to database
psql -U postgres -d TELEE

# List all tables
\dt

# Describe a table
\d user

# Show all databases
\l

# Show all users
\du

# Exit
\q
```

### Useful Queries

See `queries.sql` for a collection of useful queries:
- User statistics
- Agent performance
- Session analytics
- Escalation tracking
- Workflow execution stats
- System monitoring

Example:
```sql
-- Get all active users with session count
SELECT 
    u.user_id,
    u.name,
    u.email,
    COUNT(DISTINCT s.session_id) as total_sessions
FROM "user" u
LEFT JOIN auto_session s ON u.user_id = s.user_id
WHERE u.status = 'active'
GROUP BY u.user_id, u.name, u.email
ORDER BY total_sessions DESC;
```

## 🔒 Security Notes

**⚠️ IMPORTANT for Production:**

1. **Change default passwords** in `.env` file
2. **Use strong passwords** (20+ characters, mixed)
3. **Don't commit** `.env` file to git (already in .gitignore)
4. **Enable SSL** for PostgreSQL connections
5. **Restrict network access** to database
6. **Regular backups** - see backup section below

## 💾 Backup & Restore

### Backup Database

```bash
# Using Docker
docker exec teleai_postgres pg_dump -U postgres TELEE > backup_$(date +%Y%m%d).sql

# Using local PostgreSQL
pg_dump -U postgres -d TELEE -F c -f backup_$(date +%Y%m%d).dump
```

### Restore Database

```bash
# Using Docker
cat backup_20241031.sql | docker exec -i teleai_postgres psql -U postgres -d TELEE

# Using local PostgreSQL
pg_restore -U postgres -d TELEE backup_20241031.dump
```

## 🧪 Testing the Database

After setup, verify everything works:

```sql
-- 1. Check all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- 2. Verify dummy data
SELECT 
    (SELECT COUNT(*) FROM "user") as users,
    (SELECT COUNT(*) FROM admin) as admins,
    (SELECT COUNT(*) FROM agent) as agents,
    (SELECT COUNT(*) FROM dialogue) as dialogues,
    (SELECT COUNT(*) FROM knowledge_base) as kb_articles;

-- 3. Test relationships
SELECT 
    d.dialogue_id,
    u.name as user_name,
    a.name as agent_name,
    COUNT(t.transcription_id) as transcript_count
FROM dialogue d
JOIN "user" u ON d.user_id = u.user_id
LEFT JOIN agent a ON d.assigned_agent = a.agent_id
LEFT JOIN transcription t ON d.dialogue_id = t.dialogue_id
GROUP BY d.dialogue_id, u.name, a.name;
```

## 🔗 Integration with Application

This database is **separate** from the existing project. To integrate:

1. **Update application connection string:**
   ```python
   DATABASE_URL = "postgresql://teleai_user:password@localhost:5432/teleai_db"
   ```

2. **Install PostgreSQL adapter:**
   ```bash
   pip install psycopg2-binary
   # or
   pip install asyncpg  # for async support
   ```

3. **Use SQLAlchemy (existing pattern):**
   ```python
   from sqlalchemy import create_engine
   engine = create_engine(DATABASE_URL)
   ```

## 📞 Support

For issues or questions:
- Check Docker logs: `docker-compose logs postgres`
- Check PostgreSQL logs in PgAdmin
- Verify `.env` configuration
- Ensure ports 5432 and 5050 are available

## 📄 License

Part of the Tele-AI project.

