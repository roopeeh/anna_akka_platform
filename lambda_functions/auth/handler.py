import json
import os
import boto3
from datetime import datetime
import uuid
import logging
import re
import sys
sys.path.append('..')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table(os.environ['USERS_TABLE']) # type: ignore

# Get constants from environment variables
ERROR_CODES = {
    'VALIDATION_ERROR': os.environ.get('ERROR_CODES_VALIDATION_ERROR', 'VALIDATION_ERROR'),
    'UNAUTHORIZED': os.environ.get('ERROR_CODES_UNAUTHORIZED', 'UNAUTHORIZED'),
    'FORBIDDEN': os.environ.get('ERROR_CODES_FORBIDDEN', 'FORBIDDEN'),
    'NOT_FOUND': os.environ.get('ERROR_CODES_NOT_FOUND', 'NOT_FOUND'),
    'CONFLICT': os.environ.get('ERROR_CODES_CONFLICT', 'CONFLICT'),
    'UNPROCESSABLE_ENTITY': os.environ.get('ERROR_CODES_UNPROCESSABLE_ENTITY', 'UNPROCESSABLE_ENTITY'),
    'INTERNAL_ERROR': os.environ.get('ERROR_CODES_INTERNAL_ERROR', 'INTERNAL_ERROR')
}

STATUS_CODES = {
    'OK': int(os.environ.get('STATUS_CODES_OK', '200')),
    'CREATED': int(os.environ.get('STATUS_CODES_CREATED', '201')),
    'NO_CONTENT': int(os.environ.get('STATUS_CODES_NO_CONTENT', '204')),
    'BAD_REQUEST': int(os.environ.get('STATUS_CODES_BAD_REQUEST', '400')),
    'UNAUTHORIZED': int(os.environ.get('STATUS_CODES_UNAUTHORIZED', '401')),
    'FORBIDDEN': int(os.environ.get('STATUS_CODES_FORBIDDEN', '403')),
    'NOT_FOUND': int(os.environ.get('STATUS_CODES_NOT_FOUND', '404')),
    'METHOD_NOT_ALLOWED': int(os.environ.get('STATUS_CODES_METHOD_NOT_ALLOWED', '405')),
    'CONFLICT': int(os.environ.get('STATUS_CODES_CONFLICT', '409')),
    'UNPROCESSABLE_ENTITY': int(os.environ.get('STATUS_CODES_UNPROCESSABLE_ENTITY', '422')),
    'INTERNAL_ERROR': int(os.environ.get('STATUS_CODES_INTERNAL_ERROR', '500'))
}

CORS_HEADERS = {
    'Content-Type': os.environ.get('CORS_HEADERS_CONTENT_TYPE', 'application/json'),
    'Access-Control-Allow-Origin': os.environ.get('CORS_HEADERS_ACCESS_CONTROL_ORIGIN', '*'),
    'Access-Control-Allow-Headers': os.environ.get('CORS_HEADERS_ACCESS_CONTROL_HEADERS', 'Content-Type,Authorization'),
    'Access-Control-Allow-Methods': os.environ.get('CORS_HEADERS_ACCESS_CONTROL_METHODS', 'GET,POST,PUT,DELETE,OPTIONS')
}

USER_TYPES = {
    'CUSTOMER': os.environ.get('USER_TYPES_CUSTOMER', 'customer'),
    'VENDOR': os.environ.get('USER_TYPES_VENDOR', 'vendor'),
    'ADMIN': os.environ.get('USER_TYPES_ADMIN', 'admin')
}

# Valid roles that can be assigned to users
VALID_ROLES = ['customer', 'vendor', 'admin']

MOCK_VALUES = {
    'USER_ID': os.environ.get('MOCK_VALUES_USER_ID', 'mock-user-id'),
    'OWNER_ID': os.environ.get('MOCK_VALUES_OWNER_ID', 'mock-owner-id'),
    'STORE_ID': os.environ.get('MOCK_VALUES_STORE_ID', 'mock-store-id'),
    'CUSTOMER_ID': os.environ.get('MOCK_VALUES_CUSTOMER_ID', 'mock-customer-id')
}

def normalize_phone(phone):
    """Normalize phone number: strip whitespace, ensure leading +, and collapse spaces."""
    if not phone:
        return phone
    phone = phone.strip().replace(' ', '')
    if not phone.startswith('+') and phone.startswith('91'):
        phone = '+' + phone
    if not phone.startswith('+'):
        phone = '+' + phone
    return phone

def create_user(user_data):
    """Create a new user in DynamoDB"""
    logger.info(f"Creating user with email: {user_data.get('email')}")
    
    # Generate a new UUID for the user ID
    user_id = str(uuid.uuid4())
    
    timestamp = datetime.utcnow().isoformat()
    
    # Build user item with proper handling of optional fields
    user_item = {
        'id': user_id,  # Use generated UUID as the user ID
        'created_at': timestamp,
        'updated_at': timestamp
    }
    
    # Only add email if it's provided and not empty
    if user_data.get('email'):
        user_item['email'] = user_data['email']
    
    # Only add name if it's provided and not empty
    if user_data.get('name'):
        user_item['name'] = user_data['name']
    
    # Only add phone if it's provided and not empty
    if user_data.get('phone'):
        user_item['phone'] = user_data['phone']
    
    # Only add address if it's provided and not empty
    if user_data.get('address'):
        user_item['address'] = user_data['address']
    
    # Add roles (default to customer if not provided)
    user_item['roles'] = user_data.get('roles', [USER_TYPES['CUSTOMER']])
    
    logger.info(f"User item to be created: {json.dumps(user_item, default=str)}")
    users_table.put_item(Item=user_item)
    logger.info(f"User created successfully with ID: {user_id}")
    return user_item

def get_user_by_email(email):
    """Get user by email from DynamoDB using GSI"""
    if not email:
        logger.info("No email provided for lookup")
        return None
    
    logger.info(f"Looking up user by email: {email}")
    try:
        response = users_table.query(
            IndexName='email_index',
            KeyConditionExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        
        items = response.get('Items', [])
        user = items[0] if items else None
        logger.info(f"User lookup result: {'Found' if user else 'Not found'}")
        return user
    except Exception as e:
        logger.error(f"Error looking up user by email: {str(e)}")
        return None

def get_user_by_phone(phone):
    """Get user by phone number from DynamoDB using GSI"""
    if not phone:
        logger.info("No phone provided for lookup")
        return None
    
    logger.info(f"Looking up user by phone: {phone}")
    try:
        response = users_table.query(
            IndexName='phone_index',
            KeyConditionExpression='phone = :phone',
            ExpressionAttributeValues={':phone': phone}
        )
        
        items = response.get('Items', [])
        user = items[0] if items else None
        logger.info(f"User lookup result: {'Found' if user else 'Not found'}")
        return user
    except Exception as e:
        logger.error(f"Error looking up user by phone: {str(e)}")
        return None

def get_user_by_firebase_uid(firebase_uid):
    """Get user by Firebase UID from DynamoDB"""
    logger.info(f"Looking up user by Firebase UID: {firebase_uid}")
    response = users_table.get_item(Key={'id': firebase_uid})
    user = response.get('Item')
    logger.info(f"User lookup result: {'Found' if user else 'Not found'}")
    return user

def handler(event, context):
    """Main Lambda handler for authentication"""
    logger.info("=== AUTH HANDLER START ===")
    logger.info(f"Event: {json.dumps(event, default=str)}")
    logger.info(f"Context: {json.dumps({'function_name': context.function_name, 'function_version': context.function_version, 'invoked_function_arn': context.invoked_function_arn, 'memory_limit_in_mb': context.memory_limit_in_mb, 'remaining_time_in_millis': context.get_remaining_time_in_millis()}, default=str)}")
    
    try:
        # Parse the request
        path = event.get('requestContext', {}).get('http', {}).get('path', '')
        method = event.get('requestContext', {}).get('http', {}).get('method', '')
        
        logger.info(f"Request path: {path}")
        logger.info(f"Request method: {method}")
        
        # Check payload size for POST requests
        if method == 'POST':
            body_str = event.get('body', '')
            if len(body_str) > 1024 * 1024:  # 1MB limit
                logger.warning("Payload too large")
                return {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'], 'message': 'Payload too large'}})
                }
        
        # Parse body with proper error handling
        body = {}
        if method in ['POST', 'PUT']:
            try:
                body_str = event.get('body', '{}')
                if body_str:
                    body = json.loads(body_str)
                logger.info(f"Request body: {json.dumps(body, default=str)}")
            except json.JSONDecodeError as e:
                logger.warning(f"Malformed JSON: {str(e)}")
                return {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'], 'message': 'Malformed JSON'}})
                }
        
        # Route based on path and method
        # Handle both with and without stage prefix (/dev/auth/register or /auth/register)
        if (path.startswith('/auth/register') or path.endswith('/auth/register')):
            if method == 'POST':
                logger.info("Routing to register handler")
                response = handle_register(body)
                logger.info(f"Register response: {json.dumps(response, default=str)}")
                return response
            else:
                logger.warning(f"Method not allowed: {method} for /auth/register")
                return {
                    'statusCode': STATUS_CODES['METHOD_NOT_ALLOWED'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'], 'message': f'Method {method} not allowed for this endpoint'}})
                }
        elif (path.startswith('/auth/login') or path.endswith('/auth/login')):
            if method == 'POST':
                logger.info("Routing to login handler")
                response = handle_login(body)
                logger.info(f"Login response: {json.dumps(response, default=str)}")
                return response
            else:
                logger.warning(f"Method not allowed: {method} for /auth/login")
                return {
                    'statusCode': STATUS_CODES['METHOD_NOT_ALLOWED'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'], 'message': f'Method {method} not allowed for this endpoint'}})
                }
        elif (path.startswith('/auth/user/phone') or path.endswith('/auth/user/phone')):
            if method == 'GET':
                logger.info("Routing to get user by phone handler")
                response = handle_get_user_by_phone(event)
                logger.info(f"Get user by phone response: {json.dumps(response, default=str)}")
                return response
            else:
                logger.warning(f"Method not allowed: {method} for /auth/user/phone")
                return {
                    'statusCode': STATUS_CODES['METHOD_NOT_ALLOWED'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'], 'message': f'Method {method} not allowed for this endpoint'}})
                }
        else:
            logger.warning(f"Endpoint not found: {method} {path}")
            return {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': {'code': ERROR_CODES['NOT_FOUND'],'message': 'Endpoint not found'}})
            }
            
    except Exception as e:
        logger.error(f"Handler error: {str(e)}", exc_info=True)
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': {'code': ERROR_CODES['INTERNAL_ERROR'],'message': str(e)}})
        }
    finally:
        logger.info("=== AUTH HANDLER END ===")

def handle_register(body):
    """Handle user registration"""
    logger.info("=== REGISTER HANDLER START ===")
    try:
        logger.info(f"Registration request body: {json.dumps(body, default=str)}")
        
        # Validate required fields - phone number is required for registration
        # OTP validation is handled by the OTP auth Lambda, so we don't need it here
        if not body.get('phone'):
            logger.warning("Missing required field: phone is required")
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'],'message': 'Phone number is required'}})
            }
        
        # Validate email format if provided
        if body.get('email'):
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, body['email']):
                logger.warning(f"Invalid email format: {body['email']}")
                return {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'],'message': 'Invalid email format'}})
                }
        
        # Validate phone number format if provided
        if body.get('phone'):
            phone_pattern = r'^\+?[1-9]\d{1,14}$'
            normalized_phone = normalize_phone(body['phone'])
            if not re.match(phone_pattern, normalized_phone):
                logger.warning(f"Invalid phone format: {body['phone']}")
                return {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'],'message': 'Invalid phone number format'}})
                }
            body['phone'] = normalized_phone
        
        logger.info("All required fields present")
        
        # Check if email is already used by another user (only if email is provided)
        if body.get('email'):
            existing_user_by_email = get_user_by_email(body['email'])
            if existing_user_by_email:
                logger.warning(f"Email already exists: {body['email']}")
                return {
                    'statusCode': STATUS_CODES['CONFLICT'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': {'code': ERROR_CODES['CONFLICT'],'message': 'Email already exists'}})
                }
        
        # Check if phone number is already used by another user (only if phone is provided)
        if body.get('phone'):
            existing_user_by_phone = get_user_by_phone(body['phone'])
            if existing_user_by_phone:
                logger.warning(f"Phone number already exists: {body['phone']}")
                return {
                    'statusCode': STATUS_CODES['CONFLICT'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': {'code': ERROR_CODES['CONFLICT'],'message': 'Phone number already exists'}})
                }
        
        # Validate roles if provided
        roles = body.get('roles', [USER_TYPES['CUSTOMER']])
        
        # Ensure roles is a list
        if not isinstance(roles, list):
            roles = [roles] if roles else [USER_TYPES['CUSTOMER']]
        
        # Validate each role
        for role in roles:
            if role not in VALID_ROLES:
                logger.warning(f"Invalid role: {role}. Valid roles: {VALID_ROLES}")
                return {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'],'message': f'Invalid role: {role}. Valid roles: {", ".join(VALID_ROLES)}'}})
                }
        
        # Remove duplicates while preserving order
        roles = list(dict.fromkeys(roles))
        
        # Create user
        user_data = {
            'email': body.get('email'),  # Email is optional
            'name': body.get('name'),  # Name is optional
            'roles': roles,
            'phone': body.get('phone'),
            'address': body.get('address')
        }
        
        logger.info(f"Creating user with data: {json.dumps(user_data, default=str)}")
        user = create_user(user_data)
        
        # Return the user data (no token needed)
        response = {
            'statusCode': STATUS_CODES['CREATED'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'user': user
            })
        }
        
        logger.info("=== REGISTER HANDLER END ===")
        return response
        
    except Exception as e:
        logger.error(f"Register error: {str(e)}", exc_info=True)
        logger.info("=== REGISTER HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': {'code': ERROR_CODES['INTERNAL_ERROR'],'message': str(e)}})
        }

def handle_login(body):
    """Handle user login - OTP verification is handled by OTP auth Lambda"""
    logger.info("=== LOGIN HANDLER START ===")
    try:
        logger.info(f"Login request body: {json.dumps(body, default=str)}")
        
        # Validate required fields - only phone number is required for login
        # OTP verification is handled by the OTP auth Lambda
        phone = body.get('phone')
        
        if not phone:
            logger.warning("Missing required field: phone is required")
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'],'message': 'Phone number is required for login'}})
            }
        
        # Find user by phone number
        logger.info(f"Attempting login for phone number: {phone}")
        phone = normalize_phone(phone)
        user = get_user_by_phone(phone)
        
        if not user:
            logger.warning(f"Login failed - user not found for phone number: {phone}")
            return {
                'statusCode': STATUS_CODES['UNAUTHORIZED'],
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': {'code': ERROR_CODES['UNAUTHORIZED'],'message': f'User not found with phone number: {phone}. Please register first.'}})
            }
        
        # User found - return user data for login
        # OTP verification should be done via the OTP auth Lambda first
        logger.info(f"User found for login: {user['id']}")
        
        # Return the user data
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'message': 'User found. Please proceed with OTP verification via /auth/otp/verify endpoint.',
                'user': user
            })
        }
        
        logger.info("=== LOGIN HANDLER END ===")
        return response
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        logger.info("=== LOGIN HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': {'code': ERROR_CODES['INTERNAL_ERROR'],'message': str(e)}})
        }

def handle_get_user_by_phone(event):
    """Handle getting user by phone number"""
    logger.info("=== GET USER BY PHONE HANDLER START ===")
    try:
        # Get phone number from query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        phone = query_params.get('phone')
        
        # Handle URL encoding - replace spaces with + for phone numbers
        if phone and phone.startswith('91 '):
            phone = '+' + phone
        
        logger.info(f"Looking up user by phone number: {phone}")
        
        if not phone:
            logger.warning("Missing phone parameter in request")
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'],'message': 'Phone parameter is required'}})
            }
        
        # Validate phone number format
        phone_pattern = r'^\+?[1-9]\d{1,14}$'
        normalized_phone = normalize_phone(phone)
        if not re.match(phone_pattern, normalized_phone):
            logger.warning(f"Invalid phone format: {phone}")
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'],'message': 'Invalid phone number format'}})
            }
        
        # Find user by phone number
        user = get_user_by_phone(normalized_phone)
        if not user:
            logger.warning(f"User not found for phone number: {normalized_phone}")
            return {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': {'code': ERROR_CODES['NOT_FOUND'],'message': f'User not found with phone number: {normalized_phone}'}})
            }
        
        logger.info(f"User found for phone number: {normalized_phone}")
        
        # Return the user data (excluding sensitive information)
        safe_user_data = {
            'id': user.get('id'),
            'name': user.get('name'),
            'email': user.get('email'),
            'phone': user.get('phone'),
            'roles': user.get('roles'),
            'created_at': user.get('created_at'),
            'updated_at': user.get('updated_at')
        }
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'user': safe_user_data})
        }
        
        logger.info("=== GET USER BY PHONE HANDLER END ===")
        return response
        
    except Exception as e:
        logger.error(f"Get user by phone error: {str(e)}", exc_info=True)
        logger.info("=== GET USER BY PHONE HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': {'code': ERROR_CODES['INTERNAL_ERROR'],'message': str(e)}})
        }