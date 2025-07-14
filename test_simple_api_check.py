#!/usr/bin/env python3
"""
Simple API connectivity test to check if the API is accessible
"""

import requests
import json

# Configuration
BASE_URL = "https://z8sre11rwh.execute-api.ap-south-1.amazonaws.com/dev"

def test_api_connectivity():
    """Test basic API connectivity"""
    print("🔍 Testing API connectivity...")
    
    # Test a simple endpoint that should exist
    test_endpoints = [
        "/categories",
        "/available-products",
        "/stores",
        "/products"
    ]
    
    for endpoint in test_endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        try:
            url = f"{BASE_URL}{endpoint}"
            print(f"URL: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Response: {json.dumps(data, indent=2)[:500]}...")
                except json.JSONDecodeError:
                    print(f"Raw Response: {response.text[:500]}...")
            else:
                print(f"Error Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")

def test_specific_products_endpoint():
    """Test the specific products endpoint we're interested in"""
    print("\n🔍 Testing specific products endpoint...")
    
    test_cases = [
        {
            'store_id': 'test-store-123',
            'available_product_id': 'b9238c4d-77e1-4585-b086-11af2dabdb59',
            'description': 'Test case 1'
        },
        {
            'store_id': 'store-123',
            'available_product_id': 'b9238c4d-77e1-4585-b086-11af2dabdb59',
            'description': 'Test case 2'
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['description']}")
        endpoint = f"/stores/{test_case['store_id']}/products/available/{test_case['available_product_id']}"
        
        try:
            url = f"{BASE_URL}{endpoint}"
            print(f"URL: {url}")
            
            headers = {
                'X-User-ID': 'test-user-123',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Success Response: {json.dumps(data, indent=2)}")
                except json.JSONDecodeError:
                    print(f"Raw Response: {response.text}")
            elif response.status_code == 404:
                try:
                    data = response.json()
                    print(f"Not Found Response: {json.dumps(data, indent=2)}")
                except json.JSONDecodeError:
                    print(f"Raw Response: {response.text}")
            else:
                print(f"Error Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting API Connectivity Tests")
    print("=" * 60)
    
    test_api_connectivity()
    test_specific_products_endpoint()
    
    print("\n🎯 API Connectivity Tests Complete!") 