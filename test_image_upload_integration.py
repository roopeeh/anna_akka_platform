import os
import requests
import base64
import json
import time
from datetime import datetime
from env_config import get_base_url, get_headers

IMAGE_PATH = r"C:\Users\roope\Downloads\billing_1.png"
BASE_URL = get_base_url()
HEADERS = get_headers()
FOLDER_PATH = "integration-tests/screenshots"

class ImageUploadIntegrationTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    def log_test(self, test_name, status, message="", response_time=None):
        timestamp = datetime.now().strftime("%H:%M:%S")
        timing_info = f" ({response_time:.3f}s)" if response_time else ""
        if status == "PASS":
            print(f"✅ [{timestamp}] {test_name}: PASS{timing_info}")
            self.test_results["passed"] += 1
        else:
            print(f"❌ [{timestamp}] {test_name}: FAIL - {message}{timing_info}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {message}")

    def test_image_upload(self):
        test_name = "POST /images/upload (PNG integration)"
        if not os.path.exists(IMAGE_PATH):
            self.log_test(test_name, "FAIL", f"Image file not found: {IMAGE_PATH}")
            return
        with open(IMAGE_PATH, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        payload = {
            "image": image_data,
            "folder_path": FOLDER_PATH
        }
        endpoint = f"{BASE_URL}/images/upload"
        start_time = time.time()
        try:
            response = self.session.post(endpoint, json=payload)
            response_time = time.time() - start_time
            try:
                data = response.json()
            except Exception:
                self.log_test(test_name, "FAIL", f"Response is not JSON: {response.text}", response_time)
                return
            if response.status_code == 201 and "image_url" in data:
                self.log_test(test_name, "PASS", response_time=response_time)
                print("Uploaded image URL:", data["image_url"])
            else:
                self.log_test(test_name, "FAIL", f"Expected 201 and image_url, got {response.status_code}: {data}", response_time)
        except Exception as e:
            self.log_test(test_name, "FAIL", f"Exception: {str(e)}")

    def print_summary(self):
        print("\n=== Image Upload Integration Test Summary ===")
        print(f"Passed: {self.test_results['passed']}")
        print(f"Failed: {self.test_results['failed']}")
        if self.test_results["errors"]:
            print("Errors:")
            for err in self.test_results["errors"]:
                print(f"  - {err}")


def main():
    print("\n🖼️  Running Image Upload Integration Test\n" + "=" * 50)
    test = ImageUploadIntegrationTest()
    test.test_image_upload()
    test.print_summary()

if __name__ == "__main__":
    main() 