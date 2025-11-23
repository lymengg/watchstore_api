# Watchstore API - Refactored

This is the refactored FastAPI backend for the Watchstore e-commerce application, now following FastAPI best practices.

## New Project Structure

```
watchstore_api/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI app instance
│   ├── config.py                 # Configuration with environment variables
│   ├── database.py               # Database configuration
│   ├── dependencies.py           # FastAPI dependencies
│   ├── auth_utils.py             # Authentication utilities
│   ├── logging.py                # Logging configuration
│   ├── models/                   # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   ├── shipping.py
│   │   └── payment.py
│   ├── schemas/                  # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   ├── shipping.py
│   │   └── payment.py
│   ├── crud/                     # Database operations
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   └── payment.py
│   ├── routers/                  # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── products.py
│   │   ├── cart.py
│   │   ├── orders.py
│   │   ├── payments.py
│   │   └── webhooks.py
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   └── image_utils.py
│   └── scripts/                  # Database seeding scripts
│       ├── __init__.py
│       ├── seed_admin.py
│       └── seed_products.py
├── alembic/                      # Database migrations
├── main.py                       # Application entry point
├── .env.example                  # Environment variables example
├── requirements_new.txt          # Updated Python dependencies
└── alembic.ini                   # Alembic configuration

```

## Key Improvements

### 1. **Environment Configuration**
- Added `.env` support with `pydantic-settings`
- All configuration centralized in `app/config.py`
- Database URLs and JWT secrets moved to environment variables

### 2. **Organized Code Structure**
- Models split into separate files by domain
- Schemas organized by feature with consistent Pydantic configuration
- CRUD operations modularized by entity
- Better separation of concerns

### 3. **Enhanced Configuration**
- Settings class with type hints and validation
- Support for different environments (dev, prod, test)
- CORS configuration from environment

### 4. **Logging System**
- Structured logging configuration in `app/logging.py`
- Different log levels for different components
- Optional file logging for production

### 5. **Modern Pydantic Usage**
- All models use `model_config = {"from_attributes": True}` instead of deprecated `Config`
- Consistent schema organization

## Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your actual values:
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/watchstore_db
   JWT_SECRET_KEY=your_secret_key_here
   JWT_REFRESH_SECRET_KEY=your_refresh_secret_key_here
   ```

3. Install the updated dependencies:
   ```bash
   pip install -r requirements_new.txt
   ```

## Running the Application

1. **Development mode:**
   ```bash
   python main.py
   ```

2. **Using uvicorn directly:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Production mode:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## Database Migrations

The Alembic configuration has been updated to work with the new structure:

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Configuration Options

All configuration is now handled through environment variables or the `app/config.py` file:

- `DATABASE_URL`: Database connection string
- `JWT_SECRET_KEY`: Secret for access tokens
- `JWT_REFRESH_SECRET_KEY`: Secret for refresh tokens
- `JWT_ALGORITHM`: JWT algorithm (default: HS256)
- `JWT_ACCESS_EXPIRE_MINUTES`: Access token expiry (default: 30)
- `JWT_REFRESH_EXPIRE_MINUTES`: Refresh token expiry (default: 10080)
- `DEBUG`: Enable debug mode (default: True)
- `HOST`: Host to bind to (default: 0.0.0.0)
- `PORT`: Port to bind to (default: 8000)
- `ALLOWED_ORIGINS`: CORS allowed origins (default: ["*"])
- `LOG_LEVEL`: Logging level (default: INFO)

## Migration Guide

If you're migrating from the old structure:

1. Update any direct imports from the old files to use the new `app.*` imports
2. Update your requirements with `requirements_new.txt`
3. Create a `.env` file based on `.env.example`
4. Test that all routes still work as expected

The API endpoints and functionality remain exactly the same - only the internal organization has changed.