# Configuration file for Mock Data Population Script

# API Configuration
API_BASE_URL = "https://your-api-gateway-url/dev"  # Update with your actual API Gateway URL

# Firebase Authentication
FIREBASE_TOKEN = "your-firebase-jwt-token"  # Update with your Firebase JWT token

# Data Population Settings
CREATE_ORDERS = False  # Set to True if you want to create mock orders
DELAY_BETWEEN_REQUESTS = 0.1  # Delay in seconds between API requests

# Product Categories to Create
CATEGORIES = [
    {"name": "Rice & More", "id": "1"},
    {"name": "Household Essentials", "id": "2"},
    {"name": "Personal Care", "id": "3"},
    {"name": "Snacks & Beverages", "id": "4"}
]

# Store Information
STORES = [
    {
        "name": "Fresh Market Grocery",
        "address": "123 Main Street, Bangalore, Karnataka 560001",
        "phone": "+91 98765 43210",
        "delivery_time": "30-45 min"
    },
    {
        "name": "Organic Valley Store", 
        "address": "456 Park Avenue, Mumbai, Maharashtra 400001",
        "phone": "+91 87654 32109",
        "delivery_time": "25-40 min"
    },
    {
        "name": "City Fresh Mart",
        "address": "789 Lake Road, Delhi, Delhi 110001", 
        "phone": "+91 76543 21098",
        "delivery_time": "35-50 min"
    },
    {
        "name": "Green Grocers",
        "address": "321 Garden Street, Chennai, Tamil Nadu 600001",
        "phone": "+91 65432 10987", 
        "delivery_time": "20-35 min"
    },
    {
        "name": "Farm Fresh Express",
        "address": "654 Farm Road, Hyderabad, Telangana 500001",
        "phone": "+91 54321 09876",
        "delivery_time": "40-55 min"
    }
]

# Customer Information for Orders
CUSTOMERS = [
    {
        "id": "customer-1",
        "name": "John Doe", 
        "address": "123 Main St, Bangalore"
    },
    {
        "id": "customer-2",
        "name": "Jane Smith",
        "address": "456 Oak Ave, Mumbai" 
    },
    {
        "id": "customer-3",
        "name": "Bob Johnson",
        "address": "789 Pine Rd, Delhi"
    }
] 