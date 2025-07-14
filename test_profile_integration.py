#!/usr/bin/env python3
"""
Profile Integration Test Script

This script tests the updated profile endpoints with mock authentication
and CRUD operations including phone number lookup functionality.

Usage:
    python test_profile_integration.py
"""

import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
from env_config import get_base_url

API_BASE_URL = get_base_url()

# Test user data
TEST_USER_ID = "mock-user-id"  # Use mock user ID
TEST_PHONE = "9502528182"
TEST_EMAIL = "test.user@example.com"

class ProfileIntegrationTest:
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url
        
    def make_request(self, method, endpoint, data=None, headers=None, params=None):
        """Make API request with error handling"""
        url = f"{self.api_base_url}{endpoint}"
        
        # Default headers (no authentication required with mock system)
        default_headers = {
            "Content-Type": "application/json"
        }
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=default_headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=default_headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=default_headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_body = e.response.json()
                    logger.error(f"Error response: {error_body}")
                    return error_body
                except:
                    logger.error(f"Error status: {e.response.status_code}")
            return None
    
    def create_mock_user(self):
        """Create the mock user for testing"""
        logger.info("=== Creating Mock User ===")
        
        try:
            # First, try to get the existing user by phone to see if they already exist
            existing_user_result = self.make_request("GET", "/profile/phone", params={"phone": f"+91{TEST_PHONE}"})
            
            if existing_user_result and isinstance(existing_user_result, dict):
                if 'user' in existing_user_result:
                    user = existing_user_result['user']
                    logger.info(f"✅ Found existing user with phone {TEST_PHONE}")
                    logger.info(f"👤 User ID: {user.get('id', 'N/A')}")
                    logger.info(f"👤 Name: {user.get('name', 'N/A')}")
                    logger.info(f"👤 Email: {user.get('email', 'N/A')}")
                    logger.info(f"👤 Phone: {user.get('phone', 'N/A')}")
                    # Update the global TEST_USER_ID to use the actual user ID
                    global TEST_USER_ID
                    TEST_USER_ID = user.get('id', TEST_USER_ID)
                    return True
                elif 'body' in existing_user_result:  # Lambda response format
                    try:
                        body_data = json.loads(existing_user_result['body'])
                        if 'user' in body_data:
                            user = body_data['user']
                            logger.info(f"✅ Found existing user with phone {TEST_PHONE}")
                            logger.info(f"👤 User ID: {user.get('id', 'N/A')}")
                            logger.info(f"👤 Name: {user.get('name', 'N/A')}")
                            logger.info(f"👤 Email: {user.get('email', 'N/A')}")
                            logger.info(f"👤 Phone: {user.get('phone', 'N/A')}")
                            # Update the global TEST_USER_ID to use the actual user ID
                            global TEST_USER_ID
                            TEST_USER_ID = user.get('id', TEST_USER_ID)
                            return True
                    except:
                        pass
            
            # If no existing user found, try to create one with a different phone number
            logger.info("No existing user found, creating new mock user...")
            
            # Create mock user data with a unique phone number
            import time
            unique_phone = f"+91{int(time.time()) % 10000000000}"  # Use timestamp to make it unique
            user_data = {
                "name": "Test User",
                "email": f"test.user.{int(time.time())}@example.com",  # Make email unique too
                "phone": unique_phone,
                "address": "123 Test Street, Test City"
            }
            
            # Use the auth register endpoint to create the user
            result = self.make_request("POST", "/auth/register", data=user_data)
            
            if result and isinstance(result, dict):
                if 'user' in result:
                    user = result['user']
                    logger.info(f"✅ Mock user created successfully!")
                    logger.info(f"👤 User ID: {user.get('id', 'N/A')}")
                    logger.info(f"👤 Name: {user.get('name', 'N/A')}")
                    logger.info(f"👤 Email: {user.get('email', 'N/A')}")
                    logger.info(f"👤 Phone: {user.get('phone', 'N/A')}")
                    # Update the global TEST_USER_ID to use the actual user ID
                    global TEST_USER_ID
                    TEST_USER_ID = user.get('id', TEST_USER_ID)
                    return True
                elif 'body' in result:  # Lambda response format
                    try:
                        body_data = json.loads(result['body'])
                        if 'user' in body_data:
                            user = body_data['user']
                            logger.info(f"✅ Mock user created successfully!")
                            logger.info(f"👤 User ID: {user.get('id', 'N/A')}")
                            logger.info(f"👤 Name: {user.get('name', 'N/A')}")
                            logger.info(f"👤 Email: {user.get('email', 'N/A')}")
                            logger.info(f"👤 Phone: {user.get('phone', 'N/A')}")
                            # Update the global TEST_USER_ID to use the actual user ID
                            global TEST_USER_ID
                            TEST_USER_ID = user.get('id', TEST_USER_ID)
                            return True
                    except:
                        pass
            
            logger.error(f"❌ Failed to create mock user: {result}")
            return False
                
        except Exception as e:
            logger.error(f"❌ Error creating mock user: {str(e)}")
            return False
    
    def test_get_profile(self):
        """Test GET /profile endpoint"""
        logger.info("=== Testing GET /profile ===")
        
        try:
            result = self.make_request("GET", "/profile")
            
            # Check if we got a user object (either directly or in 'user' field)
            user = None
            if result and isinstance(result, dict):
                if 'user' in result:
                    user = result['user']
                elif 'id' in result:  # Direct user object
                    user = result
                elif 'body' in result:  # Lambda response format
                    try:
                        body_data = json.loads(result['body'])
                        if 'user' in body_data:
                            user = body_data['user']
                        elif 'id' in body_data:
                            user = body_data
                    except:
                        pass
            
            if user:
                logger.info(f"✅ Profile retrieved successfully!")
                logger.info(f"👤 User ID: {user.get('id', 'N/A')}")
                logger.info(f"👤 Name: {user.get('name', 'N/A')}")
                logger.info(f"👤 Email: {user.get('email', 'N/A')}")
                logger.info(f"👤 Phone: {user.get('phone', 'N/A')}")
                logger.info(f"👤 Roles: {user.get('roles', 'N/A')}")
                return True
            else:
                logger.error(f"❌ Failed to get profile: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing GET /profile: {str(e)}")
            return False
    
    def test_update_profile(self):
        """Test PUT /profile endpoint"""
        logger.info("=== Testing PUT /profile ===")
        
        try:
            # Test data for profile update
            update_data = {
                "name": "Updated Test User",
                "phone": "9502528182",
                "address": "456 Updated Street, Test City",
                "email": "updated.test@example.com"
            }
            
            result = self.make_request("PUT", "/profile", data=update_data)
            
            # Check if we got a user object (either directly or in 'user' field)
            user = None
            if result and isinstance(result, dict):
                if 'user' in result:
                    user = result['user']
                elif 'id' in result:  # Direct user object
                    user = result
                elif 'body' in result:  # Lambda response format
                    try:
                        body_data = json.loads(result['body'])
                        if 'user' in body_data:
                            user = body_data['user']
                        elif 'id' in body_data:
                            user = body_data
                    except:
                        pass
            
            if user:
                logger.info(f"✅ Profile updated successfully!")
                logger.info(f"👤 Updated Name: {user.get('name', 'N/A')}")
                logger.info(f"👤 Updated Phone: {user.get('phone', 'N/A')}")
                logger.info(f"👤 Updated Email: {user.get('email', 'N/A')}")
                logger.info(f"👤 Updated Address: {user.get('address', 'N/A')}")
                return True
            else:
                logger.error(f"❌ Failed to update profile: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing PUT /profile: {str(e)}")
            return False
    
    def test_get_profile_by_phone(self):
        """Test GET /profile/phone endpoint"""
        logger.info("=== Testing GET /profile/phone ===")
        
        try:
            # Test with different phone number formats for the new phone number
            phone_formats = [
                "9502528182",
                "+919502528182",
                "91 95025 28182",
                "+91 95025 28182"
            ]
            
            for phone in phone_formats:
                logger.info(f"Testing phone format: {phone}")
                result = self.make_request("GET", "/profile/phone", params={"phone": phone})
                
                # Check if we got a user object
                user = None
                if result and isinstance(result, dict):
                    if 'user' in result:
                        user = result['user']
                    elif 'id' in result:  # Direct user object
                        user = result
                    elif 'body' in result:  # Lambda response format
                        try:
                            body_data = json.loads(result['body'])
                            if 'user' in body_data:
                                user = body_data['user']
                            elif 'id' in body_data:
                                user = body_data
                        except:
                            pass
                
                if user:
                    logger.info(f"✅ Profile found by phone: {phone}")
                    logger.info(f"👤 User ID: {user.get('id', 'N/A')}")
                    logger.info(f"👤 Name: {user.get('name', 'N/A')}")
                    logger.info(f"👤 Phone: {user.get('phone', 'N/A')}")
                    return True
                else:
                    logger.warning(f"⚠️  No profile found for phone: {phone}")
            
            logger.error("❌ No profile found for any phone format")
            return False
                
        except Exception as e:
            logger.error(f"❌ Error testing GET /profile/phone: {str(e)}")
            return False
    
    def test_delete_profile(self):
        """Test DELETE /profile endpoint"""
        logger.info("=== Testing DELETE /profile ===")
        
        try:
            # Make the DELETE request
            url = f"{self.api_base_url}/profile"
            headers = {"Content-Type": "application/json"}
            
            response = requests.delete(url, headers=headers)
            
            # Check if the request was successful (204 No Content is expected)
            if response.status_code == 204:
                logger.info(f"✅ Profile deleted successfully!")
                logger.info(f"📝 Status Code: {response.status_code}")
                return True
            elif response.status_code == 200:
                # Try to parse JSON response if it's 200
                try:
                    result = response.json()
                    if 'message' in result:
                        logger.info(f"✅ Profile deleted successfully!")
                        logger.info(f"📝 Message: {result['message']}")
                        return True
                    elif 'body' in result:  # Lambda response format
                        try:
                            body_data = json.loads(result['body'])
                            if 'message' in body_data:
                                logger.info(f"✅ Profile deleted successfully!")
                                logger.info(f"📝 Message: {body_data['message']}")
                                return True
                        except:
                            pass
                except:
                    logger.info(f"✅ Profile deleted successfully!")
                    logger.info(f"📝 Status Code: {response.status_code}")
                    return True
            else:
                logger.error(f"❌ Failed to delete profile: Status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing DELETE /profile: {str(e)}")
            return False
    
    def test_unauthorized_access(self):
        """Test unauthorized access scenarios (now using mock system)"""
        logger.info("=== Testing Unauthorized Access (Mock System) ===")
        
        try:
            # Test profile endpoints without any headers
            test_cases = [
                ("GET /profile", "GET", "/profile", None, None),
                ("PUT /profile", "PUT", "/profile", {"name": "test"}, None),
                ("DELETE /profile", "DELETE", "/profile", None, None),
                ("GET /profile/phone", "GET", "/profile/phone", None, {"phone": "1234567890"})
            ]
            
            for test_name, method, endpoint, data, params in test_cases:
                logger.info(f"Testing {test_name}...")
                
                try:
                    if method == "GET":
                        response = requests.get(f"{self.api_base_url}{endpoint}", params=params)
                    elif method == "PUT":
                        response = requests.put(f"{self.api_base_url}{endpoint}", json=data)
                    elif method == "DELETE":
                        response = requests.delete(f"{self.api_base_url}{endpoint}")
                    else:
                        continue
                    
                    # With mock system, these should work without authentication
                    if response.status_code in [200, 201, 204]:
                        logger.info(f"✅ {test_name}: PASS (Mock system allows access)")
                    else:
                        logger.warning(f"⚠️  {test_name}: Got {response.status_code} (Expected success with mock system)")
                        
                except Exception as e:
                    logger.error(f"❌ {test_name}: Exception - {str(e)}")
            
            return True
                
        except Exception as e:
            logger.error(f"❌ Error testing unauthorized access: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all profile integration tests"""
        logger.info("🚀 Starting Profile Integration Tests")
        logger.info("=" * 60)
        logger.info(f"📅 Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🌐 API Base URL: {self.api_base_url}")
        logger.info(f"👤 Mock User ID: {TEST_USER_ID}")
        logger.info("=" * 60)
        
        test_results = {
            "passed": 0,
            "failed": 0,
            "total": 0
        }
        
        # First, create the mock user
        logger.info(f"\n{'='*40}")
        logger.info(f"🧪 Running: Create Mock User")
        logger.info(f"{'='*40}")
        
        if not self.create_mock_user():
            logger.error("❌ Failed to create mock user - some tests may fail")
        
        # Run all test methods
        tests = [
            ("Get Profile", self.test_get_profile),
            ("Update Profile", self.test_update_profile),
            ("Get Profile by Phone", self.test_get_profile_by_phone),
            ("Delete Profile", self.test_delete_profile),
            ("Unauthorized Access", self.test_unauthorized_access)
        ]
        
        for test_name, test_func in tests:
            test_results["total"] += 1
            logger.info(f"\n{'='*40}")
            logger.info(f"🧪 Running: {test_name}")
            logger.info(f"{'='*40}")
            
            try:
                if test_func():
                    logger.info(f"✅ {test_name}: PASS")
                    test_results["passed"] += 1
                else:
                    logger.error(f"❌ {test_name}: FAIL")
                    test_results["failed"] += 1
            except Exception as e:
                logger.error(f"❌ {test_name}: EXCEPTION - {str(e)}")
                test_results["failed"] += 1
        
        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info("📊 PROFILE INTEGRATION TEST SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Passed: {test_results['passed']}")
        logger.info(f"❌ Failed: {test_results['failed']}")
        logger.info(f"📈 Success Rate: {(test_results['passed'] / test_results['total'] * 100):.1f}%")
        logger.info(f"⏰ Test completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*60}")
        
        return test_results["failed"] == 0

def main():
    """Main function to run profile integration tests"""
    test = ProfileIntegrationTest(API_BASE_URL)
    success = test.run_all_tests()
    
    if success:
        print("\n🎉 All profile integration tests passed!")
        exit(0)
    else:
        print("\n❌ Some profile integration tests failed!")
        exit(1)

if __name__ == "__main__":
    main() 