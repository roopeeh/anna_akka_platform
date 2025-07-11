"""
Cognito Stack - Standalone Cognito Infrastructure
Deploy only Cognito User Pool and authentication
"""

import pulumi
import pulumi_aws as aws

# Import Cognito and IAM modules
from infrastructure import cognito, iam, database

# Configuration
config = pulumi.Config()
environment = config.get("environment") or "dev"
project_name = "anna-akka-platform"

print(f"🚀 Deploying Cognito infrastructure for {project_name} in {environment} environment")

# Create Database Infrastructure (needed for IAM)
database_infrastructure = database.create_database_infrastructure(project_name, environment)

# Create IAM Infrastructure (needed for Cognito)
iam_infrastructure = iam.create_iam_infrastructure(project_name, environment, database_infrastructure)

# Create Cognito Infrastructure
cognito_infrastructure = cognito.create_cognito_infrastructure(
    project_name, 
    environment, 
    iam_infrastructure["cognito_sms_role"]
)

# Outputs
pulumi.export("cognito_user_pool_id", cognito_infrastructure["cognito_user_pool"].id)
pulumi.export("cognito_user_pool_client_id", cognito_infrastructure["cognito_user_pool_client"].id)

print(f"✅ Cognito infrastructure deployment configuration complete!")
print(f"🌍 Environment: {environment}")
print(f"🏗️  Project: {project_name}") 