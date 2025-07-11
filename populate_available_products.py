#!/usr/bin/env python3
"""
Script to populate the available products table with initial data.
This creates a catalog of products that stores can add to their inventory.

Usage:
    python populate_available_products.py                    # Populate available products
    python populate_available_products.py --clear            # Clear all available products
    python populate_available_products.py --list             # List all available products
"""

import boto3
import json
import os
import argparse
from datetime import datetime, UTC
import uuid
from decimal import Decimal

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Get table name from environment or use default
table_name = os.environ.get('AVAILABLE_PRODUCTS_TABLE', 'anna-akka-platform-available-products-table')
available_products_table = dynamodb.Table(table_name)  # type: ignore

# Sample available products data
available_products = [
    # Rice & More Category (ID: 1)
    {
        "name": "Basmati Rice",
        "description": "Premium long grain basmati rice",
        "price": Decimal('120.00'),
        "unit": "kg",
        "category_id": "1",
        "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400"
    },
    {
        "name": "Toor Dal",
        "description": "Yellow pigeon peas",
        "price": Decimal('140.00'),
        "unit": "kg",
        "category_id": "1",
        "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400"
    },
    {
        "name": "Moong Dal",
        "description": "Green gram split",
        "price": Decimal('160.00'),
        "unit": "kg",
        "category_id": "1",
        "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400"
    },
    {
        "name": "Urad Dal",
        "description": "Black gram split",
        "price": Decimal('150.00'),
        "unit": "kg",
        "category_id": "1",
        "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400"
    },
    {
        "name": "Chana Dal",
        "description": "Bengal gram split",
        "price": Decimal('130.00'),
        "unit": "kg",
        "category_id": "1",
        "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400"
    },
    {
        "name": "Masoor Dal",
        "description": "Red lentils",
        "price": Decimal('120.00'),
        "unit": "kg",
        "category_id": "1",
        "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400"
    },
    
    # Household Essentials Category (ID: 2)
    {
        "name": "Detergent Powder",
        "description": "Washing powder for clothes",
        "price": Decimal('180.00'),
        "unit": "kg",
        "category_id": "2",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"
    },
    {
        "name": "Dish Wash Liquid",
        "description": "Liquid dish cleaner",
        "price": Decimal('120.00'),
        "unit": "liter",
        "category_id": "2",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"
    },
    {
        "name": "Floor Cleaner",
        "description": "Multi-surface floor cleaner",
        "price": Decimal('95.00'),
        "unit": "liter",
        "category_id": "2",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"
    },
    {
        "name": "Toilet Cleaner",
        "description": "Bathroom cleaning solution",
        "price": Decimal('85.00'),
        "unit": "liter",
        "category_id": "2",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"
    },
    {
        "name": "Glass Cleaner",
        "description": "Window and glass cleaner",
        "price": Decimal('75.00'),
        "unit": "liter",
        "category_id": "2",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"
    },
    {
        "name": "Air Freshener",
        "description": "Room freshener spray",
        "price": Decimal('150.00'),
        "unit": "piece",
        "category_id": "2",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"
    },
    
    # Personal Care Category (ID: 3)
    {
        "name": "Bathing Soap",
        "description": "Natural bathing soap",
        "price": Decimal('45.00'),
        "unit": "piece",
        "category_id": "3",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400"
    },
    {
        "name": "Shampoo",
        "description": "Hair care shampoo",
        "price": Decimal('180.00'),
        "unit": "liter",
        "category_id": "3",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400"
    },
    {
        "name": "Toothpaste",
        "description": "Dental care toothpaste",
        "price": Decimal('95.00'),
        "unit": "piece",
        "category_id": "3",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400"
    },
    {
        "name": "Toothbrush",
        "description": "Soft bristle toothbrush",
        "price": Decimal('35.00'),
        "unit": "piece",
        "category_id": "3",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400"
    },
    {
        "name": "Deodorant",
        "description": "Body deodorant spray",
        "price": Decimal('120.00'),
        "unit": "piece",
        "category_id": "3",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400"
    },
    {
        "name": "Hair Oil",
        "description": "Natural hair oil",
        "price": Decimal('85.00'),
        "unit": "liter",
        "category_id": "3",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400"
    },
    
    # Snacks & Beverages Category (ID: 4)
    {
        "name": "Potato Chips",
        "description": "Crispy potato chips",
        "price": Decimal('20.00'),
        "unit": "pack",
        "category_id": "4",
        "image_url": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400"
    },
    {
        "name": "Mixed Nuts",
        "description": "Assorted dry fruits and nuts",
        "price": Decimal('350.00'),
        "unit": "kg",
        "category_id": "4",
        "image_url": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400"
    },
    {
        "name": "Biscuits",
        "description": "Cream biscuits",
        "price": Decimal('25.00'),
        "unit": "pack",
        "category_id": "4",
        "image_url": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400"
    },
    {
        "name": "Popcorn",
        "description": "Butter flavored popcorn",
        "price": Decimal('15.00'),
        "unit": "pack",
        "category_id": "4",
        "image_url": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400"
    },
    {
        "name": "Chocolate",
        "description": "Dark chocolate bar",
        "price": Decimal('150.00'),
        "unit": "pack",
        "category_id": "4",
        "image_url": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400"
    },
    {
        "name": "Tea Bags",
        "description": "Assam tea bags",
        "price": Decimal('180.00'),
        "unit": "pack",
        "category_id": "4",
        "image_url": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400"
    },
    {
        "name": "Coffee Powder",
        "description": "Filter coffee powder",
        "price": Decimal('250.00'),
        "unit": "kg",
        "category_id": "4",
        "image_url": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400"
    },
    {
        "name": "Juice Pack",
        "description": "Mixed fruit juice",
        "price": Decimal('80.00'),
        "unit": "liter",
        "category_id": "4",
        "image_url": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400"
    },
    {
        "name": "Soft Drink",
        "description": "Carbonated soft drink",
        "price": Decimal('30.00'),
        "unit": "bottle",
        "category_id": "4",
        "image_url": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400"
    },
    {
        "name": "Mineral Water",
        "description": "Pure mineral water",
        "price": Decimal('20.00'),
        "unit": "liter",
        "category_id": "4",
        "image_url": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400"
    }
]

def populate_available_products():
    """Populate the available products table with initial data"""
    print(f"Populating available products table: {table_name}")
    
    success_count = 0
    error_count = 0
    
    for product_data in available_products:
        try:
            # Generate unique ID and timestamp
            product_id = str(uuid.uuid4())
            timestamp = datetime.now(UTC).isoformat()
            
            # Create product item
            product_item = {
                'id': product_id,
                'name': product_data['name'],
                'description': product_data['description'],
                'price': product_data['price'],
                'unit': product_data['unit'],
                'category_id': product_data['category_id'],
                'image_url': product_data['image_url'],
                'created_at': timestamp,
                'updated_at': timestamp
            }
            
            # Add to DynamoDB
            available_products_table.put_item(Item=product_item)
            print(f"✓ Added: {product_data['name']} (ID: {product_id})")
            success_count += 1
            
        except Exception as e:
            print(f"✗ Error adding {product_data['name']}: {str(e)}")
            error_count += 1
    
    print(f"\nPopulation complete!")
    print(f"Successfully added: {success_count} products")
    print(f"Errors: {error_count} products")
    
    if error_count == 0:
        print("✅ All products added successfully!")
    else:
        print("⚠️  Some products failed to add. Check the errors above.")

def clear_available_products():
    """Clear all available products from the table"""
    print(f"Clearing all available products from table: {table_name}")
    
    try:
        # Scan the table to get all items
        response = available_products_table.scan()
        items = response.get('Items', [])
        
        if not items:
            print("ℹ️  No available products found to clear.")
            return
        
        print(f"Found {len(items)} available products to delete...")
        
        deleted_count = 0
        error_count = 0
        
        for item in items:
            try:
                product_id = item['id']
                product_name = item.get('name', 'Unknown')
                
                # Delete the item
                available_products_table.delete_item(Key={'id': product_id})
                print(f"🗑️  Deleted: {product_name} (ID: {product_id})")
                deleted_count += 1
                
            except Exception as e:
                print(f"✗ Error deleting {item.get('name', 'Unknown')}: {str(e)}")
                error_count += 1
        
        print(f"\nClear operation complete!")
        print(f"Successfully deleted: {deleted_count} products")
        print(f"Errors: {error_count} products")
        
        if error_count == 0:
            print("✅ All available products cleared successfully!")
        else:
            print("⚠️  Some products failed to delete. Check the errors above.")
            
    except Exception as e:
        print(f"✗ Error scanning table: {str(e)}")

def list_available_products():
    """List all available products in the table"""
    print(f"Listing all available products from table: {table_name}")
    
    try:
        # Scan the table to get all items
        response = available_products_table.scan()
        items = response.get('Items', [])
        
        if not items:
            print("ℹ️  No available products found in the table.")
            return
        
        print(f"\nFound {len(items)} available products:")
        print("=" * 80)
        
        for i, item in enumerate(items, 1):
            print(f"{i:2d}. {item.get('name', 'Unknown')}")
            print(f"     ID: {item.get('id', 'N/A')}")
            print(f"     Price: ${item.get('price', 'N/A')}")
            print(f"     Category: {item.get('category_id', 'N/A')}")
            print(f"     Unit: {item.get('unit', 'N/A')}")
            print(f"     Description: {item.get('description', 'N/A')}")
            print()
        
        print("=" * 80)
        print(f"Total: {len(items)} available products")
        
    except Exception as e:
        print(f"✗ Error listing products: {str(e)}")

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Populate or manage available products table')
    parser.add_argument('--clear', action='store_true', help='Clear all available products from the table')
    parser.add_argument('--list', action='store_true', help='List all available products in the table')
    
    args = parser.parse_args()
    
    try:
        if args.clear:
            print("🗑️  Clearing all available products...")
            clear_available_products()
        elif args.list:
            print("📋 Listing all available products...")
            list_available_products()
        else:
            print("📝 Populating available products table...")
            populate_available_products()
    except Exception as e:
        print(f"Script error: {str(e)}")
        exit(1) 
        exit(1) 