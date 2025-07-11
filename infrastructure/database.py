"""
Database Infrastructure Module
Handles DynamoDB tables and database-related resources
"""

import pulumi
import pulumi_aws as aws

def create_database_infrastructure(project_name: str, environment: str):
    """Create DynamoDB tables"""
    
    # Users table
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

    # Available Products table
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

    # Stores table
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

    # Categories table
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

    # Products table
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

    # Orders table
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

    # Order Items table
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

    # Cart table
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

    return {
        "users_table": users_table,
        "available_products_table": available_products_table,
        "stores_table": stores_table,
        "categories_table": categories_table,
        "products_table": products_table,
        "orders_table": orders_table,
        "order_items_table": order_items_table,
        "cart_table": cart_table
    } 