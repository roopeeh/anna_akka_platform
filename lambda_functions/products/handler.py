import json
import os
import boto3
from datetime import datetime
import uuid
import sys
sys.path.append('..')
from constants import PRODUCTS_TABLE, ERROR_CODES, STATUS_CODES, CORS_HEADERS, INDEX_NAMES, ALLOWED_UPDATE_FIELDS

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
products_table = dynamodb.Table(os.environ[PRODUCTS_TABLE])  # type: ignore

def get_products_with_pagination(page=1, limit=20, store_id=None, category_id=None, search=None, min_price=None, max_price=None, in_stock=None):
    """Get products with pagination and filtering"""
    scan_kwargs = {}
    
    # Add filters
    filter_expressions = []
    expression_values = {}
    expression_names = {}
    
    if store_id:
        filter_expressions.append("#store_id = :store_id")
        expression_values[':store_id'] = store_id
        expression_names['#store_id'] = 'store_id'
    
    if category_id:
        filter_expressions.append("#category_id = :category_id")
        expression_values[':category_id'] = category_id
        expression_names['#category_id'] = 'category_id'
    
    if search:
        filter_expressions.append("contains(#name, :search)")
        expression_values[':search'] = search
        expression_names['#name'] = 'name'
    
    if min_price is not None:
        filter_expressions.append("#price >= :min_price")
        expression_values[':min_price'] = min_price
        expression_names['#price'] = 'price'
    
    if max_price is not None:
        filter_expressions.append("#price <= :max_price")
        expression_values[':max_price'] = max_price
        if '#price' not in expression_names:
            expression_names['#price'] = 'price'
    
    if in_stock is not None:
        if in_stock:
            filter_expressions.append("#stock > :zero")
        else:
            filter_expressions.append("#stock <= :zero")
        expression_values[':zero'] = 0
        expression_names['#stock'] = 'stock'
    
    if filter_expressions:
        scan_kwargs['FilterExpression'] = ' AND '.join(filter_expressions)
        scan_kwargs['ExpressionAttributeValues'] = expression_values
        scan_kwargs['ExpressionAttributeNames'] = expression_names
    
    # Get all items (in a real app, you'd implement proper pagination)
    response = products_table.scan(**scan_kwargs)
    products = response.get('Items', [])
    
    # Simple pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_products = products[start_idx:end_idx]
    
    return {
        'products': paginated_products,
        'pagination': {
            'current_page': page,
            'total_pages': (len(products) + limit - 1) // limit,
            'total_items': len(products),
            'items_per_page': limit
        }
    }

def get_product_by_id(product_id):
    """Get product by ID"""
    response = products_table.get_item(Key={'id': product_id})
    return response.get('Item')

def create_product(product_data, store_id):
    """Create a new product"""
    product_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    product_item = {
        'id': product_id,
        'store_id': store_id,
        'category_id': product_data.get('category_id'),
        'name': product_data['name'],
        'description': product_data.get('description'),
        'price': product_data['price'],
        'unit': product_data.get('unit', 'piece'),
        'stock': product_data.get('stock', 0),
        'image_url': product_data.get('image_url'),
        'created_at': timestamp,
        'updated_at': timestamp
    }
    
    products_table.put_item(Item=product_item)
    return product_item

def update_product(product_id, update_data, store_id):
    """Update product details"""
    # First verify ownership
    product = get_product_by_id(product_id)
    if not product or product['store_id'] != store_id:
        return None
    
    # Prepare update expression
    update_expression = "SET "
    expression_values = {}
    expression_names = {}
    
    for key, value in update_data.items():
        if key in ['name', 'description', 'price', 'unit', 'stock', 'image_url', 'category_id']:
            update_expression += f"#{key} = :{key}, "
            expression_values[f':{key}'] = value
            expression_names[f'#{key}'] = key
    
    update_expression += "#updated_at = :updated_at"
    expression_values[':updated_at'] = datetime.utcnow().isoformat()
    expression_names['#updated_at'] = 'updated_at'
    
    response = products_table.update_item(
        Key={'id': product_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ExpressionAttributeNames=expression_names,
        ReturnValues="ALL_NEW"
    )
    
    return response.get('Attributes')

def get_store_products(store_id, page=1, limit=20, category_id=None, search=None):
    """Get products for a specific store"""
    query_kwargs = {
        'IndexName': 'store_id_index',
        'KeyConditionExpression': 'store_id = :store_id',
        'ExpressionAttributeValues': {':store_id': store_id}
    }
    
    # Add filters
    filter_expressions = []
    expression_values = query_kwargs['ExpressionAttributeValues']
    expression_names = {}
    
    if category_id:
        filter_expressions.append("#category_id = :category_id")
        expression_values[':category_id'] = category_id
        expression_names['#category_id'] = 'category_id'
    
    if search:
        filter_expressions.append("contains(#name, :search)")
        expression_values[':search'] = search
        expression_names['#name'] = 'name'
    
    if filter_expressions:
        query_kwargs['FilterExpression'] = ' AND '.join(filter_expressions)
        query_kwargs['ExpressionAttributeNames'] = expression_names
    
    response = products_table.query(**query_kwargs)
    products = response.get('Items', [])
    
    # Simple pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_products = products[start_idx:end_idx]
    
    return {
        'products': paginated_products,
        'pagination': {
            'current_page': page,
            'total_pages': (len(products) + limit - 1) // limit,
            'total_items': len(products),
            'items_per_page': limit
        }
    }

def handler(event, context):
    """Main Lambda handler for products"""
    try:
        # Parse the request
        path = event.get('requestContext', {}).get('http', {}).get('path', '')
        method = event.get('requestContext', {}).get('http', {}).get('method', '')
        
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Parse body
        body = json.loads(event.get('body', '{}'))
        
        # Route based on path and method
        if path == '/products' and method == 'GET':
            return handle_get_products(query_params)
        elif path.startswith('/products/') and method == 'GET':
            product_id = path.split('/')[-1]
            return handle_get_product(product_id)
        elif path.startswith('/stores/') and '/products' in path and method == 'GET':
            # Handle /stores/{storeId}/products
            path_parts = path.split('/')
            store_id = path_parts[2]
            return handle_get_store_products(store_id, query_params)
        elif path.startswith('/stores/') and '/products' in path and method == 'POST':
            # Handle POST /stores/{storeId}/products
            path_parts = path.split('/')
            store_id = path_parts[2]
            return handle_create_product(body, store_id)
        elif path.startswith('/products/') and method == 'PUT':
            product_id = path.split('/')[-1]
            return handle_update_product(product_id, body)
        elif path.startswith('/products/') and method == 'DELETE':
            product_id = path.split('/')[-1]
            return handle_delete_product(product_id)
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
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['INTERNAL_ERROR'],
                    'message': str(e)
                }
            })
        }

def handle_get_products(query_params):
    """Handle GET /products"""
    try:
        page = int(query_params.get('page', 1))
        limit = int(query_params.get('limit', 20))
        store_id = query_params.get('store_id')
        category_id = query_params.get('category_id')
        search = query_params.get('search')
        min_price = float(query_params.get('min_price')) if query_params.get('min_price') else None
        max_price = float(query_params.get('max_price')) if query_params.get('max_price') else None
        in_stock = query_params.get('in_stock')
        if in_stock is not None:
            in_stock = in_stock.lower() == 'true'
        
        result = get_products_with_pagination(
            page, limit, store_id, category_id, search, min_price, max_price, in_stock
        )
        
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

def handle_get_product(product_id):
    """Handle GET /products/{id}"""
    try:
        product = get_product_by_id(product_id)
        if not product:
            return {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Product not found'
                    }
                })
            }
        
        return {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'product': product})
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

def handle_get_store_products(store_id, query_params):
    """Handle GET /stores/{storeId}/products"""
    try:
        page = int(query_params.get('page', 1))
        limit = int(query_params.get('limit', 20))
        category_id = query_params.get('category_id')
        search = query_params.get('search')
        
        result = get_store_products(store_id, page, limit, category_id, search)
        
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

def handle_create_product(body, store_id):
    """Handle POST /stores/{storeId}/products"""
    try:
        # Validate required fields
        if not body.get('name') or not body.get('price'):
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Name and price are required'
                    }
                })
            }
        
        product = create_product(body, store_id)
        
        return {
            'statusCode': STATUS_CODES['CREATED'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'product': product})
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

def handle_update_product(product_id, body):
    """Handle PUT /products/{id}"""
    try:
        # In a real app, you'd get the store_id from the JWT token or verify ownership
        store_id = "mock-store-id"
        
        # Validate that at least one field is provided
        allowed_fields = ALLOWED_UPDATE_FIELDS['PRODUCT']
        update_data = {}
        
        for field in allowed_fields:
            if field in body:
                update_data[field] = body[field]
        
        if not update_data:
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
        
        product = update_product(product_id, update_data, store_id)
        if not product:
            return {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Product not found or access denied'
                    }
                })
            }
        
        return {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'product': product})
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

def handle_delete_product(product_id):
    """Handle DELETE /products/{id}"""
    try:
        # In a real app, you'd get the store_id from the JWT token or verify ownership
        store_id = "mock-store-id"
        
        product = get_product_by_id(product_id)
        if not product or product['store_id'] != store_id:
            return {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Product not found or access denied'
                    }
                })
            }
        
        products_table.delete_item(Key={'id': product_id})
        
        return {
            'statusCode': STATUS_CODES['NO_CONTENT'],
            'headers': CORS_HEADERS,
            'body': ''
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