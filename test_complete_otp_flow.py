#!/usr/bin/env python3
"""
Complete OTP Flow Test
Covers: Registration → Login → User Validation → Existing User Login
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

def test_complete_otp_flow():
    """Test the complete OTP flow: Registration → Login → Validation"""
    print(f"🚀 Complete OTP Flow Test with phone: {TEST_PHONE}")
    print("=" * 80)
    print("📋 Flow: Registration → OTP → Login → User Validation")
    print("=" * 80)
    
    # Step 1: Check if user exists
    print("\n1️⃣ 🔍 Checking if user exists...")
    try:
        check_response = requests.get(f"{BASE_URL}/auth/user/phone?phone={TEST_PHONE}")
        print(f"🔍 Status: {check_response.status_code}")
        print(f"🔍 Response: {check_response.text}")
        
        if check_response.status_code == 200:
            print("👤 User exists - will test login flow")
            is_existing_user = True
        else:
            print("🆕 User doesn't exist - will test registration flow")
            is_existing_user = False
            
    except Exception as e:
        print(f"❌ Error checking user: {str(e)}")
        is_existing_user = False
    
    # Step 2: Send OTP
    print(f"\n2️⃣ 📤 Sending OTP for {'existing user login' if is_existing_user else 'new user registration'}...")
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
            print("✅ OTP sent successfully!")
            print("📱 Check your phone for SMS from AWS SNS")
            
            # Step 3: Wait for OTP input
            print("\n3️⃣ 🔢 Please check your phone for the OTP...")
            print("📱 Look for SMS with format: 'Your Anna Akka verification code is: XXXXXX'")
            print("⏰ OTP expires in 5 minutes")
            
            test_otp = input("🔢 Enter OTP: ").strip()
            
            if not test_otp:
                print("❌ No OTP entered!")
                return
            
            if len(test_otp) != 6:
                print("❌ OTP should be 6 digits!")
                return
            
            # Step 4: Verify OTP
            print(f"\n4️⃣ 🔍 Verifying OTP: {test_otp}")
            verify_data = {
                "phone": TEST_PHONE,
                "otp": test_otp
            }
            
            print(f"🔍 Request: POST {BASE_URL}/auth/otp/verify")
            print(f"🔍 Data: {json.dumps(verify_data, indent=2)}")
            
            verify_response = requests.post(f"{BASE_URL}/auth/otp/verify", 
                                          headers=HEADERS, 
                                          json=verify_data)
            
            print(f"🔍 Status: {verify_response.status_code}")
            print(f"🔍 Response: {verify_response.text}")
            
            if verify_response.status_code == 200:
                print("✅ OTP verified successfully!")
                
                # Parse response
                try:
                    response_data = verify_response.json()
                    is_new_user = response_data.get('is_new_user', False)
                    auth_type = response_data.get('auth_type', 'unknown')
                    
                    print(f"👤 User type: {'New User' if is_new_user else 'Existing User'}")
                    print(f"🔐 Auth type: {auth_type}")
                    
                    if is_new_user:
                        # Step 5: Register new user
                        print("\n5️⃣ 🆕 Registering new user...")
                        register_data = {
                            "phone": TEST_PHONE,
                            "name": "Test User Complete Flow",
                            "email": "test.complete@example.com",
                            "roles": ["customer"]
                        }
                        
                        print(f"📝 Request: POST {BASE_URL}/auth/register")
                        print(f"📝 Data: {json.dumps(register_data, indent=2)}")
                        
                        register_response = requests.post(f"{BASE_URL}/auth/register", 
                                                       headers=HEADERS, 
                                                       json=register_data)
                        
                        print(f"📝 Status: {register_response.status_code}")
                        print(f"📝 Response: {register_response.text}")
                        
                        if register_response.status_code == 201:
                            print("✅ User registered successfully!")
                            
                            # Step 6: Validate registration by getting user
                            print("\n6️⃣ 🔍 Validating registration by getting user...")
                            validate_registration()
                        else:
                            print("❌ User registration failed!")
                    else:
                        print("✅ Login successful for existing user!")
                        user_data = response_data.get('user', {})
                        if user_data:
                            print(f"👤 User ID: {user_data.get('id', 'N/A')}")
                            print(f"👤 Name: {user_data.get('name', 'N/A')}")
                            print(f"👤 Email: {user_data.get('email', 'N/A')}")
                            print(f"👤 Phone: {user_data.get('phone', 'N/A')}")
                            print(f"👤 Roles: {user_data.get('roles', 'N/A')}")
                        
                        # Step 6: Validate existing user by getting user
                        print("\n6️⃣ 🔍 Validating existing user by getting user...")
                        validate_existing_user()
                        
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

def validate_registration():
    """Validate that new user was registered correctly"""
    print("\n🔍 Validating new user registration...")
    
    try:
        # Get user by phone
        print(f"🔍 Request: GET {BASE_URL}/auth/user/phone?phone={TEST_PHONE}")
        response = requests.get(f"{BASE_URL}/auth/user/phone?phone={TEST_PHONE}")
        
        print(f"🔍 Status: {response.status_code}")
        print(f"🔍 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ User found in database after registration!")
            user_data = response.json()
            print(f"👤 User ID: {user_data.get('id', 'N/A')}")
            print(f"👤 Name: {user_data.get('name', 'N/A')}")
            print(f"👤 Email: {user_data.get('email', 'N/A')}")
            print(f"👤 Phone: {user_data.get('phone', 'N/A')}")
            print(f"👤 Roles: {user_data.get('roles', 'N/A')}")
        else:
            print("❌ User not found in database after registration!")
            
    except Exception as e:
        print(f"❌ Error validating registration: {str(e)}")

def validate_existing_user():
    """Validate existing user data"""
    print("\n🔍 Validating existing user data...")
    
    try:
        # Get user by phone
        print(f"🔍 Request: GET {BASE_URL}/auth/user/phone?phone={TEST_PHONE}")
        response = requests.get(f"{BASE_URL}/auth/user/phone?phone={TEST_PHONE}")
        
        print(f"🔍 Status: {response.status_code}")
        print(f"🔍 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Existing user data validated!")
            user_data = response.json()
            print(f"👤 User ID: {user_data.get('id', 'N/A')}")
            print(f"👤 Name: {user_data.get('name', 'N/A')}")
            print(f"👤 Email: {user_data.get('email', 'N/A')}")
            print(f"👤 Phone: {user_data.get('phone', 'N/A')}")
            print(f"👤 Roles: {user_data.get('roles', 'N/A')}")
        else:
            print("❌ Could not validate existing user data!")
            
    except Exception as e:
        print(f"❌ Error validating existing user: {str(e)}")

def test_user_lookup():
    """Test user lookup functionality"""
    print(f"\n🔍 Testing user lookup for: {TEST_PHONE}")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/auth/user/phone?phone={TEST_PHONE}")
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ User found!")
            user_data = response.json()
            print(f"👤 User details:")
            print(f"   ID: {user_data.get('id', 'N/A')}")
            print(f"   Name: {user_data.get('name', 'N/A')}")
            print(f"   Email: {user_data.get('email', 'N/A')}")
            print(f"   Phone: {user_data.get('phone', 'N/A')}")
            print(f"   Roles: {user_data.get('roles', 'N/A')}")
            print(f"   Created: {user_data.get('created_at', 'N/A')}")
            print(f"   Updated: {user_data.get('updated_at', 'N/A')}")
        else:
            print("❌ User not found!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_otp_send_only():
    """Quick test for OTP send only"""
    print(f"\n📤 Quick OTP Send Test for: {TEST_PHONE}")
    print("=" * 40)
    
    try:
        send_data = {"phone": TEST_PHONE}
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
    print("1. Complete OTP Flow (Registration → Login → Validation)")
    print("2. User Lookup Test")
    print("3. Quick OTP Send Test")
    
    choice = input("Enter choice (1, 2, or 3): ").strip()
    
    if choice == "2":
        test_user_lookup()
    elif choice == "3":
        test_otp_send_only()
    else:
        test_complete_otp_flow() 