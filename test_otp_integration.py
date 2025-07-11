#!/usr/bin/env python3
"""
OTP Authentication Integration Tests for Anna Akka Platform

This module contains comprehensive integration tests for OTP authentication endpoints:
- Send OTP for login
- Verify OTP for login
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

class OTPIntegrationTest:
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
            "valid_phone": f"+91 98765 {random.randint(10000, 99999)}",
            "invalid_phone": "invalid-phone",
            "non_existent_phone": f"+91 99999 {random.randint(10000, 99999)}",
            "short_phone": "+91 123",
            "empty_phone": "",
            "valid_otp": "123456",
            "invalid_otp": "000000",
            "short_otp": "123",
            "empty_otp": ""
        }

    def test_endpoint(self, method, endpoint, data=None, expected_status=200, test_name="Test"):
        """Test an endpoint and return the response"""
        try:
            url = f"{BASE_URL}{endpoint}"
            print(f"Testing: {test_name}")
            print(f"URL: {url}")
            print(f"Method: {method}")
            if data:
                print(f"Data: {json.dumps(data, indent=2)}")
            
            if method == "GET":
                response = self.session.get(url, params=data)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PUT":
                response = self.session.put(url, json=data)
            elif method == "DELETE":
                response = self.session.delete(url, json=data)
            else:
                print(f"❌ Unsupported method: {method}")
                self.test_results["failed"] += 1
                return None
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == expected_status:
                print(f"✅ PASS: {test_name}")
                self.test_results["passed"] += 1
                try:
                    return response.json()
                except:
                    return {"message": response.text}
            else:
                print(f"❌ FAIL: {test_name} - Expected {expected_status}, got {response.status_code}")
                self.test_results["failed"] += 1
                return None
                
        except Exception as e:
            print(f"❌ ERROR: {test_name} - {str(e)}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {str(e)}")
            return None

    def run_all_tests(self):
        """Run all OTP integration tests"""
        print("🚀 Starting OTP Authentication Integration Tests")
        print("=" * 60)
        
        self.test_send_otp()
        self.test_verify_otp()
        self.test_error_scenarios()
        
        self.print_results()

    def test_send_otp(self):
        """Test OTP send functionality"""
        print("\n📱 Testing OTP Send Functionality")
        print("=" * 50)
        
        # Test successful OTP send (requires existing user)
        # Note: This will fail if user doesn't exist in DynamoDB
        send_data = {"phone": self.test_data["valid_phone"]}
        result = self.test_endpoint("POST", "/auth/otp/send", send_data, 200, "Send OTP - Valid Phone")
        
        # Test invalid phone format
        send_data = {"phone": self.test_data["invalid_phone"]}
        self.test_endpoint("POST", "/auth/otp/send", send_data, 400, "Send OTP - Invalid Phone Format")
        
        # Test short phone number
        send_data = {"phone": self.test_data["short_phone"]}
        self.test_endpoint("POST", "/auth/otp/send", send_data, 400, "Send OTP - Short Phone")
        
        # Test empty phone
        send_data = {"phone": self.test_data["empty_phone"]}
        self.test_endpoint("POST", "/auth/otp/send", send_data, 400, "Send OTP - Empty Phone")
        
        # Test missing phone field
        send_data = {}
        self.test_endpoint("POST", "/auth/otp/send", send_data, 400, "Send OTP - Missing Phone")
        
        # Test non-existent user (will fail if user exists)
        send_data = {"phone": self.test_data["non_existent_phone"]}
        self.test_endpoint("POST", "/auth/otp/send", send_data, 404, "Send OTP - Non-existent User")

    def test_verify_otp(self):
        """Test OTP verification functionality"""
        print("\n🔐 Testing OTP Verification Functionality")
        print("=" * 50)
        
        # Test successful OTP verification (requires valid OTP)
        verify_data = {
            "phone": self.test_data["valid_phone"],
            "otp": self.test_data["valid_otp"]
        }
        result = self.test_endpoint("POST", "/auth/otp/verify", verify_data, 200, "Verify OTP - Valid Credentials")
        
        # Test invalid OTP
        verify_data = {
            "phone": self.test_data["valid_phone"],
            "otp": self.test_data["invalid_otp"]
        }
        self.test_endpoint("POST", "/auth/otp/verify", verify_data, 400, "Verify OTP - Invalid OTP")
        
        # Test short OTP
        verify_data = {
            "phone": self.test_data["valid_phone"],
            "otp": self.test_data["short_otp"]
        }
        self.test_endpoint("POST", "/auth/otp/verify", verify_data, 400, "Verify OTP - Short OTP")
        
        # Test empty OTP
        verify_data = {
            "phone": self.test_data["valid_phone"],
            "otp": self.test_data["empty_otp"]
        }
        self.test_endpoint("POST", "/auth/otp/verify", verify_data, 400, "Verify OTP - Empty OTP")
        
        # Test missing OTP field
        verify_data = {"phone": self.test_data["valid_phone"]}
        self.test_endpoint("POST", "/auth/otp/verify", verify_data, 400, "Verify OTP - Missing OTP")
        
        # Test missing phone field
        verify_data = {"otp": self.test_data["valid_otp"]}
        self.test_endpoint("POST", "/auth/otp/verify", verify_data, 400, "Verify OTP - Missing Phone")
        
        # Test non-existent user
        verify_data = {
            "phone": self.test_data["non_existent_phone"],
            "otp": self.test_data["valid_otp"]
        }
        self.test_endpoint("POST", "/auth/otp/verify", verify_data, 404, "Verify OTP - Non-existent User")

    def test_error_scenarios(self):
        """Test various error scenarios"""
        print("\n⚠️ Testing Error Scenarios")
        print("=" * 50)
        
        # Test invalid HTTP methods
        self.test_endpoint("GET", "/auth/otp/send", {}, 405, "Send OTP - GET Method")
        self.test_endpoint("PUT", "/auth/otp/send", {}, 405, "Send OTP - PUT Method")
        self.test_endpoint("DELETE", "/auth/otp/send", {}, 405, "Send OTP - DELETE Method")
        
        self.test_endpoint("GET", "/auth/otp/verify", {}, 405, "Verify OTP - GET Method")
        self.test_endpoint("PUT", "/auth/otp/verify", {}, 405, "Verify OTP - PUT Method")
        self.test_endpoint("DELETE", "/auth/otp/verify", {}, 405, "Verify OTP - DELETE Method")
        
        # Test non-existent endpoints
        self.test_endpoint("POST", "/auth/otp/nonexistent", {}, 404, "Non-existent Endpoint")
        self.test_endpoint("POST", "/auth/otp", {}, 404, "Invalid OTP Endpoint")

    def print_results(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 OTP Authentication Test Results")
        print("=" * 60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results["errors"]:
            print("\n🚨 Errors:")
            for error in self.test_results["errors"]:
                print(f"  - {error}")
        
        print("\n" + "=" * 60)

def main():
    """Main function to run OTP integration tests"""
    test = OTPIntegrationTest()
    test.run_all_tests()

if __name__ == "__main__":
    main() 