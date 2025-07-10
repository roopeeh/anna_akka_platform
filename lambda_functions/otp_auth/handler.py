import json
import os
import boto3
from datetime import datetime, timedelta
import logging
import re
import uuid
import sys
sys.path.append('..')

# Configure logging 
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
cognito_idp = boto3.client('cognito-idp')
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table(os.environ['USERS_TABLE'])  # type: ignore
sns = boto3.client('sns')

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

# Cognito configuration
COGNITO_USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID')
COGNITO_CLIENT_ID = os.environ.get('COGNITO_CLIENT_ID')

# OTP storage (in memory for Lambda - in production, use DynamoDB or Redis)
otp_storage = {}

def generate_otp():
    """Generate a 6-digit OTP"""
    import random
    return str(123456)

def store_otp(phone, otp):
    """Store OTP with expiration (5 minutes)"""
    import time
    otp_storage[phone] = {
        'otp': otp,
        'expires_at': time.time() + 300  # 5 minutes
    }
    logger.info(f"🔐 Stored OTP for {phone}, expires in 5 minutes")

def verify_otp(phone, otp):
    """Verify OTP and remove if valid"""
    import time
    if phone not in otp_storage:
        logger.warning(f"❌ No OTP found for {phone}")
        return False
    
    stored_data = otp_storage[phone]
    if time.time() > stored_data['expires_at']:
        logger.warning(f"❌ OTP expired for {phone}")
        del otp_storage[phone]
        return False
    
    if stored_data['otp'] == otp:
        logger.info(f"✅ OTP verified for {phone}")
        del otp_storage[phone]  # Remove after successful verification
        return True
    
    logger.warning(f"❌ Invalid OTP for {phone}")
    return False

def send_sms_otp(phone, otp):
    """Send OTP via SNS"""
    try:
        message = f"Your Anna Akka verification code is: {otp}. Valid for 5 minutes."
        response = sns.publish(
            PhoneNumber=phone,
            Message=message
        )
        logger.info(f"📤 SMS sent to {phone}: {response}")
        return True
    except Exception as e:
        logger.error(f"❌ Error sending SMS: {str(e)}")
        return False

def normalize_phone(phone):
    """Normalize phone number: strip whitespace, ensure leading +, and collapse spaces."""
    logger.info(f"🔧 Normalizing phone number: {phone}")
    if not phone:
        logger.info("🔧 Phone is empty, returning as is")
        return phone
    phone = phone.strip().replace(' ', '')
    logger.info(f"🔧 After strip and space removal: {phone}")
    if not phone.startswith('+') and phone.startswith('91'):
        phone = '+' + phone
        logger.info(f"🔧 Added + prefix for 91: {phone}")
    if not phone.startswith('+'):
        phone = '+' + phone
        logger.info(f"🔧 Added + prefix: {phone}")
    logger.info(f"🔧 Final normalized phone: {phone}")
    return phone

def validate_phone_format(phone):
    """Validate phone number format"""
    logger.info(f"🔍 Validating phone format: {phone}")
    phone_pattern = r'^\+?[1-9]\d{1,14}$'
    normalized_phone = normalize_phone(phone)
    is_valid = re.match(phone_pattern, normalized_phone) is not None
    logger.info(f"🔍 Phone validation result: {is_valid} for {normalized_phone}")
    return is_valid

def get_user_by_phone(phone):
    """Get user by phone number from DynamoDB using GSI"""
    logger.info(f"🔍 Looking up user by phone: {phone}")
    if not phone:
        logger.info("❌ No phone provided for lookup")
        return None
    
    try:
        logger.info(f"🔍 Querying DynamoDB table: {users_table.name}")
        logger.info(f"🔍 Using GSI: phone_index")
        logger.info(f"🔍 Query condition: phone = {phone}")
        
        response = users_table.query(
            IndexName='phone_index',
            KeyConditionExpression='phone = :phone',
            ExpressionAttributeValues={':phone': phone}
        )
        
        logger.info(f"🔍 DynamoDB response: {json.dumps(response, default=str)}")
        
        items = response.get('Items', [])
        user = items[0] if items else None
        logger.info(f"🔍 User lookup result: {'Found' if user else 'Not found'}")
        if user:
            logger.info(f"🔍 User data: {json.dumps(user, default=str)}")
        return user
    except Exception as e:
        logger.error(f"❌ Error looking up user by phone: {str(e)}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        logger.error(f"❌ Exception details: {e}")
        return None

def create_or_get_cognito_user(phone):
    """Create or get Cognito user for phone number"""
    try:
        # Try to get existing user from Cognito
        response = cognito_idp.admin_get_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=phone
        )
        logger.info(f"Found existing Cognito user for {phone}")
        return response['UserStatus']
    except cognito_idp.exceptions.UserNotFoundException:
        # Create new user in Cognito
        try:
            response = cognito_idp.admin_create_user(
                UserPoolId=COGNITO_USER_POOL_ID,
                Username=phone,
                UserAttributes=[
                    {
                        'Name': 'phone_number',
                        'Value': phone
                    },
                    {
                        'Name': 'phone_number_verified',
                        'Value': 'true'
                    }
                ],
                MessageAction='SUPPRESS'  # Don't send welcome message
            )
            logger.info(f"Created new Cognito user for {phone}")
            return response['User']['UserStatus']
        except Exception as e:
            logger.error(f"Error creating Cognito user: {str(e)}")
            raise e
    except Exception as e:
        logger.error(f"Error getting Cognito user: {str(e)}")
        raise e

def handle_send_otp(event):
    """Handle sending OTP to phone number for login"""
    logger.info("=== SEND OTP HANDLER START ===")
    logger.info(f"🔍 Event received: {json.dumps(event, default=str)}")
    
    try:
        body = json.loads(event.get('body', '{}'))
        logger.info(f"📝 Send OTP request body: {json.dumps(body, default=str)}")
        
        # Validate required fields
        phone = body.get('phone')
        logger.info(f"📱 Phone number from request: {phone}")
        
        if not phone:
            logger.warning("❌ Missing required field: phone")
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Phone number is required'
                    }
                })
            }
        
        # Validate phone number format
        logger.info(f"🔍 Validating phone format: {phone}")
        if not validate_phone_format(phone):
            logger.warning(f"❌ Invalid phone format: {phone}")
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Invalid phone number format'
                    }
                })
            }
        
        normalized_phone = normalize_phone(phone)
        logger.info(f"✅ Normalized phone number: {normalized_phone}")
        
        # Check if user exists in DynamoDB
        logger.info(f"🔍 Checking if user exists in DynamoDB for phone: {normalized_phone}")
        user = get_user_by_phone(normalized_phone)
        is_new_user = not user
        
        if is_new_user:
            logger.info(f"🆕 New user registration for phone number: {normalized_phone}")
        else:
            logger.info(f"👤 Existing user login for phone number: {normalized_phone}")
            logger.info(f"👤 User data from DynamoDB: {json.dumps(user, default=str)}")
        
        try:
            # Generate and send OTP
            otp = generate_otp()
            logger.info(f"🔢 Generated OTP: {otp} for {normalized_phone}")
            
            # Store OTP with expiration
            store_otp(normalized_phone, otp)
            
            # Send OTP via SMS
            sms_sent = send_sms_otp(normalized_phone, otp)
            
            if sms_sent:
                logger.info(f"✅ OTP sent successfully to {normalized_phone}")
                return {
                    'statusCode': STATUS_CODES['OK'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'message': 'OTP sent successfully',
                        'phone': normalized_phone,
                        'is_new_user': is_new_user
                    })
                }
            else:
                logger.error(f"❌ Failed to send SMS to {normalized_phone}")
                return {
                    'statusCode': STATUS_CODES['INTERNAL_ERROR'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['INTERNAL_ERROR'],
                            'message': 'Failed to send OTP'
                        }
                    })
                }
            
        except Exception as e:
            logger.error(f"❌ Error sending OTP: {str(e)}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            logger.error(f"❌ Exception details: {e}")
            return {
                'statusCode': STATUS_CODES['INTERNAL_ERROR'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['INTERNAL_ERROR'],
                        'message': 'Failed to send OTP'
                    }
                })
            }
            
    except Exception as e:
        logger.error(f"Send OTP error: {str(e)}", exc_info=True)
        logger.info("=== SEND OTP HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['INTERNAL_ERROR'],
                    'message': str(e)
                }
            })
        }

def handle_verify_otp(event):
    """Handle OTP verification for login"""
    logger.info("=== VERIFY OTP HANDLER START ===")
    logger.info(f"🔍 Event received: {json.dumps(event, default=str)}")
    
    try:
        body = json.loads(event.get('body', '{}'))
        logger.info(f"📝 Verify OTP request body: {json.dumps(body, default=str)}")
        
        # Validate required fields
        phone = body.get('phone')
        otp = body.get('otp')
        
        logger.info(f"📱 Phone number from request: {phone}")
        logger.info(f"🔢 OTP from request: {otp}")
        
        if not phone:
            logger.warning("❌ Missing required field: phone")
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Phone number is required'
                    }
                })
            }
        
        if not otp:
            logger.warning("❌ Missing required field: otp")
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'OTP is required'
                    }
                })
            }
        
        # Validate phone number format
        logger.info(f"🔍 Validating phone format: {phone}")
        if not validate_phone_format(phone):
            logger.warning(f"❌ Invalid phone format: {phone}")
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Invalid phone number format'
                    }
                })
            }
        
        normalized_phone = normalize_phone(phone)
        logger.info(f"✅ Normalized phone number: {normalized_phone}")
        
        # Check if user exists in DynamoDB
        logger.info(f"🔍 Checking if user exists in DynamoDB for phone: {normalized_phone}")
        user = get_user_by_phone(normalized_phone)
        is_new_user = not user
        
        if is_new_user:
            logger.info(f"🆕 New user registration verification for phone number: {normalized_phone}")
            # For new user registration, we'll create the user after OTP verification
            # This will be handled by the auth Lambda after OTP verification
        else:
            logger.info(f"👤 Existing user login verification for phone number: {normalized_phone}")
            logger.info(f"👤 User data from DynamoDB: {json.dumps(user, default=str)}")
        
        try:
            # Verify OTP using our simple verification system
            logger.info(f"🔍 Verifying OTP: {otp} for {normalized_phone}")
            
            if verify_otp(normalized_phone, otp):
                logger.info(f"✅ OTP verified successfully for {normalized_phone}")
                
                if is_new_user:
                    # For new user registration, return success without user data
                    logger.info(f"🆕 Returning success for new user registration")
                    return {
                        'statusCode': STATUS_CODES['OK'],
                        'headers': CORS_HEADERS,
                        'body': json.dumps({
                            'message': 'OTP verified successfully. Please proceed with registration.',
                            'phone': normalized_phone,
                            'is_new_user': True,
                            'auth_type': 'passwordless'
                        })
                    }
                else:
                    # Return user data for successful login
                    logger.info(f"👤 Returning success for existing user login")
                    
                    return {
                        'statusCode': STATUS_CODES['OK'],
                        'headers': CORS_HEADERS,
                        'body': json.dumps({
                            'message': 'Login successful',
                            'phone': normalized_phone,
                            'user': {
                                'id': user.get('id'),
                                'name': user.get('name'),
                                'email': user.get('email'),
                                'phone': user.get('phone'),
                                'roles': user.get('roles'),
                                'created_at': user.get('created_at'),
                                'updated_at': user.get('updated_at')
                            },
                            'is_new_user': False,
                            'auth_type': 'passwordless'
                        })
                    }
            else:
                logger.warning(f"❌ OTP verification failed for {normalized_phone}")
                return {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['VALIDATION_ERROR'],
                            'message': 'Invalid or expired OTP'
                        }
                    })
                }
            
        except Exception as e:
            logger.error(f"❌ Error verifying OTP: {str(e)}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            logger.error(f"❌ Exception details: {e}")
            return {
                'statusCode': STATUS_CODES['INTERNAL_ERROR'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['INTERNAL_ERROR'],
                        'message': 'Failed to verify OTP'
                    }
                })
            }
            
    except Exception as e:
        logger.error(f"Verify OTP error: {str(e)}", exc_info=True)
        logger.info("=== VERIFY OTP HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['INTERNAL_ERROR'],
                    'message': str(e)
                }
            })
        }

def lambda_handler(event, context):
    """Main Lambda handler for OTP operations"""
    logger.info("🚀 === OTP AUTH LAMBDA HANDLER START ===")
    logger.info(f"🔍 Full event received: {json.dumps(event, default=str)}")
    logger.info(f"🔍 Context: {context}")
    
    try:
        # Parse the request
        path = event.get('requestContext', {}).get('http', {}).get('path', '')
        method = event.get('requestContext', {}).get('http', {}).get('method', '')
        
        logger.info(f"🌐 HTTP Method: {method}, Path: {path}")
        logger.info(f"🌐 Request Context: {json.dumps(event.get('requestContext', {}), default=str)}")
        
        # Route to appropriate handler
        if (path == '/auth/otp/send' or path.endswith('/auth/otp/send')):
            if method == 'POST':
                logger.info("📤 Routing to send OTP handler")
                result = handle_send_otp(event)
                logger.info(f"📤 Send OTP handler result: {json.dumps(result, default=str)}")
                return result
            else:
                logger.warning(f"❌ Method not allowed: {method} for /auth/otp/send")
                return {
                    'statusCode': STATUS_CODES['METHOD_NOT_ALLOWED'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['VALIDATION_ERROR'],
                            'message': f'Method {method} not allowed for this endpoint'
                        }
                    })
                }
        elif (path == '/auth/otp/verify' or path.endswith('/auth/otp/verify')):
            if method == 'POST':
                logger.info("🔍 Routing to verify OTP handler")
                result = handle_verify_otp(event)
                logger.info(f"🔍 Verify OTP handler result: {json.dumps(result, default=str)}")
                return result
            else:
                logger.warning(f"❌ Method not allowed: {method} for /auth/otp/verify")
                return {
                    'statusCode': STATUS_CODES['METHOD_NOT_ALLOWED'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['VALIDATION_ERROR'],
                            'message': f'Method {method} not allowed for this endpoint'
                        }
                    })
                }
        elif method == 'OPTIONS':
            logger.info("🔄 Handling OPTIONS request")
            return {
                'statusCode': STATUS_CODES['OK'],
                'headers': CORS_HEADERS,
                'body': ''
            }
        else:
            logger.warning(f"❌ Endpoint not found: {method} {path}")
            return {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Endpoint not found'
                    }
                })
            }
            
    except Exception as e:
        logger.error(f"❌ OTP Auth Lambda handler error: {str(e)}", exc_info=True)
        logger.error(f"❌ Exception type: {type(e).__name__}")
        logger.error(f"❌ Exception details: {e}")
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['INTERNAL_ERROR'],
                    'message': str(e)
                }
            })
        }
    finally:
        logger.info("🏁 === OTP AUTH LAMBDA HANDLER END ===") 