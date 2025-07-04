#!/bin/bash

# Anna Akka Platform - Deployment Script
# This script sets up and deploys the grocery delivery platform infrastructure

set -e

echo "🚀 Starting Anna Akka Platform deployment..."

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

# Initialize Pulumi stack if not exists
if ! pulumi stack --show-name &> /dev/null; then
    echo "🏗️  Initializing Pulumi stack..."
    pulumi stack init dev
fi

# Set configuration
echo "⚙️  Setting Pulumi configuration..."
pulumi config set aws:region us-east-1 --stack dev
pulumi config set environment dev --stack dev

echo "✅ Configuration set"

# Preview deployment
echo "👀 Previewing deployment..."
pulumi preview --stack dev

echo ""
echo "📋 Deployment preview completed. Review the changes above."
echo ""
read -p "Do you want to proceed with deployment? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Deploying infrastructure..."
    pulumi up --stack dev --yes
    
    echo ""
    echo "✅ Deployment completed successfully!"
    echo ""
    echo "📊 Getting outputs..."
    pulumi stack output --stack dev
    
    echo ""
    echo "🎉 Anna Akka Platform is now deployed!"
    echo ""
    echo "📝 Next steps:"
    echo "1. Set up your database schema (see README.md)"
    echo "2. Configure your frontend to use the API Gateway URL"
    echo "3. Set up monitoring and alerts"
    echo "4. Test the API endpoints"
    
else
    echo "❌ Deployment cancelled"
    exit 1
fi 