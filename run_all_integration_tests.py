#!/usr/bin/env python3
"""
Master Integration Test Runner for Anna Akka Platform

This script runs all integration tests for all modules:
- Auth integration tests
- Categories integration tests
- Cart integration tests
- Stores integration tests
- Products integration tests

Usage:
    python run_all_integration_tests.py                    # Run all tests
    python run_all_integration_tests.py --auth-only        # Run only auth tests
    python run_all_integration_tests.py --categories-only  # Run only categories tests
    python run_all_integration_tests.py --cart-only        # Run only cart tests
    python run_all_integration_tests.py --stores-only      # Run only stores tests
    python run_all_integration_tests.py --products-only    # Run only products tests
"""

import subprocess
import sys
import argparse
import time
from datetime import datetime

def run_test_module(module_name, test_file):
    """Run a specific test module"""
    print(f"\n{'='*60}")
    print(f"🚀 Running {module_name.upper()} Integration Tests")
    print(f"{'='*60}")
    
    try:
        start_time = time.time()
        result = subprocess.run([sys.executable, test_file], capture_output=True, text=True)
        end_time = time.time()
        
        print(f"⏱️  {module_name} tests completed in {end_time - start_time:.2f} seconds")
        
        if result.returncode == 0:
            print(f"✅ {module_name} tests PASSED")
            return True
        else:
            print(f"❌ {module_name} tests FAILED")
            print(f"Error output: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {module_name} tests: {str(e)}")
        return False

def main():
    """Main function to run all integration tests"""
    parser = argparse.ArgumentParser(description='Run Anna Akka Platform Integration Tests')
    parser.add_argument('--auth-only', action='store_true', help='Run only auth tests')
    parser.add_argument('--categories-only', action='store_true', help='Run only categories tests')
    parser.add_argument('--cart-only', action='store_true', help='Run only cart tests')
    parser.add_argument('--stores-only', action='store_true', help='Run only stores tests')
    parser.add_argument('--products-only', action='store_true', help='Run only products tests')
    parser.add_argument('--skip-auth', action='store_true', help='Skip auth tests')
    parser.add_argument('--skip-categories', action='store_true', help='Skip categories tests')
    parser.add_argument('--skip-cart', action='store_true', help='Skip cart tests')
    parser.add_argument('--skip-stores', action='store_true', help='Skip stores tests')
    parser.add_argument('--skip-products', action='store_true', help='Skip products tests')
    
    args = parser.parse_args()
    
    # Define test modules
    test_modules = [
        ('auth', 'test_auth_integration.py'),
        ('categories', 'test_categories_integration.py'),
        ('cart', 'test_cart_integration.py'),
        ('stores', 'test_stores_integration.py'),
        ('products', 'test_products_integration.py')
    ]
    
    # Filter modules based on arguments
    if args.auth_only:
        test_modules = [('auth', 'test_auth_integration.py')]
    elif args.categories_only:
        test_modules = [('categories', 'test_categories_integration.py')]
    elif args.cart_only:
        test_modules = [('cart', 'test_cart_integration.py')]
    elif args.stores_only:
        test_modules = [('stores', 'test_stores_integration.py')]
    elif args.products_only:
        test_modules = [('products', 'test_products_integration.py')]
    else:
        # Apply skip filters
        if args.skip_auth:
            test_modules = [m for m in test_modules if m[0] != 'auth']
        if args.skip_categories:
            test_modules = [m for m in test_modules if m[0] != 'categories']
        if args.skip_cart:
            test_modules = [m for m in test_modules if m[0] != 'cart']
        if args.skip_stores:
            test_modules = [m for m in test_modules if m[0] != 'stores']
        if args.skip_products:
            test_modules = [m for m in test_modules if m[0] != 'products']
    
    print("🚀 Anna Akka Platform Integration Test Suite")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print(f"Modules to test: {[m[0] for m in test_modules]}")
    print("=" * 60)
    
    # Track results
    results = {}
    total_start_time = time.time()
    
    # Run each test module
    for module_name, test_file in test_modules:
        print(f"\n📋 Running {module_name} tests...")
        success = run_test_module(module_name, test_file)
        results[module_name] = success
    
    total_end_time = time.time()
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 INTEGRATION TEST SUITE SUMMARY")
    print(f"{'='*60}")
    print(f"⏱️  Total execution time: {total_end_time - total_start_time:.2f} seconds")
    print(f"📦 Modules tested: {len(test_modules)}")
    
    passed = sum(1 for success in results.values() if success)
    failed = len(results) - passed
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if results:
        success_rate = (passed / len(results)) * 100
        print(f"📈 Overall Success Rate: {success_rate:.1f}%")
    
    print("\n📋 Detailed Results:")
    for module_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {module_name.upper()}: {status}")
    
    print(f"{'='*60}")
    
    # Exit with appropriate code
    if failed > 0:
        print("❌ Some tests failed!")
        sys.exit(1)
    else:
        print("✅ All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main() 