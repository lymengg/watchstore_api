# FastAPI Project Structure - Best Practices Implementation

This document outlines the new FastAPI project structure that follows industry best practices while maintaining full Vercel deployment compatibility.

## 🏗️ Project Structure

```
watchstore_api/
├── alembic/                           # Database migrations
├── app/                               # Main application package
│   ├── __init__.py                   # App initialization
│   ├── main.py                       # FastAPI app factory
│   ├── config.py                     # Settings and configuration
│   ├── database.py                   # Database connection and session
│   ├── dependencies.py               # FastAPI dependencies (legacy)
│   ├── exceptions.py                 # Custom exception handlers
│   ├── middleware.py                 # Custom middleware
│   ├── core/                         # Core functionality
│   │   ├── __init__.py
│   │   ├── auth.py                   # Authentication utilities
│   │   ├── logging.py                # Logging configuration
│   │   └── security.py               # Security helpers
│   ├── models/                       # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   └── shipping.py
│   ├── schemas/                      # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── common.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   └── payment.py
│   ├── api/                          # API routes
│   │   ├── __init__.py
│   │   ├── deps.py                   # API dependencies
│   │   └── v1/                       # API versioning
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── products.py
│   │       ├── cart.py
│   │       ├── orders.py
│   │       └── payments.py
│   ├── services/                     # Business logic layer
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── product_service.py
│   │   ├── order_service.py
│   │   └── payment_service.py
│   ├── utils/                        # Utility functions
│   │   ├── __init__.py
│   │   ├── email.py
│   │   ├── telegram.py
│   │   └── image.py
│   ├── crud/                         # Database operations (legacy)
│   ├── routers/                      # Legacy routers (being migrated)
│   ├── scripts/                      # Database seeding scripts
│   └── logging_config.py             # Legacy logging (being migrated)
├── scripts/                          # Utility scripts
│   ├── seed_data.py
│   └── create_admin.py
├── tests/                            # Test files
├── .env.example                      # Environment variables template
├── requirements.txt                  # Python dependencies
├── requirements-dev.txt              # Development dependencies
├── alembic.ini                       # Alembic configuration
├── api.py                            # Vercel entry point ⭐
├── main.py                           # Local development entry point
├── dev.py                            # Simple development server
└── README.md                         # Project documentation
```

## 🚀 Running the Application

### Development

#### Option 1: Using uvicorn (Recommended)
```bash
# Using the main entry point
python main.py

# Or using the simple dev app
python dev.py

# Or using uvicorn directly
uvicorn app.main:create_app --reload --host 0.0.0.0 --port 8000
```

#### Option 2: Using FastAPI CLI
```bash
fastapi dev dev.py
```

### Production (Vercel)

The `api.py` file serves as the Vercel entry point and automatically creates the FastAPI app using the factory pattern.

## 🔧 Key Improvements

### 1. **App Factory Pattern**
- `app/main.py` contains a `create_app()` function that configures and returns the FastAPI app
- Allows for different configurations for development and production
- Easier testing and dependency injection

### 2. **API Versioning**
- All API routes are now under `/api/v1/` prefix
- Easy to add new versions without breaking existing clients
- Clean separation of API versions in `app/api/v1/`

### 3. **Service Layer**
- Business logic is separated into service classes in `app/services/`
- Improves code organization and testability
- Reduces coupling between API endpoints and database operations

### 4. **Enhanced Error Handling**
- Centralized exception handlers in `app/exceptions.py`
- Custom exception classes for different error types
- Consistent error response format across all endpoints

### 5. **Improved Configuration**
- Better organized settings in `app/config.py`
- Environment-specific configurations
- Type-safe configuration with Pydantic

### 6. **Middleware Structure**
- Custom middleware for logging, security headers, and rate limiting
- Centralized middleware configuration in `app/middleware.py`

### 7. **Core Functionality**
- Authentication utilities in `app/core/auth.py`
- Logging configuration in `app/core/logging.py`
- Security helpers for production deployment

## 🔄 Migration Status

### ✅ Completed
- [x] App factory pattern implementation
- [x] API versioning structure
- [x] Enhanced configuration management
- [x] Core authentication utilities
- [x] Exception handling system
- [x] Middleware infrastructure
- [x] Service layer foundation
- [x] Development server setup

### 🚧 In Progress
- [ ] Complete migration of all API endpoints to new structure
- [ ] Implement remaining service classes
- [ ] Add comprehensive test suite
- [ ] Update Pydantic v2 compatibility

### 📋 Planned
- [ ] API rate limiting
- [ ] Request/response validation middleware
- [ ] Performance monitoring
- [ ] API documentation generation

## 🛠 Development Guidelines

### Adding New Endpoints

1. **Create Schema**: Define request/response models in `app/schemas/`
2. **Implement Service**: Add business logic in `app/services/`
3. **Create Endpoint**: Add route in appropriate `app/api/v1/` file
4. **Add Tests**: Create test files in `tests/`

### Configuration

- Use environment variables for all sensitive data
- Development config in `.env` file
- Production config via Vercel environment variables

### Database Operations

- Use service classes for complex business logic
- Use CRUD functions for simple database operations
- Always use dependency injection for database sessions

## 🔒 Security Features

- JWT-based authentication with access/refresh tokens
- Role-based authorization
- Rate limiting capabilities
- Security headers middleware
- Input validation and sanitization
- SQL injection prevention through SQLAlchemy ORM

## 📝 API Documentation

Once the application is running:
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI spec: `http://localhost:8000/openapi.json`

## 🚀 Vercel Deployment

The project maintains full Vercel compatibility:

1. **Entry Point**: `api.py` creates the FastAPI app for Vercel
2. **Environment Variables**: Configured through Vercel dashboard
3. **Static Files**: Handled by Vercel's edge network
4. **Database**: PostgreSQL connection via environment variables
5. **Logging**: Structured JSON logs for Vercel's logging system

## 🧪 Testing

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/
```

## 📈 Performance Considerations

- Database connection pooling configured
- Async/await patterns where applicable
- Efficient query optimization through SQLAlchemy
- Response caching capabilities
- CDN-friendly static file handling

## 🔄 Backward Compatibility

- Legacy routes maintained in `app/routers/`
- Gradual migration approach
- Existing database schema unchanged
- Old authentication patterns supported during transition