import json
import os
import boto3
from datetime import datetime
import uuid
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
categories_table = dynamodb.Table(os.environ['CATEGORIES_TABLE'])  # type: ignore

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

# Validation constants
MAX_NAME_LENGTH = 100
MAX_PAYLOAD_SIZE = 1024 * 1024  # 1MB

def get_all_categories():
    """Get all categories"""
    logger.info("Getting all categories")
    response = categories_table.scan()
    categories = response.get('Items', [])
    logger.info(f"Found {len(categories)} categories")
    return categories

def check_category_name_exists(name):
    """Check if a category with the given name already exists"""
    try:
        response = categories_table.scan(
            FilterExpression='#name = :name',
            ExpressionAttributeNames={'#name': 'name'},
            ExpressionAttributeValues={':name': name}
        )
        return len(response.get('Items', [])) > 0
    except Exception as e:
        logger.error(f"Error checking category name existence: {str(e)}")
        return False

def validate_category_name(name):
    """Validate category name"""
    if not name or not name.strip():
        raise ValueError("Category name is required")
    
    if len(name) > MAX_NAME_LENGTH:
        raise ValueError(f"Category name must be {MAX_NAME_LENGTH} characters or less")
    
    if check_category_name_exists(name):
        raise ValueError(f"Category with name '{name}' already exists")

def create_category(category_data):
    """Create a new category"""
    logger.info(f"Creating category with data: {json.dumps(category_data, default=str)}")
    
    # Validate category name
    validate_category_name(category_data['name'])
    
    category_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    category_item = {
        'id': category_id,
        'name': category_data['name'],
        'created_at': timestamp
    }
    
    logger.info(f"Category item to be created: {json.dumps(category_item, default=str)}")
    categories_table.put_item(Item=category_item)
    logger.info(f"Category created successfully with ID: {category_id}")
    return category_item

def get_category_by_id(category_id):
    """Get a category by ID"""
    logger.info(f"Getting category with ID: {category_id}")
    try:
        response = categories_table.get_item(Key={'id': category_id})
        category = response.get('Item')
        if not category:
            raise ValueError(f"Category with ID {category_id} not found")
        logger.info(f"Found category: {json.dumps(category, default=str)}")
        return category
    except Exception as e:
        logger.error(f"Error getting category by ID: {str(e)}")
        raise e

def update_category(category_id, category_data):
    """Update a category"""
    logger.info(f"Updating category with ID: {category_id}, data: {json.dumps(category_data, default=str)}")
    
    # Check if category exists
    existing_category = get_category_by_id(category_id)
    
    # Validate new name if provided
    if 'name' in category_data:
        new_name = category_data['name']
        if not new_name or not new_name.strip():
            raise ValueError("Category name is required")
        
        if len(new_name) > MAX_NAME_LENGTH:
            raise ValueError(f"Category name must be {MAX_NAME_LENGTH} characters or less")
        
        # Check if new name conflicts with existing category (excluding current category)
        try:
            response = categories_table.scan(
                FilterExpression='#name = :name AND #id <> :id',
                ExpressionAttributeNames={'#name': 'name', '#id': 'id'},
                ExpressionAttributeValues={':name': new_name, ':id': category_id}
            )
            if len(response.get('Items', [])) > 0:
                raise ValueError(f"Category with name '{new_name}' already exists")
        except Exception as e:
            logger.error(f"Error checking name conflict: {str(e)}")
            raise e
    
    # Update category
    update_expression = "SET updated_at = :updated_at"
    expression_values = {':updated_at': datetime.utcnow().isoformat()}
    
    if 'name' in category_data:
        update_expression += ", #name = :name"
        expression_values[':name'] = category_data['name']
    
    try:
        categories_table.update_item(
            Key={'id': category_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames={'#name': 'name'} if 'name' in category_data else {}
        )
        
        # Get updated category
        updated_category = get_category_by_id(category_id)
        logger.info(f"Category updated successfully: {json.dumps(updated_category, default=str)}")
        return updated_category
    except Exception as e:
        logger.error(f"Error updating category: {str(e)}")
        raise e

def delete_category(category_id):
    """Delete a category"""
    logger.info(f"Deleting category with ID: {category_id}")
    
    # Check if category exists
    existing_category = get_category_by_id(category_id)
    
    try:
        categories_table.delete_item(Key={'id': category_id})
        logger.info(f"Category deleted successfully: {category_id}")
        return existing_category
    except Exception as e:
        logger.error(f"Error deleting category: {str(e)}")
        raise e

def handler(event, context):
    """Main Lambda handler for categories"""
    logger.info("=== CATEGORIES HANDLER START ===")
    logger.info(f"Event: {json.dumps(event, default=str)}")
    logger.info(f"Context: {json.dumps({'function_name': context.function_name, 'function_version': context.function_version, 'invoked_function_arn': context.invoked_function_arn, 'memory_limit_in_mb': context.memory_limit_in_mb, 'remaining_time_in_millis': context.get_remaining_time_in_millis()}, default=str)}")
    
    try:
        # Parse the request
        path = event.get('requestContext', {}).get('http', {}).get('path', '')
        method = event.get('requestContext', {}).get('http', {}).get('method', '')
        path_parameters = event.get('pathParameters', {})
        
        logger.info(f"Request path: {path}")
        logger.info(f"Request method: {method}")
        logger.info(f"Path parameters: {path_parameters}")
        
        # Handle OPTIONS requests
        if method == 'OPTIONS':
            return {
                'statusCode': STATUS_CODES['OK'],
                'headers': CORS_HEADERS,
                'body': ''
            }
        
        # Parse body for POST/PUT requests
        body = {}
        if method in ['POST', 'PUT']:
            try:
                body_str = event.get('body', '{}')
                if len(body_str) > MAX_PAYLOAD_SIZE:
                    return {
                        'statusCode': STATUS_CODES['BAD_REQUEST'],
                        'headers': CORS_HEADERS,
                        'body': json.dumps({
                            'error': {
                                'code': ERROR_CODES['VALIDATION_ERROR'],
                                'message': 'Request payload too large'
                            }
                        })
                    }
                body = json.loads(body_str)
                logger.info(f"Request body: {json.dumps(body, default=str)}")
            except json.JSONDecodeError as e:
                logger.warning(f"Malformed JSON: {str(e)}")
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
        # Handle both with and without stage prefix (/dev/categories or /categories)
        if (path == '/categories' or path.endswith('/categories')):
            # Collection endpoints
            if method == 'GET':
                logger.info("Routing to get categories handler")
                response = handle_get_categories()
                logger.info(f"Get categories response: {json.dumps(response, default=str)}")
                return response
            elif method == 'POST':
                logger.info("Routing to create category handler")
                response = handle_create_category(body)
                logger.info(f"Create category response: {json.dumps(response, default=str)}")
                return response
            else:
                logger.warning(f"Method not allowed: {method} for /categories")
                return {
                    'statusCode': STATUS_CODES['METHOD_NOT_ALLOWED'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['VALIDATION_ERROR'],
                            'message': f'Method {method} not allowed for this endpoint'
                        }
                    })
                }
        elif '/categories/' in path:
            # Individual category endpoints
            # Extract category_id from path, handling both /categories/{id} and /dev/categories/{id}
            path_parts = path.split('/')
            category_id = path_parts[-1]
            
            if method == 'GET':
                logger.info(f"Routing to get category handler for ID: {category_id}")
                response = handle_get_category(category_id)
                logger.info(f"Get category response: {json.dumps(response, default=str)}")
                return response
            elif method == 'PUT':
                logger.info(f"Routing to update category handler for ID: {category_id}")
                response = handle_update_category(category_id, body)
                logger.info(f"Update category response: {json.dumps(response, default=str)}")
                return response
            elif method == 'DELETE':
                logger.info(f"Routing to delete category handler for ID: {category_id}")
                response = handle_delete_category(category_id)
                logger.info(f"Delete category response: {json.dumps(response, default=str)}")
                return response
            else:
                logger.warning(f"Method not allowed: {method} for /categories/{category_id}")
                return {
                    'statusCode': STATUS_CODES['METHOD_NOT_ALLOWED'],
                    'headers': CORS_HEADERS,
                    'body': json.dumps({
                        'error': {
                            'code': ERROR_CODES['VALIDATION_ERROR'],
                            'message': f'Method {method} not allowed for this endpoint'
                        }
                    })
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
        logger.info("=== CATEGORIES HANDLER END ===")

def handle_get_categories():
    """Handle GET /categories"""
    logger.info("=== GET CATEGORIES HANDLER START ===")
    try:
        logger.info("Getting all categories")
        categories = get_all_categories()
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'categories': categories})
        }
        
        logger.info("=== GET CATEGORIES HANDLER END ===")
        return response
        
    except Exception as e:
        logger.error(f"Get categories error: {str(e)}", exc_info=True)
        logger.info("=== GET CATEGORIES HANDLER END ===")
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

def handle_create_category(body):
    """Handle POST /categories"""
    logger.info("=== CREATE CATEGORY HANDLER START ===")
    try:
        logger.info(f"Creating category with data: {json.dumps(body, default=str)}")
        
        # Validate required fields
        if not body.get('name'):
            logger.warning("Missing required field: name")
            response = {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Category name is required'
                    }
                })
            }
            logger.info("=== CREATE CATEGORY HANDLER END ===")
            return response
        
        # Validate name length
        if len(body['name']) > MAX_NAME_LENGTH:
            logger.warning(f"Category name too long: {len(body['name'])} characters")
            response = {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': f'Category name must be {MAX_NAME_LENGTH} characters or less'
                    }
                })
            }
            logger.info("=== CREATE CATEGORY HANDLER END ===")
            return response
        
        logger.info("Category name provided, creating category")
        category = create_category(body)
        
        response = {
            'statusCode': STATUS_CODES['CREATED'],
            'headers': CORS_HEADERS,
            'body': json.dumps(category)
        }
        
        logger.info("=== CREATE CATEGORY HANDLER END ===")
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        # Check if it's a duplicate name error
        if "already exists" in str(e):
            status_code = STATUS_CODES['CONFLICT']
            error_code = ERROR_CODES['CONFLICT']
        else:
            status_code = STATUS_CODES['BAD_REQUEST']
            error_code = ERROR_CODES['VALIDATION_ERROR']
        
        response = {
            'statusCode': status_code,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': error_code,
                    'message': str(e)
                }
            })
        }
        logger.info("=== CREATE CATEGORY HANDLER END ===")
        return response
        
    except Exception as e:
        logger.error(f"Create category error: {str(e)}", exc_info=True)
        logger.info("=== CREATE CATEGORY HANDLER END ===")
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

def handle_get_category(category_id):
    """Handle GET /categories/{id}"""
    logger.info("=== GET CATEGORY HANDLER START ===")
    try:
        logger.info(f"Getting category with ID: {category_id}")
        category = get_category_by_id(category_id)
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps(category)
        }
        
        logger.info("=== GET CATEGORY HANDLER END ===")
        return response
        
    except ValueError as e:
        logger.warning(f"Category not found: {str(e)}")
        logger.info("=== GET CATEGORY HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['NOT_FOUND'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['NOT_FOUND'],
                    'message': str(e)
                }
            })
        }
    except Exception as e:
        logger.error(f"Get category error: {str(e)}", exc_info=True)
        logger.info("=== GET CATEGORY HANDLER END ===")
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

def handle_update_category(category_id, body):
    """Handle PUT /categories/{id}"""
    logger.info("=== UPDATE CATEGORY HANDLER START ===")
    try:
        logger.info(f"Updating category with ID: {category_id}, data: {json.dumps(body, default=str)}")
        
        # Validate required fields
        if not body.get('name'):
            logger.warning("Missing required field: name")
            response = {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Category name is required'
                    }
                })
            }
            logger.info("=== UPDATE CATEGORY HANDLER END ===")
            return response
        
        # Validate name length
        if len(body['name']) > MAX_NAME_LENGTH:
            logger.warning(f"Category name too long: {len(body['name'])} characters")
            response = {
                'statusCode': STATUS_CODES['BAD_REQUEST'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['VALIDATION_ERROR'],
                        'message': f'Category name must be {MAX_NAME_LENGTH} characters or less'
                    }
                })
            }
            logger.info("=== UPDATE CATEGORY HANDLER END ===")
            return response
        
        logger.info("Category name provided, updating category")
        updated_category = update_category(category_id, body)
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps(updated_category)
        }
        
        logger.info("=== UPDATE CATEGORY HANDLER END ===")
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        # Check if it's a not found error
        if "not found" in str(e):
            status_code = STATUS_CODES['NOT_FOUND']
            error_code = ERROR_CODES['NOT_FOUND']
        elif "already exists" in str(e):
            status_code = STATUS_CODES['CONFLICT']
            error_code = ERROR_CODES['CONFLICT']
        else:
            status_code = STATUS_CODES['BAD_REQUEST']
            error_code = ERROR_CODES['VALIDATION_ERROR']
        
        response = {
            'statusCode': status_code,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': error_code,
                    'message': str(e)
                }
            })
        }
        logger.info("=== UPDATE CATEGORY HANDLER END ===")
        return response
        
    except Exception as e:
        logger.error(f"Update category error: {str(e)}", exc_info=True)
        logger.info("=== UPDATE CATEGORY HANDLER END ===")
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

def handle_delete_category(category_id):
    """Handle DELETE /categories/{id}"""
    logger.info("=== DELETE CATEGORY HANDLER START ===")
    try:
        logger.info(f"Deleting category with ID: {category_id}")
        deleted_category = delete_category(category_id)
        
        response = {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'message': 'Category deleted successfully',
                'deleted_category': deleted_category
            })
        }
        
        logger.info("=== DELETE CATEGORY HANDLER END ===")
        return response
        
    except ValueError as e:
        logger.warning(f"Category not found: {str(e)}")
        logger.info("=== DELETE CATEGORY HANDLER END ===")
        return {
            'statusCode': STATUS_CODES['NOT_FOUND'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['NOT_FOUND'],
                    'message': str(e)
                }
            })
        }
    except Exception as e:
        logger.error(f"Delete category error: {str(e)}", exc_info=True)
        logger.info("=== DELETE CATEGORY HANDLER END ===")
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