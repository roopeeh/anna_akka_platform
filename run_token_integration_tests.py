#!/usr/bin/env python3
"""
Main Token Integration Test Runner
Runs all token integration tests and provides comprehensive results.
"""

import subprocess
import sys
import os
import time
from datetime import datetime

class TokenIntegrationTestRunner:
    def __init__(self):
        self.test_files = [
            "test_custom_token_integration.py",
            "test_token_flow_detailed.py", 
            "test_auth_endpoints_comprehensive.py"
        ]
        self.results = {}
        
    def print_header(self):
        """Print test runner header"""
        print("🚀 CUSTOM TOKEN AUTHENTICATION INTEGRATION TESTS")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def print_footer(self):
        """Print test runner footer"""
        print("=" * 80)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def print_success(self, message):
        print(f"✅ {message}")
    
    def print_error(self, message):
        print(f"❌ {message}")
    
    def print_info(self, message):
        print(f"ℹ️  {message}")
    
    def run_single_test(self, test_file):
        """Run a single test file"""
        print(f"\n{'='*60}")
        print(f"Running: {test_file}")
        print(f"{'='*60}")
        
        try:
            # Check if test file exists
            if not os.path.exists(test_file):
                self.print_error(f"Test file not found: {test_file}")
                return False
            
            # Run the test
            start_time = time.time()
            result = subprocess.run([sys.executable, test_file], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=300)  # 5 minute timeout
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Print output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            
            # Check result
            if result.returncode == 0:
                self.print_success(f"{test_file} - PASSED ({duration:.2f}s)")
                return True
            else:
                self.print_error(f"{test_file} - FAILED (exit code: {result.returncode})")
                return False
                
        except subprocess.TimeoutExpired:
            self.print_error(f"{test_file} - TIMEOUT (5 minutes)")
            return False
        except Exception as e:
            self.print_error(f"{test_file} - ERROR: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        self.print_header()
        
        total_tests = len(self.test_files)
        passed_tests = 0
        
        print(f"\nFound {total_tests} test files:")
        for test_file in self.test_files:
            print(f"  - {test_file}")
        
        print(f"\nStarting test execution...")
        
        for test_file in self.test_files:
            if self.run_single_test(test_file):
                passed_tests += 1
                self.results[test_file] = "PASSED"
            else:
                self.results[test_file] = "FAILED"
        
        # Print summary
        self.print_summary(passed_tests, total_tests)
        self.print_footer()
        
        return passed_tests == total_tests
    
    def print_summary(self, passed, total):
        """Print test summary"""
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print(f"\nDetailed Results:")
        for test_file, result in self.results.items():
            status_icon = "✅" if result == "PASSED" else "❌"
            print(f"  {status_icon} {test_file}: {result}")
        
        if passed == total:
            print(f"\n🎉 ALL INTEGRATION TESTS PASSED!")
        else:
            print(f"\n❌ {total - passed} TESTS FAILED!")
    
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("Checking dependencies...")
        
        try:
            import requests
            self.print_success("requests library available")
        except ImportError:
            self.print_error("requests library not found. Please install with: pip install requests")
            return False
        
        return True

def main():
    """Main function"""
    print("🧪 Token Integration Test Runner")
    print("=" * 60)
    
    runner = TokenIntegrationTestRunner()
    
    # Check dependencies
    if not runner.check_dependencies():
        print("\n❌ Dependencies check failed. Please install required packages.")
        sys.exit(1)
    
    # Run tests
    success = runner.run_all_tests()
    
    if success:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME INTEGRATION TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main() 