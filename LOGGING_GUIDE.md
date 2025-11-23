# Comprehensive Logging Guide

This guide explains the logging system implemented for the Watchstore API, optimized for Vercel deployment and production monitoring.

## Overview

The application uses structured JSON logging with multiple log levels and automatic request tracing. All logs are optimized for Vercel's infrastructure and can be monitored through:

- Vercel Dashboard (Real-time logs)
- External log aggregation services (DataDog, LogRocket, etc.)
- Local development (console output)

## Logging Configuration

### Environment Detection
- **Production**: Uses structured JSON logging with minimal verbosity
- **Development**: Uses readable format with detailed debug information

### Log Levels
- **DEBUG**: Detailed information for development debugging
- **INFO**: General information about application flow
- **WARNING**: Unexpected behavior that doesn't stop the application
- **ERROR**: Error conditions that may affect functionality
- **CRITICAL**: Serious errors that may cause the application to stop

### Log Categories

1. **Request Logging**: All HTTP requests/responses with timing
2. **Auth Logging**: Authentication events and security-related actions
3. **Database Logging**: Database operations and connection issues
4. **Business Logic**: Application-specific business events
5. **External APIs**: Third-party service interactions
6. **Security**: Security-related events and potential threats
7. **Lifecycle**: Application startup/shutdown events

## Structured Log Format

All logs include structured fields for easy searching and analysis:

```json
{
  "timestamp": "2025-01-21T10:30:45.123Z",
  "level": "INFO",
  "message": "User registration successful",
  "application": "watchstore-api",
  "environment": "production",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "john_doe",
  "ip_address": "192.168.1.100",
  "action": "registration_success",
  "user_id": 123,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user"
}
```

## Request Tracing

Every request gets a unique `request_id` that:
- Tracks the complete request lifecycle
- Links related log entries
- Appears in response headers (`X-Request-ID`)
- Helps debug issues across multiple services

## Key Features

### 1. Automatic Request Logging
- Logs all HTTP requests and responses
- Tracks response times
- Records user context when authenticated
- Captures client IP and User-Agent

### 2. Exception Handling
- Catches and logs all unhandled exceptions
- Preserves stack traces for debugging
- Returns user-friendly error responses
- Maintains security by not exposing sensitive data

### 3. Security Event Logging
- Authentication attempts (success/failure)
- Registration attempts
- Password changes
- Permission denials
- Suspicious activities

### 4. Performance Monitoring
- Request duration tracking
- Database query timing
- External API call timing
- Memory usage (when available)

## Log Examples

### Successful User Registration
```json
{
  "timestamp": "2025-01-21T10:30:45.123Z",
  "level": "INFO",
  "message": "User registration successful",
  "application": "watchstore-api",
  "environment": "production",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "action": "registration_success",
  "user_id": 123,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user"
}
```

### Database Error
```json
{
  "timestamp": "2025-01-21T10:31:15.456Z",
  "level": "ERROR",
  "message": "Database integrity error during registration",
  "application": "watchstore-api",
  "environment": "production",
  "request_id": "550e8400-e29b-41d4-a716-446655440001",
  "action": "registration_failed",
  "error_type": "integrity_error",
  "username": "jane_doe",
  "email": "jane@example.com",
  "error_details": "null value in column \"is_active\" violates not-null constraint"
}
```

### Request Performance
```json
{
  "timestamp": "2025-01-21T10:32:00.789Z",
  "level": "INFO",
  "message": "Request completed",
  "application": "watchstore-api",
  "environment": "production",
  "request_id": "550e8400-e29b-41d4-a716-446655440002",
  "method": "GET",
  "url": "https://api.watchstore.com/api/products",
  "status_code": 200,
  "process_time_ms": 145.67,
  "user_id": "john_doe"
}
```

## Monitoring in Production

### Vercel Dashboard
1. Go to your project in Vercel
2. Click on the "Functions" tab
3. View real-time logs for your API functions
4. Filter by log level, time range, or search terms

### Log Search Examples

**Find all registration failures:**
```
action:registration_failed
```

**Find database errors:**
```
error_type:integrity_error OR error_type:sqlalchemy_error
```

**Find slow requests:**
```
process_time_ms:>1000
```

**Find authentication issues:**
```
level:ERROR application:watchstore-api action:login_failed
```

### Alerting Setup

You can set up alerts for critical events:
- High error rates
- Database connection issues
- Authentication failures
- Performance degradation

## Adding Custom Logging

### In Router Functions
```python
from ..logging_config import get_logger

@router.get("/products")
async def get_products():
    logger = get_logger("products")

    logger.info("Fetching products", extra={
        "action": "products_fetch",
        "user_id": getattr(request.state, 'current_user', None)
    })

    # ... your logic
```

### In Business Logic
```python
from .logging_config import get_logger

business_logger = get_logger("business_logic")

business_logger.info(
    "Order created successfully",
    extra={
        "action": "order_created",
        "order_id": order.id,
        "user_id": order.user_id,
        "total_amount": order.total
    }
)
```

## Security Considerations

### Sensitive Data Handling
- Passwords are never logged
- Credit card information is never logged
- Personal identifiable information (PII) is limited
- API keys and secrets are never logged

### Log Retention
- Production logs are retained according to Vercel's policies
- Sensitive operations are logged with appropriate detail levels
- Old logs are automatically pruned based on retention settings

## Troubleshooting

### Common Issues

1. **Logs not appearing in Vercel**
   - Check that `logging_config.py` is properly imported
   - Verify log level isn't set too high
   - Ensure the function is actually being called

2. **Too much log noise**
   - Adjust log levels in `setup_logging()`
   - Filter specific loggers in monitoring tools

3. **Missing user context**
   - Verify auth middleware sets `request.state.current_user`
   - Check that user information is passed to loggers

### Debug Mode
In development, set the environment variable to enable verbose logging:
```bash
export VERCEL_ENV=development
```

## Integration with External Services

### DataDog
Add DataDog logging by installing the library and configuring the logger:

```python
from datadog import initialize

options = {
    'api_key': os.getenv('DATADOG_API_KEY'),
    'app_key': os.getenv('DATADOG_APP_KEY')
}

initialize(**options)
```

### LogRocket
LogRocket can automatically capture structured logs from Vercel functions.

### New Relic
New Relic agents can be configured to ingest Vercel function logs.

## Best Practices

1. **Use structured logging**: Always use the `extra` parameter for contextual data
2. **Be specific with log levels**: Use appropriate levels for different scenarios
3. **Include request context**: Always log with request context when available
4. **Log business events**: Track important business metrics and user actions
5. **Monitor error rates**: Set up alerts for increased error rates
6. **Review logs regularly**: Regularly review logs for patterns and issues

## Performance Impact

- Logging overhead is minimal (< 1ms per request)
- JSON formatting is efficient and optimized
- Log levels prevent unnecessary processing
- Structured logs are compressed efficiently in transmission

## Maintenance

- Regularly review log patterns for optimization
- Update logging configuration as the application evolves
- Monitor log volumes and adjust levels as needed
- Keep sensitive data patterns updated