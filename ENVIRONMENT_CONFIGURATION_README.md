# Environment Configuration for Anna Akka Platform Tests

This document explains how to use the centralized environment configuration system for all integration tests.

## Overview

All test files now use a centralized configuration system through `env_config.py`. This eliminates the need to hardcode API endpoints and test settings in individual test files.

## Files Created

1. **`env_config.py`** - Main configuration module
2. **`env_example.txt`** - Example environment variables
3. **`ENVIRONMENT_CONFIGURATION_README.md`** - This documentation

## How to Use

### Method 1: Environment Variables (Recommended)

Set environment variables in your system or shell:

```bash
# API Endpoints
export API_BASE_URL=https://z8sre11rwh.execute-api.ap-south-1.amazonaws.com/dev
export API_BASE_URL_DEV=https://z8sre11rwh.execute-api.ap-south-1.amazonaws.com/dev
export API_BASE_URL_LOCAL=http://localhost:3000

# Test Configuration
export TEST_PHONE=+919502528182
export TEST_OTP=123456
export USE_REAL_SMS=true
export ACCEPT_TEST_OTP=false

# Timeout Settings
export REQUEST_TIMEOUT=30
export OTP_WAIT_TIME=60

# Test Data
export TEST_USER_NAME="Test User"
export TEST_USER_EMAIL=test@example.com
export TEST_USER_PHONE=+919876543210
```

### Method 2: .env File

1. Copy `env_example.txt` to `.env`
2. Modify the values in `.env` file
3. Load the environment variables in your shell

### Method 3: Direct Import

Import the configuration in your test files:

```python
from env_config import get_base_url, get_headers, get_test_config

# Get the base URL
base_url = get_base_url()

# Get headers
headers = get_headers()

# Get complete test configuration
config = get_test_config()
```

## Updated Test Files

The following test files have been updated to use the centralized configuration:

- `test_config.py` - Now imports from env_config.py
- `test_products_integration.py` - Uses get_base_url() and get_headers()
- `test_stores_integration.py` - Uses get_base_url() and get_headers()
- `test_cart_integration.py` - Uses get_base_url() and get_headers()
- `test_categories_integration.py` - Uses get_base_url() and get_headers()
- `test_orders_integration.py` - Uses get_base_url() and get_headers()
- `test_profile_integration.py` - Uses get_base_url()
- `test_otp_integration.py` - Uses get_base_url() and get_headers()
- `test_phone_otp.py` - Uses get_base_url() and get_headers()
- `test_otp_cognito.py` - Uses get_base_url() and get_headers()
- `test_custom_token_integration.py` - Uses get_base_url()
- `test_safe_token_integration.py` - Uses get_test_config()
- `test_token_flow_detailed.py` - Uses get_base_url()
- `test_complete_user_flow.py` - Uses get_base_url() and get_headers()
- `test_complete_otp_flow.py` - Uses get_base_url() and get_headers()
- `test_auth_integration.py` - Uses get_base_url() and get_headers()
- `test_auth_endpoints_comprehensive.py` - Uses get_base_url()

## Configuration Options

### API Endpoints

- `API_BASE_URL` - Default API endpoint (now set to dev endpoint)
- `API_BASE_URL_DEV` - Development environment endpoint
- `API_BASE_URL_LOCAL` - Local development endpoint

### Test Configuration

- `TEST_PHONE` - Phone number for testing
- `TEST_OTP` - Test OTP code
- `USE_REAL_SMS` - Whether to send real SMS (true/false)
- `ACCEPT_TEST_OTP` - Whether system accepts test OTPs (true/false)

### Timeout Settings

- `REQUEST_TIMEOUT` - Request timeout in seconds
- `OTP_WAIT_TIME` - OTP wait time in seconds

### Test Data

- `TEST_USER_NAME` - Test user name
- `TEST_USER_EMAIL` - Test user email
- `TEST_USER_PHONE` - Test user phone
- `TEST_PRODUCT_NAME` - Test product name
- `TEST_PRODUCT_PRICE` - Test product price
- `TEST_PRODUCT_UNIT` - Test product unit
- `TEST_PRODUCT_STOCK` - Test product stock
- `TEST_STORE_NAME` - Test store name
- `TEST_STORE_ADDRESS` - Test store address
- `TEST_STORE_PHONE` - Test store phone

## Benefits

1. **Centralized Configuration** - All endpoints and settings in one place
2. **Environment Flexibility** - Easy to switch between dev, local, and production
3. **No Hardcoding** - No more hardcoded URLs in test files
4. **Easy Updates** - Change endpoints by updating environment variables
5. **Backward Compatibility** - Existing test files continue to work

## Default Configuration

The default configuration now uses the dev endpoint:
- **Default API URL**: `https://z8sre11rwh.execute-api.ap-south-1.amazonaws.com/dev`
- **Test Phone**: `+919502528182`
- **Test OTP**: `123456`
- **Use Real SMS**: `true`
- **Accept Test OTP**: `false`

## Running Tests

Tests can now be run with the centralized configuration:

```bash
# Run with default configuration
python test_products_integration.py

# Run with custom environment variables
API_BASE_URL=https://your-custom-endpoint.com/dev python test_products_integration.py

# Run with local environment
API_BASE_URL=http://localhost:3000 python test_products_integration.py
```

## Migration from Old System

If you have existing test files that still use hardcoded endpoints, you can update them by:

1. Importing the configuration:
   ```python
   from env_config import get_base_url, get_headers
   ```

2. Replacing hardcoded values:
   ```python
   # Old way
   BASE_URL = "https://old-endpoint.com/dev"
   
   # New way
   BASE_URL = get_base_url()
   ```

## Troubleshooting

### Environment Variables Not Loading

If environment variables are not being loaded, check:
1. Variables are properly set in your shell
2. `.env` file exists and is properly formatted
3. No typos in variable names

### Import Errors

If you get import errors for `env_config.py`:
1. Ensure the file exists in the project root
2. Check that Python can find the module
3. Verify the file has proper permissions

### Configuration Not Updating

If configuration changes are not taking effect:
1. Restart your Python process
2. Check that environment variables are set correctly
3. Verify the configuration is being imported properly

## Future Enhancements

- Support for different configuration profiles (dev, staging, prod)
- Integration with CI/CD pipeline environment variables
- Configuration validation and error handling
- Support for encrypted configuration values 