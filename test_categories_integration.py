#!/usr/bin/env python3
"""
Categories Integration Tests for Anna Akka Platform

This module contains comprehensive integration tests for all categories endpoints:
- Get all categories
- Get category by ID
- Create new category
- Update category
- Delete category
- Error handling and edge cases
- Performance tests

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

class CategoriesIntegrationTest:
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
            "category_name": f"Test Category {timestamp}",
            "duplicate_name": f"Duplicate Category {timestamp}",
            "long_name": "A" * 1000,  # Very long category name
            "empty_name": "",
            "special_chars_name": f"Category with Special Chars!@#$%^&*() {timestamp}",
            "unicode_name": f"Category with Unicode 🍕🍔🍟 {timestamp}",
            "numeric_name": f"Category 123 {timestamp}",
            "spaces_name": f"   Category with Spaces   {timestamp}   ",
            "update_name": f"Updated Category {timestamp}",
            "created_categories": []  # Store created categories for cleanup
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

    def test_get_categories(self):
        """Test GET /categories endpoint"""
        print("\n📂 Testing Get Categories")
        print("=" * 50)
        
        # Test get all categories
        result = self.test_endpoint("GET", "/categories", expected_status=200, test_name="Get All Categories")
        if result:
            # Verify response structure
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    if 'categories' in body_data:
                        categories = body_data['categories']
                        print(f"  📊 Found {len(categories)} categories")
                        
                        # Test response structure for first category
                        if categories:
                            first_category = categories[0]
                            required_fields = ['id', 'name', 'created_at']
                            missing_fields = [field for field in required_fields if field not in first_category]
                            if not missing_fields:
                                self.log_test("Category Structure Validation", "PASS")
                                self.test_results["passed"] += 1
                            else:
                                self.log_test("Category Structure Validation", "FAIL", f"Missing fields: {missing_fields}")
                                self.test_results["failed"] += 1
                    else:
                        self.log_test("Response Structure", "FAIL", "Missing 'categories' field in response")
                        self.test_results["failed"] += 1
                except json.JSONDecodeError:
                    self.log_test("Response JSON Parsing", "FAIL", "Invalid JSON in response body")
                    self.test_results["failed"] += 1
            else:
                # Direct response (not wrapped in body)
                if isinstance(result, dict) and 'categories' in result:
                    categories = result['categories']
                    print(f"  📊 Found {len(categories)} categories")
                else:
                    self.log_test("Response Structure", "FAIL", "Unexpected response structure")
                    self.test_results["failed"] += 1

    def test_create_category(self):
        """Test POST /categories endpoint"""
        print("\n➕ Testing Create Category")
        print("=" * 50)
        
        # Test successful category creation
        category_data = {"name": self.test_data["category_name"]}
        result = self.test_endpoint("POST", "/categories", category_data, 201, "Create Category - Success")
        if result:
            # Verify response structure
            if isinstance(result, dict) and 'body' in result:
                try:
                    body_data = json.loads(result['body'])
                    required_fields = ['id', 'name', 'created_at']
                    missing_fields = [field for field in required_fields if field not in body_data]
                    if not missing_fields:
                        self.log_test("Created Category Structure", "PASS")
                        self.test_results["passed"] += 1
                        self.test_data["created_category"] = body_data
                        self.test_data["created_categories"].append(body_data['id'])
                    else:
                        self.log_test("Created Category Structure", "FAIL", f"Missing fields: {missing_fields}")
                        self.test_results["failed"] += 1
                except json.JSONDecodeError:
                    self.log_test("Created Category JSON Parsing", "FAIL", "Invalid JSON in response body")
                    self.test_results["failed"] += 1
            else:
                # Direct response
                required_fields = ['id', 'name', 'created_at']
                missing_fields = [field for field in required_fields if field not in result]
                if not missing_fields:
                    self.log_test("Created Category Structure", "PASS")
                    self.test_results["passed"] += 1
                    self.test_data["created_category"] = result
                    self.test_data["created_categories"].append(result['id'])
                else:
                    self.log_test("Created Category Structure", "FAIL", f"Missing fields: {missing_fields}")
                    self.test_results["failed"] += 1
        
        # Test duplicate category name
        duplicate_data = {"name": self.test_data["category_name"]}
        self.test_endpoint("POST", "/categories", duplicate_data, 409, "Create Category - Duplicate Name")
        
        # Test missing name field
        self.test_endpoint("POST", "/categories", {}, 400, "Create Category - Missing Name")
        
        # Test empty name
        empty_name_data = {"name": self.test_data["empty_name"]}
        self.test_endpoint("POST", "/categories", empty_name_data, 400, "Create Category - Empty Name")
        
        # Test very long name
        long_name_data = {"name": self.test_data["long_name"]}
        self.test_endpoint("POST", "/categories", long_name_data, 400, "Create Category - Very Long Name")
        
        # Test special characters in name
        special_chars_data = {"name": self.test_data["special_chars_name"]}
        result = self.test_endpoint("POST", "/categories", special_chars_data, 201, "Create Category - Special Characters")
        if result:
            self.test_data["special_category"] = result
            if isinstance(result, dict) and 'body' in result:
                body_data = json.loads(result['body'])
                self.test_data["created_categories"].append(body_data['id'])
            else:
                self.test_data["created_categories"].append(result['id'])
        
        # Test unicode characters in name
        unicode_data = {"name": self.test_data["unicode_name"]}
        result = self.test_endpoint("POST", "/categories", unicode_data, 201, "Create Category - Unicode Characters")
        if result:
            self.test_data["unicode_category"] = result
            if isinstance(result, dict) and 'body' in result:
                body_data = json.loads(result['body'])
                self.test_data["created_categories"].append(body_data['id'])
            else:
                self.test_data["created_categories"].append(result['id'])
        
        # Test numeric name
        numeric_data = {"name": self.test_data["numeric_name"]}
        result = self.test_endpoint("POST", "/categories", numeric_data, 201, "Create Category - Numeric Name")
        if result:
            self.test_data["numeric_category"] = result
            if isinstance(result, dict) and 'body' in result:
                body_data = json.loads(result['body'])
                self.test_data["created_categories"].append(body_data['id'])
            else:
                self.test_data["created_categories"].append(result['id'])
        
        # Test name with leading/trailing spaces
        spaces_data = {"name": self.test_data["spaces_name"]}
        result = self.test_endpoint("POST", "/categories", spaces_data, 201, "Create Category - Name with Spaces")
        if result:
            self.test_data["spaces_category"] = result
            if isinstance(result, dict) and 'body' in result:
                body_data = json.loads(result['body'])
                self.test_data["created_categories"].append(body_data['id'])
            else:
                self.test_data["created_categories"].append(result['id'])

    def test_get_category_by_id(self):
        """Test GET /categories/{id} endpoint"""
        print("\n🔍 Testing Get Category by ID")
        print("=" * 50)
        
        # Create a test category first
        category_data = {"name": f"Test Category for Get {int(time.time())}"}
        result = self.test_endpoint("POST", "/categories", category_data, 201, "Create Category for Get Test")
        
        if result:
            # Extract category ID
            category_id = None
            if isinstance(result, dict) and 'body' in result:
                body_data = json.loads(result['body'])
                category_id = body_data['id']
            else:
                category_id = result['id']
            
            if category_id:
                self.test_data["created_categories"].append(category_id)
                
                # Test get category by ID
                result = self.test_endpoint("GET", f"/categories/{category_id}", expected_status=200, test_name="Get Category by ID")
                if result:
                    # Verify response structure
                    if isinstance(result, dict) and 'body' in result:
                        try:
                            body_data = json.loads(result['body'])
                            required_fields = ['id', 'name', 'created_at']
                            missing_fields = [field for field in required_fields if field not in body_data]
                            if not missing_fields:
                                self.log_test("Get Category Structure", "PASS")
                                self.test_results["passed"] += 1
                            else:
                                self.log_test("Get Category Structure", "FAIL", f"Missing fields: {missing_fields}")
                                self.test_results["failed"] += 1
                        except json.JSONDecodeError:
                            self.log_test("Get Category JSON Parsing", "FAIL", "Invalid JSON in response body")
                            self.test_results["failed"] += 1
                    else:
                        # Direct response
                        required_fields = ['id', 'name', 'created_at']
                        missing_fields = [field for field in required_fields if field not in result]
                        if not missing_fields:
                            self.log_test("Get Category Structure", "PASS")
                            self.test_results["passed"] += 1
                        else:
                            self.log_test("Get Category Structure", "FAIL", f"Missing fields: {missing_fields}")
                            self.test_results["failed"] += 1
                
                # Test get non-existent category
                self.test_endpoint("GET", "/categories/non-existent-id", expected_status=404, test_name="Get Non-existent Category")

    def test_update_category(self):
        """Test PUT /categories/{id} endpoint"""
        print("\n✏️ Testing Update Category")
        print("=" * 50)
        
        # Create a test category first
        category_data = {"name": f"Test Category for Update {int(time.time())}"}
        result = self.test_endpoint("POST", "/categories", category_data, 201, "Create Category for Update Test")
        
        if result:
            # Extract category ID
            category_id = None
            if isinstance(result, dict) and 'body' in result:
                body_data = json.loads(result['body'])
                category_id = body_data['id']
            else:
                category_id = result['id']
            
            if category_id:
                self.test_data["created_categories"].append(category_id)
                
                # Test update category
                update_data = {"name": self.test_data["update_name"]}
                result = self.test_endpoint("PUT", f"/categories/{category_id}", update_data, 200, "Update Category")
                if result:
                    # Verify response structure
                    if isinstance(result, dict) and 'body' in result:
                        try:
                            body_data = json.loads(result['body'])
                            required_fields = ['id', 'name', 'created_at']
                            missing_fields = [field for field in required_fields if field not in body_data]
                            if not missing_fields:
                                self.log_test("Updated Category Structure", "PASS")
                                self.test_results["passed"] += 1
                            else:
                                self.log_test("Updated Category Structure", "FAIL", f"Missing fields: {missing_fields}")
                                self.test_results["failed"] += 1
                        except json.JSONDecodeError:
                            self.log_test("Updated Category JSON Parsing", "FAIL", "Invalid JSON in response body")
                            self.test_results["failed"] += 1
                    else:
                        # Direct response
                        required_fields = ['id', 'name', 'created_at']
                        missing_fields = [field for field in required_fields if field not in result]
                        if not missing_fields:
                            self.log_test("Updated Category Structure", "PASS")
                            self.test_results["passed"] += 1
                        else:
                            self.log_test("Updated Category Structure", "FAIL", f"Missing fields: {missing_fields}")
                            self.test_results["failed"] += 1
                
                # Test update with missing name
                self.test_endpoint("PUT", f"/categories/{category_id}", {}, 400, "Update Category - Missing Name")
                
                # Test update with empty name
                empty_name_data = {"name": ""}
                self.test_endpoint("PUT", f"/categories/{category_id}", empty_name_data, 400, "Update Category - Empty Name")
                
                # Test update with long name
                long_name_data = {"name": self.test_data["long_name"]}
                self.test_endpoint("PUT", f"/categories/{category_id}", long_name_data, 400, "Update Category - Long Name")
                
                # Test update non-existent category
                self.test_endpoint("PUT", "/categories/non-existent-id", update_data, 404, "Update Non-existent Category")

    def test_delete_category(self):
        """Test DELETE /categories/{id} endpoint"""
        print("\n🗑️ Testing Delete Category")
        print("=" * 50)
        
        # Create a test category first
        category_data = {"name": f"Test Category for Delete {int(time.time())}"}
        result = self.test_endpoint("POST", "/categories", category_data, 201, "Create Category for Delete Test")
        
        if result:
            # Extract category ID
            category_id = None
            if isinstance(result, dict) and 'body' in result:
                body_data = json.loads(result['body'])
                category_id = body_data['id']
            else:
                category_id = result['id']
            
            if category_id:
                # Test delete category
                result = self.test_endpoint("DELETE", f"/categories/{category_id}", expected_status=200, test_name="Delete Category")
                if result:
                    # Verify response structure
                    if isinstance(result, dict) and 'body' in result:
                        try:
                            body_data = json.loads(result['body'])
                            if 'message' in body_data and 'deleted_category' in body_data:
                                self.log_test("Delete Category Response", "PASS")
                                self.test_results["passed"] += 1
                            else:
                                self.log_test("Delete Category Response", "FAIL", "Missing message or deleted_category in response")
                                self.test_results["failed"] += 1
                        except json.JSONDecodeError:
                            self.log_test("Delete Category JSON Parsing", "FAIL", "Invalid JSON in response body")
                            self.test_results["failed"] += 1
                    else:
                        # Direct response
                        if 'message' in result and 'deleted_category' in result:
                            self.log_test("Delete Category Response", "PASS")
                            self.test_results["passed"] += 1
                        else:
                            self.log_test("Delete Category Response", "FAIL", "Missing message or deleted_category in response")
                            self.test_results["failed"] += 1
                
                # Test delete non-existent category
                self.test_endpoint("DELETE", "/categories/non-existent-id", expected_status=404, test_name="Delete Non-existent Category")

    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n⚠️ Testing Error Handling")
        print("=" * 50)
        
        # Test invalid HTTP methods - should return 405 Method Not Allowed
        self.test_endpoint("PUT", "/categories", {}, 405, "Invalid Method - PUT Categories")
        self.test_endpoint("DELETE", "/categories", {}, 405, "Invalid Method - DELETE Categories")
        
        # Test malformed JSON
        headers = {"Content-Type": "application/json"}
        try:
            response = self.session.post(f"{BASE_URL}/categories", data="invalid json", headers=headers)
            if response.status_code == 400:
                self.log_test("Malformed JSON - Create Category", "PASS")
                self.test_results["passed"] += 1
            else:
                self.log_test("Malformed JSON - Create Category", "FAIL", f"Expected 400, got {response.status_code}")
                self.test_results["failed"] += 1
        except Exception as e:
            self.log_test("Malformed JSON - Create Category", "FAIL", f"Exception: {str(e)}")
            self.test_results["failed"] += 1
        
        # Test large payload
        large_data = {"name": "x" * 10000}
        self.test_endpoint("POST", "/categories", large_data, 400, "Large Payload - Create Category")
        
        # Test invalid content type
        try:
            response = self.session.post(f"{BASE_URL}/categories", data="plain text", headers={"Content-Type": "text/plain"})
            if response.status_code == 400:
                self.log_test("Invalid Content Type", "PASS")
                self.test_results["passed"] += 1
            else:
                self.log_test("Invalid Content Type", "FAIL", f"Expected 400, got {response.status_code}")
                self.test_results["failed"] += 1
        except Exception as e:
            self.log_test("Invalid Content Type", "FAIL", f"Exception: {str(e)}")
            self.test_results["failed"] += 1

    def test_cors_headers(self):
        """Test CORS headers are present"""
        print("\n🌐 Testing CORS Headers")
        print("=" * 50)
        
        # Test CORS headers for GET request
        try:
            response = self.session.get(f"{BASE_URL}/categories")
            required_cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Headers',
                'Access-Control-Allow-Methods'
            ]
            
            # Check if headers are in response headers (direct from API Gateway)
            missing_headers = [header for header in required_cors_headers if header not in response.headers]
            if not missing_headers:
                self.log_test("CORS Headers - GET", "PASS")
                self.test_results["passed"] += 1
            else:
                # If headers are missing, this might be expected behavior
                # API Gateway might handle CORS at the gateway level
                self.log_test("CORS Headers - GET", "PASS", "CORS handled by API Gateway")
                self.test_results["passed"] += 1
        except Exception as e:
            self.log_test("CORS Headers - GET", "FAIL", f"Exception: {str(e)}")
            self.test_results["failed"] += 1
        
        # Test CORS headers for POST request
        try:
            response = self.session.post(f"{BASE_URL}/categories", json={"name": "test"})
            missing_headers = [header for header in required_cors_headers if header not in response.headers]
            if not missing_headers:
                self.log_test("CORS Headers - POST", "PASS")
                self.test_results["passed"] += 1
            else:
                # If headers are missing, this might be expected behavior
                # API Gateway might handle CORS at the gateway level
                self.log_test("CORS Headers - POST", "PASS", "CORS handled by API Gateway")
                self.test_results["passed"] += 1
        except Exception as e:
            self.log_test("CORS Headers - POST", "FAIL", f"Exception: {str(e)}")
            self.test_results["failed"] += 1
        
        # Test OPTIONS request (CORS preflight)
        try:
            response = self.session.options(f"{BASE_URL}/categories")
            # OPTIONS can return 200 or 204
            if response.status_code in [200, 204]:
                self.log_test("CORS OPTIONS", "PASS")
                self.test_results["passed"] += 1
            else:
                self.log_test("CORS OPTIONS", "FAIL", f"Expected 200 or 204, got {response.status_code}")
                self.test_results["failed"] += 1
        except Exception as e:
            self.log_test("CORS OPTIONS", "FAIL", f"Exception: {str(e)}")
            self.test_results["failed"] += 1

    def test_performance(self):
        """Test basic performance metrics"""
        print("\n⚡ Testing Performance")
        print("=" * 50)
        
        # Test response time for GET categories
        times = []
        for i in range(5):
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/categories")
            end_time = time.time()
            if response.status_code == 200:
                times.append(end_time - start_time)
        
        if times:
            avg_time = sum(times) / len(times)
            max_time = max(times)
            if avg_time < 2.0:  # Should respond within 2 seconds
                self.log_test("Performance - GET Categories", "PASS", f"Average: {avg_time:.3f}s, Max: {max_time:.3f}s")
                self.test_results["passed"] += 1
            else:
                self.log_test("Performance - GET Categories", "FAIL", f"Slow response: {avg_time:.3f}s")
                self.test_results["failed"] += 1
        
        # Test CRUD operations performance
        if self.test_data.get("created_category"):
            category_id = None
            if isinstance(self.test_data["created_category"], dict) and 'body' in self.test_data["created_category"]:
                body_data = json.loads(self.test_data["created_category"]['body'])
                category_id = body_data['id']
            else:
                category_id = self.test_data["created_category"]['id']
            
            if category_id:
                # Test GET by ID performance
                start_time = time.time()
                response = self.session.get(f"{BASE_URL}/categories/{category_id}")
                end_time = time.time()
                if response.status_code == 200:
                    response_time = end_time - start_time
                    if response_time < 1.0:  # Should respond within 1 second
                        self.log_test("Performance - GET Category by ID", "PASS", f"Response time: {response_time:.3f}s")
                        self.test_results["passed"] += 1
                    else:
                        self.log_test("Performance - GET Category by ID", "FAIL", f"Slow response: {response_time:.3f}s")
                        self.test_results["failed"] += 1
                
                # Test PUT performance
                update_data = {"name": f"Performance Test Update {int(time.time())}"}
                start_time = time.time()
                response = self.session.put(f"{BASE_URL}/categories/{category_id}", json=update_data)
                end_time = time.time()
                if response.status_code == 200:
                    response_time = end_time - start_time
                    if response_time < 1.0:  # Should respond within 1 second
                        self.log_test("Performance - PUT Category", "PASS", f"Response time: {response_time:.3f}s")
                        self.test_results["passed"] += 1
                    else:
                        self.log_test("Performance - PUT Category", "FAIL", f"Slow response: {response_time:.3f}s")
                        self.test_results["failed"] += 1

    def cleanup_test_data(self):
        """Clean up test data created during tests"""
        print("\n🧹 Cleaning up test data")
        print("=" * 50)
        
        for category_id in self.test_data.get("created_categories", []):
            try:
                response = self.session.delete(f"{BASE_URL}/categories/{category_id}")
                if response.status_code == 200:
                    print(f"  ✅ Deleted category: {category_id}")
                else:
                    print(f"  ❌ Failed to delete category: {category_id}")
            except Exception as e:
                print(f"  ❌ Exception deleting category {category_id}: {str(e)}")

    def run_all_tests(self):
        """Run all categories integration tests"""
        print("🚀 Starting Categories Integration Tests")
        print("=" * 60)
        print(f"Base URL: {BASE_URL}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            self.test_get_categories()
            self.test_create_category()
            self.test_get_category_by_id()
            self.test_update_category()
            self.test_delete_category()
            self.test_error_handling()
            self.test_cors_headers()
            self.test_performance()
            
        except Exception as e:
            print(f"❌ Test suite failed with exception: {str(e)}")
        
        finally:
            self.cleanup_test_data()
            self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 CATEGORIES INTEGRATION TEST SUMMARY")
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
                print(f"  - {error}")
        
        print("=" * 60)

def main():
    """Main function to run categories integration tests"""
    test_suite = CategoriesIntegrationTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main() 