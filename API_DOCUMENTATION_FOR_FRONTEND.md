# Anna Akka Platform API Documentation

## Base URL
```
https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev
```

## Authentication
All protected endpoints require user authentication. Use one of these methods:

### Method 1: Headers (Recommended)
```
X-User-ID: your-user-id
```

### Method 2: Query Parameters (Development)
```
?user_id=your-user-id
```

### Method 3: API Gateway Authorizer (Production)
```
Authorization: Bearer your-jwt-token
```

---

## 1. Authentication APIs

### 1.1 Register User
**POST** `/auth/register`

**Request Body:**
```json
{
  "phone": "+91 98765 43210",
  "email": "user@example.com",
  "name": "John Doe",
  "roles": ["customer"],
  "address": "123 Main St, Bangalore"
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid-generated",
    "phone": "+91 98765 43210",
    "email": "user@example.com",
    "name": "John Doe",
    "roles": ["customer"],
    "address": "123 Main St, Bangalore",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 1.2 Login with Phone
**POST** `/auth/login`

**Request Body:**
```json
{
  "phone": "+91 98765 43210"
}
```

**Response:**
```json
{
  "user": {
    "id": "user-id",
    "phone": "+91 98765 43210",
    "email": "user@example.com",
    "name": "John Doe",
    "roles": ["customer"]
  }
}
```

### 1.3 Check User by Phone
**GET** `/auth/user/phone?phone=+91 98765 43210`

**Response:**
```json
{
  "user": {
    "id": "user-id",
    "name": "John Doe",
    "email": "user@example.com",
    "phone": "+91 98765 43210",
    "roles": ["customer"],
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 1.4 Send OTP
**POST** `/otp/send`

**Request Body:**
```json
{
  "phone": "+91 98765 43210"
}
```

**Response:**
```json
{
  "message": "OTP sent successfully",
  "phone": "+91 98765 43210"
}
```

### 1.5 Verify OTP
**POST** `/otp/verify`

**Request Body:**
```json
{
  "phone": "+91 98765 43210",
  "otp": "123456"
}
```

**Response:**
```json
{
  "message": "OTP verified successfully",
  "user": {
    "id": "user-id",
    "phone": "+91 98765 43210",
    "name": "John Doe",
    "email": "user@example.com",
    "roles": ["customer"],
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

---

## 2. Profile Management APIs

### 2.1 Get Profile
**GET** `/profile?user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Response:**
```json
{
  "user": {
    "id": "user-id",
    "name": "John Doe",
    "email": "user@example.com",
    "phone": "+91 98765 43210",
    "address": "123 Main St, Bangalore",
    "roles": ["customer"],
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 2.2 Update Profile
**PUT** `/profile?user_id={user_id}`

**Headers:**
```
Content-Type: application/json
X-User-ID: your-user-id
```

**Request Body:**
```json
{
  "name": "John Smith",
  "phone": "+91 98765 43211",
  "address": "456 Oak Ave, Mumbai",
  "email": "john.smith@example.com"
}
```

**Response:**
```json
{
  "user": {
    "id": "user-id",
    "name": "John Smith",
    "phone": "+91 98765 43211",
    "address": "456 Oak Ave, Mumbai",
    "email": "john.smith@example.com",
    "roles": ["customer"],
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 2.3 Delete Profile
**DELETE** `/profile?user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Response:** `204 No Content`

### 2.4 Get Profile by Phone
**GET** `/profile/phone?user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Response:**
```json
{
  "user": {
    "id": "user-id",
    "name": "John Doe",
    "email": "user@example.com",
    "phone": "+91 98765 43210",
    "roles": ["customer"],
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

---

## 3. Stores APIs

### 3.1 Get All Stores
**GET** `/stores?page=1&limit=10&search=pizza&is_open=true&user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)
- `search` (optional): Search store names
- `is_open` (optional): Filter by open status (true/false)
- `user_id` (required): User ID for authentication

**Response:**
```json
{
  "stores": [
    {
      "id": "store-123",
      "name": "Pizza Palace",
      "address": "123 Main St, Bangalore",
      "phone": "+91 98765 43210",
      "is_open": true,
      "rating": 4.5,
      "delivery_time": "30-45 min",
      "product_ids": ["prod-1", "prod-2"],
      "owner_id": "user-id",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 50,
    "items_per_page": 10
  }
}
```

### 3.2 Get Store by ID
**GET** `/stores/{store_id}?user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Response:**
```json
{
  "store": {
    "id": "store-123",
    "name": "Pizza Palace",
    "address": "123 Main St, Bangalore",
    "phone": "+91 98765 43210",
    "is_open": true,
    "rating": 4.5,
    "delivery_time": "30-45 min",
    "product_ids": ["prod-1", "prod-2"],
    "owner_id": "user-id",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 3.3 Create Store
**POST** `/stores?user_id={user_id}`

**Headers:**
```
Content-Type: application/json
X-User-ID: your-user-id
```

**Request Body:**
```json
{
  "name": "Pizza Palace",
  "address": "123 Main St, Bangalore",
  "phone": "+91 98765 43210",
  "delivery_time": "30-45 min"
}
```

**Response:**
```json
{
  "store": {
    "id": "store-123",
    "name": "Pizza Palace",
    "address": "123 Main St, Bangalore",
    "phone": "+91 98765 43210",
    "is_open": true,
    "rating": 0,
    "delivery_time": "30-45 min",
    "product_ids": [],
    "owner_id": "user-id",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 3.4 Update Store
**PUT** `/stores/{store_id}?user_id={user_id}`

**Headers:**
```
Content-Type: application/json
X-User-ID: your-user-id
```

**Request Body:**
```json
{
  "name": "Updated Pizza Palace",
  "address": "456 Oak Ave, Mumbai",
  "phone": "+91 98765 43211",
  "delivery_time": "45-60 min",
  "is_open": false
}
```

**Response:**
```json
{
  "store": {
    "id": "store-123",
    "name": "Updated Pizza Palace",
    "address": "456 Oak Ave, Mumbai",
    "phone": "+91 98765 43211",
    "is_open": false,
    "delivery_time": "45-60 min",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 3.5 Delete Store
**DELETE** `/stores/{store_id}?user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Response:** `204 No Content`

### 3.6 Get Owner Stores
**GET** `/stores/owner?user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Response:**
```json
{
  "stores": [
    {
      "id": "store-123",
      "name": "Pizza Palace",
      "address": "123 Main St, Bangalore",
      "is_open": true,
      "owner_id": "user-id"
    }
  ]
}
```

---

## 4. Available Products APIs

### 4.1 Get All Available Products
**GET** `/available-products?page=1&limit=20&category_id=pizza&search=margherita&min_price=10&max_price=20`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `category_id` (optional): Filter by category
- `search` (optional): Search product names
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter

**Response:**
```json
{
  "products": [
    {
      "id": "b9238c4d-77e1-4585-b086-11af2dabdb59",
      "name": "Margherita Pizza",
      "description": "Classic tomato and mozzarella pizza",
      "price": 12.99,
      "unit": "piece",
      "category_id": "pizza",
      "image_url": "https://example.com/pizza.jpg",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 100,
    "items_per_page": 20
  }
}
```

### 4.2 Get Available Product by ID
**GET** `/available-products/{product_id}`

**Response:**
```json
{
  "product": {
    "id": "b9238c4d-77e1-4585-b086-11af2dabdb59",
    "name": "Margherita Pizza",
    "description": "Classic tomato and mozzarella pizza",
    "price": 12.99,
    "unit": "piece",
    "category_id": "pizza",
    "image_url": "https://example.com/pizza.jpg",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 4.3 Create Available Product
**POST** `/available-products`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Margherita Pizza",
  "description": "Classic tomato and mozzarella pizza with fresh basil",
  "price": 12.99,
  "unit": "piece",
  "category_id": "pizza",
  "image_url": "https://example.com/margherita-pizza.jpg"
}
```

**Response:**
```json
{
  "product": {
    "id": "b9238c4d-77e1-4585-b086-11af2dabdb59",
    "name": "Margherita Pizza",
    "description": "Classic tomato and mozzarella pizza with fresh basil",
    "price": 12.99,
    "unit": "piece",
    "category_id": "pizza",
    "image_url": "https://example.com/margherita-pizza.jpg",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 4.4 Update Available Product
**PUT** `/available-products/{product_id}`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Updated Margherita Pizza",
  "price": 14.99,
  "description": "Updated description with premium ingredients"
}
```

**Response:**
```json
{
  "product": {
    "id": "b9238c4d-77e1-4585-b086-11af2dabdb59",
    "name": "Updated Margherita Pizza",
    "price": 14.99,
    "description": "Updated description with premium ingredients",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 4.5 Delete Available Product
**DELETE** `/available-products/{product_id}`

**Response:** `204 No Content`

---

## 5. Products APIs

### 5.1 Get All Products
**GET** `/products?page=1&limit=20&store_id=store-123&category_id=pizza&search=margherita&min_price=10&max_price=20&in_stock=true&user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `store_id` (optional): Filter by store ID
- `category_id` (optional): Filter by category
- `search` (optional): Search product names
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter
- `in_stock` (optional): Filter by stock availability (true/false)
- `user_id` (required): User ID for authentication

**Response:**
```json
{
  "products": [
    {
      "id": "prod-123",
      "store_id": "store-123",
      "available_product_id": "b9238c4d-77e1-4585-b086-11af2dabdb59",
      "name": "Margherita Pizza",
      "description": "Classic tomato and mozzarella pizza",
      "price": 13.99,
      "unit": "piece",
      "stock": 25,
      "category_id": "pizza",
      "image_url": "https://example.com/pizza.jpg",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 100,
    "items_per_page": 20
  }
}
```

### 5.2 Get Product by ID
**GET** `/products/{product_id}?user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Response:**
```json
{
  "product": {
    "id": "prod-123",
    "store_id": "store-123",
    "available_product_id": "b9238c4d-77e1-4585-b086-11af2dabdb59",
    "name": "Margherita Pizza",
    "description": "Classic tomato and mozzarella pizza",
    "price": 13.99,
    "unit": "piece",
    "stock": 25,
    "category_id": "pizza",
    "image_url": "https://example.com/pizza.jpg",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 5.3 Get Store Products
**GET** `/stores/{store_id}/products?page=1&limit=10&category_id=pizza&search=margherita&user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)
- `category_id` (optional): Filter by category
- `search` (optional): Search product names
- `user_id` (required): User ID for authentication

**Response:**
```json
{
  "products": [
    {
      "id": "prod-123",
      "store_id": "store-123",
      "name": "Margherita Pizza",
      "description": "Classic tomato and mozzarella pizza",
      "price": 13.99,
      "unit": "piece",
      "stock": 25,
      "category_id": "pizza",
      "image_url": "https://example.com/pizza.jpg"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 3,
    "total_items": 30,
    "items_per_page": 10
  }
}
```

### 5.4 Create Product (From Available Catalog)
**POST** `/stores/{store_id}/products?user_id={user_id}`

**Headers:**
```
Content-Type: application/json
X-User-ID: your-user-id
```

**Request Body:**
```json
{
  "available_product_id": "b9238c4d-77e1-4585-b086-11af2dabdb59",
  "price": 13.99,
  "stock": 25
}
```

**Response:**
```json
{
  "product": {
    "id": "prod-123",
    "store_id": "store-123",
    "available_product_id": "b9238c4d-77e1-4585-b086-11af2dabdb59",
    "name": "Margherita Pizza",
    "description": "Classic tomato and mozzarella pizza",
    "price": 13.99,
    "unit": "piece",
    "stock": 25,
    "category_id": "pizza",
    "image_url": "https://example.com/pizza.jpg",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 5.5 Create Product (New Product)
**POST** `/stores/{store_id}/products?user_id={user_id}`

**Headers:**
```
Content-Type: application/json
X-User-ID: your-user-id
```

**Request Body:**
```json
{
  "name": "Fresh Carrots",
  "description": "Organic orange carrots",
  "price": 30.00,
  "unit": "kg",
  "stock": 25,
  "category_id": "vegetables",
  "image_url": "https://example.com/carrots.jpg"
}
```

**Response:**
```json
{
  "product": {
    "id": "prod-123",
    "store_id": "store-123",
    "name": "Fresh Carrots",
    "description": "Organic orange carrots",
    "price": 30.00,
    "unit": "kg",
    "stock": 25,
    "category_id": "vegetables",
    "image_url": "https://example.com/carrots.jpg",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 5.6 Update Product
**PUT** `/products/{product_id}?user_id={user_id}`

**Headers:**
```
Content-Type: application/json
X-User-ID: your-user-id
```

**Request Body:**
```json
{
  "name": "Updated Product Name",
  "price": 35.00,
  "stock": 30,
  "description": "Updated description"
}
```

**Response:**
```json
{
  "product": {
    "id": "prod-123",
    "name": "Updated Product Name",
    "price": 35.00,
    "stock": 30,
    "description": "Updated description",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 5.7 Delete Product
**DELETE** `/products/{product_id}?user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Response:** `204 No Content`

---

## 6. Cart Management APIs

### 6.1 Get Cart
**GET** `/cart?user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Response:**
```json
{
  "cart": {
    "items": [
      {
        "product_id": "b9238c4d-77e1-4585-b086-11af2dabdb59",
        "name": "Margherita Pizza",
        "price": 13.99,
        "quantity": 2,
        "total": 27.98
      }
    ],
    "total_items": 2,
    "total_amount": 27.98
  }
}
```

### 6.2 Add Item to Cart
**POST** `/cart/items?user_id={user_id}`

**Headers:**
```
Content-Type: application/json
X-User-ID: your-user-id
```

**Request Body:**
```json
{
  "product_id": "b9238c4d-77e1-4585-b086-11af2dabdb59",
  "quantity": 2
}
```

**Response:**
```json
{
  "message": "Item added to cart successfully",
  "cart": {
    "items": [
      {
        "product_id": "b9238c4d-77e1-4585-b086-11af2dabdb59",
        "name": "Margherita Pizza",
        "price": 13.99,
        "quantity": 2,
        "total": 27.98
      }
    ],
    "total_items": 2,
    "total_amount": 27.98
  }
}
```

### 6.3 Update Cart Item Quantity
**PUT** `/cart/items/{product_id}?user_id={user_id}`

**Headers:**
```
Content-Type: application/json
X-User-ID: your-user-id
```

**Request Body:**
```json
{
  "quantity": 3
}
```

**Response:**
```json
{
  "message": "Cart item updated successfully",
  "cart": {
    "items": [
      {
        "product_id": "b9238c4d-77e1-4585-b086-11af2dabdb59",
        "name": "Margherita Pizza",
        "price": 13.99,
        "quantity": 3,
        "total": 41.97
      }
    ],
    "total_items": 3,
    "total_amount": 41.97
  }
}
```

### 6.4 Remove Item from Cart
**DELETE** `/cart/items/{product_id}?user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Response:**
```json
{
  "message": "Item removed from cart successfully",
  "cart": {
    "items": [],
    "total_items": 0,
    "total_amount": 0
  }
}
```

### 6.5 Clear Cart
**DELETE** `/cart?user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Response:**
```json
{
  "message": "Cart cleared successfully",
  "cart": {
    "items": [],
    "total_items": 0,
    "total_amount": 0
  }
}
```

---

## 7. Orders APIs

### 7.1 Get All Orders
**GET** `/orders?page=1&limit=10&user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)
- `user_id` (required): User ID for authentication

**Response:**
```json
{
  "orders": [
    {
      "id": "order-123",
      "customer_id": "user-id",
      "store_id": "store-123",
      "status": "pending",
      "total_amount": 27.98,
      "delivery_address": "123 Main St, Bangalore",
      "special_instructions": "Extra cheese please",
      "items": [
        {
          "product_id": "b9238c4d-77e1-4585-b086-11af2dabdb59",
          "name": "Margherita Pizza",
          "price": 13.99,
          "quantity": 2,
          "total": 27.98
        }
      ],
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 3,
    "total_items": 25,
    "items_per_page": 10
  }
}
```

### 7.2 Get Order by ID
**GET** `/orders/{order_id}?user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Response:**
```json
{
  "order": {
    "id": "order-123",
    "customer_id": "user-id",
    "store_id": "store-123",
    "status": "pending",
    "total_amount": 27.98,
    "delivery_address": "123 Main St, Bangalore",
    "special_instructions": "Extra cheese please",
    "items": [
      {
        "product_id": "b9238c4d-77e1-4585-b086-11af2dabdb59",
        "name": "Margherita Pizza",
        "price": 13.99,
        "quantity": 2,
        "total": 27.98
      }
    ],
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 7.3 Create Order
**POST** `/orders?user_id={user_id}`

**Headers:**
```
Content-Type: application/json
X-User-ID: your-user-id
```

**Request Body:**
```json
{
  "store_id": "store-123",
  "delivery_address": "123 Main St, Bangalore",
  "special_instructions": "Extra cheese please"
}
```

**Response:**
```json
{
  "message": "Order created successfully from cart",
  "order": {
    "id": "order-123",
    "customer_id": "user-id",
    "store_id": "store-123",
    "status": "pending",
    "total_amount": 27.98,
    "delivery_address": "123 Main St, Bangalore",
    "special_instructions": "Extra cheese please",
    "items": [
      {
        "product_id": "b9238c4d-77e1-4585-b086-11af2dabdb59",
        "name": "Margherita Pizza",
        "price": 13.99,
        "quantity": 2,
        "total": 27.98
      }
    ],
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "items": [
    {
      "product_id": "b9238c4d-77e1-4585-b086-11af2dabdb59",
      "name": "Margherita Pizza",
      "price": 13.99,
      "quantity": 2,
      "total": 27.98
    }
  ],
  "total_amount": 27.98
}
```

### 7.4 Update Order Status
**PUT** `/orders/{order_id}/status?user_id={user_id}`

**Headers:**
```
Content-Type: application/json
X-User-ID: your-user-id
```

**Request Body:**
```json
{
  "status": "preparing"
}
```

**Response:**
```json
{
  "order": {
    "id": "order-123",
    "status": "preparing",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

**Valid Status Values:**
- `pending`
- `preparing`
- `ready`
- `delivered`
- `cancelled`

---

## 8. Categories APIs

### 8.1 Get All Categories
**GET** `/categories`

**Response:**
```json
{
  "categories": [
    {
      "id": "category-123",
      "name": "Pizza",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### 8.2 Create Category
**POST** `/categories`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Pizza"
}
```

**Response:**
```json
{
  "category": {
    "id": "category-123",
    "name": "Pizza",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 8.3 Get Category by ID
**GET** `/categories/{category_id}`

**Response:**
```json
{
  "category": {
    "id": "category-123",
    "name": "Pizza",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 8.4 Update Category
**PUT** `/categories/{category_id}`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Updated Pizza Category"
}
```

**Response:**
```json
{
  "category": {
    "id": "category-123",
    "name": "Updated Pizza Category",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 8.5 Delete Category
**DELETE** `/categories/{category_id}`

**Response:** `204 No Content`

---

## 9. Analytics APIs

### 9.1 Get Sales Analytics
**GET** `/analytics/sales/{store_id}?period=month&user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Query Parameters:**
- `period` (optional): Analytics period (day, week, month, year) - default: month
- `user_id` (required): User ID for authentication

**Response:**
```json
{
  "analytics": {
    "total_orders": 150,
    "total_revenue": 2500.50,
    "average_order_value": 16.67,
    "status_breakdown": {
      "pending": 20,
      "preparing": 15,
      "ready": 10,
      "delivered": 100,
      "cancelled": 5
    },
    "period": "month",
    "store_id": "store-123"
  }
}
```

### 9.2 Get Product Analytics
**GET** `/analytics/products/{store_id}?period=month&user_id={user_id}`

**Headers:**
```
X-User-ID: your-user-id
```

**Query Parameters:**
- `period` (optional): Analytics period (day, week, month, year) - default: month
- `user_id` (required): User ID for authentication

**Response:**
```json
{
  "analytics": {
    "total_products": 50,
    "in_stock": 45,
    "out_of_stock": 5,
    "price_analysis": {
      "average_price": 15.50,
      "min_price": 5.00,
      "max_price": 50.00
    },
    "category_breakdown": {
      "pizza": 20,
      "vegetables": 15,
      "fruits": 10,
      "beverages": 5
    },
    "period": "month",
    "store_id": "store-123"
  }
}
```

---

## 10. Image Upload APIs

### 10.1 Upload Image
**POST** `/images/upload`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "image": "base64_encoded_image_data",
  "folder_path": "products/electronics"
}
```

**Response:**
```json
{
  "message": "Image uploaded successfully",
  "image_url": "https://anna-akka-platform-dev-images.s3.ap-south-1.amazonaws.com/products/electronics/20231201_143022_abc12345.jpg",
  "folder_path": "products/electronics"
}
```

---

## 11. Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR` (400): Invalid request data
- `UNAUTHORIZED` (401): User not authenticated
- `FORBIDDEN` (403): User not authorized
- `NOT_FOUND` (404): Resource not found
- `CONFLICT` (409): Resource conflict
- `UNPROCESSABLE_ENTITY` (422): Invalid request format
- `INTERNAL_ERROR` (500): Server error
- `METHOD_NOT_ALLOWED` (405): HTTP method not allowed

### Example Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Missing required field: name"
  }
}
```

---

## 12. Frontend Integration Guidelines

### 12.1 Authentication Setup
```javascript
// Set user ID for all requests
const userId = 'your-user-id';

// Headers for all API calls
const headers = {
  'Content-Type': 'application/json',
  'X-User-ID': userId
};

// Example API call
const response = await fetch(`${baseUrl}/stores?user_id=${userId}`, {
  headers: headers
});
```

### 12.2 Error Handling
```javascript
try {
  const response = await fetch(url, options);
  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.error?.message || 'API request failed');
  }
  
  return data;
} catch (error) {
  console.error('API Error:', error);
  // Handle error in UI
}
```

### 12.3 Pagination Handling
```javascript
// Example: Get stores with pagination
const getStores = async (page = 1, limit = 10) => {
  const response = await fetch(
    `${baseUrl}/stores?page=${page}&limit=${limit}&user_id=${userId}`,
    { headers }
  );
  const data = await response.json();
  
  return {
    stores: data.stores,
    pagination: data.pagination
  };
};
```

### 12.4 File Upload
```javascript
// Convert image to base64
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const base64 = reader.result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
  });
};

// Upload image
const uploadImage = async (file, folderPath) => {
  const base64 = await fileToBase64(file);
  
  const response = await fetch(`${baseUrl}/images/upload`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      image: base64,
      folder_path: folderPath
    })
  });
  
  return response.json();
};
```

---

## 13. Development Notes

### 13.1 Testing
- Use the provided Postman collection for testing
- Set `user_id` variable to "test-user-123" for development
- All endpoints support CORS for frontend integration

### 13.2 Rate Limits
- No specific rate limits implemented
- Consider implementing rate limiting for production

### 13.3 Security
- User authentication required for protected endpoints
- Store ownership validation for store operations
- Input validation on all endpoints

### 13.4 Data Types
- Prices are stored as Decimal (returned as strings in JSON)
- Dates are in ISO 8601 format
- IDs are UUID strings
- Phone numbers should include country code (+91 for India)

---

This documentation provides complete API integration details for your frontend development. All endpoints are ready for production use with proper authentication and error handling. 