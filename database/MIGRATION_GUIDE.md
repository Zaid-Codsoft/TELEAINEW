# Database Migration Guide

This guide explains how to use Alembic for database migrations in the Tele-AI project.

## 📋 Overview

We use **Alembic** for version-controlled database migrations. This provides:
- ✅ Version control for database schema
- ✅ Up/down migration support (rollback capability)
- ✅ Automatic migration script generation
- ✅ Team collaboration on schema changes

## 🗂️ Migration Files

### Current Migration System

We have **TWO** approaches for database setup:

#### 1. **Raw SQL** (Simple, Docker-based)
- `schema.sql` - Complete schema (auto-loaded by Docker)
- `seed_data.sql` - Dummy data (auto-loaded by Docker)
- ✅ Best for: Quick setup, Docker environments, initial development

#### 2. **Alembic** (Professional, Version-controlled)
- `migrations/versions/001_initial_schema.py` - Initial migration
- ✅ Best for: Production, team collaboration, incremental changes

## 🚀 Quick Start

### Setup Alembic

**Step 1: Install dependencies**
```bash
cd database
pip install -r requirements.txt
```

**Step 2: Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

## 📝 Using Migrations

### Apply Migrations (Create Tables)

```bash
# Run all pending migrations (upgrade to latest)
alembic upgrade head

# Run specific migration
alembic upgrade 001

# Show current revision
alembic current

# Show migration history
alembic history
```

### Rollback Migrations (Drop Tables)

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade 001

# Rollback all migrations (drop all tables)
alembic downgrade base
```

### Create New Migrations

```bash
# Create a new migration file
alembic revision -m "add new table or column"

# This creates: migrations/versions/XXXXX_add_new_table_or_column.py
```

**Example: Adding a new table**

```python
# migrations/versions/002_add_notifications.py
def upgrade():
    op.create_table(
        'notifications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True)),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ondelete='CASCADE'),
    )
    op.create_index('idx_notifications_user', 'notifications', ['user_id'])

def downgrade():
    op.drop_table('notifications')
```

## 🔄 Migration Workflow

### Development Workflow

```bash
# 1. Make changes to your migration file
vim migrations/versions/002_new_feature.py

# 2. Apply migration
alembic upgrade head

# 3. Test your changes
psql -U teleai_user -d teleai_db
\dt  # List tables

# 4. If needed, rollback and fix
alembic downgrade -1
# Fix migration file
alembic upgrade head
```

### Team Workflow

```bash
# 1. Pull latest code (with new migrations)
git pull origin main

# 2. Check migration status
alembic current
alembic history

# 3. Apply new migrations
alembic upgrade head

# 4. Verify
psql -U postgres -d TELEE
```

## 📊 Migration vs Raw SQL

| Feature | Raw SQL | Alembic |
|---------|---------|---------|
| **Setup Speed** | Fast ⚡ | Medium |
| **Version Control** | Manual | Automatic ✅ |
| **Rollback** | Manual | Easy ✅ |
| **Team Collaboration** | Difficult | Easy ✅ |
| **Production** | Not recommended | Recommended ✅ |
| **Docker Integration** | Built-in ✅ | Manual |

## 🎯 Which Approach to Use?

### Use **Raw SQL** (schema.sql) when:
- ✅ Quick development setup
- ✅ Using Docker Compose
- ✅ Single developer
- ✅ Prototype/demo phase

### Use **Alembic** when:
- ✅ Production environment
- ✅ Multiple developers
- ✅ Need version control
- ✅ Need rollback capability
- ✅ Incremental schema changes

## 🔧 Commands Reference

### Alembic Commands

```bash
# Show help
alembic --help

# Initialize Alembic (already done)
alembic init migrations

# Create migration
alembic revision -m "description"

# Auto-generate migration (with models)
alembic revision --autogenerate -m "description"

# Upgrade
alembic upgrade head        # Latest
alembic upgrade +1          # One step forward
alembic upgrade 001         # Specific version

# Downgrade
alembic downgrade base      # Remove all
alembic downgrade -1        # One step back
alembic downgrade 001       # Specific version

# Show info
alembic current             # Current revision
alembic history             # All revisions
alembic show 001            # Show specific migration
alembic heads               # Show head revisions
alembic branches            # Show branches

# Stamp (set version without running migration)
alembic stamp head          # Mark as current
alembic stamp 001           # Mark specific version
```

### PostgreSQL Commands

```bash
# Connect to database
psql -U teleai_user -d teleai_db

# Check migrations table
SELECT * FROM alembic_version;

# List all tables
\dt

# Describe table
\d table_name

# Show table sizes
\dt+

# Exit
\q
```

## 🧪 Testing Migrations

### Test Up Migration

```bash
# 1. Start fresh
docker-compose down -v
docker-compose up -d postgres

# 2. Run migration
alembic upgrade head

# 3. Verify tables
psql -U postgres -d TELEE -c "\dt"

# 4. Check data
psql -U postgres -d TELEE -c "SELECT COUNT(*) FROM user;"
```

### Test Down Migration

```bash
# 1. Downgrade
alembic downgrade base

# 2. Verify tables are gone
psql -U teleai_user -d teleai_db -c "\dt"

# 3. Re-apply
alembic upgrade head
```

## 🔐 Best Practices

1. **Always test migrations locally first**
   ```bash
   # Test up
   alembic upgrade head
   
   # Test down
   alembic downgrade -1
   
   # Test up again
   alembic upgrade head
   ```

2. **Write reversible migrations**
   - Always implement `downgrade()`
   - Test rollback works

3. **Use descriptive messages**
   ```bash
   # Good
   alembic revision -m "add user preferences table"
   
   # Bad
   alembic revision -m "update"
   ```

4. **Don't modify existing migrations**
   - Once applied in production, never edit
   - Create a new migration to fix issues

5. **Keep migrations small**
   - One logical change per migration
   - Easier to review and rollback

## 📦 Current Migration: 001_initial_schema

The initial migration (`001_initial_schema.py`) creates all 18 tables from the ERD:

✅ user, admin, permission, agent_permission_map  
✅ agent, auto_session, dialogue, transcription  
✅ crm_entity, crm_log  
✅ escalate  
✅ knowledge_base, workflow, workflow_action_log  
✅ interaction_instance, analytics_event  
✅ webhook_event, system_log  

**To apply:**
```bash
alembic upgrade head
```

**To rollback:**
```bash
alembic downgrade base
```

## 🆘 Troubleshooting

### Error: "Can't locate revision identified by 'XXXXX'"

```bash
# Check current version
alembic current

# Check history
alembic history

# Stamp current version
alembic stamp head
```

### Error: "Target database is not up to date"

```bash
# Check pending migrations
alembic heads

# Upgrade
alembic upgrade head
```

### Error: "relation 'alembic_version' does not exist"

```bash
# Initialize Alembic version table
alembic stamp base
```

### Database is out of sync

```bash
# Option 1: Force stamp (if tables exist)
alembic stamp head

# Option 2: Start fresh
docker-compose down -v
docker-compose up -d
alembic upgrade head
```

## 📚 Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🎓 Next Steps

1. **Set up your database:**
   ```bash
   docker-compose up -d
   ```

2. **Apply migrations:**
   ```bash
   pip install -r requirements.txt
   alembic upgrade head
   ```

3. **Load dummy data:**
   ```bash
   psql -U teleai_user -d teleai_db < seed_data.sql
   ```

4. **Verify:**
   ```bash
   alembic current
   psql -U teleai_user -d teleai_db -c "\dt"
   ```

Now you have a **professional, version-controlled database migration system**! 🎉

