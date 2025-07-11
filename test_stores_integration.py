#!/usr/bin/env python3
"""
Stores Integration Tests for Anna Akka Platform

This module contains comprehensive integration tests for all stores endpoints:
- Get all stores
- Get specific store
- Create store
- Update store
- Delete store
- Get stores by owner
- Error handling and edge cases

All tests use the actual API endpoint at https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev
"""

import requests
import json
import uuid
import time
import random
from datetime import datetime

# Configuration
from env_config import get_base_url

BASE_URL = get_base_url()
from env_config import get_headers

HEADERS = get_headers()

class StoresIntegrationTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        self.test_data = {}
        self.setup_test_data()

    def setup_test_data(self):
        """Setup unique test data for each test run"""
        timestamp = int(time.time())
        self.test_data = {
            "owner_id": "mock-owner-id",  # Use mock owner ID
            "store_name": f"Test Store {timestamp}",
            "store_address": f"Test Address {timestamp}, Test City",
            "store_phone": f"+91 98765 {random.randint(10000, 99999)}",
            "store_delivery_time": "30-45 min",
            "store_rating": 4.5,
            "store_is_open": True,
            "invalid_store_id": "invalid-store-id",
            "invalid_owner_id": "invalid-owner-id",
            "long_name": "A" * 1000,
            "empty_name": "",
            "special_chars_name": f"Store with Special Chars!@#$%^&*() {timestamp}",
            "unicode_name": f"Store with Unicode 🏪🛒 {timestamp}"
        }

    def log_test(self, test_name, status, message="", response_time=None):
        """Log test results with timing"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        timing_info = f" ({response_time:.3f}s)" if response_time else ""
        
        if status == "PASS":
            print(f"✅ [{timestamp}] {test_name}: PASS{timing_info}")
            self.test_results["passed"] += 1
        else:
            print(f"❌ [{timestamp}] {test_name}: FAIL - {message}{timing_info}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {message}")

    def test_endpoint(self, method, endpoint, data=None, expected_status=200, test_name=None):
        """Generic endpoint tester"""
        if test_name is None:
            test_name = f"{method} {endpoint}"
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(f"{BASE_URL}{endpoint}")
            elif method == "POST":
                response = self.session.post(f"{BASE_URL}{endpoint}", json=data)
            elif method == "PUT":
                response = self.session.put(f"{BASE_URL}{endpoint}", json=data)
            elif method == "DELETE":
                response = self.session.delete(f"{BASE_URL}{endpoint}")
            else:
                self.log_test(test_name, "FAIL", f"Unsupported method: {method}")
                return None
            
            response_time = time.time() - start_time
            
            if response.status_code == expected_status:
                self.log_test(test_name, "PASS", response_time=response_time)
                return response.json() if response.content else None
            else:
                self.log_test(test_name, "FAIL", f"Expected {expected_status}, got {response.status_code}: {response.text}", response_time)
                return None
                
        except Exception as e:
            self.log_test(test_name, "FAIL", f"Exception: {str(e)}")
            return None

    def test_get_stores(self):
        """Test GET /stores endpoint"""
        print("\n🏪 Testing Get Stores")
        print("=" * 50)
        
        # Test get all stores
        result = self.test_endpoint("GET", "/stores", expected_status=200, test_name="Get All Stores")
        if result:
            # Verify response structure
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'stores' in body_data:
                        stores = body_data['stores']
                        print(f"  📊 Found {len(stores)} stores")
                        
                        # Test response structure for first store
                        if stores:
                            first_store = stores[0]
                            required_fields = ['id', 'name', 'address', 'phone', 'is_open', 'rating', 'delivery_time', 'created_at']
                            missing_fields = [field for field in required_fields if field not in first_store]
                            if not missing_fields:
                                self.log_test("Store Structure Validation", "PASS")
                                self.test_results["passed"] += 1
                            else:
                                self.log_test("Store Structure Validation", "FAIL", f"Missing fields: {missing_fields}")
                                self.test_results["failed"] += 1
                    else:
                        self.log_test("Response Structure", "FAIL", "Missing 'stores' field in response")
                        self.test_results["failed"] += 1
                except json.JSONDecodeError:
                    self.log_test("Response JSON Parsing", "FAIL", "Invalid JSON in response body")
                    self.test_results["failed"] += 1
            else:
                # Direct response
                if isinstance(result, dict) and 'stores' in result:
                    stores = result['stores']
                    print(f"  📊 Found {len(stores)} stores")
                else:
                    self.log_test("Response Structure", "FAIL", "Unexpected response structure")
                    self.test_results["failed"] += 1

    def test_get_specific_store(self):
        """Test GET /stores/{id} endpoint"""
        print("\n🏪 Testing Get Specific Store")
        print("=" * 50)
        
        # First get all stores to find a valid store ID
        stores_result = self.test_endpoint("GET", "/stores", expected_status=200, test_name="Get Stores for ID")
        if stores_result:
            store_id = None
            if isinstance(stores_result, dict) and 'body' in stores_result:
                try:
                    body_data = json.loads(stores_result['body'])
                    if 'stores' in body_data and body_data['stores']:
                        store_id = body_data['stores'][0]['id']
                except json.JSONDecodeError:
                    pass
            elif isinstance(stores_result, dict) and 'stores' in stores_result and stores_result['stores']:
                store_id = stores_result['stores'][0]['id']
            
            if store_id:
                # Test get specific store
                result = self.test_endpoint("GET", f"/stores/{store_id}", expected_status=200, test_name="Get Specific Store - Success")
                if result:
                    # Verify response structure
                    if isinstance(result, dict) and 'body' in result:
                        try:
                            body_data = json.loads(result['body'])
                            required_fields = ['id', 'name', 'address', 'phone', 'is_open', 'rating', 'delivery_time', 'created_at']
                            missing_fields = [field for field in required_fields if field not in body_data]
                            if not missing_fields:
                                self.log_test("Specific Store Structure", "PASS")
                                self.test_results["passed"] += 1
                            else:
                                self.log_test("Specific Store Structure", "FAIL", f"Missing fields: {missing_fields}")
                                self.test_results["failed"] += 1
                        except json.JSONDecodeError:
                            self.log_test("Specific Store JSON Parsing", "FAIL", "Invalid JSON in response body")
                            self.test_results["failed"] += 1
                    else:
                        # Direct response
                        required_fields = ['id', 'name', 'address', 'phone', 'is_open', 'rating', 'delivery_time', 'created_at']
                        missing_fields = [field for field in required_fields if field not in result]
                        if not missing_fields:
                            self.log_test("Specific Store Structure", "PASS")
                            self.test_results["passed"] += 1
                        else:
                            self.log_test("Specific Store Structure", "FAIL", f"Missing fields: {missing_fields}")
                            self.test_results["failed"] += 1
        
        # Test get non-existent store
        self.test_endpoint("GET", f"/stores/{self.test_data['invalid_store_id']}", expected_status=404, test_name="Get Specific Store - Not Found")

    def test_create_store(self):
        """Test POST /stores endpoint"""
        print("\n🏪 Testing Create Store")
        print("=" * 50)
        
        # Test create store with valid data
        store_data = {
            "name": self.test_data["store_name"],
            "address": self.test_data["store_address"],
            "phone": self.test_data["store_phone"],
            "delivery_time": self.test_data["store_delivery_time"]
        }
        
        result = self.test_endpoint("POST", "/stores", store_data, 201, "Create Store - Success")
        if result:
            # Verify response structure
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'store' in body_data:
                        store = body_data['store']
                        print(f"  🏪 Created store: {store.get('name', 'N/A')}")
                        print(f"  📍 Address: {store.get('address', 'N/A')}")
                        print(f"  📞 Phone: {store.get('phone', 'N/A')}")
                        
                        # Test response structure
                        required_fields = ['id', 'name', 'address', 'phone', 'is_open', 'rating', 'delivery_time', 'created_at']
                        missing_fields = [field for field in required_fields if field not in store]
                        if not missing_fields:
                            self.log_test("Create Store Response Structure", "PASS")
                            self.test_results["passed"] += 1
                        else:
                            self.log_test("Create Store Response Structure", "FAIL", f"Missing fields: {missing_fields}")
                            self.test_results["failed"] += 1
                    else:
                        self.log_test("Create Store Response", "FAIL", "Missing 'store' field in response")
                        self.test_results["failed"] += 1
                except json.JSONDecodeError:
                    self.log_test("Create Store JSON Parsing", "FAIL", "Invalid JSON in response body")
                    self.test_results["failed"] += 1
            else:
                # Direct response
                if isinstance(result, dict) and 'store' in result:
                    store = result['store']
                    print(f"  🏪 Created store: {store.get('name', 'N/A')}")
                    print(f"  📍 Address: {store.get('address', 'N/A')}")
                    print(f"  📞 Phone: {store.get('phone', 'N/A')}")
                else:
                    self.log_test("Create Store Response", "FAIL", "Unexpected response structure")
                    self.test_results["failed"] += 1
        
        # Test create store with missing required fields
        incomplete_data = {"name": self.test_data["store_name"]}
        self.test_endpoint("POST", "/stores", incomplete_data, 400, "Create Store - Missing Required Fields")
        
        # Test create store with empty name
        empty_name_data = {"name": "", "address": self.test_data["store_address"]}
        self.test_endpoint("POST", "/stores", empty_name_data, 400, "Create Store - Empty Name")
        
        # Test create store with special characters
        special_chars_data = {
            "name": self.test_data["special_chars_name"],
            "address": self.test_data["store_address"]
        }
        self.test_endpoint("POST", "/stores", special_chars_data, 201, "Create Store - Special Characters")

    def test_update_store(self):
        """Test PUT /stores/{id} endpoint"""
        print("\n🏪 Testing Update Store")
        print("=" * 50)
        
        # First create a store to update
        store_data = {
            "name": f"Store to Update {int(time.time())}",
            "address": "Original Address",
            "phone": "+91 98765 43210"
        }
        
        create_result = self.test_endpoint("POST", "/stores", store_data, 201, "Create Store for Update")
        if create_result:
            store_id = None
            if isinstance(create_result, dict) and 'body' in create_result:
                try:
                    body_data = json.loads(create_result['body'])
                    if 'store' in body_data:
                        store_id = body_data['store']['id']
                except json.JSONDecodeError:
                    pass
            elif isinstance(create_result, dict) and 'store' in create_result:
                store_id = create_result['store']['id']
            
            if store_id:
                # Test update store
                update_data = {
                    "name": "Updated Store Name",
                    "address": "Updated Address",
                    "phone": "+91 98765 54321",
                    "delivery_time": "45-60 min"
                }
                
                result = self.test_endpoint("PUT", f"/stores/{store_id}", update_data, 200, "Update Store - Success")
                if result:
                    # Verify response structure
                    if isinstance(result, dict) and 'body' in result:
                        try:
                            body_data = json.loads(result['body'])
                            if 'store' in body_data:
                                store = body_data['store']
                                print(f"  🏪 Updated store: {store.get('name', 'N/A')}")
                                print(f"  📍 New address: {store.get('address', 'N/A')}")
                                print(f"  📞 New phone: {store.get('phone', 'N/A')}")
                                
                                # Test response structure
                                required_fields = ['id', 'name', 'address', 'phone', 'is_open', 'rating', 'delivery_time', 'updated_at']
                                missing_fields = [field for field in required_fields if field not in store]
                                if not missing_fields:
                                    self.log_test("Update Store Response Structure", "PASS")
                                    self.test_results["passed"] += 1
                                else:
                                    self.log_test("Update Store Response Structure", "FAIL", f"Missing fields: {missing_fields}")
                                    self.test_results["failed"] += 1
                            else:
                                self.log_test("Update Store Response", "FAIL", "Missing 'store' field in response")
                                self.test_results["failed"] += 1
                        except json.JSONDecodeError:
                            self.log_test("Update Store JSON Parsing", "FAIL", "Invalid JSON in response body")
                            self.test_results["failed"] += 1
                    else:
                        # Direct response
                        if isinstance(result, dict) and 'store' in result:
                            store = result['store']
                            print(f"  🏪 Updated store: {store.get('name', 'N/A')}")
                            print(f"  📍 New address: {store.get('address', 'N/A')}")
                            print(f"  📞 New phone: {store.get('phone', 'N/A')}")
                        else:
                            self.log_test("Update Store Response", "FAIL", "Unexpected response structure")
                            self.test_results["failed"] += 1
        
        # Test update non-existent store
        self.test_endpoint("PUT", f"/stores/{self.test_data['invalid_store_id']}", {"name": "Test"}, 404, "Update Store - Not Found")

    def test_delete_store(self):
        """Test DELETE /stores/{id} endpoint"""
        print("\n🏪 Testing Delete Store")
        print("=" * 50)
        
        # First create a store to delete
        store_data = {
            "name": f"Store to Delete {int(time.time())}",
            "address": "Delete Address",
            "phone": "+91 98765 65432"
        }
        
        create_result = self.test_endpoint("POST", "/stores", store_data, 201, "Create Store for Delete")
        if create_result:
            store_id = None
            if isinstance(create_result, dict) and 'body' in create_result:
                try:
                    body_data = json.loads(create_result['body'])
                    if 'store' in body_data:
                        store_id = body_data['store']['id']
                except json.JSONDecodeError:
                    pass
            elif isinstance(create_result, dict) and 'store' in create_result:
                store_id = create_result['store']['id']
            
            if store_id:
                # Test delete store
                result = self.test_endpoint("DELETE", f"/stores/{store_id}", expected_status=204, test_name="Delete Store - Success")
                if result is not None:  # DELETE should return 204 with no content
                    self.log_test("Delete Store Response", "PASS")
                    self.test_results["passed"] += 1
        
        # Test delete non-existent store
        self.test_endpoint("DELETE", f"/stores/{self.test_data['invalid_store_id']}", expected_status=404, test_name="Delete Store - Not Found")

    def test_get_stores_by_owner(self):
        """Test GET /stores/owner endpoint"""
        print("\n🏪 Testing Get Stores by Owner")
        print("=" * 50)
        
        # Test get stores by owner (using mock owner ID)
        result = self.test_endpoint("GET", "/stores/owner", expected_status=200, test_name="Get Stores by Owner")
        if result:
            # Verify response structure
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'stores' in body_data:
                        stores = body_data['stores']
                        print(f"  📊 Found {len(stores)} stores for owner")
                        
                        # Test response structure
                        if stores:
                            first_store = stores[0]
                            required_fields = ['id', 'name', 'address', 'phone', 'is_open', 'rating', 'delivery_time', 'created_at']
                            missing_fields = [field for field in required_fields if field not in first_store]
                            if not missing_fields:
                                self.log_test("Owner Stores Structure", "PASS")
                                self.test_results["passed"] += 1
                            else:
                                self.log_test("Owner Stores Structure", "FAIL", f"Missing fields: {missing_fields}")
                                self.test_results["failed"] += 1
                    else:
                        self.log_test("Owner Stores Response", "FAIL", "Missing 'stores' field in response")
                        self.test_results["failed"] += 1
                except json.JSONDecodeError:
                    self.log_test("Owner Stores JSON Parsing", "FAIL", "Invalid JSON in response body")
                    self.test_results["failed"] += 1
            else:
                # Direct response
                if isinstance(result, dict) and 'stores' in result:
                    stores = result['stores']
                    print(f"  📊 Found {len(stores)} stores for owner")
                else:
                    self.log_test("Owner Stores Response", "FAIL", "Unexpected response structure")
                    self.test_results["failed"] += 1

    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🏪 Testing Error Handling")
        print("=" * 50)
        
        # Test invalid HTTP methods
        self.test_endpoint("PUT", "/stores", {}, 405, "Invalid Method - PUT /stores")
        self.test_endpoint("DELETE", "/stores", {}, 405, "Invalid Method - DELETE /stores")
        
        # Test malformed JSON
        headers = {"Content-Type": "application/json"}
        try:
            response = self.session.post(f"{BASE_URL}/stores", data="invalid json", headers=headers)
            if response.status_code == 400:
                self.log_test("Malformed JSON - Create Store", "PASS")
                self.test_results["passed"] += 1
            else:
                self.log_test("Malformed JSON - Create Store", "FAIL", f"Expected 400, got {response.status_code}")
                self.test_results["failed"] += 1
        except Exception as e:
            self.log_test("Malformed JSON - Create Store", "FAIL", f"Exception: {str(e)}")
            self.test_results["failed"] += 1

    def test_cors_headers(self):
        """Test CORS headers"""
        print("\n🏪 Testing CORS Headers")
        print("=" * 50)
        
        # Test OPTIONS request
        try:
            response = self.session.options(f"{BASE_URL}/stores")
            if response.status_code in [200, 204]:  # Both 200 and 204 are valid for OPTIONS
                cors_headers = response.headers
                required_headers = [
                    'Access-Control-Allow-Origin',
                    'Access-Control-Allow-Headers',
                    'Access-Control-Allow-Methods'
                ]
                
                missing_headers = [header for header in required_headers if header not in cors_headers]
                if not missing_headers:
                    self.log_test("CORS Headers", "PASS")
                    self.test_results["passed"] += 1
                else:
                    self.log_test("CORS Headers", "FAIL", f"Missing headers: {missing_headers}")
                    self.test_results["failed"] += 1
            else:
                self.log_test("CORS OPTIONS", "FAIL", f"Expected 200 or 204, got {response.status_code}")
                self.test_results["failed"] += 1
        except Exception as e:
            self.log_test("CORS Test", "FAIL", f"Exception: {str(e)}")
            self.test_results["failed"] += 1

    def run_all_tests(self):
        """Run all stores integration tests"""
        print("🚀 Starting Stores Integration Tests")
        print("=" * 60)
        print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 API Base URL: {BASE_URL}")
        print(f"👤 Mock Owner ID: {self.test_data['owner_id']}")
        print("=" * 60)
        
        try:
            # Run all test methods
            self.test_get_stores()
            self.test_get_specific_store()
            self.test_create_store()
            self.test_update_store()
            self.test_delete_store()
            self.test_get_stores_by_owner()
            self.test_error_handling()
            self.test_cors_headers()
            
            # Print summary
            self.print_summary()
            
        except Exception as e:
            print(f"❌ Test execution failed: {str(e)}")
            self.test_results["failed"] += 1

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 STORES INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors:")
            for error in self.test_results['errors']:
                print(f"  • {error}")
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

def main():
    """Main function to run stores integration tests"""
    test = StoresIntegrationTest()
    test.run_all_tests()

if __name__ == "__main__":
    main() 