#!/usr/bin/env python3
"""
Orders Integration Test Script

This script tests the orders endpoints to verify the routing fix works correctly.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
from env_config import get_base_url

BASE_URL = get_base_url()
from env_config import get_headers

HEADERS = get_headers()

class OrdersIntegrationTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
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

    def test_get_orders(self):
        """Test GET /orders endpoint"""
        print("\n📋 Testing Get Orders")
        print("=" * 50)
        
        # Test get orders list
        result = self.test_endpoint("GET", "/orders", expected_status=200, test_name="Get Orders List")
        if result:
            print(f"  📊 Orders retrieved successfully")
            print(f"  📄 Response: {json.dumps(result, indent=2)}")

    def test_get_order_by_id(self):
        """Test GET /orders/{id} endpoint"""
        print("\n📋 Testing Get Order by ID")
        print("=" * 50)
        
        # Test with a specific order ID
        order_id = "46d949be-8577-42d4-b8f9-b692ecbc0c63"
        result = self.test_endpoint("GET", f"/orders/{order_id}", expected_status=200, test_name="Get Order by ID")
        if result:
            print(f"  📊 Order retrieved successfully")
            print(f"  📄 Response: {json.dumps(result, indent=2)}")
        
        # Test with non-existent order ID
        self.test_endpoint("GET", "/orders/non-existent-id", expected_status=404, test_name="Get Non-existent Order")

    def test_create_order(self):
        """Test POST /orders endpoint"""
        print("\n📋 Testing Create Order")
        print("=" * 50)
        
        # Test create order
        order_data = {
            "store_id": "test-store-id",
            "delivery_address": "123 Test Street, Bangalore",
            "notes": "Test order"
        }
        
        result = self.test_endpoint("POST", "/orders", order_data, 201, "Create Order")
        if result:
            print(f"  📊 Order created successfully")
            print(f"  📄 Response: {json.dumps(result, indent=2)}")

    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n⚠️ Testing Error Handling")
        print("=" * 50)
        
        # Test invalid method
        self.test_endpoint("PUT", "/orders", {}, 405, "Invalid Method - PUT Orders")
        
        # Test missing required fields
        incomplete_order = {"store_id": "test-store"}
        self.test_endpoint("POST", "/orders", incomplete_order, 400, "Create Order - Missing Fields")

    def run_all_tests(self):
        """Run all orders integration tests"""
        print("🚀 Starting Orders Integration Tests")
        print("=" * 60)
        print(f"Base URL: {BASE_URL}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            self.test_get_orders()
            self.test_get_order_by_id()
            self.test_create_order()
            self.test_error_handling()
            
        except Exception as e:
            print(f"❌ Test suite failed with exception: {str(e)}")
        
        finally:
            self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 ORDERS INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        total_tests = self.test_results['passed'] + self.test_results['failed']
        if total_tests > 0:
            success_rate = (self.test_results['passed'] / total_tests) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors:")
            for error in self.test_results['errors']:
                print(f"  • {error}")
        
        print("=" * 60)

def main():
    """Main function to run orders integration tests"""
    test = OrdersIntegrationTest()
    test.run_all_tests()

if __name__ == "__main__":
    main() 