# Database Quick Reference

## ✅ Setup Complete!

Your TELEE database is ready with:
- **18 tables** created from ERD
- **Dummy data** loaded for testing
- **Migration system** (Alembic) configured

---

## 📊 Database Details

**Connection String:**
```
postgresql://postgres:postgres@localhost:5432/TELEE
```

**Connection Details:**
- Host: `localhost`
- Port: `5432`
- Database: `TELEE`
- Username: `postgres`
- Password: `postgres`

---

## 📋 Tables Created

### Core Tables
- `user` - End users (5 records)
- `admin` - Administrators (3 records)
- `permission` - Access permissions (7 records)
- `agent_permission_map` - Admin-permission junction

### Agent & Session
- `agent` - AI agents (4 records)
- `auto_session` - Session tracking
- `dialogue` - Conversations
- `transcription` - Voice transcripts

### CRM
- `crm_entity` - CRM entities (5 records)
- `crm_log` - CRM activity logs

### Escalation
- `escalate` - Issue escalations

### Knowledge & Workflows
- `knowledge_base` - Help articles (4 records)
- `workflow` - Automated workflows (3 records)
- `workflow_action_log` - Workflow execution logs

### Analytics
- `interaction_instance` - User interactions
- `analytics_event` - Analytics events

### Logging
- `webhook_event` - Webhook logs
- `system_log` - System logs (5 records)

---

## 🔧 Useful Commands

### Check Migration Status
```bash
cd database
alembic current
```

### View Database Tables
Open your PostgreSQL client and connect to `TELEE`, then:
```sql
\dt                    -- List all tables
\d user                -- Describe user table
SELECT * FROM "user";  -- View users
```

### Rollback Migration
```bash
cd database
alembic downgrade base  # Remove all tables
alembic upgrade head    # Recreate all tables
```

### Reload Seed Data
```bash
python database/load_seed_data.py
```

---

## 📝 Sample Queries

### View All Users
```sql
SELECT user_id, name, email, role, status 
FROM "user" 
ORDER BY date_joined DESC;
```

### View All Agents
```sql
SELECT agent_id, name, status, channel_type, started_at 
FROM agent 
WHERE status = 'active';
```

### View Knowledge Base
```sql
SELECT kb_id, category, title, tags, active 
FROM knowledge_base 
WHERE active = TRUE;
```

### View Admin Permissions
```sql
SELECT 
    a.name as admin_name,
    a.email,
    a.role,
    STRING_AGG(p.name, ', ') as permissions
FROM admin a
LEFT JOIN agent_permission_map apm ON a.admin_id = apm.admin_id
LEFT JOIN permission p ON apm.permission_id = p.permission_id
GROUP BY a.admin_id, a.name, a.email, a.role;
```

---

## 🎯 Integration with Application

To connect your application:

### Python (SQLAlchemy)
```python
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/TELEE"
engine = create_engine(DATABASE_URL)
```

### Python (psycopg2)
```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="TELEE",
    user="postgres",
    password="postgres"
)
```

### Node.js (pg)
```javascript
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'TELEE',
  user: 'postgres',
  password: 'postgres'
});
```

---

## 📁 File Structure

```
database/
├── .env                          # Environment variables (created)
├── .env.example                  # Template
├── schema.sql                    # Raw SQL schema
├── seed_data.sql                 # Original seed data
├── seed_data_simple.sql          # Simplified seed data (used)
├── load_seed_data.py             # Python seed data loader
├── queries.sql                   # Useful queries
├── alembic.ini                   # Alembic configuration
├── docker-compose.yml            # Docker setup
├── requirements.txt              # Python dependencies
├── migrations/
│   ├── env.py                    # Migration environment
│   └── versions/
│       └── 001_initial_schema.py # Initial migration
├── README.md                     # Main documentation
├── SETUP_GUIDE.md                # Detailed setup guide
├── MIGRATION_GUIDE.md            # Migration documentation
└── QUICK_START.md                # This file
```

---

## 🚀 Next Steps

1. **Test the database:**
   - Connect using your PostgreSQL client
   - Run sample queries from `queries.sql`

2. **Integrate with your app:**
   - Update your application's DATABASE_URL
   - Test connections

3. **Add more data:**
   - Modify `seed_data_simple.sql`
   - Run `python database/load_seed_data.py`

4. **Backup regularly:**
   ```bash
   pg_dump -U postgres TELEE > backup_$(date +%Y%m%d).sql
   ```

---

## 🆘 Troubleshooting

### Can't connect to database?
- Ensure PostgreSQL is running
- Check connection details
- Verify firewall settings

### Need to reset database?
```bash
cd database
alembic downgrade base
alembic upgrade head
python load_seed_data.py
```

### Need to add new tables?
```bash
cd database
alembic revision -m "add new table"
# Edit the new migration file
alembic upgrade head
```

---

## 📚 Documentation

- **README.md** - Overview
- **SETUP_GUIDE.md** - Comprehensive setup instructions
- **MIGRATION_GUIDE.md** - Alembic migration details
- **queries.sql** - Collection of useful queries

---

**Database Version:** 001 (Initial Schema)  
**Last Updated:** 2024-10-31  
**Status:** ✅ Ready for use

