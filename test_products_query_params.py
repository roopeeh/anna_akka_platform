#!/usr/bin/env python3
"""
Simple test for Products API with query parameters
Tests the endpoint: GET /products?store_id={store_id}&available_product_id={available_product_id}
"""

import requests
import json

# Configuration
BASE_URL = "https://z8sre11rwh.execute-api.ap-south-1.amazonaws.com/dev"

# Real data from the database (from the API connectivity test)
REAL_STORE_ID = "cfff75c2-c92d-47f4-b353-5f6e4524a874"
REAL_AVAILABLE_PRODUCT_ID = "09a43be7-d789-450b-b64d-14cdf02902d1"
TEST_USER_ID = "test-user-123"

def test_products_with_query_params():
    """Test GET /products with store_id and available_product_id query parameters"""
    print("🚀 Testing Products API with Query Parameters")
    print("=" * 60)
    
    # Test 1: Get product by store_id and available_product_id
    print("\n🔍 Test 1: Get product by store_id and available_product_id")
    url = f"{BASE_URL}/products"
    params = {
        'store_id': REAL_STORE_ID,
        'available_product_id': REAL_AVAILABLE_PRODUCT_ID,
        'user_id': TEST_USER_ID
    }
    
    print(f"URL: {url}")
    print(f"Parameters: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response:")
            print(json.dumps(data, indent=2))
            
            if 'product' in data:
                product = data['product']
                print(f"\n📋 Product Details:")
                print(f"   - ID: {product.get('id')}")
                print(f"   - Name: {product.get('name')}")
                print(f"   - Store ID: {product.get('store_id')}")
                print(f"   - Available Product ID: {product.get('available_product_id')}")
                print(f"   - Price: {product.get('price')}")
                print(f"   - Stock: {product.get('stock')}")
            else:
                print("⚠️  No product found in response")
        elif response.status_code == 404:
            print("❌ Product not found")
            print(f"Response: {response.text}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

def test_products_without_parameters():
    """Test GET /products without parameters (should return paginated results)"""
    print("\n🔍 Test 2: Get products without parameters")
    url = f"{BASE_URL}/products"
    params = {
        'user_id': TEST_USER_ID
    }
    
    print(f"URL: {url}")
    print(f"Parameters: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response:")
            print(json.dumps(data, indent=2))
            
            if 'products' in data:
                products = data['products']
                print(f"\n📋 Found {len(products)} products")
                for i, product in enumerate(products):
                    print(f"   Product {i+1}: {product.get('name', 'Unknown')} - ID: {product.get('id')}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

def test_products_with_only_store_id():
    """Test GET /products with only store_id parameter"""
    print("\n🔍 Test 3: Get products with only store_id")
    url = f"{BASE_URL}/products"
    params = {
        'store_id': REAL_STORE_ID,
        'user_id': TEST_USER_ID
    }
    
    print(f"URL: {url}")
    print(f"Parameters: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response:")
            print(json.dumps(data, indent=2))
            
            if 'products' in data:
                products = data['products']
                print(f"\n📋 Found {len(products)} products for store {REAL_STORE_ID}")
                for i, product in enumerate(products):
                    print(f"   Product {i+1}: {product.get('name', 'Unknown')} - ID: {product.get('id')}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

def main():
    """Run all tests"""
    test_products_with_query_params()
    test_products_without_parameters()
    test_products_with_only_store_id()
    
    print("\n🎯 Products API Query Parameter Tests Complete!")

if __name__ == "__main__":
    main() 