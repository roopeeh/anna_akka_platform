import json
import os
import boto3
from datetime import datetime
import uuid
import logging
from decimal import Decimal

def decimal_default(obj):
    """Convert Decimal objects to strings for JSON serialization"""
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
available_products_table = dynamodb.Table(os.environ['AVAILABLE_PRODUCTS_TABLE'])  # type: ignore

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

INDEX_NAMES = {
    'CATEGORY_ID_INDEX': os.environ.get('INDEX_NAMES_CATEGORY_ID_INDEX', 'category_id_index'),
}

ALLOWED_UPDATE_FIELDS = {
    'AVAILABLE_PRODUCT': ['name', 'description', 'price', 'unit', 'image_url', 'category_id']
}

def get_available_products_with_pagination(page=1, limit=20, category_id=None, search=None, min_price=None, max_price=None):
    """Get available products with pagination and filtering"""
    logger.info(f"Getting available products with filters - page: {page}, limit: {limit}, category_id: {category_id}, search: {search}, min_price: {min_price}, max_price: {max_price}")
    
    scan_kwargs = {}
    
    # Add filters
    filter_expressions = []
    expression_values = {}
    expression_names = {}
    
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
    
    if filter_expressions:
        scan_kwargs['FilterExpression'] = ' AND '.join(filter_expressions)
        scan_kwargs['ExpressionAttributeValues'] = expression_values
        scan_kwargs['ExpressionAttributeNames'] = expression_names
    
    logger.info(f"Scan kwargs: {json.dumps(scan_kwargs, default=str)}")
    
    # Get all items (in a real app, you'd implement proper pagination)
    response = available_products_table.scan(**scan_kwargs)
    products = response.get('Items', [])
    
    logger.info(f"Found {len(products)} available products before pagination")
    
    # Simple pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_products = products[start_idx:end_idx]
    
    result = {
        'products': paginated_products,
        'pagination': {
            'current_page': page,
            'total_pages': (len(products) + limit - 1) // limit,
            'total_items': len(products),
            'items_per_page': limit
        }
    }
    
    logger.info(f"Returning {len(paginated_products)} available products for page {page}")
    return result

def get_available_product_by_id(product_id):
    """Get available product by ID"""
    logger.info(f"Getting available product by ID: {product_id}")
    response = available_products_table.get_item(Key={'id': product_id})
    product = response.get('Item')
    logger.info(f"Available product lookup result: {'Found' if product else 'Not found'}")
    return product

def create_available_product(product_data):
    """Create a new available product"""
    logger.info(f"Creating available product")
    logger.info(f"Product data: {json.dumps(product_data, default=str)}")
    
    product_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    product_item = {
        'id': product_id,
        'category_id': product_data.get('category_id'),
        'name': product_data['name'],
        'description': product_data.get('description'),
        'price': Decimal(str(product_data['price'])),
        'unit': product_data.get('unit', 'piece'),
        'image_url': product_data.get('image_url'),
        'created_at': timestamp,
        'updated_at': timestamp
    }
    
    logger.info(f"Available product item to be created: {json.dumps(product_item, default=str)}")
    available_products_table.put_item(Item=product_item)
    logger.info(f"Available product created successfully with ID: {product_id}")
    return product_item

def update_available_product(product_id, update_data):
    """Update available product details"""
    logger.info(f"Updating available product ID: {product_id}")
    logger.info(f"Update data: {json.dumps(update_data, default=str)}")
    
    # Prepare update expression
    update_expression = "SET "
    expression_values = {}
    expression_names = {}
    
    for key, value in update_data.items():
        if key in ['name', 'description', 'price', 'unit', 'image_url', 'category_id']:
            update_expression += f"#{key} = :{key}, "
            # Convert price to Decimal if it's a price field
            if key == 'price':
                expression_values[f':{key}'] = Decimal(str(value))
            else:
                expression_values[f':{key}'] = value
            expression_names[f'#{key}'] = key
    
    update_expression += "#updated_at = :updated_at"
    expression_values[':updated_at'] = datetime.utcnow().isoformat()
    expression_names['#updated_at'] = 'updated_at'
    
    logger.info(f"Update expression: {update_expression}")
    logger.info(f"Expression values: {json.dumps(expression_values, default=str)}")
    
    response = available_products_table.update_item(
        Key={'id': product_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ExpressionAttributeNames=expression_names,
        ReturnValues="ALL_NEW"
    )
    
    updated_product = response.get('Attributes')
    logger.info(f"Available product updated successfully: {updated_product is not None}")
    return updated_product

def handler(event, context):
    """Main Lambda handler for available products"""
    logger.info("=== AVAILABLE PRODUCTS HANDLER START ===")
    logger.info(f"Event: {json.dumps(event, default=str)}")
    logger.info(f"Context: {json.dumps({'function_name': context.function_name, 'function_version': context.function_version, 'invoked_function_arn': context.invoked_function_arn, 'memory_limit_in_mb': context.memory_limit_in_mb, 'remaining_time_in_millis': context.get_remaining_time_in_millis()}, default=str)}")
    
    try:
        # Parse the request
        path = event.get('requestContext', {}).get('http', {}).get('path', '')
        method = event.get('requestContext', {}).get('http', {}).get('method', '')
        
        logger.info(f"Request path: {path}")
        logger.info(f"Request method: {method}")
        
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        logger.info(f"Query parameters: {json.dumps(query_params, default=str)}")
        
        # Parse body
        body = json.loads(event.get('body', '{}'))
        logger.info(f"Request body: {json.dumps(body, default=str)}")
        
        # Route based on path and method
        # Handle both with and without stage prefix (/dev/available-products or /available-products)
        if (path == '/available-products' or path.endswith('/available-products')) and method == 'GET':
            logger.info("Routing to get available products handler")
            response = handle_get_available_products(query_params)
            logger.info(f"Get available products response: {json.dumps(response, default=str)}")
            return response
        elif ('/available-products/' in path and method == 'GET'):
            # Extract product_id after the last '/available-products/'
            product_id = path.split('/available-products/')[-1].split('/')[0]
            logger.info(f"Routing to get available product handler for ID: {product_id}")
            response = handle_get_available_product(product_id)
            logger.info(f"Get available product response: {json.dumps(response, default=str)}")
            return response
        elif (path == '/available-products' or path.endswith('/available-products')) and method == 'POST':
            logger.info("Routing to create available product handler")
            response = handle_create_available_product(body)
            logger.info(f"Create available product response: {json.dumps(response, default=str)}")
            return response
        elif ('/available-products/' in path and method == 'PUT'):
            product_id = path.split('/available-products/')[-1].split('/')[0]
            logger.info(f"Routing to update available product handler for ID: {product_id}")
            response = handle_update_available_product(product_id, body)
            logger.info(f"Update available product response: {json.dumps(response, default=str)}")
            return response
        elif ('/available-products/' in path and method == 'DELETE'):
            product_id = path.split('/available-products/')[-1].split('/')[0]
            logger.info(f"Routing to delete available product handler for ID: {product_id}")
            response = handle_delete_available_product(product_id)
            logger.info(f"Delete available product response: {json.dumps(response, default=str)}")
            return response
        else:
            logger.warning(f"Endpoint not found: {method} {path}")
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
        logger.info("=== AVAILABLE PRODUCTS HANDLER END ===")

def handle_get_available_products(query_params):
    """Handle GET /available-products"""
    logger.info("=== GET AVAILABLE PRODUCTS HANDLER START ===")
    try:
        page = int(query_params.get('page', 1))
        limit = int(query_params.get('limit', 20))
        category_id = query_params.get('category_id')
        search = query_params.get('search')
        min_price = Decimal(str(query_params.get('min_price'))) if query_params.get('min_price') else None
        max_price = Decimal(str(query_params.get('max_price'))) if query_params.get('max_price') else None
        
        logger.info(f"Getting available products with filters - page: {page}, limit: {limit}, category_id: {category_id}, search: {search}, min_price: {min_price}, max_price: {max_price}")
        
        result = get_available_products_with_pagination(
            page, limit, category_id, search, min_price, max_price
        )
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps(result, default=decimal_default)
        }
        
        logger.info("=== GET AVAILABLE PRODUCTS HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Get available products error: {str(e)}", exc_info=True)
        logger.info("=== GET AVAILABLE PRODUCTS HANDLER END ===")
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

def handle_get_available_product(product_id):
    """Handle GET /available-products/{id}"""
    logger.info("=== GET AVAILABLE PRODUCT HANDLER START ===")
    try:
        logger.info(f"Getting available product with ID: {product_id}")
        
        product = get_available_product_by_id(product_id)
        if not product:
            logger.warning(f"Available product not found with ID: {product_id}")
            response = {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Available product not found'
                    }
                })
            }
            logger.info("=== GET AVAILABLE PRODUCT HANDLER END ===")
            return response
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'product': product}, default=decimal_default)
        }
        
        logger.info("=== GET AVAILABLE PRODUCT HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Get available product error: {str(e)}", exc_info=True)
        logger.info("=== GET AVAILABLE PRODUCT HANDLER END ===")
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

def handle_create_available_product(body):
    """Handle POST /available-products"""
    logger.info("=== CREATE AVAILABLE PRODUCT HANDLER START ===")
    try:
        logger.info(f"Creating available product")
        logger.info(f"Product data: {json.dumps(body, default=str)}")
        
        # Validate required fields
        if not body.get('name') or not body.get('price'):
            logger.warning("Missing required fields: name or price")
            response = {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Name and price are required'
                    }
                })
            }
            logger.info("=== CREATE AVAILABLE PRODUCT HANDLER END ===")
            return response
        
        product = create_available_product(body)
        
        response = {
            'statusCode': STATUS_CODES['CREATED'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'product': product}, default=decimal_default)
        }
        
        logger.info("=== CREATE AVAILABLE PRODUCT HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Create available product error: {str(e)}", exc_info=True)
        logger.info("=== CREATE AVAILABLE PRODUCT HANDLER END ===")
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

def handle_update_available_product(product_id, body):
    """Handle PUT /available-products/{id}"""
    logger.info("=== UPDATE AVAILABLE PRODUCT HANDLER START ===")
    try:
        logger.info(f"Updating available product ID: {product_id}")
        logger.info(f"Update data: {json.dumps(body, default=str)}")
        
        # Validate that at least one field is provided
        allowed_fields = ALLOWED_UPDATE_FIELDS['AVAILABLE_PRODUCT']
        update_data = {}
        
        for field in allowed_fields:
            if field in body:
                update_data[field] = body[field]
        
        logger.info(f"Fields to update: {list(update_data.keys())}")
        
        if not update_data:
            logger.warning("No valid fields provided for update")
            response = {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'At least one field must be provided for update'
                    }
                })
            }
            logger.info("=== UPDATE AVAILABLE PRODUCT HANDLER END ===")
            return response
        
        product = update_available_product(product_id, update_data)
        if not product:
            logger.warning(f"Available product not found for ID: {product_id}")
            response = {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Available product not found'
                    }
                })
            }
            logger.info("=== UPDATE AVAILABLE PRODUCT HANDLER END ===")
            return response
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'product': product}, default=decimal_default)
        }
        
        logger.info("=== UPDATE AVAILABLE PRODUCT HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Update available product error: {str(e)}", exc_info=True)
        logger.info("=== UPDATE AVAILABLE PRODUCT HANDLER END ===")
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

def handle_delete_available_product(product_id):
    """Handle DELETE /available-products/{id}"""
    logger.info("=== DELETE AVAILABLE PRODUCT HANDLER START ===")
    try:
        logger.info(f"Deleting available product ID: {product_id}")
        
        product = get_available_product_by_id(product_id)
        if not product:
            logger.warning(f"Available product not found for ID: {product_id}")
            response = {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Available product not found'
                    }
                })
            }
            logger.info("=== DELETE AVAILABLE PRODUCT HANDLER END ===")
            return response
        
        available_products_table.delete_item(Key={'id': product_id})
        logger.info(f"Available product deleted successfully: {product_id}")
        
        response = {
            'statusCode': STATUS_CODES['NO_CONTENT'],
            'headers': CORS_HEADERS,
            'body': ''
        }
        
        logger.info("=== DELETE AVAILABLE PRODUCT HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Delete available product error: {str(e)}", exc_info=True)
        logger.info("=== DELETE AVAILABLE PRODUCT HANDLER END ===")
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