#!/bin/bash

# Image Upload API Deployment Script
# This script deploys the image upload functionality to AWS

set -e

echo "🚀 Deploying Image Upload API..."

# Check if Pulumi is installed
if ! command -v pulumi &> /dev/null; then
    echo "❌ Pulumi is not installed. Please install Pulumi first."
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Set environment
ENVIRONMENT=${1:-dev}
echo "📋 Environment: $ENVIRONMENT"

# Deploy the infrastructure
echo "🏗️  Deploying infrastructure..."
pulumi up --yes

# Get the API Gateway URL
API_URL=$(pulumi stack output api_gateway_url)
BUCKET_NAME=$(pulumi stack output images_bucket_name)

echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "🌐 API Gateway URL: $API_URL"
echo "🪣 S3 Bucket Name: $BUCKET_NAME"
echo "📤 Image Upload Endpoint: $API_URL/images/upload"
echo ""
echo "🧪 To test the image upload:"
echo "1. Update the API_BASE_URL in test_image_upload.py"
echo "2. Run: python test_image_upload.py"
echo ""
echo "📚 For detailed documentation, see: IMAGE_UPLOAD_API_DOCUMENTATION.md" 