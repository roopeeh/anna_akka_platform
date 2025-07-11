#!/usr/bin/env python3
"""
Deployment script for Anna Akka Platform - Modular Structure

This script helps manage the modular Pulumi infrastructure deployment.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Anna Akka Platform - Modular Deployment")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("__main__.py"):
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Check if infrastructure modules exist
    if not os.path.exists("infrastructure"):
        print("❌ Error: Infrastructure modules not found. Please ensure the modular structure is set up.")
        sys.exit(1)
    
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
            sys.exit(1)
    
    print("✅ Modular structure validated")
    
    # Ask user what they want to do
    print("\n📋 Available actions:")
    print("1. Preview changes (dry run)")
    print("2. Deploy infrastructure")
    print("3. Destroy infrastructure")
    print("4. Show current stack")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        success = run_command("pulumi preview", "Previewing infrastructure changes")
        if success:
            print("\n💡 To apply these changes, run: python deploy_modular.py and choose option 2")
    
    elif choice == "2":
        print("\n⚠️  WARNING: This will deploy/update infrastructure resources")
        confirm = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
        if confirm == "yes":
            success = run_command("pulumi up --yes", "Deploying infrastructure")
            if success:
                print("\n🎉 Deployment completed successfully!")
                print("📊 Run 'pulumi stack output' to see your API endpoints")
        else:
            print("❌ Deployment cancelled")
    
    elif choice == "3":
        print("\n⚠️  WARNING: This will destroy ALL infrastructure resources")
        confirm = input("Are you sure you want to destroy everything? (yes/no): ").strip().lower()
        if confirm == "yes":
            success = run_command("pulumi destroy --yes", "Destroying infrastructure")
            if success:
                print("\n🗑️  Infrastructure destroyed successfully")
        else:
            print("❌ Destruction cancelled")
    
    elif choice == "4":
        success = run_command("pulumi stack", "Showing current stack")
        if success:
            print("\n📊 Run 'pulumi stack output' to see outputs")
    
    elif choice == "5":
        print("👋 Goodbye!")
        sys.exit(0)
    
    else:
        print("❌ Invalid choice. Please enter a number between 1-5")
        sys.exit(1)

if __name__ == "__main__":
    main() 