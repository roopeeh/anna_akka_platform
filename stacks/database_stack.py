"""
Database Stack - Standalone Database Infrastructure
Deploy only DynamoDB tables
"""

import pulumi
import pulumi_aws as aws

# Import database module
from infrastructure import database

# Configuration
config = pulumi.Config()
environment = config.get("environment") or "dev"
project_name = "anna-akka-platform"

print(f"🚀 Deploying database infrastructure for {project_name} in {environment} environment")

# Create Database Infrastructure
database_infrastructure = database.create_database_infrastructure(project_name, environment)

# Outputs
pulumi.export("users_table", database_infrastructure["users_table"].name)
pulumi.export("available_products_table", database_infrastructure["available_products_table"].name)
pulumi.export("stores_table", database_infrastructure["stores_table"].name)
pulumi.export("categories_table", database_infrastructure["categories_table"].name)
pulumi.export("products_table", database_infrastructure["products_table"].name)
pulumi.export("orders_table", database_infrastructure["orders_table"].name)
pulumi.export("order_items_table", database_infrastructure["order_items_table"].name)
pulumi.export("cart_table", database_infrastructure["cart_table"].name)

print(f"✅ Database infrastructure deployment configuration complete!")
print(f"🌍 Environment: {environment}")
print(f"🏗️  Project: {project_name}") 