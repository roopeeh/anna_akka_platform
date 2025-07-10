# Cart API Integration Guide for Frontend

## Overview
This guide provides the complete API documentation for integrating frontend applications with the Anna Akka Platform's cart functionality. All endpoints require authentication via Firebase JWT tokens.

## Base Configuration
- **Base URL**: Your deployed API Gateway URL
- **Authentication**: `Authorization: Bearer <firebase-jwt-token>`
- **Content-Type**: `application/json`
- **CORS**: Enabled for all origins

## API Endpoints

### 1. Get Cart Contents
**GET** `/cart`

Retrieves the current user's cart with all items organized by store.

**Headers:**
```
Authorization: Bearer <firebase-jwt-token>
Content-Type: application/json
```

**Response (200):**
```json
{
  "cart": {
    "customer_id": "customer-123",
    "items": [
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
    ],
    "total_items": 1,
    "total_quantity": 3,
    "total_amount": 76.50,
    "stores": [
      {
        "store_id": "store-789",
        "items": [...],
        "total_amount": 76.50
      }
    ]
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Server error

### 2. Add Item to Cart
**POST** `/cart/items`

Adds a product to the user's cart.

**Headers:**
```
Authorization: Bearer <firebase-jwt-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "product_id": "prod-456",
  "quantity": 3
}
```

**Required Fields:**
- `product_id`: Product ID to add to cart
- `quantity`: Quantity to add (1-100)

**Response (201):**
```json
{
  "message": "Item added to cart successfully",
  "cart": {
    "customer_id": "customer-123",
    "items": [...],
    "total_items": 1,
    "total_quantity": 3,
    "total_amount": 76.50,
    "stores": [...]
  }
}
```

**Error Responses:**
- `400 Bad Request`: Missing fields, invalid quantity, product not found
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Server error

### 3. Update Cart Item Quantity
**PUT** `/cart/items/{product_id}`

Updates the quantity of a specific product in the cart.

**Headers:**
```
Authorization: Bearer <firebase-jwt-token>
Content-Type: application/json
```

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

**Response (200):**
```json
{
  "message": "Cart item updated successfully",
  "cart": {
    "customer_id": "customer-123",
    "items": [...],
    "total_items": 1,
    "total_quantity": 5,
    "total_amount": 127.50,
    "stores": [...]
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid quantity, cart item not found
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Product not found
- `500 Internal Server Error`: Server error

### 4. Remove Item from Cart
**DELETE** `/cart/items/{product_id}`

Removes a specific product from the cart.

**Headers:**
```
Authorization: Bearer <firebase-jwt-token>
```

**Path Parameters:**
- `product_id`: Product ID to remove

**Response (200):**
```json
{
  "message": "Item removed from cart successfully",
  "cart": {
    "customer_id": "customer-123",
    "items": [],
    "total_items": 0,
    "total_quantity": 0,
    "total_amount": 0,
    "stores": []
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Cart item not found
- `500 Internal Server Error`: Server error

### 5. Clear Entire Cart
**DELETE** `/cart`

Removes all items from the user's cart.

**Headers:**
```
Authorization: Bearer <firebase-jwt-token>
```

**Response (200):**
```json
{
  "message": "Cart cleared successfully"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Server error

## Frontend Integration Examples

### JavaScript/TypeScript Examples

#### 1. Get Cart Contents
```javascript
async function getCart() {
  try {
    const response = await fetch('/cart', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${firebaseToken}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      return data.cart;
    } else {
      throw new Error('Failed to get cart');
    }
  } catch (error) {
    console.error('Error getting cart:', error);
    throw error;
  }
}
```

#### 2. Add Item to Cart
```javascript
async function addToCart(productId, quantity) {
  try {
    const response = await fetch('/cart/items', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${firebaseToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        product_id: productId,
        quantity: quantity
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      return data.cart;
    } else {
      const errorData = await response.json();
      throw new Error(errorData.error.message);
    }
  } catch (error) {
    console.error('Error adding to cart:', error);
    throw error;
  }
}
```

#### 3. Update Cart Item
```javascript
async function updateCartItem(productId, quantity) {
  try {
    const response = await fetch(`/cart/items/${productId}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${firebaseToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        quantity: quantity
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      return data.cart;
    } else {
      const errorData = await response.json();
      throw new Error(errorData.error.message);
    }
  } catch (error) {
    console.error('Error updating cart item:', error);
    throw error;
  }
}
```

#### 4. Remove Item from Cart
```javascript
async function removeFromCart(productId) {
  try {
    const response = await fetch(`/cart/items/${productId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${firebaseToken}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      return data.cart;
    } else {
      const errorData = await response.json();
      throw new Error(errorData.error.message);
    }
  } catch (error) {
    console.error('Error removing from cart:', error);
    throw error;
  }
}
```

#### 5. Clear Cart
```javascript
async function clearCart() {
  try {
    const response = await fetch('/cart', {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${firebaseToken}`
      }
    });
    
    if (response.ok) {
      return { message: 'Cart cleared successfully' };
    } else {
      const errorData = await response.json();
      throw new Error(errorData.error.message);
    }
  } catch (error) {
    console.error('Error clearing cart:', error);
    throw error;
  }
}
```

### React Hook Example
```javascript
import { useState, useEffect } from 'react';

function useCart() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCart = async () => {
    setLoading(true);
    setError(null);
    try {
      const cartData = await getCart();
      setCart(cartData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addItem = async (productId, quantity) => {
    setLoading(true);
    setError(null);
    try {
      const updatedCart = await addToCart(productId, quantity);
      setCart(updatedCart);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateItem = async (productId, quantity) => {
    setLoading(true);
    setError(null);
    try {
      const updatedCart = await updateCartItem(productId, quantity);
      setCart(updatedCart);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const removeItem = async (productId) => {
    setLoading(true);
    setError(null);
    try {
      const updatedCart = await removeFromCart(productId);
      setCart(updatedCart);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const clearCart = async () => {
    setLoading(true);
    setError(null);
    try {
      await clearCart();
      setCart(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  return {
    cart,
    loading,
    error,
    addItem,
    updateItem,
    removeItem,
    clearCart,
    refreshCart: fetchCart
  };
}
```

## Data Structures

### Cart Item Structure
```typescript
interface CartItem {
  customer_id: string;
  product_id: string;
  store_id: string;
  quantity: number;
  price: number;
  product_name: string;
  product_image: string;
  unit: string;
  expires_at: number;
  created_at: string;
  updated_at: string;
}
```

### Cart Response Structure
```typescript
interface Cart {
  customer_id: string;
  items: CartItem[];
  total_items: number;
  total_quantity: number;
  total_amount: number;
  stores: StoreGroup[];
}

interface StoreGroup {
  store_id: string;
  items: CartItem[];
  total_amount: number;
}
```

## Error Handling

### Error Response Structure
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Quantity must be greater than 0"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Invalid input data
- `UNAUTHORIZED`: Invalid or missing authentication
- `NOT_FOUND`: Resource not found
- `INTERNAL_ERROR`: Server error

## Cart Configuration Limits
- **Maximum Quantity per Item**: 100
- **Maximum Items per Cart**: 50
- **Cart TTL**: 30 days (automatic expiration)

## Best Practices for Frontend Integration

1. **Real-time Updates**: Refresh cart after each operation
2. **Loading States**: Show loading indicators during cart operations
3. **Error Handling**: Display user-friendly error messages
4. **Validation**: Validate quantities before sending requests
5. **Optimistic Updates**: Update UI immediately, rollback on error
6. **Token Management**: Ensure Firebase token is valid and refreshed
7. **CORS Handling**: Handle CORS preflight requests properly

## Testing the Integration

### Test Cart Operations
```javascript
// Test sequence
async function testCartOperations() {
  try {
    // 1. Get empty cart
    let cart = await getCart();
    console.log('Initial cart:', cart);
    
    // 2. Add item
    cart = await addToCart('prod-123', 2);
    console.log('After adding item:', cart);
    
    // 3. Update quantity
    cart = await updateCartItem('prod-123', 5);
    console.log('After updating quantity:', cart);
    
    // 4. Remove item
    cart = await removeFromCart('prod-123');
    console.log('After removing item:', cart);
    
    // 5. Clear cart
    await clearCart();
    console.log('Cart cleared');
    
  } catch (error) {
    console.error('Test failed:', error);
  }
}
```

This API integration guide provides everything needed to connect frontend applications with the cart backend functionality. All endpoints are RESTful, use standard HTTP methods, and return consistent JSON responses. 