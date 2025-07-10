#!/usr/bin/env python3
"""
Test Configuration for Custom Token Authentication Tests
Configure your test settings here to avoid using real phone numbers.
"""

# Test Configuration
TEST_CONFIG = {
    # Test phone number - CHANGE THIS TO YOUR TEST NUMBER
    "test_phone": "+919502528182",  # Replace with your test phone number
    
    # Test OTP - This is used when the system accepts test OTPs
    "test_otp": "123456",
    
    # API Base URL
    "base_url": "https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev",
    
    # Test Settings
    "use_real_sms": True,  # Set to True if you want to send real SMS
    "accept_test_otp": False,  # Set to True if your system accepts test OTPs
    
    # Timeout settings
    "request_timeout": 30,  # seconds
    "otp_wait_time": 60,   # seconds to wait for OTP
    
    # Test data
    "test_user": {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+919876543210"
    },
    
    # Test products
    "test_product": {
        "name": "Test Product",
        "price": 25.50,
        "unit": "piece",
        "stock": 10
    },
    
    # Test store
    "test_store": {
        "name": "Test Store",
        "address": "123 Test Street",
        "phone": "+919876543210"
    }
}

# Instructions for using this configuration:
"""
INSTRUCTIONS:

1. CHANGE THE TEST PHONE NUMBER:
   - Replace "test_phone" with a phone number you control
   - This can be your own number for testing
   - Or use a test number if you have one

2. OTP HANDLING OPTIONS:
   - If your system accepts test OTPs (like "123456"), set "accept_test_otp": True
   - If not, set "accept_test_otp": False and use the real OTP from your phone
   - Set "use_real_sms": False to avoid sending SMS during testing

3. FOR DEVELOPMENT TESTING:
   - You can modify the OTP handler to accept test OTPs
   - Or use a mock SMS service
   - Or temporarily disable SMS sending

4. SAFETY FEATURES:
   - Tests will warn you before sending SMS
   - You can abort tests if needed
   - Test phone numbers are clearly marked
"""

def get_test_config():
    """Get the test configuration"""
    return TEST_CONFIG

def print_test_instructions():
    """Print test instructions"""
    print("🧪 TEST CONFIGURATION INSTRUCTIONS")
    print("=" * 60)
    print("1. Edit test_config.py to set your test phone number")
    print("2. Choose your OTP handling method:")
    print("   - Use real SMS (set use_real_sms: True)")
    print("   - Use test OTPs (set accept_test_otp: True)")
    print("   - Modify the OTP handler for testing")
    print("3. Run tests with: python test_custom_token_integration.py")
    print("=" * 60)

if __name__ == "__main__":
    print_test_instructions() 