#!/usr/bin/env python3
"""
Comprehensive Authentication Endpoints Tests
Tests all auth endpoints including registration, login, and token validation.
"""

import requests
import json
import time
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AuthEndpointsTest:
    def __init__(self):
        from env_config import get_base_url
        self.base_url = get_base_url()
        self.auth_token = None
        self.user_data = None
        self.test_phone = "+919502528182"
        self.test_otp = "123456"
        
    def print_step(self, step, description):
        print(f"\n{'='*60}")
        print(f"STEP {step}: {description}")
        print(f"{'='*60}")
    
    def print_success(self, message):
        print(f"✅ {message}")
    
    def print_error(self, message):
        print(f"❌ {message}")
    
    def print_info(self, message):
        print(f"ℹ️  {message}")
    
    def test_otp_send_endpoint(self):
        """Test OTP send endpoint"""
        self.print_step(1, "Test OTP Send Endpoint")
        
        test_cases = [
            {
                "name": "Valid phone number",
                "payload": {"phone": self.test_phone},
                "expected_status": 200
            },
            {
                "name": "Invalid phone format",
                "payload": {"phone": "1234567890"},
                "expected_status": 400
            },
            {
                "name": "Missing phone",
                "payload": {},
                "expected_status": 400
            },
            {
                "name": "Empty phone",
                "payload": {"phone": ""},
                "expected_status": 400
            }
        ]
        
        for test_case in test_cases:
            try:
                self.print_info(f"Testing: {test_case['name']}")
                url = f"{self.base_url}/auth/otp/send"
                response = requests.post(url, json=test_case['payload'])
                
                if response.status_code == test_case['expected_status']:
                    self.print_success(f"{test_case['name']}: Status {response.status_code}")
                else:
                    self.print_error(f"{test_case['name']}: Expected {test_case['expected_status']}, got {response.status_code}")
                    return False
                    
            except Exception as e:
                self.print_error(f"{test_case['name']}: Error - {str(e)}")
                return False
        
        self.print_success("All OTP send tests passed")
        return True
    
    def test_otp_verify_endpoint(self):
        """Test OTP verify endpoint"""
        self.print_step(2, "Test OTP Verify Endpoint")
        
        test_cases = [
            {
                "name": "Valid OTP",
                "payload": {"phone": self.test_phone, "otp": self.test_otp},
                "expected_status": 200,
                "should_have_token": True
            },
            {
                "name": "Invalid OTP",
                "payload": {"phone": self.test_phone, "otp": "999999"},
                "expected_status": 400,
                "should_have_token": False
            },
            {
                "name": "Wrong phone number",
                "payload": {"phone": "+919876543210", "otp": self.test_otp},
                "expected_status": 400,
                "should_have_token": False
            },
            {
                "name": "Missing OTP",
                "payload": {"phone": self.test_phone},
                "expected_status": 400,
                "should_have_token": False
            },
            {
                "name": "Missing phone",
                "payload": {"otp": self.test_otp},
                "expected_status": 400,
                "should_have_token": False
            }
        ]
        
        for test_case in test_cases:
            try:
                self.print_info(f"Testing: {test_case['name']}")
                url = f"{self.base_url}/auth/otp/verify"
                response = requests.post(url, json=test_case['payload'])
                
                if response.status_code == test_case['expected_status']:
                    self.print_success(f"{test_case['name']}: Status {response.status_code}")
                    
                    if test_case['should_have_token']:
                        data = response.json()
                        if 'token' in data:
                            self.auth_token = data['token']
                            self.user_data = data.get('user', {})
                            self.print_success(f"{test_case['name']}: Token received")
                        else:
                            self.print_error(f"{test_case['name']}: No token in response")
                            return False
                else:
                    self.print_error(f"{test_case['name']}: Expected {test_case['expected_status']}, got {response.status_code}")
                    return False
                    
            except Exception as e:
                self.print_error(f"{test_case['name']}: Error - {str(e)}")
                return False
        
        self.print_success("All OTP verify tests passed")
        return True
    
    def test_registration_endpoint(self):
        """Test user registration endpoint"""
        self.print_step(3, "Test Registration Endpoint")
        
        test_cases = [
            {
                "name": "Valid registration",
                "payload": {
                    "name": "Test User",
                    "phone": "+919876543210",
                    "email": "test@example.com"
                },
                "expected_status": 200,
                "should_have_token": True
            },
            {
                "name": "Missing name",
                "payload": {
                    "phone": "+919876543210",
                    "email": "test@example.com"
                },
                "expected_status": 400,
                "should_have_token": False
            },
            {
                "name": "Missing phone",
                "payload": {
                    "name": "Test User",
                    "email": "test@example.com"
                },
                "expected_status": 400,
                "should_have_token": False
            },
            {
                "name": "Invalid email",
                "payload": {
                    "name": "Test User",
                    "phone": "+919876543210",
                    "email": "invalid-email"
                },
                "expected_status": 400,
                "should_have_token": False
            }
        ]
        
        for test_case in test_cases:
            try:
                self.print_info(f"Testing: {test_case['name']}")
                url = f"{self.base_url}/auth/register"
                response = requests.post(url, json=test_case['payload'])
                
                if response.status_code == test_case['expected_status']:
                    self.print_success(f"{test_case['name']}: Status {response.status_code}")
                    
                    if test_case['should_have_token']:
                        data = response.json()
                        if 'token' in data:
                            self.print_success(f"{test_case['name']}: Token received")
                        else:
                            self.print_error(f"{test_case['name']}: No token in response")
                            return False
                else:
                    self.print_error(f"{test_case['name']}: Expected {test_case['expected_status']}, got {response.status_code}")
                    return False
                    
            except Exception as e:
                self.print_error(f"{test_case['name']}: Error - {str(e)}")
                return False
        
        self.print_success("All registration tests passed")
        return True
    
    def test_login_endpoint(self):
        """Test user login endpoint"""
        self.print_step(4, "Test Login Endpoint")
        
        test_cases = [
            {
                "name": "Valid login",
                "payload": {
                    "phone": self.test_phone,
                    "password": "testpassword123"
                },
                "expected_status": 200,
                "should_have_token": True
            },
            {
                "name": "Invalid password",
                "payload": {
                    "phone": self.test_phone,
                    "password": "wrongpassword"
                },
                "expected_status": 401,
                "should_have_token": False
            },
            {
                "name": "Non-existent user",
                "payload": {
                    "phone": "+919876543210",
                    "password": "testpassword123"
                },
                "expected_status": 404,
                "should_have_token": False
            },
            {
                "name": "Missing password",
                "payload": {
                    "phone": self.test_phone
                },
                "expected_status": 400,
                "should_have_token": False
            }
        ]
        
        for test_case in test_cases:
            try:
                self.print_info(f"Testing: {test_case['name']}")
                url = f"{self.base_url}/auth/login"
                response = requests.post(url, json=test_case['payload'])
                
                if response.status_code == test_case['expected_status']:
                    self.print_success(f"{test_case['name']}: Status {response.status_code}")
                    
                    if test_case['should_have_token']:
                        data = response.json()
                        if 'token' in data:
                            self.print_success(f"{test_case['name']}: Token received")
                        else:
                            self.print_error(f"{test_case['name']}: No token in response")
                            return False
                else:
                    self.print_error(f"{test_case['name']}: Expected {test_case['expected_status']}, got {response.status_code}")
                    return False
                    
            except Exception as e:
                self.print_error(f"{test_case['name']}: Error - {str(e)}")
                return False
        
        self.print_success("All login tests passed")
        return True
    
    def test_token_validation(self):
        """Test token validation on protected endpoints"""
        self.print_step(5, "Test Token Validation")
        
        if not self.auth_token:
            self.print_error("No auth token available for testing")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test protected endpoints
        endpoints = [
            ("GET /profile", f"{self.base_url}/profile", "GET"),
            ("PUT /profile", f"{self.base_url}/profile", "PUT"),
            ("GET /cart", f"{self.base_url}/cart", "GET"),
            ("POST /cart/items", f"{self.base_url}/cart/items", "POST"),
            ("GET /orders", f"{self.base_url}/orders", "GET"),
            ("POST /orders", f"{self.base_url}/orders", "POST"),
            ("GET /stores/owner", f"{self.base_url}/stores/owner", "GET"),
            ("POST /stores", f"{self.base_url}/stores", "POST")
        ]
        
        for endpoint_name, url, method in endpoints:
            try:
                self.print_info(f"Testing {endpoint_name}...")
                
                if method == "GET":
                    response = requests.get(url, headers=headers)
                elif method == "POST":
                    response = requests.post(url, headers=headers, json={})
                elif method == "PUT":
                    response = requests.put(url, headers=headers, json={})
                
                if response.status_code in [200, 201]:
                    self.print_success(f"{endpoint_name} - Success")
                elif response.status_code == 401:
                    self.print_error(f"{endpoint_name} - Unauthorized")
                    return False
                else:
                    self.print_info(f"{endpoint_name} - Status: {response.status_code}")
                
            except Exception as e:
                self.print_error(f"{endpoint_name} - Error: {str(e)}")
                return False
        
        self.print_success("All protected endpoints validate tokens correctly")
        return True
    
    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints"""
        self.print_step(6, "Test Unauthorized Access")
        
        # Test without token
        endpoints = [
            ("GET /profile", f"{self.base_url}/profile", "GET"),
            ("GET /cart", f"{self.base_url}/cart", "GET"),
            ("GET /orders", f"{self.base_url}/orders", "GET"),
            ("GET /stores/owner", f"{self.base_url}/stores/owner", "GET")
        ]
        
        for endpoint_name, url, method in endpoints:
            try:
                self.print_info(f"Testing {endpoint_name} without token...")
                
                if method == "GET":
                    response = requests.get(url)
                else:
                    response = requests.post(url)
                
                if response.status_code == 401:
                    self.print_success(f"{endpoint_name} - Correctly rejected")
                else:
                    self.print_error(f"{endpoint_name} - Not rejected (status: {response.status_code})")
                    return False
                
            except Exception as e:
                self.print_error(f"{endpoint_name} - Error: {str(e)}")
                return False
        
        self.print_success("All unauthorized access correctly rejected")
        return True
    
    def run_all_tests(self):
        """Run all authentication endpoint tests"""
        print("🚀 Starting Comprehensive Authentication Endpoints Tests")
        print("=" * 60)
        
        tests = [
            ("OTP Send Endpoint", self.test_otp_send_endpoint),
            ("OTP Verify Endpoint", self.test_otp_verify_endpoint),
            ("Registration Endpoint", self.test_registration_endpoint),
            ("Login Endpoint", self.test_login_endpoint),
            ("Token Validation", self.test_token_validation),
            ("Unauthorized Access", self.test_unauthorized_access)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    self.print_error(f"Test '{test_name}' failed")
            except Exception as e:
                self.print_error(f"Test '{test_name}' failed with exception: {str(e)}")
        
        print(f"\n{'='*60}")
        print(f"TEST RESULTS: {passed}/{total} tests passed")
        print(f"{'='*60}")
        
        if passed == total:
            self.print_success("🎉 ALL AUTHENTICATION TESTS PASSED!")
            return True
        else:
            self.print_error(f"❌ {total - passed} tests failed")
            return False

def main():
    """Main test runner"""
    print("🧪 Comprehensive Authentication Endpoints Tests")
    print("=" * 60)
    
    test = AuthEndpointsTest()
    success = test.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main() 