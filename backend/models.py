from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid

# Product Variant Model
class ProductVariant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    sku: str
    price: float
    compare_at_price: Optional[float] = None
    weight_kg: float
    dimensions: Optional[Dict[str, float]] = None
    stock_quantity: int = 0
    low_stock_threshold: int = 5
    image_url: Optional[str] = None

# Product Origin Model
class ProductOrigin(BaseModel):
    region_id: str
    region_name: Dict[str, str]
    coordinates: Dict[str, float]
    producer_name: Optional[str] = None
    producer_story: Optional[Dict[str, str]] = None
    images: List[str] = []

# Product Video Model
class ProductVideo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    thumbnail_url: Optional[str] = None
    title: Dict[str, str]
    duration_seconds: Optional[int] = None
    video_type: str = "presentation"

# Product Model Extended
class ProductExtended(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: Dict[str, str]
    description: Dict[str, str]
    category: str
    labels: List[str] = []
    origin: Optional[ProductOrigin] = None
    variants: List[ProductVariant]
    videos: List[ProductVideo] = []
    reviews_summary: Dict[str, Any] = {
        "average_rating": 0,
        "total_reviews": 0,
        "rating_distribution": {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
    }
    frequently_bought_with: List[str] = []
    similar_products: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Review Model
class Review(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    variant_id: Optional[str] = None
    user_id: str
    user_name: str
    rating: int = Field(ge=1, le=5)
    title: str
    comment: str
    photos: List[str] = []
    verified_purchase: bool = False
    helpful_count: int = 0
    helpful_voters: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReviewCreate(BaseModel):
    product_id: str
    variant_id: Optional[str] = None
    rating: int = Field(ge=1, le=5)
    title: str
    comment: str
    photos: List[str] = []

class ReviewHelpful(BaseModel):
    user_id: str

# Wishlist Model
class WishlistItem(BaseModel):
    product_id: str
    variant_id: Optional[str] = None
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Wishlist(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[WishlistItem] = []
    share_token: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WishlistAdd(BaseModel):
    product_id: str
    variant_id: Optional[str] = None

# Stock Alert Model
class StockAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    user_id: Optional[str] = None
    product_id: str
    variant_id: Optional[str] = None
    notified: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notified_at: Optional[datetime] = None

class StockAlertCreate(BaseModel):
    email: EmailStr
    product_id: str
    variant_id: Optional[str] = None

# Shipping Rule Model
class WeightBracket(BaseModel):
    max_kg: float
    standard_price: float
    express_price: float

class ShippingRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    destination_country: str
    destination_zone: Optional[str] = None
    weight_brackets: List[WeightBracket]
    free_shipping_threshold: float = 50.0
    currency: str = "EUR"

class ShippingCalculation(BaseModel):
    items: List[Dict[str, Any]]
    destination_country: str = "FR"
    destination_zone: Optional[str] = None

class ShippingResult(BaseModel):
    standard: Dict[str, Any]
    express: Dict[str, Any]
    free_threshold: float
    current_total: float
    amount_to_free_shipping: float

# Origin/Region Model
class Region(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: Dict[str, str]
    coordinates: Dict[str, float]
    description: Optional[Dict[str, str]] = None
    images: List[str] = []
    producers: List[Dict[str, Any]] = []
    product_ids: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Recommendation Model
class Recommendation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    frequently_bought_together: List[str] = []
    similar_products: List[str] = []
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
