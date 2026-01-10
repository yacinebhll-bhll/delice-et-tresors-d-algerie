from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
from passlib.context import CryptContext
import json
import shutil
import aiofiles
from email_service import email_service

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is required for production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI(title="Soumam Heritage API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Setup upload directory
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount static files for serving uploaded images
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# --- Models ---

# User Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: str
    role: str = "user"  # "user" or "admin"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "user"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Category Models
class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: Dict[str, str]  # {"fr": "Dattes", "en": "Dates", "ar": "تمور"}
    slug: str  # URL-friendly name
    description: Optional[Dict[str, str]] = None
    icon: Optional[str] = "🛍️"  # Emoji or icon name
    image_url: Optional[str] = None
    order: int = 0  # For sorting
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CategoryCreate(BaseModel):
    name: Dict[str, str]
    slug: str
    description: Optional[Dict[str, str]] = None
    icon: Optional[str] = "🛍️"
    image_url: Optional[str] = None
    order: Optional[int] = 0
    is_active: Optional[bool] = True

class CategoryUpdate(BaseModel):
    name: Optional[Dict[str, str]] = None
    slug: Optional[str] = None
    description: Optional[Dict[str, str]] = None
    icon: Optional[str] = None
    image_url: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None

# Product Models
class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: Dict[str, str]
    description: Dict[str, str]
    category: str  # "epices", "thes", "robes-kabyles", "bijoux-kabyles"
    price: float
    currency: str = "EUR"
    image_urls: List[str]
    in_stock: bool = True
    # Inventory Management
    track_inventory: bool = True  # Whether to track inventory for this product
    stock_quantity: int = 0  # Current quantity in stock
    low_stock_threshold: int = 5  # Alert when stock is below this
    allow_backorder: bool = False  # Allow orders when out of stock
    origin: Dict[str, str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None

class ProductCreate(BaseModel):
    name: Dict[str, str]
    description: Dict[str, str]
    category: str
    price: float
    image_urls: List[str]
    origin: Dict[str, str]
    in_stock: bool = True
    track_inventory: bool = True
    stock_quantity: int = 0
    low_stock_threshold: int = 5
    allow_backorder: bool = False

class ProductUpdate(BaseModel):
    name: Optional[Dict[str, str]] = None
    description: Optional[Dict[str, str]] = None
    category: Optional[str] = None
    price: Optional[float] = None
    image_urls: Optional[List[str]] = None
    origin: Optional[Dict[str, str]] = None
    in_stock: Optional[bool] = None
    track_inventory: Optional[bool] = None
    stock_quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    allow_backorder: Optional[bool] = None

# Stock Adjustment Models
class StockAdjustment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    adjustment_type: str  # "increase", "decrease", "set", "order"
    quantity: int
    reason: Optional[str] = None
    notes: Optional[str] = None
    performed_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StockAdjustmentRequest(BaseModel):
    adjustment_type: str  # "increase", "decrease", "set"
    quantity: int
    reason: Optional[str] = None
    notes: Optional[str] = None

# Historical Content Models
class HistoricalContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: Dict[str, str]
    content: Dict[str, str]
    region: str  # "algerie", "kabylie", "vallee-soumam"
    image_urls: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None

class HistoricalContentCreate(BaseModel):
    title: Dict[str, str]
    content: Dict[str, str]
    region: str
    image_urls: List[str]

class HistoricalContentUpdate(BaseModel):
    title: Optional[Dict[str, str]] = None
    content: Optional[Dict[str, str]] = None
    region: Optional[str] = None
    image_urls: Optional[List[str]] = None

# Admin Statistics Model
class AdminStats(BaseModel):
    total_users: int
    total_products: int
    total_historical_content: int
    total_contact_messages: int
    recent_users: int
    recent_products: int
    recent_contact_messages: int

# Settings Model
class Settings(BaseModel):
    id: str = Field(default="site_settings")
    general: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None
    appearance: Optional[Dict[str, Any]] = None
    seo: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, Any]] = None
    security: Optional[Dict[str, Any]] = None
    media: Optional[Dict[str, Any]] = None
    backup: Optional[Dict[str, Any]] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Customization Model
class SiteCustomization(BaseModel):
    id: str = Field(default="site_customization")
    # Brand Identity
    site_name: str = "Délices et Trésors d'Algérie"
    site_slogan: Dict[str, str] = {
        "fr": "Découvrez nos trésors : dattes Deglet Nour et huile d'olive kabyle authentique",
        "en": "Discover our treasures: Deglet Nour dates and authentic Kabyle olive oil",
        "ar": "اكتشف كنوزنا: تمور دقلة نور وزيت الزيتون القبائلي الأصيل"
    }
    tagline: Dict[str, str] = {
        "fr": "Saveurs authentiques d'Algérie",
        "en": "Authentic flavors of Algeria",
        "ar": "نكهات الجزائر الأصيلة"
    }
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    
    # Colors
    primary_color: str = "#6B8E23"  # Olive green
    secondary_color: str = "#8B7355"  # Golden brown
    accent_color: str = "#F59E0B"  # Amber
    
    # Typography
    font_heading: str = "Playfair Display"
    font_body: str = "Montserrat"
    
    # Contact Info
    contact_email: str = "contact@delices-algerie.com"
    contact_phone: Optional[str] = None
    contact_address: Dict[str, str] = {
        "fr": "Algérie",
        "en": "Algeria",
        "ar": "الجزائر"
    }
    
    # Page Texts
    home_title: Dict[str, str] = {
        "fr": "Délices et Trésors d'Algérie",
        "en": "Delights and Treasures of Algeria",
        "ar": "لذائذ وكنوز الجزائر"
    }
    home_subtitle: Dict[str, str] = {
        "fr": "Découvrez l'authenticité du terroir algérien",
        "en": "Discover the authenticity of Algerian terroir",
        "ar": "اكتشف أصالة التراب الجزائري"
    }
    
    shop_title: Dict[str, str] = {
        "fr": "Boutique Délices et Trésors d'Algérie",
        "en": "Délices et Trésors d'Algérie Shop",
        "ar": "متجر لذائذ وكنوز الجزائر"
    }
    shop_description: Dict[str, str] = {
        "fr": "Découvrez nos trésors : dattes Deglet Nour et huile d'olive kabyle authentique",
        "en": "Discover our treasures: Deglet Nour dates and authentic Kabyle olive oil",
        "ar": "اكتشف كنوزنا: تمور دقلة نور وزيت الزيتون القبائلي الأصيل"
    }
    
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CustomizationUpdate(BaseModel):
    site_name: Optional[str] = None
    site_slogan: Optional[Dict[str, str]] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    font_heading: Optional[str] = None
    font_body: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_address: Optional[Dict[str, str]] = None
    home_title: Optional[Dict[str, str]] = None
    home_subtitle: Optional[Dict[str, str]] = None
    shop_title: Optional[Dict[str, str]] = None
    shop_description: Optional[Dict[str, str]] = None
    tagline: Optional[Dict[str, str]] = None

# Custom Page Models
class CustomPage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: Dict[str, str]  # {"fr": "Mentions légales", "en": "Legal notice", "ar": "..."}
    slug: str  # URL-friendly: "mentions-legales"
    content: Dict[str, str]  # HTML content in 3 languages
    meta_description: Optional[Dict[str, str]] = None
    is_published: bool = True
    show_in_menu: bool = False  # Display in navigation menu
    menu_order: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CustomPageCreate(BaseModel):
    title: Dict[str, str]
    slug: str
    content: Dict[str, str]
    meta_description: Optional[Dict[str, str]] = None
    is_published: Optional[bool] = True
    show_in_menu: Optional[bool] = False
    menu_order: Optional[int] = 0

class CustomPageUpdate(BaseModel):
    title: Optional[Dict[str, str]] = None
    slug: Optional[str] = None
    content: Optional[Dict[str, str]] = None
    meta_description: Optional[Dict[str, str]] = None
    is_published: Optional[bool] = None
    show_in_menu: Optional[bool] = None
    menu_order: Optional[int] = None

# SEO Settings Model
class SEOSettings(BaseModel):
    id: str = "seo_settings"
    site_title: Dict[str, str] = {"fr": "", "en": "", "ar": ""}
    site_description: Dict[str, str] = {"fr": "", "en": "", "ar": ""}
    site_keywords: Dict[str, str] = {"fr": "", "en": "", "ar": ""}
    og_image: str = ""
    twitter_handle: str = ""
    google_analytics_id: str = ""
    google_site_verification: str = ""
    robots_txt: str = "User-agent: *\nAllow: /"
    canonical_url: str = ""
    structured_data_enabled: bool = True
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Order Models
class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float
    image_url: Optional[str] = None

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_number: str = Field(default_factory=lambda: f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}")
    user_id: Optional[str] = None
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    shipping_address: str
    shipping_city: str
    shipping_postal_code: Optional[str] = None
    items: List[OrderItem]
    subtotal: float
    shipping_cost: float = 0.0
    promo_code: Optional[str] = None
    discount_amount: float = 0.0
    total: float
    payment_method: str = "cash"  # cash, bank_transfer, paypal
    payment_status: str = "pending"  # pending, paid, failed
    status: str = "pending"  # pending, confirmed, processing, shipped, delivered, cancelled
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OrderCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    shipping_address: str
    shipping_city: str
    shipping_postal_code: Optional[str] = None
    items: List[OrderItem]
    promo_code: Optional[str] = None
    payment_method: str = "cash"  # cash, bank_transfer, paypal
    notes: Optional[str] = None

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

# Contact Models
class ContactMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    subject: str
    message: str
    status: str = "new"  # "new", "read", "replied"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContactMessageCreate(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

class ContactMessageUpdate(BaseModel):
    status: Optional[str] = None

# Testimonial Models
class Testimonial(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_name: str
    customer_email: EmailStr
    rating: int = Field(..., ge=1, le=5)  # Rating from 1 to 5
    comment: str
    product_id: Optional[str] = None  # Optional: testimonial for a specific product
    is_approved: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None  # Admin user ID who approved

class TestimonialCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    rating: int = Field(..., ge=1, le=5)
    comment: str
    product_id: Optional[str] = None

class TestimonialUpdate(BaseModel):
    is_approved: Optional[bool] = None
    comment: Optional[str] = None

# Navigation Menu Models
class NavigationItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    label: Dict[str, str]  # {"fr": "Accueil", "en": "Home", "ar": "الرئيسية"}
    url: str  # "/", "/shop", "/about", "https://external.com"
    is_external: bool = False  # True for external links
    order: int = 0  # For sorting
    is_active: bool = True
    icon: Optional[str] = None  # Optional icon name
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NavigationItemCreate(BaseModel):
    label: Dict[str, str]
    url: str
    is_external: Optional[bool] = False
    order: Optional[int] = 0
    is_active: Optional[bool] = True
    icon: Optional[str] = None

class NavigationItemUpdate(BaseModel):
    label: Optional[Dict[str, str]] = None
    url: Optional[str] = None
    is_external: Optional[bool] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None
    icon: Optional[str] = None

# Footer Models
class FooterSettings(BaseModel):
    id: str = Field(default="footer_config")
    about_text: Dict[str, str] = Field(default_factory=dict)  # {"fr": "À propos...", "en": "About...", "ar": "..."}
    social_links: List[Dict[str, str]] = Field(default_factory=list)  # [{"name": "Facebook", "url": "...", "icon": "..."}]
    footer_links: List[Dict[str, Any]] = Field(default_factory=list)  # [{"title": {"fr": "...", "en": "...", "ar": "..."}, "links": [...]}]
    copyright_text: Dict[str, str] = Field(default_factory=dict)
    contact_info: Dict[str, Any] = Field(default_factory=dict)  # {"email": "...", "phone": "...", "address": {...}}
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FooterSettingsUpdate(BaseModel):
    about_text: Optional[Dict[str, str]] = None
    social_links: Optional[List[Dict[str, str]]] = None
    footer_links: Optional[List[Dict[str, Any]]] = None
    copyright_text: Optional[Dict[str, str]] = None
    contact_info: Optional[Dict[str, Any]] = None

# Banner Models (Homepage Slider)
class Banner(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: Dict[str, str]  # {"fr": "Titre", "en": "Title", "ar": "العنوان"}
    subtitle: Dict[str, str] = Field(default_factory=dict)
    description: Dict[str, str] = Field(default_factory=dict)
    image_url: str
    cta_text: Dict[str, str] = Field(default_factory=dict)  # Call-to-action button text
    cta_link: Optional[str] = None  # Link for the CTA button
    order: int = 0
    is_active: bool = True
    background_color: Optional[str] = None  # Optional custom background
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BannerCreate(BaseModel):
    title: Dict[str, str]
    subtitle: Optional[Dict[str, str]] = None
    description: Optional[Dict[str, str]] = None
    image_url: str
    cta_text: Optional[Dict[str, str]] = None
    cta_link: Optional[str] = None
    order: Optional[int] = 0
    is_active: Optional[bool] = True
    background_color: Optional[str] = None

class BannerUpdate(BaseModel):
    title: Optional[Dict[str, str]] = None
    subtitle: Optional[Dict[str, str]] = None
    description: Optional[Dict[str, str]] = None
    image_url: Optional[str] = None
    cta_text: Optional[Dict[str, str]] = None
    cta_link: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None
    background_color: Optional[str] = None

# Newsletter Models
class NewsletterSubscriber(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    is_active: bool = True
    subscribed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    unsubscribed_at: Optional[datetime] = None

class NewsletterSubscribe(BaseModel):
    email: EmailStr

# Promo Code Models
class PromoCode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str  # The actual promo code (e.g., "SUMMER2025")
    description: Optional[Dict[str, str]] = None  # {"fr": "...", "en": "...", "ar": "..."}
    discount_type: str  # "percentage" or "fixed"
    discount_value: float  # Percentage (e.g., 20 for 20%) or fixed amount (e.g., 10.00)
    min_order_amount: Optional[float] = None  # Minimum order amount to use this code
    max_discount_amount: Optional[float] = None  # Maximum discount for percentage codes
    usage_limit: Optional[int] = None  # Total number of times this code can be used (None = unlimited)
    usage_count: int = 0  # How many times it has been used
    user_usage_limit: Optional[int] = None  # Max uses per user (None = unlimited)
    valid_from: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    valid_until: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PromoCodeCreate(BaseModel):
    code: str
    description: Optional[Dict[str, str]] = None
    discount_type: str
    discount_value: float
    min_order_amount: Optional[float] = None
    max_discount_amount: Optional[float] = None
    usage_limit: Optional[int] = None
    user_usage_limit: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = True

class PromoCodeUpdate(BaseModel):
    description: Optional[Dict[str, str]] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    min_order_amount: Optional[float] = None
    max_discount_amount: Optional[float] = None
    usage_limit: Optional[int] = None
    user_usage_limit: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None

class PromoCodeValidation(BaseModel):
    code: str
    order_amount: float

# --- Authentication Functions ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return User(**user)

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# --- Authentication Routes ---
@api_router.post("/auth/register", response_model=User)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.dict()
    del user_dict["password"]
    user_dict["hashed_password"] = hashed_password
    
    new_user = User(**user_dict)
    # Insert the full user dict with hashed_password to database
    user_dict_with_id = new_user.dict()
    user_dict_with_id["hashed_password"] = hashed_password
    await db.users.insert_one(user_dict_with_id)
    return new_user

@api_router.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = await db.users.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.get("/auth/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# --- Password Reset Routes ---
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

@api_router.post("/auth/forgot-password")
async def forgot_password(request: PasswordResetRequest, background_tasks: BackgroundTasks):
    """Request a password reset email"""
    user = await db.users.find_one({"email": request.email})
    
    # Always return success to prevent email enumeration attacks
    if not user:
        return {"message": "If this email exists, a reset link has been sent"}
    
    # Generate reset token (valid for 1 hour)
    reset_token = str(uuid.uuid4())
    reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
    
    # Store the reset token in the database
    await db.password_resets.delete_many({"email": request.email})  # Remove old tokens
    await db.password_resets.insert_one({
        "email": request.email,
        "token": reset_token,
        "expires_at": reset_expires,
        "created_at": datetime.now(timezone.utc)
    })
    
    # Send reset email in background
    background_tasks.add_task(
        send_password_reset_email,
        request.email,
        user.get("full_name", ""),
        reset_token
    )
    
    return {"message": "If this email exists, a reset link has been sent"}

@api_router.post("/auth/reset-password")
async def reset_password(request: PasswordResetConfirm):
    """Reset password with token"""
    # Find the reset token
    reset_record = await db.password_resets.find_one({"token": request.token})
    
    if not reset_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token"
        )
    
    # Check if token is expired
    expires_at = reset_record["expires_at"]
    if isinstance(expires_at, datetime):
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if datetime.now(timezone.utc) > expires_at:
        await db.password_resets.delete_one({"token": request.token})
        raise HTTPException(
            status_code=400,
            detail="Reset token has expired"
        )
    
    # Validate password length
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters"
        )
    
    # Update the user's password
    hashed_password = get_password_hash(request.new_password)
    result = await db.users.update_one(
        {"email": reset_record["email"]},
        {"$set": {"hashed_password": hashed_password}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=400,
            detail="Failed to update password"
        )
    
    # Delete the used token
    await db.password_resets.delete_one({"token": request.token})
    
    return {"message": "Password has been reset successfully"}

@api_router.get("/auth/verify-reset-token/{token}")
async def verify_reset_token(token: str):
    """Verify if a reset token is valid"""
    reset_record = await db.password_resets.find_one({"token": token})
    
    if not reset_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid reset token"
        )
    
    expires_at = reset_record["expires_at"]
    if isinstance(expires_at, datetime):
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if datetime.now(timezone.utc) > expires_at:
        await db.password_resets.delete_one({"token": token})
        raise HTTPException(
            status_code=400,
            detail="Reset token has expired"
        )
    
    return {"valid": True, "email": reset_record["email"]}

def send_password_reset_email(email: str, full_name: str, token: str):
    """Send password reset email"""
    try:
        from email_service import email_service
        
        # Get the frontend URL from environment
        frontend_url = os.environ.get('FRONTEND_URL', '')
        if not frontend_url:
            # Fallback: construct from CORS_ORIGINS if available
            cors_origins = os.environ.get('CORS_ORIGINS', '')
            if cors_origins and cors_origins != '*':
                frontend_url = cors_origins.split(',')[0].strip()
        
        if not frontend_url:
            logger.error("FRONTEND_URL not configured - password reset email cannot be sent")
            return
            
        reset_link = f"{frontend_url}/reset-password?token={token}"
        
        subject = "Réinitialisation de votre mot de passe - Délices et Trésors d'Algérie"
        
        body_text = f"""
Bonjour {full_name or 'cher client'},

Vous avez demandé la réinitialisation de votre mot de passe.

Cliquez sur le lien suivant pour créer un nouveau mot de passe :
{reset_link}

Ce lien est valable pendant 1 heure.

Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email.

Cordialement,
L'équipe Délices et Trésors d'Algérie
        """
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #6B8E23; margin: 0;">Délices et Trésors d'Algérie</h1>
                </div>
                
                <h2 style="color: #333;">Réinitialisation de mot de passe</h2>
                
                <p>Bonjour {full_name or 'cher client'},</p>
                
                <p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
                
                <p>Cliquez sur le bouton ci-dessous pour créer un nouveau mot de passe :</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" 
                       style="background: linear-gradient(135deg, #F59E0B 0%, #6B8E23 100%); 
                              color: white; 
                              padding: 15px 30px; 
                              text-decoration: none; 
                              border-radius: 8px; 
                              font-weight: bold;
                              display: inline-block;">
                        Réinitialiser mon mot de passe
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    Ce lien est valable pendant <strong>1 heure</strong>.
                </p>
                
                <p style="color: #666; font-size: 14px;">
                    Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email.
                </p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px; text-align: center;">
                    Cet email a été envoyé par Délices et Trésors d'Algérie.<br>
                    Si le bouton ne fonctionne pas, copiez ce lien : {reset_link}
                </p>
            </div>
        </body>
        </html>
        """
        
        email_service.send_email(email, subject, body_text, body_html)
        
    except Exception as e:
        logger.error(f"Error sending password reset email: {e}")

# --- User Profile Routes ---
@api_router.put("/users/me", response_model=User)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update current user's profile"""
    update_data = {}
    
    if user_update.full_name is not None:
        update_data["full_name"] = user_update.full_name
    
    if update_data:
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": update_data}
        )
        
        # Fetch updated user
        updated_user = await db.users.find_one({"id": current_user.id})
        return User(**updated_user)
    
    return current_user

@api_router.put("/users/me/password")
async def change_password(
    password_data: Dict[str, str],
    current_user: User = Depends(get_current_user)
):
    """Change current user's password"""
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(
            status_code=400,
            detail="Both current and new passwords are required"
        )
    
    # Verify current password
    user_with_password = await db.users.find_one({"id": current_user.id})
    if not verify_password(current_password, user_with_password.get("hashed_password")):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )
    
    # Update password
    hashed_password = get_password_hash(new_password)
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"hashed_password": hashed_password}}
    )
    
    return {"message": "Password changed successfully"}

# --- Category Routes ---
@api_router.get("/categories", response_model=List[Category])
async def get_categories():
    """Get all active categories (public)"""
    categories = await db.categories.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(1000)
    return [Category(**cat) for cat in categories]

@api_router.get("/admin/categories", response_model=List[Category])
async def get_all_categories_admin(admin: User = Depends(get_admin_user)):
    """Get all categories including inactive (admin only)"""
    categories = await db.categories.find({}, {"_id": 0}).sort("order", 1).to_list(1000)
    return [Category(**cat) for cat in categories]

@api_router.post("/admin/categories", response_model=Category)
async def create_category(category_data: CategoryCreate, admin: User = Depends(get_admin_user)):
    """Create a new category (admin only)"""
    category = Category(**category_data.model_dump())
    await db.categories.insert_one(category.model_dump())
    return category

@api_router.get("/admin/categories/{category_id}", response_model=Category)
async def get_category_admin(category_id: str, admin: User = Depends(get_admin_user)):
    """Get a specific category (admin only)"""
    category = await db.categories.find_one({"id": category_id}, {"_id": 0})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return Category(**category)

@api_router.put("/admin/categories/{category_id}", response_model=Category)
async def update_category(category_id: str, category_data: CategoryUpdate, admin: User = Depends(get_admin_user)):
    """Update a category (admin only)"""
    category = await db.categories.find_one({"id": category_id}, {"_id": 0})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = {k: v for k, v in category_data.model_dump().items() if v is not None}
    if update_data:
        await db.categories.update_one({"id": category_id}, {"$set": update_data})
        category.update(update_data)
    
    return Category(**category)

@api_router.delete("/admin/categories/{category_id}")
async def delete_category(category_id: str, admin: User = Depends(get_admin_user)):
    """Delete a category (admin only)"""
    # Check if any products use this category
    products_count = await db.products.count_documents({"category": category_id})
    if products_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete category. {products_count} product(s) are using this category."
        )
    
    result = await db.categories.delete_one({"id": category_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"message": "Category deleted successfully"}

# --- Product Routes ---
@api_router.get("/products", response_model=List[Product])
async def get_products(category: Optional[str] = None):
    query = {"category": category} if category else {}
    products = await db.products.find(query, {"_id": 0}).to_list(1000)
    return [Product(**product) for product in products]

@api_router.post("/products", response_model=Product)
async def create_product(product_data: ProductCreate, current_user: User = Depends(get_current_user)):
    product_dict = product_data.dict()
    product_dict["created_by"] = current_user.id
    product = Product(**product_dict)
    await db.products.insert_one(product.dict())
    return product

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)

@api_router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product_data: ProductUpdate, admin_user: User = Depends(get_admin_user)):
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = {k: v for k, v in product_data.dict().items() if v is not None}
    if update_data:
        await db.products.update_one({"id": product_id}, {"$set": update_data})
    
    updated_product = await db.products.find_one({"id": product_id})
    return Product(**updated_product)

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str, admin_user: User = Depends(get_admin_user)):
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await db.products.delete_one({"id": product_id})
    return {"message": "Product deleted successfully"}

# --- Historical Content Routes ---
@api_router.get("/historical-content", response_model=List[HistoricalContent])
async def get_historical_content(region: Optional[str] = None):
    query = {"region": region} if region else {}
    content = await db.historical_content.find(query, {"_id": 0}).to_list(1000)
    return [HistoricalContent(**item) for item in content]

@api_router.post("/historical-content", response_model=HistoricalContent)
async def create_historical_content(content_data: HistoricalContentCreate, admin_user: User = Depends(get_admin_user)):
    content_dict = content_data.dict()
    content_dict["created_by"] = admin_user.id
    content = HistoricalContent(**content_dict)
    await db.historical_content.insert_one(content.dict())
    return content

@api_router.put("/historical-content/{content_id}", response_model=HistoricalContent)
async def update_historical_content(content_id: str, content_data: HistoricalContentUpdate, admin_user: User = Depends(get_admin_user)):
    content = await db.historical_content.find_one({"id": content_id})
    if not content:
        raise HTTPException(status_code=404, detail="Historical content not found")
    
    update_data = {k: v for k, v in content_data.dict().items() if v is not None}
    if update_data:
        await db.historical_content.update_one({"id": content_id}, {"$set": update_data})
    
    updated_content = await db.historical_content.find_one({"id": content_id})
    return HistoricalContent(**updated_content)

@api_router.delete("/historical-content/{content_id}")
async def delete_historical_content(content_id: str, admin_user: User = Depends(get_admin_user)):
    content = await db.historical_content.find_one({"id": content_id})
    if not content:
        raise HTTPException(status_code=404, detail="Historical content not found")
    
    await db.historical_content.delete_one({"id": content_id})
    return {"message": "Historical content deleted successfully"}

# --- Admin Routes ---
@api_router.get("/admin/stats", response_model=AdminStats)
async def get_admin_stats(admin_user: User = Depends(get_admin_user)):
    # Calculate statistics
    total_users = await db.users.count_documents({})
    total_products = await db.products.count_documents({})
    total_historical_content = await db.historical_content.count_documents({})
    total_contact_messages = await db.contact_messages.count_documents({})
    
    # Recent items (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_users = await db.users.count_documents({"created_at": {"$gte": thirty_days_ago}})
    recent_products = await db.products.count_documents({"created_at": {"$gte": thirty_days_ago}})
    recent_contact_messages = await db.contact_messages.count_documents({"created_at": {"$gte": thirty_days_ago}})
    
    return AdminStats(
        total_users=total_users,
        total_products=total_products,
        total_historical_content=total_historical_content,
        total_contact_messages=total_contact_messages,
        recent_users=recent_users,
        recent_products=recent_products,
        recent_contact_messages=recent_contact_messages
    )

@api_router.get("/admin/users", response_model=List[User])
async def get_all_users(admin_user: User = Depends(get_admin_user)):
    users = await db.users.find({}, {"_id": 0, "hashed_password": 0}).to_list(1000)
    # Add back hashed_password as empty string for Pydantic model
    for user in users:
        user["hashed_password"] = ""
    return [User(**user) for user in users]

@api_router.put("/admin/users/{user_id}", response_model=User)
async def update_user_admin(user_id: str, user_data: UserUpdate, admin_user: User = Depends(get_admin_user)):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {k: v for k, v in user_data.dict().items() if v is not None}
    if update_data:
        await db.users.update_one({"id": user_id}, {"$set": update_data})
    
    updated_user = await db.users.find_one({"id": user_id})
    return User(**updated_user)

@api_router.delete("/admin/users/{user_id}")
async def delete_user_admin(user_id: str, admin_user: User = Depends(get_admin_user)):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deleting themselves
    if user_id == admin_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    await db.users.delete_one({"id": user_id})
    return {"message": "User deleted successfully"}

# --- Settings Routes ---
@api_router.get("/admin/settings")
async def get_settings(admin_user: User = Depends(get_admin_user)):
    """Get site settings (admin only)"""
    settings = await db.settings.find_one({"id": "site_settings"})
    
    if not settings:
        # Return default settings if none exist
        return {}
    
    # Remove MongoDB _id field
    if "_id" in settings:
        del settings["_id"]
    
    return settings

@api_router.put("/admin/settings")
async def update_settings(
    settings_update: Dict[str, Any],
    admin_user: User = Depends(get_admin_user)
):
    """Update site settings (admin only)"""
    try:
        # Get existing settings or create new
        existing_settings = await db.settings.find_one({"id": "site_settings"})
        
        if existing_settings:
            # Update existing settings
            update_data = {
                **existing_settings,
                **settings_update,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.settings.update_one(
                {"id": "site_settings"},
                {"$set": update_data}
            )
        else:
            # Create new settings document
            new_settings = {
                "id": "site_settings",
                **settings_update,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await db.settings.insert_one(new_settings)
        
        return {"success": True, "message": "Settings updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating settings: {str(e)}")

# --- Image Upload Routes ---
@api_router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    admin_user: User = Depends(get_admin_user)
):
    """Upload an image file (admin only)"""
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Validate file size (max 10MB)
        file_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file in chunks
        async with aiofiles.open(file_path, 'wb') as f:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                file_size += len(chunk)
                
                # Check size limit (10MB)
                if file_size > 10 * 1024 * 1024:
                    # Delete the file if it exceeds the limit
                    if file_path.exists():
                        file_path.unlink()
                    raise HTTPException(
                        status_code=400,
                        detail="File size exceeds 10MB limit"
                    )
                
                await f.write(chunk)
        
        # Return the URL (through API)
        file_url = f"/api/uploads/{unique_filename}"
        
        return {
            "success": True,
            "filename": unique_filename,
            "url": file_url,
            "size": file_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@api_router.delete("/upload/{filename}")
async def delete_image(
    filename: str,
    admin_user: User = Depends(get_admin_user)
):
    """Delete an uploaded image (admin only)"""
    try:
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path.unlink()
        
        return {"success": True, "message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

# --- File Serving Route ---
@api_router.get("/uploads/{filename}")
async def serve_uploaded_file(filename: str):
    """Serve uploaded files through API"""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)

# --- Media Library Routes ---
class MediaItem(BaseModel):
    id: str
    filename: str
    original_name: str
    url: str
    mime_type: str
    size: int
    uploaded_at: datetime
    uploaded_by: Optional[str] = None

@api_router.get("/admin/media")
async def get_media_library(admin: User = Depends(get_admin_user)):
    """Get all media files in the library"""
    try:
        media_items = await db.media.find({}, {"_id": 0}).sort("uploaded_at", -1).to_list(1000)
        return media_items
    except Exception as e:
        logger.error(f"Error fetching media library: {e}")
        return []

@api_router.post("/admin/media/upload")
async def upload_media(
    file: UploadFile = File(...),
    admin: User = Depends(get_admin_user)
):
    """Upload a file to the media library"""
    try:
        # Generate unique filename
        file_extension = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Read file content and size
        content = await file.read()
        file_size = len(content)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as out_file:
            await out_file.write(content)
        
        # Create media record
        media_item = {
            "id": str(uuid.uuid4()),
            "filename": unique_filename,
            "original_name": file.filename,
            "url": f"/api/uploads/{unique_filename}",
            "mime_type": file.content_type or "application/octet-stream",
            "size": file_size,
            "uploaded_at": datetime.now(timezone.utc),
            "uploaded_by": admin.email
        }
        
        await db.media.insert_one(media_item)
        
        # Remove _id for response
        media_item.pop("_id", None)
        
        return media_item
        
    except Exception as e:
        logger.error(f"Error uploading to media library: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/admin/media/{media_id}")
async def delete_media(
    media_id: str,
    admin: User = Depends(get_admin_user)
):
    """Delete a file from the media library"""
    try:
        # Find media record
        media = await db.media.find_one({"id": media_id})
        
        if not media:
            raise HTTPException(status_code=404, detail="Media not found")
        
        # Delete file from disk
        file_path = UPLOAD_DIR / media["filename"]
        if file_path.exists():
            file_path.unlink()
        
        # Delete from database
        await db.media.delete_one({"id": media_id})
        
        return {"success": True, "message": "Media deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting media: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Order Routes ---
@api_router.post("/orders", response_model=Order)
async def create_order(order_data: OrderCreate, background_tasks: BackgroundTasks):
    """Create a new order (public)"""
    # Calculate totals
    subtotal = sum(item.price * item.quantity for item in order_data.items)
    shipping_cost = 0.0  # Free shipping for now
    discount_amount = 0.0
    promo_code = None
    
    # Apply promo code if provided
    if order_data.promo_code:
        try:
            code = await db.promo_codes.find_one(
                {"code": order_data.promo_code.upper(), "is_active": True},
                {"_id": 0}
            )
            
            if code:
                promo = PromoCode(**code)
                now = datetime.now(timezone.utc)
                
                # Validate promo code
                is_valid = True
                if promo.valid_from:
                    valid_from = promo.valid_from.replace(tzinfo=timezone.utc) if promo.valid_from.tzinfo is None else promo.valid_from
                    if now < valid_from:
                        is_valid = False
                if promo.valid_until:
                    valid_until = promo.valid_until.replace(tzinfo=timezone.utc) if promo.valid_until.tzinfo is None else promo.valid_until
                    if now > valid_until:
                        is_valid = False
                if promo.usage_limit and promo.usage_count >= promo.usage_limit:
                    is_valid = False
                if promo.min_order_amount and subtotal < promo.min_order_amount:
                    is_valid = False
                
                if is_valid:
                    # Calculate discount
                    if promo.discount_type == "percentage":
                        discount_amount = subtotal * (promo.discount_value / 100)
                        if promo.max_discount_amount:
                            discount_amount = min(discount_amount, promo.max_discount_amount)
                    else:  # fixed
                        discount_amount = min(promo.discount_value, subtotal)
                    
                    promo_code = promo.code
                    
                    # Increment usage count
                    await db.promo_codes.update_one(
                        {"id": promo.id},
                        {"$inc": {"usage_count": 1}}
                    )
        except Exception as e:
            logger.warning(f"Error applying promo code: {e}")
    
    total = subtotal + shipping_cost - discount_amount
    
    # Batch fetch all products (optimization: avoid N+1 query)
    product_ids = [item.product_id for item in order_data.items]
    products = await db.products.find(
        {"id": {"$in": product_ids}},
        {"_id": 0}
    ).to_list(len(product_ids))
    products_dict = {p["id"]: p for p in products}
    
    # Check stock availability and decrement
    for item in order_data.items:
        product = products_dict.get(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Produit {item.product_id} introuvable")
            
        if product.get('track_inventory', True):
            current_stock = product.get('stock_quantity', 0)
            allow_backorder = product.get('allow_backorder', False)
            
            # Check if enough stock
            if current_stock < item.quantity and not allow_backorder:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuffisant pour {item.product_name}. Disponible: {current_stock}"
                )
            
            # Decrement stock
            new_stock = max(0, current_stock - item.quantity)
            await db.products.update_one(
                {"id": item.product_id},
                {
                    "$set": {
                        "stock_quantity": new_stock,
                        "in_stock": new_stock > 0 or allow_backorder
                    }
                }
            )
            
            # Log stock adjustment
            adjustment = StockAdjustment(
                product_id=item.product_id,
                adjustment_type="order",
                quantity=-item.quantity,
                reason=f"Commande #{order.order_number if 'order' in locals() else 'N/A'}",
                notes=f"Décrémenté par commande"
            )
            await db.stock_adjustments.insert_one(adjustment.model_dump())
    
    # Create order
    order = Order(
        **order_data.model_dump(exclude={'promo_code'}),
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        promo_code=promo_code,
        discount_amount=discount_amount,
        total=total
    )
    
    # Save to database
    await db.orders.insert_one(order.model_dump())
    
    # Send confirmation email in background
    background_tasks.add_task(
        send_order_confirmation_email,
        order
    )
    
    return order

@api_router.get("/orders/{order_id}", response_model=Order)
async def get_order_public(order_id: str):
    """Get order details (public - by order ID)"""
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(**order)

@api_router.get("/my-orders", response_model=List[Order])
async def get_my_orders(current_user: User = Depends(get_current_user)):
    """Get current user's orders"""
    orders = await db.orders.find(
        {"$or": [{"user_id": current_user.id}, {"customer_email": current_user.email}]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(1000)
    return [Order(**order) for order in orders]

@api_router.get("/admin/orders", response_model=List[Order])
async def get_all_orders_admin(admin: User = Depends(get_admin_user)):
    """Get all orders (admin only)"""
    orders = await db.orders.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [Order(**order) for order in orders]

@api_router.get("/admin/orders/{order_id}", response_model=Order)
async def get_order_admin(order_id: str, admin: User = Depends(get_admin_user)):
    """Get order details (admin only)"""
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(**order)

@api_router.put("/admin/orders/{order_id}", response_model=Order)
async def update_order_status(
    order_id: str,
    order_data: OrderUpdate,
    admin: User = Depends(get_admin_user),
    background_tasks: BackgroundTasks = None
):
    """Update order status (admin only)"""
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    update_data = {k: v for k, v in order_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    if update_data:
        await db.orders.update_one({"id": order_id}, {"$set": update_data})
        order.update(update_data)
    
    # Send status update email if status changed
    if "status" in update_data and background_tasks:
        background_tasks.add_task(
            send_order_status_email,
            Order(**order)
        )
    
    return Order(**order)

def send_order_confirmation_email(order: Order):
    """Send order confirmation email"""
    try:
        from email_service import email_service
        
        subject = f"Confirmation de commande #{order.order_number}"
        
        items_html = "".join([
            f"<tr><td>{item.product_name}</td><td>{item.quantity}</td><td>{item.price:.2f} EUR</td></tr>"
            for item in order.items
        ])
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #6B8E23;">Merci pour votre commande !</h2>
            <p>Bonjour {order.customer_name},</p>
            <p>Votre commande <strong>#{order.order_number}</strong> a été reçue avec succès.</p>
            <h3>Détails de la commande :</h3>
            <table border="1" cellpadding="10" style="border-collapse: collapse;">
                <tr><th>Produit</th><th>Quantité</th><th>Prix</th></tr>
                {items_html}
                <tr><td colspan="2"><strong>Total</strong></td><td><strong>{order.total:.2f} EUR</strong></td></tr>
            </table>
            <p><strong>Adresse de livraison :</strong><br>{order.shipping_address}<br>{order.shipping_city}</p>
            <p>Nous vous contacterons bientôt pour confirmer la livraison.</p>
            <p>Cordialement,<br>L'équipe Délices et Trésors d'Algérie</p>
        </body>
        </html>
        """
        
        email_service.send_email(order.customer_email, subject, "Confirmation de commande", body_html)
    except Exception as e:
        print(f"Error sending order confirmation email: {e}")

def send_order_status_email(order: Order):
    """Send order status update email"""
    try:
        from email_service import email_service
        
        status_fr = {
            "pending": "En attente",
            "confirmed": "Confirmée",
            "processing": "En préparation",
            "shipped": "Expédiée",
            "delivered": "Livrée",
            "cancelled": "Annulée"
        }
        
        subject = f"Mise à jour commande #{order.order_number}"
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #6B8E23;">Mise à jour de votre commande</h2>
            <p>Bonjour {order.customer_name},</p>
            <p>Le statut de votre commande <strong>#{order.order_number}</strong> a été mis à jour :</p>
            <p style="font-size: 18px; color: #6B8E23;"><strong>{status_fr.get(order.status, order.status)}</strong></p>
            <p>Cordialement,<br>L'équipe Délices et Trésors d'Algérie</p>
        </body>
        </html>
        """
        
        email_service.send_email(order.customer_email, subject, "Mise à jour commande", body_html)
    except Exception as e:
        print(f"Error sending status email: {e}")

# --- Contact Routes ---
@api_router.post("/contact", response_model=ContactMessage)
async def create_contact_message(contact_data: ContactMessageCreate, background_tasks: BackgroundTasks):
    """Submit a contact form message"""
    # Create contact message
    contact_dict = contact_data.model_dump()
    contact_message = ContactMessage(**contact_dict)
    
    # Save to database
    await db.contact_messages.insert_one(contact_message.model_dump())
    
    # Send email notification in background
    background_tasks.add_task(
        email_service.send_contact_notification,
        contact_dict
    )
    
    return contact_message

@api_router.get("/admin/contact-messages", response_model=List[ContactMessage])
async def get_contact_messages(admin: User = Depends(get_admin_user)):
    """Get all contact messages (admin only)"""
    messages = await db.contact_messages.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [ContactMessage(**msg) for msg in messages]

@api_router.get("/admin/contact-messages/{message_id}", response_model=ContactMessage)
async def get_contact_message(message_id: str, admin: User = Depends(get_admin_user)):
    """Get a specific contact message (admin only)"""
    message = await db.contact_messages.find_one({"id": message_id}, {"_id": 0})
    if not message:
        raise HTTPException(status_code=404, detail="Contact message not found")
    return ContactMessage(**message)

@api_router.put("/admin/contact-messages/{message_id}", response_model=ContactMessage)
async def update_contact_message(message_id: str, update_data: ContactMessageUpdate, admin: User = Depends(get_admin_user)):
    """Update contact message status (admin only)"""
    message = await db.contact_messages.find_one({"id": message_id}, {"_id": 0})
    if not message:
        raise HTTPException(status_code=404, detail="Contact message not found")
    
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    
    if update_dict:
        await db.contact_messages.update_one(
            {"id": message_id},
            {"$set": update_dict}
        )
        message.update(update_dict)
    
    return ContactMessage(**message)

@api_router.delete("/admin/contact-messages/{message_id}")
async def delete_contact_message(message_id: str, admin: User = Depends(get_admin_user)):
    """Delete a contact message (admin only)"""
    result = await db.contact_messages.delete_one({"id": message_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contact message not found")
    
    return {"message": "Contact message deleted successfully"}

# --- Testimonial Routes ---
@api_router.post("/testimonials", response_model=Testimonial)
async def create_testimonial(testimonial_data: TestimonialCreate):
    """Submit a new testimonial (public)"""
    testimonial = Testimonial(**testimonial_data.model_dump())
    await db.testimonials.insert_one(testimonial.model_dump())
    return testimonial

@api_router.get("/testimonials", response_model=List[Testimonial])
async def get_approved_testimonials(limit: int = 10):
    """Get approved testimonials (public)"""
    testimonials = await db.testimonials.find(
        {"is_approved": True},
        {"_id": 0}
    ).sort("approved_at", -1).limit(limit).to_list(limit)
    return [Testimonial(**t) for t in testimonials]

@api_router.get("/admin/testimonials", response_model=List[Testimonial])
async def get_all_testimonials(admin: User = Depends(get_admin_user)):
    """Get all testimonials including pending (admin only)"""
    testimonials = await db.testimonials.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [Testimonial(**t) for t in testimonials]

@api_router.get("/admin/testimonials/{testimonial_id}", response_model=Testimonial)
async def get_testimonial(testimonial_id: str, admin: User = Depends(get_admin_user)):
    """Get a specific testimonial (admin only)"""
    testimonial = await db.testimonials.find_one({"id": testimonial_id}, {"_id": 0})
    if not testimonial:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    return Testimonial(**testimonial)

@api_router.put("/admin/testimonials/{testimonial_id}", response_model=Testimonial)
async def update_testimonial(
    testimonial_id: str,
    update_data: TestimonialUpdate,
    admin: User = Depends(get_admin_user)
):
    """Update testimonial (approve/reject) (admin only)"""
    testimonial = await db.testimonials.find_one({"id": testimonial_id}, {"_id": 0})
    if not testimonial:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    
    # If approving, set approval timestamp and admin ID
    if update_dict.get("is_approved") is True:
        update_dict["approved_at"] = datetime.now(timezone.utc)
        update_dict["approved_by"] = admin.id
    
    if update_dict:
        await db.testimonials.update_one(
            {"id": testimonial_id},
            {"$set": update_dict}
        )
        testimonial.update(update_dict)
    
    return Testimonial(**testimonial)

@api_router.delete("/admin/testimonials/{testimonial_id}")
async def delete_testimonial(testimonial_id: str, admin: User = Depends(get_admin_user)):
    """Delete a testimonial (admin only)"""
    result = await db.testimonials.delete_one({"id": testimonial_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    
    return {"message": "Testimonial deleted successfully"}

# --- Navigation Menu Routes ---
@api_router.get("/navigation", response_model=List[NavigationItem])
async def get_navigation_menu():
    """Get active navigation items (public)"""
    items = await db.navigation.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(1000)
    return [NavigationItem(**item) for item in items]

@api_router.get("/admin/navigation", response_model=List[NavigationItem])
async def get_all_navigation_items(admin: User = Depends(get_admin_user)):
    """Get all navigation items including inactive (admin only)"""
    items = await db.navigation.find({}, {"_id": 0}).sort("order", 1).to_list(1000)
    return [NavigationItem(**item) for item in items]

@api_router.post("/admin/navigation", response_model=NavigationItem)
async def create_navigation_item(item_data: NavigationItemCreate, admin: User = Depends(get_admin_user)):
    """Create a new navigation item (admin only)"""
    item = NavigationItem(**item_data.model_dump())
    await db.navigation.insert_one(item.model_dump())
    return item

@api_router.get("/admin/navigation/{item_id}", response_model=NavigationItem)
async def get_navigation_item(item_id: str, admin: User = Depends(get_admin_user)):
    """Get a specific navigation item (admin only)"""
    item = await db.navigation.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(status_code=404, detail="Navigation item not found")
    return NavigationItem(**item)

@api_router.put("/admin/navigation/{item_id}", response_model=NavigationItem)
async def update_navigation_item(
    item_id: str,
    item_data: NavigationItemUpdate,
    admin: User = Depends(get_admin_user)
):
    """Update a navigation item (admin only)"""
    item = await db.navigation.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(status_code=404, detail="Navigation item not found")
    
    update_dict = {k: v for k, v in item_data.model_dump().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc)
    
    if update_dict:
        await db.navigation.update_one({"id": item_id}, {"$set": update_dict})
        item.update(update_dict)
    
    return NavigationItem(**item)

@api_router.delete("/admin/navigation/{item_id}")
async def delete_navigation_item(item_id: str, admin: User = Depends(get_admin_user)):
    """Delete a navigation item (admin only)"""
    result = await db.navigation.delete_one({"id": item_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Navigation item not found")
    
    return {"message": "Navigation item deleted successfully"}

@api_router.post("/admin/navigation/reorder")
async def reorder_navigation_items(
    items_order: List[Dict[str, Any]],
    admin: User = Depends(get_admin_user)
):
    """Reorder navigation items (admin only)"""
    # items_order format: [{"id": "...", "order": 0}, {"id": "...", "order": 1}, ...]
    for item_order in items_order:
        await db.navigation.update_one(
            {"id": item_order["id"]},
            {"$set": {"order": item_order["order"], "updated_at": datetime.now(timezone.utc)}}
        )
    
    return {"message": "Navigation items reordered successfully"}

# --- Footer Routes ---
@api_router.get("/footer", response_model=FooterSettings)
async def get_footer_settings():
    """Get footer settings (public)"""
    footer = await db.footer_settings.find_one({"id": "footer_config"}, {"_id": 0})
    if not footer:
        # Return default footer if none exists
        default_footer = FooterSettings()
        return default_footer
    return FooterSettings(**footer)

@api_router.put("/admin/footer", response_model=FooterSettings)
async def update_footer_settings(
    footer_data: FooterSettingsUpdate,
    admin: User = Depends(get_admin_user)
):
    """Update footer settings (admin only)"""
    footer = await db.footer_settings.find_one({"id": "footer_config"}, {"_id": 0})
    
    update_dict = {k: v for k, v in footer_data.model_dump().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc)
    
    if footer:
        await db.footer_settings.update_one(
            {"id": "footer_config"},
            {"$set": update_dict}
        )
        footer.update(update_dict)
        return FooterSettings(**footer)
    else:
        # Create new footer settings
        new_footer = FooterSettings(**update_dict)
        await db.footer_settings.insert_one(new_footer.model_dump())
        return new_footer

# --- Banner/Slider Routes ---
@api_router.get("/banners", response_model=List[Banner])
async def get_active_banners():
    """Get active banners (public)"""
    banners = await db.banners.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(1000)
    return [Banner(**b) for b in banners]

@api_router.get("/admin/banners", response_model=List[Banner])
async def get_all_banners(admin: User = Depends(get_admin_user)):
    """Get all banners including inactive (admin only)"""
    banners = await db.banners.find({}, {"_id": 0}).sort("order", 1).to_list(1000)
    return [Banner(**b) for b in banners]

@api_router.post("/admin/banners", response_model=Banner)
async def create_banner(banner_data: BannerCreate, admin: User = Depends(get_admin_user)):
    """Create a new banner (admin only)"""
    banner = Banner(**banner_data.model_dump())
    await db.banners.insert_one(banner.model_dump())
    return banner

@api_router.get("/admin/banners/{banner_id}", response_model=Banner)
async def get_banner(banner_id: str, admin: User = Depends(get_admin_user)):
    """Get a specific banner (admin only)"""
    banner = await db.banners.find_one({"id": banner_id}, {"_id": 0})
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    return Banner(**banner)

@api_router.put("/admin/banners/{banner_id}", response_model=Banner)
async def update_banner(
    banner_id: str,
    banner_data: BannerUpdate,
    admin: User = Depends(get_admin_user)
):
    """Update a banner (admin only)"""
    banner = await db.banners.find_one({"id": banner_id}, {"_id": 0})
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    
    update_dict = {k: v for k, v in banner_data.model_dump().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc)
    
    if update_dict:
        await db.banners.update_one({"id": banner_id}, {"$set": update_dict})
        banner.update(update_dict)
    
    return Banner(**banner)

@api_router.delete("/admin/banners/{banner_id}")
async def delete_banner(banner_id: str, admin: User = Depends(get_admin_user)):
    """Delete a banner (admin only)"""
    result = await db.banners.delete_one({"id": banner_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Banner not found")
    
    return {"message": "Banner deleted successfully"}

@api_router.post("/admin/banners/reorder")
async def reorder_banners(
    banners_order: List[Dict[str, Any]],
    admin: User = Depends(get_admin_user)
):
    """Reorder banners (admin only)"""
    for banner_order in banners_order:
        await db.banners.update_one(
            {"id": banner_order["id"]},
            {"$set": {"order": banner_order["order"], "updated_at": datetime.now(timezone.utc)}}
        )
    
    return {"message": "Banners reordered successfully"}

# --- Order Routes ---
@api_router.post("/orders", response_model=Order)
async def create_order(order_data: OrderCreate):
    """Create a new order (public)"""
    # Calculate totals
    subtotal = sum(item.price * item.quantity for item in order_data.items)
    shipping_cost = 0.0  # Free shipping for now
    total = subtotal + shipping_cost
    
    order = Order(
        **order_data.model_dump(),
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        total=total
    )
    
    await db.orders.insert_one(order.model_dump())
    
    # TODO: Send confirmation email
    
    return order

@api_router.get("/orders/my-orders", response_model=List[Order])
async def get_my_orders(current_user: User = Depends(get_current_user)):
    """Get orders for the logged-in user"""
    orders = await db.orders.find(
        {"customer_email": current_user.email},
        {"_id": 0}
    ).sort("created_at", -1).to_list(1000)
    return [Order(**o) for o in orders]

@api_router.get("/admin/orders", response_model=List[Order])
async def get_all_orders(admin: User = Depends(get_admin_user)):
    """Get all orders (admin only)"""
    orders = await db.orders.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [Order(**o) for o in orders]

@api_router.get("/admin/orders/{order_id}", response_model=Order)
async def get_order(order_id: str, admin: User = Depends(get_admin_user)):
    """Get a specific order (admin only)"""
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(**order)

@api_router.put("/admin/orders/{order_id}", response_model=Order)
async def update_order(
    order_id: str,
    order_data: OrderUpdate,
    admin: User = Depends(get_admin_user)
):
    """Update order status (admin only)"""
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    update_dict = {k: v for k, v in order_data.model_dump().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc)
    
    if update_dict:
        await db.orders.update_one({"id": order_id}, {"$set": update_dict})
        order.update(update_dict)
    
    # TODO: Send status update email to customer
    
    return Order(**order)

@api_router.delete("/admin/orders/{order_id}")
async def delete_order(order_id: str, admin: User = Depends(get_admin_user)):
    """Delete an order (admin only)"""
    result = await db.orders.delete_one({"id": order_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"message": "Order deleted successfully"}

# --- Newsletter Routes ---
@api_router.post("/newsletter/subscribe", response_model=NewsletterSubscriber)
async def subscribe_newsletter(subscriber_data: NewsletterSubscribe):
    """Subscribe to newsletter (public)"""
    # Check if already subscribed
    existing = await db.newsletter_subscribers.find_one({"email": subscriber_data.email}, {"_id": 0})
    
    if existing:
        if existing.get("is_active"):
            raise HTTPException(status_code=400, detail="Email already subscribed")
        else:
            # Reactivate subscription
            await db.newsletter_subscribers.update_one(
                {"email": subscriber_data.email},
                {"$set": {"is_active": True, "subscribed_at": datetime.now(timezone.utc)}}
            )
            existing["is_active"] = True
            return NewsletterSubscriber(**existing)
    
    subscriber = NewsletterSubscriber(**subscriber_data.model_dump())
    await db.newsletter_subscribers.insert_one(subscriber.model_dump())
    return subscriber

@api_router.get("/admin/newsletter/subscribers", response_model=List[NewsletterSubscriber])
async def get_newsletter_subscribers(admin: User = Depends(get_admin_user)):
    """Get all newsletter subscribers (admin only)"""
    subscribers = await db.newsletter_subscribers.find({}, {"_id": 0}).sort("subscribed_at", -1).to_list(1000)
    return [NewsletterSubscriber(**s) for s in subscribers]

@api_router.delete("/admin/newsletter/subscribers/{subscriber_id}")
async def delete_newsletter_subscriber(subscriber_id: str, admin: User = Depends(get_admin_user)):
    """Delete a newsletter subscriber (admin only)"""
    result = await db.newsletter_subscribers.delete_one({"id": subscriber_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    
    return {"message": "Subscriber deleted successfully"}

# --- Custom Pages Routes ---
@api_router.get("/pages", response_model=List[CustomPage])
async def get_published_pages():
    """Get all published pages (public)"""
    pages = await db.custom_pages.find({"is_published": True}, {"_id": 0}).sort("menu_order", 1).to_list(1000)
    return [CustomPage(**page) for page in pages]

@api_router.get("/pages/{slug}", response_model=CustomPage)
async def get_page_by_slug(slug: str):
    """Get a specific published page by slug (public)"""
    page = await db.custom_pages.find_one({"slug": slug, "is_published": True}, {"_id": 0})
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return CustomPage(**page)

@api_router.get("/admin/pages", response_model=List[CustomPage])
async def get_all_pages_admin(admin: User = Depends(get_admin_user)):
    """Get all pages including drafts (admin only)"""
    pages = await db.custom_pages.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [CustomPage(**page) for page in pages]

@api_router.post("/admin/pages", response_model=CustomPage)
async def create_page(page_data: CustomPageCreate, admin: User = Depends(get_admin_user)):
    """Create a new custom page (admin only)"""
    page = CustomPage(**page_data.model_dump())
    await db.custom_pages.insert_one(page.model_dump())
    return page

@api_router.get("/admin/pages/{page_id}", response_model=CustomPage)
async def get_page_admin(page_id: str, admin: User = Depends(get_admin_user)):
    """Get a specific page (admin only)"""
    page = await db.custom_pages.find_one({"id": page_id}, {"_id": 0})
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return CustomPage(**page)

@api_router.put("/admin/pages/{page_id}", response_model=CustomPage)
async def update_page(page_id: str, page_data: CustomPageUpdate, admin: User = Depends(get_admin_user)):
    """Update a custom page (admin only)"""
    page = await db.custom_pages.find_one({"id": page_id}, {"_id": 0})
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    update_data = {k: v for k, v in page_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    if update_data:
        await db.custom_pages.update_one({"id": page_id}, {"$set": update_data})
        page.update(update_data)
    
    return CustomPage(**page)

@api_router.delete("/admin/pages/{page_id}")
async def delete_page(page_id: str, admin: User = Depends(get_admin_user)):
    """Delete a custom page (admin only)"""
    result = await db.custom_pages.delete_one({"id": page_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"message": "Page deleted successfully"}

# --- Customization Routes ---
@api_router.get("/customization", response_model=SiteCustomization)
async def get_customization():
    """Get site customization settings (public)"""
    customization = await db.customization.find_one({"id": "site_customization"}, {"_id": 0})
    
    if not customization:
        # Return default values if not found
        default_customization = SiteCustomization()
        await db.customization.insert_one(default_customization.model_dump())
        return default_customization
    
    return SiteCustomization(**customization)

@api_router.get("/admin/customization")
async def get_customization_admin(admin: User = Depends(get_admin_user)):
    """Get site customization settings (admin only)"""
    customization = await db.customization.find_one({"id": "site_customization"}, {"_id": 0})
    
    if not customization:
        default_customization = SiteCustomization()
        await db.customization.insert_one(default_customization.model_dump())
        return default_customization.model_dump()
    
    return customization

@api_router.put("/admin/customization", response_model=SiteCustomization)
async def update_customization(
    customization_data: CustomizationUpdate,
    admin: User = Depends(get_admin_user)
):
    """Update site customization (admin only)"""
    # Get existing customization or create default
    existing = await db.customization.find_one({"id": "site_customization"}, {"_id": 0})
    
    if not existing:
        existing = SiteCustomization().model_dump()
        await db.customization.insert_one(existing)
    
    # Update with new data
    update_data = {k: v for k, v in customization_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    if update_data:
        await db.customization.update_one(
            {"id": "site_customization"},
            {"$set": update_data}
        )
    
    # Return updated customization
    updated = await db.customization.find_one({"id": "site_customization"}, {"_id": 0})
    return SiteCustomization(**updated)

# --- Promo Codes Routes ---
@api_router.get("/admin/promo-codes", response_model=List[PromoCode])
async def get_all_promo_codes(admin: User = Depends(get_admin_user)):
    """Get all promo codes (admin only)"""
    codes = await db.promo_codes.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [PromoCode(**code) for code in codes]

@api_router.post("/admin/promo-codes", response_model=PromoCode)
async def create_promo_code(
    promo_data: PromoCodeCreate,
    admin: User = Depends(get_admin_user)
):
    """Create a new promo code (admin only)"""
    # Check if code already exists
    existing = await db.promo_codes.find_one({"code": promo_data.code.upper()}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Code promo déjà existant")
    
    # Create promo code
    promo = PromoCode(
        code=promo_data.code.upper(),
        description=promo_data.description,
        discount_type=promo_data.discount_type,
        discount_value=promo_data.discount_value,
        min_order_amount=promo_data.min_order_amount,
        max_discount_amount=promo_data.max_discount_amount,
        usage_limit=promo_data.usage_limit,
        user_usage_limit=promo_data.user_usage_limit,
        valid_from=promo_data.valid_from or datetime.now(timezone.utc),
        valid_until=promo_data.valid_until,
        is_active=promo_data.is_active if promo_data.is_active is not None else True
    )
    
    await db.promo_codes.insert_one(promo.model_dump())
    return promo

@api_router.get("/admin/promo-codes/{promo_id}", response_model=PromoCode)
async def get_promo_code(promo_id: str, admin: User = Depends(get_admin_user)):
    """Get a specific promo code (admin only)"""
    code = await db.promo_codes.find_one({"id": promo_id}, {"_id": 0})
    if not code:
        raise HTTPException(status_code=404, detail="Code promo non trouvé")
    return PromoCode(**code)

@api_router.put("/admin/promo-codes/{promo_id}", response_model=PromoCode)
async def update_promo_code(
    promo_id: str,
    promo_data: PromoCodeUpdate,
    admin: User = Depends(get_admin_user)
):
    """Update a promo code (admin only)"""
    code = await db.promo_codes.find_one({"id": promo_id}, {"_id": 0})
    if not code:
        raise HTTPException(status_code=404, detail="Code promo non trouvé")
    
    update_data = {k: v for k, v in promo_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    if update_data:
        await db.promo_codes.update_one({"id": promo_id}, {"$set": update_data})
    
    updated = await db.promo_codes.find_one({"id": promo_id}, {"_id": 0})
    return PromoCode(**updated)

@api_router.delete("/admin/promo-codes/{promo_id}")
async def delete_promo_code(promo_id: str, admin: User = Depends(get_admin_user)):
    """Delete a promo code (admin only)"""
    result = await db.promo_codes.delete_one({"id": promo_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Code promo non trouvé")
    return {"message": "Code promo supprimé avec succès"}


@api_router.get("/promo-codes/active")
async def get_active_promo_codes(lang: str = "fr"):
    """Get list of active promo codes for display to customers (public)"""
    now = datetime.now(timezone.utc)
    codes = await db.promo_codes.find(
        {
            "is_active": True,
            "valid_from": {"$lte": now},
            "$or": [
                {"valid_until": {"$gte": now}},
                {"valid_until": None}
            ]
        },
        {"_id": 0}
    ).to_list(100)
    
    # Format codes for client display
    formatted_codes = []
    for code in codes:
        formatted_code = {
            "code": code.get("code"),
            "discount_type": code.get("discount_type"),
            "valid_until": code.get("valid_until")
        }
        
        # Handle multilingual description
        description = code.get("description")
        if description and isinstance(description, dict):
            # Get description in requested language, fallback to fr, then en
            formatted_code["description"] = description.get(lang) or description.get("fr") or description.get("en") or ""
        else:
            formatted_code["description"] = description or ""
            
        formatted_codes.append(formatted_code)
    
    return formatted_codes

@api_router.post("/promo-codes/validate")
async def validate_promo_code(validation: PromoCodeValidation):
    """Validate a promo code and calculate discount (public)"""
    code = await db.promo_codes.find_one(
        {"code": validation.code.upper(), "is_active": True},
        {"_id": 0}
    )
    
    if not code:
        raise HTTPException(status_code=404, detail="Code promo invalide")
    
    promo = PromoCode(**code)
    now = datetime.now(timezone.utc)
    
    # Check validity period
    if promo.valid_from:
        valid_from = promo.valid_from.replace(tzinfo=timezone.utc) if promo.valid_from.tzinfo is None else promo.valid_from
        if now < valid_from:
            raise HTTPException(status_code=400, detail="Ce code promo n'est pas encore valide")
    
    if promo.valid_until:
        valid_until = promo.valid_until.replace(tzinfo=timezone.utc) if promo.valid_until.tzinfo is None else promo.valid_until
        if now > valid_until:
            raise HTTPException(status_code=400, detail="Ce code promo a expiré")
    
    # Check usage limit
    if promo.usage_limit and promo.usage_count >= promo.usage_limit:
        raise HTTPException(status_code=400, detail="Ce code promo a atteint sa limite d'utilisation")
    
    # Check minimum order amount
    if promo.min_order_amount and validation.order_amount < promo.min_order_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Commande minimum de {promo.min_order_amount:.2f} EUR requise pour ce code"
        )
    
    # Calculate discount
    if promo.discount_type == "percentage":
        discount = validation.order_amount * (promo.discount_value / 100)
        if promo.max_discount_amount:
            discount = min(discount, promo.max_discount_amount)
    else:  # fixed
        discount = min(promo.discount_value, validation.order_amount)
    
    final_amount = validation.order_amount - discount
    
    return {
        "valid": True,
        "promo_code": promo.code,
        "discount_type": promo.discount_type,
        "discount_value": promo.discount_value,
        "discount_amount": round(discount, 2),
        "original_amount": validation.order_amount,
        "final_amount": round(final_amount, 2),
        "description": promo.description
    }

# --- Stock Management Routes ---
@api_router.get("/admin/inventory", response_model=List[Product])
async def get_inventory_overview(admin: User = Depends(get_admin_user)):
    """Get all products with inventory information (admin only)"""
    products = await db.products.find({}, {"_id": 0}).sort("name.fr", 1).to_list(1000)
    return [Product(**product) for product in products]

@api_router.get("/admin/inventory/low-stock", response_model=List[Product])
async def get_low_stock_products(admin: User = Depends(get_admin_user)):
    """Get products with low stock (admin only)"""
    products = await db.products.find(
        {
            "track_inventory": True,
            "$expr": {"$lte": ["$stock_quantity", "$low_stock_threshold"]}
        },
        {"_id": 0}
    ).to_list(1000)
    return [Product(**product) for product in products]

@api_router.post("/admin/inventory/{product_id}/adjust")
async def adjust_stock(
    product_id: str,
    adjustment: StockAdjustmentRequest,
    admin: User = Depends(get_admin_user)
):
    """Adjust stock for a product (admin only)"""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    current_stock = product.get('stock_quantity', 0)
    
    # Calculate new stock based on adjustment type
    if adjustment.adjustment_type == "set":
        new_stock = adjustment.quantity
    elif adjustment.adjustment_type == "increase":
        new_stock = current_stock + adjustment.quantity
    elif adjustment.adjustment_type == "decrease":
        new_stock = max(0, current_stock - adjustment.quantity)
    else:
        raise HTTPException(status_code=400, detail="Type d'ajustement invalide")
    
    # Update product stock
    allow_backorder = product.get('allow_backorder', False)
    await db.products.update_one(
        {"id": product_id},
        {
            "$set": {
                "stock_quantity": new_stock,
                "in_stock": new_stock > 0 or allow_backorder
            }
        }
    )
    
    # Log adjustment
    stock_adjustment = StockAdjustment(
        product_id=product_id,
        adjustment_type=adjustment.adjustment_type,
        quantity=adjustment.quantity if adjustment.adjustment_type == "set" else (
            adjustment.quantity if adjustment.adjustment_type == "increase" else -adjustment.quantity
        ),
        reason=adjustment.reason,
        notes=adjustment.notes,
        performed_by=admin.get('email') if isinstance(admin, dict) else admin.email
    )
    await db.stock_adjustments.insert_one(stock_adjustment.model_dump())
    
    # Return updated product
    updated_product = await db.products.find_one({"id": product_id}, {"_id": 0})
    return Product(**updated_product)

@api_router.get("/admin/inventory/{product_id}/history")
async def get_stock_history(
    product_id: str,
    admin: User = Depends(get_admin_user)
):
    """Get stock adjustment history for a product (admin only)"""
    adjustments = await db.stock_adjustments.find(
        {"product_id": product_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    return adjustments

# --- SEO Settings Routes ---
@api_router.get("/admin/seo-settings", response_model=SEOSettings)
async def get_seo_settings(admin: User = Depends(get_admin_user)):
    """Get SEO settings (admin only)"""
    settings = await db.seo_settings.find_one({"id": "seo_settings"}, {"_id": 0})
    if not settings:
        # Return default settings if none exist
        return SEOSettings()
    return SEOSettings(**settings)

@api_router.put("/admin/seo-settings", response_model=SEOSettings)
async def update_seo_settings(
    seo_data: SEOSettings,
    admin: User = Depends(get_admin_user)
):
    """Update SEO settings (admin only)"""
    seo_data.updated_at = datetime.now(timezone.utc)
    
    await db.seo_settings.update_one(
        {"id": "seo_settings"},
        {"$set": seo_data.model_dump()},
        upsert=True
    )
    
    updated = await db.seo_settings.find_one({"id": "seo_settings"}, {"_id": 0})
    return SEOSettings(**updated)

@api_router.get("/seo-settings")
async def get_public_seo_settings():
    """Get public SEO settings (for meta tags)"""
    settings = await db.seo_settings.find_one({"id": "seo_settings"}, {"_id": 0})
    if not settings:
        return SEOSettings().model_dump()
    return settings

# --- Customization Settings ---
class CustomizationSettings(BaseModel):
    id: str = "customization_settings"
    site_name: Dict[str, str] = {"fr": "Délices et Trésors", "ar": "لذائذ وكنوز الجزائر", "en": "Delights & Treasures"}
    tagline: Dict[str, str] = {"fr": "Saveurs authentiques d'Algérie", "ar": "نكهات أصيلة من الجزائر", "en": "Authentic Algerian Flavors"}
    logo_url: str = ""
    favicon_url: str = ""
    primary_color: str = "#6B8E23"
    secondary_color: str = "#8B7355"
    accent_color: str = "#F59E0B"
    font_heading: str = "Inter"
    font_body: str = "Inter"

@api_router.get("/admin/customization")
async def get_customization_settings(current_user: User = Depends(get_current_user)):
    """Get customization settings"""
    settings = await db.customization_settings.find_one({"id": "customization_settings"}, {"_id": 0})
    if not settings:
        return CustomizationSettings().model_dump()
    return settings

@api_router.put("/admin/customization")
async def update_customization_settings(settings: CustomizationSettings, current_user: User = Depends(get_current_user)):
    """Update customization settings"""
    await db.customization_settings.update_one(
        {"id": "customization_settings"},
        {"$set": settings.model_dump()},
        upsert=True
    )
    return {"message": "Customization settings updated successfully"}

@api_router.get("/customization")
async def get_public_customization():
    """Get public customization settings"""
    settings = await db.customization_settings.find_one({"id": "customization_settings"}, {"_id": 0})
    if not settings:
        return CustomizationSettings().model_dump()
    return settings

# --- General Settings ---
class GeneralSettings(BaseModel):
    id: str = "general_settings"
    site_title: Dict[str, str] = {"fr": "", "ar": "", "en": ""}
    site_description: Dict[str, str] = {"fr": "", "ar": "", "en": ""}
    contact_email: str = ""
    support_email: str = ""
    contact_email_2: str = ""
    contact_email_3: str = ""
    phone: str = ""
    phone_2: str = ""
    phone_3: str = ""
    address: Dict[str, str] = {"fr": "", "ar": "", "en": ""}
    address_2: Dict[str, str] = {"fr": "", "ar": "", "en": ""}
    address_3: Dict[str, str] = {"fr": "", "ar": "", "en": ""}
    show_phone_2: bool = False
    show_phone_3: bool = False
    show_email_2: bool = False
    show_email_3: bool = False
    show_address_2: bool = False
    show_address_3: bool = False
    timezone: str = "Europe/Paris"
    currency: str = "EUR"
    currency_symbol: str = "€"
    date_format: str = "DD/MM/YYYY"
    facebook_url: str = ""
    instagram_url: str = ""
    twitter_url: str = ""
    linkedin_url: str = ""

@api_router.get("/admin/settings")
async def get_general_settings(current_user: User = Depends(get_current_user)):
    """Get general settings"""
    settings = await db.general_settings.find_one({"id": "general_settings"}, {"_id": 0})
    if not settings:
        return GeneralSettings().model_dump()
    return settings

@api_router.put("/admin/settings")
async def update_general_settings(settings: GeneralSettings, current_user: User = Depends(get_current_user)):
    """Update general settings"""
    await db.general_settings.update_one(
        {"id": "general_settings"},
        {"$set": settings.model_dump()},
        upsert=True
    )
    return {"message": "General settings updated successfully"}

@api_router.get("/settings")
async def get_public_settings():
    """Get public general settings"""
    settings = await db.general_settings.find_one({"id": "general_settings"}, {"_id": 0})
    if not settings:
        return GeneralSettings().model_dump()
    return settings


# --- Basic Routes ---
@api_router.get("/")
async def root():
    return {"message": "Soumam Heritage API", "version": "1.0"}

# Include the router in the main app
app.include_router(api_router)

# CORS Configuration for custom domains
cors_origins_str = os.environ.get('CORS_ORIGINS', '')
if cors_origins_str == '*':
    cors_origins = ['*']
else:
    cors_origins = [origin.strip() for origin in cors_origins_str.split(',') if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()