#!/usr/bin/env python3
"""
Extended E-commerce API Testing Suite
Tests all the extended e-commerce functionality endpoints.
"""

import requests
import json
import uuid
import time
from datetime import datetime, timezone
import sys
import traceback

class ExtendedEcommerceAPITester:
    def __init__(self, base_url="http://localhost:8001/api"):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.auth_token = None
        self.admin_token = None
        self.test_user_id = None
        self.test_product_id = None
        self.tests_passed = 0
        self.tests_failed = 0
        
    def log(self, message):
        """Log test results"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def make_request(self, method, endpoint, data=None, auth_required=False, admin_required=False, expected_status=None):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self.headers.copy()
        
        # Add authorization if needed
        if auth_required and self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        elif admin_required and self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'
            
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            # Log response details
            self.log(f"{method} {endpoint} -> {response.status_code}")
            
            if expected_status and response.status_code != expected_status:
                self.log(f"❌ Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    self.log(f"   Error: {error_data}")
                except:
                    self.log(f"   Error text: {response.text}")
                self.tests_failed += 1
                return False, {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"status_code": response.status_code, "content": response.text}
                
            if expected_status is None or response.status_code == expected_status:
                self.tests_passed += 1
                return True, response_data
            else:
                self.tests_failed += 1
                return False, response_data
                
        except Exception as e:
            self.log(f"❌ Request failed: {str(e)}")
            self.tests_failed += 1
            return False, {}

    def setup_authentication(self):
        """Setup authentication tokens"""
        self.log("=== Setting up authentication ===")
        
        # Try to login with admin credentials
        admin_login_data = {
            "email": "test@admin.com",
            "password": "testpass123"
        }
        
        success, response = self.make_request(
            'POST', 
            'auth/login', 
            admin_login_data, 
            expected_status=200
        )
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            self.log(f"✅ Admin authentication successful")
            
            # Also set as regular auth token for some tests
            self.auth_token = self.admin_token
            return True
        else:
            self.log(f"❌ Admin authentication failed")
            return False

    def test_product_reviews(self):
        """Test product reviews endpoints"""
        self.log("=== Testing Product Reviews ===")
        
        # First, get available products
        success, products_response = self.make_request('GET', 'products', expected_status=200)
        if not success or not products_response:
            self.log("❌ Cannot get products for review testing")
            return False
            
        if len(products_response) == 0:
            self.log("❌ No products available for review testing")
            return False
            
        # Use the first available product
        test_product = products_response[0]
        product_id = test_product['id']
        self.test_product_id = product_id
        
        self.log(f"Testing with product: {test_product['name']}")
        
        # Test GET reviews with different filters
        review_tests = [
            ('products/{}/reviews'.format(product_id), {}),
            ('products/{}/reviews?rating=5'.format(product_id), {}),
            ('products/{}/reviews?has_photo=true'.format(product_id), {}),
            ('products/{}/reviews?verified_only=true'.format(product_id), {}),
            ('products/{}/reviews?sort=recent'.format(product_id), {}),
            ('products/{}/reviews?sort=helpful'.format(product_id), {}),
            ('products/{}/reviews?sort=rating_high'.format(product_id), {}),
            ('products/{}/reviews?sort=rating_low'.format(product_id), {}),
            ('products/{}/reviews?skip=0&limit=10'.format(product_id), {}),
            ('products/{}/reviews?skip=10&limit=5'.format(product_id), {}),
        ]
        
        all_passed = True
        for endpoint, _ in review_tests:
            success, response = self.make_request('GET', endpoint, expected_status=200)
            if success:
                self.log(f"✅ {endpoint}")
                if 'reviews' in response:
                    self.log(f"   Found {len(response['reviews'])} reviews")
                if 'total' in response:
                    self.log(f"   Total reviews: {response['total']}")
                if 'pages' in response:
                    self.log(f"   Pages: {response['pages']}")
            else:
                self.log(f"❌ {endpoint}")
                all_passed = False
                
        # Test creating a review (requires auth)
        if self.auth_token:
            review_data = {
                "product_id": product_id,
                "rating": 5,
                "title": "Excellent Product!",
                "comment": "This is a test review. The product quality is outstanding.",
                "photos": []
            }
            
            success, response = self.make_request(
                'POST', 
                'reviews', 
                review_data, 
                auth_required=True,
                expected_status=201
            )
            
            if success:
                self.log(f"✅ Review creation successful")
                review_id = response.get('id')
                
                # Test marking review as helpful
                if review_id:
                    success, response = self.make_request(
                        'POST', 
                        f'reviews/{review_id}/helpful',
                        auth_required=True,
                        expected_status=200
                    )
                    
                    if success:
                        self.log(f"✅ Mark review helpful: {response}")
                    else:
                        self.log(f"❌ Mark review helpful failed")
                        all_passed = False
            else:
                self.log(f"❌ Review creation failed")
                all_passed = False
        
        return all_passed

    def test_wishlist_endpoints(self):
        """Test wishlist endpoints"""
        self.log("=== Testing Wishlist ===")
        
        if not self.auth_token:
            self.log("❌ Authentication required for wishlist tests")
            return False
            
        # Test GET wishlist
        success, response = self.make_request('GET', 'wishlist', auth_required=True, expected_status=200)
        if not success:
            self.log("❌ GET wishlist failed")
            return False
            
        self.log(f"✅ GET wishlist: {response}")
        
        # Test adding to wishlist (need a product)
        if self.test_product_id:
            wishlist_data = {
                "product_id": self.test_product_id
            }
            
            success, response = self.make_request(
                'POST', 
                'wishlist', 
                wishlist_data, 
                auth_required=True,
                expected_status=200
            )
            
            if success:
                self.log(f"✅ Add to wishlist: {response}")
                
                # Test removing from wishlist
                success, response = self.make_request(
                    'DELETE', 
                    f'wishlist/{self.test_product_id}',
                    auth_required=True,
                    expected_status=200
                )
                
                if success:
                    self.log(f"✅ Remove from wishlist: {response}")
                else:
                    self.log(f"❌ Remove from wishlist failed")
                    return False
            else:
                self.log(f"❌ Add to wishlist failed")
                return False
        
        return True

    def test_stock_alerts(self):
        """Test stock alerts endpoints"""
        self.log("=== Testing Stock Alerts ===")
        
        if not self.test_product_id:
            self.log("❌ No test product available for stock alerts")
            return False
            
        # Test creating stock alert
        alert_data = {
            "email": "customer@example.com",
            "product_id": self.test_product_id
        }
        
        success, response = self.make_request('POST', 'stock-alerts', alert_data, expected_status=200)
        if not success:
            self.log("❌ Create stock alert failed")
            return False
            
        self.log(f"✅ Create stock alert: {response}")
        
        # Test getting pending stock alerts (admin only)
        if self.admin_token:
            success, response = self.make_request(
                'GET', 
                'admin/stock-alerts', 
                admin_required=True,
                expected_status=200
            )
            
            if success:
                self.log(f"✅ Get pending stock alerts: {len(response.get('alerts', []))} alerts")
            else:
                self.log(f"❌ Get pending stock alerts failed")
                return False
        
        return True

    def test_shipping_calculator(self):
        """Test shipping calculator"""
        self.log("=== Testing Shipping Calculator ===")
        
        # Test different shipping scenarios
        shipping_tests = [
            {
                "items": [{"product_id": "test-id", "quantity": 1}],
                "destination_country": "FR"
            },
            {
                "items": [{"product_id": "test-id", "quantity": 2}],
                "destination_country": "DE"
            },
            {
                "items": [
                    {"product_id": "test-id1", "quantity": 1},
                    {"product_id": "test-id2", "quantity": 1}
                ],
                "destination_country": "ES"
            }
        ]
        
        all_passed = True
        for i, test_data in enumerate(shipping_tests):
            success, response = self.make_request(
                'POST', 
                'shipping/calculate', 
                test_data, 
                expected_status=200
            )
            
            if success:
                self.log(f"✅ Shipping calculation {i+1}")
                self.log(f"   Standard: {response.get('standard', {})}")
                self.log(f"   Express: {response.get('express', {})}")
                self.log(f"   Free threshold: {response.get('free_threshold', 0)}")
                self.log(f"   Current total: {response.get('current_total', 0)}")
            else:
                self.log(f"❌ Shipping calculation {i+1} failed")
                all_passed = False
                
        return all_passed

    def test_regions_origins(self):
        """Test regions/origins endpoints"""
        self.log("=== Testing Regions/Origins ===")
        
        # Test GET all regions
        success, response = self.make_request('GET', 'regions', expected_status=200)
        if not success:
            self.log("❌ GET regions failed")
            return False
            
        regions = response if isinstance(response, list) else []
        self.log(f"✅ GET regions: Found {len(regions)} regions")
        
        if len(regions) < 3:
            self.log(f"⚠️ Expected at least 3 regions, found {len(regions)}")
        
        # Test individual region access
        if len(regions) > 0:
            test_region = regions[0]
            region_id = test_region.get('id')
            
            if region_id:
                success, response = self.make_request('GET', f'regions/{region_id}', expected_status=200)
                if success:
                    self.log(f"✅ GET region {region_id}")
                    if 'coordinates' in response:
                        self.log(f"   Coordinates: {response['coordinates']}")
                    if 'products' in response:
                        self.log(f"   Products: {len(response['products'])} found")
                else:
                    self.log(f"❌ GET region {region_id} failed")
                    return False
        
        return True

    def test_recommendations(self):
        """Test recommendations endpoints"""
        self.log("=== Testing Recommendations ===")
        
        if not self.test_product_id:
            self.log("❌ No test product available for recommendations")
            return False
        
        # Test product recommendations
        success, response = self.make_request(
            'GET', 
            f'products/{self.test_product_id}/recommendations', 
            expected_status=200
        )
        
        if not success:
            self.log("❌ GET product recommendations failed")
            return False
            
        self.log(f"✅ GET product recommendations")
        if 'frequently_bought_together' in response:
            self.log(f"   Frequently bought together: {len(response['frequently_bought_together'])} items")
        if 'similar_products' in response:
            self.log(f"   Similar products: {len(response['similar_products'])} items")
        
        # Test cart recommendations
        cart_items = [
            {"product_id": self.test_product_id, "quantity": 1}
        ]
        
        success, response = self.make_request(
            'POST', 
            'cart/recommendations', 
            cart_items, 
            expected_status=200
        )
        
        if success:
            self.log(f"✅ POST cart recommendations")
            if 'recommendations' in response:
                self.log(f"   Recommendations: {len(response['recommendations'])} items")
        else:
            self.log("❌ POST cart recommendations failed")
            return False
        
        return True

    def test_advanced_filters(self):
        """Test advanced product filtering"""
        self.log("=== Testing Advanced Filters ===")
        
        # Get categories first
        success, categories = self.make_request('GET', 'categories', expected_status=200)
        test_category = categories[0]['id'] if categories and len(categories) > 0 else 'epices'
        
        # Test different filter combinations
        filter_tests = [
            # Basic filters
            ('products/filter/advanced', {}),
            ('products/filter/advanced?category={}'.format(test_category), {}),
            ('products/filter/advanced?price_min=10', {}),
            ('products/filter/advanced?price_max=50', {}),
            ('products/filter/advanced?price_min=10&price_max=50', {}),
            ('products/filter/advanced?origin=algerie', {}),
            ('products/filter/advanced?labels=organic,premium', {}),
            ('products/filter/advanced?in_stock=true', {}),
            ('products/filter/advanced?rating_min=4.0', {}),
            
            # Sort options
            ('products/filter/advanced?sort=recent', {}),
            ('products/filter/advanced?sort=price_low', {}),
            ('products/filter/advanced?sort=price_high', {}),
            ('products/filter/advanced?sort=rating', {}),
            ('products/filter/advanced?sort=popular', {}),
            
            # Pagination
            ('products/filter/advanced?skip=0&limit=10', {}),
            ('products/filter/advanced?skip=10&limit=5', {}),
            
            # Combined filters
            ('products/filter/advanced?category={}&price_min=5&price_max=100&sort=price_low&limit=20'.format(test_category), {}),
        ]
        
        all_passed = True
        for endpoint, _ in filter_tests:
            success, response = self.make_request('GET', endpoint, expected_status=200)
            if success:
                self.log(f"✅ {endpoint}")
                if 'products' in response:
                    self.log(f"   Found {len(response['products'])} products")
                if 'total' in response:
                    self.log(f"   Total: {response['total']}")
                if 'pages' in response:
                    self.log(f"   Pages: {response['pages']}")
            else:
                self.log(f"❌ {endpoint}")
                all_passed = False
                
        return all_passed

    def run_all_tests(self):
        """Run all extended e-commerce API tests"""
        self.log("🚀 Starting Extended E-commerce API Tests")
        self.log(f"Base URL: {self.base_url}")
        
        start_time = time.time()
        
        # Setup authentication
        if not self.setup_authentication():
            self.log("❌ Authentication setup failed - stopping tests")
            return False
        
        # Run all test suites
        test_suites = [
            ("Product Reviews", self.test_product_reviews),
            ("Wishlist", self.test_wishlist_endpoints),
            ("Stock Alerts", self.test_stock_alerts),
            ("Shipping Calculator", self.test_shipping_calculator),
            ("Regions/Origins", self.test_regions_origins),
            ("Recommendations", self.test_recommendations),
            ("Advanced Filters", self.test_advanced_filters),
        ]
        
        suite_results = {}
        for suite_name, test_func in test_suites:
            self.log(f"\n📋 Running {suite_name} tests...")
            try:
                result = test_func()
                suite_results[suite_name] = result
                if result:
                    self.log(f"✅ {suite_name} tests PASSED")
                else:
                    self.log(f"❌ {suite_name} tests FAILED")
            except Exception as e:
                self.log(f"❌ {suite_name} tests ERROR: {str(e)}")
                traceback.print_exc()
                suite_results[suite_name] = False
        
        # Final summary
        end_time = time.time()
        duration = end_time - start_time
        
        self.log(f"\n📊 TEST SUMMARY")
        self.log(f"=" * 50)
        self.log(f"Duration: {duration:.2f} seconds")
        self.log(f"Tests Passed: {self.tests_passed}")
        self.log(f"Tests Failed: {self.tests_failed}")
        self.log(f"Success Rate: {(self.tests_passed / (self.tests_passed + self.tests_failed) * 100):.1f}%")
        
        self.log(f"\nSuite Results:")
        for suite_name, result in suite_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"  {suite_name}: {status}")
        
        all_passed = all(suite_results.values())
        
        if all_passed:
            self.log(f"\n🎉 ALL EXTENDED E-COMMERCE API TESTS PASSED!")
        else:
            self.log(f"\n⚠️ SOME TESTS FAILED - CHECK DETAILS ABOVE")
        
        return all_passed


def main():
    """Main test runner"""
    tester = ExtendedEcommerceAPITester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()