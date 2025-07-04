
# Grocery App API Specification

## Overview
This document outlines the complete API specification for the grocery delivery application, including all endpoints, request/response structures, authentication, and implementation details.

## Base URL
- Development: `http://localhost:3000/api`
- Production: `https://your-domain.com/api`

## Authentication
The API uses Firebase Authentication with JWT tokens.

### Headers
```
Authorization: Bearer <firebase-jwt-token>
Content-Type: application/json
```

## Data Models

### User Profile
```typescript
interface Profile {
  id: string;              // Firebase Auth UID
  email: string;
  name: string;
  phone?: string;
  address?: string;
  user_type: 'customer' | 'owner';
  created_at: string;
  updated_at: string;
}
```

### Store
```typescript
interface Store {
  id: string;
  owner_id: string;        // Firebase UUID
  name: string;
  address: string;
  phone?: string;
  is_open: boolean;
  rating: number;
  delivery_time: string;   // e.g., "30-45 min"
  created_at: string;
  updated_at: string;
}
```

### Category
```typescript
interface Category {
  id: string;
  name: string;
  created_at: string;
}
```

### Product
```typescript
interface Product {
  id: string;
  store_id: string;
  category_id?: string;
  name: string;
  description?: string;
  price: number;
  unit: string;            // e.g., "kg", "piece", "liter"
  stock: number;
  image_url?: string;
  created_at: string;
  updated_at: string;
}
```

### Order
```typescript
interface Order {
  id: string;
  customer_id: string;     // Firebase UUID
  store_id: string;
  total_amount: number;
  delivery_address: string;
  status: 'pending' | 'preparing' | 'ready' | 'delivered' | 'cancelled';
  notes?: string;
  created_at: string;
  updated_at: string;
}
```

### Order Item
```typescript
interface OrderItem {
  id: string;
  order_id: string;
  product_id: string;
  quantity: number;
  price: number;           // Price at time of order
}
```

## API Endpoints

### Authentication Endpoints

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "name": "John Doe",
  "user_type": "customer",
  "phone": "+91 98765 43210",
  "address": "123 Main St, Bangalore"
}
```

**Response (201):**
```json
{
  "user": {
    "id": "firebase-auth-uid",
    "email": "user@example.com",
    "name": "John Doe",
    "user_type": "customer",
    "phone": "+91 98765 43210",
    "address": "123 Main St, Bangalore",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "token": "firebase-jwt-token"
}
```

#### POST /auth/login
Authenticate user and return JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200):**
```json
{
  "user": {
    "id": "firebase-auth-uid",
    "email": "user@example.com",
    "name": "John Doe",
    "user_type": "customer",
    "phone": "+91 98765 43210",
    "address": "123 Main St, Bangalore"
  },
  "token": "firebase-jwt-token"
}
```

### Profile Endpoints

#### GET /profile
Get current user's profile.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": "firebase-auth-uid",
  "email": "user@example.com",
  "name": "John Doe",
  "user_type": "customer",
  "phone": "+91 98765 43210",
  "address": "123 Main St, Bangalore",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### PUT /profile
Update current user's profile.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "John Smith",
  "phone": "+91 98765 43211",
  "address": "456 Oak Ave, Mumbai"
}
```

**Response (200):**
```json
{
  "id": "firebase-auth-uid",
  "email": "user@example.com",
  "name": "John Smith",
  "user_type": "customer",
  "phone": "+91 98765 43211",
  "address": "456 Oak Ave, Mumbai",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:45:00Z"
}
```

### Store Endpoints

#### GET /stores
Get all available stores.

**Query Parameters:**
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Items per page (default: 10)
- `search` (optional): Search term for store name
- `is_open` (optional): Filter by open status (true/false)

**Response (200):**
```json
{
  "stores": [
    {
      "id": "store1",
      "owner_id": "firebase-uuid-owner1",
      "name": "Fresh Vegetables Store",
      "address": "123 Market Street, Bangalore",
      "phone": "+91 98765 43210",
      "is_open": true,
      "rating": 4.5,
      "delivery_time": "30-45 min",
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-15T09:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 45,
    "items_per_page": 10
  }
}
```

#### GET /stores/:id
Get specific store details.

**Response (200):**
```json
{
  "id": "store1",
  "owner_id": "firebase-uuid-owner1",
  "name": "Fresh Vegetables Store",
  "address": "123 Market Street, Bangalore",
  "phone": "+91 98765 43210",
  "is_open": true,
  "rating": 4.5,
  "delivery_time": "30-45 min",
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-15T09:30:00Z"
}
```

#### POST /stores
Create a new store (Owner only).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "New Grocery Store",
  "address": "789 New Street, Delhi",
  "phone": "+91 87654 32109",
  "delivery_time": "25-40 min"
}
```

**Response (201):**
```json
{
  "id": "store-generated-id",
  "owner_id": "firebase-auth-uid",
  "name": "New Grocery Store",
  "address": "789 New Street, Delhi",
  "phone": "+91 87654 32109",
  "is_open": true,
  "rating": 0,
  "delivery_time": "25-40 min",
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

#### PUT /stores/:id
Update store details (Owner only).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Updated Store Name",
  "is_open": false,
  "delivery_time": "35-50 min"
}
```

**Response (200):**
```json
{
  "id": "store1",
  "owner_id": "firebase-auth-uid",
  "name": "Updated Store Name",
  "address": "123 Market Street, Bangalore",
  "phone": "+91 98765 43210",
  "is_open": false,
  "rating": 4.5,
  "delivery_time": "35-50 min",
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-15T13:15:00Z"
}
```

#### DELETE /stores/:id
Delete a store (Owner only).

**Headers:** `Authorization: Bearer <token>`

**Response (204):** No content

#### GET /stores/owner
Get stores owned by current user (Owner only).

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "stores": [
    {
      "id": "store1",
      "owner_id": "firebase-auth-uid",
      "name": "My Grocery Store",
      "address": "123 Market Street, Bangalore",
      "phone": "+91 98765 43210",
      "is_open": true,
      "rating": 4.5,
      "delivery_time": "30-45 min",
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-15T09:30:00Z"
    }
  ]
}
```

### Category Endpoints

#### GET /categories
Get all product categories.

**Response (200):**
```json
{
  "categories": [
    {
      "id": "cat1",
      "name": "Vegetables",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "cat2",
      "name": "Fruits",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### POST /categories
Create a new category (Admin only).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Dairy Products"
}
```

**Response (201):**
```json
{
  "id": "cat-generated-id",
  "name": "Dairy Products",
  "created_at": "2024-01-15T14:00:00Z"
}
```

### Product Endpoints

#### GET /products
Get all products with filtering and pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `store_id` (optional): Filter by store
- `category_id` (optional): Filter by category
- `search` (optional): Search term for product name
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter
- `in_stock` (optional): Filter products in stock (true/false)

**Response (200):**
```json
{
  "products": [
    {
      "id": "prod1",
      "store_id": "store1",
      "category_id": "cat1",
      "name": "Fresh Tomatoes",
      "description": "Locally grown organic tomatoes",
      "price": 60,
      "unit": "kg",
      "stock": 25,
      "image_url": "https://example.com/tomatoes.jpg",
      "created_at": "2024-01-12T10:00:00Z",
      "updated_at": "2024-01-15T08:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 8,
    "total_items": 156,
    "items_per_page": 20
  }
}
```

#### GET /products/:id
Get specific product details.

**Response (200):**
```json
{
  "id": "prod1",
  "store_id": "store1",
  "category_id": "cat1",
  "name": "Fresh Tomatoes",
  "description": "Locally grown organic tomatoes",
  "price": 60,
  "unit": "kg",
  "stock": 25,
  "image_url": "https://example.com/tomatoes.jpg",
  "created_at": "2024-01-12T10:00:00Z",
  "updated_at": "2024-01-15T08:30:00Z"
}
```

#### GET /stores/:storeId/products
Get all products for a specific store.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `category_id` (optional): Filter by category
- `search` (optional): Search term

**Response (200):**
```json
{
  "products": [
    {
      "id": "prod1",
      "store_id": "store1",
      "category_id": "cat1",
      "name": "Fresh Tomatoes",
      "description": "Locally grown organic tomatoes",
      "price": 60,
      "unit": "kg",
      "stock": 25,
      "image_url": "https://example.com/tomatoes.jpg",
      "created_at": "2024-01-12T10:00:00Z",
      "updated_at": "2024-01-15T08:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 3,
    "total_items": 45,
    "items_per_page": 20
  }
}
```

#### POST /stores/:storeId/products
Add new product to store (Owner only).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "category_id": "cat1",
  "name": "Fresh Carrots",
  "description": "Sweet and crunchy carrots",
  "price": 45,
  "unit": "kg",
  "stock": 30,
  "image_url": "https://example.com/carrots.jpg"
}
```

**Response (201):**
```json
{
  "id": "prod-generated-id",
  "store_id": "store1",
  "category_id": "cat1",
  "name": "Fresh Carrots",
  "description": "Sweet and crunchy carrots",
  "price": 45,
  "unit": "kg",
  "stock": 30,
  "image_url": "https://example.com/carrots.jpg",
  "created_at": "2024-01-15T15:00:00Z",
  "updated_at": "2024-01-15T15:00:00Z"
}
```

#### PUT /products/:id
Update product details (Owner only).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "price": 55,
  "stock": 20,
  "description": "Premium quality organic carrots"
}
```

**Response (200):**
```json
{
  "id": "prod1",
  "store_id": "store1",
  "category_id": "cat1",
  "name": "Fresh Carrots",
  "description": "Premium quality organic carrots",
  "price": 55,
  "unit": "kg",
  "stock": 20,
  "image_url": "https://example.com/carrots.jpg",
  "created_at": "2024-01-12T10:00:00Z",
  "updated_at": "2024-01-15T16:30:00Z"
}
```

#### DELETE /products/:id
Delete a product (Owner only).

**Headers:** `Authorization: Bearer <token>`

**Response (204):** No content

### Order Endpoints

#### GET /orders
Get orders for current user.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)
- `status` (optional): Filter by order status
- `store_id` (optional): Filter by store (for owners)

**Response (200):**
```json
{
  "orders": [
    {
      "id": "order1",
      "customer_id": "firebase-auth-uid",
      "store_id": "store1",
      "total_amount": 180,
      "delivery_address": "123 Main St, Bangalore",
      "status": "preparing",
      "notes": "Please call before delivery",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 2,
    "total_items": 15,
    "items_per_page": 10
  }
}
```

#### GET /orders/:id
Get specific order details.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "order": {
    "id": "order1",
    "customer_id": "firebase-auth-uid",
    "store_id": "store1",
    "total_amount": 180,
    "delivery_address": "123 Main St, Bangalore",
    "status": "preparing",
    "notes": "Please call before delivery",
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "items": [
    {
      "id": "item1",
      "order_id": "order1",
      "product_id": "prod1",
      "quantity": 3,
      "price": 60
    }
  ]
}
```

#### POST /orders
Create a new order (Customer only).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "store_id": "store1",
  "delivery_address": "123 Main St, Bangalore",
  "notes": "Please call before delivery",
  "items": [
    {
      "product_id": "prod1",
      "quantity": 3,
      "price": 60
    },
    {
      "product_id": "prod2",
      "quantity": 2,
      "price": 30
    }
  ]
}
```

**Response (201):**
```json
{
  "order": {
    "id": "order-generated-id",
    "customer_id": "firebase-auth-uid",
    "store_id": "store1",
    "total_amount": 240,
    "delivery_address": "123 Main St, Bangalore",
    "status": "pending",
    "notes": "Please call before delivery",
    "created_at": "2024-01-15T17:00:00Z",
    "updated_at": "2024-01-15T17:00:00Z"
  },
  "items": [
    {
      "id": "item-generated-id-1",
      "order_id": "order-generated-id",
      "product_id": "prod1",
      "quantity": 3,
      "price": 60
    },
    {
      "id": "item-generated-id-2",
      "order_id": "order-generated-id",
      "product_id": "prod2",
      "quantity": 2,
      "price": 30
    }
  ]
}
```

#### PUT /orders/:id/status
Update order status (Owner only).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "status": "ready"
}
```

**Response (200):**
```json
{
  "id": "order1",
  "customer_id": "customer-id",
  "store_id": "store1",
  "total_amount": 180,
  "delivery_address": "123 Main St, Bangalore",
  "status": "ready",
  "notes": "Please call before delivery",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T18:00:00Z"
}
```

#### GET /stores/:storeId/orders
Get orders for a specific store (Owner only).

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)
- `status` (optional): Filter by order status
- `date_from` (optional): Filter orders from date (ISO format)
- `date_to` (optional): Filter orders to date (ISO format)

**Response (200):**
```json
{
  "orders": [
    {
      "id": "order1",
      "customer_id": "customer-id",
      "store_id": "store1",
      "total_amount": 180,
      "delivery_address": "123 Main St, Bangalore",
      "status": "preparing",
      "notes": "Please call before delivery",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 48,
    "items_per_page": 10
  }
}
```

### Analytics Endpoints (Owner only)

#### GET /stores/:storeId/analytics/overview
Get store analytics overview.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `period` (optional): 'day', 'week', 'month', 'year' (default: 'month')

**Response (200):**
```json
{
  "total_orders": 156,
  "total_revenue": 23450,
  "average_order_value": 150.32,
  "top_products": [
    {
      "product_id": "prod1",
      "name": "Fresh Tomatoes",
      "quantity_sold": 45,
      "revenue": 2700
    }
  ],
  "orders_by_status": {
    "pending": 5,
    "preparing": 8,
    "ready": 3,
    "delivered": 140,
    "cancelled": 0
  },
  "revenue_by_day": [
    {
      "date": "2024-01-15",
      "revenue": 1250
    }
  ]
}
```

#### GET /stores/:storeId/analytics/sales
Get detailed sales analytics.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `period` (optional): 'day', 'week', 'month', 'year' (default: 'month')
- `group_by` (optional): 'day', 'week', 'month' (default: 'day')

**Response (200):**
```json
{
  "sales_data": [
    {
      "period": "2024-01-15",
      "orders": 12,
      "revenue": 1250,
      "customers": 10
    },
    {
      "period": "2024-01-14",
      "orders": 8,
      "revenue": 920,
      "customers": 7
    }
  ],
  "summary": {
    "total_revenue": 15680,
    "total_orders": 156,
    "unique_customers": 89,
    "growth_rate": 12.5
  }
}
```

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": "Additional error details (optional)"
  }
}
```

### Common Error Codes

#### 400 Bad Request
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  }
}
```

#### 401 Unauthorized
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}
```

#### 403 Forbidden
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions"
  }
}
```

#### 404 Not Found
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found"
  }
}
```

#### 409 Conflict
```json
{
  "error": {
    "code": "CONFLICT",
    "message": "Email already exists"
  }
}
```

#### 422 Unprocessable Entity
```json
{
  "error": {
    "code": "UNPROCESSABLE_ENTITY",
    "message": "Invalid data provided",
    "details": {
      "stock": "Stock cannot be negative"
    }
  }
}
```

#### 500 Internal Server Error
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred"
  }
}
```

## Rate Limiting

API requests are limited to:
- **General endpoints**: 100 requests per minute per IP
- **Authentication endpoints**: 10 requests per minute per IP
- **Upload endpoints**: 20 requests per minute per authenticated user

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642612800
```

## File Upload

### POST /upload/product-image
Upload product image.

**Headers:** 
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Request Body:** Form data with image file

**Response (200):**
```json
{
  "url": "https://your-cdn.com/images/product-123.jpg",
  "filename": "product-123.jpg",
  "size": 245760
}
```

## Webhooks (Future Implementation)

### Order Status Updates
```json
{
  "event": "order.status_changed",
  "data": {
    "order_id": "order1",
    "old_status": "preparing",
    "new_status": "ready",
    "timestamp": "2024-01-15T18:00:00Z"
  }
}
```

## Implementation Notes

### Current Status
- **Backend Framework**: To be implemented with Pulumi
- **Database**: Supabase PostgreSQL
- **Authentication**: Firebase Auth
- **File Storage**: To be determined (Firebase Storage or AWS S3)
- **Real-time**: Supabase real-time subscriptions for order updates

### Security Considerations
1. All endpoints require proper authentication except public store/product listings
2. Input validation and sanitization on all endpoints
3. Rate limiting to prevent abuse
4. CORS configuration for frontend domains
5. SQL injection prevention through parameterized queries
6. File upload validation and virus scanning

### Performance Optimizations
1. Database indexing on frequently queried fields
2. Caching for product listings and store data
3. Pagination for large datasets
4. Image optimization and CDN delivery
5. Connection pooling for database connections

### Monitoring and Logging
1. Request/response logging
2. Error tracking and alerting
3. Performance monitoring
4. Business metrics tracking
5. Security event logging

This API specification serves as the complete reference for implementing the backend services for the grocery delivery application.
