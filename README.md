# Anna Akka Platform - Grocery Delivery Infrastructure

This Pulumi project creates a complete AWS infrastructure for a grocery delivery platform using Lambda functions, DynamoDB, and RDS PostgreSQL.

## Architecture Overview

The infrastructure includes:

- **VPC** with public and private subnets across 2 availability zones
- **RDS PostgreSQL** database for relational data
- **DynamoDB** tables for NoSQL data storage
- **Lambda Functions** for API endpoints
- **API Gateway** for HTTP API
- **IAM Roles and Policies** for security
- **Security Groups** for network security

## DynamoDB Tables

- `users` - User profiles and authentication data
- `stores` - Store information with owner relationships
- `categories` - Product categories
- `products` - Product catalog with store relationships
- `orders` - Order data with customer and store relationships
- `order_items` - Individual items within orders

## Lambda Functions

- `auth` - User registration and authentication
- `profile` - User profile management
- `stores` - Store management operations
- `categories` - Category management
- `products` - Product catalog operations
- `orders` - Order management and processing
- `analytics` - Store analytics and reporting

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

### Profile
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile

### Stores
- `GET /stores` - List all stores
- `GET /stores/{id}` - Get store details
- `POST /stores` - Create new store
- `PUT /stores/{id}` - Update store
- `DELETE /stores/{id}` - Delete store
- `GET /stores/owner` - Get stores owned by current user

### Categories
- `GET /categories` - List all categories
- `POST /categories` - Create new category

### Products
- `GET /products` - List all products
- `GET /products/{id}` - Get product details
- `GET /stores/{storeId}/products` - Get products for a store
- `POST /stores/{storeId}/products` - Add product to store
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product

### Orders
- `GET /orders` - List user orders
- `GET /orders/{id}` - Get order details
- `POST /orders` - Create new order
- `PUT /orders/{id}/status` - Update order status
- `GET /stores/{storeId}/orders` - Get orders for a store

### Analytics
- `GET /stores/{storeId}/analytics/overview` - Store analytics overview
- `GET /stores/{storeId}/analytics/sales` - Detailed sales analytics

## Prerequisites

1. **Pulumi CLI** installed
2. **AWS CLI** configured with appropriate credentials
3. **Python 3.9+** installed
4. **Docker** (for building Lambda layers)

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create Lambda layer:**
   ```bash
   # Create lambda layer directory structure
   mkdir -p lambda_layer/python
   
   # Install dependencies to lambda layer
   pip install -r lambda_layer/requirements.txt -t lambda_layer/python/
   ```

3. **Configure Pulumi:**
   ```bash
   # Set AWS region
   pulumi config set aws:region us-east-1
   
   # Set environment
   pulumi config set environment dev
   ```

## Deployment

1. **Preview changes:**
   ```bash
   pulumi preview
   ```

2. **Deploy infrastructure:**
   ```bash
   pulumi up
   ```

3. **Get outputs:**
   ```bash
   pulumi stack output
   ```

## Database Setup

After deployment, you'll need to set up the PostgreSQL database:

1. Connect to the RDS instance using the endpoint from outputs
2. Create the database schema:

```sql
-- Users table (if needed for additional relational data)
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    user_type VARCHAR(50) DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add any additional tables as needed
```

## Environment Variables

The Lambda functions use the following environment variables:

- `ENVIRONMENT` - Deployment environment
- `USERS_TABLE` - DynamoDB users table name
- `STORES_TABLE` - DynamoDB stores table name
- `CATEGORIES_TABLE` - DynamoDB categories table name
- `PRODUCTS_TABLE` - DynamoDB products table name
- `ORDERS_TABLE` - DynamoDB orders table name
- `ORDER_ITEMS_TABLE` - DynamoDB order items table name
- `DB_HOST` - RDS endpoint
- `DB_NAME` - Database name
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password

## Security

- All Lambda functions run in private subnets
- RDS is in private subnets with no public access
- IAM roles follow least privilege principle
- Security groups restrict access appropriately
- DynamoDB tables use on-demand billing for cost optimization

## Monitoring and Logging

- Lambda functions log to CloudWatch
- API Gateway provides request/response logging
- RDS provides database logs
- Consider setting up CloudWatch alarms for monitoring

## Cost Optimization

- DynamoDB uses on-demand billing
- RDS uses t3.micro instance (upgrade as needed)
- Lambda functions have appropriate timeouts and memory limits
- Consider using provisioned concurrency for high-traffic endpoints

## Development

### Local Development

1. **Set up local environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Test Lambda functions locally:**
   ```bash
   # Set environment variables
   export USERS_TABLE="anna-akka-platform-users"
   export DB_HOST="localhost"
   # ... other variables
   
   # Test a function
   python -c "from lambda_functions.auth import handler; print(handler({'body': '{}'}, {}))"
   ```

### Adding New Endpoints

1. Create new Lambda function in `lambda_functions/`
2. Add function to `__main__.py`
3. Create API Gateway integration
4. Update this README

## Troubleshooting

### Common Issues

1. **Lambda timeout:** Increase timeout in function configuration
2. **Memory issues:** Increase memory allocation
3. **Database connection:** Check security groups and VPC configuration
4. **API Gateway errors:** Check Lambda permissions and integration

### Logs

- Lambda logs: CloudWatch > Log groups > `/aws/lambda/anna-akka-platform-*`
- API Gateway logs: CloudWatch > Log groups > `/aws/apigateway/`
- RDS logs: RDS console > Databases > [instance] > Logs

## Cleanup

To destroy the infrastructure:

```bash
pulumi destroy
```

**Warning:** This will delete all resources including databases and data.

## Contributing

1. Follow the existing code structure
2. Add appropriate error handling
3. Include CORS headers in responses
4. Test functions locally before deployment
5. Update documentation for new features

## License

MIT License - see LICENSE file for details. 