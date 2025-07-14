# Anna Akka Platform - Dev Branch Deployment Guide

This guide explains how to deploy the Anna Akka Platform infrastructure in the `ap-south-1` region for the dev branch.

## 🌿 Dev Branch Overview

The dev branch is configured to deploy infrastructure in the **ap-south-1** region (Mumbai, India) to provide:
- Lower latency for Indian users
- Cost optimization for the region
- Separate environment from production

## 📋 Prerequisites

1. **Pulumi CLI** installed
2. **AWS CLI** configured with appropriate credentials
3. **Python 3.9+** installed
4. **Git** for branch management
5. **AWS Account** with permissions for ap-south-1 region

## 🚀 Quick Start

### Option 1: Using the Python Script (Recommended)

```bash
# Make sure you're on the dev branch
git checkout dev

# Run the deployment script
python deploy_dev_fast.py
```

### Option 2: Using the Bash Script

```bash
# Make sure you're on the dev branch
git checkout dev

# Make the script executable
chmod +x deploy_dev.sh

# Run the deployment script
./deploy_dev.sh
```

### Option 3: Manual Pulumi Commands

```bash
# Switch to dev branch
git checkout dev

# Install dependencies
pip install -r requirements.txt

# Initialize dev stack (if not exists)
pulumi stack init dev-stack-ap-south-1

# Configure for ap-south-1
pulumi config set aws:region ap-south-1 --stack dev-stack-ap-south-1
pulumi config set environment dev --stack dev-stack-ap-south-1

# Preview changes
pulumi preview --stack dev-stack-ap-south-1

# Deploy infrastructure
pulumi up --yes --stack dev-stack-ap-south-1
```

## 📁 Dev Branch Files

- `Pulumi.roopeeh-dev.yaml` - Dev stack configuration for ap-south-1
- `deploy_dev.sh` - Bash deployment script for dev
- `deploy_dev_fast.py` - Python deployment script for dev
- `DEV_DEPLOYMENT_README.md` - This file

## 🔧 Configuration

### Stack Configuration

The dev stack uses the following configuration:

```yaml
config:
  aws:region: ap-south-1
  pulumi:owner: roopeeh
  aws:profile: default
  environment: dev
```

### Environment Variables

All Lambda functions in the dev environment will have:
- `ENVIRONMENT=dev`
- `AWS_REGION=ap-south-1`
- All DynamoDB table names prefixed with `anna-akka-platform-dev-`

## 🏗️ Infrastructure Components

The dev environment includes:

### Compute
- **Lambda Functions** in ap-south-1
- **API Gateway** with HTTP API
- **VPC** with private/public subnets

### Storage
- **DynamoDB Tables** (on-demand billing)
- **RDS PostgreSQL** (if configured)

### Security
- **IAM Roles** with least privilege
- **Security Groups** for network isolation
- **Cognito User Pool** for authentication

### Networking
- **VPC** in ap-south-1
- **Private Subnets** for Lambda functions
- **Public Subnets** for NAT Gateway

## 📊 Monitoring

### CloudWatch Logs
- Lambda function logs: `/aws/lambda/anna-akka-platform-dev-*`
- API Gateway logs: `/aws/apigateway/`

### Stack Outputs
```bash
# View all outputs
pulumi stack output --stack dev-stack-ap-south-1

# Common outputs
pulumi stack output api_gateway_url --stack dev-stack-ap-south-1
pulumi stack output users_table --stack dev-stack-ap-south-1
```

## 🔄 Deployment Workflow

1. **Switch to dev branch**
   ```bash
   git checkout dev
   ```

2. **Preview changes**
   ```bash
   python deploy_dev_fast.py
   # Choose option 1: Preview changes
   ```

3. **Deploy infrastructure**
   ```bash
   python deploy_dev_fast.py
   # Choose option 2: Deploy infrastructure
   ```

4. **Verify deployment**
   ```bash
   pulumi stack output --stack dev
   ```

5. **Test endpoints**
   ```bash
   # Get the API Gateway URL
API_URL=$(pulumi stack output api_gateway_url --stack dev-stack-ap-south-1)
curl $API_URL/auth/health
   ```

## 🧪 Testing

### Health Check
```bash
curl https://your-api-gateway-url/dev/auth/health
```

### Integration Tests
```bash
# Run the integration tests
python test_complete_user_flow.py
```

## 🗑️ Cleanup

To destroy the dev infrastructure:

```bash
python deploy_dev_fast.py
# Choose option 3: Destroy infrastructure
```

Or manually:
```bash
pulumi destroy --yes --stack dev-stack-ap-south-1
```

## 🔍 Troubleshooting

### Common Issues

1. **Region not available**
   - Ensure your AWS account has access to ap-south-1
   - Check AWS service availability in the region

2. **Stack not found**
   ```bash
   pulumi stack init dev-stack-ap-south-1
   ```

3. **Configuration issues**
   ```bash
   pulumi config set aws:region ap-south-1 --stack dev-stack-ap-south-1
   pulumi config set environment dev --stack dev-stack-ap-south-1
   ```

4. **Lambda deployment failures**
   - Check CloudWatch logs for specific errors
   - Verify IAM permissions
   - Ensure VPC configuration is correct

### Debug Commands

```bash
# Check current stack
pulumi stack --stack dev-stack-ap-south-1

# View configuration
pulumi config --stack dev-stack-ap-south-1

# View resource details
pulumi stack --show-urns --stack dev

# Check AWS credentials
aws sts get-caller-identity
```

## 📈 Cost Optimization

### Dev Environment Optimizations

1. **DynamoDB**: Uses on-demand billing (pay per request)
2. **Lambda**: 512MB memory, 30s timeout (adjust as needed)
3. **RDS**: t3.micro instance (upgrade for production)
4. **VPC**: Minimal subnets (2 AZs)

### Cost Monitoring

```bash
# Set up cost alerts in AWS Console
# Monitor CloudWatch metrics
# Use AWS Cost Explorer for detailed analysis
```

## 🔐 Security

### Dev Environment Security

1. **IAM Roles**: Least privilege principle
2. **VPC**: Private subnets for Lambda functions
3. **Security Groups**: Restrictive inbound rules
4. **DynamoDB**: Encryption at rest enabled
5. **API Gateway**: CORS configured for development

## 📝 Next Steps

After successful deployment:

1. **Set up database schema** (if using RDS)
2. **Configure frontend** to use the new API Gateway URL
3. **Set up monitoring** and alerting
4. **Run integration tests** to verify functionality
5. **Update CI/CD pipeline** to use ap-south-1 for dev

## 🆘 Support

For issues with dev deployment:

1. Check the troubleshooting section above
2. Review CloudWatch logs for specific errors
3. Verify AWS credentials and permissions
4. Ensure you're on the dev branch
5. Check that ap-south-1 services are available

---

**🎉 Your dev environment is now ready in ap-south-1!** 