#!/usr/bin/env python3
"""
Auth Integration Tests for Anna Akka Platform

This module contains comprehensive integration tests for all authentication endpoints:
- User registration
- User login (multiple methods)
- Phone number validation
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

class AuthIntegrationTest:
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
            "firebase_uid": f"test-{timestamp}-{uuid.uuid4()}",
            "email": f"test-{timestamp}@example.com",
            "name": f"Test User {timestamp}",
            "phone": f"+91 98765 {random.randint(10000, 99999)}",
            "address": f"Test Address {timestamp}",
            "duplicate_firebase_uid": f"test-{timestamp}-{uuid.uuid4()}",
            "duplicate_email": f"duplicate-{timestamp}@example.com",
            "duplicate_phone": f"+91 98765 {random.randint(10000, 99999)}",
            "non_existent_uid": f"non-existent-{uuid.uuid4()}",
            "invalid_phone": "+91 99999 99999"
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

    def test_user_registration(self):
        """Test user registration endpoint"""
        print("\n📝 Testing User Registration")
        print("=" * 50)
        
        # Test successful registration
        user_data = {
            "firebase_uid": self.test_data["firebase_uid"],
            "email": self.test_data["email"],
            "name": self.test_data["name"],
            "phone": self.test_data["phone"],
            "address": self.test_data["address"],
            "roles": ["customer"]
        }
        
        result = self.test_endpoint("POST", "/auth/register", user_data, 201, "User Registration - Success")
        if result:
            self.test_data["registered_user"] = result.get("user")
        
        # Test duplicate Firebase UID
        duplicate_user = user_data.copy()
        duplicate_user["email"] = self.test_data["duplicate_email"]
        self.test_endpoint("POST", "/auth/register", duplicate_user, 409, "User Registration - Duplicate Firebase UID")
        
        # Test duplicate phone number
        duplicate_phone_user = user_data.copy()
        duplicate_phone_user["firebase_uid"] = self.test_data["duplicate_firebase_uid"]
        duplicate_phone_user["email"] = self.test_data["duplicate_email"]
        duplicate_phone_user["phone"] = self.test_data["phone"]  # Same phone as first user
        self.test_endpoint("POST", "/auth/register", duplicate_phone_user, 409, "User Registration - Duplicate Phone Number")
        
        # Test missing required fields
        incomplete_user = {}  # No firebase_uid
        self.test_endpoint("POST", "/auth/register", incomplete_user, 400, "User Registration - Missing Required Fields")
        
        # Test invalid email format
        invalid_email_user = user_data.copy()
        invalid_email_user["firebase_uid"] = f"test-{int(time.time())}-{uuid.uuid4()}"
        invalid_email_user["email"] = "invalid-email"
        invalid_email_user["phone"] = f"+91 98765 {random.randint(10000, 99999)}"  # Use unique phone
        self.test_endpoint("POST", "/auth/register", invalid_email_user, 400, "User Registration - Invalid Email")

    def test_user_login(self):
        """Test user login endpoint"""
        print("\n🔑 Testing User Login")
        print("=" * 50)
        
        # Test Firebase UID login
        login_data = {"firebase_uid": self.test_data["firebase_uid"]}
        result = self.test_endpoint("POST", "/auth/login", login_data, 200, "Login - Firebase UID")
        if result:
            self.test_data["auth_token"] = result.get("token")
        
        # Test phone number login
        login_data = {"phone": self.test_data["phone"]}
        self.test_endpoint("POST", "/auth/login", login_data, 200, "Login - Phone Number")
        
        # Test combined login (both firebase_uid and phone)
        login_data = {
            "firebase_uid": self.test_data["firebase_uid"],
            "phone": self.test_data["phone"]
        }
        self.test_endpoint("POST", "/auth/login", login_data, 200, "Login - Combined Credentials")
        
        # Test non-existent user
        login_data = {"firebase_uid": self.test_data["non_existent_uid"]}
        self.test_endpoint("POST", "/auth/login", login_data, 401, "Login - Non-existent User")
        
        # Test missing credentials
        self.test_endpoint("POST", "/auth/login", {}, 400, "Login - Missing Credentials")
        
        # Test invalid phone number
        login_data = {"phone": self.test_data["invalid_phone"]}
        self.test_endpoint("POST", "/auth/login", login_data, 401, "Login - Invalid Phone Number")

    def test_phone_validation(self):
        """Test phone number validation endpoint"""
        print("\n📱 Testing Phone Number Validation")
        print("=" * 50)
        
        # Test phone search for existing user
        self.test_endpoint("GET", f"/auth/user/phone?phone={self.test_data['phone']}", expected_status=200, test_name="Phone Search - Existing User")
        
        # Test phone search for non-existent user
        self.test_endpoint("GET", f"/auth/user/phone?phone={self.test_data['invalid_phone']}", expected_status=404, test_name="Phone Search - Non-existent User")
        
        # Test phone search without parameter
        self.test_endpoint("GET", "/auth/user/phone", expected_status=400, test_name="Phone Search - Missing Parameter")
        
        # Test phone search with empty parameter
        self.test_endpoint("GET", "/auth/user/phone?phone=", expected_status=400, test_name="Phone Search - Empty Parameter")
        
        # Test phone search with invalid phone format
        self.test_endpoint("GET", "/auth/user/phone?phone=invalid-phone", expected_status=400, test_name="Phone Search - Invalid Phone Format")

    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n⚠️ Testing Error Handling")
        print("=" * 50)
        
        # Test invalid HTTP method
        self.test_endpoint("PUT", "/auth/register", {}, 405, "Invalid Method - Register")
        self.test_endpoint("DELETE", "/auth/login", {}, 405, "Invalid Method - Login")
        
        # Test malformed JSON
        headers = {"Content-Type": "application/json"}
        try:
            response = self.session.post(f"{BASE_URL}/auth/register", data='{"invalid": json}', headers=headers)
            if response.status_code == 400:
                self.log_test("Malformed JSON - Register", "PASS")
                self.test_results["passed"] += 1
            else:
                self.log_test("Malformed JSON - Register", "FAIL", f"Expected 400, got {response.status_code}")
                self.test_results["failed"] += 1
        except Exception as e:
            self.log_test("Malformed JSON - Register", "FAIL", f"Exception: {str(e)}")
            self.test_results["failed"] += 1
        
        # Test large payload
        large_data = {"firebase_uid": "x" * (1024 * 1024 + 100)}  # Just over 1MB
        self.test_endpoint("POST", "/auth/register", large_data, 400, "Large Payload - Register")

    def run_all_tests(self):
        """Run all auth integration tests"""
        print("🚀 Starting Auth Integration Tests")
        print("=" * 60)
        print(f"Base URL: {BASE_URL}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            self.test_user_registration()
            self.test_user_login()
            self.test_phone_validation()
            self.test_error_handling()
            
        except Exception as e:
            print(f"❌ Test suite failed with exception: {str(e)}")
        
        finally:
            self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 AUTH INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        print("=" * 60)

def main():
    """Main function to run auth integration tests"""
    test_suite = AuthIntegrationTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main() 