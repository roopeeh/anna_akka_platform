#!/usr/bin/env python3
"""
Detailed Token Flow Tests
Tests the complete token generation, verification, and usage flow.
"""

import requests
import json
import time
import sys
import os
import hashlib

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TokenFlowTest:
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
    
    def test_token_generation(self):
        """Test token generation during OTP verification"""
        self.print_step(1, "Test Token Generation")
        
        try:
            # Step 1: Send OTP
            self.print_info("Sending OTP...")
            send_url = f"{self.base_url}/auth/otp/send"
            send_response = requests.post(send_url, json={"phone": self.test_phone})
            
            if send_response.status_code != 200:
                self.print_error(f"Failed to send OTP: {send_response.status_code}")
                return False
            
            self.print_success("OTP sent successfully")
            
            # Step 2: Verify OTP and get token
            self.print_info("Verifying OTP and getting token...")
            verify_url = f"{self.base_url}/auth/otp/verify"
            verify_response = requests.post(verify_url, json={
                "phone": self.test_phone,
                "otp": self.test_otp
            })
            
            if verify_response.status_code != 200:
                self.print_error(f"Failed to verify OTP: {verify_response.status_code}")
                return False
            
            data = verify_response.json()
            if 'token' not in data:
                self.print_error("No token in response")
                return False
            
            self.auth_token = data['token']
            self.user_data = data.get('user', {})
            
            self.print_success("Token generated successfully")
            self.print_info(f"Token: {self.auth_token}")
            self.print_info(f"User ID: {self.user_data.get('id', 'N/A')}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Token generation test failed: {str(e)}")
            return False
    
    def test_token_structure(self):
        """Test token structure and format"""
        self.print_step(2, "Test Token Structure")
        
        if not self.auth_token:
            self.print_error("No token available for testing")
            return False
        
        try:
            # Parse token parts
            parts = self.auth_token.split('.')
            
            if len(parts) != 4:
                self.print_error(f"Invalid token format. Expected 4 parts, got {len(parts)}")
                return False
            
            user_id, phone, expiry, signature = parts
            
            self.print_info(f"Token parts:")
            self.print_info(f"  User ID: {user_id}")
            self.print_info(f"  Phone: {phone}")
            self.print_info(f"  Expiry: {expiry}")
            self.print_info(f"  Signature: {signature}")
            
            # Validate expiry timestamp
            try:
                expiry_int = int(expiry)
                current_time = int(time.time())
                
                if expiry_int <= current_time:
                    self.print_error("Token is expired")
                    return False
                
                self.print_success("Token expiry is valid")
                
            except ValueError:
                self.print_error("Invalid expiry timestamp")
                return False
            
            # Validate phone number format
            if not phone.startswith('+'):
                self.print_error("Phone number should start with +")
                return False
            
            self.print_success("Token structure is valid")
            return True
            
        except Exception as e:
            self.print_error(f"Token structure test failed: {str(e)}")
            return False
    
    def test_token_verification(self):
        """Test token verification on protected endpoints"""
        self.print_step(3, "Test Token Verification")
        
        if not self.auth_token:
            self.print_error("No token available for testing")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test multiple protected endpoints
        endpoints = [
            ("GET /profile", f"{self.base_url}/profile", "GET"),
            ("GET /cart", f"{self.base_url}/cart", "GET"),
            ("GET /orders", f"{self.base_url}/orders", "GET"),
            ("GET /stores/owner", f"{self.base_url}/stores/owner", "GET")
        ]
        
        for endpoint_name, url, method in endpoints:
            try:
                self.print_info(f"Testing {endpoint_name}...")
                
                if method == "GET":
                    response = requests.get(url, headers=headers)
                else:
                    response = requests.post(url, headers=headers)
                
                if response.status_code == 200:
                    self.print_success(f"{endpoint_name} - Success")
                elif response.status_code == 401:
                    self.print_error(f"{endpoint_name} - Unauthorized")
                    return False
                else:
                    self.print_info(f"{endpoint_name} - Status: {response.status_code}")
                
            except Exception as e:
                self.print_error(f"{endpoint_name} - Error: {str(e)}")
                return False
        
        self.print_success("All protected endpoints accept valid token")
        return True
    
    def test_token_expiration(self):
        """Test token expiration handling"""
        self.print_step(4, "Test Token Expiration")
        
        try:
            # Create an expired token
            expired_token = "user123.+919876543210.1640995200.expired123"
            
            headers = {
                "Authorization": f"Bearer {expired_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/profile"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 401:
                self.print_success("Expired token correctly rejected")
                return True
            else:
                self.print_error(f"Expired token not rejected: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Token expiration test failed: {str(e)}")
            return False
    
    def test_invalid_tokens(self):
        """Test various invalid token scenarios"""
        self.print_step(5, "Test Invalid Tokens")
        
        invalid_tokens = [
            ("No token", {}),
            ("Empty token", {"Authorization": "Bearer "}),
            ("Invalid format", {"Authorization": "InvalidToken"}),
            ("Missing Bearer", {"Authorization": "user123.phone.1234567890.signature"}),
            ("Wrong parts", {"Authorization": "Bearer user123.phone"}),
            ("Invalid signature", {"Authorization": "Bearer user123.+919876543210.1685888000.invalid"})
        ]
        
        for test_name, headers in invalid_tokens:
            try:
                url = f"{self.base_url}/profile"
                response = requests.get(url, headers=headers)
                
                if response.status_code == 401:
                    self.print_success(f"{test_name}: Correctly rejected")
                else:
                    self.print_error(f"{test_name}: Not rejected (status: {response.status_code})")
                    return False
                    
            except Exception as e:
                self.print_error(f"{test_name}: Test failed - {str(e)}")
                return False
        
        self.print_success("All invalid tokens correctly rejected")
        return True
    
    def test_token_regeneration(self):
        """Test token regeneration after login"""
        self.print_step(6, "Test Token Regeneration")
        
        try:
            # Login again to get a new token
            verify_url = f"{self.base_url}/auth/otp/verify"
            verify_response = requests.post(verify_url, json={
                "phone": self.test_phone,
                "otp": self.test_otp
            })
            
            if verify_response.status_code != 200:
                self.print_error(f"Failed to regenerate token: {verify_response.status_code}")
                return False
            
            data = verify_response.json()
            if 'token' not in data:
                self.print_error("No token in regeneration response")
                return False
            
            new_token = data['token']
            
            if new_token != self.auth_token:
                self.print_success("New token generated (different from previous)")
            else:
                self.print_info("Same token returned (this is acceptable)")
            
            # Test the new token
            headers = {
                "Authorization": f"Bearer {new_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/profile"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                self.print_success("New token works correctly")
                return True
            else:
                self.print_error(f"New token failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Token regeneration test failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all token flow tests"""
        print("🚀 Starting Detailed Token Flow Tests")
        print("=" * 60)
        
        tests = [
            ("Token Generation", self.test_token_generation),
            ("Token Structure", self.test_token_structure),
            ("Token Verification", self.test_token_verification),
            ("Token Expiration", self.test_token_expiration),
            ("Invalid Tokens", self.test_invalid_tokens),
            ("Token Regeneration", self.test_token_regeneration)
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
            self.print_success("🎉 ALL TOKEN FLOW TESTS PASSED!")
            return True
        else:
            self.print_error(f"❌ {total - passed} tests failed")
            return False

def main():
    """Main test runner"""
    print("🧪 Detailed Token Flow Tests")
    print("=" * 60)
    
    test = TokenFlowTest()
    success = test.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main() 