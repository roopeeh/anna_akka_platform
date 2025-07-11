#!/usr/bin/env python3
"""
Test script for store product IDs functionality.
This script tests the new endpoints and functionality for updating stores
with product IDs from available products.
"""

import requests
import json
import os
import time
from datetime import datetime

# Configuration
BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:3000')
API_KEY = os.environ.get('API_KEY', '')

class StoreProductIDsTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}' if API_KEY else ''
        }
        self.test_results = []
    
    def log_test(self, test_name, success, message=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def test_get_stores(self):
        """Test getting all stores"""
        print("\n🔍 Testing GET /stores")
        try:
            response = requests.get(f"{self.base_url}/stores", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                stores = data.get('stores', [])
                self.log_test("GET /stores", True, f"Found {len(stores)} stores")
                return stores
            else:
                self.log_test("GET /stores", False, f"Status code: {response.status_code}")
                return []
        except Exception as e:
            self.log_test("GET /stores", False, f"Error: {str(e)}")
            return []
    
    def test_get_available_products(self):
        """Test getting available products"""
        print("\n🔍 Testing GET /available-products")
        try:
            response = requests.get(f"{self.base_url}/available-products", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                self.log_test("GET /available-products", True, f"Found {len(products)} available products")
                return products
            else:
                self.log_test("GET /available-products", False, f"Status code: {response.status_code}")
                return []
        except Exception as e:
            self.log_test("GET /available-products", False, f"Error: {str(e)}")
            return []
    
    def test_update_all_stores_product_ids(self):
        """Test updating all stores with product IDs"""
        print("\n🔍 Testing POST /stores/update-product-ids")
        try:
            response = requests.post(f"{self.base_url}/stores/update-product-ids", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                updated_count = data.get('updated_count', 0)
                self.log_test("POST /stores/update-product-ids", True, f"Updated {updated_count} stores")
                return True
            else:
                self.log_test("POST /stores/update-product-ids", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("POST /stores/update-product-ids", False, f"Error: {str(e)}")
            return False
    
    def test_update_specific_store_product_ids(self, store_id):
        """Test updating a specific store with product IDs"""
        print(f"\n🔍 Testing POST /stores/{store_id}/update-product-ids")
        try:
            response = requests.post(f"{self.base_url}/stores/{store_id}/update-product-ids", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                store = data.get('store', {})
                product_ids = store.get('product_ids', [])
                self.log_test(f"POST /stores/{store_id}/update-product-ids", True, f"Updated store with {len(product_ids)} product IDs")
                return True
            else:
                self.log_test(f"POST /stores/{store_id}/update-product-ids", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"POST /stores/{store_id}/update-product-ids", False, f"Error: {str(e)}")
            return False
    
    def test_get_store_with_product_ids(self, store_id):
        """Test getting a store and verify it has product_ids field"""
        print(f"\n🔍 Testing GET /stores/{store_id}")
        try:
            response = requests.get(f"{self.base_url}/stores/{store_id}", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                store = data.get('store', {})
                product_ids = store.get('product_ids', [])
                has_product_ids = 'product_ids' in store
                self.log_test(f"GET /stores/{store_id}", True, f"Store has product_ids field: {has_product_ids}, {len(product_ids)} product IDs")
                return store
            else:
                self.log_test(f"GET /stores/{store_id}", False, f"Status code: {response.status_code}")
                return None
        except Exception as e:
            self.log_test(f"GET /stores/{store_id}", False, f"Error: {str(e)}")
            return None
    
    def test_create_product_and_verify_store_update(self, store_id, available_product_id):
        """Test creating a product and verify store product IDs are updated"""
        print(f"\n🔍 Testing product creation and store update for store {store_id}")
        try:
            # Create a product
            product_data = {
                "available_product_id": available_product_id,
                "price": 25.99,
                "stock": 10
            }
            
            response = requests.post(f"{self.base_url}/stores/{store_id}/products", 
                                  headers=self.headers, 
                                  json=product_data)
            
            if response.status_code == 201:
                self.log_test("Create product", True, "Product created successfully")
                
                # Wait a moment for the store update to complete
                time.sleep(2)
                
                # Check if store product IDs were updated
                store = self.test_get_store_with_product_ids(store_id)
                if store and available_product_id in store.get('product_ids', []):
                    self.log_test("Store product IDs update", True, "Store product IDs updated after product creation")
                    return True
                else:
                    self.log_test("Store product IDs update", False, "Store product IDs not updated after product creation")
                    return False
            else:
                self.log_test("Create product", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Create product and verify store update", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Store Product IDs Tests")
        print("=" * 50)
        
        # Test 1: Get stores
        stores = self.test_get_stores()
        
        # Test 2: Get available products
        available_products = self.test_get_available_products()
        
        # Test 3: Update all stores with product IDs
        self.test_update_all_stores_product_ids()
        
        # Test 4: Test specific store update if we have stores
        if stores:
            first_store = stores[0]
            store_id = first_store.get('id')
            if store_id:
                self.test_update_specific_store_product_ids(store_id)
                self.test_get_store_with_product_ids(store_id)
        
        # Test 5: Test product creation and store update
        if stores and available_products:
            first_store = stores[0]
            first_available_product = available_products[0]
            store_id = first_store.get('id')
            available_product_id = first_available_product.get('id')
            
            if store_id and available_product_id:
                self.test_create_product_and_verify_store_update(store_id, available_product_id)
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%" if total > 0 else "N/A")
        
        # Print failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        return passed == total

def main():
    """Main function"""
    print("=== Store Product IDs Test Suite ===")
    
    # Check if API base URL is set
    if not BASE_URL:
        print("❌ Error: API_BASE_URL environment variable not set")
        print("Please set API_BASE_URL to your API endpoint")
        return False
    
    # Create test instance and run tests
    tester = StoreProductIDsTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
    
    return success

if __name__ == "__main__":
    main() 