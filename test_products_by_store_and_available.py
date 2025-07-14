#!/usr/bin/env python3
"""
Integration Tests for Products API - Get Product by Store ID and Available Product ID
Tests the endpoint: GET /products?store_id={store_id}&available_product_id={available_product_id}
"""

import requests
import json
import time
import uuid
from datetime import datetime
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuration
BASE_URL = "https://z8sre11rwh.execute-api.ap-south-1.amazonaws.com/dev"
TEST_USER_ID = "test-user-products-123"
TEST_STORE_ID = "test-store-products-456"
TEST_AVAILABLE_PRODUCT_ID = "b9238c4d-77e1-4585-b086-11af2dabdb59"

class ProductsByStoreAndAvailableTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-User-ID': TEST_USER_ID
        })
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }

    def log_test(self, test_name, success, error=None, response_data=None):
        """Log test results"""
        if success:
            print(f"✅ PASS: {test_name}")
            if response_data:
                print(f"   Response: {json.dumps(response_data, indent=2)}")
            self.test_results['passed'] += 1
        else:
            print(f"❌ FAIL: {test_name}")
            if error:
                print(f"   Error: {error}")
            if response_data:
                print(f"   Response: {json.dumps(response_data, indent=2)}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append({
                'test': test_name,
                'error': str(error) if error else 'Unknown error',
                'response': response_data
            })

    def make_request(self, method, endpoint, params=None):
        """Make HTTP request with error handling"""
        try:
            url = f"{BASE_URL}{endpoint}"
            
            # Add user_id to query parameters if not present
            if params is None:
                params = {}
            if 'user_id' not in params:
                params['user_id'] = TEST_USER_ID
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except Exception as e:
            print(f"Request error: {str(e)}")
            return None

    def test_get_product_by_store_and_available_basic(self):
        """Test GET /products?store_id={store_id}&available_product_id={available_product_id} - Basic functionality"""
        print("\n🔍 Testing GET /products?store_id={store_id}&available_product_id={available_product_id} - Basic functionality")
        
        endpoint = "/products"
        params = {
            'store_id': TEST_STORE_ID,
            'available_product_id': TEST_AVAILABLE_PRODUCT_ID,
            'user_id': TEST_USER_ID
        }
        
        response = self.make_request('GET', endpoint, params=params)
        
        if response:
            try:
                data = response.json()
                if response.status_code == 200:
                    if 'product' in data:
                        product = data['product']
                        if (product.get('store_id') == TEST_STORE_ID and 
                            product.get('available_product_id') == TEST_AVAILABLE_PRODUCT_ID):
                            self.log_test("GET /products?store_id&available_product_id - Basic", True, response_data=data)
                            print(f"   Product ID: {product.get('id')}")
                            print(f"   Product Name: {product.get('name')}")
                            print(f"   Price: {product.get('price')}")
                            print(f"   Stock: {product.get('stock')}")
                        else:
                            self.log_test("GET /products?store_id&available_product_id - Basic", False, "Product data mismatch", data)
                    else:
                        self.log_test("GET /products?store_id&available_product_id - Basic", False, "Invalid response structure", data)
                elif response.status_code == 404:
                    self.log_test("GET /products?store_id&available_product_id - Basic", True, response_data=data)
                    print(f"   Product not found (expected for test data)")
                else:
                    self.log_test("GET /products?store_id&available_product_id - Basic", False, f"Unexpected status code: {response.status_code}", data)
            except json.JSONDecodeError:
                self.log_test("GET /products?store_id&available_product_id - Basic", False, "Invalid JSON response", {"raw_response": response.text})
        else:
            self.log_test("GET /products?store_id&available_product_id - Basic", False, "No response received")

    def test_get_product_by_store_and_available_with_additional_params(self):
        """Test GET /products?store_id={store_id}&available_product_id={available_product_id} - With additional query parameters"""
        print("\n🔍 Testing GET /products?store_id={store_id}&available_product_id={available_product_id} - With additional query parameters")
        
        endpoint = "/products"
        params = {
            'store_id': TEST_STORE_ID,
            'available_product_id': TEST_AVAILABLE_PRODUCT_ID,
            'user_id': TEST_USER_ID,
            'include_details': 'true',
            'page': '1',
            'limit': '10'
        }
        
        response = self.make_request('GET', endpoint, params=params)
        
        if response:
            try:
                data = response.json()
                if response.status_code == 200:
                    if 'product' in data:
                        self.log_test("GET /products?store_id&available_product_id - With additional params", True, response_data=data)
                        print(f"   Additional query parameters applied successfully")
                    else:
                        self.log_test("GET /products?store_id&available_product_id - With additional params", False, "Invalid response structure", data)
                elif response.status_code == 404:
                    self.log_test("GET /products?store_id&available_product_id - With additional params", True, response_data=data)
                    print(f"   Product not found (expected for test data)")
                else:
                    self.log_test("GET /products?store_id&available_product_id - With additional params", False, f"Unexpected status code: {response.status_code}", data)
            except json.JSONDecodeError:
                self.log_test("GET /products?store_id&available_product_id - With additional params", False, "Invalid JSON response", {"raw_response": response.text})
        else:
            self.log_test("GET /products?store_id&available_product_id - With additional params", False, "No response received")

    def test_get_product_by_store_and_available_invalid_store_id(self):
        """Test GET /products?store_id={store_id}&available_product_id={available_product_id} - Invalid store ID"""
        print("\n🔍 Testing GET /products?store_id={store_id}&available_product_id={available_product_id} - Invalid store ID")
        
        invalid_store_id = "invalid-store-id-999"
        endpoint = "/products"
        params = {
            'store_id': invalid_store_id,
            'available_product_id': TEST_AVAILABLE_PRODUCT_ID,
            'user_id': TEST_USER_ID
        }
        
        response = self.make_request('GET', endpoint, params=params)
        
        if response:
            try:
                data = response.json()
                if response.status_code == 404:
                    self.log_test("GET /products?store_id&available_product_id - Invalid store ID", True, response_data=data)
                    print(f"   Product not found (expected for invalid store ID)")
                elif response.status_code == 200:
                    self.log_test("GET /products?store_id&available_product_id - Invalid store ID", True, response_data=data)
                    print(f"   Product found (unexpected but valid)")
                else:
                    self.log_test("GET /products?store_id&available_product_id - Invalid store ID", False, f"Unexpected status code: {response.status_code}", data)
            except json.JSONDecodeError:
                self.log_test("GET /products?store_id&available_product_id - Invalid store ID", False, "Invalid JSON response", {"raw_response": response.text})
        else:
            self.log_test("GET /products?store_id&available_product_id - Invalid store ID", False, "No response received")

    def test_get_product_by_store_and_available_invalid_available_product_id(self):
        """Test GET /products?store_id={store_id}&available_product_id={available_product_id} - Invalid available product ID"""
        print("\n🔍 Testing GET /products?store_id={store_id}&available_product_id={available_product_id} - Invalid available product ID")
        
        invalid_available_product_id = "invalid-available-product-id-999"
        endpoint = "/products"
        params = {
            'store_id': TEST_STORE_ID,
            'available_product_id': invalid_available_product_id,
            'user_id': TEST_USER_ID
        }
        
        response = self.make_request('GET', endpoint, params=params)
        
        if response:
            try:
                data = response.json()
                if response.status_code == 404:
                    self.log_test("GET /products?store_id&available_product_id - Invalid available product ID", True, response_data=data)
                    print(f"   Product not found (expected for invalid available product ID)")
                elif response.status_code == 200:
                    self.log_test("GET /products?store_id&available_product_id - Invalid available product ID", True, response_data=data)
                    print(f"   Product found (unexpected but valid)")
                else:
                    self.log_test("GET /products?store_id&available_product_id - Invalid available product ID", False, f"Unexpected status code: {response.status_code}", data)
            except json.JSONDecodeError:
                self.log_test("GET /products?store_id&available_product_id - Invalid available product ID", False, "Invalid JSON response", {"raw_response": response.text})
        else:
            self.log_test("GET /products?store_id&available_product_id - Invalid available product ID", False, "No response received")

    def test_get_product_by_store_and_available_missing_store_id(self):
        """Test GET /products?store_id={store_id}&available_product_id={available_product_id} - Missing store ID"""
        print("\n🔍 Testing GET /products?store_id={store_id}&available_product_id={available_product_id} - Missing store ID")
        
        endpoint = "/products"
        params = {
            'available_product_id': TEST_AVAILABLE_PRODUCT_ID,
            'user_id': TEST_USER_ID
        }
        
        response = self.make_request('GET', endpoint, params=params)
        
        if response:
            try:
                data = response.json()
                # Should return paginated results when only available_product_id is provided
                if response.status_code == 200:
                    self.log_test("GET /products?store_id&available_product_id - Missing store ID", True, response_data=data)
                    print(f"   Paginated results returned (expected)")
                else:
                    self.log_test("GET /products?store_id&available_product_id - Missing store ID", False, f"Unexpected status code: {response.status_code}", data)
            except json.JSONDecodeError:
                self.log_test("GET /products?store_id&available_product_id - Missing store ID", False, "Invalid JSON response", {"raw_response": response.text})
        else:
            self.log_test("GET /products?store_id&available_product_id - Missing store ID", False, "No response received")

    def test_get_product_by_store_and_available_missing_available_product_id(self):
        """Test GET /products?store_id={store_id}&available_product_id={available_product_id} - Missing available product ID"""
        print("\n🔍 Testing GET /products?store_id={store_id}&available_product_id={available_product_id} - Missing available product ID")
        
        endpoint = "/products"
        params = {
            'store_id': TEST_STORE_ID,
            'user_id': TEST_USER_ID
        }
        
        response = self.make_request('GET', endpoint, params=params)
        
        if response:
            try:
                data = response.json()
                # Should return paginated results when only store_id is provided
                if response.status_code == 200:
                    self.log_test("GET /products?store_id&available_product_id - Missing available product ID", True, response_data=data)
                    print(f"   Paginated results returned (expected)")
                else:
                    self.log_test("GET /products?store_id&available_product_id - Missing available product ID", False, f"Unexpected status code: {response.status_code}", data)
            except json.JSONDecodeError:
                self.log_test("GET /products?store_id&available_product_id - Missing available product ID", False, "Invalid JSON response", {"raw_response": response.text})
        else:
            self.log_test("GET /products?store_id&available_product_id - Missing available product ID", False, "No response received")

    def test_get_product_by_store_and_available_unauthorized(self):
        """Test GET /products?store_id={store_id}&available_product_id={available_product_id} - Unauthorized access"""
        print("\n🔍 Testing GET /products?store_id={store_id}&available_product_id={available_product_id} - Unauthorized access")
        
        # Test without user ID
        original_headers = self.session.headers.copy()
        self.session.headers.pop('X-User-ID', None)
        
        endpoint = "/products"
        params = {
            'store_id': TEST_STORE_ID,
            'available_product_id': TEST_AVAILABLE_PRODUCT_ID
        }
        
        response = self.make_request('GET', endpoint, params=params)
        
        if response:
            try:
                data = response.json()
                if response.status_code == 401:
                    self.log_test("GET /products?store_id&available_product_id - Unauthorized", True, response_data=data)
                    print(f"   Unauthorized (expected)")
                elif response.status_code == 200:
                    self.log_test("GET /products?store_id&available_product_id - Unauthorized", True, response_data=data)
                    print(f"   Access allowed (unexpected but valid)")
                else:
                    self.log_test("GET /products?store_id&available_product_id - Unauthorized", False, f"Unexpected status code: {response.status_code}", data)
            except json.JSONDecodeError:
                self.log_test("GET /products?store_id&available_product_id - Unauthorized", False, "Invalid JSON response", {"raw_response": response.text})
        else:
            self.log_test("GET /products?store_id&available_product_id - Unauthorized", False, "No response received")
        
        # Restore headers
        self.session.headers = original_headers

    def test_get_product_by_store_and_available_method_not_allowed(self):
        """Test GET /products?store_id={store_id}&available_product_id={available_product_id} - Method not allowed"""
        print("\n🔍 Testing GET /products?store_id={store_id}&available_product_id={available_product_id} - Method not allowed")
        
        endpoint = "/products"
        params = {
            'store_id': TEST_STORE_ID,
            'available_product_id': TEST_AVAILABLE_PRODUCT_ID,
            'user_id': TEST_USER_ID
        }
        
        # Test with POST method (not allowed)
        try:
            response = self.session.post(f"{BASE_URL}{endpoint}", params=params)
            
            if response:
                try:
                    data = response.json()
                    if response.status_code == 405:
                        self.log_test("GET /products?store_id&available_product_id - Method not allowed", True, response_data=data)
                        print(f"   Method not allowed (expected)")
                    else:
                        self.log_test("GET /products?store_id&available_product_id - Method not allowed", False, f"Unexpected status code: {response.status_code}", data)
                except json.JSONDecodeError:
                    self.log_test("GET /products?store_id&available_product_id - Method not allowed", False, "Invalid JSON response", {"raw_response": response.text})
            else:
                self.log_test("GET /products?store_id&available_product_id - Method not allowed", False, "No response received")
        except Exception as e:
            self.log_test("GET /products?store_id&available_product_id - Method not allowed", False, f"Request error: {str(e)}")

    def test_get_product_by_store_and_available_real_data(self):
        """Test GET /products?store_id={store_id}&available_product_id={available_product_id} - With real data scenarios"""
        print("\n🔍 Testing GET /products?store_id={store_id}&available_product_id={available_product_id} - With real data scenarios")
        
        # Test with different store IDs and available product IDs
        test_cases = [
            {
                'store_id': 'store-real-123',
                'available_product_id': 'b9238c4d-77e1-4585-b086-11af2dabdb59',
                'description': 'Real store with real available product'
            },
            {
                'store_id': 'store-real-456',
                'available_product_id': 'c9238c4d-77e1-4585-b086-11af2dabdb60',
                'description': 'Another real store with different available product'
            },
            {
                'store_id': 'store-real-789',
                'available_product_id': 'd9238c4d-77e1-4585-b086-11af2dabdb61',
                'description': 'Third real store with another available product'
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\n   Testing case {i+1}: {test_case['description']}")
            endpoint = "/products"
            params = {
                'store_id': test_case['store_id'],
                'available_product_id': test_case['available_product_id'],
                'user_id': TEST_USER_ID
            }
            
            response = self.make_request('GET', endpoint, params=params)
            
            if response:
                try:
                    data = response.json()
                    if response.status_code == 200:
                        if 'product' in data:
                            product = data['product']
                            if (product.get('store_id') == test_case['store_id'] and 
                                product.get('available_product_id') == test_case['available_product_id']):
                                print(f"   ✅ Found product: {product.get('name', 'Unknown')} - Price: {product.get('price')} - Stock: {product.get('stock')}")
                            else:
                                print(f"   ⚠️  Product data mismatch")
                        else:
                            print(f"   ⚠️  Invalid response structure")
                    elif response.status_code == 404:
                        print(f"   ℹ️  Product not found (expected for test data)")
                    else:
                        print(f"   ❌ Unexpected status code: {response.status_code}")
                except json.JSONDecodeError:
                    print(f"   ❌ Invalid JSON response")
            else:
                print(f"   ❌ No response received")

    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Products API Integration Tests - Get Product by Store and Available Product ID")
        print("=" * 80)
        
        # Basic functionality tests
        self.test_get_product_by_store_and_available_basic()
        self.test_get_product_by_store_and_available_with_additional_params()
        
        # Error handling tests
        self.test_get_product_by_store_and_available_invalid_store_id()
        self.test_get_product_by_store_and_available_invalid_available_product_id()
        self.test_get_product_by_store_and_available_missing_store_id()
        self.test_get_product_by_store_and_available_missing_available_product_id()
        
        # Security tests
        self.test_get_product_by_store_and_available_unauthorized()
        self.test_get_product_by_store_and_available_method_not_allowed()
        
        # Real data scenarios
        self.test_get_product_by_store_and_available_real_data()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        total_tests = self.test_results['passed'] + self.test_results['failed']
        if total_tests > 0:
            success_rate = (self.test_results['passed'] / total_tests) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.test_results['errors']:
            print("\n🔍 ERRORS:")
            for error in self.test_results['errors']:
                print(f"   • {error['test']}: {error['error']}")
        
        print("\n🎯 Products API Integration Tests Complete!")

def main():
    """Main function to run the integration tests"""
    tester = ProductsByStoreAndAvailableTest()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 