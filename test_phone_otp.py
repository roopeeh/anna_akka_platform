#!/usr/bin/env python3
"""
Test Passwordless OTP Flow with specific phone number
Updated for latest changes: Direct SNS SMS, no Cognito password reset
"""

import requests
import json
import time

# Configuration
BASE_URL = "https://4yvijqg3z3.execute-api.us-east-1.amazonaws.com/dev"
HEADERS = {
    "Content-Type": "application/json"
}

TEST_PHONE = "+919502528182"

def test_otp_flow():
    """Test the complete passwordless OTP flow with the specific phone number"""
    print(f"🚀 Testing Passwordless OTP Flow with phone: {TEST_PHONE}")
    print("=" * 60)
    print("📱 Flow: Phone → OTP → Login (No passwords!)")
    print("=" * 60)
    
    # Step 1: Send OTP
    print("\n1️⃣ 📤 Sending OTP...")
    send_data = {"phone": TEST_PHONE}
    
    try:
        print(f"📤 Request: POST {BASE_URL}/auth/otp/send")
        print(f"📤 Data: {json.dumps(send_data, indent=2)}")
        
        response = requests.post(f"{BASE_URL}/auth/otp/send", 
                               headers=HEADERS, 
                               json=send_data)
        
        print(f"📤 Status: {response.status_code}")
        print(f"📤 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ OTP sent successfully via SNS SMS!")
            print("📱 Check your phone for SMS from AWS SNS")
            
            # Step 2: Wait for user to enter OTP
            print("\n2️⃣ 🔢 Please check your phone for the OTP...")
            print("📱 Look for SMS with format: 'Your Anna Akka verification code is: XXXXXX'")
            print("⏰ OTP expires in 5 minutes")
            
            test_otp = input("🔢 Enter OTP: ").strip()
            
            if not test_otp:
                print("❌ No OTP entered!")
                return
            
            if len(test_otp) != 6:
                print("❌ OTP should be 6 digits!")
                return
            
            verify_data = {
                "phone": TEST_PHONE,
                "otp": test_otp
            }
            
            print(f"\n3️⃣ 🔍 Verifying OTP: {test_otp}")
            print(f"🔍 Request: POST {BASE_URL}/auth/otp/verify")
            print(f"🔍 Data: {json.dumps(verify_data, indent=2)}")
            
            verify_response = requests.post(f"{BASE_URL}/auth/otp/verify", 
                                          headers=HEADERS, 
                                          json=verify_data)
            
            print(f"🔍 Status: {verify_response.status_code}")
            print(f"🔍 Response: {verify_response.text}")
            
            if verify_response.status_code == 200:
                print("✅ OTP verified successfully!")
                
                # Parse the response to see if it's a new user or existing user
                try:
                    response_data = verify_response.json()
                    is_new_user = response_data.get('is_new_user', False)
                    auth_type = response_data.get('auth_type', 'unknown')
                    
                    print(f"👤 User type: {'New User' if is_new_user else 'Existing User'}")
                    print(f"🔐 Auth type: {auth_type}")
                    
                    if is_new_user:
                        print("\n4️⃣ 🆕 This is a new user - registration needed")
                        print("📝 To complete registration, call the /auth/register endpoint")
                        print("📝 with name, email, and user_type")
                    else:
                        print("✅ Login successful for existing user!")
                        user_data = response_data.get('user', {})
                        if user_data:
                            print(f"👤 User ID: {user_data.get('id', 'N/A')}")
                            print(f"👤 Name: {user_data.get('name', 'N/A')}")
                            print(f"👤 Email: {user_data.get('email', 'N/A')}")
                        
                except json.JSONDecodeError:
                    print("❌ Could not parse response!")
            else:
                print("❌ OTP verification failed!")
                print("💡 Possible reasons:")
                print("   - Invalid OTP")
                print("   - Expired OTP (5 minutes)")
                print("   - Wrong phone number")
        else:
            print("❌ OTP send failed!")
            print("💡 Check CloudWatch logs for detailed error")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Check network connection and API endpoint")

def test_quick_flow():
    """Quick test without user input - for debugging"""
    print(f"🔧 Quick Test Mode - {TEST_PHONE}")
    print("=" * 40)
    
    # Test 1: Send OTP
    print("\n📤 Testing OTP Send...")
    send_data = {"phone": TEST_PHONE}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/otp/send", 
                               headers=HEADERS, 
                               json=send_data)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ OTP send test passed!")
        else:
            print("❌ OTP send test failed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🎯 Choose test mode:")
    print("1. Full OTP Flow (with user input)")
    print("2. Quick Test (OTP send only)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        test_quick_flow()
    else:
        test_otp_flow() 