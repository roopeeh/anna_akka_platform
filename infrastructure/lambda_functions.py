"""
Lambda Functions Infrastructure Module
Handles Lambda functions and their configurations
"""

import pulumi
import pulumi_aws as aws

def create_lambda_function(name, handler, lambda_role, vpc_config, environment_vars=None):
    """Create a Lambda function with standard configuration"""
    env_vars = {
        "ENVIRONMENT": environment_vars.get("ENVIRONMENT", "dev"),
        "USERS_TABLE": environment_vars.get("USERS_TABLE", ""),
        "AVAILABLE_PRODUCTS_TABLE": environment_vars.get("AVAILABLE_PRODUCTS_TABLE", ""),
        "STORES_TABLE": environment_vars.get("STORES_TABLE", ""),
        "CATEGORIES_TABLE": environment_vars.get("CATEGORIES_TABLE", ""),
        "PRODUCTS_TABLE": environment_vars.get("PRODUCTS_TABLE", ""),
        "ORDERS_TABLE": environment_vars.get("ORDERS_TABLE", ""),
        "ORDER_ITEMS_TABLE": environment_vars.get("ORDER_ITEMS_TABLE", ""),
        "CART_TABLE": environment_vars.get("CART_TABLE", ""),
        # Add constants as environment variables
        "ERROR_CODES_VALIDATION_ERROR": "VALIDATION_ERROR",
        "ERROR_CODES_UNAUTHORIZED": "UNAUTHORIZED",
        "ERROR_CODES_FORBIDDEN": "FORBIDDEN",
        "ERROR_CODES_NOT_FOUND": "NOT_FOUND",
        "ERROR_CODES_CONFLICT": "CONFLICT",
        "ERROR_CODES_UNPROCESSABLE_ENTITY": "UNPROCESSABLE_ENTITY",
        "ERROR_CODES_INTERNAL_ERROR": "INTERNAL_ERROR",
        "STATUS_CODES_OK": "200",
        "STATUS_CODES_CREATED": "201",
        "STATUS_CODES_NO_CONTENT": "204",
        "STATUS_CODES_BAD_REQUEST": "400",
        "STATUS_CODES_UNAUTHORIZED": "401",
        "STATUS_CODES_FORBIDDEN": "403",
        "STATUS_CODES_NOT_FOUND": "404",
        "STATUS_CODES_CONFLICT": "409",
        "STATUS_CODES_UNPROCESSABLE_ENTITY": "422",
        "STATUS_CODES_INTERNAL_ERROR": "500",
        "USER_TYPES_CUSTOMER": "customer",
        "USER_TYPES_OWNER": "owner",
        "ORDER_STATUS_PENDING": "pending",
        "ORDER_STATUS_PREPARING": "preparing",
        "ORDER_STATUS_READY": "ready",
        "ORDER_STATUS_DELIVERED": "delivered",
        "ORDER_STATUS_CANCELLED": "cancelled",
        "DEFAULT_VALUES_DELIVERY_TIME": "30-45 min",
        "DEFAULT_VALUES_PRODUCT_UNIT": "piece",
        "DEFAULT_VALUES_PRODUCT_STOCK": "0",
        "DEFAULT_VALUES_STORE_RATING": "0",
        "DEFAULT_VALUES_STORE_IS_OPEN": "true",
        "CORS_HEADERS_CONTENT_TYPE": "application/json",
        "CORS_HEADERS_ACCESS_CONTROL_ORIGIN": "*",
        "CORS_HEADERS_ACCESS_CONTROL_HEADERS": "Content-Type,Authorization",
        "CORS_HEADERS_ACCESS_CONTROL_METHODS": "GET,POST,PUT,DELETE,OPTIONS",
        "INDEX_NAMES_OWNER_ID_INDEX": "owner_id_index",
        "INDEX_NAMES_STORE_ID_INDEX": "store_id_index",
        "INDEX_NAMES_CATEGORY_ID_INDEX": "category_id_index",
        "INDEX_NAMES_CUSTOMER_ID_INDEX": "customer_id_index",
        "INDEX_NAMES_STATUS_INDEX": "status_index",
        "INDEX_NAMES_ORDER_ID_INDEX": "order_id_index",
        "MOCK_VALUES_USER_ID": "mock-user-id",
        "MOCK_VALUES_OWNER_ID": "mock-owner-id",
        "MOCK_VALUES_STORE_ID": "mock-store-id",
        "MOCK_VALUES_CUSTOMER_ID": "mock-customer-id",
    }
    if environment_vars:
        env_vars.update(environment_vars)
    
    return aws.lambda_.Function(f"anna-akka-platform-{name}",
        name=f"anna-akka-platform-{name}",
        runtime="python3.9",
        handler=handler,
        role=lambda_role.arn,
        code=pulumi.AssetArchive({
            ".": pulumi.FileArchive(f"./lambda_functions/{name}"),
            "constants.py": pulumi.FileAsset("./lambda_functions/constants.py"),
        }),
        timeout=30,
        memory_size=512,
        environment={
            "variables": env_vars,
        },
        vpc_config=vpc_config,
        tags={
            "Name": f"anna-akka-platform-{name}",
            "Environment": environment_vars.get("ENVIRONMENT", "dev"),
        }
    )

def create_all_lambda_functions(project_name: str, environment: str, lambda_role, vpc_config, tables, cognito_resources):
    """Create all Lambda functions"""
    
    # Environment variables for all functions
    env_vars = {
        "ENVIRONMENT": environment,
        "USERS_TABLE": tables["users_table"].name,
        "AVAILABLE_PRODUCTS_TABLE": tables["available_products_table"].name,
        "STORES_TABLE": tables["stores_table"].name,
        "CATEGORIES_TABLE": tables["categories_table"].name,
        "PRODUCTS_TABLE": tables["products_table"].name,
        "ORDERS_TABLE": tables["orders_table"].name,
        "ORDER_ITEMS_TABLE": tables["order_items_table"].name,
        "CART_TABLE": tables["cart_table"].name,
    }
    
    # Create Lambda functions
    auth_lambda = create_lambda_function("auth", "handler.handler", lambda_role, vpc_config, env_vars)
    
    otp_auth_lambda = create_lambda_function("otp_auth", "handler.lambda_handler", lambda_role, vpc_config, {
        **env_vars,
        "COGNITO_USER_POOL_ID": cognito_resources["cognito_user_pool"].id,
        "COGNITO_CLIENT_ID": cognito_resources["cognito_user_pool_client"].id,
    })
    
    profile_lambda = create_lambda_function("profile", "handler.handler", lambda_role, vpc_config, env_vars)
    categories_lambda = create_lambda_function("categories", "handler.handler", lambda_role, vpc_config, env_vars)
    stores_lambda = create_lambda_function("stores", "handler.handler", lambda_role, vpc_config, env_vars)
    products_lambda = create_lambda_function("products", "handler.handler", lambda_role, vpc_config, env_vars)
    available_products_lambda = create_lambda_function("available_products", "handler.handler", lambda_role, vpc_config, env_vars)
    orders_lambda = create_lambda_function("orders", "handler.handler", lambda_role, vpc_config, env_vars)
    cart_lambda = create_lambda_function("cart", "handler.lambda_handler", lambda_role, vpc_config, env_vars)
    
    return {
        "auth_lambda": auth_lambda,
        "otp_auth_lambda": otp_auth_lambda,
        "profile_lambda": profile_lambda,
        "categories_lambda": categories_lambda,
        "stores_lambda": stores_lambda,
        "products_lambda": products_lambda,
        "available_products_lambda": available_products_lambda,
        "orders_lambda": orders_lambda,
        "cart_lambda": cart_lambda
    } 