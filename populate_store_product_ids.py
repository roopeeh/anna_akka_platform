#!/usr/bin/env python3
"""
Script to populate stores with product IDs from available products using API endpoints.
This script creates stores and products via API calls and lets the automatic
update mechanism handle the product_ids field.
"""

import requests
import json
import os
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = 'https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev'
API_KEY = os.environ.get('API_KEY', '')

class StoreProductIDsPopulator:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}' if API_KEY else ''
        }
        self.test_stores = [
            {
                'name': 'Fresh Grocery Store',
                'address': '123 Main Street, Bangalore',
                'phone': '+91 98765 43210',
                'delivery_time': '30-45 min'
            },
            {
                'name': 'Organic Market',
                'address': '456 Green Avenue, Bangalore',
                'phone': '+91 98765 43211',
                'delivery_time': '25-40 min'
            },
            {
                'name': 'Local Food Mart',
                'address': '789 Food Street, Bangalore',
                'phone': '+91 98765 43212',
                'delivery_time': '35-50 min'
            }
        ]
    
    def get_available_products(self):
        """Get available products from API"""
        logger.info("Getting available products from API...")
        
        try:
            response = requests.get(f"{self.base_url}/available-products", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                logger.info(f"Found {len(products)} available products")
                return products
            else:
                logger.error(f"Failed to get available products: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting available products: {str(e)}")
            return []
    
    def get_stores(self):
        """Get existing stores from API"""
        logger.info("Getting existing stores from API...")
        
        try:
            response = requests.get(f"{self.base_url}/stores", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                stores = data.get('stores', [])
                logger.info(f"Found {len(stores)} existing stores")
                return stores
            else:
                logger.error(f"Failed to get stores: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting stores: {str(e)}")
            return []
    
    def create_store(self, store_data):
        """Create a store via API"""
        logger.info(f"Creating store: {store_data['name']}")
        
        try:
            response = requests.post(f"{self.base_url}/stores", headers=self.headers, json=store_data)
            if response.status_code == 201:
                data = response.json()
                store = data.get('store', {})
                logger.info(f"Store created successfully: {store.get('id')}")
                return store
            else:
                logger.error(f"Failed to create store: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating store: {str(e)}")
            return None
    
    def create_product(self, store_id, product_data):
        """Create a product for a store via API"""
        logger.info(f"Creating product for store {store_id}: {product_data.get('name', product_data.get('available_product_id'))}")
        
        try:
            response = requests.post(f"{self.base_url}/stores/{store_id}/products", 
                                  headers=self.headers, json=product_data)
            if response.status_code == 201:
                data = response.json()
                product = data.get('product', {})
                logger.info(f"Product created successfully: {product.get('id')}")
                return product
            else:
                logger.error(f"Failed to create product: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            return None
    
    def update_store_product_ids(self, store_id):
        """Update store product IDs via API"""
        logger.info(f"Updating product IDs for store: {store_id}")
        
        try:
            response = requests.post(f"{self.base_url}/stores/{store_id}/update-product-ids", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                store = data.get('store', {})
                product_ids = store.get('product_ids', [])
                logger.info(f"Store product IDs updated successfully: {len(product_ids)} product IDs")
                return store
            else:
                logger.error(f"Failed to update store product IDs: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error updating store product IDs: {str(e)}")
            return None
    
    def update_all_stores_product_ids(self):
        """Update all stores product IDs via API"""
        logger.info("Updating all stores product IDs via API...")
        
        try:
            response = requests.post(f"{self.base_url}/stores/update-product-ids", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                updated_count = data.get('updated_count', 0)
                logger.info(f"Updated {updated_count} stores with product IDs")
                return updated_count
            else:
                logger.error(f"Failed to update all stores: {response.status_code} - {response.text}")
                return 0
        except Exception as e:
            logger.error(f"Error updating all stores: {str(e)}")
            return 0
    
    def get_store_details(self, store_id):
        """Get store details via API"""
        logger.info(f"Getting store details: {store_id}")
        
        try:
            response = requests.get(f"{self.base_url}/stores/{store_id}", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                store = data.get('store', {})
                product_ids = store.get('product_ids', [])
                logger.info(f"Store has {len(product_ids)} product IDs")
                return store
            else:
                logger.error(f"Failed to get store details: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting store details: {str(e)}")
            return None
    
    def populate_stores_with_products(self):
        """Main function to populate stores with products"""
        logger.info("Starting to populate stores with products via API...")
        
        # Get available products
        available_products = self.get_available_products()
        if not available_products:
            logger.warning("No available products found. Creating some test products first...")
            # You might want to create some available products here if none exist
            return
        
        # Get existing stores
        existing_stores = self.get_stores()
        
        # Create stores if none exist
        stores = existing_stores
        if not stores:
            logger.info("No stores found. Creating test stores...")
            stores = []
            for store_data in self.test_stores:
                store = self.create_store(store_data)
                if store:
                    stores.append(store)
                    # Wait a moment between store creations
                    time.sleep(1)
        
        if not stores:
            logger.error("No stores available for product creation")
            return
        
        # Create products for each store
        for store in stores:
            store_id = store['id']
            store_name = store['name']
            
            logger.info(f"Creating products for store: {store_name}")
            
            # Create 2-3 products per store from available products
            products_to_create = min(3, len(available_products))
            for i in range(products_to_create):
                available_product = available_products[i]
                available_product_id = available_product['id']
                
                # Create product data
                product_data = {
                    "available_product_id": available_product_id,
                    "price": float(available_product['price']) + (i * 2),  # Slightly different price per store
                    "stock": 10 + (i * 5)  # Different stock levels
                }
                
                # Create the product
                product = self.create_product(store_id, product_data)
                if product:
                    logger.info(f"Created product: {product.get('name')} for store: {store_name}")
                
                # Wait a moment between product creations
                time.sleep(1)
        
        # Update all stores with product IDs
        logger.info("Updating all stores with product IDs...")
        updated_count = self.update_all_stores_product_ids()
        
        # Verify the updates
        logger.info("Verifying store updates...")
        for store in stores:
            store_id = store['id']
            store_name = store['name']
            
            updated_store = self.get_store_details(store_id)
            if updated_store:
                product_ids = updated_store.get('product_ids', [])
                logger.info(f"Store '{store_name}' has {len(product_ids)} product IDs: {product_ids}")
        
        logger.info(f"Completed! Updated {updated_count} stores with product IDs.")

def main():
    """Main function"""
    logger.info("=== STORE PRODUCT IDS POPULATION SCRIPT (API VERSION) ===")
    
    # Check if API base URL is set
    if not BASE_URL:
        logger.error("API_BASE_URL environment variable not set")
        logger.info("Please set API_BASE_URL to your API endpoint")
        return
    
    # Create populator instance and run
    populator = StoreProductIDsPopulator()
    populator.populate_stores_with_products()
    
    logger.info("=== END ===")

if __name__ == "__main__":
    main() 