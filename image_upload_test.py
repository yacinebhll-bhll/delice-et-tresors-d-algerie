#!/usr/bin/env python3
"""
Focused Image Upload Testing for Soumam Heritage CMS
Tests the image upload functionality comprehensively
"""

import requests
import sys
import json
import os
import io
from datetime import datetime
from PIL import Image

class ImageUploadTester:
    def __init__(self, base_url="https://api-fix-preview-2.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.uploaded_files = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")

    def admin_login(self):
        """Login with admin credentials"""
        print("🔐 Testing Admin Authentication...")
        
        admin_credentials = {
            "email": "admin.soumam@gmail.com",
            "password": "soumam2024"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=admin_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.admin_token = data['access_token']
                    self.log_test("Admin Login", True, f"Token: {self.admin_token[:20]}...")
                    return True
                else:
                    self.log_test("Admin Login", False, "No access token in response")
            else:
                self.log_test("Admin Login", False, f"Status: {response.status_code}, Error: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Login", False, f"Exception: {str(e)}")
        
        return False

    def create_test_image(self, format='JPEG', size=(100, 100), color='red'):
        """Create a test image in memory"""
        img = Image.new('RGB', size, color=color)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format)
        img_bytes.seek(0)
        return img_bytes

    def create_large_image(self, size_mb=11):
        """Create a large image for size testing"""
        import random
        
        # Create a large image with random pixels to prevent compression
        side_length = 3000  # Should create ~27MB PNG
        
        # Create image with random pixels
        pixels = []
        for i in range(side_length * side_length):
            pixels.append((
                random.randint(0, 255),
                random.randint(0, 255), 
                random.randint(0, 255)
            ))
        
        img = Image.new('RGB', (side_length, side_length))
        img.putdata(pixels)
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')  # PNG to maintain size
        img_bytes.seek(0)
        return img_bytes

    def test_successful_upload(self):
        """Test successful JPEG upload"""
        print("\n📤 Testing Successful Image Upload...")
        
        if not self.admin_token:
            self.log_test("JPEG Upload", False, "No admin token available")
            return False
        
        test_image = self.create_test_image('JPEG')
        files = {'file': ('test_image.jpg', test_image, 'image/jpeg')}
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        try:
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                required_keys = ['success', 'filename', 'url', 'size']
                
                if all(key in data for key in required_keys):
                    self.uploaded_files.append(data['filename'])
                    self.log_test("JPEG Upload", True, 
                                f"File: {data['filename']}, Size: {data['size']} bytes, URL: {data['url']}")
                    return True
                else:
                    self.log_test("JPEG Upload", False, f"Missing keys in response: {list(data.keys())}")
            else:
                self.log_test("JPEG Upload", False, f"Status: {response.status_code}, Error: {response.text}")
                
        except Exception as e:
            self.log_test("JPEG Upload", False, f"Exception: {str(e)}")
        
        return False

    def test_png_upload(self):
        """Test PNG upload"""
        print("\n📤 Testing PNG Upload...")
        
        if not self.admin_token:
            self.log_test("PNG Upload", False, "No admin token available")
            return False
        
        test_image = self.create_test_image('PNG', color='green')
        files = {'file': ('test_image.png', test_image, 'image/png')}
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        try:
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'filename' in data:
                    self.uploaded_files.append(data['filename'])
                    self.log_test("PNG Upload", True, f"File: {data['filename']}")
                    return True
                else:
                    self.log_test("PNG Upload", False, "No filename in response")
            else:
                self.log_test("PNG Upload", False, f"Status: {response.status_code}, Error: {response.text}")
                
        except Exception as e:
            self.log_test("PNG Upload", False, f"Exception: {str(e)}")
        
        return False

    def test_file_size_validation(self):
        """Test file size validation (>10MB should fail)"""
        print("\n📏 Testing File Size Validation...")
        
        if not self.admin_token:
            self.log_test("Size Validation", False, "No admin token available")
            return False
        
        # Create a large image (>10MB)
        large_image = self.create_large_image(11)  # 11MB
        files = {'file': ('large_image.jpg', large_image, 'image/jpeg')}
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        try:
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                headers=headers,
                timeout=30  # Longer timeout for large file
            )
            
            if response.status_code == 400:
                data = response.json()
                if 'detail' in data and '10MB' in data['detail']:
                    self.log_test("Size Validation", True, "Correctly rejected large file")
                    return True
                else:
                    self.log_test("Size Validation", False, f"Wrong error message: {data}")
            else:
                self.log_test("Size Validation", False, f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Size Validation", False, f"Exception: {str(e)}")
        
        return False

    def test_file_type_validation(self):
        """Test file type validation"""
        print("\n📄 Testing File Type Validation...")
        
        if not self.admin_token:
            self.log_test("Type Validation", False, "No admin token available")
            return False
        
        # Create a fake text file
        fake_file = io.BytesIO(b"This is not an image file")
        files = {'file': ('fake.txt', fake_file, 'text/plain')}
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        try:
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 400:
                data = response.json()
                if 'detail' in data and 'Invalid file type' in data['detail']:
                    self.log_test("Type Validation", True, "Correctly rejected non-image file")
                    return True
                else:
                    self.log_test("Type Validation", False, f"Wrong error message: {data}")
            else:
                self.log_test("Type Validation", False, f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Type Validation", False, f"Exception: {str(e)}")
        
        return False

    def test_unauthorized_upload(self):
        """Test upload without authentication"""
        print("\n🚫 Testing Unauthorized Upload...")
        
        test_image = self.create_test_image('JPEG')
        files = {'file': ('test_image.jpg', test_image, 'image/jpeg')}
        
        try:
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                timeout=10
            )
            
            if response.status_code in [401, 403]:
                self.log_test("Unauthorized Upload", True, f"Correctly rejected (Status: {response.status_code})")
                return True
            else:
                self.log_test("Unauthorized Upload", False, f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Unauthorized Upload", False, f"Exception: {str(e)}")
        
        return False

    def test_static_file_serving(self):
        """Test that uploaded files are accessible"""
        print("\n🌐 Testing Static File Serving...")
        
        if not self.uploaded_files:
            self.log_test("Static File Serving", False, "No uploaded files to test")
            return False
        
        filename = self.uploaded_files[0]
        static_url = f"https://api-fix-preview-2.preview.emergentagent.com/api/uploads/{filename}"
        
        try:
            response = requests.get(static_url, timeout=10)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type.lower():
                    self.log_test("Static File Serving", True, 
                                f"File accessible, Content-Type: {content_type}")
                    return True
                else:
                    self.log_test("Static File Serving", False, 
                                f"File accessible but wrong content-type: {content_type}")
            else:
                self.log_test("Static File Serving", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Static File Serving", False, f"Exception: {str(e)}")
        
        return False

    def test_image_deletion(self):
        """Test image deletion"""
        print("\n🗑️  Testing Image Deletion...")
        
        if not self.admin_token or not self.uploaded_files:
            self.log_test("Image Deletion", False, "No admin token or uploaded files")
            return False
        
        filename = self.uploaded_files[0]
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        try:
            response = requests.delete(
                f"{self.base_url}/upload/{filename}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.uploaded_files.remove(filename)
                    self.log_test("Image Deletion", True, f"Successfully deleted {filename}")
                    
                    # Verify file is no longer accessible
                    static_url = f"https://api-fix-preview-2.preview.emergentagent.com/api/uploads/{filename}"
                    verify_response = requests.get(static_url, timeout=10)
                    if verify_response.status_code == 404:
                        print("   ✅ File confirmed deleted from static serving")
                    else:
                        print(f"   ⚠️ File still accessible (Status: {verify_response.status_code})")
                    
                    return True
                else:
                    self.log_test("Image Deletion", False, "Success flag not set in response")
            else:
                self.log_test("Image Deletion", False, f"Status: {response.status_code}, Error: {response.text}")
                
        except Exception as e:
            self.log_test("Image Deletion", False, f"Exception: {str(e)}")
        
        return False

    def test_delete_nonexistent(self):
        """Test deleting non-existent file"""
        print("\n🚫 Testing Delete Non-existent File...")
        
        if not self.admin_token:
            self.log_test("Delete Non-existent", False, "No admin token available")
            return False
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        try:
            response = requests.delete(
                f"{self.base_url}/upload/nonexistent-file.jpg",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 404:
                self.log_test("Delete Non-existent", True, "Correctly returned 404")
                return True
            else:
                self.log_test("Delete Non-existent", False, f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Delete Non-existent", False, f"Exception: {str(e)}")
        
        return False

    def test_admin_stats(self):
        """Test admin stats endpoint"""
        print("\n📊 Testing Admin Stats...")
        
        if not self.admin_token:
            self.log_test("Admin Stats", False, "No admin token available")
            return False
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        try:
            response = requests.get(
                f"{self.base_url}/admin/stats",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                expected_keys = ['total_users', 'total_recipes', 'total_products', 
                               'total_historical_content', 'recent_users', 'recent_recipes', 'recent_products']
                
                if all(key in data for key in expected_keys):
                    self.log_test("Admin Stats", True, 
                                f"Users: {data['total_users']}, Recipes: {data['total_recipes']}, Products: {data['total_products']}")
                    return True
                else:
                    self.log_test("Admin Stats", False, f"Missing keys in response: {list(data.keys())}")
            else:
                self.log_test("Admin Stats", False, f"Status: {response.status_code}, Error: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Stats", False, f"Exception: {str(e)}")
        
        return False

    def cleanup(self):
        """Clean up any remaining uploaded files"""
        if not self.admin_token or not self.uploaded_files:
            return
        
        print(f"\n🧹 Cleaning up {len(self.uploaded_files)} remaining files...")
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        for filename in self.uploaded_files[:]:
            try:
                response = requests.delete(
                    f"{self.base_url}/upload/{filename}",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    print(f"   ✅ Deleted {filename}")
                    self.uploaded_files.remove(filename)
                else:
                    print(f"   ⚠️ Could not delete {filename} - Status: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting {filename}: {str(e)}")

    def run_all_tests(self):
        """Run all image upload tests"""
        print("🖼️  Soumam Heritage - Image Upload Functionality Test")
        print("=" * 60)
        
        # Authentication
        if not self.admin_login():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Core upload tests
        self.test_successful_upload()
        self.test_png_upload()
        
        # Validation tests
        self.test_file_size_validation()
        self.test_file_type_validation()
        self.test_unauthorized_upload()
        
        # File serving and management
        self.test_static_file_serving()
        self.test_image_deletion()
        self.test_delete_nonexistent()
        
        # Admin functionality
        self.test_admin_stats()
        
        # Cleanup
        self.cleanup()
        
        # Results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All image upload tests passed!")
            return True
        else:
            failed = self.tests_run - self.tests_passed
            print(f"⚠️  {failed} test(s) failed")
            return False

def main():
    tester = ImageUploadTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())