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

# VPC and Networking - Optimized for faster deployment
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
    subnet_strategy=awsx.ec2.SubnetAllocationStrategy.AUTO,
    enable_dns_hostnames=True,
    enable_dns_support=True,
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

# IAM Role for Cognito SMS
cognito_sms_role = aws.iam.Role(f"{project_name}-cognito-sms-role",
    name=f"{project_name}-{environment}-cognito-sms-role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {
                "Service": "cognito-idp.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }]
    }),
    tags={
        "Name": f"{project_name}-cognito-sms-role",
        "Environment": environment,
    }
)

# Create custom SMS policy for Cognito
cognito_sms_policy = aws.iam.Policy(f"{project_name}-cognito-sms-policy",
    name=f"{project_name}-{environment}-cognito-sms-policy",
    description="Policy for Cognito SMS functionality",
    policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "sns:Publish"
                ],
                "Resource": "*"
            }
        ]
    }),
    tags={
        "Name": f"{project_name}-cognito-sms-policy",
        "Environment": environment,
    }
)

# Attach the custom SMS policy
cognito_sms_policy_attachment = aws.iam.RolePolicyAttachment(f"{project_name}-cognito-sms-policy-attachment",
    role=cognito_sms_role.name,
    policy_arn=cognito_sms_policy.arn
)

# Cognito User Pool
cognito_user_pool = aws.cognito.UserPool(f"{project_name}-user-pool",
    name=f"{project_name}-user-pool",
    username_attributes=["phone_number"],
    auto_verified_attributes=["phone_number"],
    password_policy={
        "minimum_length": 8,
        "require_lowercase": True,
        "require_numbers": True,
        "require_symbols": False,
        "require_uppercase": True,
    },
    account_recovery_setting={
        "recovery_mechanisms": [{
            "name": "verified_phone_number",
            "priority": 1,
        }],
    },
    verification_message_template={
        "default_email_option": "CONFIRM_WITH_CODE",
    },
    mfa_configuration="OPTIONAL",
    software_token_mfa_configuration={
        "enabled": True,
    },
    sms_configuration=aws.cognito.UserPoolSmsConfigurationArgs(
        external_id=f"{project_name}-sms-config",
        sns_caller_arn=cognito_sms_role.arn,
        sns_region=config.get("aws:region") or "ap-south-1",
    ),
    tags={
        "Name": f"{project_name}-user-pool",
        "Environment": environment,
    }
)

# Cognito User Pool Client
cognito_user_pool_client = aws.cognito.UserPoolClient(f"{project_name}-user-pool-client",
    name=f"{project_name}-user-pool-client",
    user_pool_id=cognito_user_pool.id,
    generate_secret=False,
    explicit_auth_flows=[
        "ALLOW_USER_PASSWORD_AUTH",
        "ALLOW_REFRESH_TOKEN_AUTH",
        "ALLOW_USER_SRP_AUTH",
    ],
    read_attributes=["phone_number", "email", "name"],
    write_attributes=["phone_number", "email", "name"],
    supported_identity_providers=["COGNITO"],
)

# DynamoDB Tables
users_table = aws.dynamodb.Table(f"{project_name}-users-table",
    name=f"{project_name}-users-table",
    attributes=[
        aws.dynamodb.TableAttributeArgs(
            name="id",
            type="S",
        ),
        aws.dynamodb.TableAttributeArgs(
            name="phone",
            type="S",
        ),
        aws.dynamodb.TableAttributeArgs(
            name="email",
            type="S",
        ),
    ],
    hash_key="id",
    global_secondary_indexes=[
        {
            "name": "phone_index",
            "hash_key": "phone",
            "projection_type": "ALL",
        },
        {
            "name": "email_index",
            "hash_key": "email",
            "projection_type": "ALL",
        },
    ],
    billing_mode="PAY_PER_REQUEST",
    tags={
        "Name": f"{project_name}-users-table",
        "Environment": environment,
    }
)

available_products_table = aws.dynamodb.Table(f"{project_name}-available-products-table",
    name=f"{project_name}-available-products-table",
    attributes=[
        aws.dynamodb.TableAttributeArgs(
            name="id",
            type="S",
        ),
        aws.dynamodb.TableAttributeArgs(
            name="category_id",
            type="S",
        ),
    ],
    hash_key="id",
    global_secondary_indexes=[{
        "name": "category_id_index",
        "hash_key": "category_id",
        "projection_type": "ALL",
    }],
    billing_mode="PAY_PER_REQUEST",
    tags={
        "Name": f"{project_name}-available-products-table",
        "Environment": environment,
    }
)

stores_table = aws.dynamodb.Table(f"{project_name}-stores-table",
    name=f"{project_name}-stores-table",
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
        "Name": f"{project_name}-stores-table",
        "Environment": environment,
    }
)

categories_table = aws.dynamodb.Table(f"{project_name}-categories-table",
    name=f"{project_name}-categories-table",
    attributes=[
        aws.dynamodb.TableAttributeArgs(
            name="id",
            type="S",
        ),
    ],
    hash_key="id",
    billing_mode="PAY_PER_REQUEST",
    tags={
        "Name": f"{project_name}-categories-table",
        "Environment": environment,
    }
)

products_table = aws.dynamodb.Table(f"{project_name}-products-table",
    name=f"{project_name}-products-table",
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
        "Name": f"{project_name}-products-table",
        "Environment": environment,
    }
)

orders_table = aws.dynamodb.Table(f"{project_name}-orders-table",
    name=f"{project_name}-orders-table",
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
        "Name": f"{project_name}-orders-table",
        "Environment": environment,
    }
)

order_items_table = aws.dynamodb.Table(f"{project_name}-order-items-table",
    name=f"{project_name}-order-items-table",
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
        "Name": f"{project_name}-order-items-table",
        "Environment": environment,
    }
)

# Cart table for storing customer cart items
cart_table = aws.dynamodb.Table(f"{project_name}-cart-table",
    name=f"{project_name}-cart-table",
    attributes=[
        aws.dynamodb.TableAttributeArgs(
            name="customer_id",
            type="S",
        ),
        aws.dynamodb.TableAttributeArgs(
            name="product_id",
            type="S",
        ),
        aws.dynamodb.TableAttributeArgs(
            name="store_id",
            type="S",
        ),
        aws.dynamodb.TableAttributeArgs(
            name="expires_at",
            type="N",
        ),
    ],
    hash_key="customer_id",
    range_key="product_id",
    global_secondary_indexes=[
        {
            "name": "store_id_index",
            "hash_key": "store_id",
            "projection_type": "ALL",
        },
        {
            "name": "expires_at_index",
            "hash_key": "expires_at",
            "projection_type": "ALL",
        },
    ],
    billing_mode="PAY_PER_REQUEST",
    tags={
        "Name": f"{project_name}-cart-table",
        "Environment": environment,
    }
)

# S3 Bucket for Image Storage
images_bucket = aws.s3.Bucket(f"{project_name}-images-bucket",
    bucket=f"{project_name}-{environment}-images",
    cors_rules=[{
        "allowed_headers": ["*"],
        "allowed_methods": ["GET", "PUT", "POST", "DELETE"],
        "allowed_origins": ["*"],
        "expose_headers": ["ETag"],
        "max_age_seconds": 3000,
    }],
    tags={
        "Name": f"{project_name}-images-bucket",
        "Environment": environment,
    }
)

# S3 Bucket Public Access Block (configure for public read access)
s3_public_access_block = aws.s3.BucketPublicAccessBlock(f"{project_name}-images-public-access",
    bucket=images_bucket.id,
    block_public_acls=True,
    block_public_policy=False,
    ignore_public_acls=True,
    restrict_public_buckets=False,
)

# S3 Bucket Policy for Public Read Access
s3_bucket_policy = aws.s3.BucketPolicy(f"{project_name}-images-bucket-policy",
    bucket=images_bucket.id,
    policy=images_bucket.arn.apply(lambda bucket_arn: json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"{bucket_arn}/*"
            }
        ]
    })),
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
        available_products_table.arn,
        stores_table.arn,
        categories_table.arn,
        products_table.arn,
        orders_table.arn,
        order_items_table.arn,
        cart_table.arn
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
                    "dynamodb:BatchWriteItem",
                ],
                "Resource": [
                    arns[0],
                    arns[1],
                    arns[2],
                    arns[3],
                    arns[4],
                    arns[5],
                    arns[6],
                    arns[7],
                    f"{arns[0]}/index/*",
                    f"{arns[1]}/index/*",
                    f"{arns[2]}/index/*",
                    f"{arns[4]}/index/*",
                    f"{arns[5]}/index/*",
                    f"{arns[6]}/index/*",
                    f"{arns[7]}/index/*",
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

# Cognito policy for OTP operations
cognito_policy = aws.iam.Policy(f"{project_name}-cognito-policy",
    policy=pulumi.Output.all(cognito_user_pool.arn).apply(lambda arns: json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "cognito-idp:ForgotPassword",
                    "cognito-idp:ConfirmForgotPassword",
                    "cognito-idp:AdminGetUser",
                    "cognito-idp:AdminCreateUser",
                    "cognito-idp:AdminSetUserPassword",
                    "cognito-idp:AdminInitiateAuth",
                    "cognito-idp:AdminRespondToAuthChallenge",
                ],
                "Resource": arns[0],
            },
        ],
    })),
    tags={
        "Name": f"{project_name}-cognito-policy",
        "Environment": environment,
    }
)
lambda_cognito_policy_attachment = aws.iam.RolePolicyAttachment(f"{project_name}-lambda-cognito",
    role=lambda_role.name,
    policy_arn=cognito_policy.arn
)

# SNS policy for SMS functionality
sns_policy = aws.iam.Policy(f"{project_name}-sns-policy",
    policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "sns:Publish"
                ],
                "Resource": "*"
            }
        ],
    }),
    tags={
        "Name": f"{project_name}-sns-policy",
        "Environment": environment,
    }
)

lambda_sns_policy_attachment = aws.iam.RolePolicyAttachment(f"{project_name}-lambda-sns",
    role=lambda_role.name,
    policy_arn=sns_policy.arn
)

# S3 policy for image upload functionality
s3_policy = aws.iam.Policy(f"{project_name}-s3-policy",
    policy=pulumi.Output.all(images_bucket.arn).apply(lambda arns: json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:PutObjectAcl",
                    "s3:GetObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    arns[0],
                    f"{arns[0]}/*"
                ],
            },
        ],
    })),
    tags={
        "Name": f"{project_name}-s3-policy",
        "Environment": environment,
    }
)

lambda_s3_policy_attachment = aws.iam.RolePolicyAttachment(f"{project_name}-lambda-s3",
    role=lambda_role.name,
    policy_arn=s3_policy.arn
)

def create_lambda_function(name, handler, environment_vars=None):
    env_vars = {
        "ENVIRONMENT": environment,
        "USERS_TABLE": users_table.name,
        "AVAILABLE_PRODUCTS_TABLE": available_products_table.name,
        "STORES_TABLE": stores_table.name,
        "CATEGORIES_TABLE": categories_table.name,
        "PRODUCTS_TABLE": products_table.name,
        "ORDERS_TABLE": orders_table.name,
        "ORDER_ITEMS_TABLE": order_items_table.name,
        "CART_TABLE": cart_table.name,
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
    return aws.lambda_.Function(f"{project_name}-{name}",
        name=f"{project_name}-{name}",
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
auth_lambda = create_lambda_function("auth", "handler.handler")
otp_auth_lambda = create_lambda_function("otp_auth", "handler.lambda_handler", {
    "COGNITO_USER_POOL_ID": cognito_user_pool.id,
    "COGNITO_CLIENT_ID": cognito_user_pool_client.id,
})
profile_lambda = create_lambda_function("profile", "handler.handler")
categories_lambda = create_lambda_function("categories", "handler.handler")
stores_lambda = create_lambda_function("stores", "handler.handler")
products_lambda = create_lambda_function("products", "handler.handler")
available_products_lambda = create_lambda_function("available_products", "handler.handler")
orders_lambda = create_lambda_function("orders", "handler.handler")
cart_lambda = create_lambda_function("cart", "handler.lambda_handler")
image_upload_lambda = create_lambda_function("image_upload", "handler.handler", {
    "S3_BUCKET_NAME": images_bucket.bucket,
    "S3_BUCKET_REGION": config.get("aws:region") or "ap-south-1",
})
# analytics_lambda = create_lambda_function("analytics", "handler.handler")

# API Gateway (create after Lambda)
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

# Create Lambda integration
auth_integration = aws.apigatewayv2.Integration(f"{project_name}-auth-integration",
    api_id=api_gateway.id,
    integration_type="AWS_PROXY",
    integration_uri=auth_lambda.invoke_arn,
    integration_method="POST",
    payload_format_version="2.0",
)

otp_integration = aws.apigatewayv2.Integration(f"{project_name}-otp-integration",
    api_id=api_gateway.id,
    integration_type="AWS_PROXY",
    integration_uri=otp_auth_lambda.invoke_arn,
    integration_method="POST",
    payload_format_version="2.0",
)

# Create integrations for other lambda functions
profile_integration = aws.apigatewayv2.Integration(f"{project_name}-profile-integration",
    api_id=api_gateway.id,
    integration_type="AWS_PROXY",
    integration_uri=profile_lambda.invoke_arn,
    integration_method="POST",
    payload_format_version="2.0",
)

categories_integration = aws.apigatewayv2.Integration(f"{project_name}-categories-integration",
    api_id=api_gateway.id,
    integration_type="AWS_PROXY",
    integration_uri=categories_lambda.invoke_arn,
    integration_method="POST",
    payload_format_version="2.0",
)

stores_integration = aws.apigatewayv2.Integration(f"{project_name}-stores-integration",
    api_id=api_gateway.id,
    integration_type="AWS_PROXY",
    integration_uri=stores_lambda.invoke_arn,
    integration_method="POST",
    payload_format_version="2.0",
)

products_integration = aws.apigatewayv2.Integration(f"{project_name}-products-integration",
    api_id=api_gateway.id,
    integration_type="AWS_PROXY",
    integration_uri=products_lambda.invoke_arn,
    integration_method="POST",
    payload_format_version="2.0",
)

available_products_integration = aws.apigatewayv2.Integration(f"{project_name}-available-products-integration",
    api_id=api_gateway.id,
    integration_type="AWS_PROXY",
    integration_uri=available_products_lambda.invoke_arn,
    integration_method="POST",
    payload_format_version="2.0",
)

orders_integration = aws.apigatewayv2.Integration(f"{project_name}-orders-integration",
    api_id=api_gateway.id,
    integration_type="AWS_PROXY",
    integration_uri=orders_lambda.invoke_arn,
    integration_method="POST",
    payload_format_version="2.0",
)

cart_integration = aws.apigatewayv2.Integration(f"{project_name}-cart-integration",
    api_id=api_gateway.id,
    integration_type="AWS_PROXY",
    integration_uri=cart_lambda.invoke_arn,
    integration_method="POST",
    payload_format_version="2.0",
)

image_upload_integration = aws.apigatewayv2.Integration(f"{project_name}-image-upload-integration",
    api_id=api_gateway.id,
    integration_type="AWS_PROXY",
    integration_uri=image_upload_lambda.invoke_arn,
    integration_method="POST",
    payload_format_version="2.0",
)

# analytics_integration = aws.apigatewayv2.Integration(f"{project_name}-analytics-integration",
#     api_id=api_gateway.id,
#     integration_type="AWS_PROXY",
#     integration_uri=analytics_lambda.invoke_arn,
#     integration_method="POST",
#     payload_format_version="2.0",
# )

# Create route with simpler route key
auth_route = aws.apigatewayv2.Route(f"{project_name}-auth-route",
    api_id=api_gateway.id,
    route_key="POST /auth/register",
    target=auth_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Create another route for login
auth_login_route = aws.apigatewayv2.Route(f"{project_name}-auth-login-route",
    api_id=api_gateway.id,
    route_key="POST /auth/login",
    target=auth_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Create route for phone number search
auth_phone_route = aws.apigatewayv2.Route(f"{project_name}-auth-phone-route",
    api_id=api_gateway.id,
    route_key="GET /auth/user/phone",
    target=auth_integration.id.apply(lambda id: f"integrations/{id}"),
)

# OTP routes
otp_send_route = aws.apigatewayv2.Route(f"{project_name}-otp-send-route",
    api_id=api_gateway.id,
    route_key="POST /auth/otp/send",
    target=otp_integration.id.apply(lambda id: f"integrations/{id}"),
)

otp_verify_route = aws.apigatewayv2.Route(f"{project_name}-otp-verify-route",
    api_id=api_gateway.id,
    route_key="POST /auth/otp/verify",
    target=otp_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Add routes for invalid methods to allow proper 405 responses
auth_register_put_route = aws.apigatewayv2.Route(f"{project_name}-auth-register-put-route",
    api_id=api_gateway.id,
    route_key="PUT /auth/register",
    target=auth_integration.id.apply(lambda id: f"integrations/{id}"),
)

auth_register_delete_route = aws.apigatewayv2.Route(f"{project_name}-auth-register-delete-route",
    api_id=api_gateway.id,
    route_key="DELETE /auth/register",
    target=auth_integration.id.apply(lambda id: f"integrations/{id}"),
)

auth_login_put_route = aws.apigatewayv2.Route(f"{project_name}-auth-login-put-route",
    api_id=api_gateway.id,
    route_key="PUT /auth/login",
    target=auth_integration.id.apply(lambda id: f"integrations/{id}"),
)

auth_login_delete_route = aws.apigatewayv2.Route(f"{project_name}-auth-login-delete-route",
    api_id=api_gateway.id,
    route_key="DELETE /auth/login",
    target=auth_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Profile routes
profile_get_route = aws.apigatewayv2.Route(f"{project_name}-profile-get-route",
    api_id=api_gateway.id,
    route_key="GET /profile",
    target=profile_integration.id.apply(lambda id: f"integrations/{id}"),
)

profile_put_route = aws.apigatewayv2.Route(f"{project_name}-profile-put-route",
    api_id=api_gateway.id,
    route_key="PUT /profile",
    target=profile_integration.id.apply(lambda id: f"integrations/{id}"),
)

profile_delete_route = aws.apigatewayv2.Route(f"{project_name}-profile-delete-route",
    api_id=api_gateway.id,
    route_key="DELETE /profile",
    target=profile_integration.id.apply(lambda id: f"integrations/{id}"),
)

profile_get_by_phone_route = aws.apigatewayv2.Route(f"{project_name}-profile-get-by-phone-route",
    api_id=api_gateway.id,
    route_key="GET /profile/phone",
    target=profile_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Categories routes
categories_get_route = aws.apigatewayv2.Route(f"{project_name}-categories-get-route",
    api_id=api_gateway.id,
    route_key="GET /categories",
    target=categories_integration.id.apply(lambda id: f"integrations/{id}"),
)

categories_post_route = aws.apigatewayv2.Route(f"{project_name}-categories-post-route",
    api_id=api_gateway.id,
    route_key="POST /categories",
    target=categories_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Add routes for unsupported methods to allow proper 405 responses
categories_put_route_collection = aws.apigatewayv2.Route(f"{project_name}-categories-put-route-collection",
    api_id=api_gateway.id,
    route_key="PUT /categories",
    target=categories_integration.id.apply(lambda id: f"integrations/{id}"),
)

categories_delete_route_collection = aws.apigatewayv2.Route(f"{project_name}-categories-delete-route-collection",
    api_id=api_gateway.id,
    route_key="DELETE /categories",
    target=categories_integration.id.apply(lambda id: f"integrations/{id}"),
)

categories_get_by_id_route = aws.apigatewayv2.Route(f"{project_name}-categories-get-by-id-route",
    api_id=api_gateway.id,
    route_key="GET /categories/{proxy+}",
    target=categories_integration.id.apply(lambda id: f"integrations/{id}"),
)

categories_put_route = aws.apigatewayv2.Route(f"{project_name}-categories-put-route",
    api_id=api_gateway.id,
    route_key="PUT /categories/{proxy+}",
    target=categories_integration.id.apply(lambda id: f"integrations/{id}"),
)

categories_delete_route = aws.apigatewayv2.Route(f"{project_name}-categories-delete-route",
    api_id=api_gateway.id,
    route_key="DELETE /categories/{proxy+}",
    target=categories_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Stores routes
stores_get_route = aws.apigatewayv2.Route(f"{project_name}-stores-get-route",
    api_id=api_gateway.id,
    route_key="GET /stores",
    target=stores_integration.id.apply(lambda id: f"integrations/{id}"),
)

stores_post_route = aws.apigatewayv2.Route(f"{project_name}-stores-post-route",
    api_id=api_gateway.id,
    route_key="POST /stores",
    target=stores_integration.id.apply(lambda id: f"integrations/{id}"),
)

stores_get_by_id_route = aws.apigatewayv2.Route(f"{project_name}-stores-get-by-id-route",
    api_id=api_gateway.id,
    route_key="GET /stores/{proxy+}",
    target=stores_integration.id.apply(lambda id: f"integrations/{id}"),
)

stores_put_route = aws.apigatewayv2.Route(f"{project_name}-stores-put-route",
    api_id=api_gateway.id,
    route_key="PUT /stores/{proxy+}",
    target=stores_integration.id.apply(lambda id: f"integrations/{id}"),
)

stores_delete_route = aws.apigatewayv2.Route(f"{project_name}-stores-delete-route",
    api_id=api_gateway.id,
    route_key="DELETE /stores/{proxy+}",
    target=stores_integration.id.apply(lambda id: f"integrations/{id}"),
)

stores_owner_route = aws.apigatewayv2.Route(f"{project_name}-stores-owner-route",
    api_id=api_gateway.id,
    route_key="GET /stores/owner",
    target=stores_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Add routes for unsupported methods to allow proper 405 responses
stores_put_collection_route = aws.apigatewayv2.Route(f"{project_name}-stores-put-collection-route",
    api_id=api_gateway.id,
    route_key="PUT /stores",
    target=stores_integration.id.apply(lambda id: f"integrations/{id}"),
)

stores_delete_collection_route = aws.apigatewayv2.Route(f"{project_name}-stores-delete-collection-route",
    api_id=api_gateway.id,
    route_key="DELETE /stores",
    target=stores_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Products routes
products_get_route = aws.apigatewayv2.Route(f"{project_name}-products-get-route",
    api_id=api_gateway.id,
    route_key="GET /products",
    target=products_integration.id.apply(lambda id: f"integrations/{id}"),
)

products_post_route = aws.apigatewayv2.Route(f"{project_name}-products-post-route",
    api_id=api_gateway.id,
    route_key="POST /products",
    target=products_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Add routes for unsupported methods to allow proper 405 responses
products_put_collection_route = aws.apigatewayv2.Route(f"{project_name}-products-put-collection-route",
    api_id=api_gateway.id,
    route_key="PUT /products",
    target=products_integration.id.apply(lambda id: f"integrations/{id}"),
)

products_delete_collection_route = aws.apigatewayv2.Route(f"{project_name}-products-delete-collection-route",
    api_id=api_gateway.id,
    route_key="DELETE /products",
    target=products_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Add OPTIONS route for CORS preflight requests
products_options_route = aws.apigatewayv2.Route(f"{project_name}-products-options-route",
    api_id=api_gateway.id,
    route_key="OPTIONS /products",
    target=products_integration.id.apply(lambda id: f"integrations/{id}"),
)

products_get_by_id_route = aws.apigatewayv2.Route(f"{project_name}-products-get-by-id-route",
    api_id=api_gateway.id,
    route_key="GET /products/{proxy+}",
    target=products_integration.id.apply(lambda id: f"integrations/{id}"),
)

products_put_route = aws.apigatewayv2.Route(f"{project_name}-products-put-route",
    api_id=api_gateway.id,
    route_key="PUT /products/{proxy+}",
    target=products_integration.id.apply(lambda id: f"integrations/{id}"),
)

products_delete_route = aws.apigatewayv2.Route(f"{project_name}-products-delete-route",
    api_id=api_gateway.id,
    route_key="DELETE /products/{proxy+}",
    target=products_integration.id.apply(lambda id: f"integrations/{id}"),
)

stores_products_get_route = aws.apigatewayv2.Route(f"{project_name}-stores-products-get-route",
    api_id=api_gateway.id,
    route_key="GET /stores/{store_id}/products",
    target=products_integration.id.apply(lambda id: f"integrations/{id}"),
)

stores_products_post_route = aws.apigatewayv2.Route(f"{project_name}-stores-products-post-route",
    api_id=api_gateway.id,
    route_key="POST /stores/{store_id}/products",
    target=products_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Add specific route for getting products by store and available product ID
stores_products_available_get_route = aws.apigatewayv2.Route(f"{project_name}-stores-products-available-get-route",
    api_id=api_gateway.id,
    route_key="GET /stores/{store_id}/products/available/{available_product_id}",
    target=products_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Available Products routes
available_products_get_route = aws.apigatewayv2.Route(f"{project_name}-available-products-get-route",
    api_id=api_gateway.id,
    route_key="GET /available-products",
    target=available_products_integration.id.apply(lambda id: f"integrations/{id}"),
)

available_products_post_route = aws.apigatewayv2.Route(f"{project_name}-available-products-post-route",
    api_id=api_gateway.id,
    route_key="POST /available-products",
    target=available_products_integration.id.apply(lambda id: f"integrations/{id}"),
)

available_products_get_by_id_route = aws.apigatewayv2.Route(f"{project_name}-available-products-get-by-id-route",
    api_id=api_gateway.id,
    route_key="GET /available-products/{proxy+}",
    target=available_products_integration.id.apply(lambda id: f"integrations/{id}"),
)

available_products_put_route = aws.apigatewayv2.Route(f"{project_name}-available-products-put-route",
    api_id=api_gateway.id,
    route_key="PUT /available-products/{proxy+}",
    target=available_products_integration.id.apply(lambda id: f"integrations/{id}"),
)

available_products_delete_route = aws.apigatewayv2.Route(f"{project_name}-available-products-delete-route",
    api_id=api_gateway.id,
    route_key="DELETE /available-products/{proxy+}",
    target=available_products_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Orders routes
orders_get_route = aws.apigatewayv2.Route(f"{project_name}-orders-get-route",
    api_id=api_gateway.id,
    route_key="GET /orders",
    target=orders_integration.id.apply(lambda id: f"integrations/{id}"),
)

orders_post_route = aws.apigatewayv2.Route(f"{project_name}-orders-post-route",
    api_id=api_gateway.id,
    route_key="POST /orders",
    target=orders_integration.id.apply(lambda id: f"integrations/{id}"),
)

orders_put_collection_route = aws.apigatewayv2.Route(f"{project_name}-orders-put-collection-route",
    api_id=api_gateway.id,
    route_key="PUT /orders",
    target=orders_integration.id.apply(lambda id: f"integrations/{id}"),
)

orders_delete_collection_route = aws.apigatewayv2.Route(f"{project_name}-orders-delete-collection-route",
    api_id=api_gateway.id,
    route_key="DELETE /orders",
    target=orders_integration.id.apply(lambda id: f"integrations/{id}"),
)

orders_get_by_id_route = aws.apigatewayv2.Route(f"{project_name}-orders-get-by-id-route",
    api_id=api_gateway.id,
    route_key="GET /orders/{proxy+}",
    target=orders_integration.id.apply(lambda id: f"integrations/{id}"),
)

orders_put_route = aws.apigatewayv2.Route(f"{project_name}-orders-put-route",
    api_id=api_gateway.id,
    route_key="PUT /orders/{proxy+}",
    target=orders_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Cart routes
cart_get_route = aws.apigatewayv2.Route(f"{project_name}-cart-get-route",
    api_id=api_gateway.id,
    route_key="GET /cart",
    target=cart_integration.id.apply(lambda id: f"integrations/{id}"),
)

cart_items_post_route = aws.apigatewayv2.Route(f"{project_name}-cart-items-post-route",
    api_id=api_gateway.id,
    route_key="POST /cart/items",
    target=cart_integration.id.apply(lambda id: f"integrations/{id}"),
)

cart_items_put_route = aws.apigatewayv2.Route(f"{project_name}-cart-items-put-route",
    api_id=api_gateway.id,
    route_key="PUT /cart/items/{proxy+}",
    target=cart_integration.id.apply(lambda id: f"integrations/{id}"),
)

cart_items_delete_route = aws.apigatewayv2.Route(f"{project_name}-cart-items-delete-route",
    api_id=api_gateway.id,
    route_key="DELETE /cart/items/{proxy+}",
    target=cart_integration.id.apply(lambda id: f"integrations/{id}"),
)

cart_delete_route = aws.apigatewayv2.Route(f"{project_name}-cart-delete-route",
    api_id=api_gateway.id,
    route_key="DELETE /cart",
    target=cart_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Image Upload routes
image_upload_post_route = aws.apigatewayv2.Route(f"{project_name}-image-upload-post-route",
    api_id=api_gateway.id,
    route_key="POST /images/upload",
    target=image_upload_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Add routes for unsupported methods to allow proper 405 responses
image_upload_get_route = aws.apigatewayv2.Route(f"{project_name}-image-upload-get-route",
    api_id=api_gateway.id,
    route_key="GET /images/upload",
    target=image_upload_integration.id.apply(lambda id: f"integrations/{id}"),
)

image_upload_put_route = aws.apigatewayv2.Route(f"{project_name}-image-upload-put-route",
    api_id=api_gateway.id,
    route_key="PUT /images/upload",
    target=image_upload_integration.id.apply(lambda id: f"integrations/{id}"),
)

image_upload_delete_route = aws.apigatewayv2.Route(f"{project_name}-image-upload-delete-route",
    api_id=api_gateway.id,
    route_key="DELETE /images/upload",
    target=image_upload_integration.id.apply(lambda id: f"integrations/{id}"),
)

# Create permission for auth lambda
auth_permission = aws.lambda_.Permission(f"{project_name}-auth-permission",
    action="lambda:InvokeFunction",
    function=auth_lambda.name,
    principal="apigateway.amazonaws.com",
    source_arn=api_gateway.execution_arn.apply(lambda arn: f"{arn}/*/*"),
)

# Create permissions for other lambda functions
profile_permission = aws.lambda_.Permission(f"{project_name}-profile-permission",
    action="lambda:InvokeFunction",
    function=profile_lambda.name,
    principal="apigateway.amazonaws.com",
    source_arn=api_gateway.execution_arn.apply(lambda arn: f"{arn}/*/*"),
)

categories_permission = aws.lambda_.Permission(f"{project_name}-categories-permission",
    action="lambda:InvokeFunction",
    function=categories_lambda.name,
    principal="apigateway.amazonaws.com",
    source_arn=api_gateway.execution_arn.apply(lambda arn: f"{arn}/*/*"),
)

stores_permission = aws.lambda_.Permission(f"{project_name}-stores-permission",
    action="lambda:InvokeFunction",
    function=stores_lambda.name,
    principal="apigateway.amazonaws.com",
    source_arn=api_gateway.execution_arn.apply(lambda arn: f"{arn}/*/*"),
)

products_permission = aws.lambda_.Permission(f"{project_name}-products-permission",
    action="lambda:InvokeFunction",
    function=products_lambda.name,
    principal="apigateway.amazonaws.com",
    source_arn=api_gateway.execution_arn.apply(lambda arn: f"{arn}/*/*"),
)

available_products_permission = aws.lambda_.Permission(f"{project_name}-available-products-permission",
    action="lambda:InvokeFunction",
    function=available_products_lambda.name,
    principal="apigateway.amazonaws.com",
    source_arn=api_gateway.execution_arn.apply(lambda arn: f"{arn}/*/*"),
)

orders_permission = aws.lambda_.Permission(f"{project_name}-orders-permission",
    action="lambda:InvokeFunction",
    function=orders_lambda.name,
    principal="apigateway.amazonaws.com",
    source_arn=api_gateway.execution_arn.apply(lambda arn: f"{arn}/*/*"),
)

cart_permission = aws.lambda_.Permission(f"{project_name}-cart-permission",
    action="lambda:InvokeFunction",
    function=cart_lambda.name,
    principal="apigateway.amazonaws.com",
    source_arn=api_gateway.execution_arn.apply(lambda arn: f"{arn}/*/*"),
)

otp_permission = aws.lambda_.Permission(f"{project_name}-otp-permission",
    action="lambda:InvokeFunction",
    function=otp_auth_lambda.name,
    principal="apigateway.amazonaws.com",
    source_arn=api_gateway.execution_arn.apply(lambda arn: f"{arn}/*/*"),
)

image_upload_permission = aws.lambda_.Permission(f"{project_name}-image-upload-permission",
    action="lambda:InvokeFunction",
    function=image_upload_lambda.name,
    principal="apigateway.amazonaws.com",
    source_arn=api_gateway.execution_arn.apply(lambda arn: f"{arn}/*/*"),
)

# analytics_permission = aws.lambda_.Permission(f"{project_name}-analytics-permission",
#     action="lambda:InvokeFunction",
#     function=analytics_lambda.name,
#     principal="apigateway.amazonaws.com",
#     source_arn=f"{api_gateway.execution_arn}/*/*",
# )

# Outputs
pulumi.export("api_gateway_url", api_stage.invoke_url)
pulumi.export("users_table", users_table.name)
pulumi.export("available_products_table", available_products_table.name)
pulumi.export("stores_table", stores_table.name)
pulumi.export("products_table", products_table.name)
pulumi.export("orders_table", orders_table.name)
pulumi.export("vpc_id", vpc.vpc_id)
pulumi.export("auth_lambda_arn", auth_lambda.invoke_arn)
pulumi.export("profile_lambda_arn", profile_lambda.invoke_arn)
pulumi.export("categories_lambda_arn", categories_lambda.invoke_arn)
pulumi.export("stores_lambda_arn", stores_lambda.invoke_arn)
pulumi.export("products_lambda_arn", products_lambda.invoke_arn)
pulumi.export("available_products_lambda_arn", available_products_lambda.invoke_arn)
pulumi.export("orders_lambda_arn", orders_lambda.invoke_arn)
pulumi.export("cart_lambda_arn", cart_lambda.invoke_arn)
pulumi.export("image_upload_lambda_arn", image_upload_lambda.invoke_arn)
pulumi.export("images_bucket_name", images_bucket.bucket)
pulumi.export("images_bucket_arn", images_bucket.arn)
# pulumi.export("analytics_lambda_arn", analytics_lambda.invoke_arn) 