"""
Lambda Stack - Standalone Lambda Infrastructure
Deploy only Lambda functions
"""

import pulumi
import pulumi_aws as aws

# Import all required modules
from infrastructure import lambda_functions, iam, database, cognito, vpc

# Configuration
config = pulumi.Config()
environment = config.get("environment") or "dev"
project_name = "anna-akka-platform"

print(f"🚀 Deploying Lambda infrastructure for {project_name} in {environment} environment")

# Create all required infrastructure
vpc_infrastructure = vpc.create_vpc_infrastructure(project_name, environment)
database_infrastructure = database.create_database_infrastructure(project_name, environment)
iam_infrastructure = iam.create_iam_infrastructure(project_name, environment, database_infrastructure)
cognito_infrastructure = cognito.create_cognito_infrastructure(
    project_name, 
    environment, 
    iam_infrastructure["cognito_sms_role"]
)

# Create Lambda Functions
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

# Outputs
pulumi.export("auth_lambda_arn", lambda_infrastructure["auth_lambda"].invoke_arn)
pulumi.export("profile_lambda_arn", lambda_infrastructure["profile_lambda"].invoke_arn)
pulumi.export("categories_lambda_arn", lambda_infrastructure["categories_lambda"].invoke_arn)
pulumi.export("stores_lambda_arn", lambda_infrastructure["stores_lambda"].invoke_arn)
pulumi.export("products_lambda_arn", lambda_infrastructure["products_lambda"].invoke_arn)
pulumi.export("available_products_lambda_arn", lambda_infrastructure["available_products_lambda"].invoke_arn)
pulumi.export("orders_lambda_arn", lambda_infrastructure["orders_lambda"].invoke_arn)
pulumi.export("cart_lambda_arn", lambda_infrastructure["cart_lambda"].invoke_arn)
pulumi.export("otp_auth_lambda_arn", lambda_infrastructure["otp_auth_lambda"].invoke_arn)

print(f"✅ Lambda infrastructure deployment configuration complete!")
print(f"🌍 Environment: {environment}")
print(f"🏗️  Project: {project_name}") 