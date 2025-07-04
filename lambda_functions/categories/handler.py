import json
import os
import boto3
from datetime import datetime
import uuid
import sys
sys.path.append('..')
from constants import CATEGORIES_TABLE, ERROR_CODES, STATUS_CODES, CORS_HEADERS

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
categories_table = dynamodb.Table(os.environ[CATEGORIES_TABLE])  # type: ignore

def get_all_categories():
    """Get all categories"""
    response = categories_table.scan()
    return response.get('Items', [])

def create_category(category_data):
    """Create a new category"""
    category_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    category_item = {
        'id': category_id,
        'name': category_data['name'],
        'created_at': timestamp
    }
    
    categories_table.put_item(Item=category_item)
    return category_item

def handler(event, context):
    """Main Lambda handler for categories"""
    try:
        # Parse the request
        path = event.get('requestContext', {}).get('http', {}).get('path', '')
        method = event.get('requestContext', {}).get('http', {}).get('method', '')
        
        # Parse body
        body = json.loads(event.get('body', '{}'))
        
        # Route based on path and method
        if path == '/categories' and method == 'GET':
            return handle_get_categories()
        elif path == '/categories' and method == 'POST':
            return handle_create_category(body)
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                },
                'body': json.dumps({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Endpoint not found'
                    }
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            })
        }

def handle_get_categories():
    """Handle GET /categories"""
    try:
        categories = get_all_categories()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({'categories': categories})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            })
        }

def handle_create_category(body):
    """Handle POST /categories"""
    try:
        # Validate required fields
        if not body.get('name'):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                },
                'body': json.dumps({
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Category name is required'
                    }
                })
            }
        
        category = create_category(body)
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps(category)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            })
        } 