import json
import os
import boto3
import base64
import uuid
import logging
from datetime import datetime
import sys
sys.path.append('..')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize S3 client
s3_client = boto3.client('s3')

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
    'Access-Control-Allow-Headers': os.environ.get('CORS_HEADERS_ACCESS_CONTROL_HEADERS', 'Content-Type,Authorization'),
    'Access-Control-Allow-Methods': os.environ.get('CORS_HEADERS_ACCESS_CONTROL_METHODS', 'GET,POST,PUT,DELETE,OPTIONS')
}

# S3 Configuration
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'anna-akka-platform-images')
S3_BUCKET_REGION = os.environ.get('S3_BUCKET_REGION', 'ap-south-1')

# Allowed image types
ALLOWED_IMAGE_TYPES = {
    'image/jpeg': '.jpg',
    'image/jpg': '.jpg',
    'image/png': '.png',
    'image/gif': '.gif',
    'image/webp': '.webp'
}

# Maximum file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

def create_response(status_code, body, headers=None):
    """Create a standardized API response"""
    response_headers = CORS_HEADERS.copy()
    if headers:
        response_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': response_headers,
        'body': json.dumps(body, default=str)
    }

def validate_image_upload_request(body):
    """Validate the image upload request"""
    if not body:
        return False, "Request body is required"
    
    if 'image' not in body:
        return False, "Image data is required"
    
    if 'folder_path' not in body:
        return False, "Folder path is required"
    
    image_data = body['image']
    folder_path = body['folder_path']
    
    # Validate folder path
    if not folder_path or not isinstance(folder_path, str):
        return False, "Folder path must be a non-empty string"
    
    # Clean folder path (remove leading/trailing slashes)
    folder_path = folder_path.strip('/')
    
    # Validate image data
    if not image_data or not isinstance(image_data, str):
        return False, "Image data must be a base64 encoded string"
    
    try:
        # Decode base64 to check if it's valid
        decoded_data = base64.b64decode(image_data)
        
        # Check file size
        if len(decoded_data) > MAX_FILE_SIZE:
            return False, f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB"
        
        # Try to determine image type from the data
        # For now, we'll accept any base64 data and let S3 handle it
        # In a production environment, you might want to add more validation
        
    except Exception as e:
        return False, f"Invalid base64 image data: {str(e)}"
    
    return True, folder_path

def upload_image_to_s3(image_data, folder_path, file_extension='.jpg'):
    """Upload image to S3 and return the URL"""
    try:
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}{file_extension}"
        
        # Create full S3 key
        s3_key = f"{folder_path}/{filename}"
        
        # Decode base64 image data
        image_bytes = base64.b64decode(image_data)
        
        # Upload to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=image_bytes,
            ContentType='image/jpeg'  # Default to JPEG, can be made dynamic
        )
        
        # Generate the public URL
        image_url = f"https://{S3_BUCKET_NAME}.s3.{S3_BUCKET_REGION}.amazonaws.com/{s3_key}"
        
        logger.info(f"Image uploaded successfully to S3: {s3_key}")
        return image_url
        
    except Exception as e:
        logger.error(f"Error uploading image to S3: {str(e)}")
        raise e

def handle_upload_image(event, body):
    """Handle image upload request"""
    try:
        # Validate request
        is_valid, result = validate_image_upload_request(body)
        if not is_valid:
            return create_response(
                STATUS_CODES['BAD_REQUEST'],
                {
                    'error': ERROR_CODES['VALIDATION_ERROR'],
                    'message': result
                }
            )
        
        folder_path = result
        image_data = body['image']
        
        # Upload image to S3
        image_url = upload_image_to_s3(image_data, folder_path)
        
        return create_response(
            STATUS_CODES['CREATED'],
            {
                'message': 'Image uploaded successfully',
                'image_url': image_url,
                'folder_path': folder_path
            }
        )
        
    except Exception as e:
        logger.error(f"Error in handle_upload_image: {str(e)}")
        return create_response(
            STATUS_CODES['INTERNAL_ERROR'],
            {
                'error': ERROR_CODES['INTERNAL_ERROR'],
                'message': 'Internal server error'
            }
        )

def handler(event, context):
    """Main Lambda handler"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Get HTTP method from API Gateway v2 event structure
        http_method = event.get('requestContext', {}).get('http', {}).get('method', event.get('httpMethod', ''))
        
        # Handle CORS preflight requests
        if http_method == 'OPTIONS':
            return create_response(
                STATUS_CODES['OK'],
                {'message': 'CORS preflight response'}
            )
        
        # Only allow POST method
        if http_method != 'POST':
            return create_response(
                STATUS_CODES['METHOD_NOT_ALLOWED'],
                {
                    'error': ERROR_CODES['METHOD_NOT_ALLOWED'],
                    'message': 'Only POST method is allowed'
                }
            )
        
        # Parse request body
        body = None
        if event.get('body'):
            try:
                body = json.loads(event['body'])
            except json.JSONDecodeError:
                return create_response(
                    STATUS_CODES['BAD_REQUEST'],
                    {
                        'error': ERROR_CODES['VALIDATION_ERROR'],
                        'message': 'Invalid JSON in request body'
                    }
                )
        
        # Handle image upload
        return handle_upload_image(event, body)
        
    except Exception as e:
        logger.error(f"Unexpected error in handler: {str(e)}")
        return create_response(
            STATUS_CODES['INTERNAL_ERROR'],
            {
                'error': ERROR_CODES['INTERNAL_ERROR'],
                'message': 'Internal server error'
            }
        ) 