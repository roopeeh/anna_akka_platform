# Phone Number OTP Verification Documentation

This document describes the phone number OTP (One-Time Password) verification system implemented with AWS Cognito for mobile app authentication in the Anna Akka Platform.

## Overview

The OTP verification system allows users to:
1. Request an OTP to be sent to their registered phone number
2. Verify the OTP to complete login
3. Access the application without password-based authentication

This is designed specifically for mobile app authentication where users can login with just their phone number and OTP.

## Architecture

### Components

1. **AWS Cognito User Pool**: Manages user authentication and SMS delivery
2. **Lambda Functions**: Handle OTP requests and verification
3. **DynamoDB**: Stores user information and validates phone numbers
4. **API Gateway**: Routes OTP-related requests

### Flow

1. User requests OTP via `/auth/otp/send`
2. System validates phone number exists in DynamoDB
3. Cognito creates/gets user and sends SMS with OTP
4. User verifies OTP via `/auth/otp/verify`
5. System confirms OTP and returns user data for login

## API Endpoints

### 1. Send OTP

**Endpoint:** `POST /auth/otp/send`

**Description:** Sends an OTP to the user's registered phone number for login authentication.

**Request Body:**
```json
{
  "phone": "+91 98765 43210"
}
```

**Required Fields:**
- `phone`: User's phone number (supports various formats)

**Phone Number Formats Supported:**
- `+91 98765 43210` (with spaces)
- `+919876543210` (without spaces)
- `91 98765 43210` (without + prefix)
- `919876543210` (minimal format)

**Validation Process:**
1. Phone number format validation
2. Normalization to consistent format
3. Check if user exists in DynamoDB
4. Create or get Cognito user
5. Send OTP via Cognito SMS

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
  "body": "{\"message\": \"OTP sent successfully\", \"phone\": \"+919876543210\", \"user_status\": \"CONFIRMED\"}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing phone or invalid format
- `404 Not Found`: User not found with provided phone number
- `500 Internal Server Error`: Failed to send OTP

### 2. Verify OTP

**Endpoint:** `POST /auth/otp/verify`

**Description:** Verifies the OTP and completes the login process.

**Request Body:**
```json
{
  "phone": "+91 98765 43210",
  "otp": "123456"
}
```

**Required Fields:**
- `phone`: User's phone number
- `otp`: One-time password received via SMS

**Validation Process:**
1. Phone number format validation
2. Check if user exists in DynamoDB
3. Verify OTP with Cognito
4. Return user data for successful login

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
  "body": "{\"message\": \"Login successful\", \"phone\": \"+919876543210\", \"user\": {\"id\": \"firebase-auth-uid-123\", \"name\": \"John Doe\", \"email\": \"user@example.com\", \"phone\": \"+919876543210\", \"roles\": [\"customer\"], \"created_at\": \"2024-01-15T10:30:00Z\", \"updated_at\": \"2024-01-15T10:30:00Z\"}, \"auth_type\": \"otp\"}"
}
```

**Error Responses:**
- `400 Bad Request`: Missing fields or invalid format
- `400 Bad Request`: Invalid OTP
- `400 Bad Request`: Expired OTP
- `404 Not Found`: User not found with provided phone number
- `500 Internal Server Error`: Failed to verify OTP

## Integration with Existing System

### User Registration Flow

1. **Existing Flow:**
   - User registers with Firebase UID
   - Phone number stored in DynamoDB
   - User can login with Firebase UID or phone number

2. **New OTP Flow:**
   - User requests OTP for login
   - System validates phone exists in DynamoDB
   - Cognito creates/gets user and sends SMS with OTP
   - User verifies OTP and gets logged in
   - No password required for mobile app authentication

### Database Integration

The OTP system integrates with the existing DynamoDB structure:

- **Users Table**: Validates phone number existence
- **Phone Index**: Fast phone number lookups
- **User Data**: Returns complete user information after successful login

## Security Features

### OTP Security
- **Expiration**: OTPs expire after a configurable time (default: 10 minutes)
- **Rate Limiting**: Cognito provides built-in rate limiting
- **One-time Use**: Each OTP can only be used once
- **Secure Delivery**: SMS delivered via AWS SNS

### Authentication Security
- **Phone Verification**: Only verified phone numbers can receive OTP
- **User Validation**: Users must exist in DynamoDB before OTP can be sent
- **No Password Storage**: No passwords are stored or managed by the application
- **Temporary Passwords**: Cognito uses temporary passwords internally (not visible to users)

## Error Handling

### Common Error Scenarios

1. **Invalid Phone Number**
   ```json
   {
     "error": {
       "code": "VALIDATION_ERROR",
       "message": "Invalid phone number format"
     }
   }
   ```

2. **User Not Found**
   ```json
   {
     "error": {
       "code": "NOT_FOUND",
       "message": "No user found with this phone number. Please register first."
     }
   }
   ```

3. **Invalid OTP**
   ```json
   {
     "error": {
       "code": "VALIDATION_ERROR",
       "message": "Invalid OTP"
     }
   }
   ```

4. **Expired OTP**
   ```json
   {
     "error": {
       "code": "VALIDATION_ERROR",
       "message": "OTP has expired"
     }
   }
   ```

## Usage Examples

### Complete OTP Login Flow

1. **Request OTP:**
   ```bash
   curl -X POST https://api.example.com/auth/otp/send \
     -H "Content-Type: application/json" \
     -d '{"phone": "+91 98765 43210"}'
   ```

2. **Receive SMS with OTP** (e.g., "Your verification code is: 123456")

3. **Verify OTP and Login:**
   ```bash
   curl -X POST https://api.example.com/auth/otp/verify \
     -H "Content-Type: application/json" \
     -d '{
       "phone": "+91 98765 43210",
       "otp": "123456"
     }'
   ```

4. **Use returned user data for app authentication**

### Mobile App Integration

```javascript
// Example mobile app flow
async function loginWithOTP(phoneNumber) {
  // Step 1: Request OTP
  const sendOTPResponse = await fetch('/auth/otp/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone: phoneNumber })
  });
  
  if (sendOTPResponse.ok) {
    // Step 2: Show OTP input screen
    const otp = await getUserInputOTP();
    
    // Step 3: Verify OTP
    const verifyResponse = await fetch('/auth/otp/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        phone: phoneNumber, 
        otp: otp 
      })
    });
    
    if (verifyResponse.ok) {
      const userData = await verifyResponse.json();
      // Store user data and proceed with app
      storeUserData(userData.user);
      navigateToMainApp();
    }
  }
}
```

## Configuration

### Environment Variables

The OTP system uses the following environment variables:

```bash
# Cognito Configuration
COGNITO_USER_POOL_ID=us-east-1_xxxxxxxxx
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx

# SMS Configuration
SMS_REGION=us-east-1
SMS_EXTERNAL_ID=anna-akka-platform-sms-config
```

### AWS Services Required

1. **Cognito User Pool**: User authentication and SMS delivery
2. **SNS**: SMS service for OTP delivery
3. **IAM**: Permissions for Lambda to access Cognito
4. **DynamoDB**: User data storage and validation

## Testing

### Test Scenarios

1. **Valid OTP Flow**
   - Request OTP with valid phone number
   - Verify OTP with correct code
   - Complete login successfully

2. **Invalid Phone Number**
   - Request OTP with invalid format
   - Request OTP with non-existent number

3. **Invalid OTP**
   - Verify with wrong OTP
   - Verify with expired OTP

4. **User Not Registered**
   - Try to request OTP for unregistered phone number

### Test Commands

```bash
# Test OTP send
curl -X POST https://api.example.com/auth/otp/send \
  -H "Content-Type: application/json" \
  -d '{"phone": "+91 98765 43210"}'

# Test OTP verify
curl -X POST https://api.example.com/auth/otp/verify \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+91 98765 43210",
    "otp": "123456"
  }'
```

## Monitoring and Logging

### CloudWatch Logs

The OTP system logs all operations to CloudWatch:

- **OTP Send Attempts**: Phone number, success/failure, user status
- **OTP Verification**: Phone number, OTP validity, success/failure
- **User Creation**: Cognito user creation events
- **Error Details**: Full error messages for debugging

### Metrics to Monitor

1. **OTP Send Success Rate**
2. **OTP Verification Success Rate**
3. **SMS Delivery Success Rate**
4. **User Creation Rate**
5. **Error Rates by Type**

## Troubleshooting

### Common Issues

1. **SMS Not Delivered**
   - Check Cognito SMS configuration
   - Verify phone number format
   - Check AWS SNS limits

2. **OTP Verification Fails**
   - Verify OTP hasn't expired
   - Check OTP format (6 digits)
   - Ensure user exists in DynamoDB

3. **User Not Found**
   - Verify user is registered in DynamoDB
   - Check phone number format and normalization
   - Ensure user has valid phone number

### Debug Steps

1. **Check CloudWatch Logs** for detailed error messages
2. **Verify Cognito User Pool** configuration
3. **Test SMS delivery** with AWS SNS console
4. **Validate DynamoDB** user records
5. **Check IAM permissions** for Lambda functions

## Future Enhancements

### Planned Features

1. **Email OTP**: Support for email-based OTP delivery
2. **Voice OTP**: Phone call-based OTP delivery
3. **Multi-factor Authentication**: Combine SMS and email OTP
4. **Rate Limiting**: Custom rate limiting per phone number
5. **Analytics Dashboard**: OTP usage and success metrics
6. **Session Management**: Track user sessions after OTP login

### Security Improvements

1. **OTP Complexity**: Increase OTP length or add alphanumeric
2. **Device Fingerprinting**: Track device for suspicious activity
3. **Geolocation**: Block OTP requests from unusual locations
4. **Time-based Restrictions**: Limit OTP requests during certain hours
5. **Biometric Integration**: Combine OTP with fingerprint/face recognition 