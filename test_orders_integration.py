#!/usr/bin/env python3
"""
Comprehensive Integration Tests for Orders API
Tests all orders endpoints including GET, POST, and PUT operations with all parameters
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
BASE_URL = "https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev"
TEST_USER_ID = "test-user-orders-123"
TEST_STORE_ID = "test-store-orders-456"
TEST_AVAILABLE_PRODUCT_ID = "b9238c4d-77e1-4585-b086-11af2dabdb59"

# Test data
TEST_ORDER_DATA = {
    "create_from_cart": False,
    "store_id": TEST_STORE_ID,
    "delivery_address": "123 Test Street, Bangalore, Karnataka 560001",
    "notes": "Test order with manual items",
    "items": [
        {
            "product_id": "test-prod-789",
            "product_name": "Test Chicken Biryani",
            "quantity": 2,
            "price": 15.00,
            "unit": "piece",
            "special_notes": "Extra spicy please"
        },
        {
            "product_id": "test-prod-790",
            "product_name": "Test Naan Bread",
            "quantity": 3,
            "price": 5.17,
            "unit": "piece",
            "special_notes": ""
        }
    ]
}

TEST_CART_ORDER_DATA = {
    "create_from_cart": True,
    "store_id": TEST_STORE_ID,
    "delivery_address": "456 Test Avenue, Mumbai, Maharashtra 400001",
    "notes": "Test order from cart"
}

class OrdersIntegrationTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-User-ID': TEST_USER_ID
        })
        self.created_orders = []
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }

    def log_test(self, test_name, success, error=None):
        """Log test results"""
        if success:
            print(f"✅ PASS: {test_name}")
            self.test_results['passed'] += 1
        else:
            print(f"❌ FAIL: {test_name}")
            if error:
                print(f"   Error: {error}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append({
                'test': test_name,
                'error': str(error) if error else 'Unknown error'
            })

    def make_request(self, method, endpoint, data=None, params=None):
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
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except Exception as e:
            print(f"Request error: {str(e)}")
            return None

    def test_get_customer_orders_basic(self):
        """Test GET /orders - Basic customer orders retrieval"""
        print("\n🔍 Testing GET /orders - Basic customer orders retrieval")
        
        response = self.make_request('GET', '/orders')
        
        if response and response.status_code == 200:
            data = response.json()
            if 'orders' in data and 'pagination' in data:
                self.log_test("GET /orders - Basic", True)
                print(f"   Found {len(data['orders'])} orders")
                print(f"   Pagination: {data['pagination']}")
            else:
                self.log_test("GET /orders - Basic", False, "Invalid response structure")
        else:
            self.log_test("GET /orders - Basic", False, f"Status: {response.status_code if response else 'No response'}")

    def test_get_customer_orders_with_pagination(self):
        """Test GET /orders - Customer orders with pagination parameters"""
        print("\n🔍 Testing GET /orders - Customer orders with pagination")
        
        params = {
            'page': 1,
            'limit': 5
        }
        
        response = self.make_request('GET', '/orders', params=params)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'orders' in data and 'pagination' in data:
                pagination = data['pagination']
                if (pagination.get('current_page') == 1 and 
                    pagination.get('items_per_page') == 5):
                    self.log_test("GET /orders - With pagination", True)
                    print(f"   Pagination: {pagination}")
                else:
                    self.log_test("GET /orders - With pagination", False, "Invalid pagination data")
            else:
                self.log_test("GET /orders - With pagination", False, "Invalid response structure")
        else:
            self.log_test("GET /orders - With pagination", False, f"Status: {response.status_code if response else 'No response'}")

    def test_get_store_orders_basic(self):
        """Test GET /orders?store_id={store_id} - Basic store orders retrieval"""
        print("\n🔍 Testing GET /orders - Store orders retrieval")
        
        params = {
            'store_id': TEST_STORE_ID
        }
        
        response = self.make_request('GET', '/orders', params=params)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'orders' in data and 'pagination' in data:
                self.log_test("GET /orders - Store orders", True)
                print(f"   Found {len(data['orders'])} orders for store {TEST_STORE_ID}")
                print(f"   Pagination: {data['pagination']}")
            else:
                self.log_test("GET /orders - Store orders", False, "Invalid response structure")
        else:
            self.log_test("GET /orders - Store orders", False, f"Status: {response.status_code if response else 'No response'}")

    def test_get_store_orders_with_pagination(self):
        """Test GET /orders?store_id={store_id} - Store orders with pagination"""
        print("\n🔍 Testing GET /orders - Store orders with pagination")
        
        params = {
            'store_id': TEST_STORE_ID,
            'page': 1,
            'limit': 3
        }
        
        response = self.make_request('GET', '/orders', params=params)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'orders' in data and 'pagination' in data:
                pagination = data['pagination']
                if (pagination.get('current_page') == 1 and 
                    pagination.get('items_per_page') == 3):
                    self.log_test("GET /orders - Store orders with pagination", True)
                    print(f"   Pagination: {pagination}")
                else:
                    self.log_test("GET /orders - Store orders with pagination", False, "Invalid pagination data")
            else:
                self.log_test("GET /orders - Store orders with pagination", False, "Invalid response structure")
        else:
            self.log_test("GET /orders - Store orders with pagination", False, f"Status: {response.status_code if response else 'No response'}")

    def test_create_order_with_manual_items(self):
        """Test POST /orders - Create order with manual items"""
        print("\n🔍 Testing POST /orders - Create order with manual items")
        
        response = self.make_request('POST', '/orders', data=TEST_ORDER_DATA)
        
        if response and response.status_code == 201:
            data = response.json()
            if 'order' in data and 'message' in data:
                order = data['order']
                if (order.get('store_id') == TEST_STORE_ID and 
                    order.get('customer_id') == TEST_USER_ID and
                    'products' in order):
                    self.log_test("POST /orders - Manual items", True)
                    print(f"   Order ID: {order.get('id')}")
                    print(f"   Total Amount: {order.get('total_amount')}")
                    print(f"   Products: {len(order.get('products', []))}")
                    self.created_orders.append(order.get('id'))
                else:
                    self.log_test("POST /orders - Manual items", False, "Invalid order data")
            else:
                self.log_test("POST /orders - Manual items", False, "Invalid response structure")
        else:
            self.log_test("POST /orders - Manual items", False, f"Status: {response.status_code if response else 'No response'}")

    def test_create_order_with_manual_items_minimal(self):
        """Test POST /orders - Create order with minimal manual items"""
        print("\n🔍 Testing POST /orders - Create order with minimal manual items")
        
        minimal_order_data = {
            "create_from_cart": False,
            "store_id": TEST_STORE_ID,
            "delivery_address": "789 Minimal Street, Delhi, Delhi 110001",
            "items": [
                {
                    "product_id": "minimal-prod-123",
                    "product_name": "Minimal Test Product",
                    "quantity": 1,
                    "price": 10.00,
                    "unit": "piece"
                }
            ]
        }
        
        response = self.make_request('POST', '/orders', data=minimal_order_data)
        
        if response and response.status_code == 201:
            data = response.json()
            if 'order' in data:
                order = data['order']
                if order.get('store_id') == TEST_STORE_ID:
                    self.log_test("POST /orders - Minimal manual items", True)
                    print(f"   Order ID: {order.get('id')}")
                    self.created_orders.append(order.get('id'))
                else:
                    self.log_test("POST /orders - Minimal manual items", False, "Invalid order data")
            else:
                self.log_test("POST /orders - Minimal manual items", False, "Invalid response structure")
        else:
            self.log_test("POST /orders - Minimal manual items", False, f"Status: {response.status_code if response else 'No response'}")

    def test_create_order_with_manual_items_complex(self):
        """Test POST /orders - Create order with complex manual items"""
        print("\n🔍 Testing POST /orders - Create order with complex manual items")
        
        complex_order_data = {
            "create_from_cart": False,
            "store_id": TEST_STORE_ID,
            "delivery_address": "321 Complex Avenue, Chennai, Tamil Nadu 600001",
            "notes": "Complex order with multiple items and special notes",
            "items": [
                {
                    "product_id": "complex-prod-1",
                    "product_name": "Complex Product 1",
                    "quantity": 2,
                    "price": 25.50,
                    "unit": "piece",
                    "special_notes": "Extra spicy, no onions"
                },
                {
                    "product_id": "complex-prod-2",
                    "product_name": "Complex Product 2",
                    "quantity": 1,
                    "price": 45.75,
                    "unit": "kg",
                    "special_notes": "Fresh and organic only"
                },
                {
                    "product_id": "complex-prod-3",
                    "product_name": "Complex Product 3",
                    "quantity": 5,
                    "price": 8.25,
                    "unit": "piece",
                    "special_notes": ""
                }
            ]
        }
        
        response = self.make_request('POST', '/orders', data=complex_order_data)
        
        if response and response.status_code == 201:
            data = response.json()
            if 'order' in data:
                order = data['order']
                products = order.get('products', [])
                if (order.get('store_id') == TEST_STORE_ID and 
                    len(products) == 3):
                    self.log_test("POST /orders - Complex manual items", True)
                    print(f"   Order ID: {order.get('id')}")
                    print(f"   Total Amount: {order.get('total_amount')}")
                    print(f"   Products: {len(products)}")
                    self.created_orders.append(order.get('id'))
                else:
                    self.log_test("POST /orders - Complex manual items", False, "Invalid order data")
            else:
                self.log_test("POST /orders - Complex manual items", False, "Invalid response structure")
        else:
            self.log_test("POST /orders - Complex manual items", False, f"Status: {response.status_code if response else 'No response'}")

    def test_create_order_validation_errors(self):
        """Test POST /orders - Validation error cases"""
        print("\n🔍 Testing POST /orders - Validation error cases")
        
        # Test missing required fields
        invalid_order_data = {
            "create_from_cart": False,
            "delivery_address": "123 Test Street"
            # Missing store_id and items
        }
        
        response = self.make_request('POST', '/orders', data=invalid_order_data)
        
        if response and response.status_code == 400:
            data = response.json()
            if 'error' in data and 'code' in data['error']:
                self.log_test("POST /orders - Validation errors", True)
                print(f"   Error: {data['error'].get('message', 'Unknown error')}")
            else:
                self.log_test("POST /orders - Validation errors", False, "Invalid error response structure")
        else:
            self.log_test("POST /orders - Validation errors", False, f"Expected 400, got: {response.status_code if response else 'No response'}")

    def test_get_order_by_id(self):
        """Test GET /orders/{order_id} - Get specific order"""
        print("\n🔍 Testing GET /orders/{order_id} - Get specific order")
        
        if not self.created_orders:
            self.log_test("GET /orders/{order_id}", False, "No orders created for testing")
            return
        
        order_id = self.created_orders[0]
        response = self.make_request('GET', f'/orders/{order_id}')
        
        if response and response.status_code == 200:
            data = response.json()
            if 'order' in data:
                order = data['order']
                if (order.get('id') == order_id and 
                    order.get('customer_id') == TEST_USER_ID):
                    self.log_test("GET /orders/{order_id}", True)
                    print(f"   Order ID: {order.get('id')}")
                    print(f"   Status: {order.get('status')}")
                    print(f"   Products: {len(order.get('products', []))}")
                else:
                    self.log_test("GET /orders/{order_id}", False, "Invalid order data")
            else:
                self.log_test("GET /orders/{order_id}", False, "Invalid response structure")
        else:
            self.log_test("GET /orders/{order_id}", False, f"Status: {response.status_code if response else 'No response'}")

    def test_get_order_by_id_not_found(self):
        """Test GET /orders/{order_id} - Order not found"""
        print("\n🔍 Testing GET /orders/{order_id} - Order not found")
        
        non_existent_order_id = "non-existent-order-123"
        response = self.make_request('GET', f'/orders/{non_existent_order_id}')
        
        if response and response.status_code == 404:
            data = response.json()
            if 'error' in data and 'code' in data['error']:
                self.log_test("GET /orders/{order_id} - Not found", True)
                print(f"   Error: {data['error'].get('message', 'Unknown error')}")
            else:
                self.log_test("GET /orders/{order_id} - Not found", False, "Invalid error response structure")
        else:
            self.log_test("GET /orders/{order_id} - Not found", False, f"Expected 404, got: {response.status_code if response else 'No response'}")

    def test_update_order_status(self):
        """Test PUT /orders/{order_id}/status - Update order status"""
        print("\n🔍 Testing PUT /orders/{order_id}/status - Update order status")
        
        if not self.created_orders:
            self.log_test("PUT /orders/{order_id}/status", False, "No orders created for testing")
            return
        
        order_id = self.created_orders[0]
        status_data = {
            "status": "preparing"
        }
        
        response = self.make_request('PUT', f'/orders/{order_id}/status', data=status_data)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'order' in data:
                order = data['order']
                if order.get('status') == 'preparing':
                    self.log_test("PUT /orders/{order_id}/status", True)
                    print(f"   Order ID: {order.get('id')}")
                    print(f"   Updated Status: {order.get('status')}")
                else:
                    self.log_test("PUT /orders/{order_id}/status", False, "Status not updated correctly")
            else:
                self.log_test("PUT /orders/{order_id}/status", False, "Invalid response structure")
        else:
            self.log_test("PUT /orders/{order_id}/status", False, f"Status: {response.status_code if response else 'No response'}")

    def test_update_order_status_invalid(self):
        """Test PUT /orders/{order_id}/status - Invalid status"""
        print("\n🔍 Testing PUT /orders/{order_id}/status - Invalid status")
        
        if not self.created_orders:
            self.log_test("PUT /orders/{order_id}/status - Invalid", False, "No orders created for testing")
            return
        
        order_id = self.created_orders[0]
        invalid_status_data = {
            "status": "invalid_status"
        }
        
        response = self.make_request('PUT', f'/orders/{order_id}/status', data=invalid_status_data)
        
        if response and response.status_code == 400:
            data = response.json()
            if 'error' in data and 'code' in data['error']:
                self.log_test("PUT /orders/{order_id}/status - Invalid status", True)
                print(f"   Error: {data['error'].get('message', 'Unknown error')}")
            else:
                self.log_test("PUT /orders/{order_id}/status - Invalid status", False, "Invalid error response structure")
        else:
            self.log_test("PUT /orders/{order_id}/status - Invalid status", False, f"Expected 400, got: {response.status_code if response else 'No response'}")

    def test_update_order_status_missing(self):
        """Test PUT /orders/{order_id}/status - Missing status"""
        print("\n🔍 Testing PUT /orders/{order_id}/status - Missing status")
        
        if not self.created_orders:
            self.log_test("PUT /orders/{order_id}/status - Missing", False, "No orders created for testing")
            return
        
        order_id = self.created_orders[0]
        missing_status_data = {}
        
        response = self.make_request('PUT', f'/orders/{order_id}/status', data=missing_status_data)
        
        if response and response.status_code == 400:
            data = response.json()
            if 'error' in data and 'code' in data['error']:
                self.log_test("PUT /orders/{order_id}/status - Missing status", True)
                print(f"   Error: {data['error'].get('message', 'Unknown error')}")
            else:
                self.log_test("PUT /orders/{order_id}/status - Missing status", False, "Invalid error response structure")
        else:
            self.log_test("PUT /orders/{order_id}/status - Missing status", False, f"Expected 400, got: {response.status_code if response else 'No response'}")

    def test_update_order_status_not_found(self):
        """Test PUT /orders/{order_id}/status - Order not found"""
        print("\n🔍 Testing PUT /orders/{order_id}/status - Order not found")
        
        non_existent_order_id = "non-existent-order-123"
        status_data = {
            "status": "preparing"
        }
        
        response = self.make_request('PUT', f'/orders/{non_existent_order_id}/status', data=status_data)
        
        if response and response.status_code == 404:
            data = response.json()
            if 'error' in data and 'code' in data['error']:
                self.log_test("PUT /orders/{order_id}/status - Not found", True)
                print(f"   Error: {data['error'].get('message', 'Unknown error')}")
            else:
                self.log_test("PUT /orders/{order_id}/status - Not found", False, "Invalid error response structure")
        else:
            self.log_test("PUT /orders/{order_id}/status - Not found", False, f"Expected 404, got: {response.status_code if response else 'No response'}")

    def test_unauthorized_access(self):
        """Test unauthorized access to orders endpoints"""
        print("\n🔍 Testing unauthorized access to orders endpoints")
        
        # Test without user ID
        original_headers = self.session.headers.copy()
        self.session.headers.pop('X-User-ID', None)
        
        response = self.make_request('GET', '/orders')
        
        if response and response.status_code == 401:
            data = response.json()
            if 'error' in data and 'code' in data['error']:
                self.log_test("Unauthorized access", True)
                print(f"   Error: {data['error'].get('message', 'Unknown error')}")
            else:
                self.log_test("Unauthorized access", False, "Invalid error response structure")
        else:
            self.log_test("Unauthorized access", False, f"Expected 401, got: {response.status_code if response else 'No response'}")
        
        # Restore headers
        self.session.headers = original_headers

    def test_method_not_allowed(self):
        """Test method not allowed for orders endpoints"""
        print("\n🔍 Testing method not allowed for orders endpoints")
        
        # Test DELETE method on /orders (not allowed)
        response = self.make_request('DELETE', '/orders')
        
        if response and response.status_code == 405:
            data = response.json()
            if 'error' in data and 'code' in data['error']:
                self.log_test("Method not allowed", True)
                print(f"   Error: {data['error'].get('message', 'Unknown error')}")
            else:
                self.log_test("Method not allowed", False, "Invalid error response structure")
        else:
            self.log_test("Method not allowed", False, f"Expected 405, got: {response.status_code if response else 'No response'}")

    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Orders API Integration Tests")
        print("=" * 60)
        
        # GET endpoint tests
        self.test_get_customer_orders_basic()
        self.test_get_customer_orders_with_pagination()
        self.test_get_store_orders_basic()
        self.test_get_store_orders_with_pagination()
        
        # POST endpoint tests
        self.test_create_order_with_manual_items()
        self.test_create_order_with_manual_items_minimal()
        self.test_create_order_with_manual_items_complex()
        self.test_create_order_validation_errors()
        
        # GET specific order tests
        self.test_get_order_by_id()
        self.test_get_order_by_id_not_found()
        
        # PUT endpoint tests
        self.test_update_order_status()
        self.test_update_order_status_invalid()
        self.test_update_order_status_missing()
        self.test_update_order_status_not_found()
        
        # Error handling tests
        self.test_unauthorized_access()
        self.test_method_not_allowed()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n🔍 ERRORS:")
            for error in self.test_results['errors']:
                print(f"   • {error['test']}: {error['error']}")
        
        print("\n🎯 Orders API Integration Tests Complete!")

def main():
    """Main function to run the integration tests"""
    tester = OrdersIntegrationTest()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 