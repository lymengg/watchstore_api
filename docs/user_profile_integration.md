# User Profile & Password APIs – Frontend Integration Guide

Base URL: /api

Auth: All endpoints require Bearer access token in Authorization header: `Authorization: Bearer <access_token>`

## Get current user profile
- Method: GET
- Path: /api/users/me
- Response: 200

```http path=null start=null
GET /api/users/me HTTP/1.1
Authorization: Bearer <access_token>
```

```json path=null start=null
{
  "status": "success",
  "data": {
    "username": "jdoe",
    "email": "john@example.com",
    "phone_number": "+15551234567",
    "role": "user"
  }
}
```

Notes:
- Use `username` as the display name ("Full name") unless/until a dedicated full_name field is introduced.
- There is currently no avatar field in the API; if needed, we can extend the model later.

## Update current user profile
- Method: PUT
- Path: /api/users/me
- Body: any subset of username, email, phone_number
- Response: 200 on success, 400 if uniqueness constraint fails

```http path=null start=null
PUT /api/users/me HTTP/1.1
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "username": "john.doe",
  "email": "john.doe@example.com",
  "phone_number": "+15559876543"
}
```

```json path=null start=null
{
  "status": "success",
  "data": {
    "username": "john.doe",
    "email": "john.doe@example.com",
    "phone_number": "+15559876543",
    "role": "user"
  }
}
```

Validation/Errors:
- 400 Username already exists
- 400 Email already exists
- 400 Phone number already exists

## Change password
Two equivalent endpoints are available; prefer the users route.

- Method: POST
- Path: /api/users/change-password (preferred)
- Alt Path: /api/auth/change-password
- Body:
  - current_password: string
  - new_password: string

```http path=null start=null
POST /api/users/change-password HTTP/1.1
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "OldPass123!",
  "new_password": "NewPass456!"
}
```

Responses:
- 200 `{ "status": "success", "data": "Password updated" }`
- 400 `Current password is incorrect`

## UI Wiring Tips
- On the profile top section, display `username`, `email`, `phone_number`.
- Add an "Edit Profile" button to open a form bound to PUT /api/users/me.
- Add a "Change Password" button to open a modal bound to POST /api/users/change-password.
- Persist the access token and send it on each request via Authorization header.
