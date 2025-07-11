"""
VPC Stack - Standalone VPC Infrastructure
Deploy only VPC and networking components
"""

import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx

# Import VPC module
from infrastructure import vpc

# Configuration
config = pulumi.Config()
environment = config.get("environment") or "dev"
project_name = "anna-akka-platform"

print(f"🚀 Deploying VPC infrastructure for {project_name} in {environment} environment")

# Create VPC and Networking Infrastructure
vpc_infrastructure = vpc.create_vpc_infrastructure(project_name, environment)

# Outputs
pulumi.export("vpc_id", vpc_infrastructure["vpc_id"])
pulumi.export("private_subnet_ids", vpc_infrastructure["private_subnet_ids"])
pulumi.export("public_subnet_ids", vpc_infrastructure["public_subnet_ids"])
pulumi.export("lambda_security_group_id", vpc_infrastructure["lambda_sg"].id)

print(f"✅ VPC infrastructure deployment configuration complete!")
print(f"🌍 Environment: {environment}")
print(f"🏗️  Project: {project_name}") 