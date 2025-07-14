#!/usr/bin/env python3
"""
Example script demonstrating how to use the Image Upload API
This script shows how to upload images and use the returned URLs in product creation
"""

import requests
import base64
import json
import os
from pathlib import Path

# Configuration - Update these with your actual API Gateway URL
API_BASE_URL = "https://your-api-gateway-url.ap-south-1.amazonaws.com/dev"
IMAGE_UPLOAD_ENDPOINT = f"{API_BASE_URL}/images/upload"

def encode_image_to_base64(image_path):
    """Encode an image file to base64 string"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        print(f"❌ Error encoding image: {e}")
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

def create_product_with_image(product_data, image_path, folder_path):
    """Create a product with an uploaded image"""
    
    print(f"🖼️  Uploading image for product: {product_data.get('name', 'Unknown')}")
    
    # Upload the image
    image_url = upload_image(image_path, folder_path)
    
    if not image_url:
        print("❌ Failed to upload image, cannot create product")
        return None
    
    # Add the image URL to the product data
    product_data['image_url'] = image_url
    
    print(f"📦 Product data with image:")
    print(json.dumps(product_data, indent=2))
    
    return product_data

def main():
    """Main function demonstrating image upload usage"""
    
    print("🖼️  Image Upload API Example")
    print("=" * 50)
    
    # Example 1: Upload a product image
    print("\n📸 Example 1: Uploading a product image")
    print("-" * 40)
    
    # Create a test image if it doesn't exist
    test_image_path = "test_product_image.jpg"
    if not os.path.exists(test_image_path):
        print(f"📸 Creating test image: {test_image_path}")
        # Create a simple test image (you would normally have real images)
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (300, 200), color='lightblue')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Test Product Image", fill='black')
        img.save(test_image_path)
    
    # Upload the image
    image_url = upload_image(test_image_path, "products/electronics/phones")
    
    if image_url:
        # Example product data with the uploaded image
        product_data = {
            "name": "iPhone 15 Pro",
            "description": "Latest iPhone model with advanced features",
            "price": 999.99,
            "category_id": "electronics",
            "store_id": "store-123",
            "image_url": image_url,
            "stock": 10,
            "unit": "piece"
        }
        
        print(f"\n📦 Product data with uploaded image:")
        print(json.dumps(product_data, indent=2))
    
    # Example 2: Upload multiple images for different categories
    print("\n📸 Example 2: Uploading multiple images")
    print("-" * 40)
    
    categories = [
        ("products/electronics/laptops", "laptop_image.jpg"),
        ("products/clothing/shirts", "shirt_image.jpg"),
        ("products/food/fast-food", "food_image.jpg"),
        ("stores/store-logos", "store_logo.jpg"),
        ("profiles/avatars", "avatar_image.jpg")
    ]
    
    uploaded_images = []
    
    for folder_path, image_name in categories:
        if os.path.exists(image_name):
            print(f"\n📤 Uploading {image_name} to {folder_path}")
            image_url = upload_image(image_name, folder_path)
            if image_url:
                uploaded_images.append({
                    "folder": folder_path,
                    "filename": image_name,
                    "url": image_url
                })
    
    if uploaded_images:
        print(f"\n✅ Successfully uploaded {len(uploaded_images)} images:")
        for img in uploaded_images:
            print(f"  📁 {img['folder']}/{img['filename']}")
            print(f"  🔗 {img['url']}")
    
    # Example 3: Error handling
    print("\n❌ Example 3: Error handling")
    print("-" * 40)
    
    # Try to upload without image data
    try:
        response = requests.post(
            IMAGE_UPLOAD_ENDPOINT,
            json={"folder_path": "test"},
            headers={"Content-Type": "application/json"}
        )
        print(f"❌ Expected error response: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📋 Usage Instructions:")
    print("1. Update API_BASE_URL with your actual API Gateway URL")
    print("2. Place your images in the same directory as this script")
    print("3. Run the script to test image uploads")
    print("4. Use the returned image URLs in your product data")
    
    print("\n📝 Example API Request:")
    print("POST /images/upload")
    print("Content-Type: application/json")
    print(json.dumps({
        "image": "base64_encoded_image_data",
        "folder_path": "products/electronics"
    }, indent=2))

if __name__ == "__main__":
    main() 