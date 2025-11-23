# 🧾 Backend API Specification — Checkout & Stripe Payment Integration

## 📘 Overview
This document outlines the backend API requirements to support the checkout process, order management, and Stripe payment integration for the e-commerce application.

---

## ⚙️ API Endpoints

### 1️⃣ POST `/api/orders` — Create a New Order
**Description:**  
Creates a new order when the user submits the checkout form.  
Includes shipping details and cart items.  
The order should initially be stored with a status of **"Pending Payment"** until the Stripe payment is completed.

**Responsibilities:**
- Validate shipping and cart data.
- Calculate total amount.
- Save order and order items in the database.
- Return the created order details (e.g., `order_id`, total, status).

---

### 2️⃣ POST `/api/payments/create-session` — Create Stripe Checkout Session
**Description:**  
Creates a new **Stripe Checkout Session** for the specified order.  
This session provides a secure Stripe-hosted payment page where the customer can complete the payment.

**Responsibilities:**
- Retrieve order details from the database.
- Create a Stripe Checkout Session with order items and total amount.
- Return the **Stripe session URL** for frontend redirection.

---

### 3️⃣ POST `/api/webhooks/stripe` — Handle Stripe Webhook Events
**Description:**  
Handles asynchronous payment events sent by Stripe (e.g., successful payments or failed transactions).  
This ensures the backend stays in sync with Stripe’s payment results.

**Responsibilities:**
- Verify the Stripe webhook signature.
- Process events such as:
  - `checkout.session.completed` → Mark order as **“Paid”**
  - `payment_intent.payment_failed` → Mark order as **“Failed”**
- Update order status accordingly.
- Optionally trigger invoice creation and/or send confirmation emails.

---

### 4️⃣ GET `/api/orders/:order_id` — Retrieve Order Details
**Description:**  
Fetches detailed order information by order ID.  
Used by the frontend to show order details or generate invoice previews.

**Responsibilities:**
- Retrieve order, shipping, and order item data.
- Include payment status and timestamps.
- Return all relevant order information to the frontend.

---

### 5️⃣ GET `/api/orders/:order_id/invoice` — Retrieve or Generate Invoice
**Description:**  
Provides invoice information for the specified order.  
This may return structured JSON data or a downloadable PDF file.

**Responsibilities:**
- Generate invoice data (order number, total, date, items, etc.).
- Optionally generate a PDF version and return the download URL.
- Ensure only paid orders can generate invoices.

---

### 6️⃣ GET `/api/orders/:order_id/status` — Check Order Payment Status
**Description:**  
Allows the frontend to confirm whether a given order has been successfully paid.  
Useful after returning from the Stripe Checkout success page.

**Responsibilities:**
- Retrieve the current order payment status.
- Return a simple response with order ID, payment status, and updated timestamp.

---

### 7️⃣ (Optional) GET `/api/cart/verify` — Validate Cart Before Order
**Description:**  
Verifies the cart items before an order is placed to prevent inconsistencies.  
Checks for price updates, stock availability, and product validity.

**Responsibilities:**
- Validate product IDs and quantities.
- Confirm stock and current pricing.
- Return corrected or validated cart data to the frontend.

---

## 🧱 Backend Responsibilities Summary

| Responsibility | Description |
|----------------|--------------|
| **Order Management** | Create, retrieve, and update order records |
| **Shipping Handling** | Store and manage customer shipping information |
| **Payment Integration** | Communicate with Stripe for secure payment sessions |
| **Payment Status Update** | Handle Stripe webhooks and update payment results |
| **Invoice Management** | Generate and serve invoices for paid orders |
| **Security** | Authenticate users and verify Stripe webhook signatures |
| **Data Validation** | Validate shipping info, cart data, and stock before processing |

---

## 🔐 Security Considerations
- Implement authentication for all protected endpoints.
- Use HTTPS for all API communication.
- Verify Stripe webhook signatures before processing events.
- Never store or process raw card data on your servers (Stripe handles this).

---

## 🧭 Payment Flow Summary

1. **User submits checkout form** → Frontend calls `/api/orders`
2. **Order created** → Backend returns `order_id`
3. **Frontend requests payment session** → `/api/payments/create-session`
4. **Backend creates Stripe session** → Returns redirect URL
5. **User redirected to Stripe Checkout**
6. **Stripe completes payment** → Sends webhook to `/api/webhooks/stripe`
7. **Backend updates order status** → Marks as **Paid**
8. **Frontend fetches invoice** → `/api/orders/:order_id/invoice`

---

## 🧩 Entities Overview

| Entity | Description |
|--------|--------------|
| **Order** | Stores order details such as user, total, status, and timestamps |
| **OrderItem** | Stores product details (name, price, quantity) for each order |
| **Shipping** | Stores customer shipping information linked to the order |
| **Invoice** | Contains invoice number, reference to order, and optional PDF |
| **Payment** | Stores Stripe payment session ID and payment status |

---

**Last Updated:** October 2025  
**Prepared for:** Backend Developer Team  
**Purpose:** To implement API support for frontend checkout and Stripe integration.
