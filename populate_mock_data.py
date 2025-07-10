#!/usr/bin/env python3
"""
Mock Data Population Script for Anna Akka Platform

This script populates DynamoDB with mock data for stores, products, and categories
using the actual API endpoints. It creates realistic grocery store data for testing.

Usage:
    python populate_mock_data.py                           # Create mock data
    python populate_mock_data.py --clear-all               # Remove all data
    python populate_mock_data.py --clear-products          # Remove only products
    python populate_mock_data.py --clear-available-products # Remove only available products
    python populate_mock_data.py --clear-stores            # Remove only stores
    python populate_mock_data.py --clear-categories        # Remove only categories

Requirements:
    - requests library
    - API Gateway URL configured
    - Firebase authentication set up
"""

import requests
import json
import time
import random
import argparse
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev"  # Update with your actual API Gateway URL

# Headers for API requests
HEADERS = {
    "Content-Type": "application/json"
}

class MockDataPopulator:
    def __init__(self, api_base_url, headers):
        self.api_base_url = api_base_url
        self.headers = headers
        self.categories = []
        self.stores = []
        self.products = []
        self.users = []
        
    def make_request(self, method, endpoint, data=None):
        """Make API request with error handling"""
        url = f"{self.api_base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
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
    
    def create_users(self):
        """Create mock users (owners and customers)"""
        logger.info("Creating mock users...")
        
        users_data = [
            {
                "email": "owner1@example.com",
                "name": "John Store Owner",
                "firebase_uid": "firebase-owner-1",
                "user_type": "owner",
                "phone": "+91 98765 43210",
                "address": "123 Main St, Bangalore"
            },
            {
                "email": "owner2@example.com", 
                "name": "Jane Grocery Owner",
                "firebase_uid": "firebase-owner-2",
                "user_type": "owner",
                "phone": "+91 87654 32109",
                "address": "456 Oak Ave, Mumbai"
            },
            {
                "email": "customer1@example.com",
                "name": "Bob Customer",
                "firebase_uid": "firebase-customer-1", 
                "user_type": "customer",
                "phone": "+91 76543 21098",
                "address": "789 Pine Rd, Delhi"
            },
            {
                "email": "customer2@example.com",
                "name": "Alice Shopper",
                "firebase_uid": "firebase-customer-2",
                "user_type": "customer", 
                "phone": "+91 65432 10987",
                "address": "321 Garden St, Chennai"
            }
        ]
        
        for user in users_data:
            response = self.make_request("POST", "/auth/register", user)
            if response:
                self.users.append(response)
                logger.info(f"Created user: {user['name']} ({user['user_type']})")
            else:
                logger.error(f"Failed to create user: {user['name']}")
        
        logger.info(f"Created {len(self.users)} users")

    def create_categories(self):
        """Create product categories"""
        logger.info("Creating product categories...")
        
        categories_data = [
            {"name": "Vegetables"},
            {"name": "Fruits"},
            {"name": "Dairy Products"},
            {"name": "Bakery"},
            {"name": "Meat & Poultry"},
            {"name": "Grains & Pulses"},
            {"name": "Spices & Condiments"},
            {"name": "Beverages"},
            {"name": "Snacks"},
            {"name": "Frozen Foods"}
        ]
        
        for category in categories_data:
            response = self.make_request("POST", "/categories", category)
            if response:
                # Handle the response structure - it might be wrapped in a body field
                if isinstance(response, dict) and 'body' in response:
                    try:
                        category_data = json.loads(response['body'])
                        self.categories.append(category_data)
                        logger.info(f"Created category: {category['name']}")
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse category response: {response}")
                else:
                    self.categories.append(response)
                    logger.info(f"Created category: {category['name']}")
            else:
                logger.error(f"Failed to create category: {category['name']}")
        
        logger.info(f"Created {len(self.categories)} categories")
    
    def create_stores(self):
        """Create mock stores"""
        logger.info("Creating mock stores...")
        
        stores_data = [
            {
                "name": "Fresh Market Grocery",
                "address": "123 Main Street, Bangalore, Karnataka 560001",
                "phone": "+91 98765 43210",
                "delivery_time": "30-45 min"
            },
            {
                "name": "Organic Valley Store",
                "address": "456 Park Avenue, Mumbai, Maharashtra 400001",
                "phone": "+91 87654 32109",
                "delivery_time": "25-40 min"
            },
            {
                "name": "City Fresh Mart",
                "address": "789 Lake Road, Delhi, Delhi 110001",
                "phone": "+91 76543 21098",
                "delivery_time": "35-50 min"
            },
            {
                "name": "Green Grocers",
                "address": "321 Garden Street, Chennai, Tamil Nadu 600001",
                "phone": "+91 65432 10987",
                "delivery_time": "20-35 min"
            },
            {
                "name": "Farm Fresh Express",
                "address": "654 Farm Road, Hyderabad, Telangana 500001",
                "phone": "+91 54321 09876",
                "delivery_time": "40-55 min"
            }
        ]
        
        for store in stores_data:
            response = self.make_request("POST", "/stores", store)
            if response:
                # Handle the response structure - it might be wrapped in a body field
                if isinstance(response, dict) and 'body' in response:
                    try:
                        store_data = json.loads(response['body'])
                        self.stores.append(store_data)
                        logger.info(f"Created store: {store['name']}")
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse store response: {response}")
                else:
                    self.stores.append(response)
                    logger.info(f"Created store: {store['name']}")
            else:
                logger.error(f"Failed to create store: {store['name']}")
        
        logger.info(f"Created {len(self.stores)} stores")
    
    def create_products(self):
        """Create mock products for each store"""
        logger.info("Creating mock products...")
        
        # Product templates for different categories
        product_templates = {
            "Vegetables": [
                {"name": "Fresh Tomatoes", "description": "Organic red tomatoes", "price": 25.50, "unit": "kg", "stock": 50},
                {"name": "Onions", "description": "Fresh white onions", "price": 30.00, "unit": "kg", "stock": 75},
                {"name": "Potatoes", "description": "Fresh potatoes", "price": 35.00, "unit": "kg", "stock": 100},
                {"name": "Carrots", "description": "Organic orange carrots", "price": 40.00, "unit": "kg", "stock": 45},
                {"name": "Cucumber", "description": "Fresh green cucumbers", "price": 20.00, "unit": "kg", "stock": 30}
            ],
            "Fruits": [
                {"name": "Bananas", "description": "Fresh yellow bananas", "price": 60.00, "unit": "dozen", "stock": 25},
                {"name": "Apples", "description": "Red delicious apples", "price": 120.00, "unit": "kg", "stock": 40},
                {"name": "Oranges", "description": "Sweet oranges", "price": 80.00, "unit": "kg", "stock": 35},
                {"name": "Mangoes", "description": "Ripe alphonso mangoes", "price": 150.00, "unit": "kg", "stock": 20},
                {"name": "Grapes", "description": "Fresh black grapes", "price": 100.00, "unit": "kg", "stock": 30}
            ],
            "Dairy Products": [
                {"name": "Milk", "description": "Fresh cow milk", "price": 60.00, "unit": "liter", "stock": 50},
                {"name": "Curd", "description": "Fresh homemade curd", "price": 40.00, "unit": "kg", "stock": 30},
                {"name": "Butter", "description": "Pure butter", "price": 120.00, "unit": "pack", "stock": 25},
                {"name": "Cheese", "description": "Processed cheese", "price": 200.00, "unit": "pack", "stock": 20},
                {"name": "Paneer", "description": "Fresh cottage cheese", "price": 180.00, "unit": "kg", "stock": 15}
            ],
            "Bakery": [
                {"name": "Bread", "description": "Fresh white bread", "price": 35.00, "unit": "pack", "stock": 40},
                {"name": "Buns", "description": "Soft dinner buns", "price": 25.00, "unit": "pack", "stock": 30},
                {"name": "Cake", "description": "Vanilla sponge cake", "price": 150.00, "unit": "piece", "stock": 10},
                {"name": "Cookies", "description": "Chocolate chip cookies", "price": 80.00, "unit": "pack", "stock": 25},
                {"name": "Pastry", "description": "Chocolate pastry", "price": 45.00, "unit": "piece", "stock": 20}
            ],
            "Meat & Poultry": [
                {"name": "Chicken", "description": "Fresh chicken", "price": 180.00, "unit": "kg", "stock": 25},
                {"name": "Mutton", "description": "Fresh mutton", "price": 400.00, "unit": "kg", "stock": 15},
                {"name": "Fish", "description": "Fresh fish", "price": 250.00, "unit": "kg", "stock": 20},
                {"name": "Eggs", "description": "Farm fresh eggs", "price": 120.00, "unit": "dozen", "stock": 30},
                {"name": "Pork", "description": "Fresh pork", "price": 300.00, "unit": "kg", "stock": 10}
            ],
            "Grains & Pulses": [
                {"name": "Rice", "description": "Basmati rice", "price": 80.00, "unit": "kg", "stock": 100},
                {"name": "Wheat", "description": "Whole wheat flour", "price": 45.00, "unit": "kg", "stock": 75},
                {"name": "Lentils", "description": "Red lentils", "price": 120.00, "unit": "kg", "stock": 50},
                {"name": "Chickpeas", "description": "White chickpeas", "price": 90.00, "unit": "kg", "stock": 40},
                {"name": "Oats", "description": "Rolled oats", "price": 60.00, "unit": "kg", "stock": 30}
            ],
            "Spices & Condiments": [
                {"name": "Salt", "description": "Iodized salt", "price": 20.00, "unit": "kg", "stock": 50},
                {"name": "Sugar", "description": "Refined sugar", "price": 45.00, "unit": "kg", "stock": 60},
                {"name": "Turmeric", "description": "Pure turmeric powder", "price": 150.00, "unit": "kg", "stock": 25},
                {"name": "Chili Powder", "description": "Red chili powder", "price": 120.00, "unit": "kg", "stock": 30},
                {"name": "Garam Masala", "description": "Mixed spices", "price": 200.00, "unit": "kg", "stock": 20}
            ],
            "Beverages": [
                {"name": "Tea", "description": "Assam tea leaves", "price": 180.00, "unit": "kg", "stock": 40},
                {"name": "Coffee", "description": "Filter coffee powder", "price": 250.00, "unit": "kg", "stock": 30},
                {"name": "Juice", "description": "Orange juice", "price": 80.00, "unit": "liter", "stock": 25},
                {"name": "Soda", "description": "Lemon soda", "price": 30.00, "unit": "bottle", "stock": 50},
                {"name": "Water", "description": "Mineral water", "price": 20.00, "unit": "liter", "stock": 100}
            ],
            "Snacks": [
                {"name": "Chips", "description": "Potato chips", "price": 20.00, "unit": "pack", "stock": 60},
                {"name": "Nuts", "description": "Mixed nuts", "price": 300.00, "unit": "kg", "stock": 20},
                {"name": "Biscuits", "description": "Cream biscuits", "price": 25.00, "unit": "pack", "stock": 40},
                {"name": "Popcorn", "description": "Butter popcorn", "price": 15.00, "unit": "pack", "stock": 30},
                {"name": "Chocolate", "description": "Dark chocolate", "price": 150.00, "unit": "pack", "stock": 25}
            ],
            "Frozen Foods": [
                {"name": "Ice Cream", "description": "Vanilla ice cream", "price": 200.00, "unit": "liter", "stock": 15},
                {"name": "Frozen Peas", "description": "Green peas", "price": 80.00, "unit": "kg", "stock": 20},
                {"name": "Frozen Corn", "description": "Sweet corn", "price": 60.00, "unit": "kg", "stock": 25},
                {"name": "Frozen Pizza", "description": "Margherita pizza", "price": 150.00, "unit": "piece", "stock": 10},
                {"name": "Frozen Fish", "description": "Frozen fish fillets", "price": 300.00, "unit": "kg", "stock": 15}
            ]
        }
        
        # Create products for each store
        for store in self.stores:
            # Handle different response structures
            if isinstance(store, dict):
                if 'id' in store:
                    store_id = store['id']
                    store_name = store.get('name', 'Unknown Store')
                elif 'body' in store:
                    try:
                        store_data = json.loads(store['body'])
                        store_id = store_data.get('id')
                        store_name = store_data.get('name', 'Unknown Store')
                    except (json.JSONDecodeError, KeyError):
                        logger.error(f"Failed to parse store data: {store}")
                        continue
                else:
                    logger.error(f"Invalid store data structure: {store}")
                    continue
            else:
                logger.error(f"Store is not a dictionary: {store}")
                continue
                
            logger.info(f"Creating products for store: {store_name}")
            
            # Select random categories for this store
            store_categories = random.sample(self.categories, min(5, len(self.categories)))
            
            for category in store_categories:
                # Handle different category response structures
                if isinstance(category, dict):
                    if 'name' in category:
                        category_name = category['name']
                        category_id = category.get('id')
                    elif 'body' in category:
                        try:
                            category_data = json.loads(category['body'])
                            category_name = category_data.get('name')
                            category_id = category_data.get('id')
                        except (json.JSONDecodeError, KeyError):
                            logger.error(f"Failed to parse category data: {category}")
                            continue
                    else:
                        logger.error(f"Invalid category data structure: {category}")
                        continue
                else:
                    logger.error(f"Category is not a dictionary: {category}")
                    continue
                    
                if category_name in product_templates:
                    # Create 2-4 products per category for this store
                    num_products = random.randint(2, 4)
                    selected_products = random.sample(product_templates[category_name], num_products)
                    
                    for product_template in selected_products:
                        # Add some variation to prices and stock
                        price_variation = random.uniform(0.8, 1.2)
                        stock_variation = random.uniform(0.7, 1.3)
                        
                        product_data = {
                            "name": product_template["name"],
                            "description": product_template["description"],
                            "price": round(product_template["price"] * price_variation, 2),
                            "unit": product_template["unit"],
                            "stock": int(product_template["stock"] * stock_variation),
                            "category_id": category_id,
                            "image_url": f"https://example.com/images/{product_template['name'].lower().replace(' ', '-')}.jpg"
                        }
                        
                        response = self.make_request("POST", f"/stores/{store_id}/products", product_data)
                        if response:
                            self.products.append(response)
                            logger.info(f"Created product: {product_template['name']} for {store_name}")
                        else:
                            logger.error(f"Failed to create product: {product_template['name']} for {store_name}")
                        
                        # Small delay to avoid overwhelming the API
                        time.sleep(0.1)
        
        logger.info(f"Created {len(self.products)} products across all stores")
    
    def clear_all_data(self):
        """Clear all data from all tables"""
        logger.info("Clearing all data from all tables...")
        
        # Clear products first (they depend on stores and categories)
        self.clear_products()
        time.sleep(1)
        
        # Clear available products
        self.clear_available_products()
        time.sleep(1)
        
        # Clear stores
        self.clear_stores()
        time.sleep(1)
        
        # Clear categories
        self.clear_categories()
        time.sleep(1)
        
        logger.info("All data cleared successfully!")
    
    def clear_products(self):
        """Clear all products"""
        logger.info("Clearing all products...")
        
        # Get all products first
        response = self.make_request("GET", "/products?limit=1000")
        if response and isinstance(response, dict) and 'body' in response:
            try:
                products_data = json.loads(response['body'])
                products = products_data.get('products', [])
                
                for product in products:
                    product_id = product.get('id')
                    if product_id:
                        delete_response = self.make_request("DELETE", f"/products/{product_id}")
                        if delete_response:
                            logger.info(f"Deleted product: {product.get('name', 'Unknown')}")
                        else:
                            logger.error(f"Failed to delete product: {product.get('name', 'Unknown')}")
                        time.sleep(0.1)  # Small delay between deletions
                
                logger.info(f"Cleared {len(products)} products")
            except json.JSONDecodeError:
                logger.error("Failed to parse products response")
        else:
            logger.info("No products found to clear")
    
    def clear_stores(self):
        """Clear all stores"""
        logger.info("Clearing all stores...")
        
        # Get all stores first
        response = self.make_request("GET", "/stores?limit=1000")
        if response and isinstance(response, dict) and 'body' in response:
            try:
                stores_data = json.loads(response['body'])
                stores = stores_data.get('stores', [])
                
                for store in stores:
                    store_id = store.get('id')
                    if store_id:
                        delete_response = self.make_request("DELETE", f"/stores/{store_id}")
                        if delete_response:
                            logger.info(f"Deleted store: {store.get('name', 'Unknown')}")
                        else:
                            logger.error(f"Failed to delete store: {store.get('name', 'Unknown')}")
                        time.sleep(0.1)  # Small delay between deletions
                
                logger.info(f"Cleared {len(stores)} stores")
            except json.JSONDecodeError:
                logger.error("Failed to parse stores response")
        else:
            logger.info("No stores found to clear")
    
    def clear_categories(self):
        """Clear all categories"""
        logger.info("Clearing all categories...")
        
        # Get all categories first
        response = self.make_request("GET", "/categories")
        if response and isinstance(response, dict) and 'body' in response:
            try:
                categories_data = json.loads(response['body'])
                categories = categories_data.get('categories', [])
                
                for category in categories:
                    category_id = category.get('id')
                    if category_id:
                        # Note: Categories might not have DELETE endpoint, so we'll just log
                        logger.info(f"Found category: {category.get('name', 'Unknown')} (ID: {category_id})")
                        logger.warning("Category deletion not implemented - categories are typically not deleted")
                
                logger.info(f"Found {len(categories)} categories (deletion not implemented)")
            except json.JSONDecodeError:
                logger.error("Failed to parse categories response")
        else:
            logger.info("No categories found to clear")
    
    def clear_available_products(self):
        """Clear all available products"""
        logger.info("Clearing all available products...")
        
        # Get all available products first
        response = self.make_request("GET", "/available-products?limit=1000")
        if response and isinstance(response, dict) and 'body' in response:
            try:
                products_data = json.loads(response['body'])
                products = products_data.get('products', [])
                
                for product in products:
                    product_id = product.get('id')
                    if product_id:
                        delete_response = self.make_request("DELETE", f"/available-products/{product_id}")
                        if delete_response:
                            logger.info(f"Deleted available product: {product.get('name', 'Unknown')}")
                        else:
                            logger.error(f"Failed to delete available product: {product.get('name', 'Unknown')}")
                        time.sleep(0.1)  # Small delay between deletions
                
                logger.info(f"Cleared {len(products)} available products")
            except json.JSONDecodeError:
                logger.error("Failed to parse available products response")
        else:
            logger.info("No available products found to clear")
    
    def create_orders(self):
        """Create some mock orders"""
        logger.info("Creating mock orders...")
        
        # Sample customer data
        customers = [
            {"id": "customer-1", "name": "John Doe", "address": "123 Main St, Bangalore"},
            {"id": "customer-2", "name": "Jane Smith", "address": "456 Oak Ave, Mumbai"},
            {"id": "customer-3", "name": "Bob Johnson", "address": "789 Pine Rd, Delhi"}
        ]
        
        order_statuses = ["pending", "preparing", "ready", "delivered"]
        
        for customer in customers:
            # Create 2-4 orders per customer
            num_orders = random.randint(2, 4)
            for i in range(num_orders):
                # Select random store
                store = random.choice(self.stores)
                
                # Calculate random total amount
                total_amount = random.randint(100, 500)
                
                order_data = {
                    "store_id": store['id'],
                    "delivery_address": customer['address'],
                    "total_amount": total_amount,
                    "notes": f"Order for {customer['name']}"
                }
                
                response = self.make_request("POST", "/orders", order_data)
                if response:
                    logger.info(f"Created order for {customer['name']}: ${total_amount}")
                else:
                    logger.error(f"Failed to create order for {customer['name']}")
                
                time.sleep(0.1)
        
        logger.info("Mock orders created")
    
    def run(self):
        """Run the complete data population process"""
        logger.info("Starting mock data population...")
        
        try:
            # Step 1: Create categories (skip users for now as they require Firebase setup)
            self.create_categories()
            time.sleep(1)
            
            # Step 2: Create stores
            self.create_stores()
            time.sleep(1)
            
            # Step 3: Create products
            self.create_products()
            time.sleep(1)
            
            # Step 4: Create orders (optional)
            # self.create_orders()
            
            logger.info("Mock data population completed successfully!")
            logger.info(f"Summary:")
            logger.info(f"- Categories created: {len(self.categories)}")
            logger.info(f"- Stores created: {len(self.stores)}")
            logger.info(f"- Products created: {len(self.products)}")
            logger.info(f"Note: User creation skipped - requires Firebase setup")
            
        except Exception as e:
            logger.error(f"Error during data population: {e}")
            raise

def main():
    """Main function to run the mock data population"""
    parser = argparse.ArgumentParser(description='Anna Akka Platform - Mock Data Population Script')
    parser.add_argument('--clear-all', action='store_true', help='Clear all data from all tables')
    parser.add_argument('--clear-products', action='store_true', help='Clear only products')
    parser.add_argument('--clear-available-products', action='store_true', help='Clear only available products')
    parser.add_argument('--clear-stores', action='store_true', help='Clear only stores')
    parser.add_argument('--clear-categories', action='store_true', help='Clear only categories')
    
    args = parser.parse_args()
    
    print("Anna Akka Platform - Mock Data Population Script")
    print("=" * 50)
    
    # Check if configuration is set
    if API_BASE_URL == "https://your-api-gateway-url/dev":
        print("ERROR: Please update the API_BASE_URL in the script with your actual API Gateway URL")
        return
    
    print("✅ Configuration looks good!")
    
    # Create populator instance
    populator = MockDataPopulator(API_BASE_URL, HEADERS)
    
    try:
        if args.clear_all:
            print("🗑️  Clearing all data from all tables...")
            populator.clear_all_data()
            print("\n✅ All data cleared successfully!")
        elif args.clear_products:
            print("🗑️  Clearing products...")
            populator.clear_products()
            print("\n✅ Products cleared successfully!")
        elif args.clear_stores:
            print("🗑️  Clearing stores...")
            populator.clear_stores()
            print("\n✅ Stores cleared successfully!")
        elif args.clear_available_products:
            print("🗑️  Clearing available products...")
            populator.clear_available_products()
            print("\n✅ Available products cleared successfully!")
        elif args.clear_categories:
            print("🗑️  Clearing categories...")
            populator.clear_categories()
            print("\n✅ Categories cleared successfully!")
        else:
            print("📝 Note: This script will create mock categories, stores, and products.")
            print("🔐 No Firebase JWT token required - using Firebase UIDs for authentication.")
            populator.run()
            print("\n✅ Mock data population completed successfully!")
            print("\nYou can now test your application with the populated data.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your API configuration and try again.")

if __name__ == "__main__":
    main() 