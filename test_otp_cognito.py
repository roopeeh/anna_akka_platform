#!/usr/bin/env python3
"""
Simple OTP Test with Cognito SMS

This script tests the OTP functionality using Cognito's built-in SMS.
"""

import requests
import json
import time

# Configuration
from env_config import get_base_url

BASE_URL = get_base_url()
from env_config import get_headers

HEADERS = get_headers()

def test_otp_flow():
    """Test the complete OTP flow"""
    print("🚀 Testing OTP Flow with Cognito SMS")
    print("=" * 50)
    
    # Test phone number (replace with your actual phone number for testing)
    test_phone = "+91 98765 43210"  # Use a real phone number for testing
    
    print(f"📱 Testing with phone: {test_phone}")
    
    # Step 1: Send OTP
    print("\n1️⃣ Sending OTP...")
    send_data = {"phone": test_phone}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/otp/send", 
                               headers=HEADERS, 
                               json=send_data)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ OTP sent successfully!")
            
            # Step 2: Verify OTP (you'll need to enter the actual OTP)
            print("\n2️⃣ Verifying OTP...")
            print("Please check your phone for the OTP and enter it below:")
            
            # For testing, we'll use a mock OTP
            # In real usage, you would get this from the user
            test_otp = "123456"  # Replace with actual OTP
            
            verify_data = {
                "phone": test_phone,
                "otp": test_otp
            }
            
            verify_response = requests.post(f"{BASE_URL}/auth/otp/verify", 
                                          headers=HEADERS, 
                                          json=verify_data)
            
            print(f"Status: {verify_response.status_code}")
            print(f"Response: {verify_response.text}")
            
            if verify_response.status_code == 200:
                print("✅ OTP verified successfully!")
                
                # Step 3: Register user (if new user)
                print("\n3️⃣ Registering user...")
                register_data = {
                    "phone": test_phone,
                    "otp": test_otp,
                    "name": "Test User",
                    "email": "test@example.com",
                    "user_type": "customer"
                }
                
                register_response = requests.post(f"{BASE_URL}/auth/register", 
                                               headers=HEADERS, 
                                               json=register_data)
                
                print(f"Status: {register_response.status_code}")
                print(f"Response: {register_response.text}")
                
                if register_response.status_code == 201:
                    print("✅ User registered successfully!")
                else:
                    print("❌ User registration failed!")
            else:
                print("❌ OTP verification failed!")
        else:
            print("❌ OTP send failed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_existing_user_login():
    """Test login for existing user"""
    print("\n🔐 Testing Login for Existing User")
    print("=" * 50)
    
    test_phone = "+91 98765 43210"  # Use a real phone number
    
    # Step 1: Send OTP for login
    print("\n1️⃣ Sending OTP for login...")
    send_data = {"phone": test_phone}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/otp/send", 
                               headers=HEADERS, 
                               json=send_data)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ OTP sent for login!")
            
            # Step 2: Verify OTP for login
            print("\n2️⃣ Verifying OTP for login...")
            test_otp = "123456"  # Replace with actual OTP
            
            verify_data = {
                "phone": test_phone,
                "otp": test_otp
            }
            
            verify_response = requests.post(f"{BASE_URL}/auth/otp/verify", 
                                          headers=HEADERS, 
                                          json=verify_data)
            
            print(f"Status: {verify_response.status_code}")
            print(f"Response: {verify_response.text}")
            
            if verify_response.status_code == 200:
                print("✅ Login successful!")
            else:
                print("❌ Login failed!")
        else:
            print("❌ OTP send for login failed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("Choose test:")
    print("1. New user registration flow")
    print("2. Existing user login flow")
    print("3. Both")
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == "1":
        test_otp_flow()
    elif choice == "2":
        test_existing_user_login()
    elif choice == "3":
        test_otp_flow()
        test_existing_user_login()
    else:
        print("Invalid choice!") 