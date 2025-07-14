#!/usr/bin/env python3
"""
Test script for the Image Upload API
This script demonstrates how to upload images to S3 via the API
"""

import requests
import base64
import json
import os
from pathlib import Path

# Configuration
API_BASE_URL = "https://your-api-gateway-url.ap-south-1.amazonaws.com/dev"  # Replace with your actual API URL
IMAGE_UPLOAD_ENDPOINT = f"{API_BASE_URL}/images/upload"

def encode_image_to_base64(image_path):
    """Encode an image file to base64 string"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

def upload_image(image_path, folder_path):
    """Upload an image to S3 via the API"""
    
    # Encode image to base64
    image_data = encode_image_to_base64(image_path)
    if not image_data:
        return None
    
    # Prepare request payload
    payload = {
        "image": image_data,
        "folder_path": folder_path
    }
    
    # Make API request
    try:
        response = requests.post(
            IMAGE_UPLOAD_ENDPOINT,
            json=payload,
            headers={
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Image uploaded successfully!")
            print(f"📁 Folder: {result.get('folder_path')}")
            print(f"🔗 Image URL: {result.get('image_url')}")
            return result.get('image_url')
        else:
            print(f"❌ Upload failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error making API request: {e}")
        return None

def test_image_upload():
    """Test the image upload functionality"""
    
    print("🚀 Testing Image Upload API")
    print("=" * 50)
    
    # Test with different folder paths
    test_cases = [
        {
            "image_path": "test_images/product1.jpg",  # Replace with actual image path
            "folder_path": "products"
        },
        {
            "image_path": "test_images/store_logo.png",  # Replace with actual image path
            "folder_path": "stores/logos"
        },
        {
            "image_path": "test_images/category_icon.gif",  # Replace with actual image path
            "folder_path": "categories/icons"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📸 Test Case {i}: Uploading to {test_case['folder_path']}")
        print("-" * 40)
        
        # Check if test image exists
        if not os.path.exists(test_case['image_path']):
            print(f"⚠️  Test image not found: {test_case['image_path']}")
            print("   Please create a test image or update the path")
            continue
        
        # Upload image
        image_url = upload_image(test_case['image_path'], test_case['folder_path'])
        
        if image_url:
            print(f"✅ Test case {i} passed!")
        else:
            print(f"❌ Test case {i} failed!")

def create_test_image():
    """Create a simple test image for testing"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple test image
        img = Image.new('RGB', (300, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add some text
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 80), "Test Image", fill='black', font=font)
        draw.text((50, 110), "For API Testing", fill='gray', font=font)
        
        # Create test_images directory if it doesn't exist
        os.makedirs("test_images", exist_ok=True)
        
        # Save the image
        img.save("test_images/test_product.jpg")
        print("✅ Created test image: test_images/test_product.jpg")
        
        return "test_images/test_product.jpg"
        
    except ImportError:
        print("⚠️  PIL not available. Please install Pillow: pip install Pillow")
        return None
    except Exception as e:
        print(f"❌ Error creating test image: {e}")
        return None

if __name__ == "__main__":
    print("🖼️  Image Upload API Test Script")
    print("=" * 50)
    
    # Check if test images exist, create one if not
    if not os.path.exists("test_images/test_product.jpg"):
        print("📸 Creating test image...")
        test_image_path = create_test_image()
        if test_image_path:
            # Test with the created image
            print("\n🧪 Testing with created image...")
            upload_image(test_image_path, "test/products")
    else:
        # Run the full test suite
        test_image_upload()
    
    print("\n" + "=" * 50)
    print("📋 Usage Instructions:")
    print("1. Update API_BASE_URL with your actual API Gateway URL")
    print("2. Place test images in the test_images/ directory")
    print("3. Run the script to test image uploads")
    print("4. Use the returned image URLs in your product data")
    
    print("\n📝 Example API Request:")
    print("POST /images/upload")
    print("Content-Type: application/json")
    print(json.dumps({
        "image": "base64_encoded_image_data",
        "folder_path": "products"
    }, indent=2))
    
    print("\n📝 Example API Response:")
    print(json.dumps({
        "message": "Image uploaded successfully",
        "image_url": "https://anna-akka-platform-dev-images.s3.ap-south-1.amazonaws.com/products/20231201_143022_abc12345.jpg",
        "folder_path": "products"
    }, indent=2)) 