# Order Management API — Frontend Integration

This doc covers user order history and admin order management endpoints.

Auth: Bearer token required. Admin routes require admin role.

Statuses and allowed transitions:
- Pending Payment → Paid | Cancelled
- Paid → Shipped | Cancelled
- Shipped → Completed | Cancelled
- Completed (terminal)
- Cancelled (terminal)

## User Endpoints

### List My Orders
GET `/api/orders?status=Paid&skip=0&limit=50`

Response: `OrderOut[]`

Example:
```json path=null start=null
[
  {
    "id": 1001,
    "items": [
      { "product": {"id": 101, "name": "Ocean Watch", "brand": "Aqua", "price": 199.99, "image": "data:image/jpeg;base64,..."},
        "quantity": 2, "line_total": 399.98 }
    ],
    "total_items": 2,
    "subtotal": 399.98,
    "status": "Paid",
    "created_at": "2025-10-18T18:00:00Z"  
  }
]
```

### Get Order Details
GET `/api/orders/{order_id}` → `OrderOut`

### Get Order Status
GET `/api/orders/{order_id}/status` → `{ order_id, status, updated_at }`

### Get Invoice
GET `/api/orders/{order_id}/invoice` → JSON invoice structure

## Admin Endpoints

All admin endpoints require the admin role.

### List Orders (filterable)
GET `/api/orders/admin/orders?status=Shipped&user_id=42&skip=0&limit=50`

Response: `OrderOut[]`

### Update Order Status
PATCH `/api/orders/admin/orders/{order_id}/status`

Body:
```json path=null start=null
{ "status": "Shipped" }
```

Response:
```json path=null start=null
{ "order_id": 1001, "status": "Shipped", "updated_at": "2025-10-19T09:20:00Z" }
```

Errors:
- 400 Invalid transition (e.g., Completed → Shipped)
- 404 Order not found

## Notes
- Status values are case-sensitive; use the exact strings shown above.
- User list endpoint supports optional status filtering and pagination via `skip` and `limit`.
- Admin list endpoint supports filtering by `status` and/or `user_id`.
