# DynamoDB Table Names
USERS_TABLE = 'USERS_TABLE'
STORES_TABLE = 'STORES_TABLE'
CATEGORIES_TABLE = 'CATEGORIES_TABLE'
PRODUCTS_TABLE = 'PRODUCTS_TABLE'
ORDERS_TABLE = 'ORDERS_TABLE'
ORDER_ITEMS_TABLE = 'ORDER_ITEMS_TABLE'

# Environment Variables
ENVIRONMENT = 'ENVIRONMENT'

# Error Codes
ERROR_CODES = {
    'VALIDATION_ERROR': 'VALIDATION_ERROR',
    'UNAUTHORIZED': 'UNAUTHORIZED',
    'FORBIDDEN': 'FORBIDDEN',
    'NOT_FOUND': 'NOT_FOUND',
    'CONFLICT': 'CONFLICT',
    'UNPROCESSABLE_ENTITY': 'UNPROCESSABLE_ENTITY',
    'INTERNAL_ERROR': 'INTERNAL_ERROR'
}

# HTTP Status Codes
STATUS_CODES = {
    'OK': 200,
    'CREATED': 201,
    'NO_CONTENT': 204,
    'BAD_REQUEST': 400,
    'UNAUTHORIZED': 401,
    'FORBIDDEN': 403,
    'NOT_FOUND': 404,
    'CONFLICT': 409,
    'UNPROCESSABLE_ENTITY': 422,
    'INTERNAL_ERROR': 500
}

# Order Status Values
ORDER_STATUS = {
    'PENDING': 'pending',
    'PREPARING': 'preparing',
    'READY': 'ready',
    'DELIVERED': 'delivered',
    'CANCELLED': 'cancelled'
}

# User Types
USER_TYPES = {
    'CUSTOMER': 'customer',
    'OWNER': 'owner'
}

# Default Values
DEFAULT_VALUES = {
    'DELIVERY_TIME': '30-45 min',
    'PRODUCT_UNIT': 'piece',
    'PRODUCT_STOCK': 0,
    'STORE_RATING': 0,
    'STORE_IS_OPEN': True
}

# API Headers
HEADERS = {
    'CONTENT_TYPE': 'Content-Type',
    'ACCESS_CONTROL_ORIGIN': 'Access-Control-Allow-Origin',
    'ACCESS_CONTROL_HEADERS': 'Access-Control-Allow-Headers',
    'ACCESS_CONTROL_METHODS': 'Access-Control-Allow-Methods',
    'AUTHORIZATION': 'Authorization'
}

# CORS Headers
CORS_HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
}

# DynamoDB Index Names
INDEX_NAMES = {
    'OWNER_ID_INDEX': 'owner_id_index',
    'STORE_ID_INDEX': 'store_id_index',
    'CATEGORY_ID_INDEX': 'category_id_index',
    'CUSTOMER_ID_INDEX': 'customer_id_index',
    'STATUS_INDEX': 'status_index',
    'ORDER_ID_INDEX': 'order_id_index'
}

# Required Fields for Validation
REQUIRED_FIELDS = {
    'USER_REGISTER': ['email', 'password', 'name'],
    'STORE_CREATE': ['name', 'address'],
    'PRODUCT_CREATE': ['name', 'price'],
    'ORDER_CREATE': ['store_id', 'delivery_address', 'items'],
    'CATEGORY_CREATE': ['name']
}

# Allowed Update Fields
ALLOWED_UPDATE_FIELDS = {
    'USER_PROFILE': ['name', 'phone', 'address'],
    'STORE': ['name', 'address', 'phone', 'is_open', 'delivery_time'],
    'PRODUCT': ['name', 'description', 'price', 'unit', 'stock', 'image_url', 'category_id']
}

# Pagination Defaults
PAGINATION_DEFAULTS = {
    'STORES_PAGE': 1,
    'STORES_LIMIT': 10,
    'PRODUCTS_PAGE': 1,
    'PRODUCTS_LIMIT': 20,
    'ORDERS_PAGE': 1,
    'ORDERS_LIMIT': 10
}

# Analytics Periods
ANALYTICS_PERIODS = {
    'DAY': 'day',
    'WEEK': 'week',
    'MONTH': 'month',
    'YEAR': 'year'
}

# Mock Values (for development)
MOCK_VALUES = {
    'USER_ID': 'mock-user-id',
    'OWNER_ID': 'mock-owner-id',
    'STORE_ID': 'mock-store-id',
    'CUSTOMER_ID': 'mock-customer-id'
} 