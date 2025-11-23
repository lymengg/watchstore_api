# WatchStore API – Frontend Integration (Agent Brief)

Purpose: Describe how to integrate with the existing backend without prescribing client-side implementation.

## Base
- Base URL: use your deployment origin (e.g., http://localhost:8000)
- CORS: enabled for all origins (adjustable server-side)
- Content types: JSON unless noted; login uses x-www-form-urlencoded

## Authentication Model
- Scheme: JWT with access and refresh tokens
- Token payload includes: `sub` (username), `role` (e.g., `user`, `admin`), `type` (`access`|`refresh`), `exp`
- Expiration: evaluated using local system time
- Authorization header: `Authorization: Bearer <access_token>` for protected endpoints
- Token rotation: refresh endpoint returns a new access and refresh token

## Configuration (backend)
- `JWT_SECRET_KEY`, `JWT_REFRESH_SECRET_KEY`
- `JWT_ALGORITHM` (default `HS256`)
- `JWT_ACCESS_EXPIRE_MINUTES` (default `30`)
- `JWT_REFRESH_EXPIRE_MINUTES` (default `10080` = 7 days)

## Error Envelope
- Error responses: `{ "status": "error", "data": <string|array|object> }`
- Validation errors: HTTP 422 with details array in `data`

## Endpoints Inventory

### Register
- Method/Path: `POST /api/auth/register`
- Auth: none
- Request (JSON): `username`, `password`, `email`, `phone_number`
- Success: `{ status: "success", data: { access_token, refresh_token, token_type, username, role } }`
- Failure: 400 if username/email/phone taken

### Login
- Method/Path: `POST /api/auth/login`
- Auth: none
- Request (x-www-form-urlencoded): `username`, `password`
- Success: same shape as Register
- Failure: 401 invalid credentials

### Refresh Tokens
- Method/Path: `POST /api/auth/refresh`
- Auth: none
- Request (JSON): `refresh_token`
- Success: `{ status: "success", data: { access_token, refresh_token, token_type } }`
- Failure: 401 invalid refresh or user not found

### Profile (current user)
- Method/Path: `GET /api/auth/profile`
- Auth: Bearer access token required
- Success: `{ status: "success", data: { username, email, phone_number, role } }`

### Change Password
- Method/Path: `POST /api/auth/change-password`
- Auth: Bearer access token required
- Request (JSON): `current_password`, `new_password`
- Success: `{ status: "success", data: "Password updated" }`
- Failure: 400 incorrect current password

### Logout
- Method/Path: `POST /api/auth/logout`
- Auth: optional
- Semantics: stateless server acknowledgment; client handles token disposal
- Success: `{ status: "success", data: "Logged out" }`

### Products – Create (Admin only)
- Method/Path: `POST /api/products/`
- Auth: Bearer access token with `role=admin`
- Request (JSON): `name`, `brand`, `description?`, `price`, `image?` (base64), `stock`
- Success: `{ message: "Product '<name>' created by <sub>" }`
- Failure: 403 for non-admin

### Products – Get by ID
- Method/Path: `GET /api/products/{product_id}`
- Auth: none
- Success object: `id`, `name`, `brand`, `description`, `price`, `image` (base64 or null), `stock`
- Failure: 404 not found

## Integration Protocol Notes
- Protected requests MUST include `Authorization: Bearer <access_token>`
- On 401 from protected endpoints, invoke `POST /api/auth/refresh` with `refresh_token` and retry with returned `access_token`
- On refresh failure (401), initiate re-authentication
- Role-aware UI/flows: `role` available from login/register responses and `/api/auth/profile`
- Product creation requires `admin` role; other routes may be restricted similarly if extended later
