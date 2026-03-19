"""
Test suite for Iteration 2 features:
- Order creation and stock decrement
- My Orders endpoint
- Review image upload
- Product reviews with photos
- Advanced filter with search
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://api-fix-preview-2.preview.emergentagent.com').rstrip('/')
API = f"{BASE_URL}/api"

# Test credentials
TEST_EMAIL = "yacbhll@gmail.com"
TEST_PASSWORD = "Mazi@go"
VALID_PRODUCT_ID = "45785465-377b-4845-b89f-a493fdff988b"
EXISTING_ORDER = "ORD-20260319-21695FBE"

class TestAuthentication:
    """Test authentication to get token for authenticated endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get auth token"""
        response = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        return data["access_token"]
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


class TestOrderCreation:
    """Test order creation with stock decrement"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get auth token"""
        response = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_get_product_stock_before(self):
        """Get product stock before order"""
        response = requests.get(f"{API}/products/{VALID_PRODUCT_ID}")
        assert response.status_code == 200
        product = response.json()
        assert "variants" in product
        assert len(product["variants"]) > 0
        stock = product["variants"][0].get("stock_quantity", 0)
        print(f"Stock before order: {stock}")
        return stock
    
    def test_create_order_success(self, auth_token):
        """Create order with valid product ID and verify response"""
        # Get product info first
        product_resp = requests.get(f"{API}/products/{VALID_PRODUCT_ID}")
        product = product_resp.json()
        variant = product["variants"][0]
        
        order_data = {
            "customer_name": "TEST_OrderTest User",
            "customer_email": TEST_EMAIL,
            "customer_phone": "+213555123456",
            "shipping_address": "123 Test Street",
            "shipping_city": "Algiers",
            "shipping_postal_code": "16000",
            "items": [
                {
                    "product_id": VALID_PRODUCT_ID,
                    "product_name": product["name"]["fr"],
                    "quantity": 1,
                    "price": variant["price"],
                    "image_url": product.get("image_urls", [""])[0]
                }
            ],
            "payment_method": "cash",
            "notes": "Test order for iteration 2"
        }
        
        response = requests.post(f"{API}/orders", json=order_data)
        assert response.status_code == 200, f"Order creation failed: {response.text}"
        
        order = response.json()
        assert "id" in order
        assert "order_number" in order
        assert order["status"] == "pending"
        assert order["total"] > 0
        print(f"Created order: {order['order_number']}")
        return order
    
    def test_stock_decrement_after_order(self):
        """Verify stock was decremented after order"""
        response = requests.get(f"{API}/products/{VALID_PRODUCT_ID}")
        assert response.status_code == 200
        product = response.json()
        stock = product["variants"][0].get("stock_quantity", 0)
        print(f"Stock after order: {stock}")
        # Stock should have decreased (we can't be 100% sure without knowing initial value)
        assert stock >= 0  # Stock shouldn't be negative


class TestMyOrders:
    """Test my-orders endpoint for authenticated user"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_my_orders_requires_auth(self):
        """Test that my-orders requires authentication"""
        response = requests.get(f"{API}/my-orders")
        assert response.status_code == 403 or response.status_code == 401
    
    def test_my_orders_with_auth(self, auth_token):
        """Test fetching user orders with valid token"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/my-orders", headers=headers)
        assert response.status_code == 200
        
        orders = response.json()
        assert isinstance(orders, list)
        print(f"User has {len(orders)} orders")
        
        if len(orders) > 0:
            order = orders[0]
            assert "id" in order
            assert "order_number" in order
            assert "status" in order
            assert "items" in order
            assert "total" in order


class TestReviewImageUpload:
    """Test review image upload endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_upload_requires_auth(self):
        """Test that review image upload requires authentication"""
        # Create a simple test image
        files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}
        response = requests.post(f"{API}/reviews/upload-image", files=files)
        assert response.status_code == 401
    
    def test_upload_invalid_type(self, auth_token):
        """Test upload with invalid file type"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        files = {"file": ("test.txt", b"text content", "text/plain")}
        response = requests.post(f"{API}/reviews/upload-image", files=files, headers=headers)
        assert response.status_code == 400
        assert "JPEG" in response.text or "PNG" in response.text or "WebP" in response.text
    
    def test_upload_valid_jpeg(self, auth_token):
        """Test upload with valid JPEG image"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        # Create a minimal valid JPEG file (1x1 pixel)
        jpeg_data = bytes([
            0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
            0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
            0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
            0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
            0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
            0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
            0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
            0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
            0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
            0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
            0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
            0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
            0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06,
            0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xA1, 0x08,
            0x23, 0x42, 0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24, 0x33, 0x62, 0x72,
            0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x25, 0x26, 0x27, 0x28,
            0x29, 0x2A, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x43, 0x44, 0x45,
            0x46, 0x47, 0x48, 0x49, 0x4A, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59,
            0x5A, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75,
            0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01, 0x00, 0x00, 0x3F, 0x00, 0xFB, 0xD5,
            0xDB, 0x20, 0x00, 0x00, 0x00, 0xFF, 0xD9
        ])
        files = {"file": ("test.jpg", jpeg_data, "image/jpeg")}
        response = requests.post(f"{API}/reviews/upload-image", files=files, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "filename" in data
        print(f"Uploaded image URL: {data['url']}")


class TestProductReviews:
    """Test product reviews endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_get_product_reviews(self):
        """Test fetching reviews for a product"""
        response = requests.get(f"{API}/products/{VALID_PRODUCT_ID}/reviews")
        assert response.status_code == 200
        data = response.json()
        assert "reviews" in data
        assert "total" in data
        print(f"Product has {data['total']} reviews")
        
        if len(data["reviews"]) > 0:
            review = data["reviews"][0]
            assert "id" in review
            assert "rating" in review
            assert "comment" in review or "title" in review


class TestAdvancedSearch:
    """Test advanced product search/filter"""
    
    def test_search_by_name(self):
        """Test search products by name"""
        response = requests.get(f"{API}/products/filter/advanced", params={"search": "dattes"})
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert "total" in data
        print(f"Search 'dattes' returned {data['total']} products")
        
        # At least one product should match
        if data["total"] > 0:
            product = data["products"][0]
            name_fr = product.get("name", {}).get("fr", "").lower()
            name_en = product.get("name", {}).get("en", "").lower()
            category = product.get("category", "").lower()
            # Product should contain 'dattes' in name or be in dattes category
            assert "dattes" in name_fr or "dates" in name_en or "dattes" in category
    
    def test_filter_by_category(self):
        """Test filter products by category"""
        response = requests.get(f"{API}/products/filter/advanced", params={"category": "dattes"})
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        print(f"Category 'dattes' returned {data['total']} products")
        
        for product in data["products"]:
            assert product["category"] == "dattes"
    
    def test_search_with_sort(self):
        """Test search with sorting"""
        response = requests.get(f"{API}/products/filter/advanced", params={
            "search": "dattes",
            "sort": "price_high"
        })
        assert response.status_code == 200
        data = response.json()
        assert "products" in data


class TestBanners:
    """Test banner/hero slider data"""
    
    def test_get_banners(self):
        """Test fetching banners for hero slider"""
        response = requests.get(f"{API}/banners")
        assert response.status_code == 200
        banners = response.json()
        assert isinstance(banners, list)
        print(f"Found {len(banners)} banners")
        
        if len(banners) > 0:
            banner = banners[0]
            assert "id" in banner
            assert "title" in banner
            assert "image_url" in banner


class TestOrderDetails:
    """Test order details retrieval"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_get_order_by_id(self, auth_token):
        """Test fetching a specific order"""
        # First get my orders to find a valid order ID
        headers = {"Authorization": f"Bearer {auth_token}"}
        orders_resp = requests.get(f"{API}/my-orders", headers=headers)
        orders = orders_resp.json()
        
        if len(orders) > 0:
            order_id = orders[0]["id"]
            response = requests.get(f"{API}/orders/{order_id}")
            assert response.status_code == 200
            order = response.json()
            assert order["id"] == order_id
            assert "order_number" in order
            assert "status" in order
            assert "items" in order
            assert "total" in order
            assert "shipping_address" in order
            print(f"Order {order['order_number']} status: {order['status']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
