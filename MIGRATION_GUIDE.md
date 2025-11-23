# Automatic Migration System for Vercel

This guide explains the automatic migration and seeding system designed specifically for Vercel deployments where manual migration commands cannot be executed.

## Overview

The application includes a comprehensive automatic migration system that:
- Runs database migrations on application startup
- Seeds initial data (admin user, sample products)
- Provides health check endpoints for monitoring
- Handles migration failures gracefully
- Logs all migration activities

## How It Works

### 1. Application Startup Sequence

```
Application Start
       ↓
   Setup Logging
       ↓
   Run Migrations
       ↓
   Run Seeding
       ↓
   Start FastAPI App
```

### 2. Migration Process

1. **Database Connection Check**: Verifies database connectivity
2. **Current Revision Check**: Determines the current migration state
3. **Migration Execution**: Runs Alembic migrations or creates tables manually
4. **Schema Verification**: Confirms required tables exist
5. **Error Handling**: Logs errors and continues if possible

### 3. Seeding Process

1. **Admin User Creation**: Creates default admin user if not exists
2. **Sample Data**: Adds sample products (development only)
3. **Verification**: Confirms seeding was successful

## Files and Components

### Core Files

- **`app/migration_runner.py`**: Main migration logic and Alembic integration
- **`app/database_seeder.py`**: Data seeding functionality
- **`app/main.py`**: Integration with FastAPI startup
- **`alembic/`**: Alembic migration files and configuration

### Key Classes

#### `MigrationRunner`
- Handles database connection verification
- Runs Alembic migrations automatically
- Falls back to manual table creation
- Provides detailed logging

#### `DatabaseSeeder`
- Creates default admin user
- Seeds sample products in development
- Verifies seeding success

## Environment Variables

Required environment variables for migrations:

```bash
# Database connection (required)
DATABASE_URL=postgresql+psycopg2://user:password@host:port/database

# Optional: Environment detection
VERCEL_ENV=production
```

## Migration Scripts

### Creating New Migrations

1. **Local Development**:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

2. **Migration File Structure**:
   ```python
   """Description of changes

   Revision ID: abc123def456
   Revises: previous_revision_id
   Create Date: 2025-01-21 10:30:00.000000

   """
   from alembic import op
   import sqlalchemy as sa

   def upgrade():
       # Upgrade logic here
       pass

   def downgrade():
       # Downgrade logic here
       pass
   ```

### Migration Execution

#### Automatic (Production/Vercel)
- Migrations run automatically on application startup
- No manual intervention required
- Fully logged and monitored

#### Manual (Development)
```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade +1

# Downgrade
alembic downgrade -1

# Check current status
alembic current
```

## Default Admin User

The system automatically creates a default admin user:

- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@watchstore.com`

⚠️ **Security Warning**: Change the default admin password immediately after first deployment!

## Monitoring and Debugging

### Health Endpoints

#### `/api/health`
Basic health check with migration status:
```json
{
  "status": "ok",
  "timestamp": "2025-01-21T10:30:00Z",
  "migration_status": "success"
}
```

#### `/api/db-status`
Detailed database status:
```json
{
  "status": "ok",
  "database_connected": true,
  "tables_present": ["users", "products"],
  "migration_info": {
    "current_revision": "abc123def456",
    "head_revision": "abc123def456",
    "needs_migration": false
  },
  "migration_success": true
}
```

### Log Monitoring

#### Migration Logs
```json
{
  "timestamp": "2025-01-21T10:30:00Z",
  "level": "INFO",
  "message": "Starting automatic migration process",
  "application": "watchstore-api",
  "environment": "production"
}
```

#### Database Connection Logs
```json
{
  "timestamp": "2025-01-21T10:30:01Z",
  "level": "INFO",
  "message": "Database connection successful",
  "application": "watchstore-api"
}
```

#### Migration Success Logs
```json
{
  "timestamp": "2025-01-21T10:30:05Z",
  "level": "INFO",
  "message": "Alembic migrations completed successfully",
  "application": "watchstore-api",
  "migration_target": "head"
}
```

## Error Handling

### Migration Failures

The system handles migration failures gracefully:

1. **Connection Errors**: Logged, application continues with limited functionality
2. **Alembic Failures**: Falls back to manual table creation
3. **Constraint Violations**: Logged and handled appropriately
4. **Critical Errors**: Logged extensively, application attempts to continue

### Common Issues and Solutions

#### Database Connection Issues
```json
{
  "level": "ERROR",
  "message": "Database connection failed",
  "error_type": "connection_error",
  "error_details": "Connection refused"
}
```
**Solution**: Check DATABASE_URL and database connectivity

#### Migration Conflicts
```json
{
  "level": "ERROR",
  "message": "Alembic migration failed",
  "error_type": "migration_error",
  "error_details": "Relation already exists"
}
```
**Solution**: Manual database inspection or fresh deployment

#### Seeding Failures
```json
{
  "level": "WARNING",
  "message": "Database seeding encountered issues",
  "error_type": "seeding_error"
}
```
**Solution**: Check database permissions and constraints

## Best Practices

### 1. Migration Development
- Always test migrations locally before deployment
- Use descriptive migration names
- Include both upgrade and downgrade logic
- Review auto-generated migrations

### 2. Production Deployment
- Monitor deployment logs closely
- Verify database status after deployment
- Change default admin credentials immediately
- Set up monitoring for the `/api/db-status` endpoint

### 3. Security
- Never commit sensitive database credentials
- Change default admin password
- Use environment-specific configurations
- Monitor for unusual database activities

### 4. Performance
- Keep migrations small and focused
- Test migration performance with large datasets
- Monitor migration execution times
- Use indexes appropriately

## Troubleshooting

### Quick Diagnostics

1. **Check Application Logs**: Look for migration-related entries
2. **Visit `/api/db-status`**: Verify database connectivity and table status
3. **Check Environment Variables**: Ensure DATABASE_URL is correct
4. **Review Migration Files**: Verify migration logic is sound

### Common Scenarios

#### Fresh Deployment
1. Application starts → Migrations run → Tables created → Admin user created
2. Expected: Clean database with admin user and sample data

#### Existing Database
1. Application starts → Migration check → No migration needed → Seeding runs
2. Expected: Existing data preserved, admin user created if missing

#### Migration Update
1. Application starts → Migration check → New migrations applied
2. Expected: Database schema updated, existing data preserved

## Integration with CI/CD

### Vercel Integration

The migration system is designed to work seamlessly with Vercel:

1. **Automatic Execution**: Runs on every deployment
2. **Idempotent**: Safe to run multiple times
3. **Zero Downtime**: Non-disruptive to existing data
4. **Monitoring**: Full logging for debugging

### Deployment Pipeline

```yaml
# Example CI/CD pipeline
stages:
  - test: Run tests against migrated database
  - build: Build application
  - deploy: Deploy to Vercel
    post-deploy:
      - check /api/health
      - check /api/db-status
      - verify admin user creation
```

## Advanced Configuration

### Custom Migration Logic

For complex migrations, customize the `MigrationRunner`:

```python
def run_custom_migrations(self) -> bool:
    """Run custom business logic migrations."""
    # Add your custom migration logic here
    return True
```

### Custom Seeding Logic

Extend the `DatabaseSeeder` for additional data:

```python
def seed_custom_data(self) -> bool:
    """Seed custom application data."""
    # Add your custom seeding logic here
    return True
```

This migration system ensures that your FastAPI application automatically handles database schema management on Vercel without requiring manual intervention.