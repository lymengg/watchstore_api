# CORS Debugging Guide for Admin Endpoints

## Problem Analysis
The CORS error with `PATCH /api/orders/admin/orders/2/status` occurs because:

1. **Authentication Required**: Admin endpoints require JWT authentication
2. **Preflight Request**: PATCH requests trigger OPTIONS preflight
3. **Missing Headers**: Insufficient CORS configuration for admin operations

## Fixed Configuration

### 1. Enhanced CORS Settings
```python
# In app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "X-Requested-With",
        "X-Forwarded-For",
        "X-Real-IP",
        "Origin",
        "User-Agent",
        "Cache-Control",
        "Pragma"
    ],
    expose_headers=["X-Request-ID", "X-Process-Time"],
    max_age=600,  # Cache preflight for 10 minutes
)
```

### 2. Admin Endpoint Requirements
The admin endpoint requires:
- **JWT Bearer Token** in Authorization header
- **Admin role** for the authenticated user
- **Valid Order ID** in the URL
- **Valid Status** in request body

## Testing the Fix

### Test Request Format
```bash
# First, get admin JWT token
curl -X POST "https://watchstore-api-taupe.vercel.app/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Origin: https://st10-ecommerce.pages.dev" \
  -d "username=admin_username&password=admin_password"

# Then use the token to update order status
curl -X PATCH "https://watchstore-api-taupe.vercel.app/api/orders/admin/orders/2/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Origin: https://st10-ecommerce.pages.dev" \
  -d '{"status": "Paid"}'
```

### Expected Response Headers
```
access-control-allow-origin: https://st10-ecommerce.pages.dev
access-control-allow-credentials: true
access-control-allow-methods: GET, POST, PUT, DELETE, PATCH, OPTIONS
access-control-allow-headers: Authorization, Content-Type, Accept, ...
```

## Debugging Steps

### 1. Check CORS Headers
```bash
# Test preflight request
curl -X OPTIONS "https://watchstore-api-taupe.vercel.app/api/orders/admin/orders/2/status" \
  -H "Origin: https://st10-ecommerce.pages.dev" \
  -H "Access-Control-Request-Method: PATCH" \
  -H "Access-Control-Request-Headers: Authorization, Content-Type" \
  -v
```

### 2. Check Authentication
Ensure you're sending a valid JWT token:
```bash
# Verify token is valid
curl -X GET "https://watchstore-api-taupe.vercel.app/api/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Origin: https://st10-ecommerce.pages.dev"
```

### 3. Check Admin Role
The authenticated user must have `role: "admin"` in the database.

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "No 'Access-Control-Allow-Origin' header" | Missing origin in CORS list | Verify `https://st10-ecommerce.pages.dev` is in `BACKEND_CORS_ORIGINS` |
| "Method not allowed" | PATCH not in allowed methods | Added `PATCH` to `allow_methods` |
| "Header not allowed" | Authorization missing from allowed headers | Added comprehensive header list |
| "Credentials not allowed" | Missing `allow_credentials=True` | Ensure credentials are allowed |

## Environment Variables
For production, set:
```bash
CORS_ORIGINS=https://st10-ecommerce.pages.dev,https://www.st10-ecommerce.pages.dev
```

## Deploy the Fix
1. Deploy the updated backend to Vercel
2. Test the admin endpoint with proper authentication
3. Verify CORS headers in browser dev tools

The enhanced CORS configuration should resolve all admin endpoint CORS issues.