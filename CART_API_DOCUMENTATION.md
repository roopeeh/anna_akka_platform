# Cart API Documentation

## Overview

The Cart API provides comprehensive cart management functionality for the Anna Akka Platform. The cart system allows customers to:

- Add products to cart
- Update product quantities
- Remove products from cart
- View cart contents
- Clear entire cart
- Create orders from cart items

## Cart Features

### Key Features
- **Persistent Storage**: Cart items are saved until order completion or manual removal
- **TTL (Time To Live)**: Cart items automatically expire after 30 days
- **Store-based Organization**: Cart items are organized by store
- **Stock Validation**: Real-time stock validation when adding/updating items
- **Price Locking**: Product prices are captured at time of adding to cart
- **Quantity Limits**: Maximum quantity per item (100) and total items (50)

### Cart Item Structure
```json
{
  "customer_id": "customer-123",
  "product_id": "prod-456",
  "store_id": "store-789",
  "quantity": 3,
  "price": 25.50,
  "product_name": "Fresh Tomatoes",
  "product_image": "https://example.com/tomatoes.jpg",
  "unit": "kg",
  "expires_at": 1704067200,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## API Endpoints

### 1. Get Cart
**GET** `/cart`

Retrieves the current customer's cart with all items organized by store.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Response (200 - OK):**
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
  },
  "body": "{\"customer_id\": \"customer-123\", \"items\": [{\"customer_id\": \"customer-123\", \"product_id\": \"prod-456\", \"store_id\": \"store-789\", \"quantity\": 3, \"price\": 25.50, \"product_name\": \"Fresh Tomatoes\", \"product_image\": \"https://example.com/tomatoes.jpg\", \"unit\": \"kg\", \"expires_at\": 1704067200, \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}], \"total_items\": 1, \"total_quantity\": 3, \"total_amount\": 76.50, \"stores\": [{\"store_id\": \"store-789\", \"items\": [{\"customer_id\": \"customer-123\", \"product_id\": \"prod-456\", \"store_id\": \"store-789\", \"quantity\": 3, \"price\": 25.50, \"product_name\": \"Fresh Tomatoes\", \"product_image\": \"https://example.com/tomatoes.jpg\", \"unit\": \"kg\", \"expires_at\": 1704067200, \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}], \"total_amount\": 76.50}]}"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Server error

### 2. Add Item to Cart
**POST** `/cart/items`

Adds a product to the customer's cart.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Request Body:**
```json
{
  "product_id": "prod-456",
  "quantity": 3,
  "store_id": "store-789"
}
```

**Required Fields:**
- `product_id`: Product ID to add to cart
- `quantity`: Quantity to add (1-100)

**Optional Fields:**
- `store_id`: Store ID (if not provided, will be retrieved from product)

**Response (201 - Created):**
```json
{
  "statusCode": 201,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
  },
  "body": "{\"message\": \"Item added to cart successfully\", \"cart\": {\"customer_id\": \"customer-123\", \"items\": [{\"customer_id\": \"customer-123\", \"product_id\": \"prod-456\", \"store_id\": \"store-789\", \"quantity\": 3, \"price\": 25.50, \"product_name\": \"Fresh Tomatoes\", \"product_image\": \"https://example.com/tomatoes.jpg\", \"unit\": \"kg\", \"expires_at\": 1704067200, \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}], \"total_items\": 1, \"total_quantity\": 3, \"total_amount\": 76.50, \"stores\": [{\"store_id\": \"store-789\", \"items\": [{\"customer_id\": \"customer-123\", \"product_id\": \"prod-456\", \"store_id\": \"store-789\", \"quantity\": 3, \"price\": 25.50, \"product_name\": \"Fresh Tomatoes\", \"product_image\": \"https://example.com/tomatoes.jpg\", \"unit\": \"kg\", \"expires_at\": 1704067200, \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}], \"total_amount\": 76.50}]}}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields, invalid quantity, insufficient stock
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Product not found
- `500 Internal Server Error`: Server error

### 3. Update Cart Item
**PUT** `/cart/items/{product_id}`

Updates the quantity of a specific product in the cart.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Path Parameters:**
- `product_id`: Product ID to update

**Request Body:**
```json
{
  "quantity": 5
}
```

**Required Fields:**
- `quantity`: New quantity (0-100, 0 removes the item)

**Response (200 - OK):**
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
  },
  "body": "{\"message\": \"Cart item updated successfully\", \"cart\": {\"customer_id\": \"customer-123\", \"items\": [{\"customer_id\": \"customer-123\", \"product_id\": \"prod-456\", \"store_id\": \"store-789\", \"quantity\": 5, \"price\": 25.50, \"product_name\": \"Fresh Tomatoes\", \"product_image\": \"https://example.com/tomatoes.jpg\", \"unit\": \"kg\", \"expires_at\": 1704067200, \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}], \"total_items\": 1, \"total_quantity\": 5, \"total_amount\": 127.50, \"stores\": [{\"store_id\": \"store-789\", \"items\": [{\"customer_id\": \"customer-123\", \"product_id\": \"prod-456\", \"store_id\": \"store-789\", \"quantity\": 5, \"price\": 25.50, \"product_name\": \"Fresh Tomatoes\", \"product_image\": \"https://example.com/tomatoes.jpg\", \"unit\": \"kg\", \"expires_at\": 1704067200, \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}], \"total_amount\": 127.50}]}}"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid quantity, insufficient stock, cart item not found
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Product not found
- `500 Internal Server Error`: Server error

### 4. Remove Item from Cart
**DELETE** `/cart/items/{product_id}`

Removes a specific product from the cart.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Path Parameters:**
- `product_id`: Product ID to remove

**Response (200 - OK):**
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
  },
  "body": "{\"message\": \"Item removed from cart successfully\", \"cart\": {\"customer_id\": \"customer-123\", \"items\": [], \"total_items\": 0, \"total_quantity\": 0, \"total_amount\": 0, \"stores\": []}}"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Server error

### 5. Clear Cart
**DELETE** `/cart`

Removes all items from the customer's cart.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Response (200 - OK):**
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
  },
  "body": "{\"message\": \"Cart cleared successfully\"}"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Server error

## Order Creation from Cart

### Create Order from Cart
**POST** `/orders`

Creates an order from cart items for a specific store.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Request Body:**
```json
{
  "create_from_cart": true,
  "store_id": "store-789",
  "delivery_address": "123 Main St, Bangalore",
  "notes": "Please call before delivery"
}
```

**Required Fields:**
- `create_from_cart`: Must be `true` to create from cart
- `store_id`: Store ID to create order for
- `delivery_address`: Delivery address

**Optional Fields:**
- `notes`: Order notes

**Response (201 - Created):**
```json
{
  "statusCode": 201,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
  },
  "body": "{\"message\": \"Order created successfully from cart\", \"order\": {\"id\": \"order-123\", \"customer_id\": \"customer-123\", \"store_id\": \"store-789\", \"delivery_address\": \"123 Main St, Bangalore\", \"status\": \"pending\", \"total_amount\": 76.50, \"notes\": \"Please call before delivery\", \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}, \"items\": [{\"product_id\": \"prod-456\", \"quantity\": 3, \"price\": 25.50, \"product_name\": \"Fresh Tomatoes\", \"unit\": \"kg\"}], \"total_amount\": 76.50}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields, no items in cart for store
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Server error

## Cart Configuration

### Cart Limits
- **Maximum Quantity per Item**: 100
- **Maximum Items per Cart**: 50
- **Cart TTL**: 30 days (automatic expiration)

### Cart Validation Rules
1. **Stock Validation**: Cannot add more items than available stock
2. **Store Validation**: Products must belong to the specified store
3. **Price Locking**: Product prices are captured at time of adding to cart
4. **Quantity Limits**: Enforced maximum quantities
5. **TTL Management**: Automatic cleanup of expired items

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Invalid input data |
| `UNAUTHORIZED` | Invalid or missing authentication |
| `NOT_FOUND` | Resource not found |
| `INTERNAL_ERROR` | Server error |

## Best Practices

### For Frontend Implementation
1. **Real-time Updates**: Refresh cart after each operation
2. **Loading States**: Show loading indicators during cart operations
3. **Error Handling**: Display user-friendly error messages
4. **Validation**: Validate quantities before sending requests
5. **Optimistic Updates**: Update UI immediately, rollback on error

### For Backend Integration
1. **Stock Validation**: Always validate stock before cart operations
2. **Price Updates**: Handle price changes gracefully
3. **Cart Cleanup**: Implement TTL cleanup for expired items
4. **Order Integration**: Clear cart items after successful order creation
5. **Error Recovery**: Implement proper error handling and logging

## Example Usage

### Complete Cart Workflow

1. **Add Items to Cart**
```bash
curl -X POST /cart/items \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "prod-456",
    "quantity": 3,
    "store_id": "store-789"
  }'
```

2. **View Cart**
```bash
curl -X GET /cart \
  -H "Authorization: Bearer <token>"
```

3. **Update Item Quantity**
```bash
curl -X PUT /cart/items/prod-456 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 5
  }'
```

4. **Create Order from Cart**
```bash
curl -X POST /orders \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "create_from_cart": true,
    "store_id": "store-789",
    "delivery_address": "123 Main St, Bangalore",
    "notes": "Please call before delivery"
  }'
```

This cart system provides a robust, scalable solution for managing customer shopping carts with automatic cleanup, validation, and seamless integration with the order creation process. 