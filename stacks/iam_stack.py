"""
IAM Stack - Standalone IAM Infrastructure
Deploy only IAM roles and policies
"""

import pulumi
import pulumi_aws as aws

# Import IAM module
from infrastructure import iam, database

# Configuration
config = pulumi.Config()
environment = config.get("environment") or "dev"
project_name = "anna-akka-platform"

print(f"🚀 Deploying IAM infrastructure for {project_name} in {environment} environment")

# Create Database Infrastructure (needed for IAM policies)
database_infrastructure = database.create_database_infrastructure(project_name, environment)

# Create IAM Infrastructure
iam_infrastructure = iam.create_iam_infrastructure(project_name, environment, database_infrastructure)

# Outputs
pulumi.export("lambda_role_arn", iam_infrastructure["lambda_role"].arn)
pulumi.export("cognito_sms_role_arn", iam_infrastructure["cognito_sms_role"].arn)
pulumi.export("cognito_sms_policy_arn", iam_infrastructure["cognito_sms_policy"].arn)

print(f"✅ IAM infrastructure deployment configuration complete!")
print(f"🌍 Environment: {environment}")
print(f"🏗️  Project: {project_name}") 