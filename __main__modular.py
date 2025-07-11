"""
Anna Akka Platform - Modular Infrastructure
Main entry point that orchestrates all infrastructure modules
"""

import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx
import pulumi_random as random
import json
import os

# Import infrastructure modules
from infrastructure import vpc, iam, database, cognito, lambda_functions, api_gateway

# Configuration
config = pulumi.Config()
environment = config.get("environment") or "dev"
project_name = "anna-akka-platform"

print(f"🚀 Deploying {project_name} in {environment} environment")

# Step 1: Create VPC and Networking Infrastructure
print("📡 Creating VPC and networking infrastructure...")
vpc_infrastructure = vpc.create_vpc_infrastructure(project_name, environment)

# Step 2: Create Database Infrastructure
print("🗄️  Creating database infrastructure...")
database_infrastructure = database.create_database_infrastructure(project_name, environment)

# Step 3: Create IAM Infrastructure
print("🔐 Creating IAM roles and policies...")
iam_infrastructure = iam.create_iam_infrastructure(project_name, environment, database_infrastructure)

# Step 4: Create Cognito Infrastructure
print("👤 Creating Cognito authentication infrastructure...")
cognito_infrastructure = cognito.create_cognito_infrastructure(
    project_name, 
    environment, 
    iam_infrastructure["cognito_sms_role"]
)

# Step 5: Create Lambda Functions
print("⚡ Creating Lambda functions...")
vpc_config = {
    "subnet_ids": vpc_infrastructure["private_subnet_ids"],
    "security_group_ids": [vpc_infrastructure["lambda_sg"].id],
}

lambda_infrastructure = lambda_functions.create_all_lambda_functions(
    project_name,
    environment,
    iam_infrastructure["lambda_role"],
    vpc_config,
    database_infrastructure,
    cognito_infrastructure
)

# Step 6: Create API Gateway Infrastructure
print("🌐 Creating API Gateway infrastructure...")
api_gateway_infrastructure = api_gateway.create_api_gateway_infrastructure(
    project_name,
    environment,
    lambda_infrastructure
)

# Outputs
print("📊 Setting up outputs...")

# API Gateway outputs
pulumi.export("api_gateway_url", api_gateway_infrastructure["api_stage"].invoke_url)

# Database outputs
pulumi.export("users_table", database_infrastructure["users_table"].name)
pulumi.export("available_products_table", database_infrastructure["available_products_table"].name)
pulumi.export("stores_table", database_infrastructure["stores_table"].name)
pulumi.export("products_table", database_infrastructure["products_table"].name)
pulumi.export("orders_table", database_infrastructure["orders_table"].name)

# VPC outputs
pulumi.export("vpc_id", vpc_infrastructure["vpc_id"])

# Lambda outputs
pulumi.export("auth_lambda_arn", lambda_infrastructure["auth_lambda"].invoke_arn)
pulumi.export("profile_lambda_arn", lambda_infrastructure["profile_lambda"].invoke_arn)
pulumi.export("categories_lambda_arn", lambda_infrastructure["categories_lambda"].invoke_arn)
pulumi.export("stores_lambda_arn", lambda_infrastructure["stores_lambda"].invoke_arn)
pulumi.export("products_lambda_arn", lambda_infrastructure["products_lambda"].invoke_arn)
pulumi.export("available_products_lambda_arn", lambda_infrastructure["available_products_lambda"].invoke_arn)
pulumi.export("orders_lambda_arn", lambda_infrastructure["orders_lambda"].invoke_arn)
pulumi.export("cart_lambda_arn", lambda_infrastructure["cart_lambda"].invoke_arn)

# Cognito outputs
pulumi.export("cognito_user_pool_id", cognito_infrastructure["cognito_user_pool"].id)
pulumi.export("cognito_user_pool_client_id", cognito_infrastructure["cognito_user_pool_client"].id)

print(f"✅ {project_name} infrastructure deployment configuration complete!")
print(f"🌍 Environment: {environment}")
print(f"🏗️  Project: {project_name}") 