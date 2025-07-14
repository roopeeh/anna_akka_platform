import json
import os
import boto3
from datetime import datetime
import uuid
import logging
from decimal import Decimal
import sys
sys.path.append('..')

def decimal_default(obj):
    """Convert Decimal objects to strings for JSON serialization"""
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

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

def extract_store_id_from_request(event, body):
    """Extract store ID from request path, body, or headers"""
    try:
        # First try to get store_id from the request path
        path = event.get('requestContext', {}).get('http', {}).get('path', '')
        if '/stores/' in path and '/products' in path:
            path_parts = path.split('/')
            try:
                stores_index = path_parts.index('stores')
                if stores_index + 1 < len(path_parts):
                    store_id = path_parts[stores_index + 1]
                    logger.info(f"Extracted store ID from path: {store_id}")
                    return store_id
            except ValueError:
                pass
        
        # Try to get store_id from request body
        if body and body.get('store_id'):
            store_id = body.get('store_id')
            logger.info(f"Extracted store ID from body: {store_id}")
            return store_id
        
        # Check for store_id in headers
        headers = event.get('headers', {}) or {}
        store_id = headers.get('X-Store-ID') or headers.get('x-store-id')
        if store_id:
            logger.info(f"Extracted store ID from headers: {store_id}")
            return store_id
        
        # For development/testing, check for store_id in query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        store_id = query_params.get('store_id')
        if store_id:
            logger.info(f"Extracted store ID from query params: {store_id}")
            return store_id
        
        logger.warning("No store ID found in request path, body, headers, or query parameters")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting store ID: {str(e)}")
        return None

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
products_table = dynamodb.Table(os.environ['PRODUCTS_TABLE'])  # type: ignore
available_products_table = dynamodb.Table(os.environ['AVAILABLE_PRODUCTS_TABLE'])  # type: ignore
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
    'METHOD_NOT_ALLOWED': int(os.environ.get('STATUS_CODES_METHOD_NOT_ALLOWED', '405')),
    'CONFLICT': int(os.environ.get('STATUS_CODES_CONFLICT', '409')),
    'UNPROCESSABLE_ENTITY': int(os.environ.get('STATUS_CODES_UNPROCESSABLE_ENTITY', '422')),
    'INTERNAL_ERROR': int(os.environ.get('STATUS_CODES_INTERNAL_ERROR', '500'))
}

CORS_HEADERS = {
    'Content-Type': os.environ.get('CORS_HEADERS_CONTENT_TYPE', 'application/json'),
    'Access-Control-Allow-Origin': os.environ.get('CORS_HEADERS_ACCESS_CONTROL_ORIGIN', '*'),
    'Access-Control-Allow-Headers': os.environ.get('CORS_HEADERS_ACCESS_CONTROL_HEADERS', 'Content-Type,Authorization,X-Requested-With'),
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

ALLOWED_UPDATE_FIELDS = {
    'PRODUCT': ['name', 'description', 'price', 'unit', 'stock', 'image_url', 'category_id']
}

def get_products_with_pagination(page=1, limit=20, store_id=None, category_id=None, search=None, min_price=None, max_price=None, in_stock=None, available_product_id=None):
    """Get products with pagination and filtering"""
    logger.info(f"Getting products with filters - page: {page}, limit: {limit}, store_id: {store_id}, category_id: {category_id}, search: {search}, min_price: {min_price}, max_price: {max_price}, in_stock: {in_stock}, available_product_id: {available_product_id}")
    
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
    
    if available_product_id:
        filter_expressions.append("#available_product_id = :available_product_id")
        expression_values[':available_product_id'] = available_product_id
        expression_names['#available_product_id'] = 'available_product_id'
    
    if filter_expressions:
        scan_kwargs['FilterExpression'] = ' AND '.join(filter_expressions)
        scan_kwargs['ExpressionAttributeValues'] = expression_values
        scan_kwargs['ExpressionAttributeNames'] = expression_names
    
    logger.info(f"Scan kwargs: {json.dumps(scan_kwargs, default=str)}")
    
    # Get all items (in a real app, you'd implement proper pagination)
    response = products_table.scan(**scan_kwargs)
    products = response.get('Items', [])
    
    logger.info(f"Found {len(products)} products before pagination")
    
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
    
    logger.info(f"Returning {len(paginated_products)} products for page {page}")
    return result

def get_product_by_store_and_available_product(store_id, available_product_id):
    """Get product by store ID and available product ID"""
    logger.info(f"Getting product for store ID: {store_id}, available product ID: {available_product_id}")
    
    scan_kwargs = {
        'FilterExpression': '#store_id = :store_id AND #available_product_id = :available_product_id',
        'ExpressionAttributeValues': {
            ':store_id': store_id,
            ':available_product_id': available_product_id
        },
        'ExpressionAttributeNames': {
            '#store_id': 'store_id',
            '#available_product_id': 'available_product_id'
        }
    }
    
    logger.info(f"Scan kwargs: {json.dumps(scan_kwargs, default=str)}")
    
    response = products_table.scan(**scan_kwargs)
    products = response.get('Items', [])
    
    logger.info(f"Found {len(products)} products for store {store_id} and available product {available_product_id}")
    
    # Return the first product found (should be unique combination)
    product = products[0] if products else None
    logger.info(f"Product lookup result: {'Found' if product else 'Not found'}")
    return product

def get_product_by_id(product_id):
    """Get product by ID"""
    logger.info(f"Getting product by ID: {product_id}")
    response = products_table.get_item(Key={'id': product_id})
    product = response.get('Item')
    logger.info(f"Product lookup result: {'Found' if product else 'Not found'}")
    return product

def update_store_product_ids(store_id):
    """Update store with product IDs from available products"""
    logger.info(f"Updating product IDs for store: {store_id}")
    
    try:
        # Get all products for this store
        query_kwargs = {
            'IndexName': 'store_id_index',
            'KeyConditionExpression': 'store_id = :store_id',
            'ExpressionAttributeValues': {':store_id': store_id}
        }
        
        response = products_table.query(**query_kwargs)
        products = response.get('Items', [])
        
        # Extract available product IDs from store products
        available_product_ids = []
        for product in products:
            available_product_id = product.get('available_product_id')
            if available_product_id:
                available_product_ids.append(available_product_id)
        
        # Remove duplicates
        available_product_ids = list(set(available_product_ids))
        
        logger.info(f"Found {len(available_product_ids)} unique available product IDs for store {store_id}")
        
        # Update the store with product IDs
        update_expression = "SET #product_ids = :product_ids, #updated_at = :updated_at"
        expression_values = {
            ':product_ids': available_product_ids,
            ':updated_at': datetime.utcnow().isoformat()
        }
        expression_names = {
            '#product_ids': 'product_ids',
            '#updated_at': 'updated_at'
        }
        
        response = stores_table.update_item(
            Key={'id': store_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names,
            ReturnValues="ALL_NEW"
        )
        
        updated_store = response.get('Attributes')
        logger.info(f"Store product IDs updated successfully: {updated_store is not None}")
        return updated_store
        
    except Exception as e:
        logger.error(f"Error updating store product IDs: {str(e)}")
        return None

def create_product(product_data, store_id):
    """Create a new product"""
    logger.info(f"Creating product for store ID: {store_id}")
    logger.info(f"Product data: {json.dumps(product_data, default=str)}")
    
    # Check if this is adding from available products or creating new
    available_product_id = product_data.get('available_product_id')
    
    if available_product_id:
        # Adding from available products catalog
        logger.info(f"Adding product from available catalog with ID: {available_product_id}")
        
        # Get the available product
        available_product = available_products_table.get_item(Key={'id': available_product_id})
        available_product_item = available_product.get('Item')
        
        if not available_product_item:
            logger.warning(f"Available product not found with ID: {available_product_id}")
            return None
        
        # Create store product based on available product
        product_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        product_item = {
            'id': product_id,
            'store_id': store_id,
            'available_product_id': available_product_id,
            'category_id': available_product_item.get('category_id', 'uncategorized'),  # Default category
            'name': available_product_item['name'],
            'description': available_product_item.get('description'),
            'price': Decimal(str(product_data.get('price', available_product_item['price']))),  # Allow store to set their own price
            'unit': available_product_item.get('unit', 'piece'),
            'stock': product_data.get('stock', 0),
            'image_url': available_product_item.get('image_url'),
            'created_at': timestamp,
            'updated_at': timestamp
        }
    else:
        # Creating a completely new product
        logger.info("Creating new product (not from available catalog)")
        
        product_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        product_item = {
            'id': product_id,
            'store_id': store_id,
            'category_id': product_data.get('category_id', 'uncategorized'),  # Default category
            'name': product_data['name'],
            'description': product_data.get('description'),
            'price': Decimal(str(product_data['price'])),
            'unit': product_data.get('unit', 'piece'),
            'stock': product_data.get('stock', 0),
            'image_url': product_data.get('image_url'),
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        # Also add to available products catalog
        available_product_item = {
            'id': str(uuid.uuid4()),
            'category_id': product_data.get('category_id', 'uncategorized'),  # Default category
            'name': product_data['name'],
            'description': product_data.get('description'),
            'price': Decimal(str(product_data['price'])),
            'unit': product_data.get('unit', 'piece'),
            'image_url': product_data.get('image_url'),
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        logger.info(f"Adding new product to available catalog: {json.dumps(available_product_item, default=str)}")
        available_products_table.put_item(Item=available_product_item)
        
        # Link the store product to the available product
        product_item['available_product_id'] = available_product_item['id']
    
    logger.info(f"Product item to be created: {json.dumps(product_item, default=str)}")
    products_table.put_item(Item=product_item)
    logger.info(f"Product created successfully with ID: {product_id}")
    
    # Update store product IDs after creating product
    update_store_product_ids(store_id)
    
    return product_item

def update_product(product_id, update_data, store_id):
    """Update product details"""
    logger.info(f"Updating product ID: {product_id} for store ID: {store_id}")
    logger.info(f"Update data: {json.dumps(update_data, default=str)}")
    
    # First verify ownership
    product = get_product_by_id(product_id)
    if not product or product['store_id'] != store_id:
        logger.warning(f"Product not found or access denied for product ID: {product_id}, store ID: {store_id}")
        return None
    
    # Prepare update expression
    update_expression = "SET "
    expression_values = {}
    expression_names = {}
    
    for key, value in update_data.items():
        if key in ['name', 'description', 'price', 'unit', 'stock', 'image_url', 'category_id']:
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
    
    response = products_table.update_item(
        Key={'id': product_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ExpressionAttributeNames=expression_names,
        ReturnValues="ALL_NEW"
    )
    
    updated_product = response.get('Attributes')
    logger.info(f"Product updated successfully: {updated_product is not None}")
    return updated_product

def get_store_products(store_id, page=1, limit=20, category_id=None, search=None):
    """Get products for a specific store"""
    logger.info(f"Getting products for store ID: {store_id}, page: {page}, limit: {limit}, category_id: {category_id}, search: {search}")
    
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
    
    logger.info(f"Query kwargs: {json.dumps(query_kwargs, default=str)}")
    
    response = products_table.query(**query_kwargs)
    products = response.get('Items', [])
    
    logger.info(f"Found {len(products)} products for store {store_id}")
    
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
    
    logger.info(f"Returning {len(paginated_products)} products for page {page}")
    return result

def handler(event, context):
    """Main Lambda handler for products"""
    logger.info("=== PRODUCTS HANDLER START ===")
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
            logger.error(f"Malformed JSON in request body: {str(e)}")
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
        # Handle both with and without stage prefix (/dev/products or /products)
        if (path == '/products' or path.endswith('/products')):
            if method == 'GET':
                logger.info("Routing to get products handler")
                response = handle_get_products(query_params)
                logger.info(f"Get products response: {json.dumps(response, default=str)}")
                return response
            elif method == 'POST':
                logger.info("Routing to create product handler (general)")
                # For POST /products, we need a store_id in the body or use a default
                store_id = extract_store_id_from_request(event, body)
                if not store_id:
                    response = {
                        'statusCode': STATUS_CODES['BAD_REQUEST'],
                        'headers': CORS_HEADERS,
                        'body': json.dumps({
                            'error': {
                                'code': ERROR_CODES['VALIDATION_ERROR'],
                                'message': 'Store ID is required'
                            }
                        })
                    }
                    logger.info("=== PRODUCTS HANDLER END ===")
                    return response
                response = handle_create_product(event, body, store_id)
                logger.info(f"Create product response: {json.dumps(response, default=str)}")
                return response
            elif method == 'OPTIONS':
                logger.info("Handling OPTIONS request for CORS preflight")
                return {
                    'statusCode': STATUS_CODES['OK'],
                    'headers': CORS_HEADERS,
                    'body': ''
                }
            elif method in ['PUT', 'DELETE']:
                logger.warning(f"Method not allowed: {method} for /products")
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
        elif '/products/' in path and method == 'GET':
            # Extract product_id from path, handling both /products/{id} and /dev/products/{id}
            # Find the product_id after the last '/products/' in the path
            products_index = path.rfind('/products/')
            if products_index != -1:
                product_id = path[products_index + 10:]  # '/products/' is 10 characters
                logger.info(f"Routing to get product handler for ID: {product_id}")
                response = handle_get_product(product_id)
                logger.info(f"Get product response: {json.dumps(response, default=str)}")
                return response
            else:
                logger.warning("Could not extract product_id from path")
                return {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['VALIDATION_ERROR'],
                            'message': 'Invalid product ID in path'
                        }
                    })
                }
        elif (path.startswith('/stores/') and '/products' in path) and method == 'GET':
            # Handle GET /stores/{store_id}/products and /dev/stores/{store_id}/products
            path_parts = path.split('/')
            logger.info(f"Path parts for GET store products: {path_parts}")
            
            # Find store_id in the path parts - look for 'stores' then the next part
            store_id = None
            try:
                stores_index = path_parts.index('stores')
                if stores_index + 1 < len(path_parts):
                    store_id = path_parts[stores_index + 1]
                    logger.info(f"Extracted store_id for get products: {store_id}")
                    logger.info(f"Routing to get store products handler for store ID: {store_id}")
                    response = handle_get_store_products(store_id, query_params)
                    logger.info(f"Get store products response: {json.dumps(response, default=str)}")
                    return response
                else:
                    logger.warning("No store_id found in path for get products")
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
                logger.warning("Could not find 'stores' in path for get products")
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
        elif (path.startswith('/stores/') and '/products' in path) and method == 'POST':
            # Handle POST /stores/{store_id}/products and /dev/stores/{store_id}/products
            path_parts = path.split('/')
            logger.info(f"Path parts for POST store products: {path_parts}")
            
            # Find store_id in the path parts - look for 'stores' then the next part
            store_id = None
            try:
                stores_index = path_parts.index('stores')
                if stores_index + 1 < len(path_parts):
                    store_id = path_parts[stores_index + 1]
                    logger.info(f"Extracted store_id for product creation: {store_id}")
                    logger.info(f"Routing to create product handler for store ID: {store_id}")
                    response = handle_create_product(event, body, store_id)
                    logger.info(f"Create product response: {json.dumps(response, default=str)}")
                    return response
                else:
                    logger.warning("No store_id found in path for product creation")
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
                logger.warning("Could not find 'stores' in path for product creation")
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
        elif '/products/' in path and method == 'PUT':
            # Extract product_id from path, handling both /products/{id} and /dev/products/{id}
            products_index = path.rfind('/products/')
            if products_index != -1:
                product_id = path[products_index + 10:]  # '/products/' is 10 characters
                logger.info(f"Routing to update product handler for ID: {product_id}")
                response = handle_update_product(event, product_id, body)
                logger.info(f"Update product response: {json.dumps(response, default=str)}")
                return response
            else:
                logger.warning("Could not extract product_id from path")
                return {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['VALIDATION_ERROR'],
                            'message': 'Invalid product ID in path'
                        }
                    })
                }
        elif '/products/' in path and method == 'DELETE':
            # Extract product_id from path, handling both /products/{id} and /dev/products/{id}
            products_index = path.rfind('/products/')
            if products_index != -1:
                product_id = path[products_index + 10:]  # '/products/' is 10 characters
                logger.info(f"Routing to delete product handler for ID: {product_id}")
                response = handle_delete_product(event, product_id)
                logger.info(f"Delete product response: {json.dumps(response, default=str)}")
                return response
            else:
                logger.warning("Could not extract product_id from path")
                return {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['VALIDATION_ERROR'],
                            'message': 'Invalid product ID in path'
                        }
                    })
                }

        else:
            logger.warning(f"Endpoint not found: {method} {path}")
            return {
                'statusCode': 404,
                'headers': CORS_HEADERS,
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
        logger.info("=== PRODUCTS HANDLER END ===")

def handle_get_products(query_params):
    """Handle GET /products"""
    logger.info("=== GET PRODUCTS HANDLER START ===")
    try:
        page = int(query_params.get('page', 1))
        limit = int(query_params.get('limit', 20))
        store_id = query_params.get('store_id')
        category_id = query_params.get('category_id')
        search = query_params.get('search')
        min_price = Decimal(str(query_params.get('min_price'))) if query_params.get('min_price') else None
        max_price = Decimal(str(query_params.get('max_price'))) if query_params.get('max_price') else None
        in_stock = query_params.get('in_stock')
        if in_stock is not None:
            in_stock = in_stock.lower() == 'true'
        available_product_id = query_params.get('available_product_id')
        
        # If both store_id and available_product_id are provided, get specific product
        if store_id and available_product_id:
            logger.info(f"Getting specific product for store ID: {store_id}, available product ID: {available_product_id}")
            product = get_product_by_store_and_available_product(store_id, available_product_id)
            if not product:
                logger.warning(f"Product not found for store ID: {store_id}, available product ID: {available_product_id}")
                response = {
                    'statusCode': STATUS_CODES['NOT_FOUND'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['NOT_FOUND'],
                            'message': 'Product not found for this store and available product combination'
                        }
                    })
                }
                logger.info("=== GET PRODUCTS HANDLER END ===")
                return response
            
            response = {
                'statusCode': STATUS_CODES['OK'],
                'headers': CORS_HEADERS,
                'body': json.dumps({'product': product}, default=decimal_default)
            }
            logger.info("=== GET PRODUCTS HANDLER END ===")
            return response
        
        # Otherwise, get products with pagination and filtering
        logger.info(f"Getting products with filters - page: {page}, limit: {limit}, store_id: {store_id}, category_id: {category_id}, search: {search}, min_price: {min_price}, max_price: {max_price}, in_stock: {in_stock}, available_product_id: {available_product_id}")
        
        result = get_products_with_pagination(
            page, limit, store_id, category_id, search, min_price, max_price, in_stock, available_product_id
        )
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps(result, default=decimal_default)
        }
        
        logger.info("=== GET PRODUCTS HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Get products error: {str(e)}", exc_info=True)
        logger.info("=== GET PRODUCTS HANDLER END ===")
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
    logger.info("=== GET PRODUCT HANDLER START ===")
    try:
        logger.info(f"Getting product with ID: {product_id}")
        
        product = get_product_by_id(product_id)
        if not product:
            logger.warning(f"Product not found with ID: {product_id}")
            response = {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Product not found'
                    }
                })
            }
            logger.info("=== GET PRODUCT HANDLER END ===")
            return response
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'product': product}, default=decimal_default)
        }
        
        logger.info("=== GET PRODUCT HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Get product error: {str(e)}", exc_info=True)
        logger.info("=== GET PRODUCT HANDLER END ===")
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
    logger.info("=== GET STORE PRODUCTS HANDLER START ===")
    try:
        page = int(query_params.get('page', 1))
        limit = int(query_params.get('limit', 20))
        category_id = query_params.get('category_id')
        search = query_params.get('search')
        
        logger.info(f"Getting products for store ID: {store_id}, page: {page}, limit: {limit}, category_id: {category_id}, search: {search}")
        
        result = get_store_products(store_id, page, limit, category_id, search)
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps(result, default=decimal_default)
        }
        
        logger.info("=== GET STORE PRODUCTS HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Get store products error: {str(e)}", exc_info=True)
        logger.info("=== GET STORE PRODUCTS HANDLER END ===")
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

def handle_create_product(event, body, store_id):
    """Handle POST /stores/{storeId}/products"""
    logger.info("=== CREATE PRODUCT HANDLER START ===")
    try:
        # Extract user ID for authorization
        user_id = extract_user_id_from_request(event)
        if not user_id:
            logger.warning("User ID not found in request for create product")
            response = {
                'statusCode': STATUS_CODES['UNAUTHORIZED'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['UNAUTHORIZED'],
                        'message': 'User not authenticated'
                    }
                })
            }
            logger.info("=== CREATE PRODUCT HANDLER END ===")
            return response
        
        logger.info(f"Creating product for store ID: {store_id} by user ID: {user_id}")
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
            logger.info("=== CREATE PRODUCT HANDLER END ===")
            return response
        
        # Validate price is positive
        try:
            price = float(body.get('price', 0))
            if price <= 0:
                logger.warning("Invalid price: must be positive")
                response = {
                    'statusCode': STATUS_CODES['BAD_REQUEST'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['VALIDATION_ERROR'],
                            'message': 'Price must be positive'
                        }
                    })
                }
                logger.info("=== CREATE PRODUCT HANDLER END ===")
                return response
        except (ValueError, TypeError):
            logger.warning("Invalid price format")
            response = {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Invalid price format'
                    }
                })
            }
            logger.info("=== CREATE PRODUCT HANDLER END ===")
            return response
        
        # Validate stock is non-negative
        stock = body.get('stock', 0)
        if stock is not None and stock < 0:
            logger.warning("Invalid stock: must be non-negative")
            response = {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Stock must be non-negative'
                    }
                })
            }
            logger.info("=== CREATE PRODUCT HANDLER END ===")
            return response
        
        product = create_product(body, store_id)
        
        response = {
            'statusCode': STATUS_CODES['CREATED'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'product': product}, default=decimal_default)
        }
        
        logger.info("=== CREATE PRODUCT HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Create product error: {str(e)}", exc_info=True)
        logger.info("=== CREATE PRODUCT HANDLER END ===")
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

def handle_update_product(event, product_id, body):
    """Handle PUT /products/{id}"""
    logger.info("=== UPDATE PRODUCT HANDLER START ===")
    try:
        # For now, use a mock store_id - security will be implemented later
        store_id = extract_store_id_from_request(event, body)
        if not store_id:
            response = {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Store ID is required'
                    }
                })
            }
            logger.info("=== UPDATE PRODUCT HANDLER END ===")
            return response

        logger.info(f"Updating product ID: {product_id} for store ID: {store_id}")
        logger.info(f"Update data: {json.dumps(body, default=str)}")
        
        # Validate that at least one field is provided
        allowed_fields = ALLOWED_UPDATE_FIELDS['PRODUCT']
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
            logger.info("=== UPDATE PRODUCT HANDLER END ===")
            return response
        
        product = update_product(product_id, update_data, store_id)
        if not product:
            logger.warning(f"Product not found or access denied for ID: {product_id}")
            response = {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Product not found or access denied'
                    }
                })
            }
            logger.info("=== UPDATE PRODUCT HANDLER END ===")
            return response
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'product': product}, default=decimal_default)
        }
        
        logger.info("=== UPDATE PRODUCT HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Update product error: {str(e)}", exc_info=True)
        logger.info("=== UPDATE PRODUCT HANDLER END ===")
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

def handle_delete_product(event, product_id):
    """Handle DELETE /products/{id}"""
    logger.info("=== DELETE PRODUCT HANDLER START ===")
    try:
        # For now, use a mock store_id - security will be implemented later
        store_id = extract_store_id_from_request(event, {}) # No body for delete
        if not store_id:
            response = {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Store ID is required'
                    }
                })
            }
            logger.info("=== DELETE PRODUCT HANDLER END ===")
            return response

        logger.info(f"Deleting product ID: {product_id} for store ID: {store_id}")
        
        product = get_product_by_id(product_id)
        if not product or product['store_id'] != store_id:
            logger.warning(f"Product not found or access denied for ID: {product_id}")
            response = {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Product not found or access denied'
                    }
                })
            }
            logger.info("=== DELETE PRODUCT HANDLER END ===")
            return response
        
        products_table.delete_item(Key={'id': product_id})
        logger.info(f"Product deleted successfully: {product_id}")
        
        # Update store product IDs after deleting product
        update_store_product_ids(product['store_id'])
        
        response = {
            'statusCode': STATUS_CODES['NO_CONTENT'],
            'headers': CORS_HEADERS,
            'body': ''
        }
        
        logger.info("=== DELETE PRODUCT HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Delete product error: {str(e)}", exc_info=True)
        logger.info("=== DELETE PRODUCT HANDLER END ===")
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

def handle_get_product_by_store_and_available_product(store_id, available_product_id):
    """Handle GET /stores/{storeId}/products/available/{availableProductId}"""
    logger.info("=== GET PRODUCT BY STORE AND AVAILABLE PRODUCT HANDLER START ===")
    try:
        logger.info(f"Getting product for store ID: {store_id}, available product ID: {available_product_id}")
        
        product = get_product_by_store_and_available_product(store_id, available_product_id)
        if not product:
            logger.warning(f"Product not found for store ID: {store_id}, available product ID: {available_product_id}")
            response = {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Product not found for this store and available product combination'
                    }
                })
            }
            logger.info("=== GET PRODUCT BY STORE AND AVAILABLE PRODUCT HANDLER END ===")
            return response
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'product': product}, default=decimal_default)
        }
        
        logger.info("=== GET PRODUCT BY STORE AND AVAILABLE PRODUCT HANDLER END ===")
        return response
    except Exception as e:
        logger.error(f"Get product by store and available product error: {str(e)}", exc_info=True)
        logger.info("=== GET PRODUCT BY STORE AND AVAILABLE PRODUCT HANDLER END ===")
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