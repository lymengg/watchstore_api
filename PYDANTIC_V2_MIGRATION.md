# Pydantic v2 Migration Guide

This document outlines the Pydantic v2 compatibility fixes applied to resolve warnings and ensure smooth operation.

## 🎯 **Problem Identified**

The following warning appeared in production logs:
```
/var/task/_vendor/pydantic/_internal/_config.py:383: UserWarning: Valid config keys have changed in V2:
* 'schema_extra' has been renamed to 'json_schema_extra'
```

## ✅ **Changes Made**

### **1. Updated Pydantic Schema Configuration**

**File**: `app/schemas/auth.py`

**Before** (Pydantic v1 syntax):
```python
class Config:
    schema_extra = {
        "example": {
            "username": "johndoe",
            "email": "john@example.com"
        }
    }
```

**After** (Pydantic v2 syntax):
```python
class Config:
    json_schema_extra = {
        "example": {
            "username": "johndoe",
            "email": "john@example.com"
        }
    }
```

### **2. Schemas Updated**

Fixed the following schema classes in `app/schemas/auth.py`:

- ✅ `UserCreate`
- ✅ `UserUpdate`
- ✅ `UserResponse`
- ✅ `PasswordChange`
- ✅ `Token`
- ✅ `TokenRefresh`

### **3. API Endpoint Structure Updated**

**Before** (with `/v1`):
```python
# Routes had /api/v1/ prefix
POST /api/v1/auth/login
POST /api/v1/auth/register
GET  /api/v1/users/me
```

**After** (clean URLs):
```python
# Routes now use /api/ prefix only
POST /api/auth/login
POST /api/auth/register
GET  /api/users/me
```

### **4. OpenAPI Documentation Updated**

**Before**:
```python
openapi_url=f"/api/v1/openapi.json"
```

**After**:
```python
openapi_url="/openapi.json"
```

## 🔄 **API Endpoint Changes Summary**

| Category | Before | After |
|----------|--------|-------|
| Authentication | `/api/v1/auth/*` | `/api/auth/*` |
| Users | `/api/v1/users/*` | `/api/users/*` |
| Products | `/api/v1/products/*` | `/api/products/*` |
| Cart | `/api/v1/cart/*` | `/api/cart/*` |
| Orders | `/api/v1/orders/*` | `/api/orders/*` |
| Payments | `/api/v1/payments/*` | `/api/payments/*` |

## 📋 **Testing Results**

### **Pydantic Warning Resolution**
```bash
# Before: Warning appeared
python -c "import api"
→ Warning: 'schema_extra' has been renamed to 'json_schema_extra'

# After: No warnings
python -c "import api"
→ SUCCESS: No Pydantic v2 warnings!
```

### **API Structure Verification**
```bash
# All routes confirmed to work without /v1
GET  /api/auth/me
POST /api/auth/login
POST /api/products/
GET  /api/cart/
GET  /api/orders/
GET  /api/payments/
```

## 🚀 **Impact on Frontend**

### **Required Frontend Changes**

If your frontend was using `/api/v1/` paths, update them to remove `/v1`:

**Before**:
```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

**After**:
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

**Example endpoint updates:**
```javascript
// Authentication
fetch(`${API_BASE_URL}/auth/login`)     // Before: /api/v1/auth/login
fetch(`${API_BASE_URL}/users/me`)       // Before: /api/v1/users/me
fetch(`${API_BASE_URL}/products/`)      // Before: /api/v1/products/
```

## 🔧 **Configuration Updates**

### **Updated Configuration**

**File**: `app/config.py`
```python
# Before
API_V1_STR: str = "/api/v1"

# After
API_V1_STR: str = "/api"  # Updated to remove /v1
```

### **OpenAPI Documentation**

- **Interactive Docs**: `http://localhost:8000/docs`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`
- **ReDoc**: `http://localhost:8000/redoc`

## ✅ **Verification Checklist**

- [x] No more Pydantic v2 warnings in logs
- [x] All schemas use `json_schema_extra` instead of `schema_extra`
- [x] API endpoints work without `/v1` prefix
- [x] OpenAPI documentation accessible at correct URLs
- [x] Frontend documentation updated
- [x] Application loads without errors

## 📚 **Additional Resources**

- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [FastAPI with Pydantic v2](https://fastapi.tiangolo.com/tutorial/pydantic-types/)
- [OpenAPI Specification](https://swagger.io/specification/)

## 🎉 **Benefits Achieved**

1. **Eliminated Warnings**: No more Pydantic v2 compatibility warnings
2. **Cleaner URLs**: Simpler API paths without unnecessary versioning
3. **Better Documentation**: Updated OpenAPI specs
4. **Future-Proof**: Compatible with latest Pydantic v2 features
5. **Improved UX**: Cleaner, more intuitive API endpoints

Your FastAPI application is now fully compatible with Pydantic v2 and has cleaner API endpoints! 🚀