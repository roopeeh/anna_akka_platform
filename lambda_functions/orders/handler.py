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

def extract_user_id_from_request(event):
    """Extract user ID from request context or headers"""
    try:
        # Try to get user ID from request context (API Gateway authorizer)
        request_context = event.get('requestContext', {})
        authorizer = request_context.get('authorizer', {})
        
        # Check for user ID in authorizer claims
        if authorizer:
            user_id = authorizer.get('claims', {}).get('sub') or authorizer.get('user_id')
            if user_id:
                logger.info(f"Extracted user ID from authorizer: {user_id}")
                return user_id
        
        # Check for user ID in headers
        headers = event.get('headers', {}) or {}
        user_id = headers.get('X-User-ID') or headers.get('x-user-id')
        if user_id:
            logger.info(f"Extracted user ID from headers: {user_id}")
            return user_id
        
        # For development/testing, check for user ID in query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        user_id = query_params.get('user_id')
        if user_id:
            logger.info(f"Extracted user ID from query params: {user_id}")
            return user_id
        
        logger.warning("No user ID found in request context, headers, or query parameters")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting user ID: {str(e)}")
        return None

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
orders_table = dynamodb.Table(os.environ['ORDERS_TABLE'])  # type: ignore
cart_table = dynamodb.Table(os.environ['CART_TABLE'])  # type: ignore

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
    'INTERNAL_ERROR': int(os.environ.get('STATUS_CODES_INTERNAL_ERROR', '500')),
    'METHOD_NOT_ALLOWED': int(os.environ.get('STATUS_CODES_METHOD_NOT_ALLOWED', '405'))
}

CORS_HEADERS = {
    'Content-Type': os.environ.get('CORS_HEADERS_CONTENT_TYPE', 'application/json'),
    'Access-Control-Allow-Origin': os.environ.get('CORS_HEADERS_ACCESS_CONTROL_ORIGIN', '*'),
    'Access-Control-Allow-Headers': os.environ.get('CORS_HEADERS_ACCESS_CONTROL_HEADERS', 'Content-Type,Authorization'),
    'Access-Control-Allow-Methods': os.environ.get('CORS_HEADERS_ACCESS_CONTROL_METHODS', 'GET,POST,PUT,DELETE,OPTIONS')
}

ORDER_STATUS = {
    'PENDING': os.environ.get('ORDER_STATUS_PENDING', 'pending'),
    'PREPARING': os.environ.get('ORDER_STATUS_PREPARING', 'preparing'),
    'READY': os.environ.get('ORDER_STATUS_READY', 'ready'),
    'DELIVERED': os.environ.get('ORDER_STATUS_DELIVERED', 'delivered'),
    'CANCELLED': os.environ.get('ORDER_STATUS_CANCELLED', 'cancelled')
}

INDEX_NAMES = {
    'OWNER_ID_INDEX': os.environ.get('INDEX_NAMES_OWNER_ID_INDEX', 'owner_id_index'),
    'STORE_ID_INDEX': os.environ.get('INDEX_NAMES_STORE_ID_INDEX', 'store_id_index'),
    'CATEGORY_ID_INDEX': os.environ.get('INDEX_NAMES_CATEGORY_ID_INDEX', 'category_id_index'),
    'CUSTOMER_ID_INDEX': os.environ.get('INDEX_NAMES_CUSTOMER_ID_INDEX', 'customer_id_index'),
    'STATUS_INDEX': os.environ.get('INDEX_NAMES_STATUS_INDEX', 'status_index'),
    'ORDER_ID_INDEX': os.environ.get('INDEX_NAMES_ORDER_ID_INDEX', 'order_id_index')
}

def create_order(order_data, customer_id):
    """Create a new order"""
    logger.info(f"Creating order for customer ID: {customer_id}")
    logger.info(f"Order data: {json.dumps(order_data, default=str)}")
    
    order_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    order_item = {
        'id': order_id,
        'customer_id': customer_id,
        'store_id': order_data['store_id'],
        'delivery_address': order_data['delivery_address'],
        'status': ORDER_STATUS['PENDING'],
        'total_amount': order_data.get('total_amount', 0),
        'products': order_data.get('products', []),  # Store complete product information
        'created_at': timestamp,
        'updated_at': timestamp
    }
    
    logger.info(f"Order item to be created: {json.dumps(order_item, default=str)}")
    orders_table.put_item(Item=order_item)
    logger.info(f"Order created successfully with ID: {order_id}")
    return order_item

def get_order_by_id(order_id):
    """Get order by ID"""
    logger.info(f"Getting order by ID: {order_id}")
    response = orders_table.get_item(Key={'id': order_id})
    order = response.get('Item')
    logger.info(f"Order lookup result: {'Found' if order else 'Not found'}")
    return order

def get_orders_by_customer(customer_id, page=1, limit=10):
    """Get orders for a specific customer"""
    logger.info(f"Getting orders for customer ID: {customer_id}, page: {page}, limit: {limit}")
    
    query_kwargs = {
        'IndexName': INDEX_NAMES['CUSTOMER_ID_INDEX'],
        'KeyConditionExpression': 'customer_id = :customer_id',
        'ExpressionAttributeValues': {':customer_id': customer_id}
    }
    
    logger.info(f"Query kwargs: {json.dumps(query_kwargs, default=str)}")
    
    response = orders_table.query(**query_kwargs)
    orders = response.get('Items', [])
    
    logger.info(f"Found {len(orders)} orders for customer {customer_id}")
    
    # Simple pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_orders = orders[start_idx:end_idx]
    
    result = {
        'orders': paginated_orders,
        'pagination': {
            'current_page': page,
            'total_pages': (len(orders) + limit - 1) // limit,
            'total_items': len(orders),
            'items_per_page': limit
        }
    }
    
    logger.info(f"Returning {len(paginated_orders)} orders for page {page}")
    return result

def get_orders_by_store(store_id, page=1, limit=10):
    """Get orders for a specific store"""
    logger.info(f"Getting orders for store ID: {store_id}, page: {page}, limit: {limit}")
    
    query_kwargs = {
        'IndexName': INDEX_NAMES['STORE_ID_INDEX'],
        'KeyConditionExpression': 'store_id = :store_id',
        'ExpressionAttributeValues': {':store_id': store_id}
    }
    
    logger.info(f"Query kwargs: {json.dumps(query_kwargs, default=str)}")
    
    response = orders_table.query(**query_kwargs)
    orders = response.get('Items', [])
    
    logger.info(f"Found {len(orders)} orders for store {store_id}")
    
    # Simple pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_orders = orders[start_idx:end_idx]
    
    result = {
        'orders': paginated_orders,
        'pagination': {
            'current_page': page,
            'total_pages': (len(orders) + limit - 1) // limit,
            'total_items': len(orders),
            'items_per_page': limit
        }
    }
    
    logger.info(f"Returning {len(paginated_orders)} orders for page {page}")
    return result

def update_order_status(order_id, status, customer_id):
    """Update order status"""
    logger.info(f"Updating order status for order ID: {order_id}, status: {status}, customer ID: {customer_id}")
    
    # First verify ownership
    order = get_order_by_id(order_id)
    if not order or order['customer_id'] != customer_id:
        logger.warning(f"Order not found or access denied for order ID: {order_id}, customer ID: {customer_id}")
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
    
    updated_order = response.get('Attributes')
    logger.info(f"Order status updated successfully: {updated_order is not None}")
    return updated_order

def get_cart_items(customer_id, store_id):
    """Get cart items for a specific store"""
    logger.info(f"Getting cart items for customer: {customer_id}, store: {store_id}")
    
    try:
        response = cart_table.query(
            KeyConditionExpression='customer_id = :customer_id',
            FilterExpression='store_id = :store_id',
            ExpressionAttributeValues={
                ':customer_id': customer_id,
                ':store_id': store_id
            }
        )
        
        cart_items = response.get('Items', [])
        logger.info(f"Found {len(cart_items)} cart items for store {store_id}")
        return cart_items
    except Exception as e:
        logger.error(f"Error getting cart items: {str(e)}")
        raise e

def create_order_from_cart(customer_id, store_id, delivery_address, notes=None):
    """Create order from cart items"""
    logger.info(f"Creating order from cart for customer: {customer_id}, store: {store_id}")
    
    # Get cart items for the store
    cart_items = get_cart_items(customer_id, store_id)
    
    if not cart_items:
        raise ValueError("No items in cart for this store")
    
    # Calculate total amount and prepare product information
    total_amount = 0
    order_items = []
    products_info = []
    
    for item in cart_items:
        product_id = item.get('product_id')
        quantity = item.get('quantity', 0)
        price = item.get('price', 0)
        product_name = item.get('product_name', '')
        unit = item.get('unit', 'piece')
        special_notes = item.get('special_notes', '')
        
        total_amount += price * quantity
        
        # Prepare order item for order_items table
        order_items.append({
            'product_id': product_id,
            'quantity': quantity,
            'price': price,
            'product_name': product_name,
            'unit': unit,
            'special_notes': special_notes
        })
        
        # Prepare product info for order table
        products_info.append({
            'product_id': product_id,
            'product_name': product_name,
            'quantity': quantity,
            'price': price,
            'unit': unit,
            'special_notes': special_notes,
            'total': price * quantity
        })
    
    # Create order
    order_data = {
        'store_id': store_id,
        'delivery_address': delivery_address,
        'total_amount': total_amount,
        'products': products_info,  # Store complete product information
        'notes': notes
    }
    
    order = create_order(order_data, customer_id)
    
    # Clear cart items for this store
    clear_cart_items_for_store(customer_id, store_id)
    
    return {
        'order': order,
        'total_amount': total_amount
    }



def clear_cart_items_for_store(customer_id, store_id):
    """Clear cart items for a specific store"""
    logger.info(f"Clearing cart items for customer: {customer_id}, store: {store_id}")
    
    try:
        # Get cart items for the store
        response = cart_table.query(
            KeyConditionExpression='customer_id = :customer_id',
            FilterExpression='store_id = :store_id',
            ExpressionAttributeValues={
                ':customer_id': customer_id,
                ':store_id': store_id
            }
        )
        
        cart_items = response.get('Items', [])
        
        # Delete all items for this store
        with cart_table.batch_writer() as batch:
            for item in cart_items:
                batch.delete_item(
                    Key={
                        'customer_id': customer_id,
                        'product_id': item['product_id']
                    }
                )
        
        logger.info(f"Cleared {len(cart_items)} cart items for store {store_id}")
    except Exception as e:
        logger.error(f"Error clearing cart items: {str(e)}")
        raise e

def handler(event, context):
    """Main Lambda handler for orders"""
    logger.info("=== ORDERS HANDLER START ===")
    logger.info(f"Event: {json.dumps(event, default=str)}")
    logger.info(f"Context: {json.dumps({'function_name': context.function_name, 'function_version': context.function_version, 'invoked_function_arn': context.invoked_function_arn, 'memory_limit_in_mb': context.memory_limit_in_mb, 'remaining_time_in_millis': context.get_remaining_time_in_millis()}, default=str)}")
    
    try:
        # Parse the request
        path = event.get('requestContext', {}).get('http', {}).get('path', '')
        method = event.get('requestContext', {}).get('http', {}).get('method', '')
        
        logger.info(f"Request path: {path}")
        logger.info(f"Request method: {method}")
        logger.info(f"Path parts: {path.split('/')}")
        logger.info(f"Path ends with /status: {path.endswith('/status')}")
        logger.info(f"Path starts with /orders/: {path.startswith('/orders/')}")
        logger.info(f"Path ends with /orders/: {path.endswith('/orders/')}")
        logger.info(f"Full event structure: {json.dumps(event, default=str)}")
        
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        logger.info(f"Query parameters: {json.dumps(query_params, default=str)}")
        
        # Parse body
        try:
            body = json.loads(event.get('body', '{}'))
            logger.info(f"Request body: {json.dumps(body, default=str)}")
        except json.JSONDecodeError as e:
            logger.warning(f"Malformed JSON in request body: {str(e)}")
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Malformed JSON in request body'
                    }
                })
            }
        
        # Route based on path and method
        # Handle both with and without stage prefix (/dev/orders or /orders)
        if (path == '/orders' or path.endswith('/orders')) and method == 'GET':
            # Check if this is a store orders request
            store_id = query_params.get('store_id')
            if store_id:
                logger.info("Routing to get store orders handler")
                response = handle_get_store_orders(event, query_params)
                logger.info(f"Get store orders response: {json.dumps(response, default=str)}")
                return response
            else:
                logger.info("Routing to get orders handler")
                response = handle_get_orders(event, query_params)
                logger.info(f"Get orders response: {json.dumps(response, default=str)}")
                return response
        elif ('/orders/' in path) and method == 'GET':
            # Extract order_id from path, handling both /orders/{id} and /dev/orders/{id}
            path_parts = path.split('/')
            logger.info(f"Path parts for GET: {path_parts}")
            
            # Handle /orders/{id} and /orders/{id}/status
            if len(path_parts) >= 3:
                # Try to find the order_id - it should be after 'orders' in the path
                order_id = None
                for i, part in enumerate(path_parts):
                    if part == 'orders' and i + 1 < len(path_parts):
                        order_id = path_parts[i + 1]
                        break
                
                if order_id:
                    logger.info(f"Extracted order_id: {order_id}")
                    logger.info(f"Routing to get order handler for ID: {order_id}")
                    response = handle_get_order(event, order_id)
                    logger.info(f"Get order response: {json.dumps(response, default=str)}")
                    return response
                else:
                    logger.warning(f"No order_id found in path: {path}")
                    return {
                        'statusCode': STATUS_CODES['NOT_FOUND'],
                        'headers': CORS_HEADERS,
                        'body': json.dumps({
                            'error': {
                                'code': ERROR_CODES['NOT_FOUND'],
                                'message': 'Order ID not found in path'
                            }
                        })
                    }
            else:
                logger.warning(f"Invalid path for GET order: {path}")
                return {
                    'statusCode': STATUS_CODES['NOT_FOUND'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['NOT_FOUND'],
                            'message': 'Invalid order path'
                        }
                    })
                }
        elif (path == '/orders' or path.endswith('/orders')) and method == 'POST':
            logger.info("Routing to create order handler")
            response = handle_create_order(event, body)
            logger.info(f"Create order response: {json.dumps(response, default=str)}")
            return response
        elif ('/orders/' in path) and method == 'PUT':
            # Handle PUT requests to /orders/{id} or /orders/{id}/status
            path_parts = path.split('/')
            logger.info(f"Path parts for PUT: {path_parts}")
            
            if len(path_parts) >= 3:
                # Try to find the order_id - it should be after 'orders' in the path
                order_id = None
                for i, part in enumerate(path_parts):
                    if part == 'orders' and i + 1 < len(path_parts):
                        order_id = path_parts[i + 1]
                        break
                
                if order_id:
                    logger.info(f"Extracted order_id: {order_id}")
                    
                    if path.endswith('/status'):
                        # Update order status: /orders/{id}/status
                        logger.info(f"Routing to update order status handler for ID: {order_id}")
                        response = handle_update_order_status(event, order_id, body)
                        logger.info(f"Update order status response: {json.dumps(response, default=str)}")
                        return response
                    else:
                        # Update order: /orders/{id}
                        logger.info(f"Routing to update order handler for ID: {order_id}")
                        # For now, return not implemented
                        response = {
                            'statusCode': STATUS_CODES['METHOD_NOT_ALLOWED'],
                            'headers': CORS_HEADERS,
                            'body': json.dumps({
                                'error': {
                                    'code': ERROR_CODES['VALIDATION_ERROR'],
                                    'message': 'Order update not implemented yet'
                                }
                            })
                        }
                        logger.info(f"Update order response: {json.dumps(response, default=str)}")
                        return response
                else:
                    logger.warning(f"No order_id found in path: {path}")
                    return {
                        'statusCode': STATUS_CODES['NOT_FOUND'],
                        'headers': CORS_HEADERS,
                        'body': json.dumps({
                            'error': {
                                'code': ERROR_CODES['NOT_FOUND'],
                                'message': 'Order ID not found in path'
                            }
                        })
                    }
            else:
                logger.warning(f"Invalid path for PUT order: {path}")
                return {
                    'statusCode': STATUS_CODES['NOT_FOUND'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['NOT_FOUND'],
                            'message': 'Invalid order path'
                        }
                    })
                }
        elif (path == '/orders' or path.endswith('/orders')) and method in ['PUT', 'DELETE']:
            # Method not allowed for collection endpoint
            logger.warning(f"Method not allowed: {method} for /orders")
            response = {
                'statusCode': STATUS_CODES['METHOD_NOT_ALLOWED'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': f'Method {method} not allowed for this endpoint'
                    }
                })
            }
            logger.info(f"Method not allowed response: {json.dumps(response, default=str)}")
            return response
        elif method == 'OPTIONS':
            # Handle CORS preflight requests
            logger.info("Handling CORS preflight request")
            response = {
                'statusCode': STATUS_CODES['OK'],
                'headers': CORS_HEADERS,
                'body': ''
            }
            logger.info(f"CORS response: {json.dumps(response, default=str)}")
            return response
        else:
            logger.warning(f"Endpoint not found: {method} {path}")
            logger.warning(f"Path starts with /orders/: {path.startswith('/orders/')}")
            logger.warning(f"Path ends with /orders/: {path.endswith('/orders/')}")
            logger.warning(f"Path contains /orders/: {'/orders/' in path}")
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
        logger.info("=== ORDERS HANDLER END ===")

def handle_get_store_orders(event, query_params):
    """Handle GET /orders?store_id={store_id}"""
    logger.info("=== GET STORE ORDERS HANDLER START ===")
    try:
        # Extract user ID from request
        customer_id = extract_user_id_from_request(event)
        if not customer_id:
            logger.warning("User ID not found in request, cannot get store orders.")
            return {
                'statusCode': STATUS_CODES['UNAUTHORIZED'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['UNAUTHORIZED'],
                        'message': 'User not authenticated'
                    }
                })
            }
        
        store_id = query_params.get('store_id')
        if not store_id:
            logger.warning("Store ID not provided in query parameters")
            return {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'store_id is required'
                    }
                })
            }
        
        logger.info(f"Getting orders for store ID: {store_id}")
        
        page = int(query_params.get('page', 1))
        limit = int(query_params.get('limit', 10))
        
        logger.info(f"Getting store orders with pagination - page: {page}, limit: {limit}")
        
        result = get_orders_by_store(store_id, page, limit)
        
        # Convert Decimal types for JSON serialization
        result = convert_decimals(result)
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps(result)
        }
        
        logger.info("=== GET STORE ORDERS HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Get store orders error: {str(e)}", exc_info=True)
        logger.info("=== GET STORE ORDERS HANDLER END ===")
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

def handle_get_orders(event, query_params):
    """Handle GET /orders"""
    logger.info("=== GET ORDERS HANDLER START ===")
    try:
        # Extract user ID from request
        customer_id = extract_user_id_from_request(event)
        if not customer_id:
            logger.warning("User ID not found in request, cannot get orders.")
            return {
                'statusCode': STATUS_CODES['UNAUTHORIZED'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['UNAUTHORIZED'],
                        'message': 'User not authenticated'
                    }
                })
            }
        
        logger.info(f"Getting orders for customer ID: {customer_id}")
        
        page = int(query_params.get('page', 1))
        limit = int(query_params.get('limit', 10))
        
        logger.info(f"Getting orders with pagination - page: {page}, limit: {limit}")
        
        result = get_orders_by_customer(customer_id, page, limit)
        
        # Convert Decimal types for JSON serialization
        result = convert_decimals(result)
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps(result)
        }
        
        logger.info("=== GET ORDERS HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Get orders error: {str(e)}", exc_info=True)
        logger.info("=== GET ORDERS HANDLER END ===")
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

def handle_get_order(event, order_id):
    """Handle GET /orders/{id}"""
    logger.info("=== GET ORDER HANDLER START ===")
    try:
        # Extract user ID from request
        customer_id = extract_user_id_from_request(event)
        if not customer_id:
            logger.warning("User ID not found in request, cannot get order.")
            return {
                'statusCode': STATUS_CODES['UNAUTHORIZED'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['UNAUTHORIZED'],
                        'message': 'User not authenticated'
                    }
                })
            }
        
        logger.info(f"Getting order ID: {order_id} for customer ID: {customer_id}")
        
        order = get_order_by_id(order_id)
        if not order or order['customer_id'] != customer_id:
            logger.warning(f"Order not found or access denied for order ID: {order_id}, customer ID: {customer_id}")
            response = {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Order not found'
                    }
                })
            }
            logger.info("=== GET ORDER HANDLER END ===")
            return response
        
        # Convert Decimal types for JSON serialization
        order = convert_decimals(order)
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'order': order})
        }
        
        logger.info("=== GET ORDER HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Get order error: {str(e)}", exc_info=True)
        logger.info("=== GET ORDER HANDLER END ===")
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

def handle_create_order(event, body):
    """Handle POST /orders"""
    logger.info("=== CREATE ORDER HANDLER START ===")
    try:
        logger.info(f"Creating order with data: {json.dumps(body, default=str)}")
        
        # Extract user ID from request
        customer_id = extract_user_id_from_request(event)
        if not customer_id:
            logger.warning("User ID not found in request, cannot create order.")
            return {
                'statusCode': STATUS_CODES['UNAUTHORIZED'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['UNAUTHORIZED'],
                        'message': 'User not authenticated'
                    }
                })
            }
        
        logger.info(f"Creating order for customer ID: {customer_id}")
        
        # Check if creating order from cart
        create_from_cart = body.get('create_from_cart', False)
        
        if create_from_cart:
            # Create order from cart
            store_id = body.get('store_id')
            delivery_address = body.get('delivery_address')
            notes = body.get('notes')
            
            # Validate required fields for cart order
            if not store_id or not delivery_address:
                logger.warning("Missing required fields for cart order")
                response = {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['VALIDATION_ERROR'],
                            'message': 'store_id and delivery_address are required for cart orders'
                        }
                    })
                }
                logger.info("=== CREATE ORDER HANDLER END ===")
                return response
            
            try:
                result = create_order_from_cart(customer_id, store_id, delivery_address, notes)
                
                # Convert Decimal types for JSON serialization
                order = convert_decimals(result['order'])
                items = convert_decimals(result['items'])
                total_amount = convert_decimals(result['total_amount'])
                
                response = {
                    'statusCode': STATUS_CODES['CREATED'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'message': 'Order created successfully from cart',
                        'order': order,
                        'items': items,
                        'total_amount': total_amount
                    })
                }
                
                logger.info("=== CREATE ORDER HANDLER END ===")
                return response
            except ValueError as e:
                logger.warning(f"Cart order validation error: {str(e)}")
                response = {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['VALIDATION_ERROR'],
                            'message': str(e)
                        }
                    })
                }
                logger.info("=== CREATE ORDER HANDLER END ===")
                return response
        else:
            # Create order with manual items
            # Validate required fields
            required_fields = ['store_id', 'delivery_address', 'items']
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
                    logger.info("=== CREATE ORDER HANDLER END ===")
                    return response
            
            logger.info("All required fields present")
            
            # Extract items and prepare product information
            items = body.get('items', [])
            products_info = []
            total_amount = 0
            
            for item in items:
                product_id = item.get('product_id')
                product_name = item.get('product_name', '')
                quantity = item.get('quantity', 0)
                price = item.get('price', 0)
                unit = item.get('unit', 'piece')
                special_notes = item.get('special_notes', '')
                
                item_total = price * quantity
                total_amount += item_total
                
                # Prepare product info for order table
                products_info.append({
                    'product_id': product_id,
                    'product_name': product_name,
                    'quantity': quantity,
                    'price': price,
                    'unit': unit,
                    'special_notes': special_notes,
                    'total': item_total
                })
            
            # Create order with complete product information
            order_data = {
                'store_id': body['store_id'],
                'delivery_address': body['delivery_address'],
                'total_amount': total_amount,
                'products': products_info,
                'notes': body.get('notes')
            }
            
            order = create_order(order_data, customer_id)
            
            # Convert Decimal types for JSON serialization
            order = convert_decimals(order)
            
            response = {
                'statusCode': STATUS_CODES['CREATED'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'message': 'Order created successfully with manual items',
                    'order': order
                })
            }
            
            logger.info("=== CREATE ORDER HANDLER END ===")
            return response
    except Exception as e:
        logger.error(f"Create order error: {str(e)}", exc_info=True)
        logger.info("=== CREATE ORDER HANDLER END ===")
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

def handle_update_order_status(event, order_id, body):
    """Handle PUT /orders/{id}/status"""
    logger.info("=== UPDATE ORDER STATUS HANDLER START ===")
    try:
        # Extract user ID from request
        customer_id = extract_user_id_from_request(event)
        if not customer_id:
            logger.warning("User ID not found in request, cannot update order status.")
            return {
                'statusCode': STATUS_CODES['UNAUTHORIZED'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['UNAUTHORIZED'],
                        'message': 'User not authenticated'
                    }
                })
            }
        
        logger.info(f"Updating order status for order ID: {order_id}, customer ID: {customer_id}")
        logger.info(f"Status update data: {json.dumps(body, default=str)}")
        
        # Validate required fields
        if not body.get('status'):
            logger.warning("Missing required field: status")
            response = {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Status is required'
                    }
                })
            }
            logger.info("=== UPDATE ORDER STATUS HANDLER END ===")
            return response
        
        # Validate status value
        valid_statuses = list(ORDER_STATUS.values())
        if body['status'] not in valid_statuses:
            logger.warning(f"Invalid status: {body['status']}. Valid statuses: {valid_statuses}")
            response = {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': f'Invalid status. Valid statuses: {valid_statuses}'
                    }
                })
            }
            logger.info("=== UPDATE ORDER STATUS HANDLER END ===")
            return response
        
        updated_order = update_order_status(order_id, body['status'], customer_id)
        
        if not updated_order:
            logger.warning(f"Order not found or access denied for order ID: {order_id}")
            response = {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Order not found or access denied'
                    }
                })
            }
            logger.info("=== UPDATE ORDER STATUS HANDLER END ===")
            return response
        
        # Convert Decimal types for JSON serialization
        updated_order = convert_decimals(updated_order)
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'order': updated_order})
        }
        
        logger.info("=== UPDATE ORDER STATUS HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Update order status error: {str(e)}", exc_info=True)
        logger.info("=== UPDATE ORDER STATUS HANDLER END ===")
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