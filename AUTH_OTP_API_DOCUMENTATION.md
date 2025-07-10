# Auth & OTP Auth API Documentation

## Base URL
```
https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev
```

## Authentication Flow

### Passwordless OTP Authentication
The system uses passwordless authentication with OTP (One-Time Password) sent via SMS.

**Flow:**
1. Send OTP → Verify OTP → Register/Login
2. No passwords required
3. OTP expires in 5 minutes

---

## OTP Auth Endpoints

### 1. Send OTP

**Endpoint:** `POST /auth/otp/send`

**Description:** Send OTP to phone number for authentication

**Request:**
```json
{
  "phone": "+919502528182"
}
```

**cURL:**
```bash
curl -X POST "https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev/auth/otp/send" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919502528182"
  }'
```

**JavaScript/Fetch:**
```javascript
const response = await fetch('https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev/auth/otp/send', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    phone: '+919502528182'
  })
});

const data = await response.json();
```

**Success Response (200):**
```json
{
  "message": "OTP sent successfully",
  "phone": "+919502528182",
  "is_new_user": false
}
```

**Error Response (400):**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Phone number is required"
  }
}
```

**Error Response (500):**
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Failed to send OTP"
  }
}
```

---

### 2. Verify OTP

**Endpoint:** `POST /auth/otp/verify`

**Description:** Verify OTP and authenticate user

**Request:**
```json
{
  "phone": "+919502528182",
  "otp": "123456"
}
```

**cURL:**
```bash
curl -X POST "https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev/auth/otp/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919502528182",
    "otp": "123456"
  }'
```

**JavaScript/Fetch:**
```javascript
const response = await fetch('https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev/auth/otp/verify', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    phone: '+919502528182',
    otp: '123456'
  })
});

const data = await response.json();
```

**Success Response - New User (200):**
```json
{
  "message": "OTP verified successfully. Please proceed with registration.",
  "phone": "+919502528182",
  "is_new_user": true,
  "auth_type": "passwordless"
}
```

**Success Response - Existing User (200):**
```json
{  
  "message": "Login successful",
  "phone": "+919502528182",
  "user": {
    "id": "h4xwmmtFxwfFqWP84vQFYEY6SuF3",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+919502528182",
    "roles": ["customer"],
    "created_at": "2025-07-07T10:25:10.779069",
    "updated_at": "2025-07-07T10:25:10.779069"
  },
  "is_new_user": false,
  "auth_type": "passwordless"
}
```

**Error Response - Invalid OTP (400):**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid or expired OTP"
  }
}
```

**Error Response - Expired OTP (400):**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "OTP has expired"
  }
}
```

---

## Auth Endpoints

### 1. Register User

**Endpoint:** `POST /auth/register`

**Description:** Register new user after OTP verification

**Request:**
```json
{
  "phone": "+919502528182",
  "name": "John Doe",
  "email": "john@example.com",
  "roles": ["customer"]
}
```

**cURL:**
```bash
curl -X POST "https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919502528182",
    "name": "John Doe",
    "email": "john@example.com",
    "roles": ["customer"]
  }'
```

**JavaScript/Fetch:**
```javascript
const response = await fetch('https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    phone: '+919502528182',
    name: 'John Doe',
    email: 'john@example.com',
    roles: ['customer']
  })
});

const data = await response.json();
```

**Success Response (201):**
```json
{
  "user": {
    "id": "h4xwmmtFxwfFqWP84vQFYEY6SuF3",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+919502528182",
    "roles": ["customer"],
    "created_at": "2025-07-07T10:25:10.779069",
    "updated_at": "2025-07-07T10:25:10.779069"
  }
}
```

**Error Response - Phone Already Exists (409):**
```json
{
  "error": {
    "code": "CONFLICT",
    "message": "Phone number already exists"
  }
}
```

**Error Response - Email Already Exists (409):**
```json
{
  "error": {
    "code": "CONFLICT",
    "message": "Email already exists"
  }
}
```

---

### 2. Login (Check User)

**Endpoint:** `POST /auth/login`

**Description:** Check if user exists for login

**Request:**
```json
{
  "phone": "+919502528182"
}
```

**cURL:**
```bash
curl -X POST "https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919502528182"
  }'
```

**JavaScript/Fetch:**
```javascript
const response = await fetch('https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    phone: '+919502528182'
  })
});

const data = await response.json();
```

**Success Response (200):**
```json
{
  "message": "User found. Please proceed with OTP verification via /auth/otp/verify endpoint.",
  "user": {
    "id": "h4xwmmtFxwfFqWP84vQFYEY6SuF3",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+919502528182",
    "roles": ["customer"],
    "created_at": "2025-07-07T10:25:10.779069",
    "updated_at": "2025-07-07T10:25:10.779069"
  }
}
```

**Error Response - User Not Found (401):**
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "User not found with phone number: +919502528182. Please register first."
  }
}
```

---

### 3. Get User by Phone

**Endpoint:** `GET /auth/user/phone`

**Description:** Get user details by phone number

**Request:**
```
GET /auth/user/phone?phone=%2B919502528182
```

**cURL:**
```bash
curl -X GET "https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev/auth/user/phone?phone=%2B919502528182" \
  -H "Content-Type: application/json"
```

**JavaScript/Fetch:**
```javascript
const phone = encodeURIComponent('+919502528182');
const response = await fetch(`https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev/auth/user/phone?phone=${phone}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
});

const data = await response.json();
```

**Success Response (200):**
```json
{
  "user": {
    "id": "h4xwmmtFxwfFqWP84vQFYEY6SuF3",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+919502528182",
    "roles": ["customer"],
    "created_at": "2025-07-07T10:25:10.779069",
    "updated_at": "2025-07-07T10:25:10.779069"
  }
}
```

**Error Response - User Not Found (404):**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "User not found with phone number: +919502528182"
  }
}
```

---

## Complete Authentication Flow Examples

### New User Registration Flow

```javascript
// Step 1: Send OTP
const sendOtpResponse = await fetch('/auth/otp/send', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ phone: '+919502528182' })
});

// Step 2: User enters OTP (from SMS)
const otp = '123456'; // User input

// Step 3: Verify OTP
const verifyOtpResponse = await fetch('/auth/otp/verify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ phone: '+919502528182', otp })
});

const verifyData = await verifyOtpResponse.json();

if (verifyData.is_new_user) {
  // Step 4: Register new user
  const registerResponse = await fetch('/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      phone: '+919502528182',
      name: 'John Doe',
      email: 'john@example.com',
      roles: ['customer']
    })
  });
}
```

### Existing User Login Flow

```javascript
// Step 1: Send OTP
const sendOtpResponse = await fetch('/auth/otp/send', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ phone: '+919502528182' })
});

// Step 2: User enters OTP (from SMS)
const otp = '123456'; // User input

// Step 3: Verify OTP
const verifyOtpResponse = await fetch('/auth/otp/verify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ phone: '+919502528182', otp })
});

const verifyData = await verifyOtpResponse.json();

if (!verifyData.is_new_user) {
  // User is logged in, verifyData.user contains user information
  console.log('User logged in:', verifyData.user);
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Invalid input data |
| `UNAUTHORIZED` | User not found or authentication failed |
| `NOT_FOUND` | Resource not found |
| `CONFLICT` | Resource already exists |
| `INTERNAL_ERROR` | Server error |

---

## Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `201` | Created |
| `400` | Bad Request |
| `401` | Unauthorized |
| `404` | Not Found |
| `409` | Conflict |
| `500` | Internal Server Error |

---

## Notes

1. **Phone Number Format**: Always use international format with `+` prefix
2. **OTP Expiration**: OTP expires in 5 minutes
3. **Passwordless**: No passwords required, only OTP authentication
4. **User Roles**: Valid roles are `["customer"]`, `["vendor"]`, `["admin"]`
5. **Email**: Optional field for registration
6. **SMS Delivery**: Uses AWS SNS for SMS delivery

---

## Frontend Integration Tips

1. **Store User Data**: After successful login, store user data in localStorage/sessionStorage
2. **Handle OTP Input**: Implement 6-digit OTP input with proper validation
3. **Loading States**: Show loading states during API calls
4. **Error Handling**: Display user-friendly error messages
5. **Phone Validation**: Validate phone number format before sending OTP
6. **Session Management**: Implement proper session management after login 