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
    {
        "name": "Margherita Pizza",
        "description": "Classic tomato sauce with fresh mozzarella cheese",
        "price": Decimal('12.99'),
        "unit": "piece",
        "category_id": "pizza",
        "image_url": "https://images.unsplash.com/photo-1604382355076-af4b0eb60143?w=400"
    },
    {
        "name": "Pepperoni Pizza",
        "description": "Spicy pepperoni with melted cheese and tomato sauce",
        "price": Decimal('14.99'),
        "unit": "piece",
        "category_id": "pizza",
        "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400"
    },
    {
        "name": "Chicken Burger",
        "description": "Grilled chicken breast with lettuce, tomato, and special sauce",
        "price": Decimal('8.99'),
        "unit": "piece",
        "category_id": "burger",
        "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58e2?w=400"
    },
    {
        "name": "Beef Burger",
        "description": "Juicy beef patty with cheese, lettuce, and tomato",
        "price": Decimal('9.99'),
        "unit": "piece",
        "category_id": "burger",
        "image_url": "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=400"
    },
    {
        "name": "Caesar Salad",
        "description": "Fresh romaine lettuce with Caesar dressing, croutons, and parmesan",
        "price": Decimal('7.99'),
        "unit": "piece",
        "category_id": "salad",
        "image_url": "https://images.unsplash.com/photo-1546793665-c74683f339c1?w=400"
    },
    {
        "name": "Greek Salad",
        "description": "Mixed greens with feta cheese, olives, cucumber, and olive oil",
        "price": Decimal('6.99'),
        "unit": "piece",
        "category_id": "salad",
        "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400"
    },
    {
        "name": "Chicken Wings",
        "description": "Crispy fried chicken wings with your choice of sauce",
        "price": Decimal('11.99'),
        "unit": "piece",
        "category_id": "appetizer",
        "image_url": "https://images.unsplash.com/photo-1567620832904-9fc6debc209f?w=400"
    },
    {
        "name": "French Fries",
        "description": "Crispy golden fries with sea salt",
        "price": Decimal('4.99'),
        "unit": "piece",
        "category_id": "side",
        "image_url": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400"
    },
    {
        "name": "Onion Rings",
        "description": "Crispy battered onion rings",
        "price": Decimal('5.99'),
        "unit": "piece",
        "category_id": "side",
        "image_url": "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400"
    },
    {
        "name": "Chocolate Milkshake",
        "description": "Rich chocolate milkshake with whipped cream",
        "price": Decimal('6.99'),
        "unit": "piece",
        "category_id": "beverage",
        "image_url": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400"
    },
    {
        "name": "Vanilla Milkshake",
        "description": "Creamy vanilla milkshake with whipped cream",
        "price": Decimal('5.99'),
        "unit": "piece",
        "category_id": "beverage",
        "image_url": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400"
    },
    {
        "name": "Coca Cola",
        "description": "Classic Coca Cola soft drink",
        "price": Decimal('2.99'),
        "unit": "piece",
        "category_id": "beverage",
        "image_url": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400"
    },
    {
        "name": "Pepsi",
        "description": "Refreshing Pepsi soft drink",
        "price": Decimal('2.99'),
        "unit": "piece",
        "category_id": "beverage",
        "image_url": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400"
    },
    {
        "name": "Chocolate Cake",
        "description": "Rich chocolate cake with chocolate frosting",
        "price": Decimal('7.99'),
        "unit": "piece",
        "category_id": "dessert",
        "image_url": "https://images.unsplash.com/photo-1578985545062-6999b3a36d01?w=400"
    },
    {
        "name": "Cheesecake",
        "description": "Creamy New York style cheesecake",
        "price": Decimal('8.99'),
        "unit": "piece",
        "category_id": "dessert",
        "image_url": "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=400"
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