import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx
import pulumi_random as random
import json
import os

# Configuration
config = pulumi.Config()
environment = config.get("environment") or "dev"
project_name = "anna-akka-platform"

# VPC and Networking
vpc = awsx.ec2.Vpc(f"{project_name}-vpc",
    cidr_block="10.0.0.0/16",
    number_of_availability_zones=2,
    subnet_specs=[
        awsx.ec2.SubnetSpecArgs(
            type=awsx.ec2.SubnetType.PRIVATE,
            cidr_mask=24,
        ),
        awsx.ec2.SubnetSpecArgs(
            type=awsx.ec2.SubnetType.PUBLIC,
            cidr_mask=24,
        ),
    ],
    tags={
        "Name": f"{project_name}-vpc",
        "Environment": environment,
    }
)

# Security Group for Lambda
lambda_sg = aws.ec2.SecurityGroup(f"{project_name}-lambda-sg",
    vpc_id=vpc.vpc_id,
    description="Security group for Lambda functions",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=443,
            to_port=443,
            cidr_blocks=["0.0.0.0/0"],
            description="HTTPS outbound"
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags={
        "Name": f"{project_name}-lambda-sg",
        "Environment": environment,
    }
)

# DynamoDB Tables
users_table = aws.dynamodb.Table(f"{project_name}-users",
    attributes=[
        aws.dynamodb.TableAttributeArgs(
            name="id",
            type="S",
        ),
    ],
    hash_key="id",
    billing_mode="PAY_PER_REQUEST",
    tags={
        "Name": f"{project_name}-users",
        "Environment": environment,
    }
)

stores_table = aws.dynamodb.Table(f"{project_name}-stores",
    attributes=[
        aws.dynamodb.TableAttributeArgs(
            name="id",
            type="S",
        ),
        aws.dynamodb.TableAttributeArgs(
            name="owner_id",
            type="S",
        ),
    ],
    hash_key="id",
    global_secondary_indexes=[{
        "name": "owner_id_index",
        "hash_key": "owner_id",
        "projection_type": "ALL",
    }],
    billing_mode="PAY_PER_REQUEST",
    tags={
        "Name": f"{project_name}-stores",
        "Environment": environment,
    }
)

categories_table = aws.dynamodb.Table(f"{project_name}-categories",
    attributes=[
        aws.dynamodb.TableAttributeArgs(
            name="id",
            type="S",
        ),
    ],
    hash_key="id",
    billing_mode="PAY_PER_REQUEST",
    tags={
        "Name": f"{project_name}-categories",
        "Environment": environment,
    }
)

products_table = aws.dynamodb.Table(f"{project_name}-products",
    attributes=[
        aws.dynamodb.TableAttributeArgs(
            name="id",
            type="S",
        ),
        aws.dynamodb.TableAttributeArgs(
            name="store_id",
            type="S",
        ),
        aws.dynamodb.TableAttributeArgs(
            name="category_id",
            type="S",
        ),
    ],
    hash_key="id",
    global_secondary_indexes=[
        {
            "name": "store_id_index",
            "hash_key": "store_id",
            "projection_type": "ALL",
        },
        {
            "name": "category_id_index",
            "hash_key": "category_id",
            "projection_type": "ALL",
        },
    ],
    billing_mode="PAY_PER_REQUEST",
    tags={
        "Name": f"{project_name}-products",
        "Environment": environment,
    }
)

orders_table = aws.dynamodb.Table(f"{project_name}-orders",
    attributes=[
        aws.dynamodb.TableAttributeArgs(
            name="id",
            type="S",
        ),
        aws.dynamodb.TableAttributeArgs(
            name="customer_id",
            type="S",
        ),
        aws.dynamodb.TableAttributeArgs(
            name="store_id",
            type="S",
        ),
        aws.dynamodb.TableAttributeArgs(
            name="status",
            type="S",
        ),
    ],
    hash_key="id",
    global_secondary_indexes=[
        {
            "name": "customer_id_index",
            "hash_key": "customer_id",
            "projection_type": "ALL",
        },
        {
            "name": "store_id_index",
            "hash_key": "store_id",
            "projection_type": "ALL",
        },
        {
            "name": "status_index",
            "hash_key": "status",
            "projection_type": "ALL",
        },
    ],
    billing_mode="PAY_PER_REQUEST",
    tags={
        "Name": f"{project_name}-orders",
        "Environment": environment,
    }
)

order_items_table = aws.dynamodb.Table(f"{project_name}-order-items",
    attributes=[
        aws.dynamodb.TableAttributeArgs(
            name="id",
            type="S",
        ),
        aws.dynamodb.TableAttributeArgs(
            name="order_id",
            type="S",
        ),
    ],
    hash_key="id",
    global_secondary_indexes=[{
        "name": "order_id_index",
        "hash_key": "order_id",
        "projection_type": "ALL",
    }],
    billing_mode="PAY_PER_REQUEST",
    tags={
        "Name": f"{project_name}-order-items",
        "Environment": environment,
    }
)

# IAM Role for Lambda
lambda_role = aws.iam.Role(f"{project_name}-lambda-role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com",
            },
        }],
    }),
    tags={
        "Name": f"{project_name}-lambda-role",
        "Environment": environment,
    }
)

# Attach policies to Lambda role
lambda_basic_policy = aws.iam.RolePolicyAttachment(f"{project_name}-lambda-basic",
    role=lambda_role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
)
lambda_vpc_policy = aws.iam.RolePolicyAttachment(f"{project_name}-lambda-vpc",
    role=lambda_role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
)

# DynamoDB policy
dynamodb_policy = aws.iam.Policy(f"{project_name}-dynamodb-policy",
    policy=pulumi.Output.all(
        users_table.arn,
        stores_table.arn,
        categories_table.arn,
        products_table.arn,
        orders_table.arn,
        order_items_table.arn
    ).apply(lambda arns: json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                ],
                "Resource": [
                    arns[0],
                    arns[1],
                    arns[2],
                    arns[3],
                    arns[4],
                    arns[5],
                    f"{arns[0]}/index/*",
                    f"{arns[1]}/index/*",
                    f"{arns[3]}/index/*",
                    f"{arns[4]}/index/*",
                    f"{arns[5]}/index/*",
                ],
            },
        ],
    })),
    tags={
        "Name": f"{project_name}-dynamodb-policy",
        "Environment": environment,
    }
)
lambda_dynamodb_policy_attachment = aws.iam.RolePolicyAttachment(f"{project_name}-lambda-dynamodb",
    role=lambda_role.name,
    policy_arn=dynamodb_policy.arn
)

def create_lambda_function(name, handler, environment_vars=None):
    env_vars = {
        "ENVIRONMENT": environment,
        "USERS_TABLE": users_table.name,
        "STORES_TABLE": stores_table.name,
        "CATEGORIES_TABLE": categories_table.name,
        "PRODUCTS_TABLE": products_table.name,
        "ORDERS_TABLE": orders_table.name,
        "ORDER_ITEMS_TABLE": order_items_table.name,
    }
    if environment_vars:
        env_vars.update(environment_vars)
    return aws.lambda_.Function(f"{project_name}-{name}",
        runtime="python3.9",
        handler=handler,
        role=lambda_role.arn,
        code=pulumi.AssetArchive({
            ".": pulumi.FileArchive(f"./lambda_functions/{name}"),
        }),
        timeout=30,
        memory_size=512,
        environment={
            "variables": env_vars,
        },
        vpc_config={
            "subnet_ids": vpc.private_subnet_ids,
            "security_group_ids": [lambda_sg.id],
        },
        tags={
            "Name": f"{project_name}-{name}",
            "Environment": environment,
        }
    )

# Create Lambda functions
auth_lambda = create_lambda_function("auth", "auth.handler")
profile_lambda = create_lambda_function("profile", "profile.handler")
stores_lambda = create_lambda_function("stores", "stores.handler")
categories_lambda = create_lambda_function("categories", "categories.handler")
products_lambda = create_lambda_function("products", "products.handler")
orders_lambda = create_lambda_function("orders", "orders.handler")
analytics_lambda = create_lambda_function("analytics", "analytics.handler")

# API Gateway
api_gateway = aws.apigatewayv2.Api(f"{project_name}-api",
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

def create_lambda_integration(lambda_function, route_key):
    integration = aws.apigatewayv2.Integration(f"{project_name}-{route_key}-integration",
        api_id=api_gateway.id,
        integration_type="AWS_PROXY",
        integration_uri=lambda_function.invoke_arn,
        integration_method="POST",
        payload_format_version="2.0",
    )
    route = aws.apigatewayv2.Route(f"{project_name}-{route_key}-route",
        api_id=api_gateway.id,
        route_key=route_key,
        target=f"integrations/{integration.id}",
    )
    return integration, route

# Create API routes
auth_integration, auth_route = create_lambda_integration(auth_lambda, "POST /auth/{proxy+}")
profile_integration, profile_route = create_lambda_integration(profile_lambda, "GET /profile")
profile_update_integration, profile_update_route = create_lambda_integration(profile_lambda, "PUT /profile")
stores_integration, stores_route = create_lambda_integration(stores_lambda, "GET /stores")
stores_detail_integration, stores_detail_route = create_lambda_integration(stores_lambda, "GET /stores/{proxy+}")
stores_create_integration, stores_create_route = create_lambda_integration(stores_lambda, "POST /stores")
categories_integration, categories_route = create_lambda_integration(categories_lambda, "GET /categories")
categories_create_integration, categories_create_route = create_lambda_integration(categories_lambda, "POST /categories")
products_integration, products_route = create_lambda_integration(products_lambda, "GET /products")
products_detail_integration, products_detail_route = create_lambda_integration(products_lambda, "GET /products/{proxy+}")
orders_integration, orders_route = create_lambda_integration(orders_lambda, "GET /orders")
orders_create_integration, orders_create_route = create_lambda_integration(orders_lambda, "POST /orders")
orders_detail_integration, orders_detail_route = create_lambda_integration(orders_lambda, "GET /orders/{proxy+}")
analytics_integration, analytics_route = create_lambda_integration(analytics_lambda, "GET /stores/{proxy+}/analytics/{proxy+}")

def create_lambda_permission(lambda_function, source_arn):
    return aws.lambda_.Permission(f"{project_name}-{lambda_function.name}-permission",
        action="lambda:InvokeFunction",
        function=lambda_function.name,
        principal="apigateway.amazonaws.com",
        source_arn=source_arn,
    )

lambda_permissions = []
for lambda_func in [auth_lambda, profile_lambda, stores_lambda, categories_lambda, products_lambda, orders_lambda, analytics_lambda]:
    permission = create_lambda_permission(
        lambda_func,
        f"{api_gateway.execution_arn}/*/*"
    )
    lambda_permissions.append(permission)

# Outputs
pulumi.export("api_gateway_url", api_stage.invoke_url)
pulumi.export("users_table", users_table.name)
pulumi.export("stores_table", stores_table.name)
pulumi.export("products_table", products_table.name)
pulumi.export("orders_table", orders_table.name)
pulumi.export("vpc_id", vpc.vpc_id) 