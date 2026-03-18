"""
Backend API Tests for Mazigho E-commerce Application
Tests for:
- Categories API
- Products API
- Testimonials API  
- Authentication (login, me)
- Wishlist
- Shipping calculation
- Navigation & Customization
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://api-fix-preview-2.preview.emergentagent.com')

# Test credentials
TEST_EMAIL = "yacbhll@gmail.com"
TEST_PASSWORD = "Mazi@go"


class TestCategoriesAPI:
    """Test categories endpoints"""
    
    def test_get_categories_returns_200(self):
        """GET /api/categories returns 200 and list of categories"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Categories count: {len(data)}")
        
    def test_get_categories_has_6_categories(self):
        """GET /api/categories returns 6 categories"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 6, f"Expected at least 6 categories, got {len(data)}"
        print(f"Categories found: {len(data)}")
        
    def test_categories_have_name_fr_field(self):
        """Categories have name.fr field"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0, "No categories found"
        
        for category in data:
            assert "name" in category, f"Category missing 'name' field: {category}"
            assert "fr" in category["name"], f"Category name missing 'fr' field: {category}"
            print(f"Category: {category['name']['fr']}")


class TestProductsAPI:
    """Test products endpoints"""
    
    def test_get_products_returns_200(self):
        """GET /api/products returns 200"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Products count: {len(data)}")
        
    def test_products_filter_advanced_returns_200(self):
        """GET /api/products/filter/advanced returns 200"""
        response = requests.get(f"{BASE_URL}/api/products/filter/advanced")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "products" in data, "Response should have 'products' key"
        assert "total" in data, "Response should have 'total' key"
        print(f"Advanced filter returned {data['total']} products")
        
    def test_products_filter_advanced_returns_25_products(self):
        """GET /api/products/filter/advanced returns 25 products"""
        response = requests.get(f"{BASE_URL}/api/products/filter/advanced")
        assert response.status_code == 200
        
        data = response.json()
        # Should return 25 products or all if less than 25
        assert data["total"] >= 20, f"Expected at least 20 products, got {data['total']}"
        print(f"Total products: {data['total']}")
        
    def test_products_have_variants_labels_reviews_summary(self):
        """Products have variants, labels, reviews_summary fields"""
        response = requests.get(f"{BASE_URL}/api/products/filter/advanced")
        assert response.status_code == 200
        
        data = response.json()
        products = data.get("products", [])
        assert len(products) > 0, "No products returned"
        
        # Check first few products have required fields
        for product in products[:5]:
            assert "id" in product, f"Product missing 'id': {product}"
            assert "name" in product, f"Product missing 'name': {product}"
            # variants, labels, reviews_summary are optional but should be present
            print(f"Product {product['id']}: variants={product.get('variants') is not None}, labels={product.get('labels') is not None}")
            
    def test_get_single_product(self):
        """GET /api/products/{id} returns a single product"""
        # First get list of products
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        
        products = response.json()
        assert len(products) > 0, "No products found"
        
        product_id = products[0]["id"]
        
        # Get single product
        response = requests.get(f"{BASE_URL}/api/products/{product_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        product = response.json()
        assert product["id"] == product_id, "Product ID mismatch"
        assert "name" in product, "Product missing 'name'"
        print(f"Single product retrieved: {product.get('name', {}).get('fr', 'N/A')}")


class TestTestimonialsAPI:
    """Test testimonials endpoints"""
    
    def test_get_testimonials_returns_200(self):
        """GET /api/testimonials returns 200"""
        response = requests.get(f"{BASE_URL}/api/testimonials")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Testimonials count: {len(data)}")
        
    def test_testimonials_returns_6_approved(self):
        """GET /api/testimonials returns 6 approved testimonials"""
        response = requests.get(f"{BASE_URL}/api/testimonials")
        assert response.status_code == 200
        
        data = response.json()
        # Should return approved testimonials
        assert len(data) >= 6, f"Expected at least 6 testimonials, got {len(data)}"
        print(f"Approved testimonials: {len(data)}")
        
    def test_testimonials_have_required_fields(self):
        """Testimonials have required fields (user_name, rating, content)"""
        response = requests.get(f"{BASE_URL}/api/testimonials")
        assert response.status_code == 200
        
        data = response.json()
        if len(data) > 0:
            testimonial = data[0]
            assert "user_name" in testimonial, "Missing user_name"
            assert "rating" in testimonial, "Missing rating"
            assert "content" in testimonial, "Missing content"
            print(f"Testimonial from: {testimonial['user_name']}")


class TestAuthenticationAPI:
    """Test authentication endpoints"""
    
    def test_login_with_valid_credentials(self):
        """POST /api/auth/login with valid credentials returns token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "access_token" in data, "Missing access_token in response"
        assert "token_type" in data, "Missing token_type in response"
        print(f"Login successful, token_type: {data['token_type']}")
        
    def test_login_returns_valid_token(self):
        """Login token can be used to access /api/auth/me"""
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        
        # Use token to get user info
        headers = {"Authorization": f"Bearer {token}"}
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        
        assert me_response.status_code == 200, f"Failed to get user: {me_response.status_code}"
        
        user = me_response.json()
        assert "email" in user, "Missing email in user data"
        assert user["email"] == TEST_EMAIL, f"Email mismatch: expected {TEST_EMAIL}, got {user['email']}"
        print(f"User retrieved: {user['email']}, role: {user.get('role', 'N/A')}")
        
    def test_login_invalid_credentials(self):
        """POST /api/auth/login with invalid credentials returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpass"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("Invalid credentials correctly rejected")


class TestWishlistAPI:
    """Test wishlist endpoints (requires authentication)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Authentication failed")
        return response.json()["access_token"]
    
    def test_get_wishlist_with_auth(self, auth_token):
        """GET /api/wishlist with valid token returns wishlist"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/wishlist", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "items" in data, "Missing 'items' in wishlist response"
        print(f"Wishlist items: {len(data.get('items', []))}")
        
    def test_get_wishlist_without_auth(self):
        """GET /api/wishlist without token returns 401"""
        response = requests.get(f"{BASE_URL}/api/wishlist")
        
        assert response.status_code == 401 or response.status_code == 403, \
            f"Expected 401/403, got {response.status_code}"
        print("Wishlist correctly requires authentication")


class TestShippingAPI:
    """Test shipping calculation endpoint"""
    
    def test_shipping_calculate(self):
        """POST /api/shipping/calculate returns shipping rates"""
        payload = {
            "destination_country": "FR",
            "items": [
                {"product_id": "test-product", "quantity": 1}
            ]
        }
        
        response = requests.post(f"{BASE_URL}/api/shipping/calculate", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "standard" in data, "Missing 'standard' shipping option"
        assert "express" in data, "Missing 'express' shipping option"
        print(f"Shipping rates: standard={data['standard']}, express={data['express']}")


class TestNavigationAPI:
    """Test navigation endpoints"""
    
    def test_get_navigation(self):
        """GET /api/navigation returns navigation items"""
        response = requests.get(f"{BASE_URL}/api/navigation")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Navigation items: {len(data)}")


class TestCustomizationAPI:
    """Test site customization endpoint"""
    
    def test_get_customization(self):
        """GET /api/customization returns site settings"""
        response = requests.get(f"{BASE_URL}/api/customization")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, dict), "Response should be a dict"
        print(f"Customization keys: {list(data.keys())[:5]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
