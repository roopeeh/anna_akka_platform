#!/usr/bin/env python3
"""
Test Configuration for Custom Token Authentication Tests
This module now uses the centralized environment configuration.
"""

from env_config import get_test_config, print_config

# Get test configuration from environment
TEST_CONFIG = get_test_config()

# Instructions for using this configuration:
"""
INSTRUCTIONS:

1. ENVIRONMENT CONFIGURATION:
   - Copy env_example.txt to .env and modify values
   - Or set environment variables in your system
   - The API endpoint is now centralized in env_config.py

2. CHANGE THE TEST PHONE NUMBER:
   - Set TEST_PHONE environment variable to your test number
   - This can be your own number for testing
   - Or use a test number if you have one

3. OTP HANDLING OPTIONS:
   - Set ACCEPT_TEST_OTP=true if your system accepts test OTPs
   - Set USE_REAL_SMS=false to avoid sending SMS during testing
   - Configure these in environment variables

4. API ENDPOINTS:
   - Default endpoint: https://z8sre11rwh.execute-api.ap-south-1.amazonaws.com/dev
   - Can be overridden with API_BASE_URL environment variable
   - Multiple environments supported (dev, local)

5. SAFETY FEATURES:
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
    print("1. Configure environment variables or copy env_example.txt to .env")
    print("2. Set TEST_PHONE to your test phone number")
    print("3. Choose your OTP handling method:")
    print("   - Use real SMS (set USE_REAL_SMS=true)")
    print("   - Use test OTPs (set ACCEPT_TEST_OTP=true)")
    print("   - Modify the OTP handler for testing")
    print("4. Run tests with: python test_custom_token_integration.py")
    print("5. Current configuration:")
    print_config()
    print("=" * 60)

if __name__ == "__main__":
    print_test_instructions() 