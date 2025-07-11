#!/usr/bin/env python3
"""
Script to update all test files to use the new API endpoint
"""

import os
import re

# New API endpoint
NEW_BASE_URL = "https://z8sre11rwh.execute-api.ap-south-1.amazonaws.com/dev"
OLD_BASE_URL = "https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev"

# Note: This script is now deprecated. Use env_config.py for centralized configuration.

def update_file(file_path):
    """Update a single file to use the new API endpoint"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the old URL with the new one
        updated_content = content.replace(OLD_BASE_URL, NEW_BASE_URL)
        
        if content != updated_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ Updated: {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {str(e)}")
        return False

def main():
    """Update all test files"""
    print("🔄 Updating test files to use new API endpoint")
    print(f"Old URL: {OLD_BASE_URL}")
    print(f"New URL: {NEW_BASE_URL}")
    print("=" * 60)
    
    # List of test files to update
    test_files = [
        "test_auth_integration.py",
        "test_categories_integration.py",
        "test_cart_integration.py",
        "test_stores_integration.py",
        "test_products_integration.py",
        "test_orders_integration.py",
        "test_profile_integration.py",
        "test_otp_integration.py",
        "test_complete_user_flow.py",
        "test_complete_otp_flow.py",
        "test_custom_token_integration.py",
        "test_safe_token_integration.py",
        "test_token_flow_detailed.py",
        "test_auth_endpoints_comprehensive.py",
        "test_phone_otp.py",
        "test_otp_cognito.py",
        "test_config.py",
        "populate_mock_data.py",
        "populate_categories.py",
        "populate_store_product_ids.py"
    ]
    
    updated_count = 0
    total_count = 0
    
    for file_name in test_files:
        if os.path.exists(file_name):
            total_count += 1
            if update_file(file_name):
                updated_count += 1
    
    print("\n" + "=" * 60)
    print("📊 UPDATE SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {total_count}")
    print(f"Files updated: {updated_count}")
    print(f"Files unchanged: {total_count - updated_count}")
    print("=" * 60)
    
    if updated_count > 0:
        print("✅ All test files updated successfully!")
    else:
        print("ℹ️  No files needed updating")

if __name__ == "__main__":
    main() 