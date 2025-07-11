#!/usr/bin/env python3
"""
Anna Akka Platform - Dev Branch Deployment Script
Deploys infrastructure in ap-south-1 region for the dev branch
"""

import os
import sys
import subprocess
import json

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔄 {description}...")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("📋 Checking prerequisites...")
    
    # Check if we're in the right directory
    if not os.path.exists("__main__.py"):
        print("❌ Error: Please run this script from the project root directory")
        return False
    
    # Check if infrastructure modules exist
    if not os.path.exists("infrastructure"):
        print("❌ Error: Infrastructure modules not found. Please ensure the modular structure is set up.")
        return False
    
    # Validate the structure
    required_files = [
        "infrastructure/__init__.py",
        "infrastructure/database.py",
        "infrastructure/lambda_functions.py",
        "infrastructure/api_gateway.py"
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Error: Required file {file} not found")
            return False
    
    print("✅ Modular structure validated")
    return True

def check_git_branch():
    """Check if we're on the dev branch"""
    print("🌿 Checking git branch...")
    
    try:
        result = subprocess.run("git branch --show-current", shell=True, check=True, capture_output=True, text=True)
        current_branch = result.stdout.strip()
        
        if current_branch != "dev":
            print(f"⚠️  Warning: You're not on the dev branch. Current branch: {current_branch}")
            response = input("Do you want to continue anyway? (y/N): ").strip().lower()
            if response != "y":
                print("❌ Deployment cancelled")
                return False
        else:
            print(f"✅ Currently on dev branch: {current_branch}")
        
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Warning: Could not determine git branch. Continuing...")
        return True

def main():
    """Main deployment function"""
    print("🚀 Anna Akka Platform - DEV Branch Deployment (ap-south-1)")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Check git branch
    if not check_git_branch():
        sys.exit(1)
    
    # Ask user what they want to do
    print("\n📋 Available actions:")
    print("1. Preview changes for ap-south-1 (dry run)")
    print("2. Deploy infrastructure in ap-south-1")
    print("3. Destroy infrastructure in ap-south-1")
    print("4. Show current stack")
    print("5. Configure stack for ap-south-1")
    print("6. Exit")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        success = run_command("pulumi preview --stack dev-stack-ap-south-1", "Previewing infrastructure changes for ap-south-1")
        if success:
            print("\n💡 To apply these changes, run: python deploy_dev_modular.py and choose option 2")
    
    elif choice == "2":
        print("\n⚠️  WARNING: This will deploy/update infrastructure resources in ap-south-1")
        confirm = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
        if confirm == "yes":
            success = run_command("pulumi up --yes --stack dev-stack-ap-south-1", "Deploying infrastructure in ap-south-1")
            if success:
                print("\n🎉 Deployment completed successfully in ap-south-1!")
                print("📊 Run 'pulumi stack output --stack dev-stack-ap-south-1' to see your API endpoints")
        else:
            print("❌ Deployment cancelled")
    
    elif choice == "3":
        print("\n⚠️  WARNING: This will destroy ALL infrastructure resources in ap-south-1")
        confirm = input("Are you sure you want to destroy everything? (yes/no): ").strip().lower()
        if confirm == "yes":
            success = run_command("pulumi destroy --yes --stack dev-stack-ap-south-1", "Destroying infrastructure in ap-south-1")
            if success:
                print("\n🗑️  Infrastructure destroyed successfully in ap-south-1")
        else:
            print("❌ Destruction cancelled")
    
    elif choice == "4":
        success = run_command("pulumi stack --stack dev-stack-ap-south-1", "Showing current stack")
        if success:
            print("\n📊 Run 'pulumi stack output --stack dev-stack-ap-south-1' to see outputs")
    
    elif choice == "5":
        print("\n⚙️  Configuring stack for ap-south-1...")
        success1 = run_command("pulumi config set aws:region ap-south-1 --stack dev-stack-ap-south-1", "Setting AWS region to ap-south-1")
        success2 = run_command("pulumi config set environment dev --stack dev-stack-ap-south-1", "Setting environment to dev")
        if success1 and success2:
            print("✅ Stack configured for ap-south-1 region")
    
    elif choice == "6":
        print("👋 Goodbye!")
        sys.exit(0)
    
    else:
        print("❌ Invalid choice. Please enter a number between 1-6")
        sys.exit(1)

if __name__ == "__main__":
    main() 