# 🚀 FastAPI Single Entry Point Architecture

## **Best Practice Implementation**

Your FastAPI application now follows industry best practices with **one unified entry point** that works seamlessly for both development and Vercel production deployment.

## 📁 **Simplified Project Structure**

```
watchstore_api/
├── api.py                      # ⭐ Single Entry Point - Development & Vercel
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
├── alembic.ini                 # Database migrations config
├── alembic/                    # Database migrations
├── app/                        # Main application package
│   ├── main.py                 # FastAPI app factory
│   ├── config.py               # Environment-aware settings
│   ├── database.py             # Database connection
│   ├── core/                   # Core functionality
│   │   ├── auth.py             # Authentication utilities
│   │   ├── logging.py          # Logging configuration
│   │   └── __init__.py
│   ├── api/                    # API routes
│   │   ├── v1/                 # API version 1
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── users.py        # User endpoints
│   │   │   ├── products.py     # Product endpoints
│   │   │   ├── cart.py         # Cart endpoints
│   │   │   ├── orders.py       # Order endpoints
│   │   │   ├── payments.py     # Payment endpoints
│   │   │   └── __init__.py
│   │   └── deps.py             # API dependencies
│   ├── models/                 # Database models
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business logic
│   ├── exceptions.py           # Error handling
│   ├── middleware.py           # Custom middleware
│   └── routers/                # Legacy routers (preserved)
├── legacy/                     # Legacy files moved here
└── docs/                       # Documentation
```

## 🎯 **How It Works**

### **Single File, Multiple Modes**

The `api.py` file automatically detects the environment and behaves accordingly:

```python
# Development: python api.py
# Vercel Production: automatic import
```

### **Environment Detection**

```bash
# Development Mode (Default)
python api.py
→ Uses development settings
→ Enables hot reload and debugging
→ Local database connections

# Production Mode (Vercel)
# Vercel automatically sets ENVIRONMENT=production
→ Uses production settings
→ Optimized for performance
→ Production database and security
```

## 🚀 **Running Your Application**

### **Development**
```bash
# Single command - that's it!
python api.py
```

### **Production (Vercel)**
No changes needed! Vercel automatically uses the same `api.py` file.

### **Environment Variables**

Create a `.env` file for development:

```bash
# Development Environment
ENVIRONMENT=development
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/watchstore_dev
HOST=127.0.0.1
PORT=8000
```

Set these in Vercel dashboard for production:

```bash
# Production Environment
ENVIRONMENT=production
DATABASE_URL=your_production_database_url
DEBUG=false
```

## 🔧 **Environment-Specific Features**

### **Development Mode** (`ENVIRONMENT=development`)
- ✅ **Hot Reload**: Automatic code changes
- ✅ **Debug Mode**: Detailed error messages
- ✅ **Local Database**: PostgreSQL or SQLite
- ✅ **CORS**: Local development URLs enabled
- ✅ **Verbose Logging**: Debug level logs
- ✅ **Longer JWT Tokens**: 30 min access, 7 days refresh

### **Production Mode** (`ENVIRONMENT=production`)
- ✅ **Optimized**: Performance tuned
- ✅ **Secure**: Production security settings
- ✅ **Structured Logs**: JSON format for monitoring
- ✅ **Production Database**: Your production PostgreSQL
- ✅ **Restricted CORS**: Only your frontend domains
- ✅ **Shorter JWT Tokens**: 15 min access, 1 day refresh
- ✅ **Security Headers**: HSTS, XSS protection, etc.

## 📋 **Environment Variables Reference**

| Variable | Development | Production | Description |
|----------|-------------|------------|-------------|
| `ENVIRONMENT` | `development` | `production` | Environment detection |
| `DATABASE_URL` | Local DB | Production DB | PostgreSQL connection |
| `HOST` | `127.0.0.1` | `0.0.0.0` | Server binding |
| `PORT` | `8000` | Vercel sets | Server port |
| `DEBUG` | `true` | `false` | Debug mode |
| `JWT_SECRET_KEY` | Dev key | Production key | JWT signing |
| `STRIPE_SECRET_KEY` | Test key | Live key | Payment processing |

## 🔒 **Security Features**

### **Automatic Security Based on Environment**

```python
# Development: Permissive settings
- Localhost only
- Debug information shown
- Long-lived tokens
- Verbose logging

# Production: Secure settings
- HTTPS enforced
- Minimal error exposure
- Short-lived tokens
- Structured security logs
- Rate limiting enabled
```

## 🌐 **API Endpoints**

All endpoints now use versioned URLs:

```bash
# Authentication
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
GET  /api/v1/auth/me
POST /api/v1/auth/change-password

# Users
GET  /api/v1/users/me

# Other endpoints follow the same pattern
/api/v1/products/...
/api/v1/cart/...
/api/v1/orders/...
/api/v1/payments/...
```

## 🧪 **Testing Different Environments**

```bash
# Test development mode
python -c "import api; print(api.settings.ENVIRONMENT)"

# Test production mode
ENVIRONMENT=production python -c "import api; print(api.settings.ENVIRONMENT)"

# Run development server
python api.py
```

## 📝 **Benefits of Single Entry Point**

### **1. Simplicity**
- **One file to understand** - No confusion about which entry point to use
- **Less code duplication** - Single source of truth
- **Easier debugging** - Single import path

### **2. Environment Flexibility**
- **Automatic detection** - No manual switching required
- **Consistent behavior** - Same app, different configurations
- **Easy deployment** - No special deployment scripts

### **3. Maintenance**
- **Single point of change** - Modify startup logic in one place
- **Unified error handling** - Consistent across environments
- **Simplified CI/CD** - Same entry point for testing and production

### **4. FastAPI Best Practices**
- **Follows official patterns** - Recommended by FastAPI creators
- **Pydantic configuration** - Type-safe settings
- **Dependency injection** - Clean architecture
- **Middleware support** - Production-ready middleware stack

## 🔄 **Migration from Multiple Files**

**Before** ❌
```bash
# Multiple files - confusing
python main.py      # Which one?
python dev.py        # When to use?
api.py              # Vercel only?
```

**After** ✅
```bash
# Single file - simple
python api.py       # Always works
# Vercel uses the same file automatically
```

## 🎯 **Getting Started**

### **1. Setup Development**
```bash
# Copy environment template
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Run development server
python api.py
```

### **2. Deploy to Vercel**
```bash
# No changes needed!
# Vercel automatically uses api.py
# Set environment variables in Vercel dashboard
```

### **3. Update Frontend**
```javascript
// Update API base URL
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://your-api.vercel.app/api/v1'
  : 'http://localhost:8000/api/v1';
```

## 🚨 **Important Notes**

1. **Environment Variables**: Always use environment variables for sensitive data
2. **Database**: Ensure your production database is accessible from Vercel
3. **CORS**: Update production CORS origins with your actual frontend domain
4. **JWT Keys**: Use different keys for development and production
5. **Testing**: Test both environments before deploying

Your FastAPI application now follows **industry best practices** with a **clean, maintainable, and production-ready** architecture! 🎉