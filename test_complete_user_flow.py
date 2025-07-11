#!/usr/bin/env python3
"""
Complete User Flow Integration Test

This script tests a complete user journey through the Anna Akka Platform:
1. User registration/login (mock)
2. Browse stores
3. Browse products
4. Add items to cart
5. Place order
6. Track order status

All tests use the actual API endpoint at https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev
"""

import requests
import json
import time
import random
from datetime import datetime

# Configuration
from env_config import get_base_url

BASE_URL = get_base_url()
from env_config import get_headers

HEADERS = get_headers()

class CompleteUserFlowTest:
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
        """Setup test data for the complete user flow"""
        timestamp = int(time.time())
        self.test_data = {
            "user_id": "mock-user-id",  # Use mock user ID
            "customer_id": "mock-customer-id",  # Use mock customer ID
            "store_id": "mock-store-id",  # Use mock store ID
            "product_id": None,  # Will be set after browsing products
            "order_id": None,
            "cart_items": [],
            "test_phone": "+919876543210",
            "test_email": "test.user@example.com",
            "test_address": f"Test Address {timestamp}, Test City",
            "test_phone_delivery": f"+91 98765 {random.randint(10000, 99999)}"
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

    def get_available_products(self):
        """Get available products from the catalog"""
        try:
            response = self.session.get(f"{BASE_URL}/available-products")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'body' in data:
                    try:
                        body_data = json.loads(data['body'])
                        return body_data.get('products', [])
                    except json.JSONDecodeError:
                        return []
                elif isinstance(data, dict) and 'products' in data:
                    return data.get('products', [])
            return []
        except Exception as e:
            print(f"  ❌ Error getting available products: {str(e)}")
            return []

    def step_1_browse_stores(self):
        """Step 1: User browses available stores"""
        print("\n🏪 Step 1: Browse Stores")
        print("=" * 50)
        
        # Get all stores
        result = self.test_endpoint("GET", "/stores", expected_status=200, test_name="Browse All Stores")
        if result:
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'stores' in body_data:
                        stores = body_data['stores']
                        print(f"  📊 Found {len(stores)} stores")
                        
                        if stores:
                            # Select first store for the flow
                            selected_store = stores[0]
                            self.test_data["store_id"] = selected_store.get('id')
                            print(f"  🏪 Selected store: {selected_store.get('name', 'N/A')}")
                            print(f"  📍 Address: {selected_store.get('address', 'N/A')}")
                            print(f"  📞 Phone: {selected_store.get('phone', 'N/A')}")
                            return True
                except json.JSONDecodeError:
                    pass
            elif isinstance(result, dict) and 'stores' in result:
                stores = result['stores']
                print(f"  📊 Found {len(stores)} stores")
                
                if stores:
                    selected_store = stores[0]
                    self.test_data["store_id"] = selected_store.get('id')
                    print(f"  🏪 Selected store: {selected_store.get('name', 'N/A')}")
                    print(f"  📍 Address: {selected_store.get('address', 'N/A')}")
                    print(f"  📞 Phone: {selected_store.get('phone', 'N/A')}")
                    return True
        
        print("  ⚠️  No stores found or failed to get stores")
        return False

    def step_2_browse_products(self):
        """Step 2: User browses products from selected store"""
        print("\n📦 Step 2: Browse Products")
        print("=" * 50)
        
        # Get products from selected store
        result = self.test_endpoint("GET", f"/stores/{self.test_data['store_id']}/products", expected_status=200, test_name="Browse Store Products")
        if result:
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'products' in body_data:
                        products = body_data['products']
                        print(f"  📊 Found {len(products)} products")
                        
                        if products:
                            # Select first product for the flow
                            selected_product = products[0]
                            self.test_data["product_id"] = selected_product.get('id')
                            print(f"  📦 Selected product: {selected_product.get('name', 'N/A')}")
                            print(f"  💰 Price: {selected_product.get('price', 'N/A')}")
                            print(f"  📦 Stock: {selected_product.get('stock', 'N/A')}")
                            return True
                except json.JSONDecodeError:
                    pass
            elif isinstance(result, dict) and 'products' in result:
                products = result['products']
                print(f"  📊 Found {len(products)} products")
                
                if products:
                    selected_product = products[0]
                    self.test_data["product_id"] = selected_product.get('id')
                    print(f"  📦 Selected product: {selected_product.get('name', 'N/A')}")
                    print(f"  💰 Price: {selected_product.get('price', 'N/A')}")
                    print(f"  📦 Stock: {selected_product.get('stock', 'N/A')}")
                    return True
        
        print("  ⚠️  No products found or failed to get products")
        return False

    def step_3_add_to_cart(self):
        """Step 3: User adds items to cart"""
        print("\n🛒 Step 3: Add to Cart")
        print("=" * 50)
        
        # If no product was selected from store products, get one from available products
        if not self.test_data["product_id"]:
            print("  🔍 No product selected from store, getting from available products...")
            available_products = self.get_available_products()
            if available_products:
                # Use the first available product
                self.test_data["product_id"] = available_products[0].get('id')
                print(f"  📦 Using available product: {available_products[0].get('name', 'N/A')}")
            else:
                print("  ❌ No available products found")
                return False
        
        # Add item to cart
        cart_data = {
            "product_id": self.test_data["product_id"],
            "quantity": 2
        }
        
        result = self.test_endpoint("POST", "/cart/items", cart_data, 201, "Add Item to Cart")
        if result:
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'cart' in body_data:
                        cart = body_data['cart']
                        print(f"  📊 Cart items: {len(cart.get('items', []))}")
                        print(f"  💰 Cart total: {cart.get('total', 0)}")
                        self.test_data["cart_items"] = cart.get('items', [])
                        return True
                except json.JSONDecodeError:
                    pass
            elif isinstance(result, dict) and 'cart' in result:
                cart = result['cart']
                print(f"  📊 Cart items: {len(cart.get('items', []))}")
                print(f"  💰 Cart total: {cart.get('total', 0)}")
                self.test_data["cart_items"] = cart.get('items', [])
                return True
        
        print("  ⚠️  Failed to add item to cart")
        return False

    def step_4_view_cart(self):
        """Step 4: User views their cart"""
        print("\n🛒 Step 4: View Cart")
        print("=" * 50)
        
        # Get cart contents
        result = self.test_endpoint("GET", "/cart", expected_status=200, test_name="View Cart")
        if result:
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'cart' in body_data:
                        cart = body_data['cart']
                        print(f"  📊 Cart items: {len(cart.get('items', []))}")
                        print(f"  💰 Cart total: {cart.get('total', 0)}")
                        
                        for item in cart.get('items', []):
                            print(f"    📦 {item.get('name', 'N/A')} - Qty: {item.get('quantity', 0)} - Price: {item.get('price', 0)}")
                        return True
                except json.JSONDecodeError:
                    pass
            elif isinstance(result, dict) and 'cart' in result:
                cart = result['cart']
                print(f"  📊 Cart items: {len(cart.get('items', []))}")
                print(f"  💰 Cart total: {cart.get('total', 0)}")
                
                for item in cart.get('items', []):
                    print(f"    📦 {item.get('name', 'N/A')} - Qty: {item.get('quantity', 0)} - Price: {item.get('price', 0)}")
                return True
        
        print("  ⚠️  Failed to view cart")
        return False

    def step_5_place_order(self):
        """Step 5: User places an order"""
        print("\n📦 Step 5: Place Order")
        print("=" * 50)
        
        # Create order from cart
        order_data = {
            "store_id": self.test_data["store_id"],
            "items": [
                {
                    "product_id": self.test_data["product_id"],
                    "quantity": 2,
                    "price": 25.50
                }
            ],
            "delivery_address": self.test_data["test_address"],
            "delivery_phone": self.test_data["test_phone_delivery"],
            "payment_method": "cash_on_delivery"
        }
        
        result = self.test_endpoint("POST", "/orders", order_data, 201, "Place Order")
        if result:
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'order' in body_data:
                        order = body_data['order']
                        self.test_data["order_id"] = order.get('id')
                        print(f"  📦 Order created: {order.get('id', 'N/A')}")
                        print(f"  💰 Order total: {order.get('total', 0)}")
                        print(f"  📊 Order status: {order.get('status', 'N/A')}")
                        return True
                except json.JSONDecodeError:
                    pass
            elif isinstance(result, dict) and 'order' in result:
                order = result['order']
                self.test_data["order_id"] = order.get('id')
                print(f"  📦 Order created: {order.get('id', 'N/A')}")
                print(f"  💰 Order total: {order.get('total', 0)}")
                print(f"  📊 Order status: {order.get('status', 'N/A')}")
                return True
        
        print("  ⚠️  Failed to place order")
        return False

    def step_6_track_order(self):
        """Step 6: User tracks their order"""
        print("\n📦 Step 6: Track Order")
        print("=" * 50)
        
        if not self.test_data["order_id"]:
            print("  ⚠️  No order ID available for tracking")
            return False
        
        # Get order details
        result = self.test_endpoint("GET", f"/orders/{self.test_data['order_id']}", expected_status=200, test_name="Track Order")
        if result:
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    print(f"  📦 Order ID: {body_data.get('id', 'N/A')}")
                    print(f"  📊 Status: {body_data.get('status', 'N/A')}")
                    print(f"  💰 Total: {body_data.get('total', 0)}")
                    print(f"  📅 Created: {body_data.get('created_at', 'N/A')}")
                    return True
                except json.JSONDecodeError:
                    pass
            elif isinstance(result, dict):
                print(f"  📦 Order ID: {result.get('id', 'N/A')}")
                print(f"  📊 Status: {result.get('status', 'N/A')}")
                print(f"  💰 Total: {result.get('total', 0)}")
                print(f"  📅 Created: {result.get('created_at', 'N/A')}")
                return True
        
        print("  ⚠️  Failed to track order")
        return False

    def step_7_update_order_status(self):
        """Step 7: Update order status (simulating store action)"""
        print("\n📦 Step 7: Update Order Status")
        print("=" * 50)
        
        if not self.test_data["order_id"]:
            print("  ⚠️  No order ID available for status update")
            return False
        
        # Update order status
        status_data = {
            "status": "confirmed"
        }
        
        result = self.test_endpoint("PUT", f"/orders/{self.test_data['order_id']}/status", status_data, 200, "Update Order Status")
        if result:
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'order' in body_data:
                        order = body_data['order']
                        print(f"  📦 Order ID: {order.get('id', 'N/A')}")
                        print(f"  📊 New Status: {order.get('status', 'N/A')}")
                        print(f"  📅 Updated: {order.get('updated_at', 'N/A')}")
                        return True
                except json.JSONDecodeError:
                    pass
            elif isinstance(result, dict) and 'order' in result:
                order = result['order']
                print(f"  📦 Order ID: {order.get('id', 'N/A')}")
                print(f"  📊 New Status: {order.get('status', 'N/A')}")
                print(f"  📅 Updated: {order.get('updated_at', 'N/A')}")
                return True
        
        print("  ⚠️  Failed to update order status")
        return False

    def step_8_clear_cart(self):
        """Step 8: User clears their cart after order"""
        print("\n🛒 Step 8: Clear Cart")
        print("=" * 50)
        
        # Clear cart
        result = self.test_endpoint("DELETE", "/cart", expected_status=200, test_name="Clear Cart")
        if result:
            print("  ✅ Cart cleared successfully")
            return True
        
        print("  ⚠️  Failed to clear cart")
        return False

    def run_complete_flow(self):
        """Run the complete user flow test"""
        print("🚀 Starting Complete User Flow Test")
        print("=" * 60)
        print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 API Base URL: {BASE_URL}")
        print(f"👤 Mock User ID: {self.test_data['user_id']}")
        print(f"👤 Mock Customer ID: {self.test_data['customer_id']}")
        print("=" * 60)
        
        flow_steps = [
            ("Browse Stores", self.step_1_browse_stores),
            ("Browse Products", self.step_2_browse_products),
            ("Add to Cart", self.step_3_add_to_cart),
            ("View Cart", self.step_4_view_cart),
            ("Place Order", self.step_5_place_order),
            ("Track Order", self.step_6_track_order),
            ("Update Order Status", self.step_7_update_order_status),
            ("Clear Cart", self.step_8_clear_cart)
        ]
        
        successful_steps = 0
        total_steps = len(flow_steps)
        
        for step_name, step_func in flow_steps:
            print(f"\n{'='*40}")
            print(f"🔄 Running: {step_name}")
            print(f"{'='*40}")
            
            try:
                if step_func():
                    successful_steps += 1
                    print(f"✅ {step_name}: COMPLETED")
                else:
                    print(f"❌ {step_name}: FAILED")
            except Exception as e:
                print(f"❌ {step_name}: EXCEPTION - {str(e)}")
        
        # Print flow summary
        print(f"\n{'='*60}")
        print("📊 COMPLETE USER FLOW SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Successful steps: {successful_steps}/{total_steps}")
        print(f"📈 Success rate: {(successful_steps/total_steps)*100:.1f}%")
        
        if successful_steps == total_steps:
            print("🎉 Complete user flow test PASSED!")
            self.test_results["passed"] += 1
        else:
            print("❌ Complete user flow test FAILED!")
            self.test_results["failed"] += 1
        
        print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

    def run_all_tests(self):
        """Run all tests"""
        try:
            self.run_complete_flow()
            self.print_summary()
        except Exception as e:
            print(f"❌ Test execution failed: {str(e)}")
            self.test_results["failed"] += 1

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 COMPLETE USER FLOW TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        
        if self.test_results['errors']:
            print("\n❌ Errors:")
            for error in self.test_results['errors']:
                print(f"  • {error}")
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

def main():
    """Main function to run complete user flow test"""
    test = CompleteUserFlowTest()
    test.run_all_tests()

if __name__ == "__main__":
    main() 