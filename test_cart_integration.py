#!/usr/bin/env python3
"""
Cart Integration Tests for Anna Akka Platform

This module contains comprehensive integration tests for all cart endpoints:
- Get cart
- Add item to cart
- Update cart item
- Remove item from cart
- Clear cart
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
BASE_URL = "https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev"
HEADERS = {
    "Content-Type": "application/json"
}

class CartIntegrationTest:
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
        
        # First, let's create a test product in the available products catalog
        self.create_test_product()
        
        self.test_data = {
            "user_id": "mock-customer-id",  # Use mock customer ID
            "store_id": f"test-store-{timestamp}",
            "product_id": "test-product-cart",  # Use a fixed product ID for testing
            "quantity": random.randint(1, 10),
            "large_quantity": 999999,
            "zero_quantity": 0,
            "negative_quantity": -5,
            "invalid_product_id": "invalid-product-id",
            "invalid_store_id": "invalid-store-id",
            "invalid_user_id": "invalid-user-id",
            "test_phone": "+919876543210",  # Test phone number
            "test_otp": "123456"  # Test OTP
        }

    def create_test_product(self):
        """Create a test product in the available products catalog"""
        try:
            import boto3
            import os
            from decimal import Decimal
            from datetime import datetime, UTC
            
            # Initialize DynamoDB client
            dynamodb = boto3.resource('dynamodb')
            table_name = os.environ.get('AVAILABLE_PRODUCTS_TABLE', 'anna-akka-platform-available-products-table')
            available_products_table = dynamodb.Table(table_name) # type: ignore
            
            # Create test product
            product_item = {
                'id': 'test-product-cart',
                'name': 'Test Product for Cart',
                'description': 'A test product for cart integration tests',
                'price': Decimal('10.99'),
                'unit': 'piece',
                'category_id': 'test',
                'image_url': 'https://example.com/test-image.jpg',
                'created_at': datetime.now(UTC).isoformat(),
                'updated_at': datetime.now(UTC).isoformat()
            }
            
            # Add to DynamoDB
            available_products_table.put_item(Item=product_item)
            print("✓ Created test product: test-product-cart")
            
        except Exception as e:
            print(f"⚠️  Could not create test product: {str(e)}")
            # Continue with tests even if product creation fails

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

    def test_get_cart(self):
        """Test GET /cart endpoint"""
        print("\n🛒 Testing Get Cart")
        print("=" * 50)
        
        # Test get cart (no authentication required with mock system)
        result = self.test_endpoint("GET", "/cart", expected_status=200, test_name="Get Cart")
        if result:
            # Verify response structure
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'cart' in body_data:
                        cart = body_data['cart']
                        print(f"  📊 Cart items: {len(cart.get('items', []))}")
                        print(f"  💰 Total: {cart.get('total', 0)}")
                        
                        # Test response structure
                        required_fields = ['items', 'total', 'item_count']
                        missing_fields = [field for field in required_fields if field not in cart]
                        if not missing_fields:
                            self.log_test("Cart Structure Validation", "PASS")
                            self.test_results["passed"] += 1
                        else:
                            self.log_test("Cart Structure Validation", "FAIL", f"Missing fields: {missing_fields}")
                            self.test_results["failed"] += 1
                    else:
                        self.log_test("Response Structure", "FAIL", "Missing 'cart' field in response")
                        self.test_results["failed"] += 1
                except json.JSONDecodeError:
                    self.log_test("Response JSON Parsing", "FAIL", "Invalid JSON in response body")
                    self.test_results["failed"] += 1
            else:
                # Direct response
                if isinstance(result, dict) and 'cart' in result:
                    cart = result['cart']
                    print(f"  📊 Cart items: {len(cart.get('items', []))}")
                    print(f"  💰 Total: {cart.get('total', 0)}")
                else:
                    self.log_test("Response Structure", "FAIL", "Unexpected response structure")
                    self.test_results["failed"] += 1

    def test_add_to_cart(self):
        """Test POST /cart/items endpoint"""
        print("\n🛒 Testing Add to Cart")
        print("=" * 50)
        
        # Test add item to cart
        add_data = {
            "product_id": self.test_data["product_id"],
            "quantity": self.test_data["quantity"]
        }
        
        result = self.test_endpoint("POST", "/cart/items", add_data, 201, "Add Item to Cart")
        if result:
            # Verify response structure
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'message' in body_data and 'cart' in body_data:
                        cart = body_data['cart']
                        print(f"  📊 Cart items after add: {len(cart.get('items', []))}")
                        print(f"  💰 Total after add: {cart.get('total', 0)}")
                        
                        # Test response structure
                        required_fields = ['message', 'cart']
                        missing_fields = [field for field in required_fields if field not in body_data]
                        if not missing_fields:
                            self.log_test("Add to Cart Response Structure", "PASS")
                            self.test_results["passed"] += 1
                        else:
                            self.log_test("Add to Cart Response Structure", "FAIL", f"Missing fields: {missing_fields}")
                            self.test_results["failed"] += 1
                    else:
                        self.log_test("Add to Cart Response", "FAIL", "Missing expected fields in response")
                        self.test_results["failed"] += 1
                except json.JSONDecodeError:
                    self.log_test("Add to Cart JSON Parsing", "FAIL", "Invalid JSON in response body")
                    self.test_results["failed"] += 1
            else:
                # Direct response
                if isinstance(result, dict) and 'message' in result and 'cart' in result:
                    cart = result['cart']
                    print(f"  📊 Cart items after add: {len(cart.get('items', []))}")
                    print(f"  💰 Total after add: {cart.get('total', 0)}")
                else:
                    self.log_test("Add to Cart Response", "FAIL", "Unexpected response structure")
                    self.test_results["failed"] += 1
        
        # Test add item with invalid data
        invalid_data = {
            "product_id": self.test_data["invalid_product_id"],
            "quantity": self.test_data["quantity"]
        }
        self.test_endpoint("POST", "/cart/items", invalid_data, 400, "Add Invalid Product to Cart")
        
        # Test add item with invalid quantity
        invalid_quantity_data = {
            "product_id": self.test_data["product_id"],
            "quantity": self.test_data["negative_quantity"]
        }
        self.test_endpoint("POST", "/cart/items", invalid_quantity_data, 400, "Add Item with Negative Quantity")

    def test_update_cart_item(self):
        """Test PUT /cart/items/{product_id} endpoint"""
        print("\n🛒 Testing Update Cart Item")
        print("=" * 50)
        
        # First add an item to cart
        add_data = {
            "product_id": self.test_data["product_id"],
            "quantity": self.test_data["quantity"]
        }
        self.test_endpoint("POST", "/cart/items", add_data, 201, "Add Item for Update")
        
        # Test update cart item
        update_data = {
            "quantity": self.test_data["quantity"] + 2
        }
        
        result = self.test_endpoint("PUT", f"/cart/items/{self.test_data['product_id']}", update_data, 200, "Update Cart Item")
        if result:
            # Verify response structure
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'message' in body_data and 'cart' in body_data:
                        cart = body_data['cart']
                        print(f"  📊 Cart items after update: {len(cart.get('items', []))}")
                        print(f"  💰 Total after update: {cart.get('total', 0)}")
                        
                        # Test response structure
                        required_fields = ['message', 'cart']
                        missing_fields = [field for field in required_fields if field not in body_data]
                        if not missing_fields:
                            self.log_test("Update Cart Item Response Structure", "PASS")
                            self.test_results["passed"] += 1
                        else:
                            self.log_test("Update Cart Item Response Structure", "FAIL", f"Missing fields: {missing_fields}")
                            self.test_results["failed"] += 1
                    else:
                        self.log_test("Update Cart Item Response", "FAIL", "Missing expected fields in response")
                        self.test_results["failed"] += 1
                except json.JSONDecodeError:
                    self.log_test("Update Cart Item JSON Parsing", "FAIL", "Invalid JSON in response body")
                    self.test_results["failed"] += 1
            else:
                # Direct response
                if isinstance(result, dict) and 'message' in result and 'cart' in result:
                    cart = result['cart']
                    print(f"  📊 Cart items after update: {len(cart.get('items', []))}")
                    print(f"  💰 Total after update: {cart.get('total', 0)}")
                else:
                    self.log_test("Update Cart Item Response", "FAIL", "Unexpected response structure")
                    self.test_results["failed"] += 1
        
        # Test update non-existent item
        self.test_endpoint("PUT", f"/cart/items/{self.test_data['invalid_product_id']}", update_data, 400, "Update Non-existent Cart Item")

    def test_remove_from_cart(self):
        """Test DELETE /cart/items/{product_id} endpoint"""
        print("\n🛒 Testing Remove from Cart")
        print("=" * 50)
        
        # First add an item to cart
        add_data = {
            "product_id": self.test_data["product_id"],
            "quantity": self.test_data["quantity"]
        }
        self.test_endpoint("POST", "/cart/items", add_data, 201, "Add Item for Removal")
        
        # Test remove item from cart
        result = self.test_endpoint("DELETE", f"/cart/items/{self.test_data['product_id']}", expected_status=200, test_name="Remove Item from Cart")
        if result:
            # Verify response structure
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'message' in body_data and 'cart' in body_data:
                        cart = body_data['cart']
                        print(f"  📊 Cart items after removal: {len(cart.get('items', []))}")
                        print(f"  💰 Total after removal: {cart.get('total', 0)}")
                        
                        # Test response structure
                        required_fields = ['message', 'cart']
                        missing_fields = [field for field in required_fields if field not in body_data]
                        if not missing_fields:
                            self.log_test("Remove from Cart Response Structure", "PASS")
                            self.test_results["passed"] += 1
                        else:
                            self.log_test("Remove from Cart Response Structure", "FAIL", f"Missing fields: {missing_fields}")
                            self.test_results["failed"] += 1
                    else:
                        self.log_test("Remove from Cart Response", "FAIL", "Missing expected fields in response")
                        self.test_results["failed"] += 1
                except json.JSONDecodeError:
                    self.log_test("Remove from Cart JSON Parsing", "FAIL", "Invalid JSON in response body")
                    self.test_results["failed"] += 1
            else:
                # Direct response
                if isinstance(result, dict) and 'message' in result and 'cart' in result:
                    cart = result['cart']
                    print(f"  📊 Cart items after removal: {len(cart.get('items', []))}")
                    print(f"  💰 Total after removal: {cart.get('total', 0)}")
                else:
                    self.log_test("Remove from Cart Response", "FAIL", "Unexpected response structure")
                    self.test_results["failed"] += 1
        
        # Test remove non-existent item
        self.test_endpoint("DELETE", f"/cart/items/{self.test_data['invalid_product_id']}", expected_status=404, test_name="Remove Non-existent Item")

    def test_clear_cart(self):
        """Test DELETE /cart endpoint"""
        print("\n🛒 Testing Clear Cart")
        print("=" * 50)
        
        # First add some items to cart
        add_data = {
            "product_id": self.test_data["product_id"],
            "quantity": self.test_data["quantity"]
        }
        self.test_endpoint("POST", "/cart/items", add_data, 201, "Add Item for Clear")
        
        # Test clear cart
        result = self.test_endpoint("DELETE", "/cart", expected_status=200, test_name="Clear Cart")
        if result:
            # Verify response structure
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'message' in body_data and 'cart' in body_data:
                        cart = body_data['cart']
                        print(f"  📊 Cart items after clear: {len(cart.get('items', []))}")
                        print(f"  💰 Total after clear: {cart.get('total', 0)}")
                        
                        # Test response structure
                        required_fields = ['message', 'cart']
                        missing_fields = [field for field in required_fields if field not in body_data]
                        if not missing_fields:
                            self.log_test("Clear Cart Response Structure", "PASS")
                            self.test_results["passed"] += 1
                        else:
                            self.log_test("Clear Cart Response Structure", "FAIL", f"Missing fields: {missing_fields}")
                            self.test_results["failed"] += 1
                    else:
                        self.log_test("Clear Cart Response", "FAIL", "Missing expected fields in response")
                        self.test_results["failed"] += 1
                except json.JSONDecodeError:
                    self.log_test("Clear Cart JSON Parsing", "FAIL", "Invalid JSON in response body")
                    self.test_results["failed"] += 1
            else:
                # Direct response - handle both formats
                if isinstance(result, dict):
                    if 'message' in result and 'cart' in result:
                        cart = result['cart']
                        print(f"  📊 Cart items after clear: {len(cart.get('items', []))}")
                        print(f"  💰 Total after clear: {cart.get('total', 0)}")
                        self.log_test("Clear Cart Response Structure", "PASS")
                        self.test_results["passed"] += 1
                    elif 'message' in result:
                        # Simple success message format
                        print(f"  📝 Message: {result.get('message', 'N/A')}")
                        self.log_test("Clear Cart Response Structure", "PASS")
                        self.test_results["passed"] += 1
                    else:
                        self.log_test("Clear Cart Response", "FAIL", "Unexpected response structure")
                        self.test_results["failed"] += 1
                else:
                    self.log_test("Clear Cart Response", "FAIL", "Unexpected response structure")
                    self.test_results["failed"] += 1

    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🛒 Testing Error Handling")
        print("=" * 50)
        
        # Test missing required fields
        self.test_endpoint("POST", "/cart/items", {}, 400, "Add Item - Missing Fields")
        
        # Test invalid product ID
        invalid_data = {
            "product_id": self.test_data["invalid_product_id"],
            "quantity": self.test_data["quantity"]
        }
        self.test_endpoint("POST", "/cart/items", invalid_data, 400, "Add Item - Invalid Product")
        
        # Test invalid quantity
        invalid_quantity_data = {
            "product_id": self.test_data["product_id"],
            "quantity": self.test_data["negative_quantity"]
        }
        self.test_endpoint("POST", "/cart/items", invalid_quantity_data, 400, "Add Item - Negative Quantity")
        
        # Test zero quantity
        zero_quantity_data = {
            "product_id": self.test_data["product_id"],
            "quantity": self.test_data["zero_quantity"]
        }
        self.test_endpoint("POST", "/cart/items", zero_quantity_data, 400, "Add Item - Zero Quantity")
        
        # Test large quantity
        large_quantity_data = {
            "product_id": self.test_data["product_id"],
            "quantity": self.test_data["large_quantity"]
        }
        self.test_endpoint("POST", "/cart/items", large_quantity_data, 400, "Add Item - Large Quantity")

    def test_cors_headers(self):
        """Test CORS headers"""
        print("\n🛒 Testing CORS Headers")
        print("=" * 50)
        
        # Test OPTIONS request
        try:
            response = self.session.options(f"{BASE_URL}/cart")
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
        """Run all cart integration tests"""
        print("🚀 Starting Cart Integration Tests")
        print("=" * 60)
        print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 API Base URL: {BASE_URL}")
        print(f"👤 Mock Customer ID: {self.test_data['user_id']}")
        print("=" * 60)
        
        try:
            # Run all test methods
            self.test_get_cart()
            self.test_add_to_cart()
            self.test_update_cart_item()
            self.test_remove_from_cart()
            self.test_clear_cart()
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
        print("📊 CART INTEGRATION TEST SUMMARY")
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
    """Main function to run cart integration tests"""
    test = CartIntegrationTest()
    test.run_all_tests()

if __name__ == "__main__":
    main() 