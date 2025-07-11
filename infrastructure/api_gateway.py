"""
API Gateway Infrastructure Module
Handles API Gateway, integrations, routes, and permissions
"""

import pulumi
import pulumi_aws as aws

def create_api_gateway_infrastructure(project_name: str, environment: str, lambda_functions):
    """Create API Gateway and all integrations"""
    
    # API Gateway
    api_gateway = aws.apigatewayv2.Api(f"{project_name}-api",
        name=f"{project_name}-api",
        protocol_type="HTTP",
        cors_configuration={
            "allow_origins": ["*"],
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["*"],
        },
        tags={
            "Name": f"{project_name}-api",
            "Environment": environment,
        }
    )

    # API Gateway Stage
    api_stage = aws.apigatewayv2.Stage(f"{project_name}-stage",
        api_id=api_gateway.id,
        name=environment,
        auto_deploy=True,
        tags={
            "Name": f"{project_name}-stage",
            "Environment": environment,
        }
    )

    # Create integrations for all lambda functions
    integrations = {}
    for name, lambda_func in lambda_functions.items():
        integration_name = f"{project_name}-{name}-integration"
        integrations[name] = aws.apigatewayv2.Integration(integration_name,
            api_id=api_gateway.id,
            integration_type="AWS_PROXY",
            integration_uri=lambda_func.invoke_arn,
            integration_method="POST",
            payload_format_version="2.0",
        )

    # Create routes
    routes = create_all_routes(project_name, api_gateway, integrations)
    
    # Create permissions
    permissions = create_lambda_permissions(project_name, api_gateway, lambda_functions)

    return {
        "api_gateway": api_gateway,
        "api_stage": api_stage,
        "integrations": integrations,
        "routes": routes,
        "permissions": permissions
    }

def create_all_routes(project_name: str, api_gateway, integrations):
    """Create all API Gateway routes"""
    
    routes = {}
    
    # Auth routes
    routes["auth_post"] = aws.apigatewayv2.Route(f"{project_name}-auth-post-route",
        api_id=api_gateway.id,
        route_key="POST /auth",
        target=integrations["auth_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["auth_get"] = aws.apigatewayv2.Route(f"{project_name}-auth-get-route",
        api_id=api_gateway.id,
        route_key="GET /auth",
        target=integrations["auth_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["auth_put"] = aws.apigatewayv2.Route(f"{project_name}-auth-put-route",
        api_id=api_gateway.id,
        route_key="PUT /auth",
        target=integrations["auth_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["auth_delete"] = aws.apigatewayv2.Route(f"{project_name}-auth-delete-route",
        api_id=api_gateway.id,
        route_key="DELETE /auth",
        target=integrations["auth_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )

    # OTP routes
    routes["otp_send"] = aws.apigatewayv2.Route(f"{project_name}-otp-send-route",
        api_id=api_gateway.id,
        route_key="POST /auth/otp/send",
        target=integrations["otp_auth_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["otp_verify"] = aws.apigatewayv2.Route(f"{project_name}-otp-verify-route",
        api_id=api_gateway.id,
        route_key="POST /auth/otp/verify",
        target=integrations["otp_auth_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )

    # Profile routes
    routes["profile_get"] = aws.apigatewayv2.Route(f"{project_name}-profile-get-route",
        api_id=api_gateway.id,
        route_key="GET /profile",
        target=integrations["profile_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["profile_put"] = aws.apigatewayv2.Route(f"{project_name}-profile-put-route",
        api_id=api_gateway.id,
        route_key="PUT /profile",
        target=integrations["profile_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )

    # Categories routes
    routes["categories_get"] = aws.apigatewayv2.Route(f"{project_name}-categories-get-route",
        api_id=api_gateway.id,
        route_key="GET /categories",
        target=integrations["categories_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["categories_post"] = aws.apigatewayv2.Route(f"{project_name}-categories-post-route",
        api_id=api_gateway.id,
        route_key="POST /categories",
        target=integrations["categories_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )

    # Stores routes
    routes["stores_get"] = aws.apigatewayv2.Route(f"{project_name}-stores-get-route",
        api_id=api_gateway.id,
        route_key="GET /stores",
        target=integrations["stores_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["stores_post"] = aws.apigatewayv2.Route(f"{project_name}-stores-post-route",
        api_id=api_gateway.id,
        route_key="POST /stores",
        target=integrations["stores_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["stores_get_by_id"] = aws.apigatewayv2.Route(f"{project_name}-stores-get-by-id-route",
        api_id=api_gateway.id,
        route_key="GET /stores/{proxy+}",
        target=integrations["stores_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["stores_put"] = aws.apigatewayv2.Route(f"{project_name}-stores-put-route",
        api_id=api_gateway.id,
        route_key="PUT /stores/{proxy+}",
        target=integrations["stores_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["stores_delete"] = aws.apigatewayv2.Route(f"{project_name}-stores-delete-route",
        api_id=api_gateway.id,
        route_key="DELETE /stores/{proxy+}",
        target=integrations["stores_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )

    # Products routes
    routes["products_get"] = aws.apigatewayv2.Route(f"{project_name}-products-get-route",
        api_id=api_gateway.id,
        route_key="GET /products",
        target=integrations["products_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["products_post"] = aws.apigatewayv2.Route(f"{project_name}-products-post-route",
        api_id=api_gateway.id,
        route_key="POST /products",
        target=integrations["products_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["products_get_by_id"] = aws.apigatewayv2.Route(f"{project_name}-products-get-by-id-route",
        api_id=api_gateway.id,
        route_key="GET /products/{proxy+}",
        target=integrations["products_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["products_put"] = aws.apigatewayv2.Route(f"{project_name}-products-put-route",
        api_id=api_gateway.id,
        route_key="PUT /products/{proxy+}",
        target=integrations["products_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["products_delete"] = aws.apigatewayv2.Route(f"{project_name}-products-delete-route",
        api_id=api_gateway.id,
        route_key="DELETE /products/{proxy+}",
        target=integrations["products_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )

    # Store Products routes
    routes["stores_products_get"] = aws.apigatewayv2.Route(f"{project_name}-stores-products-get-route",
        api_id=api_gateway.id,
        route_key="GET /stores/{store_id}/products",
        target=integrations["products_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["stores_products_post"] = aws.apigatewayv2.Route(f"{project_name}-stores-products-post-route",
        api_id=api_gateway.id,
        route_key="POST /stores/{store_id}/products",
        target=integrations["products_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )

    # Available Products routes
    routes["available_products_get"] = aws.apigatewayv2.Route(f"{project_name}-available-products-get-route",
        api_id=api_gateway.id,
        route_key="GET /available-products",
        target=integrations["available_products_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["available_products_post"] = aws.apigatewayv2.Route(f"{project_name}-available-products-post-route",
        api_id=api_gateway.id,
        route_key="POST /available-products",
        target=integrations["available_products_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["available_products_get_by_id"] = aws.apigatewayv2.Route(f"{project_name}-available-products-get-by-id-route",
        api_id=api_gateway.id,
        route_key="GET /available-products/{proxy+}",
        target=integrations["available_products_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["available_products_put"] = aws.apigatewayv2.Route(f"{project_name}-available-products-put-route",
        api_id=api_gateway.id,
        route_key="PUT /available-products/{proxy+}",
        target=integrations["available_products_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["available_products_delete"] = aws.apigatewayv2.Route(f"{project_name}-available-products-delete-route",
        api_id=api_gateway.id,
        route_key="DELETE /available-products/{proxy+}",
        target=integrations["available_products_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )

    # Orders routes
    routes["orders_get"] = aws.apigatewayv2.Route(f"{project_name}-orders-get-route",
        api_id=api_gateway.id,
        route_key="GET /orders",
        target=integrations["orders_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["orders_post"] = aws.apigatewayv2.Route(f"{project_name}-orders-post-route",
        api_id=api_gateway.id,
        route_key="POST /orders",
        target=integrations["orders_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["orders_get_by_id"] = aws.apigatewayv2.Route(f"{project_name}-orders-get-by-id-route",
        api_id=api_gateway.id,
        route_key="GET /orders/{proxy+}",
        target=integrations["orders_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["orders_put"] = aws.apigatewayv2.Route(f"{project_name}-orders-put-route",
        api_id=api_gateway.id,
        route_key="PUT /orders/{proxy+}",
        target=integrations["orders_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )

    # Cart routes
    routes["cart_get"] = aws.apigatewayv2.Route(f"{project_name}-cart-get-route",
        api_id=api_gateway.id,
        route_key="GET /cart",
        target=integrations["cart_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["cart_items_post"] = aws.apigatewayv2.Route(f"{project_name}-cart-items-post-route",
        api_id=api_gateway.id,
        route_key="POST /cart/items",
        target=integrations["cart_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["cart_items_put"] = aws.apigatewayv2.Route(f"{project_name}-cart-items-put-route",
        api_id=api_gateway.id,
        route_key="PUT /cart/items/{proxy+}",
        target=integrations["cart_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["cart_items_delete"] = aws.apigatewayv2.Route(f"{project_name}-cart-items-delete-route",
        api_id=api_gateway.id,
        route_key="DELETE /cart/items/{proxy+}",
        target=integrations["cart_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )
    
    routes["cart_delete"] = aws.apigatewayv2.Route(f"{project_name}-cart-delete-route",
        api_id=api_gateway.id,
        route_key="DELETE /cart",
        target=integrations["cart_lambda"].id.apply(lambda id: f"integrations/{id}"),
    )

    return routes

def create_lambda_permissions(project_name: str, api_gateway, lambda_functions):
    """Create Lambda permissions for API Gateway"""
    
    permissions = {}
    
    for name, lambda_func in lambda_functions.items():
        permission_name = f"{project_name}-{name}-permission"
        permissions[name] = aws.lambda_.Permission(permission_name,
            action="lambda:InvokeFunction",
            function=lambda_func.name,
            principal="apigateway.amazonaws.com",
            source_arn=api_gateway.execution_arn.apply(lambda arn: f"{arn}/*/*"),
        )
    
    return permissions 