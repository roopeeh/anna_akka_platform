# Image Upload API – Frontend Integration Guide

This guide explains how to use the `/images/upload` API endpoint from a web frontend (React, Angular, Vue, etc.).

---

## 1. API Endpoint

- **URL:** `POST /images/upload`
- **Full Example:** `https://your-api-gateway-url/images/upload`
- **Content-Type:** `application/json`

---

## 2. Request Format

Send a JSON body with two fields:
- `image`: The image file as a base64-encoded string (no data URL prefix, just the base64 data)
- `folder_path`: The folder path in S3 where the image should be stored (e.g., `products/electronics`)

**Example Request Body:**
```json
{
  "image": "<base64 string>",
  "folder_path": "products/electronics"
}
```

---

## 3. How to Use in the Frontend (React Example)

### **Step 1: Let the user pick a file**
```jsx
<input type="file" accept="image/*" onChange={handleFileUpload} />
```

### **Step 2: Convert the file to base64 and send to API**
```javascript
function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    // Remove the data:image/png;base64, part
    const base64String = e.target.result.split(',')[1];
    fetch('https://your-api-gateway-url/images/upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image: base64String,
        folder_path: 'products/electronics' // or any folder you want
      })
    })
    .then(res => res.json())
    .then(data => {
      console.log('Image URL:', data.image_url);
      // Use the image URL in your app (e.g., save to product, show preview, etc.)
    });
  };
  reader.readAsDataURL(file);
}
```

---

## 4. Example Success Response
```json
{
  "message": "Image uploaded successfully",
  "image_url": "https://anna-akka-platform-dev-images.s3.ap-south-1.amazonaws.com/products/electronics/20231201_143022_abc12345.jpg",
  "folder_path": "products/electronics"
}
```

---

## 5. Error Responses
- **400 Bad Request:**
  ```json
  { "error": "VALIDATION_ERROR", "message": "Request body is required" }
  ```
- **405 Method Not Allowed:**
  ```json
  { "error": "METHOD_NOT_ALLOWED", "message": "Only POST method is allowed" }
  ```
- **500 Internal Server Error:**
  ```json
  { "error": "INTERNAL_ERROR", "message": "Internal server error" }
  ```

---

## 6. Best Practices
- **Limit file size**: The API supports up to 5MB per image.
- **Supported formats**: JPEG, PNG, GIF, WebP.
- **No data URL prefix**: Only send the base64 data, not the `data:image/png;base64,` part.
- **Show upload progress**: For large files, consider showing a progress bar.
- **Use the returned URL**: Save the `image_url` in your product/user data for later display.

---

## 7. Security & Performance Notes
- **Base64 increases file size by ~33%**. For very large images or high-frequency uploads, consider using S3 pre-signed URLs instead.
- **This API is ideal for product images, profile pictures, and similar use cases.**

---

## 8. Example: Full Upload Flow
```jsx
<input type="file" accept="image/*" onChange={handleFileUpload} />

function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    const base64String = e.target.result.split(',')[1];
    fetch('https://your-api-gateway-url/images/upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image: base64String,
        folder_path: 'products/electronics'
      })
    })
    .then(res => res.json())
    .then(data => {
      alert('Image uploaded! URL: ' + data.image_url);
    });
  };
  reader.readAsDataURL(file);
}
```

---

## 9. Contact
If you have questions, contact the backend team or check the main API documentation for more details. 