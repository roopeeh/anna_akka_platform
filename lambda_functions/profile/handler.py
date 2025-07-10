import json
import os
import boto3
from datetime import datetime
import logging
import re
import sys
sys.path.append('..')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table(os.environ['USERS_TABLE'])  # type: ignore

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

ALLOWED_UPDATE_FIELDS = {
    'USER_PROFILE': ['name', 'phone', 'address', 'email']
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

# Remove the old extract_user_from_token function - now using the one from constants

def get_user_by_id(user_id):
    """Get user by ID from DynamoDB"""
    logger.info(f"Looking up user by ID: {user_id}")
    try:
        response = users_table.get_item(Key={'id': user_id})
        user = response.get('Item')
        logger.info(f"User lookup result: {'Found' if user else 'Not found'}")
        return user
    except Exception as e:
        logger.error(f"Error looking up user by ID: {str(e)}")
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

def update_user_profile(user_id, update_data):
    """Update user profile"""
    logger.info(f"Updating user profile for ID: {user_id}")
    logger.info(f"Update data: {json.dumps(update_data, default=str)}")
    
    try:
        # Prepare update expression
        update_expression = "SET "
        expression_values = {}
        expression_names = {}
        
        for key, value in update_data.items():
            if key in ALLOWED_UPDATE_FIELDS['USER_PROFILE']:
                update_expression += f"#{key} = :{key}, "
                expression_values[f':{key}'] = value
                expression_names[f'#{key}'] = key
        
        update_expression += "#updated_at = :updated_at"
        expression_values[':updated_at'] = datetime.utcnow().isoformat()
        expression_names['#updated_at'] = 'updated_at'
        
        logger.info(f"Update expression: {update_expression}")
        logger.info(f"Expression values: {json.dumps(expression_values, default=str)}")
        
        response = users_table.update_item(
            Key={'id': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names,
            ReturnValues="ALL_NEW"
        )
        
        updated_user = response.get('Attributes')
        logger.info(f"User profile updated successfully: {updated_user is not None}")
        return updated_user
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        return None

def delete_user_profile(user_id):
    """Delete user profile"""
    logger.info(f"Deleting user profile for ID: {user_id}")
    
    try:
        response = users_table.delete_item(
            Key={'id': user_id},
            ReturnValues="ALL_OLD"
        )
        
        deleted_user = response.get('Attributes')
        logger.info(f"User profile deleted successfully: {deleted_user is not None}")
        return deleted_user
    except Exception as e:
        logger.error(f"Error deleting user profile: {str(e)}")
        return None

def handler(event, context):
    """Main Lambda handler for profile operations"""
    logger.info("=== PROFILE HANDLER START ===")
    logger.info(f"Event: {json.dumps(event, default=str)}")
    logger.info(f"Context: {json.dumps({'function_name': context.function_name, 'function_version': context.function_version, 'invoked_function_arn': context.invoked_function_arn, 'memory_limit_in_mb': context.memory_limit_in_mb, 'remaining_time_in_millis': context.get_remaining_time_in_millis()}, default=str)}")
    
    try:
        # Parse the request
        path = event.get('requestContext', {}).get('http', {}).get('path', '')
        method = event.get('requestContext', {}).get('http', {}).get('method', '')
        
        logger.info(f"Request path: {path}")
        logger.info(f"Request method: {method}")
        
        # Parse body
        body = json.loads(event.get('body', '{}'))
        logger.info(f"Request body: {json.dumps(body, default=str)}")
        
        # Route based on path and method
        if (path == '/profile' or path.endswith('/profile')) and method == 'GET':
            logger.info("Routing to get profile handler")
            response = handle_get_profile(event)
            logger.info(f"Get profile response: {json.dumps(response, default=str)}")
            return response
        elif (path == '/profile' or path.endswith('/profile')) and method == 'PUT':
            logger.info("Routing to update profile handler")
            response = handle_update_profile(event, body)
            logger.info(f"Update profile response: {json.dumps(response, default=str)}")
            return response
        elif (path == '/profile' or path.endswith('/profile')) and method == 'DELETE':
            logger.info("Routing to delete profile handler")
            response = handle_delete_profile(event)
            logger.info(f"Delete profile response: {json.dumps(response, default=str)}")
            return response
        elif (path.startswith('/profile/phone') or path.endswith('/profile/phone')) and method == 'GET':
            logger.info("Routing to get profile by phone handler")
            response = handle_get_profile_by_phone(event)
            logger.info(f"Get profile by phone response: {json.dumps(response, default=str)}")
            return response
        else:
            logger.warning(f"Endpoint not found: {method} {path}")
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
        logger.error(f"Handler error: {str(e)}", exc_info=True)
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
        logger.info("=== PROFILE HANDLER END ===")

def handle_get_profile(event):
    """Handle GET /profile"""
    logger.info("=== GET PROFILE HANDLER START ===")
    try:
        # For now, use a mock user ID - security will be implemented later
        user_id = 'mock-user-id'
        logger.info(f"Getting profile for user ID: {user_id}")
        
        user = get_user_by_id(user_id)
        
        if not user:
            logger.warning(f"User not found for ID: {user_id}")
            return {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'User not found'
                    }
                })
            }
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'user': user})
        }
        
        logger.info("=== GET PROFILE HANDLER END ===")
        return response
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}", exc_info=True)
        logger.info("=== GET PROFILE HANDLER END ===")
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

def handle_get_profile_by_phone(event):
    """Handle GET /profile/phone?phone=<phone_number>"""
    logger.info("=== GET PROFILE BY PHONE HANDLER START ===")
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
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Phone parameter is required'
                    }
                })
            }
        
        # Validate phone number format
        phone_pattern = r'^\+?[1-9]\d{1,14}$'
        normalized_phone = normalize_phone(phone)
        if not re.match(phone_pattern, normalized_phone):
            logger.warning(f"Invalid phone format: {phone}")
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
        
        # Find user by phone number
        user = get_user_by_phone(normalized_phone)
        if not user:
            logger.warning(f"User not found for phone number: {normalized_phone}")
            return {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': f'User not found with phone number: {normalized_phone}'
                    }
                })
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
        
        logger.info("=== GET PROFILE BY PHONE HANDLER END ===")
        return response
        
    except Exception as e:
        logger.error(f"Get profile by phone error: {str(e)}", exc_info=True)
        logger.info("=== GET PROFILE BY PHONE HANDLER END ===")
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

def handle_update_profile(event, body):
    """Handle PUT /profile"""
    logger.info("=== UPDATE PROFILE HANDLER START ===")
    try:
        # For now, use a mock user ID - security will be implemented later
        user_id = 'mock-user-id'
        logger.info(f"Updating profile for user ID: {user_id}")
        logger.info(f"Update request body: {json.dumps(body, default=str)}")
        
        # Validate that at least one field is provided
        allowed_fields = ALLOWED_UPDATE_FIELDS['USER_PROFILE']
        update_data = {}
        
        for field in allowed_fields:
            if field in body:
                update_data[field] = body[field]
        
        logger.info(f"Fields to update: {list(update_data.keys())}")
        
        if not update_data:
            logger.warning("No valid fields provided for update")
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'At least one field must be provided for update'
                    }
                })
            }
        
        # Normalize phone number if provided
        if 'phone' in update_data:
            update_data['phone'] = normalize_phone(update_data['phone'])
        
        updated_user = update_user_profile(user_id, update_data)
        
        if not updated_user:
            logger.warning(f"User not found for update, ID: {user_id}")
            return {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'User not found'
                    }
                })
            }
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'user': updated_user})
        }
        
        logger.info("=== UPDATE PROFILE HANDLER END ===")
        return response
        
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}", exc_info=True)
        logger.info("=== UPDATE PROFILE HANDLER END ===")
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

def handle_delete_profile(event):
    """Handle DELETE /profile"""
    logger.info("=== DELETE PROFILE HANDLER START ===")
    try:
        # For now, use a mock user ID - security will be implemented later
        user_id = 'mock-user-id'
        logger.info(f"Deleting profile for user ID: {user_id}")
        
        deleted_user = delete_user_profile(user_id)
        
        if not deleted_user:
            logger.warning(f"User not found for deletion, ID: {user_id}")
            return {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'User not found'
                    }
                })
            }
        
        response = {
            'statusCode': STATUS_CODES['NO_CONTENT'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'message': 'User profile deleted successfully',
                'deleted_user': deleted_user
            })
        }
        
        logger.info("=== DELETE PROFILE HANDLER END ===")
        return response
        
    except Exception as e:
        logger.error(f"Delete profile error: {str(e)}", exc_info=True)
        logger.info("=== DELETE PROFILE HANDLER END ===")
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