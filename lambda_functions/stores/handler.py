import json
import os
import boto3
from datetime import datetime
import uuid

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
stores_table = dynamodb.Table(os.environ['STORES_TABLE'])

def get_stores_with_pagination(page=1, limit=10, search=None, is_open=None):
    """Get stores with pagination and filtering"""
    scan_kwargs = {}
    
    # Add filters
    filter_expressions = []
    expression_values = {}
    
    if search:
        filter_expressions.append("contains(#name, :search)")
        expression_values[':search'] = search
        scan_kwargs['ExpressionAttributeNames'] = {'#name': 'name'}
    
    if is_open is not None:
        filter_expressions.append("#is_open = :is_open")
        expression_values[':is_open'] = is_open
        if 'ExpressionAttributeNames' not in scan_kwargs:
            scan_kwargs['ExpressionAttributeNames'] = {}
        scan_kwargs['ExpressionAttributeNames']['#is_open'] = 'is_open'
    
    if filter_expressions:
        scan_kwargs['FilterExpression'] = ' AND '.join(filter_expressions)
        scan_kwargs['ExpressionAttributeValues'] = expression_values
    
    # Get all items (in a real app, you'd implement proper pagination)
    response = stores_table.scan(**scan_kwargs)
    stores = response.get('Items', [])
    
    # Simple pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_stores = stores[start_idx:end_idx]
    
    return {
        'stores': paginated_stores,
        'pagination': {
            'current_page': page,
            'total_pages': (len(stores) + limit - 1) // limit,
            'total_items': len(stores),
            'items_per_page': limit
        }
    }

def get_store_by_id(store_id):
    """Get store by ID"""
    response = stores_table.get_item(Key={'id': store_id})
    return response.get('Item')

def create_store(store_data, owner_id):
    """Create a new store"""
    store_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    store_item = {
        'id': store_id,
        'owner_id': owner_id,
        'name': store_data['name'],
        'address': store_data['address'],
        'phone': store_data.get('phone'),
        'is_open': True,
        'rating': 0,
        'delivery_time': store_data.get('delivery_time', '30-45 min'),
        'created_at': timestamp,
        'updated_at': timestamp
    }
    
    stores_table.put_item(Item=store_item)
    return store_item

def update_store(store_id, update_data, owner_id):
    """Update store details"""
    # First verify ownership
    store = get_store_by_id(store_id)
    if not store or store['owner_id'] != owner_id:
        return None
    
    # Prepare update expression
    update_expression = "SET "
    expression_values = {}
    expression_names = {}
    
    for key, value in update_data.items():
        if key in ['name', 'address', 'phone', 'is_open', 'delivery_time']:
            update_expression += f"#{key} = :{key}, "
            expression_values[f':{key}'] = value
            expression_names[f'#{key}'] = key
    
    update_expression += "#updated_at = :updated_at"
    expression_values[':updated_at'] = datetime.utcnow().isoformat()
    expression_names['#updated_at'] = 'updated_at'
    
    response = stores_table.update_item(
        Key={'id': store_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ExpressionAttributeNames=expression_names,
        ReturnValues="ALL_NEW"
    )
    
    return response.get('Attributes')

def get_stores_by_owner(owner_id):
    """Get stores owned by a specific user"""
    response = stores_table.query(
        IndexName='owner_id_index',
        KeyConditionExpression='owner_id = :owner_id',
        ExpressionAttributeValues={':owner_id': owner_id}
    )
    
    return response.get('Items', [])

def handler(event, context):
    """Main Lambda handler for stores"""
    try:
        # Parse the request
        path = event.get('requestContext', {}).get('http', {}).get('path', '')
        method = event.get('requestContext', {}).get('http', {}).get('method', '')
        
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Parse body
        body = json.loads(event.get('body', '{}'))
        
        # Route based on path and method
        if path == '/stores' and method == 'GET':
            return handle_get_stores(query_params)
        elif path.startswith('/stores/') and method == 'GET':
            store_id = path.split('/')[-1]
            return handle_get_store(store_id)
        elif path == '/stores' and method == 'POST':
            return handle_create_store(body)
        elif path.startswith('/stores/') and method == 'PUT':
            store_id = path.split('/')[-1]
            return handle_update_store(store_id, body)
        elif path.startswith('/stores/') and method == 'DELETE':
            store_id = path.split('/')[-1]
            return handle_delete_store(store_id)
        elif path == '/stores/owner' and method == 'GET':
            return handle_get_owner_stores()
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
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
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            })
        }
# ... rest of the file ... 