# Checkout & Payments API — Frontend Integration Guide

This guide documents the checkout, orders, and Stripe payment endpoints implemented in the backend.

- Auth: All endpoints (except the Stripe webhook) require a Bearer access token in the `Authorization` header.
- Currency: Amounts are in USD; Stripe amounts are sent in cents.
- Order status values: `"Pending Payment"`, `"Paid"`, `"Failed"`.

## Data contracts

- ProductList
  - `{ id: number, name: string, brand: string, price: number, image?: string (data URL), description?: string }`
- CartItemOut
  - `{ product: ProductList, quantity: number, line_total: number }`
- CartOut
  - `{ items: CartItemOut[], total_items: number, subtotal: number }`
- ShippingAddress
  - `{ full_name: string, phone: string, address1: string, address2?: string, city: string, state?: string, postal_code: string, country: string }`
- OrderCreate
  - `{ shipping: ShippingAddress, items?: { product_id: number, quantity: number }[] }`
  - If `items` is omitted, the server uses the current user's cart contents.
- OrderOut
  - `{ id: number, items: { product: ProductList, quantity: number, line_total: number }[], total_items: number, subtotal: number, status: string, created_at: string }`
- PaymentSessionCreate
  - `{ order_id: number, success_url: string, cancel_url: string }`
- PaymentSessionOut
  - `{ url: string, session_id: string }`
- OrderStatusOut
  - `{ order_id: number, status: string, updated_at: string }`

## Endpoints

### Create Order
POST `/api/orders`

Request (uses cart by default):
```json path=null start=null
{
  "shipping": {
    "full_name": "John Doe",
    "phone": "+1-555-0100",
    "address1": "123 Main St",
    "city": "Springfield",
    "postal_code": "12345",
    "country": "US"
  }
}
```

Optional explicit items:
```json path=null start=null
{
  "shipping": { /* as above */ },
  "items": [
    { "product_id": 101, "quantity": 2 },
    { "product_id": 202, "quantity": 1 }
  ]
}
```

Response:
```json path=null start=null
{
  "id": 1001,
  "items": [
    {
      "product": { "id": 101, "name": "Ocean Watch", "brand": "Aqua", "price": 199.99, "image": "data:image/jpeg;base64,..." },
      "quantity": 2,
      "line_total": 399.98
    }
  ],
  "total_items": 2,
  "subtotal": 399.98,
  "status": "Pending Payment",
  "created_at": "2025-10-18T18:00:00Z"
}
```

Errors: 400 (empty cart, insufficient stock), 404 (product not found)

---

### Get Order
GET `/api/orders/{order_id}`

Response: `OrderOut`

Errors: 404 (not found or not owned by user)

---

### Get Order Status
GET `/api/orders/{order_id}/status`

Response:
```json path=null start=null
{ "order_id": 1001, "status": "Paid", "updated_at": "2025-10-18T18:05:00Z" }
```

Errors: 404 (not found or not owned by user)

---

### Get Invoice (JSON)
GET `/api/orders/{order_id}/invoice`

Response (example):
```json path=null start=null
{
  "order_id": 1001,
  "status": "Paid",
  "created_at": "2025-10-18T18:00:00Z",
  "billing": {
    "name": "John Doe",
    "phone": "+1-555-0100",
    "address": {
      "line1": "123 Main St",
      "line2": null,
      "city": "Springfield",
      "state": null,
      "postal_code": "12345",
      "country": "US"
    }
  },
  "items": [
    { "name": "Ocean Watch", "brand": "Aqua", "unit_price": 199.99, "quantity": 2, "line_total": 399.98 }
  ],
  "total_items": 2,
  "subtotal": 399.98
}
```

Errors: 404 (not found or not owned by user)

---

### Create Stripe Checkout Session
POST `/api/payments/create-session`

Request:
```json path=null start=null
{
  "order_id": 1001,
  "success_url": "https://frontend.example.com/checkout/success?order_id=1001",
  "cancel_url": "https://frontend.example.com/checkout/cancel?order_id=1001"
}
```

Response:
```json path=null start=null
{ "url": "https://checkout.stripe.com/c/session_...", "session_id": "cs_test_..." }
```

Notes:
- Redirect the browser to `url` to pay.
- Requires server env `STRIPE_SECRET_KEY`.
- The server records the Stripe `session_id` and tracks status via webhooks.

Errors: 400 (order missing items), 404 (order not found/not owned), 500 (Stripe not configured)

---

### Stripe Webhook (server-to-server)
POST `/api/webhooks/stripe`

- Stripe sends events with `Stripe-Signature` header.
- Requires server env `STRIPE_WEBHOOK_SECRET`.
- Handled events:
  - `checkout.session.completed` → order marked `Paid` and payment updated
  - `payment_intent.payment_failed` → order marked `Failed`

Frontend does not call this endpoint.

---

### Get Cart (for review before order)
GET `/api/cart`

Response:
```json path=null start=null
{
  "items": [
    { "product": { "id": 101, "name": "Ocean Watch", "brand": "Aqua", "price": 199.99, "image": "data:image/jpeg;base64,...", "description": "..." },
      "quantity": 2,
      "line_total": 399.98 }
  ],
  "total_items": 2,
  "subtotal": 399.98
}
```

## Typical frontend flow

1. Fetch cart: `GET /api/cart` and render summary.
2. Create order: `POST /api/orders` with shipping info (omit `items` to use cart).
3. Create Stripe session: `POST /api/payments/create-session` with the order ID and success/cancel URLs.
4. Redirect user to Stripe Checkout using the returned `url`.
5. After redirect back, poll `GET /api/orders/{order_id}/status` until `Paid` or `Failed`.
6. If `Paid`, fetch `GET /api/orders/{order_id}/invoice` to show receipt.

## HTTP headers

Include the access token on authenticated requests:
```http path=null start=null
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```
