import json
import os
import boto3
from datetime import datetime, timedelta
import uuid
import logging
from decimal import Decimal
import sys
sys.path.append('..')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Custom JSON encoder to handle Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
cart_table = dynamodb.Table(os.environ['CART_TABLE'])  # type: ignore
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
    'METHOD_NOT_ALLOWED': int(os.environ.get('STATUS_CODES_METHOD_NOT_ALLOWED', '405')),
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
    'OWNER_ID_INDEX': os.environ.get('INDEX_NAMES_OWNER_ID_INDEX', 'owner_id_index'),
    'STORE_ID_INDEX': os.environ.get('INDEX_NAMES_STORE_ID_INDEX', 'store_id_index'),
    'CATEGORY_ID_INDEX': os.environ.get('INDEX_NAMES_CATEGORY_ID_INDEX', 'category_id_index'),
    'CUSTOMER_ID_INDEX': os.environ.get('INDEX_NAMES_CUSTOMER_ID_INDEX', 'customer_id_index'),
    'STATUS_INDEX': os.environ.get('INDEX_NAMES_STATUS_INDEX', 'status_index'),
    'ORDER_ID_INDEX': os.environ.get('INDEX_NAMES_ORDER_ID_INDEX', 'order_id_index'),
    'CART_STORE_ID_INDEX': os.environ.get('INDEX_NAMES_CART_STORE_ID_INDEX', 'store_id_index'),
    'CART_EXPIRES_AT_INDEX': os.environ.get('INDEX_NAMES_CART_EXPIRES_AT_INDEX', 'expires_at_index')
}

REQUIRED_FIELDS = {
    'CART_ADD_ITEM': ['product_id', 'quantity'],
    'CART_UPDATE_ITEM': ['quantity']
}

CART_CONFIG = {
    'TTL_DAYS': int(os.environ.get('CART_CONFIG_TTL_DAYS', '30')),
    'MAX_QUANTITY': int(os.environ.get('CART_CONFIG_MAX_QUANTITY', '100')),
    'MAX_ITEMS': int(os.environ.get('CART_CONFIG_MAX_ITEMS', '50'))
}

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

def get_product_by_id(product_id):
    """Get product by ID from available products catalog"""
    try:
        response = available_products_table.get_item(Key={'id': product_id})
        return response.get('Item')
    except Exception as e:
        logger.error(f"Error getting available product {product_id}: {str(e)}")
        return None

def calculate_cart_total(cart_items):
    """Calculate total amount for cart items"""
    total = 0
    for item in cart_items:
        total += item.get('price', 0) * item.get('quantity', 0)
    return total

def add_item_to_cart(customer_id, product_id, quantity):
    """Add item to cart from available products catalog"""
    logger.info(f"Adding item to cart - customer: {customer_id}, product: {product_id}, quantity: {quantity}")
    
    # Validate product exists in available products catalog
    product = get_product_by_id(product_id)
    if not product:
        raise ValueError(f"Product {product_id} not found in available products catalog")
    
    # Available products don't have stock limits, so we skip stock validation
    
    # Check if item already exists in cart
    try:
        response = cart_table.get_item(
            Key={
                'customer_id': customer_id,
                'product_id': product_id
            }
        )
        existing_item = response.get('Item')
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item.get('quantity', 0) + quantity
            if new_quantity > CART_CONFIG['MAX_QUANTITY']:
                raise ValueError(f"Quantity exceeds maximum limit of {CART_CONFIG['MAX_QUANTITY']}")
            
            # Update existing item
            cart_table.update_item(
                Key={
                    'customer_id': customer_id,
                    'product_id': product_id
                },
                UpdateExpression="SET quantity = :quantity, updated_at = :updated_at",
                ExpressionAttributeValues={
                    ':quantity': new_quantity,
                    ':updated_at': datetime.utcnow().isoformat()
                }
            )
            logger.info(f"Updated cart item quantity to {new_quantity}")
        else:
            # Add new item
            expires_at = int((datetime.utcnow() + timedelta(days=CART_CONFIG['TTL_DAYS'])).timestamp())
            
            cart_item = {
                'customer_id': customer_id,
                'product_id': product_id,
                'store_id': 'catalog',  # All items from available products go to 'catalog' store
                'quantity': quantity,
                'price': product.get('price', 0),
                'product_name': product.get('name', ''),
                'product_image': product.get('image_url', ''),
                'unit': product.get('unit', 'piece'),
                'expires_at': expires_at,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            cart_table.put_item(Item=cart_item)
            logger.info(f"Added new item to cart")
            
    except Exception as e:
        logger.error(f"Error adding item to cart: {str(e)}")
        raise e

def update_cart_item(customer_id, product_id, quantity):
    """Update cart item quantity"""
    logger.info(f"Updating cart item - customer: {customer_id}, product: {product_id}, quantity: {quantity}")
    
    if quantity <= 0:
        # Remove item if quantity is 0 or negative
        remove_item_from_cart(customer_id, product_id)
        return
    
    if quantity > CART_CONFIG['MAX_QUANTITY']:
        raise ValueError(f"Quantity exceeds maximum limit of {CART_CONFIG['MAX_QUANTITY']}")
    
    # Validate product exists in available products catalog
    product = get_product_by_id(product_id)
    if not product:
        raise ValueError(f"Product {product_id} not found in available products catalog")
    
    # Available products don't have stock limits, so we skip stock validation
    
    try:
        cart_table.update_item(
            Key={
                'customer_id': customer_id,
                'product_id': product_id
            },
            UpdateExpression="SET quantity = :quantity, updated_at = :updated_at",
            ExpressionAttributeValues={
                ':quantity': quantity,
                ':updated_at': datetime.utcnow().isoformat()
            },
            ConditionExpression="attribute_exists(customer_id) AND attribute_exists(product_id)"
        )
        logger.info(f"Updated cart item quantity to {quantity}")
    except cart_table.meta.client.exceptions.ConditionalCheckFailedException:
        raise ValueError(f"Cart item not found")
    except Exception as e:
        logger.error(f"Error updating cart item: {str(e)}")
        raise e

def remove_item_from_cart(customer_id, product_id):
    """Remove item from cart"""
    logger.info(f"Removing item from cart - customer: {customer_id}, product: {product_id}")
    
    try:
        cart_table.delete_item(
            Key={
                'customer_id': customer_id,
                'product_id': product_id
            }
        )
        logger.info(f"Removed item from cart")
    except Exception as e:
        logger.error(f"Error removing item from cart: {str(e)}")
        raise e

def clear_cart(customer_id):
    """Clear all items from cart"""
    logger.info(f"Clearing cart for customer: {customer_id}")
    
    try:
        # Get all cart items for customer
        response = cart_table.query(
            KeyConditionExpression='customer_id = :customer_id',
            ExpressionAttributeValues={
                ':customer_id': customer_id
            }
        )
        
        cart_items = response.get('Items', [])
        
        # Delete all items
        with cart_table.batch_writer() as batch:
            for item in cart_items:
                batch.delete_item(
                    Key={
                        'customer_id': customer_id,
                        'product_id': item['product_id']
                    }
                )
        
        logger.info(f"Cleared {len(cart_items)} items from cart")
    except Exception as e:
        logger.error(f"Error clearing cart: {str(e)}")
        raise e

def get_cart(customer_id):
    """Get customer's cart"""
    logger.info(f"Getting cart for customer: {customer_id}")
    
    try:
        response = cart_table.query(
            KeyConditionExpression='customer_id = :customer_id',
            ExpressionAttributeValues={
                ':customer_id': customer_id
            }
        )
        
        cart_items = response.get('Items', [])
        
        # Calculate totals
        total_items = len(cart_items)
        total_quantity = sum(item.get('quantity', 0) for item in cart_items)
        total_amount = calculate_cart_total(cart_items)
        
        # Group by store
        stores = {}
        for item in cart_items:
            store_id = item.get('store_id')
            if store_id not in stores:
                stores[store_id] = {
                    'store_id': store_id,
                    'items': [],
                    'total_amount': 0
                }
            stores[store_id]['items'].append(item)
            stores[store_id]['total_amount'] += item.get('price', 0) * item.get('quantity', 0)
        
        cart_data = {
            'customer_id': customer_id,
            'items': cart_items,
            'total_items': total_items,
            'total_quantity': total_quantity,
            'total_amount': total_amount,
            'stores': list(stores.values())
        }
        
        logger.info(f"Retrieved cart with {total_items} items, total amount: {total_amount}")
        return cart_data
        
    except Exception as e:
        logger.error(f"Error getting cart: {str(e)}")
        raise e

def validate_cart_for_order(customer_id, store_id):
    """Validate cart items before creating order"""
    logger.info(f"Validating cart for order - customer: {customer_id}, store: {store_id}")
    
    try:
        # Get cart items for the specific store
        response = cart_table.query(
            KeyConditionExpression='customer_id = :customer_id',
            FilterExpression='store_id = :store_id',
            ExpressionAttributeValues={
                ':customer_id': customer_id,
                ':store_id': store_id
            }
        )
        
        cart_items = response.get('Items', [])
        
        if not cart_items:
            raise ValueError("No items in cart for this store")
        
        # Validate each item
        validated_items = []
        total_amount = 0
        
        for item in cart_items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)
            price = item.get('price', 0)
            
            # Check if product still exists in available products catalog
            product = get_product_by_id(product_id)
            if not product:
                raise ValueError(f"Product {product_id} no longer available in catalog")
            
            # Available products don't have stock limits, so we skip stock validation
            
            if product.get('price', 0) != price:
                # Price has changed, update cart item
                cart_table.update_item(
                    Key={
                        'customer_id': customer_id,
                        'product_id': product_id
                    },
                    UpdateExpression="SET price = :price, updated_at = :updated_at",
                    ExpressionAttributeValues={
                        ':price': product.get('price', 0),
                        ':updated_at': datetime.utcnow().isoformat()
                    }
                )
                price = product.get('price', 0)
            
            validated_items.append({
                'product_id': product_id,
                'quantity': quantity,
                'price': price,
                'product_name': product.get('name', ''),
                'unit': product.get('unit', 'piece')
            })
            
            total_amount += price * quantity
        
        return {
            'items': validated_items,
            'total_amount': total_amount,
            'item_count': len(validated_items)
        }
        
    except Exception as e:
        logger.error(f"Error validating cart: {str(e)}")
        raise e

def handle_get_cart(event):
    """Handle GET /cart"""
    logger.info("=== GET CART HANDLER START ===")
    try:
        customer_id = extract_user_id_from_request(event)
        if not customer_id:
            raise ValueError("User ID not found in request")
        logger.info(f"Getting cart for customer ID: {customer_id}")
        
        cart_data = get_cart(customer_id)
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'cart': cart_data}, cls=DecimalEncoder)
        }
        
        logger.info("=== GET CART HANDLER END ===")
        return response
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        logger.info("=== GET CART HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['BAD_REQUEST'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['VALIDATION_ERROR'],
                    'message': str(e)
                }
            }, cls=DecimalEncoder)
        }
    except Exception as e:
        logger.error(f"Get cart error: {str(e)}", exc_info=True)
        logger.info("=== GET CART HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['INTERNAL_ERROR'],
                    'message': str(e)
                }
            }, cls=DecimalEncoder)
        }

def handle_add_to_cart(event):
    """Handle POST /cart/items"""
    logger.info("=== ADD TO CART HANDLER START ===")
    try:
        body = json.loads(event.get('body', '{}'))
        logger.info(f"Adding item to cart with data: {json.dumps(body, default=str)}")
        
        customer_id = extract_user_id_from_request(event)
        if not customer_id:
            raise ValueError("User ID not found in request")
        logger.info(f"Adding item to cart for customer ID: {customer_id}")
        
        # Validate required fields
        required_fields = REQUIRED_FIELDS['CART_ADD_ITEM']
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
                    }, cls=DecimalEncoder)
                }
                logger.info("=== ADD TO CART HANDLER END ===")
                return response
        
        product_id = body['product_id']
        quantity = int(body['quantity'])
        
        if quantity <= 0:
            logger.warning("Quantity must be greater than 0")
            response = {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Quantity must be greater than 0'
                    }
                }, cls=DecimalEncoder)
            }
            logger.info("=== ADD TO CART HANDLER END ===")
            return response
        
        if quantity > CART_CONFIG['MAX_QUANTITY']:
            logger.warning(f"Quantity exceeds maximum limit of {CART_CONFIG['MAX_QUANTITY']}")
            response = {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': f'Quantity exceeds maximum limit of {CART_CONFIG["MAX_QUANTITY"]}'
                    }
                }, cls=DecimalEncoder)
            }
            logger.info("=== ADD TO CART HANDLER END ===")
            return response
        
        # Add item to cart from available products catalog
        add_item_to_cart(customer_id, product_id, quantity)
        
        # Get updated cart
        cart_data = get_cart(customer_id)
        
        response = {
            'statusCode': STATUS_CODES['CREATED'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'message': 'Item added to cart successfully',
                'cart': cart_data
            }, cls=DecimalEncoder)
        }
        
        logger.info("=== ADD TO CART HANDLER END ===")
        return response
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        logger.info("=== ADD TO CART HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['BAD_REQUEST'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['VALIDATION_ERROR'],
                    'message': str(e)
                }
            }, cls=DecimalEncoder)
        }
    except Exception as e:
        logger.error(f"Add to cart error: {str(e)}", exc_info=True)
        logger.info("=== ADD TO CART HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['INTERNAL_ERROR'],
                    'message': str(e)
                }
            }, cls=DecimalEncoder)
        }

def handle_update_cart_item(event, product_id):
    """Handle PUT /cart/items/{product_id}"""
    logger.info("=== UPDATE CART ITEM HANDLER START ===")
    try:
        body = json.loads(event.get('body', '{}'))
        logger.info(f"Updating cart item with data: {json.dumps(body, default=str)}")
        
        customer_id = extract_user_id_from_request(event)
        if not customer_id:
            raise ValueError("User ID not found in request")
        logger.info(f"Updating cart item for customer ID: {customer_id}, product ID: {product_id}")
        
        # Validate required fields
        required_fields = REQUIRED_FIELDS['CART_UPDATE_ITEM']
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
                    }, cls=DecimalEncoder)
                }
                logger.info("=== UPDATE CART ITEM HANDLER END ===")
                return response
        
        quantity = int(body['quantity'])
        
        if quantity < 0:
            logger.warning("Quantity cannot be negative")
            response = {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Quantity cannot be negative'
                    }
                }, cls=DecimalEncoder)
            }
            logger.info("=== UPDATE CART ITEM HANDLER END ===")
            return response
        
        if quantity > CART_CONFIG['MAX_QUANTITY']:
            logger.warning(f"Quantity exceeds maximum limit of {CART_CONFIG['MAX_QUANTITY']}")
            response = {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': f'Quantity exceeds maximum limit of {CART_CONFIG["MAX_QUANTITY"]}'
                    }
                }, cls=DecimalEncoder)
            }
            logger.info("=== UPDATE CART ITEM HANDLER END ===")
            return response
        
        update_cart_item(customer_id, product_id, quantity)
        
        # Get updated cart
        cart_data = get_cart(customer_id)
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'message': 'Cart item updated successfully',
                'cart': cart_data
            }, cls=DecimalEncoder)
        }
        
        logger.info("=== UPDATE CART ITEM HANDLER END ===")
        return response
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        logger.info("=== UPDATE CART ITEM HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['BAD_REQUEST'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['VALIDATION_ERROR'],
                    'message': str(e)
                }
            }, cls=DecimalEncoder)
        }
    except Exception as e:
        logger.error(f"Update cart item error: {str(e)}", exc_info=True)
        logger.info("=== UPDATE CART ITEM HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['INTERNAL_ERROR'],
                    'message': str(e)
                }
            }, cls=DecimalEncoder)
        }

def handle_remove_from_cart(event, product_id):
    """Handle DELETE /cart/items/{product_id}"""
    logger.info("=== REMOVE FROM CART HANDLER START ===")
    try:
        customer_id = extract_user_id_from_request(event)
        if not customer_id:
            raise ValueError("User ID not found in request")
        logger.info(f"Removing item from cart for customer ID: {customer_id}, product ID: {product_id}")
        
        # Check if item exists before removing
        try:
            response = cart_table.get_item(
                Key={
                    'customer_id': customer_id,
                    'product_id': product_id
                }
            )
            existing_item = response.get('Item')
            
            if not existing_item:
                logger.warning(f"Cart item not found for customer: {customer_id}, product: {product_id}")
                return {
                    'statusCode': STATUS_CODES['NOT_FOUND'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['NOT_FOUND'],
                            'message': f'Cart item not found for product: {product_id}'
                        }
                    }, cls=DecimalEncoder)
                }
        except Exception as e:
            logger.error(f"Error checking cart item existence: {str(e)}")
            return {
                'statusCode': STATUS_CODES['INTERNAL_ERROR'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['INTERNAL_ERROR'],
                        'message': str(e)
                    }
                }, cls=DecimalEncoder)
            }
        
        remove_item_from_cart(customer_id, product_id)
        
        # Get updated cart
        cart_data = get_cart(customer_id)
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'message': 'Item removed from cart successfully',
                'cart': cart_data
            }, cls=DecimalEncoder)
        }
        
        logger.info("=== REMOVE FROM CART HANDLER END ===")
        return response
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        logger.info("=== REMOVE FROM CART HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['NOT_FOUND'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['NOT_FOUND'],
                    'message': str(e)
                }
            }, cls=DecimalEncoder)
        }
    except Exception as e:
        logger.error(f"Remove from cart error: {str(e)}", exc_info=True)
        logger.info("=== REMOVE FROM CART HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['INTERNAL_ERROR'],
                    'message': str(e)
                }
            }, cls=DecimalEncoder)
        }

def handle_clear_cart(event):
    """Handle DELETE /cart"""
    logger.info("=== CLEAR CART HANDLER START ===")
    try:
        customer_id = extract_user_id_from_request(event)
        if not customer_id:
            raise ValueError("User ID not found in request")
        logger.info(f"Clearing cart for customer ID: {customer_id}")
        
        clear_cart(customer_id)
        
        # Get empty cart data after clearing
        cart_data = get_cart(customer_id)
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'message': 'Cart cleared successfully',
                'cart': cart_data
            }, cls=DecimalEncoder)
        }
        
        logger.info("=== CLEAR CART HANDLER END ===")
        return response
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        logger.info("=== CLEAR CART HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['BAD_REQUEST'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['VALIDATION_ERROR'],
                    'message': str(e)
                }
            }, cls=DecimalEncoder)
        }
    except Exception as e:
        logger.error(f"Clear cart error: {str(e)}", exc_info=True)
        logger.info("=== CLEAR CART HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['INTERNAL_ERROR'],
                    'message': str(e)
                }
            }, cls=DecimalEncoder)
        }

def lambda_handler(event, context):
    """Main Lambda handler for cart operations"""
    logger.info(f"Cart Lambda handler called with event: {json.dumps(event, default=str)}")
    
    try:
        # Parse the request using the same structure as other handlers
        path = event.get('requestContext', {}).get('http', {}).get('path', '')
        method = event.get('requestContext', {}).get('http', {}).get('method', '')
        path_parameters = event.get('pathParameters', {})
        
        logger.info(f"HTTP Method: {method}, Path: {path}")
        
        # Route to appropriate handler
        # Handle both with and without stage prefix (/dev/cart or /cart)
        if (path == '/cart' or path.endswith('/cart')):
            if method == 'GET':
                logger.info("Routing to get cart handler")
                return handle_get_cart(event)
            elif method == 'DELETE':
                logger.info("Routing to clear cart handler")
                return handle_clear_cart(event)
            else:
                logger.warning(f"Method not allowed: {method} for /cart")
                return {
                    'statusCode': STATUS_CODES['METHOD_NOT_ALLOWED'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'], 'message': f'Method {method} not allowed for this endpoint'}})
                }
        elif (path == '/cart/items' or path.endswith('/cart/items')):
            if method == 'POST':
                logger.info("Routing to add to cart handler")
                return handle_add_to_cart(event)
            else:
                logger.warning(f"Method not allowed: {method} for /cart/items")
                return {
                    'statusCode': STATUS_CODES['METHOD_NOT_ALLOWED'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'], 'message': f'Method {method} not allowed for this endpoint'}})
                }
        elif '/cart/items/' in path:
            # Extract product_id from path, handling both /cart/items/{id} and /dev/cart/items/{id}
            path_parts = path.split('/')
            product_id = path_parts[-1]
            
            if method == 'PUT':
                logger.info(f"Routing to update cart item handler for product ID: {product_id}")
                return handle_update_cart_item(event, product_id)
            elif method == 'DELETE':
                logger.info(f"Routing to remove from cart handler for product ID: {product_id}")
                return handle_remove_from_cart(event, product_id)
            else:
                logger.warning(f"Method not allowed: {method} for /cart/items/{product_id}")
                return {
                    'statusCode': STATUS_CODES['METHOD_NOT_ALLOWED'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': {'code': ERROR_CODES['VALIDATION_ERROR'], 'message': f'Method {method} not allowed for this endpoint'}})
                }
        elif method == 'OPTIONS':
            return {
                'statusCode': STATUS_CODES['OK'],
                'headers': CORS_HEADERS,
                'body': ''
            }
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
        logger.error(f"Cart Lambda handler error: {str(e)}", exc_info=True)
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['INTERNAL_ERROR'],
                    'message': str(e)
                }
            }, cls=DecimalEncoder)
        } 