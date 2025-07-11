#!/usr/bin/env python3
"""
Anna Akka Platform - Fast Dev Deployment Script
Optimized for quick deployment in ap-south-1
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

def cleanup_existing_resources():
    """Clean up existing resources that might conflict"""
    print("🧹 Cleaning up existing resources...")
    
    # List and delete existing IAM roles
    try:
        roles = subprocess.run("aws iam list-roles --query 'Roles[?contains(RoleName, `anna-akka-platform`)].RoleName' --output text", 
                             shell=True, capture_output=True, text=True)
        if roles.stdout.strip():
            for role in roles.stdout.strip().split('\t'):
                if role:
                    print(f"Deleting IAM role: {role}")
                    subprocess.run(f"aws iam delete-role --role-name {role}", shell=True, capture_output=True)
    except:
        pass
    
    # List and delete existing IAM policies
    try:
        policies = subprocess.run("aws iam list-policies --query 'Policies[?contains(PolicyName, `anna-akka-platform`)].PolicyName' --output text", 
                                shell=True, capture_output=True, text=True)
        if policies.stdout.strip():
            for policy in policies.stdout.strip().split('\t'):
                if policy:
                    print(f"Deleting IAM policy: {policy}")
                    subprocess.run(f"aws iam delete-policy --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/{policy}", 
                                 shell=True, capture_output=True)
    except:
        pass

def main():
    """Main deployment function"""
    print("🚀 Anna Akka Platform - FAST DEV Deployment (ap-south-1)")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("__main__.py"):
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
    
    # Clean up existing resources
    cleanup_existing_resources()
    
    # Initialize stack
    if not run_command("pulumi stack init dev-stack-ap-south-1", "Initializing stack"):
        print("ℹ️  Stack might already exist, continuing...")
    
    # Configure stack
    if not run_command("pulumi config set aws:region ap-south-1 --stack dev-stack-ap-south-1", "Setting AWS region"):
        sys.exit(1)
    
    if not run_command("pulumi config set environment dev --stack dev-stack-ap-south-1", "Setting environment"):
        sys.exit(1)
    
    # Preview with timeout
    print("\n👀 Previewing deployment (this may take a few minutes)...")
    if not run_command("pulumi preview --stack dev-stack-ap-south-1", "Previewing deployment"):
        print("❌ Preview failed")
        sys.exit(1)
    
    # Ask for confirmation
    print("\n📋 Deployment preview completed.")
    confirm = input("Do you want to proceed with deployment? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        print("\n🚀 Starting deployment...")
        start_time = time.time()
        
        # Deploy with progress monitoring
        if run_command("pulumi up --yes --stack dev-stack-ap-south-1", "Deploying infrastructure"):
            end_time = time.time()
            duration = end_time - start_time
            print(f"\n🎉 Deployment completed successfully in {duration:.1f} seconds!")
            
            # Get outputs
            print("\n📊 Getting outputs...")
            run_command("pulumi stack output --stack dev-stack-ap-south-1", "Getting stack outputs")
            
            print(f"\n✅ Infrastructure deployed in ap-south-1!")
            print(f"⏱️  Total deployment time: {duration:.1f} seconds")
        else:
            print("❌ Deployment failed")
            sys.exit(1)
    else:
        print("❌ Deployment cancelled")
        sys.exit(1)

if __name__ == "__main__":
    main() 