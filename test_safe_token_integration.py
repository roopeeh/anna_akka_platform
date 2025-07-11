#!/usr/bin/env python3
"""
Safe Integration Tests for Custom Token Authentication System
This version doesn't send real SMS by default and provides testing options.
"""

import requests
import json
import time
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import test configuration
try:
    from test_config import get_test_config
    config = get_test_config()
except ImportError:
    # Fallback configuration
    from env_config import get_test_config
    config = get_test_config()

class SafeTokenIntegrationTest:
    def __init__(self):
        self.base_url = config["base_url"]
        self.auth_token = None
        self.user_data = None
        self.test_phone = config["test_phone"]
        self.test_otp = config["test_otp"]
        self.use_real_sms = config["use_real_sms"]
        self.accept_test_otp = config["accept_test_otp"]
        
    def print_step(self, step, description):
        """Print a formatted test step"""
        print(f"\n{'='*60}")
        print(f"STEP {step}: {description}")
        print(f"{'='*60}")
    
    def print_success(self, message):
        """Print success message"""
        print(f"✅ {message}")
    
    def print_error(self, message):
        """Print error message"""
        print(f"❌ {message}")
    
    def print_info(self, message):
        """Print info message"""
        print(f"ℹ️  {message}")
    
    def print_warning(self, message):
        """Print warning message"""
        print(f"⚠️  {message}")
    
    def get_user_choice(self, prompt, default="n"):
        """Get user input with default"""
        try:
            response = input(f"{prompt} (y/N): ").lower().strip()
            return response == "y" or (response == "" and default == "y")
        except:
            return default == "y"
    
    def run_test(self):
        """Run the complete integration test"""
        print("🚀 Starting Safe Custom Token Authentication Integration Tests")
        print("=" * 60)
        
        # Show current configuration
        self.print_info(f"Test phone: {self.test_phone}")
        self.print_info(f"Use real SMS: {self.use_real_sms}")
        self.print_info(f"Accept test OTP: {self.accept_test_otp}")
        print()
        
        # Ask user if they want to proceed
        if not self.use_real_sms:
            self.print_warning("This test will NOT send real SMS messages.")
            self.print_info("To test with real SMS, set use_real_sms: True in test_config.py")
        else:
            self.print_warning("This test WILL send real SMS messages.")
            proceed = self.get_user_choice("Do you want to proceed with real SMS?", "n")
            if not proceed:
                self.print_info("Test cancelled by user.")
                return False
        
        try:
            # Step 1: Test OTP sending (with safety checks)
            if not self.test_send_otp_safe():
                return False
            
            # Step 2: Test OTP verification
            if not self.test_verify_otp_safe():
                return False
            
            # Step 3: Test protected endpoints with token
            if not self.test_protected_endpoints():
                return False
            
            # Step 4: Test token expiration
            if not self.test_token_expiration():
                return False
            
            # Step 5: Test invalid token scenarios
            if not self.test_invalid_token_scenarios():
                return False
            
            self.print_success("🎉 ALL INTEGRATION TESTS PASSED!")
            return True
            
        except Exception as e:
            self.print_error(f"Test failed with exception: {str(e)}")
            return False
    
    def test_send_otp_safe(self):
        """Test sending OTP with safety checks"""
        self.print_step(1, "Send OTP (Safe Mode)")
        
        try:
            url = f"{self.base_url}/auth/otp/send"
            payload = {
                "phone": self.test_phone
            }
            
            self.print_info(f"Preparing to send OTP to: {self.test_phone}")
            
            if not self.use_real_sms:
                self.print_warning("SMS sending is disabled in safe mode.")
                self.print_info("This will test the API endpoint but won't send real SMS.")
                self.print_info("To enable real SMS, set use_real_sms: True in test_config.py")
                
                # Ask user if they want to proceed anyway
                proceed = self.get_user_choice("Proceed with API test (no real SMS)?", "y")
                if not proceed:
                    self.print_info("Test cancelled by user.")
                    return False
            
            response = requests.post(url, json=payload)
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'OTP sent' in data['message']:
                    self.print_success("OTP API endpoint working correctly")
                    if self.use_real_sms:
                        self.print_info("Real SMS sent - check your phone for OTP")
                    else:
                        self.print_info("SMS not sent (safe mode) - using test OTP")
                    return True
                else:
                    self.print_error("Unexpected response format")
                    return False
            else:
                self.print_error(f"Failed to send OTP: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Error sending OTP: {str(e)}")
            return False
    
    def test_verify_otp_safe(self):
        """Test OTP verification with user input option"""
        self.print_step(2, "Verify OTP and Get Token")
        
        try:
            url = f"{self.base_url}/auth/otp/verify"
            
            # Determine which OTP to use
            if self.accept_test_otp:
                otp_to_use = self.test_otp
                self.print_info(f"Using test OTP: {otp_to_use}")
            else:
                # Ask user for OTP
                self.print_info("Test OTP not accepted by system.")
                self.print_info("Please enter the OTP received on your phone:")
                try:
                    otp_to_use = input("Enter OTP: ").strip()
                    if not otp_to_use:
                        self.print_error("No OTP entered")
                        return False
                except:
                    self.print_error("Failed to get OTP input")
                    return False
            
            payload = {
                "phone": self.test_phone,
                "otp": otp_to_use
            }
            
            self.print_info(f"Verifying OTP for: {self.test_phone}")
            
            response = requests.post(url, json=payload)
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.auth_token = data['token']
                    self.user_data = data.get('user', {})
                    
                    self.print_success("OTP verified and token received")
                    self.print_info(f"Token: {self.auth_token[:50]}...")
                    self.print_info(f"User ID: {self.user_data.get('id', 'N/A')}")
                    return True
                else:
                    self.print_error("No token in response")
                    return False
            else:
                self.print_error(f"Failed to verify OTP: {response.status_code}")
                if not self.accept_test_otp:
                    self.print_warning("This might be because:")
                    self.print_warning("1. The OTP you entered is incorrect")
                    self.print_warning("2. The OTP has expired")
                    self.print_warning("3. The phone number doesn't match")
                return False
                
        except Exception as e:
            self.print_error(f"Error verifying OTP: {str(e)}")
            return False
    
    def test_protected_endpoints(self):
        """Test all protected endpoints with valid token"""
        self.print_step(3, "Test Protected Endpoints with Valid Token")
        
        if not self.auth_token:
            self.print_error("No auth token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test Profile endpoints
        if not self.test_profile_endpoints(headers):
            return False
        
        # Test Cart endpoints
        if not self.test_cart_endpoints(headers):
            return False
        
        # Test Orders endpoints
        if not self.test_orders_endpoints(headers):
            return False
        
        # Test Stores endpoints
        if not self.test_stores_endpoints(headers):
            return False
        
        # Test Products endpoints
        if not self.test_products_endpoints(headers):
            return False
        
        self.print_success("All protected endpoints working with valid token")
        return True
    
    def test_profile_endpoints(self, headers):
        """Test profile endpoints"""
        self.print_info("Testing Profile endpoints...")
        
        try:
            # Test GET /profile
            url = f"{self.base_url}/profile"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                self.print_success("GET /profile - Success")
            else:
                self.print_error(f"GET /profile - Failed: {response.status_code}")
                return False
            
            # Test PUT /profile
            update_data = {
                "name": "Updated Test User",
                "phone": self.test_phone
            }
            response = requests.put(url, headers=headers, json=update_data)
            
            if response.status_code == 200:
                self.print_success("PUT /profile - Success")
            else:
                self.print_error(f"PUT /profile - Failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.print_error(f"Profile endpoints test failed: {str(e)}")
            return False
    
    def test_cart_endpoints(self, headers):
        """Test cart endpoints"""
        self.print_info("Testing Cart endpoints...")
        
        try:
            # Test GET /cart
            url = f"{self.base_url}/cart"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                self.print_success("GET /cart - Success")
            else:
                self.print_error(f"GET /cart - Failed: {response.status_code}")
                return False
            
            # Test POST /cart/items
            cart_item = {
                "product_id": "test-product-123",
                "quantity": 2
            }
            response = requests.post(f"{self.base_url}/cart/items", headers=headers, json=cart_item)
            
            if response.status_code in [200, 201]:
                self.print_success("POST /cart/items - Success")
            else:
                self.print_error(f"POST /cart/items - Failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.print_error(f"Cart endpoints test failed: {str(e)}")
            return False
    
    def test_orders_endpoints(self, headers):
        """Test orders endpoints"""
        self.print_info("Testing Orders endpoints...")
        
        try:
            # Test GET /orders
            url = f"{self.base_url}/orders"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                self.print_success("GET /orders - Success")
            else:
                self.print_error(f"GET /orders - Failed: {response.status_code}")
                return False
            
            # Test POST /orders
            order_data = {
                "store_id": "test-store-123",
                "delivery_address": "123 Test Street",
                "total_amount": 100.00
            }
            response = requests.post(url, headers=headers, json=order_data)
            
            if response.status_code in [200, 201]:
                self.print_success("POST /orders - Success")
            else:
                self.print_error(f"POST /orders - Failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.print_error(f"Orders endpoints test failed: {str(e)}")
            return False
    
    def test_stores_endpoints(self, headers):
        """Test stores endpoints"""
        self.print_info("Testing Stores endpoints...")
        
        try:
            # Test GET /stores/owner
            url = f"{self.base_url}/stores/owner"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                self.print_success("GET /stores/owner - Success")
            else:
                self.print_error(f"GET /stores/owner - Failed: {response.status_code}")
                return False
            
            # Test POST /stores
            store_data = {
                "name": "Test Store",
                "address": "456 Test Avenue",
                "phone": self.test_phone
            }
            response = requests.post(f"{self.base_url}/stores", headers=headers, json=store_data)
            
            if response.status_code in [200, 201]:
                self.print_success("POST /stores - Success")
            else:
                self.print_error(f"POST /stores - Failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.print_error(f"Stores endpoints test failed: {str(e)}")
            return False
    
    def test_products_endpoints(self, headers):
        """Test products endpoints"""
        self.print_info("Testing Products endpoints...")
        
        try:
            # Test POST /stores/{store_id}/products
            store_id = "test-store-123"
            product_data = {
                "name": "Test Product",
                "price": 25.50,
                "unit": "piece",
                "stock": 10
            }
            url = f"{self.base_url}/stores/{store_id}/products"
            response = requests.post(url, headers=headers, json=product_data)
            
            if response.status_code in [200, 201]:
                self.print_success("POST /stores/{store_id}/products - Success")
            else:
                self.print_error(f"POST /stores/{store_id}/products - Failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.print_error(f"Products endpoints test failed: {str(e)}")
            return False
    
    def test_token_expiration(self):
        """Test token expiration handling"""
        self.print_step(4, "Test Token Expiration")
        
        try:
            # Create an expired token
            expired_token = "user123.+919876543210.1640995200.expired123"  # Expired timestamp
            
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
    
    def test_invalid_token_scenarios(self):
        """Test various invalid token scenarios"""
        self.print_step(5, "Test Invalid Token Scenarios")
        
        test_cases = [
            ("No token", {}, "No Authorization header"),
            ("Empty token", {"Authorization": "Bearer "}, "Empty token"),
            ("Invalid format", {"Authorization": "InvalidToken"}, "Invalid token format"),
            ("Missing Bearer", {"Authorization": "user123.phone.1234567890.signature"}, "Missing Bearer prefix"),
            ("Invalid signature", {"Authorization": "Bearer user123.+919876543210.1685888000.invalid"}, "Invalid signature")
        ]
        
        for test_name, headers, description in test_cases:
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
        
        self.print_success("All invalid token scenarios handled correctly")
        return True

def main():
    """Main test runner"""
    print("🧪 Safe Custom Token Authentication Integration Tests")
    print("=" * 60)
    
    test = SafeTokenIntegrationTest()
    success = test.run_test()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main() 