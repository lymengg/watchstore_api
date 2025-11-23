"""
Database seeder for automatic data population on first deployment.
Runs after migrations to populate initial data.
"""

import logging
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import text, create_engine

from .database import get_db
from .models import User
from .logging_config import get_logger
from .crud import get_user_by_username
from .auth_utils import hash_password
from .config import settings


class DatabaseSeeder:
    """Handles automatic database seeding for initial data."""

    def __init__(self):
        self.logger = get_logger("database_seeder")

    def seed_admin_user(self) -> bool:
        """Create default admin user if it doesn't exist."""
        try:
            # Get database session
            from .database import engine
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()

            try:
                # Check if admin user already exists
                admin_username = "admin"
                existing_admin = get_user_by_username(db, admin_username)

                if existing_admin:
                    self.logger.info(
                        "Admin user already exists",
                        extra={"username": admin_username}
                    )
                    return True

                # Create admin user
                admin_user = User(
                    username=admin_username,
                    email="admin@watchstore.com",
                    phone_number="0000000000",  # Default phone number
                    hashed_password=hash_password("admin123"),  # Default password - should be changed
                    role="admin"
                )

                db.add(admin_user)
                db.commit()

                self.logger.info(
                    "Admin user created successfully",
                    extra={
                        "username": admin_user.username,
                        "email": admin_user.email,
                        "role": admin_user.role
                    }
                )

                # Log security warning
                self.logger.warning(
                    "Default admin credentials created - please change immediately",
                    extra={
                        "security_warning": "default_credentials",
                        "username": admin_username,
                        "default_password": "admin123"
                    }
                )

                return True

            except Exception as e:
                db.rollback()
                self.logger.error(
                    "Failed to create admin user",
                    extra={
                        "error_type": "admin_creation_error",
                        "error_details": str(e)
                    },
                    exc_info=True
                )
                return False
            finally:
                db.close()

        except Exception as e:
            self.logger.error(
                "Failed to initialize database seeder",
                extra={"error_details": str(e)},
                exc_info=True
            )
            return False

    def seed_sample_data(self) -> bool:
        """Seed sample data for testing (optional - only in development)."""
        try:
            # Only seed sample data in development
            from .config import settings
            if settings.debug:
                self.logger.info("Skipping sample data seeding in production")
                return True

            # Get database session
            from .database import engine
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()

            try:
                # Check if sample products already exist
                result = db.execute(text("SELECT COUNT(*) FROM products"))
                product_count = result.scalar()

                if product_count > 0:
                    self.logger.info(
                        "Sample products already exist",
                        extra={"product_count": product_count}
                    )
                    return True

                # Insert sample products
                sample_products = [
                    {
                        "name": "Rolex Submariner",
                        "brand": "Rolex",
                        "description": "Classic dive watch with automatic movement",
                        "price": 8500.00,
                        "stock": 10
                    },
                    {
                        "name": "Omega Speedmaster",
                        "brand": "Omega",
                        "description": "Legendary chronograph watch",
                        "price": 4500.00,
                        "stock": 15
                    },
                    {
                        "name": "Tag Heuer Carrera",
                        "brand": "Tag Heuer",
                        "description": "Sporty chronograph for racing enthusiasts",
                        "price": 2200.00,
                        "stock": 25
                    },
                    {
                        "name": "Seiko Presage",
                        "brand": "Seiko",
                        "description": "Elegant automatic watch with Japanese craftsmanship",
                        "price": 550.00,
                        "stock": 30
                    },
                    {
                        "name": "Citizen Eco-Drive",
                        "brand": "Citizen",
                        "description": "Solar-powered watch with modern design",
                        "price": 320.00,
                        "stock": 40
                    }
                ]

                for product_data in sample_products:
                    db.execute(text("""
                        INSERT INTO products (name, brand, description, price, stock)
                        VALUES (:name, :brand, :description, :price, :stock)
                    """), product_data)

                db.commit()

                self.logger.info(
                    "Sample products created successfully",
                    extra={"product_count": len(sample_products)}
                )

                return True

            except Exception as e:
                db.rollback()
                self.logger.error(
                    "Failed to create sample products",
                    extra={
                        "error_type": "sample_products_error",
                        "error_details": str(e)
                    },
                    exc_info=True
                )
                return False
            finally:
                db.close()

        except Exception as e:
            self.logger.error(
                "Failed to initialize sample data seeder",
                extra={"error_details": str(e)},
                exc_info=True
            )
            return False

    def verify_seeding(self) -> bool:
        """Verify that seeding was successful."""
        try:
            from .database import engine
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()

            try:
                # Check admin user
                admin_user = get_user_by_username(db, "admin")
                admin_exists = admin_user is not None

                # Check product count
                result = db.execute(text("SELECT COUNT(*) FROM products"))
                product_count = result.scalar()

                self.logger.info(
                    "Database seeding verification",
                    extra={
                        "admin_user_exists": admin_exists,
                        "product_count": product_count
                    }
                )

                return admin_exists and product_count >= 0  # Products can be 0 in production

            except Exception as e:
                self.logger.error(
                    "Failed to verify seeding",
                    extra={"error_details": str(e)},
                    exc_info=True
                )
                return False
            finally:
                db.close()

        except Exception as e:
            self.logger.error(
                "Failed to initialize verification",
                extra={"error_details": str(e)},
                exc_info=True
            )
            return False

    def run_seeding(self) -> bool:
        """Run the complete seeding process."""
        self.logger.info("Starting database seeding process")

        try:
            # Step 1: Seed admin user
            admin_success = self.seed_admin_user()
            if not admin_success:
                self.logger.error("Failed to seed admin user")
                return False

            # Step 2: Seed sample data (development only)
            sample_success = self.seed_sample_data()
            # Continue even if sample data fails in production

            # Step 3: Verify seeding
            verification_success = self.verify_seeding()

            if admin_success and verification_success:
                self.logger.info("Database seeding completed successfully")
                return True
            else:
                self.logger.error("Database seeding completed with errors")
                return False

        except Exception as e:
            self.logger.error(
                "Critical error during database seeding",
                extra={
                    "error_type": "critical_seeding_error",
                    "error_details": str(e)
                },
                exc_info=True
            )
            return False


def run_startup_seeding() -> bool:
    """Run seeding on application startup."""
    try:
        seeder = DatabaseSeeder()
        return seeder.run_seeding()
    except Exception as e:
        logger = get_logger("seeding")
        logger.error(
            "Failed to run startup seeding",
            extra={"error_details": str(e)},
            exc_info=True
        )
        return False