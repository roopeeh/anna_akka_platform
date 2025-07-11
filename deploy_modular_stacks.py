#!/usr/bin/env python3
"""
Anna Akka Platform - Modular Stack Deployment Script
Deploy infrastructure in smaller, manageable stacks
"""

import os
import sys
import subprocess
import json
import time

def run_command(command, description, check_output=False):
    """Run a command and return success status"""
    print(f"\n🔄 {description}...")
    print(f"Command: {command}")
    
    try:
        if check_output:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, timeout=300)
            print(f"✅ {description} completed successfully")
            return result.stdout.strip()
        else:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, timeout=300)
            print(f"✅ {description} completed successfully")
            return True
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out after 5 minutes")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def deploy_stack(stack_name, stack_file, description):
    """Deploy a specific stack"""
    print(f"\n🚀 {description}")
    print("=" * 50)
    
    # Initialize stack if not exists
    if not run_command(f"pulumi stack init {stack_name}", f"Initializing {stack_name} stack"):
        print(f"ℹ️  Stack {stack_name} might already exist, continuing...")
    
    # Configure stack
    if not run_command(f"pulumi config set aws:region ap-south-1 --stack {stack_name}", f"Setting AWS region for {stack_name}"):
        return False
    
    if not run_command(f"pulumi config set environment dev --stack {stack_name}", f"Setting environment for {stack_name}"):
        return False
    
    # Preview deployment
    print(f"\n👀 Previewing {stack_name} deployment...")
    if not run_command(f"pulumi preview --stack {stack_name}", f"Previewing {stack_name}"):
        return False
    
    # Ask for confirmation
    confirm = input(f"\nDo you want to deploy {stack_name}? (yes/no): ").strip().lower()
    if confirm != "yes":
        print(f"❌ {stack_name} deployment cancelled")
        return False
    
    # Deploy
    start_time = time.time()
    if run_command(f"pulumi up --yes --stack {stack_name}", f"Deploying {stack_name}"):
        end_time = time.time()
        duration = end_time - start_time
        print(f"✅ {stack_name} deployed successfully in {duration:.1f} seconds!")
        return True
    else:
        print(f"❌ {stack_name} deployment failed")
        return False

def main():
    """Main deployment function"""
    print("🚀 Anna Akka Platform - Modular Stack Deployment")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("__main__modular.py"):
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Check AWS credentials
    if not run_command("aws sts get-caller-identity", "Checking AWS credentials"):
        print("❌ AWS credentials not configured. Please run 'aws configure' first.")
        sys.exit(1)
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Define stacks to deploy
    stacks = [
        {
            "name": "dev-vpc-stack",
            "file": "stacks/vpc_stack.py",
            "description": "VPC and Networking Infrastructure"
        },
        {
            "name": "dev-database-stack", 
            "file": "stacks/database_stack.py",
            "description": "Database (DynamoDB) Infrastructure"
        },
        {
            "name": "dev-iam-stack",
            "file": "stacks/iam_stack.py", 
            "description": "IAM Roles and Policies"
        },
        {
            "name": "dev-cognito-stack",
            "file": "stacks/cognito_stack.py",
            "description": "Cognito Authentication"
        },
        {
            "name": "dev-lambda-stack",
            "file": "stacks/lambda_stack.py",
            "description": "Lambda Functions"
        },
        {
            "name": "dev-api-gateway-stack",
            "file": "stacks/api_gateway_stack.py",
            "description": "API Gateway and Routes"
        }
    ]
    
    # Ask user what they want to do
    print("\n📋 Available options:")
    print("1. Deploy all stacks sequentially")
    print("2. Deploy specific stack")
    print("3. Deploy complete infrastructure (monolithic)")
    print("4. Show stack status")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        print("\n🚀 Deploying all stacks sequentially...")
        for stack in stacks:
            if not deploy_stack(stack["name"], stack["file"], stack["description"]):
                print(f"❌ Failed to deploy {stack['name']}. Stopping deployment.")
                sys.exit(1)
        print("\n🎉 All stacks deployed successfully!")
        
    elif choice == "2":
        print("\n📋 Available stacks:")
        for i, stack in enumerate(stacks, 1):
            print(f"{i}. {stack['name']} - {stack['description']}")
        
        stack_choice = input("\nEnter stack number (1-6): ").strip()
        try:
            stack_index = int(stack_choice) - 1
            if 0 <= stack_index < len(stacks):
                stack = stacks[stack_index]
                deploy_stack(stack["name"], stack["file"], stack["description"])
            else:
                print("❌ Invalid stack number")
        except ValueError:
            print("❌ Invalid input")
    
    elif choice == "3":
        print("\n🚀 Deploying complete infrastructure (monolithic)...")
        if not deploy_stack("dev-stack-ap-south-1", "__main__modular.py", "Complete Infrastructure"):
            print("❌ Complete infrastructure deployment failed")
            sys.exit(1)
        print("\n🎉 Complete infrastructure deployed successfully!")
    
    elif choice == "4":
        print("\n📊 Stack Status:")
        run_command("pulumi stack ls", "Listing all stacks")
    
    elif choice == "5":
        print("👋 Goodbye!")
        sys.exit(0)
    
    else:
        print("❌ Invalid choice. Please enter a number between 1-5")
        sys.exit(1)

if __name__ == "__main__":
    main() 