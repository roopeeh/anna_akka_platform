import json
import os
import boto3
from datetime import datetime
import uuid
from constants import USERS_TABLE, ERROR_CODES, STATUS_CODES, CORS_HEADERS, USER_TYPES, MOCK_VALUES

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table(os.environ[USERS_TABLE])  # type: ignore

def create_user(user_data):
    """Create a new user in DynamoDB"""
    user_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    user_item = {
        'id': user_id,
        'email': user_data['email'],
        'name': user_data['name'],
        'user_type': user_data.get('user_type', USER_TYPES['CUSTOMER']),
        'phone': user_data.get('phone'),
        'address': user_data.get('address'),
        'created_at': timestamp,
        'updated_at': timestamp
    }
    
    users_table.put_item(Item=user_item)
    return user_item

def get_user_by_email(email):
    """Get user by email from DynamoDB"""
    response = users_table.scan(
        FilterExpression='email = :email',
        ExpressionAttributeValues={':email': email}
    )
    
    items = response.get('Items', [])
    return items[0] if items else None

def handler(event, context):
    """Main Lambda handler for authentication"""
    try:
        # Parse the request
        path = event.get('requestContext', {}).get('http', {}).get('path', '')
        method = event.get('requestContext', {}).get('http', {}).get('method', '')
        
        # Parse body
        body = json.loads(event.get('body', '{}'))
        
        # Route based on path and method
        if path.startswith('/auth/register') and method == 'POST':
            return handle_register(body)
        elif path.startswith('/auth/login') and method == 'POST':
            return handle_login(body)
        else:
            return {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': {'code': ERROR_CODES['NOT_FOUND'],'message': 'Endpoint not found'}})
            }
            
    except Exception as e:
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': {'code': ERROR_CODES['INTERNAL_ERROR'],'message': str(e)}})
        }

def handle_register(body):
    """Handle user registration"""
    try:
        # Validate required fields
        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if not body.get(field):
                return {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'],'message': f'Missing required field: {field}'}})
                }
        
        # Check if user already exists
        existing_user = get_user_by_email(body['email'])
        if existing_user:
            return {
                'statusCode': STATUS_CODES['CONFLICT'],
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': {'code': ERROR_CODES['CONFLICT'],'message': 'Email already exists'}})
            }
        
        # Create user
        user_data = {
            'email': body['email'],
            'name': body['name'],
            'user_type': body.get('user_type', USER_TYPES['CUSTOMER']),
            'phone': body.get('phone'),
            'address': body.get('address')
        }
        
        user = create_user(user_data)
        
        # In a real implementation, you would generate a JWT token here
        # For now, we'll return a mock token
        token = f"mock-jwt-token-{user['id']}"
        
        return {
            'statusCode': STATUS_CODES['CREATED'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'user': user,'token': token})
        }
        
    except Exception as e:
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': {'code': ERROR_CODES['INTERNAL_ERROR'],'message': str(e)}})
        }

def handle_login(body):
    """Handle user login"""
    try:
        # Validate required fields
        if not body.get('email') or not body.get('password'):
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'],'message': 'Email and password are required'}})
            }
        
        # Find user by email
        user = get_user_by_email(body['email'])
        if not user:
            return {
                'statusCode': STATUS_CODES['UNAUTHORIZED'],
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': {'code': ERROR_CODES['UNAUTHORIZED'],'message': 'Invalid email or password'}})
            }
        
        # In a real implementation, you would verify the password here
        # For now, we'll assume the password is correct
        token = f"mock-jwt-token-{user['id']}"
        
        return {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'user': user,'token': token})
        }
        
    except Exception as e:
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': {'code': ERROR_CODES['INTERNAL_ERROR'],'message': str(e)}})
        } 