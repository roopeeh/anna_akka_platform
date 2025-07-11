#!/bin/bash

# Anna Akka Platform - Dev Branch Deployment Script
# This script sets up and deploys the grocery delivery platform infrastructure in ap-south-1

set -e

echo "🚀 Starting Anna Akka Platform DEV deployment in ap-south-1..."

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v pulumi &> /dev/null; then
    echo "❌ Pulumi CLI not found. Please install Pulumi first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+ first."
    exit 1
fi

if ! command -v pip &> /dev/null; then
    echo "❌ pip not found. Please install pip first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check AWS credentials
echo "🔐 Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS credentials verified"

# Check if we're on dev branch
echo "🌿 Checking git branch..."
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "dev" ]; then
    echo "⚠️  Warning: You're not on the dev branch. Current branch: $CURRENT_BRANCH"
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
fi

# Initialize Pulumi stack if not exists
if ! pulumi stack --show-name &> /dev/null; then
    echo "🏗️  Initializing Pulumi stack for dev-stack-ap-south-1..."
    pulumi stack init dev-stack-ap-south-1
fi

# Set configuration for ap-south-1
echo "⚙️  Setting Pulumi configuration for ap-south-1..."
pulumi config set aws:region ap-south-1 --stack dev-stack-ap-south-1
pulumi config set environment dev --stack dev-stack-ap-south-1

echo "✅ Configuration set for ap-south-1 region"

# Preview deployment
echo "👀 Previewing deployment for ap-south-1..."
pulumi preview --stack dev-stack-ap-south-1

echo ""
echo "📋 Deployment preview completed. Review the changes above."
echo ""
read -p "Do you want to proceed with deployment in ap-south-1? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Deploying infrastructure in ap-south-1..."
    pulumi up --stack dev-stack-ap-south-1 --yes
    
    echo ""
    echo "✅ Deployment completed successfully in ap-south-1!"
    echo ""
    echo "📊 Getting outputs..."
    pulumi stack output --stack dev-stack-ap-south-1
    
    echo ""
    echo "🎉 Anna Akka Platform DEV is now deployed in ap-south-1!"
    echo ""
    echo "📝 Next steps:"
    echo "1. Set up your database schema (see README.md)"
    echo "2. Configure your frontend to use the API Gateway URL"
    echo "3. Set up monitoring and alerts"
    echo "4. Test the API endpoints"
    echo "5. Update your CI/CD pipeline to use ap-south-1 for dev"
    
else
    echo "❌ Deployment cancelled"
    exit 1
fi 