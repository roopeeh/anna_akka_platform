"""
API Gateway Stack - Standalone API Gateway Infrastructure
Deploy only API Gateway, integrations, and routes
"""

import pulumi
import pulumi_aws as aws

# Import all required modules
from infrastructure import api_gateway, lambda_functions, iam, database, cognito, vpc

# Configuration
config = pulumi.Config()
environment = config.get("environment") or "dev"
project_name = "anna-akka-platform"

print(f"🚀 Deploying API Gateway infrastructure for {project_name} in {environment} environment")

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

# Create API Gateway Infrastructure
api_gateway_infrastructure = api_gateway.create_api_gateway_infrastructure(
    project_name,
    environment,
    lambda_infrastructure
)

# Outputs
pulumi.export("api_gateway_url", api_gateway_infrastructure["api_stage"].invoke_url)
pulumi.export("api_gateway_id", api_gateway_infrastructure["api_gateway"].id)

print(f"✅ API Gateway infrastructure deployment configuration complete!")
print(f"🌍 Environment: {environment}")
print(f"🏗️  Project: {project_name}") 