"""
Automatic migration runner for Vercel deployment.
Runs database migrations on application startup.
"""

import logging
import os
from typing import List
from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from alembic.runtime.environment import EnvironmentContext
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from .database import Base, get_db
from .config import settings
from .logging_config import get_logger


class MigrationRunner:
    """Handles automatic database migrations on application startup."""

    def __init__(self):
        self.logger = get_logger("migration")
        self.database_url = settings.database_url

    def check_database_connection(self) -> bool:
        """Check if database connection is working."""
        try:
            engine = create_engine(self.database_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.logger.info("Database connection successful")
            return True
        except Exception as e:
            self.logger.error(
                "Database connection failed",
                extra={
                    "error_type": "connection_error",
                    "error_details": str(e)
                },
                exc_info=True
            )
            return False

    def get_current_revision(self) -> str:
        """Get the current database revision."""
        try:
            engine = create_engine(self.database_url)
            with engine.connect() as conn:
                context = MigrationContext.configure(conn)
                return context.get_current_revision()
        except Exception as e:
            self.logger.warning(
                "Could not get current revision (likely new database)",
                extra={"error_details": str(e)}
            )
            return None

    def get_head_revision(self) -> str:
        """Get the latest available revision."""
        try:
            # Get the migrations directory
            alembic_cfg = Config("alembic.ini")
            script_dir = ScriptDirectory.from_config(alembic_cfg)
            return script_dir.get_current_head()
        except Exception as e:
            self.logger.error(
                "Could not get head revision",
                extra={"error_details": str(e)},
                exc_info=True
            )
            return None

    def run_alembic_migrations(self) -> bool:
        """Run Alembic migrations to bring database to latest version."""
        try:
            self.logger.info("Starting Alembic migration process")

            # Configure Alembic
            alembic_cfg = Config("alembic.ini")

            # Set the database URL from environment if not in alembic.ini
            if not alembic_cfg.get_main_option("sqlalchemy.url"):
                alembic_cfg.set_main_option("sqlalchemy.url", self.database_url)

            # Run the upgrade to head
            command.upgrade(alembic_cfg, "head")

            self.logger.info(
                "Alembic migrations completed successfully",
                extra={"migration_target": "head"}
            )
            return True

        except Exception as e:
            self.logger.error(
                "Alembic migration failed",
                extra={
                    "error_type": "migration_error",
                    "error_details": str(e)
                },
                exc_info=True
            )
            return False

    def create_tables_manually(self) -> bool:
        """Create tables manually if Alembic is not available or fails."""
        try:
            self.logger.info("Attempting manual table creation")

            engine = create_engine(self.database_url)

            # Create all tables
            Base.metadata.create_all(bind=engine)

            self.logger.info(
                "Manual table creation completed",
                extra={"tables_count": len(Base.metadata.tables)}
            )
            return True

        except Exception as e:
            self.logger.error(
                "Manual table creation failed",
                extra={
                    "error_type": "table_creation_error",
                    "error_details": str(e)
                },
                exc_info=True
            )
            return False

    def check_table_exists(self, table_name: str) -> bool:
        """Check if a specific table exists in the database."""
        try:
            engine = create_engine(self.database_url)
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = :table_name
                    );
                """), {"table_name": table_name})
                return result.scalar()
        except Exception as e:
            self.logger.error(
                f"Error checking if table {table_name} exists",
                extra={"error_details": str(e)}
            )
            return False

    def verify_database_schema(self) -> bool:
        """Verify that essential tables exist and are properly configured."""
        required_tables = ['users', 'products']
        existing_tables = []

        for table in required_tables:
            if self.check_table_exists(table):
                existing_tables.append(table)
            else:
                self.logger.warning(
                    f"Required table {table} does not exist"
                )

        if len(existing_tables) == len(required_tables):
            self.logger.info(
                "All required tables exist",
                extra={"tables": existing_tables}
            )
            return True
        else:
            self.logger.error(
                "Missing required tables",
                extra={
                    "required_tables": required_tables,
                    "existing_tables": existing_tables
                }
            )
            return False

    def run_migrations(self) -> bool:
        """Main method to run the migration process."""
        self.logger.info("Starting automatic migration process")

        # Step 1: Check database connection
        if not self.check_database_connection():
            self.logger.error("Cannot proceed with migrations - database connection failed")
            return False

        # Step 2: Get current and head revisions
        current_rev = self.get_current_revision()
        head_rev = self.get_head_revision()

        self.logger.info(
            "Migration status check",
            extra={
                "current_revision": current_rev,
                "head_revision": head_rev,
                "needs_migration": current_rev != head_rev
            }
        )

        # Step 3: Run migrations if needed
        if current_rev != head_rev:
            self.logger.info("Database needs migration")

            # Try Alembic first
            if self.run_alembic_migrations():
                # Verify the migration worked
                if self.verify_database_schema():
                    self.logger.info("Migration completed and verified successfully")
                    return True
                else:
                    self.logger.error("Migration completed but verification failed")
                    return False
            else:
                self.logger.warning("Alembic failed, trying manual table creation")
                if self.create_tables_manually():
                    if self.verify_database_schema():
                        self.logger.info("Manual table creation completed and verified")
                        return True
                    else:
                        self.logger.error("Manual table creation completed but verification failed")
                        return False
                else:
                    self.logger.error("Both Alembic and manual table creation failed")
                    return False
        else:
            # No migration needed, just verify schema
            if self.verify_database_schema():
                self.logger.info("No migration needed, database schema is up to date")
                return True
            else:
                self.logger.warning("No migration needed but schema verification failed, attempting repair")
                if self.create_tables_manually():
                    return self.verify_database_schema()
                return False


# Global migration runner instance
migration_runner = None


async def run_startup_migrations():
    """Run migrations on application startup."""
    global migration_runner

    try:
        migration_runner = MigrationRunner()

        # Run migrations
        success = migration_runner.run_migrations()

        if success:
            logger = get_logger("migration")
            logger.info("Startup migrations completed successfully")
            return True
        else:
            logger = get_logger("migration")
            logger.error("Startup migrations failed")
            return False

    except Exception as e:
        logger = get_logger("migration")
        logger.error(
            "Critical error during startup migrations",
            extra={
                "error_type": "critical_migration_error",
                "error_details": str(e)
            },
            exc_info=True
        )
        return False


def run_startup_migrations_sync():
    """Synchronous version for non-async contexts."""
    global migration_runner

    try:
        migration_runner = MigrationRunner()

        # Run migrations
        success = migration_runner.run_migrations()

        if success:
            logger = get_logger("migration")
            logger.info("Startup migrations completed successfully")
            return True
        else:
            logger = get_logger("migration")
            logger.error("Startup migrations failed")
            return False

    except Exception as e:
        logger = get_logger("migration")
        logger.error(
            "Critical error during startup migrations",
            extra={
                "error_type": "critical_migration_error",
                "error_details": str(e)
            },
            exc_info=True
        )
        return False