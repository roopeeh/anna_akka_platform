import json
import os
import boto3
from datetime import datetime
import uuid
import sys
sys.path.append('..')
from constants import ORDERS_TABLE, ORDER_ITEMS_TABLE, ERROR_CODES, STATUS_CODES, CORS_HEADERS, ORDER_STATUS, INDEX_NAMES

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table(os.environ[ORDERS_TABLE])  # type: ignore
order_items_table = dynamodb.Table(os.environ[ORDER_ITEMS_TABLE])     # type: ignore

def create_order(order_data, customer_id):
    """Create a new order"""
    order_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    order_item = {
        'id': order_id,
        'customer_id': customer_id,
        'store_id': order_data['store_id'],
        'delivery_address': order_data['delivery_address'],
        'status': ORDER_STATUS['PENDING'],
        'total_amount': order_data.get('total_amount', 0),
        'created_at': timestamp,
        'updated_at': timestamp
    }
    
    orders_table.put_item(Item=order_item)
    return order_item

def get_order_by_id(order_id):
    """Get order by ID"""
    response = orders_table.get_item(Key={'id': order_id})
    return response.get('Item')

def get_orders_by_customer(customer_id, page=1, limit=10):
    """Get orders for a specific customer"""
    query_kwargs = {
        'IndexName': INDEX_NAMES['CUSTOMER_ID_INDEX'],
        'KeyConditionExpression': 'customer_id = :customer_id',
        'ExpressionAttributeValues': {':customer_id': customer_id}
    }
    
    response = orders_table.query(**query_kwargs)
    orders = response.get('Items', [])
    
    # Simple pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_orders = orders[start_idx:end_idx]
    
    return {
        'orders': paginated_orders,
        'pagination': {
            'current_page': page,
            'total_pages': (len(orders) + limit - 1) // limit,
            'total_items': len(orders),
            'items_per_page': limit
        }
    }

def update_order_status(order_id, status, customer_id):
    """Update order status"""
    # First verify ownership
    order = get_order_by_id(order_id)
    if not order or order['customer_id'] != customer_id:
        return None
    
    response = orders_table.update_item(
        Key={'id': order_id},
        UpdateExpression="SET #status = :status, #updated_at = :updated_at",
        ExpressionAttributeValues={
            ':status': status,
            ':updated_at': datetime.utcnow().isoformat()
        },
        ExpressionAttributeNames={
            '#status': 'status',
            '#updated_at': 'updated_at'
        },
        ReturnValues="ALL_NEW"
    )
    
    return response.get('Attributes')

def handler(event, context):
    """Main Lambda handler for orders"""
    try:
        # Parse the request
        path = event.get('requestContext', {}).get('http', {}).get('path', '')
        method = event.get('requestContext', {}).get('http', {}).get('method', '')
        
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Parse body
        body = json.loads(event.get('body', '{}'))
        
        # Route based on path and method
        if path == '/orders' and method == 'GET':
            return handle_get_orders(query_params)
        elif path.startswith('/orders/') and method == 'GET':
            order_id = path.split('/')[-1]
            return handle_get_order(order_id)
        elif path == '/orders' and method == 'POST':
            return handle_create_order(body)
        elif path.startswith('/orders/') and path.endswith('/status') and method == 'PUT':
            order_id = path.split('/')[-2]
            return handle_update_order_status(order_id, body)
        else:
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

def handle_get_orders(query_params):
    """Handle GET /orders"""
    try:
        # In a real app, you'd get the customer_id from the JWT token
        customer_id = "mock-customer-id"
        
        page = int(query_params.get('page', 1))
        limit = int(query_params.get('limit', 10))
        
        result = get_orders_by_customer(customer_id, page, limit)
        
        return {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps(result)
        }
    except Exception as e:
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

def handle_get_order(order_id):
    """Handle GET /orders/{id}"""
    try:
        # In a real app, you'd get the customer_id from the JWT token
        customer_id = "mock-customer-id"
        
        order = get_order_by_id(order_id)
        if not order or order['customer_id'] != customer_id:
            return {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Order not found'
                    }
                })
            }
        
        return {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'order': order})
        }
    except Exception as e:
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

def handle_create_order(body):
    """Handle POST /orders"""
    try:
        # Validate required fields
        if not body.get('store_id') or not body.get('delivery_address') or not body.get('items'):
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Store ID, delivery address, and items are required'
                    }
                })
            }
        
        # In a real app, you'd get the customer_id from the JWT token
        customer_id = "mock-customer-id"
        
        order = create_order(body, customer_id)
        
        return {
            'statusCode': STATUS_CODES['CREATED'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'order': order})
        }
    except Exception as e:
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

def handle_update_order_status(order_id, body):
    """Handle PUT /orders/{id}/status"""
    try:
        # In a real app, you'd get the customer_id from the JWT token
        customer_id = "mock-customer-id"
        
        if not body.get('status'):
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Status is required'
                    }
                })
            }
        
        order = update_order_status(order_id, body['status'], customer_id)
        if not order:
            return {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Order not found or access denied'
                    }
                })
            }
        
        return {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'order': order})
        }
    except Exception as e:
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