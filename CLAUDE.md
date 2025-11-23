# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI e-commerce watch store backend with PostgreSQL database integration. The API handles authentication, products, cart management, orders, and payments.

## Development Commands

### Running the Application
```bash
# Development server with auto-reload
python main.py
# OR
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server (without reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Database Management
```bash
# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Seed products data
python app/scripts/seed_products.py

# Seed admin user
python app/scripts/seed_admin.py
```

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your configuration
```

## Architecture Overview

### Directory Structure
```
app/
├── main.py              # FastAPI application entry point
├── config.py            # Settings and configuration
├── database.py          # Database connection and session
├── dependencies.py      # FastAPI dependencies
├── auth_utils.py        # JWT authentication utilities
├── logging.py           # Logging configuration
├── models/              # SQLAlchemy ORM models
│   ├── user.py         # User model
│   ├── product.py      # Product model
│   ├── cart.py         # Cart and CartItem models
│   ├── order.py        # Order and OrderItem models
│   ├── payment.py      # Payment model
│   └── shipping.py     # Shipping address model
├── schemas/             # Pydantic request/response models
├── routers/             # API route handlers
│   ├── auth.py         # Authentication endpoints
│   ├── products.py     # Product CRUD
│   ├── cart.py         # Cart management
│   ├── orders.py       # Order management
│   ├── payments.py     # Payment processing
│   ├── webhooks.py     # Stripe webhook handling
│   └── users.py        # User profile management
├── crud/                # Database operations
├── utils/               # Helper utilities
│   ├── mailer.py       # Email notifications
│   ├── telegram.py     # Telegram bot notifications
│   └── image_utils.py  # Image processing
└── scripts/             # Database seeding scripts
```

### Key Components

#### Authentication System
- JWT-based authentication with access/refresh tokens
- Role-based authorization (user/admin)
- Token rotation on refresh
- Password hashing with bcrypt

#### Database Models
- Users with role-based access
- Products with stock management
- Cart system with user-specific items
- Order processing with multiple items per order
- Payment tracking with Stripe integration
- Shipping address management

#### API Structure
- RESTful endpoints following `/api/{resource}/` pattern
- Consistent response format: `{"status": "success/error", "data": ...}`
- Global exception handlers for HTTP and validation errors
- CORS middleware configured for frontend integration

#### External Integrations
- Stripe payments with webhook handling
- Gmail SMTP for email notifications
- Telegram bot for admin notifications
- PostgreSQL with Alembic migrations

## Configuration

### Environment Variables
Key variables (see `.env.example` for complete list):
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`/`JWT_REFRESH_SECRET_KEY`: JWT signing keys
- `STRIPE_SECRET_KEY`: Payment processing
- `SMTP_USER`/`SMTP_PASSWORD`: Email configuration
- `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID`: Telegram notifications

### Settings
The `app/config.py` uses Pydantic Settings to manage configuration with environment variable overrides and defaults.

## Database Schema

The application uses SQLAlchemy with the following relationships:
- Users → Cart (one-to-one)
- Users → Orders (one-to-many)
- Cart → CartItems (one-to-many)
- Orders → OrderItems (one-to-many)
- Products → CartItems/OrderItems (one-to-many)

## Development Notes

### Code Organization
- Models in `app/models/` define the database schema
- Schemas in `app/schemas/` define API request/response shapes
- CRUD operations in `app/crud/` handle database logic
- Routers in `app/routers/` contain the API endpoints

### Security
- All sensitive operations require authentication
- Admin-only endpoints check for `role="admin"`
- Passwords are hashed before storage
- JWT tokens have configurable expiration times

### Error Handling
- Global exception handlers return consistent error format
- Validation errors return detailed field information
- Database constraints are handled gracefully

### Testing
- Test files should be placed in a `tests/` directory (not currently present)
- Use pytest for testing framework
- Test database should be separate from development database

## Deployment

### Vercel Configuration
The application is configured for Vercel deployment with `vercel.json` pointing to `app/main.py` as the entry point.

### Production Considerations
- Set proper environment variables for production
- Use HTTPS in production
- Configure CORS origins appropriately
- Use production database with proper credentials
- Set secure JWT secrets
- Enable logging for monitoring