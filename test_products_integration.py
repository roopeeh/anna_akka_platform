#!/usr/bin/env python3
"""
Products Integration Tests for Anna Akka Platform

This module contains comprehensive integration tests for all products endpoints:
- Get all products with filtering and pagination
- Get specific product
- Get products by store
- Create product
- Update product
- Delete product
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

class ProductsIntegrationTest:
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
            "store_id": "mock-store-id",  # Use mock store ID
            "category_id": f"test-category-{timestamp}",
            "product_name": f"Test Product {timestamp}",
            "product_description": f"Test product description {timestamp}",
            "product_price": random.uniform(10.0, 100.0),
            "product_unit": "kg",
            "product_stock": random.randint(10, 100),
            "product_image_url": f"https://example.com/images/test-product-{timestamp}.jpg",
            "invalid_product_id": "invalid-product-id",
            "invalid_store_id": "invalid-store-id",
            "invalid_category_id": "invalid-category-id",
            "long_name": "A" * 1000,
            "empty_name": "",
            "negative_price": -10.0,
            "zero_price": 0.0,
            "negative_stock": -5,
            "large_stock": 999999
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

    def test_get_products(self):
        """Test GET /products endpoint"""
        print("\n📦 Testing Get Products")
        print("=" * 50)
        
        # Test get all products
        result = self.test_endpoint("GET", "/products", expected_status=200, test_name="Get All Products")
        if result:
            # Verify response structure
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'products' in body_data:
                        products = body_data['products']
                        print(f"  📊 Found {len(products)} products")
                        
                        # Test response structure for first product
                        if products:
                            first_product = products[0]
                            required_fields = ['id', 'name', 'price', 'unit', 'stock', 'created_at']
                            missing_fields = [field for field in required_fields if field not in first_product]
                            if not missing_fields:
                                self.log_test("Product Structure Validation", "PASS")
                                self.test_results["passed"] += 1
                            else:
                                self.log_test("Product Structure Validation", "FAIL", f"Missing fields: {missing_fields}")
                                self.test_results["failed"] += 1
                    else:
                        self.log_test("Response Structure", "FAIL", "Missing 'products' field in response")
                        self.test_results["failed"] += 1
                except json.JSONDecodeError:
                    self.log_test("Response JSON Parsing", "FAIL", "Invalid JSON in response body")
                    self.test_results["failed"] += 1
            else:
                # Direct response
                if isinstance(result, dict) and 'products' in result:
                    products = result['products']
                    print(f"  📊 Found {len(products)} products")
                else:
                    self.log_test("Response Structure", "FAIL", "Unexpected response structure")
                    self.test_results["failed"] += 1
        
        # Test get products with pagination
        self.test_endpoint("GET", "/products?page=1&limit=5", expected_status=200, test_name="Get Products - With Pagination")
        
        # Test get products with filtering
        self.test_endpoint("GET", f"/products?store_id={self.test_data['store_id']}", expected_status=200, test_name="Get Products - Filter by Store")
        self.test_endpoint("GET", f"/products?category_id={self.test_data['category_id']}", expected_status=200, test_name="Get Products - Filter by Category")
        self.test_endpoint("GET", "/products?search=test", expected_status=200, test_name="Get Products - Search")
        self.test_endpoint("GET", "/products?min_price=10&max_price=100", expected_status=200, test_name="Get Products - Price Range")
        self.test_endpoint("GET", "/products?in_stock=true", expected_status=200, test_name="Get Products - In Stock")

    def test_get_specific_product(self):
        """Test GET /products/{id} endpoint"""
        print("\n📦 Testing Get Specific Product")
        print("=" * 50)
        
        # First get all products to find a valid product ID
        products_result = self.test_endpoint("GET", "/products", expected_status=200, test_name="Get Products for ID")
        if products_result:
            product_id = None
            if isinstance(products_result, dict) and 'body' in products_result:
                try:
                    body_data = json.loads(products_result['body'])
                    if 'products' in body_data and body_data['products']:
                        product_id = body_data['products'][0]['id']
                except json.JSONDecodeError:
                    pass
            elif isinstance(products_result, dict) and 'products' in products_result and products_result['products']:
                product_id = products_result['products'][0]['id']
            
            if product_id:
                # Test get specific product
                result = self.test_endpoint("GET", f"/products/{product_id}", expected_status=200, test_name="Get Specific Product - Success")
                if result:
                    # Verify response structure
                    if isinstance(result, dict) and 'body' in result:
                        try:
                            body_data = json.loads(result['body'])
                            required_fields = ['id', 'name', 'price', 'unit', 'stock', 'created_at']
                            missing_fields = [field for field in required_fields if field not in body_data]
                            if not missing_fields:
                                self.log_test("Specific Product Structure", "PASS")
                                self.test_results["passed"] += 1
                            else:
                                self.log_test("Specific Product Structure", "FAIL", f"Missing fields: {missing_fields}")
                                self.test_results["failed"] += 1
                        except json.JSONDecodeError:
                            self.log_test("Specific Product JSON Parsing", "FAIL", "Invalid JSON in response body")
                            self.test_results["failed"] += 1
                    else:
                        # Direct response
                        required_fields = ['id', 'name', 'price', 'unit', 'stock', 'created_at']
                        missing_fields = [field for field in required_fields if field not in result]
                        if not missing_fields:
                            self.log_test("Specific Product Structure", "PASS")
                            self.test_results["passed"] += 1
                        else:
                            self.log_test("Specific Product Structure", "FAIL", f"Missing fields: {missing_fields}")
                            self.test_results["failed"] += 1
        
        # Test get non-existent product
        self.test_endpoint("GET", f"/products/{self.test_data['invalid_product_id']}", expected_status=404, test_name="Get Specific Product - Not Found")

    def test_get_store_products(self):
        """Test GET /stores/{store_id}/products endpoint"""
        print("\n📦 Testing Get Store Products")
        print("=" * 50)
        
        # Test get products by store
        result = self.test_endpoint("GET", f"/stores/{self.test_data['store_id']}/products", expected_status=200, test_name="Get Store Products")
        if result:
            # Verify response structure
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'products' in body_data:
                        products = body_data['products']
                        print(f"  📊 Found {len(products)} products for store")
                        
                        # Test response structure
                        if products:
                            first_product = products[0]
                            required_fields = ['id', 'name', 'price', 'unit', 'stock', 'created_at']
                            missing_fields = [field for field in required_fields if field not in first_product]
                            if not missing_fields:
                                self.log_test("Store Products Structure", "PASS")
                                self.test_results["passed"] += 1
                            else:
                                self.log_test("Store Products Structure", "FAIL", f"Missing fields: {missing_fields}")
                                self.test_results["failed"] += 1
                    else:
                        self.log_test("Store Products Response", "FAIL", "Missing 'products' field in response")
                        self.test_results["failed"] += 1
                except json.JSONDecodeError:
                    self.log_test("Store Products JSON Parsing", "FAIL", "Invalid JSON in response body")
                    self.test_results["failed"] += 1
            else:
                # Direct response
                if isinstance(result, dict) and 'products' in result:
                    products = result['products']
                    print(f"  📊 Found {len(products)} products for store")
                else:
                    self.log_test("Store Products Response", "FAIL", "Unexpected response structure")
                    self.test_results["failed"] += 1

    def test_create_product(self):
        """Test POST /stores/{store_id}/products endpoint"""
        print("\n📦 Testing Create Product")
        print("=" * 50)
        
        # Test create product with valid data
        product_data = {
            "name": self.test_data["product_name"],
            "description": self.test_data["product_description"],
            "price": self.test_data["product_price"],
            "unit": self.test_data["product_unit"],
            "stock": self.test_data["product_stock"],
            "image_url": self.test_data["product_image_url"],
            "category_id": self.test_data["category_id"]
        }
        
        result = self.test_endpoint("POST", f"/stores/{self.test_data['store_id']}/products", product_data, 201, "Create Product - Success")
        if result:
            # Verify response structure
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'product' in body_data:
                        product = body_data['product']
                        print(f"  📦 Created product: {product.get('name', 'N/A')}")
                        print(f"  💰 Price: {product.get('price', 'N/A')}")
                        print(f"  📦 Stock: {product.get('stock', 'N/A')}")
                        
                        # Test response structure
                        required_fields = ['id', 'name', 'price', 'unit', 'stock', 'created_at']
                        missing_fields = [field for field in required_fields if field not in product]
                        if not missing_fields:
                            self.log_test("Create Product Response Structure", "PASS")
                            self.test_results["passed"] += 1
                        else:
                            self.log_test("Create Product Response Structure", "FAIL", f"Missing fields: {missing_fields}")
                            self.test_results["failed"] += 1
                    else:
                        self.log_test("Create Product Response", "FAIL", "Missing 'product' field in response")
                        self.test_results["failed"] += 1
                except json.JSONDecodeError:
                    self.log_test("Create Product JSON Parsing", "FAIL", "Invalid JSON in response body")
                    self.test_results["failed"] += 1
            else:
                # Direct response
                if isinstance(result, dict) and 'product' in result:
                    product = result['product']
                    print(f"  📦 Created product: {product.get('name', 'N/A')}")
                    print(f"  💰 Price: {product.get('price', 'N/A')}")
                    print(f"  📦 Stock: {product.get('stock', 'N/A')}")
                else:
                    self.log_test("Create Product Response", "FAIL", "Unexpected response structure")
                    self.test_results["failed"] += 1
        
        # Test create product with missing required fields
        incomplete_data = {"name": self.test_data["product_name"]}
        self.test_endpoint("POST", f"/stores/{self.test_data['store_id']}/products", incomplete_data, 400, "Create Product - Missing Required Fields")
        
        # Test create product with invalid price
        invalid_price_data = {
            "name": self.test_data["product_name"],
            "price": self.test_data["negative_price"]
        }
        self.test_endpoint("POST", f"/stores/{self.test_data['store_id']}/products", invalid_price_data, 400, "Create Product - Negative Price")
        
        # Test create product with invalid stock
        invalid_stock_data = {
            "name": self.test_data["product_name"],
            "price": self.test_data["product_price"],
            "stock": self.test_data["negative_stock"]
        }
        self.test_endpoint("POST", f"/stores/{self.test_data['store_id']}/products", invalid_stock_data, 400, "Create Product - Negative Stock")

    def test_update_product(self):
        """Test PUT /products/{id} endpoint"""
        print("\n📦 Testing Update Product")
        print("=" * 50)
        
        # First create a product to update
        product_data = {
            "name": f"Product to Update {int(time.time())}",
            "description": "Original description",
            "price": 25.50,
            "unit": "piece",
            "stock": 50
        }
        
        create_result = self.test_endpoint("POST", f"/stores/{self.test_data['store_id']}/products", product_data, 201, "Create Product for Update")
        if create_result:
            product_id = None
            if isinstance(create_result, dict) and 'body' in create_result:
                try:
                    body_data = json.loads(create_result['body'])
                    if 'product' in body_data:
                        product_id = body_data['product']['id']
                except json.JSONDecodeError:
                    pass
            elif isinstance(create_result, dict) and 'product' in create_result:
                product_id = create_result['product']['id']
            
            if product_id:
                # Test update product
                update_data = {
                    "name": "Updated Product Name",
                    "description": "Updated description",
                    "price": 35.75,
                    "stock": 75
                }
                
                result = self.test_endpoint("PUT", f"/products/{product_id}", update_data, 200, "Update Product - Success")
                if result:
                    # Verify response structure
                    if isinstance(result, dict) and 'body' in result:
                        try:
                            body_data = json.loads(result['body'])
                            if 'product' in body_data:
                                product = body_data['product']
                                print(f"  📦 Updated product: {product.get('name', 'N/A')}")
                                print(f"  💰 New price: {product.get('price', 'N/A')}")
                                print(f"  📦 New stock: {product.get('stock', 'N/A')}")
                                
                                # Test response structure
                                required_fields = ['id', 'name', 'price', 'unit', 'stock', 'updated_at']
                                missing_fields = [field for field in required_fields if field not in product]
                                if not missing_fields:
                                    self.log_test("Update Product Response Structure", "PASS")
                                    self.test_results["passed"] += 1
                                else:
                                    self.log_test("Update Product Response Structure", "FAIL", f"Missing fields: {missing_fields}")
                                    self.test_results["failed"] += 1
                            else:
                                self.log_test("Update Product Response", "FAIL", "Missing 'product' field in response")
                                self.test_results["failed"] += 1
                        except json.JSONDecodeError:
                            self.log_test("Update Product JSON Parsing", "FAIL", "Invalid JSON in response body")
                            self.test_results["failed"] += 1
                    else:
                        # Direct response
                        if isinstance(result, dict) and 'product' in result:
                            product = result['product']
                            print(f"  📦 Updated product: {product.get('name', 'N/A')}")
                            print(f"  💰 New price: {product.get('price', 'N/A')}")
                            print(f"  📦 New stock: {product.get('stock', 'N/A')}")
                        else:
                            self.log_test("Update Product Response", "FAIL", "Unexpected response structure")
                            self.test_results["failed"] += 1
        
        # Test update non-existent product
        self.test_endpoint("PUT", f"/products/{self.test_data['invalid_product_id']}", {"name": "Test"}, 404, "Update Product - Not Found")

    def test_delete_product(self):
        """Test DELETE /products/{id} endpoint"""
        print("\n📦 Testing Delete Product")
        print("=" * 50)
        
        # First create a product to delete
        product_data = {
            "name": f"Product to Delete {int(time.time())}",
            "description": "Delete description",
            "price": 15.25,
            "unit": "piece",
            "stock": 25
        }
        
        create_result = self.test_endpoint("POST", f"/stores/{self.test_data['store_id']}/products", product_data, 201, "Create Product for Delete")
        if create_result:
            product_id = None
            if isinstance(create_result, dict) and 'body' in create_result:
                try:
                    body_data = json.loads(create_result['body'])
                    if 'product' in body_data:
                        product_id = body_data['product']['id']
                except json.JSONDecodeError:
                    pass
            elif isinstance(create_result, dict) and 'product' in create_result:
                product_id = create_result['product']['id']
            
            if product_id:
                # Test delete product
                result = self.test_endpoint("DELETE", f"/products/{product_id}", expected_status=204, test_name="Delete Product - Success")
                if result is not None:  # DELETE should return 204 with no content
                    self.log_test("Delete Product Response", "PASS")
                    self.test_results["passed"] += 1
        
        # Test delete non-existent product
        self.test_endpoint("DELETE", f"/products/{self.test_data['invalid_product_id']}", expected_status=404, test_name="Delete Product - Not Found")

    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n📦 Testing Error Handling")
        print("=" * 50)
        
        # Test invalid HTTP methods
        self.test_endpoint("PUT", "/products", {}, 405, "Invalid Method - PUT /products")
        self.test_endpoint("DELETE", "/products", {}, 405, "Invalid Method - DELETE /products")
        
        # Test malformed JSON
        headers = {"Content-Type": "application/json"}
        try:
            response = self.session.post(f"{BASE_URL}/stores/{self.test_data['store_id']}/products", data="invalid json", headers=headers)
            if response.status_code == 400:
                self.log_test("Malformed JSON - Create Product", "PASS")
                self.test_results["passed"] += 1
            else:
                self.log_test("Malformed JSON - Create Product", "FAIL", f"Expected 400, got {response.status_code}")
                self.test_results["failed"] += 1
        except Exception as e:
            self.log_test("Malformed JSON - Create Product", "FAIL", f"Exception: {str(e)}")
            self.test_results["failed"] += 1

    def test_cors_headers(self):
        """Test CORS headers"""
        print("\n📦 Testing CORS Headers")
        print("=" * 50)
        
        # Test OPTIONS request
        try:
            response = self.session.options(f"{BASE_URL}/products")
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
        """Run all products integration tests"""
        print("🚀 Starting Products Integration Tests")
        print("=" * 60)
        print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 API Base URL: {BASE_URL}")
        print(f"👤 Mock Store ID: {self.test_data['store_id']}")
        print("=" * 60)
        
        try:
            # Run all test methods
            self.test_get_products()
            self.test_get_specific_product()
            self.test_get_store_products()
            self.test_create_product()
            self.test_update_product()
            self.test_delete_product()
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
        print("📊 PRODUCTS INTEGRATION TEST SUMMARY")
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
    """Main function to run products integration tests"""
    test = ProductsIntegrationTest()
    test.run_all_tests()

if __name__ == "__main__":
    main() 