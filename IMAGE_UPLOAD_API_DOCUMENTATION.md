# Image Upload API Documentation

## Overview

The Image Upload API provides functionality to upload images to S3 storage and return public URLs for use in products and other services. The API accepts base64-encoded images and organizes them by folder paths.

## API Endpoint

### Upload Image
- **URL**: `POST /images/upload`
- **Description**: Upload an image to S3 and get a public URL
- **Content-Type**: `application/json`

## Request Format

### Request Body
```json
{
  "image": "base64_encoded_image_data",
  "folder_path": "products/category1"
}
```

### Parameters
- `image` (string, required): Base64-encoded image data
- `folder_path` (string, required): Folder path where the image will be stored in S3

### Supported Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

### File Size Limits
- Maximum file size: 5MB

## Response Format

### Success Response (201 Created)
```json
{
  "message": "Image uploaded successfully",
  "image_url": "https://anna-akka-platform-dev-images.s3.ap-south-1.amazonaws.com/products/category1/20231201_143022_abc12345.jpg",
  "folder_path": "products/category1"
}
```

### Error Responses

#### 400 Bad Request - Validation Error
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Request body is required"
}
```

#### 405 Method Not Allowed
```json
{
  "error": "METHOD_NOT_ALLOWED",
  "message": "Only POST method is allowed"
}
```

#### 500 Internal Server Error
```json
{
  "error": "INTERNAL_ERROR",
  "message": "Internal server error"
}
```

## Usage Examples

### JavaScript/Node.js
```javascript
const axios = require('axios');
const fs = require('fs');

async function uploadImage(imagePath, folderPath) {
  try {
    // Read and encode image
    const imageBuffer = fs.readFileSync(imagePath);
    const base64Image = imageBuffer.toString('base64');
    
    // Make API request
    const response = await axios.post('https://your-api-gateway-url.ap-south-1.amazonaws.com/dev/images/upload', {
      image: base64Image,
      folder_path: folderPath
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log('Image uploaded successfully:', response.data.image_url);
    return response.data.image_url;
  } catch (error) {
    console.error('Upload failed:', error.response?.data || error.message);
  }
}

// Example usage
uploadImage('./product-image.jpg', 'products/electronics');
```

### Python
```python
import requests
import base64

def upload_image(image_path, folder_path):
    try:
        # Read and encode image
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Make API request
        response = requests.post(
            'https://your-api-gateway-url.ap-south-1.amazonaws.com/dev/images/upload',
            json={
                'image': image_data,
                'folder_path': folder_path
            },
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"Image uploaded successfully: {result['image_url']}")
            return result['image_url']
        else:
            print(f"Upload failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

# Example usage
upload_image('product-image.jpg', 'products/electronics')
```

### cURL
```bash
# Encode image to base64
base64_image=$(base64 -i product-image.jpg)

# Upload image
curl -X POST \
  https://your-api-gateway-url.ap-south-1.amazonaws.com/dev/images/upload \
  -H 'Content-Type: application/json' \
  -d "{
    \"image\": \"$base64_image\",
    \"folder_path\": \"products/electronics\"
  }"
```

## Folder Structure Examples

### Products
```
products/
├── electronics/
│   ├── phones/
│   ├── laptops/
│   └── accessories/
├── clothing/
│   ├── shirts/
│   ├── pants/
│   └── shoes/
└── food/
    ├── fast-food/
    ├── desserts/
    └── beverages/
```

### Store Images
```
stores/
├── store-logos/
├── store-banners/
└── store-interiors/
```

### User Profile Images
```
profiles/
├── avatars/
└── cover-photos/
```

## Integration with Products

When creating or updating products, you can use the returned image URL:

```json
{
  "name": "iPhone 15 Pro",
  "description": "Latest iPhone model",
  "price": 999.99,
  "image_url": "https://anna-akka-platform-dev-images.s3.ap-south-1.amazonaws.com/products/electronics/phones/20231201_143022_abc12345.jpg",
  "category_id": "electronics",
  "store_id": "store-123"
}
```

## Security Considerations

1. **File Size Limits**: Images are limited to 5MB to prevent abuse
2. **File Type Validation**: Only supported image formats are accepted
3. **Public Access**: Images are stored with public read access for easy retrieval
4. **Unique Naming**: Files are automatically renamed with timestamps and UUIDs to prevent conflicts

## Error Handling

### Common Error Scenarios

1. **Missing Image Data**
   ```json
   {
     "error": "VALIDATION_ERROR",
     "message": "Image data is required"
   }
   ```

2. **Missing Folder Path**
   ```json
   {
     "error": "VALIDATION_ERROR",
     "message": "Folder path is required"
   }
   ```

3. **Invalid Base64 Data**
   ```json
   {
     "error": "VALIDATION_ERROR",
     "message": "Invalid base64 image data"
   }
   ```

4. **File Too Large**
   ```json
   {
     "error": "VALIDATION_ERROR",
     "message": "File size exceeds maximum limit of 5MB"
   }
   ```

## Infrastructure Components

### S3 Bucket
- **Name**: `anna-akka-platform-{environment}-images`
- **Region**: `ap-south-1`
- **Access**: Public read access
- **CORS**: Configured for cross-origin requests

### Lambda Function
- **Name**: `anna-akka-platform-image_upload`
- **Runtime**: Python 3.9
- **Handler**: `handler.handler`
- **Timeout**: 30 seconds
- **Memory**: 512 MB

### API Gateway
- **Endpoint**: `POST /images/upload`
- **Integration**: Lambda proxy integration
- **CORS**: Enabled for all origins

## Testing

Use the provided test script `test_image_upload.py` to test the image upload functionality:

```bash
python test_image_upload.py
```

The test script will:
1. Create test images if they don't exist
2. Upload images to different folder paths
3. Display the returned image URLs
4. Provide usage examples

## Deployment

The image upload functionality is automatically deployed with the main infrastructure using Pulumi. The deployment includes:

1. S3 bucket with public read access
2. Lambda function with S3 permissions
3. API Gateway integration
4. All necessary IAM policies and roles

To deploy:

```bash
pulumi up
```

## Monitoring and Logs

### CloudWatch Logs
- **Log Group**: `/aws/lambda/anna-akka-platform-image_upload`
- **Log Level**: INFO
- **Retention**: 14 days

### Key Metrics to Monitor
- Upload success rate
- File size distribution
- Error rates by type
- Lambda execution duration
- S3 storage usage

## Cost Considerations

### S3 Storage Costs
- Standard storage: $0.023 per GB per month
- Data transfer: $0.09 per GB (outbound)

### Lambda Costs
- Request count: $0.20 per 1M requests
- Compute time: $0.0000166667 per GB-second

### API Gateway Costs
- Request count: $3.50 per 1M requests
- Data transfer: $0.09 per GB

## Best Practices

1. **Image Optimization**: Compress images before upload to reduce storage costs
2. **Folder Organization**: Use consistent folder naming conventions
3. **Error Handling**: Always handle upload errors gracefully in your application
4. **Caching**: Consider implementing client-side caching for frequently accessed images
5. **Monitoring**: Set up alerts for upload failures and storage usage 