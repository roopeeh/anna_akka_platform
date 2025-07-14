# Anna Akka Platform - Complete API Documentation

## Overview
This document provides comprehensive documentation for all API endpoints in the Anna Akka Platform, including authentication, user management, stores, products, orders, categories, profile management, and analytics.

## Base URL
- Development: `https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev`
- Production: `https://your-api-gateway-url/prod`

## Authentication
The API uses JWT tokens for authentication. The system supports authentication using either user ID or phone number for enhanced flexibility.

### Headers
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

### Authentication Methods
1. **User ID**: Primary authentication method using user ID
2. **Phone Number**: Alternative authentication method for users who prefer phone-based login
3. **Combined**: Enhanced validation using both user ID and phone number

### Database Optimizations
- **Global Secondary Indexes (GSI)**: Optimized phone and email lookups using DynamoDB GSIs
- **Efficient Queries**: Phone and email searches use O(1) query operations instead of O(n) scan operations
- **Performance**: Significantly faster response times and reduced DynamoDB read capacity usage

## Common Response Format

### Success Response
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"data\": {...}}"
}
```

### Error Response
```json
{
  "statusCode": 400,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"error\": {\"code\": \"VALIDATION_ERROR\", \"message\": \"Error description\"}}"
}
```

## API Endpoints

### 1. Authentication Endpoints

#### POST /auth/register
Register a new user account.

**Description:** Creates a new user account using user ID for authentication. The system performs comprehensive validation including phone number uniqueness checks using optimized DynamoDB Global Secondary Indexes (GSI).

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "user_id": "user-123",
  "roles": ["customer", "admin"],
  "phone": "+91 98765 43210",
  "address": "123 Main St, Bangalore"
}
```

**Required Fields:**
- `email`: User's email address
- `name`: User's full name
- `user_id`: User ID

**Optional Fields:**
- `roles`: Array of roles - can include "customer", "vendor", "admin" (default: ["customer"])
- `phone`: Phone number
- `address`: Delivery address

**Phone Number Validation:**
The registration endpoint performs comprehensive phone number validation:
- **Format Support**: Accepts various formats (with/without spaces, with/without + prefix)
- **Normalization**: Automatically normalizes to consistent format (`+919876543210`)
- **Duplicate Check**: Validates that phone number is not already registered using GSI
- **Uniqueness**: Ensures phone number uniqueness across all users

**Supported Phone Number Formats:**
- `+91 98765 43210` (with spaces)
- `+919876543210` (without spaces)
- `91 98765 43210` (without + prefix)
- `919876543210` (minimal format)

**Validation Process:**
1. Phone number format validation
2. Normalization to consistent format
3. Check for existing phone number in database using GSI
4. If duplicate found, returns 409 Conflict error
5. If unique, proceeds with user creation

**Database Optimizations:**
- Uses DynamoDB GSI for O(1) phone number lookups
- Uses DynamoDB GSI for O(1) email lookups
- Significantly faster validation compared to table scans

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
  "body": "{\"user\": {\"id\": \"firebase-auth-uid-123\", \"email\": \"user@example.com\", \"name\": \"John Doe\", \"roles\": [\"customer\", \"admin\"], \"phone\": \"+919876543210\", \"address\": \"123 Main St, Bangalore\", \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields or invalid roles
- `409 Conflict`: User already exists with user ID, email, or phone number

#### POST /auth/login
Authenticate user using user ID or phone number.

**Description:** Validates user existence using user ID or phone number for login. The system will try user ID first, then fall back to phone number if user is not found.

**Request Body (User ID):**
```json
{
  "user_id": "user-123"
}
```

**Request Body (Phone Number):**
```json
{
  "phone": "+91 98765 43210"
}
```

**Request Body (Both - for enhanced validation):**
```json
{
  "user_id": "user-123",
  "phone": "+91 98765 43210"
}
```

**Required Fields:**
- Either `user_id` OR `phone` (at least one must be provided)

**Phone Number Support:**
The login endpoint supports various phone number formats:
- `+91 98765 43210` (with spaces)
- `+919876543210` (without spaces)
- `91 98765 43210` (without + prefix)
- `919876543210` (minimal format)

**Phone Number Normalization:**
Phone numbers are automatically normalized to consistent format:
- Spaces are removed
- + prefix is added if missing
- Final format: `+919876543210`

**Login Priority:**
1. User ID (if provided) - checked first
2. Phone number (if provided) - checked if user ID not found or not provided

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
  "body": "{\"user\": {\"id\": \"firebase-auth-uid-123\", \"email\": \"user@example.com\", \"name\": \"John Doe\", \"roles\": [\"customer\", \"admin\"], \"phone\": \"+919876543210\", \"address\": \"123 Main St, Bangalore\", \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing both user_id and phone
- `401 Unauthorized`: User not found with provided identifiers

#### GET /auth/user/phone
Search user by phone number.

**Description:** Retrieves user information by phone number for validation purposes. This endpoint uses the optimized DynamoDB Global Secondary Index (GSI) for fast phone number lookups.

**Query Parameters:**
- `phone` (required): Phone number to search for (supports various formats)

**Supported Phone Number Formats:**
- `+91 98765 43210` (with spaces)
- `+919876543210` (without spaces)
- `91 98765 43210` (without + prefix)
- `919876543210` (minimal format)

**Phone Number Normalization:**
The system automatically normalizes phone numbers by:
- Removing all spaces
- Adding + prefix if missing
- Converting to consistent format: `+919876543210`

**Example Requests:**
```
GET /auth/user/phone?phone=+91 98765 43210
GET /auth/user/phone?phone=+919876543210
GET /auth/user/phone?phone=91 98765 43210
```

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
  "body": "{\"user\": {\"id\": \"firebase-auth-uid-123\", \"email\": \"user@example.com\", \"name\": \"John Doe\", \"phone\": \"+919876543210\", \"roles\": [\"customer\", \"admin\"], \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing phone parameter
- `404 Not Found`: User not found with provided phone number

**Performance:**
- Uses DynamoDB GSI for O(1) lookup performance
- Response time: < 100ms typically
- Supports high-throughput phone number searches

### 2. Profile Management Endpoints

#### GET /profile
Get current user's profile.

**Description:** Retrieves the profile information for the authenticated user.

**Headers:** `Authorization: Bearer <jwt-token>`

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
  "body": "{\"user\": {\"id\": \"efbea127-1840-4f3c-b3ae-c38371b3ffea\", \"email\": \"user@example.com\", \"name\": \"John Doe\", \"roles\": [\"customer\"], \"phone\": \"+919876543210\", \"address\": \"123 Main St, Bangalore\", \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}}"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: User not found

#### PUT /profile
Update current user's profile.

**Description:** Updates the profile information for the authenticated user.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Request Body:**
```json
{
  "name": "John Smith",
  "phone": "+91 98765 43211",
  "address": "456 Oak Ave, Mumbai",
  "email": "john.smith@example.com"
}
```

**Optional Fields:**
- `name`: Updated name
- `phone`: Updated phone number (automatically normalized)
- `address`: Updated address
- `email`: Updated email address

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
  "body": "{\"user\": {\"id\": \"efbea127-1840-4f3c-b3ae-c38371b3ffea\", \"email\": \"john.smith@example.com\", \"name\": \"John Smith\", \"roles\": [\"customer\"], \"phone\": \"+919876543211\", \"address\": \"456 Oak Ave, Mumbai\", \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T11:45:00Z\"}}"
}
```

**Error Responses:**
- `400 Bad Request`: No valid fields provided for update
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: User not found

#### DELETE /profile
Delete current user's profile.

**Description:** Permanently deletes the user profile and all associated data.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Response (204 - No Content):**
```json
{
  "statusCode": 204,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
  },
  "body": "{\"message\": \"User profile deleted successfully\", \"deleted_user\": {\"id\": \"efbea127-1840-4f3c-b3ae-c38371b3ffea\", \"email\": \"user@example.com\", \"name\": \"John Doe\", \"roles\": [\"customer\"], \"phone\": \"+919876543210\", \"address\": \"123 Main St, Bangalore\", \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T11:45:00Z\"}}"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: User not found

#### GET /profile/phone?phone=<phone_number>
Get user profile by phone number.

**Description:** Retrieves user profile information by phone number. This endpoint is useful for looking up users by their phone number without requiring authentication.

**Query Parameters:**
- `phone`: Phone number to search for (required)

**Supported Phone Number Formats:**
- `+91 98765 43210` (with spaces)
- `+919876543210` (without spaces)
- `91 98765 43210` (without + prefix)
- `919876543210` (minimal format)

**Example Requests:**
```
GET /profile/phone?phone=+919876543210
GET /profile/phone?phone=91 98765 43210
```

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
  "body": "{\"user\": {\"id\": \"efbea127-1840-4f3c-b3ae-c38371b3ffea\", \"email\": \"user@example.com\", \"name\": \"John Doe\", \"phone\": \"+919876543210\", \"roles\": [\"customer\"], \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing phone parameter or invalid phone format
- `404 Not Found`: User not found with provided phone number

**Performance:**
- Uses DynamoDB GSI for O(1) lookup performance
- Response time: < 100ms typically
- Supports high-throughput phone number searches

### 3. Available Products Endpoints

#### GET /available-products
Get all available market products with pagination and filtering.

**Description:** Retrieves the general catalog of available products that can be added to stores.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `category_id` (optional): Filter by category ID
- `search` (optional): Search by product name
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter

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
  "body": "{\"products\": [{\"id\": \"prod-123\", \"name\": \"Margherita Pizza\", \"description\": \"Classic tomato and mozzarella pizza\", \"price\": 12.99, \"unit\": \"piece\", \"category_id\": \"cat-123\", \"image_url\": \"https://example.com/pizza.jpg\", \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}], \"pagination\": {\"current_page\": 1, \"total_pages\": 5, \"total_items\": 100, \"items_per_page\": 20}}"
}
```

#### GET /available-products/{id}
Get a specific available product by ID.

**Description:** Retrieves details of a specific available product from the catalog.

**Path Parameters:**
- `id`: Available product ID

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
  "body": "{\"product\": {\"id\": \"prod-123\", \"name\": \"Margherita Pizza\", \"description\": \"Classic tomato and mozzarella pizza\", \"price\": 12.99, \"unit\": \"piece\", \"category_id\": \"cat-123\", \"image_url\": \"https://example.com/pizza.jpg\", \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}}"
}
```

**Error Responses:**
- `404 Not Found`: Available product not found

#### POST /available-products
Create a new available product in the catalog.

**Description:** Adds a new product to the general available products catalog.

**Request Body:**
```json
{
  "name": "Pepperoni Pizza",
  "description": "Spicy pepperoni with melted cheese",
  "price": 14.99,
  "unit": "piece",
  "category_id": "cat-123",
  "image_url": "https://example.com/pepperoni.jpg"
}
```

**Required Fields:**
- `name`: Product name
- `price`: Product price

**Optional Fields:**
- `description`: Product description
- `unit`: Product unit (default: "piece")
- `category_id`: Category ID
- `image_url`: Product image URL

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
  "body": "{\"product\": {\"id\": \"prod-456\", \"name\": \"Pepperoni Pizza\", \"description\": \"Spicy pepperoni with melted cheese\", \"price\": 14.99, \"unit\": \"piece\", \"category_id\": \"cat-123\", \"image_url\": \"https://example.com/pepperoni.jpg\", \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields

#### PUT /available-products/{id}
Update an available product in the catalog.

**Description:** Updates an existing product in the available products catalog.

**Path Parameters:**
- `id`: Available product ID

**Request Body:**
```json
{
  "name": "Updated Pepperoni Pizza",
  "price": 15.99,
  "description": "Updated description"
}
```

**Optional Fields:**
- `name`: Updated product name
- `description`: Updated product description
- `price`: Updated product price
- `unit`: Updated product unit
- `category_id`: Updated category ID
- `image_url`: Updated product image URL

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
  "body": "{\"product\": {\"id\": \"prod-456\", \"name\": \"Updated Pepperoni Pizza\", \"description\": \"Updated description\", \"price\": 15.99, \"unit\": \"piece\", \"category_id\": \"cat-123\", \"image_url\": \"https://example.com/pepperoni.jpg\", \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T11:45:00Z\"}}"
}
```

**Error Responses:**
- `400 Bad Request`: No valid fields provided for update
- `404 Not Found`: Available product not found

#### DELETE /available-products/{id}
Delete an available product from the catalog.

**Description:** Removes a product from the available products catalog.

**Path Parameters:**
- `id`: Available product ID

**Response (204 - No Content):**
```json
{
  "statusCode": 204,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
  },
  "body": ""
}
```

**Error Responses:**
- `404 Not Found`: Available product not found

### 4. Store Management Endpoints

#### GET /stores
Get all available stores with pagination and filtering.

**Description:** Retrieves a paginated list of stores with optional filtering.

**Query Parameters:**
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Items per page (default: 10)
- `search` (optional): Search term for store name
- `is_open` (optional): Filter by open status (true/false)

**Example Request:**
```
GET /stores?page=1&limit=5&search=fresh&is_open=true
```

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
  "body": "{\"stores\": [{\"id\": \"store1\", \"owner_id\": \"user-123\", \"name\": \"Fresh Market Store\", \"address\": \"123 Market Street, Bangalore\", \"phone\": \"+91 98765 43210\", \"is_open\": true, \"rating\": 4.5, \"delivery_time\": \"30-45 min\", \"created_at\": \"2024-01-10T08:00:00Z\", \"updated_at\": \"2024-01-15T09:30:00Z\"}], \"pagination\": {\"current_page\": 1, \"total_pages\": 5, \"total_items\": 45, \"items_per_page\": 10}}"
}
```

#### GET /stores/{id}
Get specific store details.

**Description:** Retrieves detailed information about a specific store.

**Path Parameters:**
- `id`: Store ID

**Example Request:**
```
GET /stores/store1
```

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
  "body": "{\"store\": {\"id\": \"store1\", \"owner_id\": \"user-123\", \"name\": \"Fresh Market Store\", \"address\": \"123 Market Street, Bangalore\", \"phone\": \"+91 98765 43210\", \"is_open\": true, \"rating\": 4.5, \"delivery_time\": \"30-45 min\", \"created_at\": \"2024-01-10T08:00:00Z\", \"updated_at\": \"2024-01-15T09:30:00Z\"}}"
}
```

**Error Responses:**
- `404 Not Found`: Store not found

#### POST /stores
Create a new store (Owner only).

**Description:** Creates a new store for the authenticated owner.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Request Body:**
```json
{
  "name": "New Grocery Store",
  "address": "789 New Street, Delhi",
  "phone": "+91 87654 32109",
  "delivery_time": "25-40 min"
}
```

**Required Fields:**
- `name`: Store name
- `address`: Store address

**Optional Fields:**
- `phone`: Store phone number
- `delivery_time`: Estimated delivery time

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
  "body": "{\"id\": \"store-generated-id\", \"owner_id\": \"user-123\", \"name\": \"New Grocery Store\", \"address\": \"789 New Street, Delhi\", \"phone\": \"+91 87654 32109\", \"is_open\": true, \"rating\": 0, \"delivery_time\": \"25-40 min\", \"created_at\": \"2024-01-15T12:00:00Z\", \"updated_at\": \"2024-01-15T12:00:00Z\"}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields
- `401 Unauthorized`: Invalid or missing token

#### PUT /stores/{id}
Update store details (Owner only).

**Description:** Updates store information for the authenticated owner.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Path Parameters:**
- `id`: Store ID

**Request Body:**
```json
{
  "name": "Updated Store Name",
  "is_open": false,
  "delivery_time": "35-50 min"
}
```

**Optional Fields:**
- `name`: Updated store name
- `address`: Updated address
- `phone`: Updated phone number
- `is_open`: Store open status
- `delivery_time`: Updated delivery time

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
  "body": "{\"id\": \"store1\", \"owner_id\": \"user-123\", \"name\": \"Updated Store Name\", \"address\": \"123 Market Street, Bangalore\", \"phone\": \"+91 98765 43210\", \"is_open\": false, \"rating\": 4.5, \"delivery_time\": \"35-50 min\", \"created_at\": \"2024-01-10T08:00:00Z\", \"updated_at\": \"2024-01-15T13:15:00Z\"}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Store not found
- `403 Forbidden`: Not authorized to update this store

#### DELETE /stores/{id}
Delete a store (Owner only).

**Description:** Deletes a store for the authenticated owner.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Path Parameters:**
- `id`: Store ID

**Response (204 - No Content):**
```json
{
  "statusCode": 204,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
  },
  "body": ""
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Store not found
- `403 Forbidden`: Not authorized to delete this store

#### GET /stores/owner
Get stores owned by current user (Owner only).

**Description:** Retrieves all stores owned by the authenticated user.

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
  "body": "{\"stores\": [{\"id\": \"store1\", \"owner_id\": \"user-123\", \"name\": \"My Grocery Store\", \"address\": \"123 Market Street, Bangalore\", \"phone\": \"+91 98765 43210\", \"is_open\": true, \"rating\": 4.5, \"delivery_time\": \"30-45 min\", \"created_at\": \"2024-01-10T08:00:00Z\", \"updated_at\": \"2024-01-15T09:30:00Z\"}]}"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token

### 4. Category Management Endpoints

#### GET /categories
Get all product categories.

**Description:** Retrieves all available product categories.

**Response (200 - OK):**
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
  },
  "body": "{\"categories\": [{\"id\": \"1\", \"name\": \"Rice & More\", \"created_at\": \"2024-01-10T08:00:00Z\"}, {\"id\": \"2\", \"name\": \"Household Essentials\", \"created_at\": \"2024-01-10T08:00:00Z\"}]}"
}
```

#### POST /categories
Create a new category.

**Description:** Creates a new product category.

**Request Body:**
```json
{
  "name": "Personal Care"
}
```

**Required Fields:**
- `name`: Category name

**Response (201 - Created):**
```json
{
  "statusCode": 201,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
  },
  "body": "{\"id\": \"cat-generated-id\", \"name\": \"Personal Care\", \"created_at\": \"2024-01-15T12:00:00Z\"}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing category name

### 5. Product Management Endpoints

#### GET /products
Get all products with pagination and filtering.

**Description:** Retrieves a paginated list of products with optional filtering.

**Query Parameters:**
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Items per page (default: 20)
- `store_id` (optional): Filter by store ID
- `category_id` (optional): Filter by category ID
- `search` (optional): Search term for product name
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter
- `in_stock` (optional): Filter by stock availability (true/false)

**Example Request:**
```
GET /products?page=1&limit=10&category_id=cat1&min_price=10&max_price=100&in_stock=true
```

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
  "body": "{\"products\": [{\"id\": \"prod1\", \"store_id\": \"store1\", \"category_id\": \"cat1\", \"name\": \"Fresh Tomatoes\", \"description\": \"Organic red tomatoes\", \"price\": 25.50, \"unit\": \"kg\", \"stock\": 50, \"image_url\": \"https://example.com/tomatoes.jpg\", \"created_at\": \"2024-01-10T08:00:00Z\", \"updated_at\": \"2024-01-15T09:30:00Z\"}], \"pagination\": {\"current_page\": 1, \"total_pages\": 5, \"total_items\": 45, \"items_per_page\": 10}}"
}
```

#### GET /products/{id}
Get specific product details.

**Description:** Retrieves detailed information about a specific product.

**Path Parameters:**
- `id`: Product ID

**Example Request:**
```
GET /products/prod1
```

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
  "body": "{\"product\": {\"id\": \"prod1\", \"store_id\": \"store1\", \"category_id\": \"cat1\", \"name\": \"Fresh Tomatoes\", \"description\": \"Organic red tomatoes\", \"price\": 25.50, \"unit\": \"kg\", \"stock\": 50, \"image_url\": \"https://example.com/tomatoes.jpg\", \"created_at\": \"2024-01-10T08:00:00Z\", \"updated_at\": \"2024-01-15T09:30:00Z\"}}"
}
```

**Error Responses:**
- `404 Not Found`: Product not found

#### GET /stores/{storeId}/products
Get products for a specific store.

**Description:** Retrieves all products for a specific store with pagination and filtering.

**Path Parameters:**
- `storeId`: Store ID

**Query Parameters:**
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Items per page (default: 20)
- `category_id` (optional): Filter by category ID
- `search` (optional): Search term for product name

**Example Request:**
```
GET /stores/store1/products?page=1&limit=10&category_id=cat1
```

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
  "body": "{\"products\": [{\"id\": \"prod1\", \"store_id\": \"store1\", \"category_id\": \"cat1\", \"name\": \"Fresh Tomatoes\", \"description\": \"Organic red tomatoes\", \"price\": 25.50, \"unit\": \"kg\", \"stock\": 50, \"image_url\": \"https://example.com/tomatoes.jpg\", \"created_at\": \"2024-01-10T08:00:00Z\", \"updated_at\": \"2024-01-15T09:30:00Z\"}], \"pagination\": {\"current_page\": 1, \"total_pages\": 3, \"total_items\": 25, \"items_per_page\": 10}}"
}
```

#### POST /stores/{storeId}/products
Create a new product for a store (Owner only).

**Description:** Creates a new product for the specified store. You can either add a product from the available products catalog or create a completely new product.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Path Parameters:**
- `storeId`: Store ID

**Request Body (Adding from Available Catalog):**
```json
{
  "available_product_id": "avail-prod-123",
  "price": 30.00,
  "stock": 25
}
```

**Request Body (Creating New Product):**
```json
{
  "name": "Fresh Carrots",
  "description": "Organic orange carrots",
  "price": 30.00,
  "unit": "kg",
  "stock": 25,
  "category_id": "cat1",
  "image_url": "https://example.com/carrots.jpg"
}
```

**Required Fields:**
- Either `available_product_id` (to add from catalog) OR `name` and `price` (to create new)

**Optional Fields (when creating new):**
- `description`: Product description
- `unit`: Unit of measurement (default: "piece")
- `stock`: Available stock (default: 0)
- `category_id`: Category ID
- `image_url`: Product image URL

**Optional Fields (when adding from catalog):**
- `price`: Store-specific price (overrides catalog price)
- `stock`: Available stock (default: 0)

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
  "body": "{\"id\": \"prod-generated-id\", \"store_id\": \"store1\", \"category_id\": \"cat1\", \"name\": \"Fresh Carrots\", \"description\": \"Organic orange carrots\", \"price\": 30.00, \"unit\": \"kg\", \"stock\": 25, \"image_url\": \"https://example.com/carrots.jpg\", \"created_at\": \"2024-01-15T12:00:00Z\", \"updated_at\": \"2024-01-15T12:00:00Z\"}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Not authorized to create products for this store

#### PUT /products/{id}
Update product details (Owner only).

**Description:** Updates product information for the authenticated owner.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Path Parameters:**
- `id`: Product ID

**Request Body:**
```json
{
  "name": "Updated Product Name",
  "price": 35.00,
  "stock": 30,
  "description": "Updated description"
}
```

**Optional Fields:**
- `name`: Updated product name
- `description`: Updated description
- `price`: Updated price
- `unit`: Updated unit
- `stock`: Updated stock
- `image_url`: Updated image URL
- `category_id`: Updated category ID

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
  "body": "{\"id\": \"prod1\", \"store_id\": \"store1\", \"category_id\": \"cat1\", \"name\": \"Updated Product Name\", \"description\": \"Updated description\", \"price\": 35.00, \"unit\": \"kg\", \"stock\": 30, \"image_url\": \"https://example.com/carrots.jpg\", \"created_at\": \"2024-01-10T08:00:00Z\", \"updated_at\": \"2024-01-15T13:15:00Z\"}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Product not found
- `403 Forbidden`: Not authorized to update this product

#### DELETE /products/{id}
Delete a product (Owner only).

**Description:** Deletes a product for the authenticated owner.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Path Parameters:**
- `id`: Product ID

**Response (204 - No Content):**
```json
{
  "statusCode": 204,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
  },
  "body": ""
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Product not found
- `403 Forbidden`: Not authorized to delete this product

### 5. Store Product IDs Management Endpoints

#### POST /stores/update-product-ids
Update all stores with their product IDs from available products.

**Description:** Updates all stores to include a list of available product IDs that each store has in their inventory. This endpoint automatically scans all stores and their products to build the product_ids list.

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
  "body": "{\"message\": \"Updated 5 stores with product IDs\", \"updated_count\": 5}"
}
```

#### POST /stores/{storeId}/update-product-ids
Update a specific store with its product IDs from available products.

**Description:** Updates a specific store to include a list of available product IDs that the store has in their inventory.

**Path Parameters:**
- `storeId`: Store ID

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
  "body": "{\"message\": \"Store product IDs updated successfully\", \"store\": {\"id\": \"store1\", \"name\": \"My Store\", \"product_ids\": [\"avail-prod-1\", \"avail-prod-2\", \"avail-prod-3\"], \"updated_at\": \"2024-01-15T14:30:00Z\"}}"
}
```

**Error Responses:**
- `404 Not Found`: Store not found
- `500 Internal Server Error`: Failed to update store product IDs

### 6. Order Management Endpoints

#### GET /orders
Get orders for the current user (Customer only).

**Description:** Retrieves all orders for the authenticated customer.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Query Parameters:**
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Items per page (default: 10)
- `status` (optional): Filter by order status
- `date_from` (optional): Filter orders from date (ISO format)
- `date_to` (optional): Filter orders to date (ISO format)

**Example Request:**
```
GET /orders?page=1&limit=5&status=pending
```

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
  "body": "{\"orders\": [{\"id\": \"order1\", \"customer_id\": \"customer-id\", \"store_id\": \"store1\", \"total_amount\": 180, \"delivery_address\": \"123 Main St, Bangalore\", \"status\": \"pending\", \"notes\": \"Please call before delivery\", \"created_at\": \"2024-01-15T10:00:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}], \"pagination\": {\"current_page\": 1, \"total_pages\": 5, \"total_items\": 48, \"items_per_page\": 10}}"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token

#### GET /orders/{id}
Get specific order details.

**Description:** Retrieves detailed information about a specific order.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Path Parameters:**
- `id`: Order ID

**Example Request:**
```
GET /orders/order1
```

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
  "body": "{\"order\": {\"id\": \"order1\", \"customer_id\": \"customer-id\", \"store_id\": \"store1\", \"total_amount\": 180, \"delivery_address\": \"123 Main St, Bangalore\", \"status\": \"pending\", \"notes\": \"Please call before delivery\", \"created_at\": \"2024-01-15T10:00:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}}"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Order not found
- `403 Forbidden`: Not authorized to view this order

#### POST /orders
Create a new order (Customer only).

**Description:** Creates a new order for the authenticated customer.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Request Body:**
```json
{
  "store_id": "store1",
  "delivery_address": "123 Main St, Bangalore",
  "total_amount": 180,
  "notes": "Please call before delivery"
}
```

**Required Fields:**
- `store_id`: Store ID
- `delivery_address`: Delivery address

**Optional Fields:**
- `total_amount`: Order total amount (default: 0)
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
  "body": "{\"id\": \"order-generated-id\", \"customer_id\": \"customer-id\", \"store_id\": \"store1\", \"total_amount\": 180, \"delivery_address\": \"123 Main St, Bangalore\", \"status\": \"pending\", \"notes\": \"Please call before delivery\", \"created_at\": \"2024-01-15T12:00:00Z\", \"updated_at\": \"2024-01-15T12:00:00Z\"}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields
- `401 Unauthorized`: Invalid or missing token

#### PUT /orders/{id}/status
Update order status (Customer only).

**Description:** Updates the status of an order for the authenticated customer.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Path Parameters:**
- `id`: Order ID

**Request Body:**
```json
{
  "status": "cancelled"
}
```

**Required Fields:**
- `status`: New order status (pending, preparing, ready, delivered, cancelled)

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
  "body": "{\"id\": \"order1\", \"customer_id\": \"customer-id\", \"store_id\": \"store1\", \"total_amount\": 180, \"delivery_address\": \"123 Main St, Bangalore\", \"status\": \"cancelled\", \"notes\": \"Please call before delivery\", \"created_at\": \"2024-01-15T10:00:00Z\", \"updated_at\": \"2024-01-15T13:15:00Z\"}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing or invalid status
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Order not found
- `403 Forbidden`: Not authorized to update this order

### 7. Cart Management Endpoints

#### GET /cart
Get customer's shopping cart.

**Description:** Retrieves all items in the customer's shopping cart with totals and store grouping.

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
  "body": "{\"customer_id\": \"mock-customer-id\", \"items\": [{\"customer_id\": \"mock-customer-id\", \"product_id\": \"prod-123\", \"store_id\": \"store-123\", \"quantity\": 2, \"price\": 12.99, \"product_name\": \"Margherita Pizza\", \"product_image\": \"https://example.com/pizza.jpg\", \"unit\": \"piece\", \"expires_at\": 1705312800, \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}], \"total_items\": 1, \"total_quantity\": 2, \"total_amount\": 25.98, \"stores\": [{\"store_id\": \"store-123\", \"items\": [{\"customer_id\": \"mock-customer-id\", \"product_id\": \"prod-123\", \"store_id\": \"store-123\", \"quantity\": 2, \"price\": 12.99, \"product_name\": \"Margherita Pizza\", \"product_image\": \"https://example.com/pizza.jpg\", \"unit\": \"piece\", \"expires_at\": 1705312800, \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}], \"total_amount\": 25.98}]}"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Server error

#### POST /cart/items
Add item to shopping cart.

**Description:** Adds a product to the customer's shopping cart or updates quantity if already exists.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Request Body:**
```json
{
  "product_id": "prod-123",
  "quantity": 2,
  "store_id": "store-123"
}
```

**Required Fields:**
- `product_id`: Product ID to add to cart
- `quantity`: Quantity to add (must be > 0)

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
  "body": "{\"message\": \"Item added to cart successfully\", \"cart\": {\"customer_id\": \"mock-customer-id\", \"items\": [{\"customer_id\": \"mock-customer-id\", \"product_id\": \"prod-123\", \"store_id\": \"store-123\", \"quantity\": 2, \"price\": 12.99, \"product_name\": \"Margherita Pizza\", \"product_image\": \"https://example.com/pizza.jpg\", \"unit\": \"piece\", \"expires_at\": 1705312800, \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}], \"total_items\": 1, \"total_quantity\": 2, \"total_amount\": 25.98, \"stores\": [{\"store_id\": \"store-123\", \"items\": [{\"customer_id\": \"mock-customer-id\", \"product_id\": \"prod-123\", \"store_id\": \"store-123\", \"quantity\": 2, \"price\": 12.99, \"product_name\": \"Margherita Pizza\", \"product_image\": \"https://example.com/pizza.jpg\", \"unit\": \"piece\", \"expires_at\": 1705312800, \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}], \"total_amount\": 25.98}]}}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields, invalid quantity, or insufficient stock
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Product not found
- `500 Internal Server Error`: Server error

#### PUT /cart/items/{product_id}
Update cart item quantity.

**Description:** Updates the quantity of a specific item in the customer's cart.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Path Parameters:**
- `product_id`: Product ID to update

**Request Body:**
```json
{
  "quantity": 3
}
```

**Required Fields:**
- `quantity`: New quantity (0 to remove item, max 50)

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
  "body": "{\"message\": \"Cart item updated successfully\", \"cart\": {\"customer_id\": \"mock-customer-id\", \"items\": [{\"customer_id\": \"mock-customer-id\", \"product_id\": \"prod-123\", \"store_id\": \"store-123\", \"quantity\": 3, \"price\": 12.99, \"product_name\": \"Margherita Pizza\", \"product_image\": \"https://example.com/pizza.jpg\", \"unit\": \"piece\", \"expires_at\": 1705312800, \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}], \"total_items\": 1, \"total_quantity\": 3, \"total_amount\": 38.97, \"stores\": [{\"store_id\": \"store-123\", \"items\": [{\"customer_id\": \"mock-customer-id\", \"product_id\": \"prod-123\", \"store_id\": \"store-123\", \"quantity\": 3, \"price\": 12.99, \"product_name\": \"Margherita Pizza\", \"product_image\": \"https://example.com/pizza.jpg\", \"unit\": \"piece\", \"expires_at\": 1705312800, \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}], \"total_amount\": 38.97}]}}"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid quantity or insufficient stock
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Cart item not found
- `500 Internal Server Error`: Server error

#### DELETE /cart/items/{product_id}
Remove item from cart.

**Description:** Removes a specific item from the customer's shopping cart.

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
  "body": "{\"message\": \"Item removed from cart successfully\", \"cart\": {\"customer_id\": \"mock-customer-id\", \"items\": [], \"total_items\": 0, \"total_quantity\": 0, \"total_amount\": 0, \"stores\": []}}"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Server error

#### DELETE /cart
Clear entire cart.

**Description:** Removes all items from the customer's shopping cart.

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

### 8. Analytics Endpoints (Owner only)

#### GET /analytics/sales/{store_id}
Get sales analytics for a store.

**Description:** Retrieves sales analytics data for a specific store.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Path Parameters:**
- `store_id`: Store ID

**Query Parameters:**
- `period` (optional): Analytics period - 'day', 'week', 'month', 'year' (default: 'month')

**Example Request:**
```
GET /analytics/sales/store1?period=month
```

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
  "body": "{\"analytics\": {\"period\": \"month\", \"total_orders\": 45, \"total_revenue\": 2250.50, \"average_order_value\": 50.01, \"status_breakdown\": {\"pending\": 5, \"preparing\": 10, \"ready\": 15, \"delivered\": 15}, \"date_range\": {\"start\": \"2024-01-01T00:00:00Z\", \"end\": \"2024-01-31T23:59:59Z\"}}}"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Not authorized to view analytics for this store

#### GET /analytics/products/{store_id}
Get product analytics for a store.

**Description:** Retrieves product analytics data for a specific store.

**Headers:** `Authorization: Bearer <firebase-jwt-token>`

**Path Parameters:**
- `store_id`: Store ID

**Query Parameters:**
- `period` (optional): Analytics period - 'day', 'week', 'month', 'year' (default: 'month')

**Example Request:**
```
GET /analytics/products/store1?period=month
```

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
  "body": "{\"analytics\": {\"total_products\": 25, \"products_in_stock\": 20, \"products_out_of_stock\": 5, \"price_analysis\": {\"average_price\": 45.50, \"min_price\": 10.00, \"max_price\": 150.00}}}"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Not authorized to view analytics for this store

## Error Codes

The API uses standardized error codes:

- `VALIDATION_ERROR`: Input validation failed
- `UNAUTHORIZED`: Authentication required or failed
- `FORBIDDEN`: Access denied
- `NOT_FOUND`: Resource not found
- `CONFLICT`: Resource already exists
- `UNPROCESSABLE_ENTITY`: Request cannot be processed
- `INTERNAL_ERROR`: Server error

## Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no content returned
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `422 Unprocessable Entity`: Request cannot be processed
- `500 Internal Server Error`: Server error

## CORS Headers

All endpoints include CORS headers:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type,Authorization
Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS
```

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## Pagination

Most list endpoints support pagination with the following parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (varies by endpoint)

Pagination response includes:
```json
{
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 45,
    "items_per_page": 10
  }
}
```

## Authentication Flow

1. User registers with the system
2. User receives user ID
3. User calls `/auth/register` with user ID to create profile (phone number validation included)
4. User can login using either:
   - User ID: `/auth/login` with `user_id`
   - Phone Number: `/auth/login` with `phone`
   - Enhanced: `/auth/login` with both `user_id` and `phone`
5. Include JWT token in Authorization header for protected endpoints
6. Optional: Use `/auth/user/phone?phone=<number>` to validate phone number existence

## Data Models Summary

### User
- `id`: User ID
- `email`: Email address
- `name`: Full name
- `user_type`: "customer" or "owner"
- `phone`: Phone number (optional)
- `address`: Delivery address (optional)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Store
- `id`: Unique store ID
- `owner_id`: User ID of owner
- `name`: Store name
- `address`: Store address
- `phone`: Store phone (optional)
- `is_open`: Open status
- `rating`: Store rating
- `delivery_time`: Estimated delivery time
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Product
- `id`: Unique product ID
- `store_id`: Associated store ID
- `category_id`: Category ID (optional)
- `name`: Product name
- `description`: Product description (optional)
- `price`: Product price
- `unit`: Unit of measurement
- `stock`: Available stock
- `image_url`: Product image URL (optional)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Order
- `id`: Unique order ID
- `customer_id`: User ID of customer
- `store_id`: Associated store ID
- `total_amount`: Order total
- `delivery_address`: Delivery address
- `status`: Order status (pending, preparing, ready, delivered, cancelled)
- `notes`: Order notes (optional)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Cart Item
- `customer_id`: User ID of customer
- `product_id`: Product ID
- `store_id`: Associated store ID
- `quantity`: Item quantity
- `price`: Product price at time of adding to cart
- `product_name`: Product name
- `product_image`: Product image URL
- `unit`: Product unit (piece, kg, etc.)
- `expires_at`: Cart item expiration timestamp
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Category
- `id`: Unique category ID
- `name`: Category name
- `created_at`: Creation timestamp 