#!/usr/bin/env python3
"""
Environment Configuration for Anna Akka Platform Tests

This module provides centralized configuration for all API endpoints and test settings.
All test files should import and use this configuration instead of hardcoding values.
"""

import os
from typing import Dict, Any

class EnvConfig:
    """Environment configuration for Anna Akka Platform tests"""
    
    def __init__(self):
        # API Endpoints - Priority: Environment Variable > Default
        self.api_base_url = os.environ.get(
            'API_BASE_URL', 
            'https://z8sre11rwh.execute-api.ap-south-1.amazonaws.com/dev'
        )
        self.api_base_url_dev = os.environ.get(
            'API_BASE_URL_DEV', 
            'https://z8sre11rwh.execute-api.ap-south-1.amazonaws.com/dev'
        )
        self.api_base_url_local = os.environ.get(
            'API_BASE_URL_LOCAL', 
            'http://localhost:3000'
        )
        
        # Test Configuration
        self.test_phone = os.environ.get('TEST_PHONE', '+919502528182')
        self.test_otp = os.environ.get('TEST_OTP', '123456')
        self.use_real_sms = os.environ.get('USE_REAL_SMS', 'true').lower() == 'true'
        self.accept_test_otp = os.environ.get('ACCEPT_TEST_OTP', 'false').lower() == 'true'
        
        # Timeout Settings
        self.request_timeout = int(os.environ.get('REQUEST_TIMEOUT', '30'))
        self.otp_wait_time = int(os.environ.get('OTP_WAIT_TIME', '60'))
        
        # Test Data
        self.test_user = {
            'name': os.environ.get('TEST_USER_NAME', 'Test User'),
            'email': os.environ.get('TEST_USER_EMAIL', 'test@example.com'),
            'phone': os.environ.get('TEST_USER_PHONE', '+919876543210')
        }
        
        # Test Product Data
        self.test_product = {
            'name': os.environ.get('TEST_PRODUCT_NAME', 'Test Product'),
            'price': float(os.environ.get('TEST_PRODUCT_PRICE', '25.50')),
            'unit': os.environ.get('TEST_PRODUCT_UNIT', 'piece'),
            'stock': int(os.environ.get('TEST_PRODUCT_STOCK', '10'))
        }
        
        # Test Store Data
        self.test_store = {
            'name': os.environ.get('TEST_STORE_NAME', 'Test Store'),
            'address': os.environ.get('TEST_STORE_ADDRESS', '123 Test Street'),
            'phone': os.environ.get('TEST_STORE_PHONE', '+919876543210')
        }
        
        # Headers
        self.headers = {
            'Content-Type': os.environ.get('CONTENT_TYPE', 'application/json')
        }
    
    def get_api_url(self, environment: str = 'default') -> str:
        """Get API URL for specified environment"""
        if environment == 'dev':
            return self.api_base_url_dev
        elif environment == 'local':
            return self.api_base_url_local
        else:
            return self.api_base_url
    
    def get_test_config(self) -> Dict[str, Any]:
        """Get complete test configuration dictionary"""
        return {
            'base_url': self.api_base_url,
            'test_phone': self.test_phone,
            'test_otp': self.test_otp,
            'use_real_sms': self.use_real_sms,
            'accept_test_otp': self.accept_test_otp,
            'request_timeout': self.request_timeout,
            'otp_wait_time': self.otp_wait_time,
            'test_user': self.test_user,
            'test_product': self.test_product,
            'test_store': self.test_store,
            'headers': self.headers
        }
    
    def print_config(self):
        """Print current configuration"""
        print("🔧 Environment Configuration")
        print("=" * 50)
        print(f"API Base URL: {self.api_base_url}")
        print(f"API Base URL (Dev): {self.api_base_url_dev}")
        print(f"API Base URL (Local): {self.api_base_url_local}")
        print(f"Test Phone: {self.test_phone}")
        print(f"Use Real SMS: {self.use_real_sms}")
        print(f"Accept Test OTP: {self.accept_test_otp}")
        print(f"Request Timeout: {self.request_timeout}s")
        print(f"OTP Wait Time: {self.otp_wait_time}s")
        print("=" * 50)

# Global instance
config = EnvConfig()

def get_config() -> EnvConfig:
    """Get the global configuration instance"""
    return config

def get_api_url(environment: str = 'default') -> str:
    """Get API URL for specified environment"""
    return config.get_api_url(environment)

def get_test_config() -> Dict[str, Any]:
    """Get complete test configuration dictionary"""
    return config.get_test_config()

def print_config():
    """Print current configuration"""
    config.print_config()

# Backward compatibility functions
def get_base_url() -> str:
    """Get the default base URL (backward compatibility)"""
    return config.api_base_url

def get_headers() -> Dict[str, str]:
    """Get default headers (backward compatibility)"""
    return config.headers

if __name__ == "__main__":
    print_config() 