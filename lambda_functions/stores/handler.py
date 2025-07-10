import json
import os
import boto3
from datetime import datetime
import uuid
import logging
import sys
from decimal import Decimal
sys.path.append('..')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def convert_decimals(obj):
    """Convert Decimal types to regular numbers for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj) if obj % 1 != 0 else int(obj)
    elif isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    else:
        return obj

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
stores_table = dynamodb.Table(os.environ['STORES_TABLE'])  # type: ignore

# Get constants from environment variables
ERROR_CODES = {
    'VALIDATION_ERROR': os.environ.get('ERROR_CODES_VALIDATION_ERROR', 'VALIDATION_ERROR'),
    'UNAUTHORIZED': os.environ.get('ERROR_CODES_UNAUTHORIZED', 'UNAUTHORIZED'),
    'FORBIDDEN': os.environ.get('ERROR_CODES_FORBIDDEN', 'FORBIDDEN'),
    'NOT_FOUND': os.environ.get('ERROR_CODES_NOT_FOUND', 'NOT_FOUND'),
    'CONFLICT': os.environ.get('ERROR_CODES_CONFLICT', 'CONFLICT'),
    'UNPROCESSABLE_ENTITY': os.environ.get('ERROR_CODES_UNPROCESSABLE_ENTITY', 'UNPROCESSABLE_ENTITY'),
    'INTERNAL_ERROR': os.environ.get('ERROR_CODES_INTERNAL_ERROR', 'INTERNAL_ERROR'),
    'METHOD_NOT_ALLOWED': os.environ.get('ERROR_CODES_METHOD_NOT_ALLOWED', 'METHOD_NOT_ALLOWED')
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
    'INTERNAL_ERROR': int(os.environ.get('STATUS_CODES_INTERNAL_ERROR', '500')),
    'METHOD_NOT_ALLOWED': int(os.environ.get('STATUS_CODES_METHOD_NOT_ALLOWED', '405'))
}

CORS_HEADERS = {
    'Content-Type': os.environ.get('CORS_HEADERS_CONTENT_TYPE', 'application/json'),
    'Access-Control-Allow-Origin': os.environ.get('CORS_HEADERS_ACCESS_CONTROL_ORIGIN', '*'),
    'Access-Control-Allow-Headers': os.environ.get('CORS_HEADERS_ACCESS_CONTROL_HEADERS', 'Content-Type,Authorization'),
    'Access-Control-Allow-Methods': os.environ.get('CORS_HEADERS_ACCESS_CONTROL_METHODS', 'GET,POST,PUT,DELETE,OPTIONS')
}

INDEX_NAMES = {
    'OWNER_ID_INDEX': os.environ.get('INDEX_NAMES_OWNER_ID_INDEX', 'owner_id_index'),
    'STORE_ID_INDEX': os.environ.get('INDEX_NAMES_STORE_ID_INDEX', 'store_id_index'),
    'CATEGORY_ID_INDEX': os.environ.get('INDEX_NAMES_CATEGORY_ID_INDEX', 'category_id_index'),
    'CUSTOMER_ID_INDEX': os.environ.get('INDEX_NAMES_CUSTOMER_ID_INDEX', 'customer_id_index'),
    'STATUS_INDEX': os.environ.get('INDEX_NAMES_STATUS_INDEX', 'status_index'),
    'ORDER_ID_INDEX': os.environ.get('INDEX_NAMES_ORDER_ID_INDEX', 'order_id_index')
}

def get_stores_with_pagination(page=1, limit=10, search=None, is_open=None):
    """Get stores with pagination and filtering"""
    logger.info(f"Getting stores with filters - page: {page}, limit: {limit}, search: {search}, is_open: {is_open}")
    
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
    
    logger.info(f"Scan kwargs: {json.dumps(scan_kwargs, default=str)}")
    
    # Get all items (in a real app, you'd implement proper pagination)
    response = stores_table.scan(**scan_kwargs)
    stores = response.get('Items', [])
    
    logger.info(f"Found {len(stores)} stores before pagination")
    
    # Simple pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_stores = stores[start_idx:end_idx]
    
    result = {
        'stores': paginated_stores,
        'pagination': {
            'current_page': page,
            'total_pages': (len(stores) + limit - 1) // limit,
            'total_items': len(stores),
            'items_per_page': limit
        }
    }
    
    logger.info(f"Returning {len(paginated_stores)} stores for page {page}")
    return result

def get_store_by_id(store_id):
    """Get store by ID"""
    logger.info(f"Getting store by ID: {store_id}")
    response = stores_table.get_item(Key={'id': store_id})
    store = response.get('Item')
    logger.info(f"Store lookup result: {'Found' if store else 'Not found'}")
    return store

def create_store(store_data, owner_id):
    """Create a new store"""
    logger.info(f"Creating store for owner ID: {owner_id}")
    logger.info(f"Store data: {json.dumps(store_data, default=str)}")
    
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
    
    logger.info(f"Store item to be created: {json.dumps(store_item, default=str)}")
    stores_table.put_item(Item=store_item)
    logger.info(f"Store created successfully with ID: {store_id}")
    return store_item

def update_store(store_id, update_data, owner_id):
    """Update store details"""
    logger.info(f"Updating store ID: {store_id} for owner ID: {owner_id}")
    logger.info(f"Update data: {json.dumps(update_data, default=str)}")
    
    # First verify ownership
    store = get_store_by_id(store_id)
    if not store or store['owner_id'] != owner_id:
        logger.warning(f"Store not found or access denied for store ID: {store_id}, owner ID: {owner_id}")
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
    
    logger.info(f"Update expression: {update_expression}")
    logger.info(f"Expression values: {json.dumps(expression_values, default=str)}")
    
    response = stores_table.update_item(
        Key={'id': store_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ExpressionAttributeNames=expression_names,
        ReturnValues="ALL_NEW"
    )
    
    updated_store = response.get('Attributes')
    logger.info(f"Store updated successfully: {updated_store is not None}")
    return updated_store

def get_stores_by_owner(owner_id):
    """Get stores owned by a specific user"""
    logger.info(f"Getting stores for owner ID: {owner_id}")
    
    response = stores_table.query(
        IndexName='owner_id_index',
        KeyConditionExpression='owner_id = :owner_id',
        ExpressionAttributeValues={':owner_id': owner_id}
    )
    
    stores = response.get('Items', [])
    logger.info(f"Found {len(stores)} stores for owner {owner_id}")
    return stores

def handler(event, context):
    """Main Lambda handler for stores"""
    logger.info("=== STORES HANDLER START ===")
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
        try:
            body = json.loads(event.get('body', '{}'))
            logger.info(f"Request body: {json.dumps(body, default=str)}")
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in request body: {str(e)}")
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Invalid JSON format'
                    }
                })
            }
        
        # Route based on path and method
        # Handle both with and without stage prefix (/dev/stores or /stores)
        if (path == '/stores' or path.endswith('/stores')) and method == 'GET':
            logger.info("Routing to get stores handler")
            response = handle_get_stores(query_params)
            logger.info(f"Get stores response: {json.dumps(response, default=str)}")
            return response
        elif ('/stores/' in path) and method == 'GET':
            # Check if this is a request for owner stores
            if path.endswith('/owner') or '/stores/owner' in path:
                logger.info("Routing to get owner stores handler")
                response = handle_get_owner_stores(event)
                logger.info(f"Get owner stores response: {json.dumps(response, default=str)}")
                return response
            
            # Extract store_id from path, handling both /stores/{id} and /dev/stores/{id}
            path_parts = path.split('/')
            logger.info(f"Path parts for GET store: {path_parts}")
            
            # Find the store_id - it should be after 'stores' in the path
            try:
                stores_index = path_parts.index('stores')
                if stores_index + 1 < len(path_parts):
                    store_id = path_parts[stores_index + 1]
                    logger.info(f"Extracted store_id: {store_id}")
                    
                    response = handle_get_store(store_id)
                    logger.info(f"Get store response: {json.dumps(response, default=str)}")
                    return response
                else:
                    logger.warning("No store_id found in path")
                    return {
                        'statusCode': STATUS_CODES['BAD_REQUEST'],
                        'headers': CORS_HEADERS,
                        'body': json.dumps({
                            'error': {
                                'code': ERROR_CODES['VALIDATION_ERROR'],
                                'message': 'Store ID is required'
                            }
                        })
                    }
            except ValueError:
                logger.warning("Could not find 'stores' in path")
                return {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['VALIDATION_ERROR'],
                            'message': 'Invalid path format'
                        }
                    })
                }
        elif ('/stores/' in path) and method == 'PUT':
            # Extract store_id from path
            path_parts = path.split('/')
            logger.info(f"Path parts for PUT store: {path_parts}")
            
            try:
                stores_index = path_parts.index('stores')
                if stores_index + 1 < len(path_parts):
                    store_id = path_parts[stores_index + 1]
                    logger.info(f"Extracted store_id for update: {store_id}")
                    
                    response = handle_update_store(event, store_id, body)
                    logger.info(f"Update store response: {json.dumps(response, default=str)}")
                    return response
                else:
                    logger.warning("No store_id found in path for update")
                    return {
                        'statusCode': STATUS_CODES['BAD_REQUEST'],
                        'headers': CORS_HEADERS,
                        'body': json.dumps({
                            'error': {
                                'code': ERROR_CODES['VALIDATION_ERROR'],
                                'message': 'Store ID is required'
                            }
                        })
                    }
            except ValueError:
                logger.warning("Could not find 'stores' in path for update")
                return {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['VALIDATION_ERROR'],
                            'message': 'Invalid path format'
                        }
                    })
                }
        elif ('/stores/' in path) and method == 'DELETE':
            # Extract store_id from path
            path_parts = path.split('/')
            logger.info(f"Path parts for DELETE store: {path_parts}")
            
            try:
                stores_index = path_parts.index('stores')
                if stores_index + 1 < len(path_parts):
                    store_id = path_parts[stores_index + 1]
                    logger.info(f"Extracted store_id for delete: {store_id}")
                    
                    response = handle_delete_store(event, store_id)
                    logger.info(f"Delete store response: {json.dumps(response, default=str)}")
                    return response
                else:
                    logger.warning("No store_id found in path for delete")
                    return {
                        'statusCode': STATUS_CODES['BAD_REQUEST'],
                        'headers': CORS_HEADERS,
                        'body': json.dumps({
                            'error': {
                                'code': ERROR_CODES['VALIDATION_ERROR'],
                                'message': 'Store ID is required'
                            }
                        })
                    }
            except ValueError:
                logger.warning("Could not find 'stores' in path for delete")
                return {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['VALIDATION_ERROR'],
                            'message': 'Invalid path format'
                        }
                    })
                }
        elif (path == '/stores' or path.endswith('/stores')) and method == 'POST':
            logger.info("Routing to create store handler")
            response = handle_create_store(event, body)
            logger.info(f"Create store response: {json.dumps(response, default=str)}")
            return response
        elif method == 'OPTIONS':
            # Handle CORS preflight requests
            logger.info("Handling CORS preflight request")
            response = {
                'statusCode': 200,
                'headers': CORS_HEADERS,
                'body': ''
            }
            logger.info(f"CORS response: {json.dumps(response, default=str)}")
            return response
        else:
            # Handle method not allowed for collection endpoints
            if (path == '/stores' or path.endswith('/stores')) and method in ['PUT', 'DELETE']:
                logger.warning(f"Method not allowed: {method} {path}")
                return {
                    'statusCode': STATUS_CODES['METHOD_NOT_ALLOWED'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['METHOD_NOT_ALLOWED'],
                            'message': f'Method {method} not allowed for this endpoint'
                        }
                    })
                }
            
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
        logger.info("=== STORES HANDLER END ===")

def handle_get_stores(query_params):
    """Handle GET /stores"""
    logger.info("=== GET STORES HANDLER START ===")
    try:
        page = int(query_params.get('page', 1))
        limit = int(query_params.get('limit', 10))
        search = query_params.get('search')
        is_open = query_params.get('is_open')
        
        logger.info(f"Getting stores with filters - page: {page}, limit: {limit}, search: {search}, is_open: {is_open}")
        
        result = get_stores_with_pagination(page, limit, search, is_open)
        
        # Convert Decimal types for JSON serialization
        result = convert_decimals(result)
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps(result)
        }
        
        logger.info("=== GET STORES HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Get stores error: {str(e)}", exc_info=True)
        logger.info("=== GET STORES HANDLER END ===")
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

def handle_get_store(store_id):
    """Handle GET /stores/{id}"""
    logger.info("=== GET STORE HANDLER START ===")
    try:
        logger.info(f"Getting store with ID: {store_id}")
        
        store = get_store_by_id(store_id)
        if not store:
            logger.warning(f"Store not found with ID: {store_id}")
            response = {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Store not found'
                    }
                })
            }
            logger.info("=== GET STORE HANDLER END ===")
            return response
        
        # Convert Decimal types for JSON serialization
        store = convert_decimals(store)
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps(store)
        }
        
        logger.info("=== GET STORE HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Get store error: {str(e)}", exc_info=True)
        logger.info("=== GET STORE HANDLER END ===")
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

def handle_create_store(event, body):
    """Handle POST /stores"""
    logger.info("=== CREATE STORE HANDLER START ===")
    try:
        logger.info(f"Creating store with data: {json.dumps(body, default=str)}")
        
        # For now, use a mock owner ID - security will be implemented later
        owner_id = 'mock-owner-id'
        logger.info(f"Creating store for owner ID: {owner_id}")
        
        # Validate required fields
        required_fields = ['name', 'address']
        for field in required_fields:
            if not body.get(field):
                logger.warning(f"Missing required field: {field}")
                response = {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['VALIDATION_ERROR'],
                            'message': f'Missing required field: {field}'
                        }
                    })
                }
                logger.info("=== CREATE STORE HANDLER END ===")
                return response
        
        logger.info("All required fields present")
        
        store = create_store(body, owner_id)
        
        # Convert Decimal types for JSON serialization
        store = convert_decimals(store)
        
        response = {
            'statusCode': STATUS_CODES['CREATED'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'store': store})
        }
        
        logger.info("=== CREATE STORE HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Create store error: {str(e)}", exc_info=True)
        logger.info("=== CREATE STORE HANDLER END ===")
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

def handle_update_store(event, store_id, body):
    """Handle PUT /stores/{id}"""
    logger.info("=== UPDATE STORE HANDLER START ===")
    try:
        # For now, use a mock owner ID - security will be implemented later
        owner_id = 'mock-owner-id'
        logger.info(f"Updating store ID: {store_id} for owner ID: {owner_id}")
        logger.info(f"Update data: {json.dumps(body, default=str)}")
        
        # Validate that at least one field is provided
        allowed_fields = ['name', 'address', 'phone', 'is_open', 'delivery_time']
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
            logger.info("=== UPDATE STORE HANDLER END ===")
            return response
        
        store = update_store(store_id, update_data, owner_id)
        if not store:
            logger.warning(f"Store not found or access denied for ID: {store_id}")
            response = {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Store not found or access denied'
                    }
                })
            }
            logger.info("=== UPDATE STORE HANDLER END ===")
            return response
        
        # Convert Decimal types for JSON serialization
        store = convert_decimals(store)
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'store': store})
        }
        
        logger.info("=== UPDATE STORE HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Update store error: {str(e)}", exc_info=True)
        logger.info("=== UPDATE STORE HANDLER END ===")
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

def handle_delete_store(event, store_id):
    """Handle DELETE /stores/{id}"""
    logger.info("=== DELETE STORE HANDLER START ===")
    try:
        # For now, use a mock owner ID - security will be implemented later
        owner_id = 'mock-owner-id'
        logger.info(f"Deleting store ID: {store_id} for owner ID: {owner_id}")
        
        store = get_store_by_id(store_id)
        if not store or store['owner_id'] != owner_id:
            logger.warning(f"Store not found or access denied for ID: {store_id}")
            response = {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Store not found or access denied'
                    }
                })
            }
            logger.info("=== DELETE STORE HANDLER END ===")
            return response
        
        stores_table.delete_item(Key={'id': store_id})
        logger.info(f"Store deleted successfully: {store_id}")
        
        response = {
            'statusCode': STATUS_CODES['NO_CONTENT'],
            'headers': CORS_HEADERS,
            'body': ''
        }
        
        logger.info("=== DELETE STORE HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Delete store error: {str(e)}", exc_info=True)
        logger.info("=== DELETE STORE HANDLER END ===")
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

def handle_get_owner_stores(event):
    """Handle GET /stores/owner"""
    logger.info("=== GET OWNER STORES HANDLER START ===")
    try:
        # For now, use a mock owner ID - security will be implemented later
        owner_id = 'mock-owner-id'
        logger.info(f"Getting stores for owner ID: {owner_id}")
        
        stores = get_stores_by_owner(owner_id)
        
        # Convert Decimal types for JSON serialization
        stores = convert_decimals(stores)
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'stores': stores})
        }
        
        logger.info("=== GET OWNER STORES HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Get owner stores error: {str(e)}", exc_info=True)
        logger.info("=== GET OWNER STORES HANDLER END ===")
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