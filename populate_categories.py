#!/usr/bin/env python3
"""
Script to populate categories with predefined IDs.
This creates the 4 main categories for the grocery platform.

Usage:
    python populate_categories.py                    # Populate categories
    python populate_categories.py --clear            # Clear all categories
    python populate_categories.py --list             # List all categories
"""

import requests
import json
import argparse
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev"

# Headers for API requests
HEADERS = {
    "Content-Type": "application/json"
}

# Predefined categories with specific IDs
CATEGORIES = [
    {"name": "Rice & More", "id": "1"},
    {"name": "Household Essentials", "id": "2"},
    {"name": "Personal Care", "id": "3"},
    {"name": "Snacks & Beverages", "id": "4"}
]

def make_request(method, endpoint, data=None):
    """Make API request with error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=HEADERS)
        elif method.upper() == "POST":
            response = requests.post(url, headers=HEADERS, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=HEADERS)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_body = e.response.json()
                logger.error(f"Error response: {error_body}")
            except:
                logger.error(f"Error status: {e.response.status_code}")
        return None

def populate_categories():
    """Populate categories with predefined IDs"""
    logger.info("Populating categories...")
    
    success_count = 0
    error_count = 0
    
    for category in CATEGORIES:
        category_name = category['name']
        category_id = category['id']
        
        # Create category data
        category_data = {
            "name": category_name,
            "id": category_id
        }
        
        # Make API call to create category
        response = make_request("POST", "/categories", category_data)
        if response:
            logger.info(f"✅ Created category: {category_name} with ID: {category_id}")
            success_count += 1
        else:
            logger.error(f"❌ Failed to create category: {category_name}")
            error_count += 1
    
    logger.info(f"\nCategory population complete!")
    logger.info(f"Successfully created: {success_count} categories")
    logger.info(f"Errors: {error_count} categories")
    
    if error_count == 0:
        logger.info("✅ All categories created successfully!")
    else:
        logger.warning("⚠️  Some categories failed to create. Check the errors above.")

def clear_categories():
    """Clear all categories"""
    logger.info("Clearing all categories...")
    
    # Get all categories first
    response = make_request("GET", "/categories")
    if response and isinstance(response, dict) and 'body' in response:
        try:
            categories_data = json.loads(response['body'])
            categories = categories_data.get('categories', [])
            
            if not categories:
                logger.info("ℹ️  No categories found to clear.")
                return
            
            logger.info(f"Found {len(categories)} categories to delete...")
            
            deleted_count = 0
            error_count = 0
            
            for category in categories:
                category_id = category.get('id')
                category_name = category.get('name', 'Unknown')
                
                if category_id:
                    delete_response = make_request("DELETE", f"/categories/{category_id}")
                    if delete_response:
                        logger.info(f"🗑️  Deleted category: {category_name} (ID: {category_id})")
                        deleted_count += 1
                    else:
                        logger.error(f"❌ Failed to delete category: {category_name}")
                        error_count += 1
            
            logger.info(f"Cleared {deleted_count} categories")
            if error_count > 0:
                logger.warning(f"Failed to delete {error_count} categories")
                
        except json.JSONDecodeError:
            logger.error("Failed to parse categories response")
    else:
        logger.error("Failed to get categories list")

def list_categories():
    """List all categories"""
    logger.info("Listing all categories...")
    
    response = make_request("GET", "/categories")
    if response and isinstance(response, dict) and 'body' in response:
        try:
            categories_data = json.loads(response['body'])
            categories = categories_data.get('categories', [])
            
            if not categories:
                logger.info("ℹ️  No categories found.")
                return
            
            logger.info(f"Found {len(categories)} categories:")
            for i, category in enumerate(categories, 1):
                category_id = category.get('id', 'N/A')
                category_name = category.get('name', 'Unknown')
                created_at = category.get('created_at', 'N/A')
                logger.info(f"{i}. ID: {category_id} | Name: {category_name} | Created: {created_at}")
                
        except json.JSONDecodeError:
            logger.error("Failed to parse categories response")
    else:
        logger.error("Failed to get categories list")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Populate categories for Anna Akka Platform")
    parser.add_argument("--clear", action="store_true", help="Clear all categories")
    parser.add_argument("--list", action="store_true", help="List all categories")
    
    args = parser.parse_args()
    
    try:
        if args.clear:
            clear_categories()
        elif args.list:
            list_categories()
        else:
            populate_categories()
            
    except Exception as e:
        logger.error(f"Script error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 