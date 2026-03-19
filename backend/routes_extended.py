from fastapi import APIRouter, HTTPException, status, Header, UploadFile, File
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr
from pathlib import Path
import jwt
import os
import uuid as uuid_mod
import aiofiles

router = APIRouter(prefix="/api")

UPLOAD_DIR = Path(__file__).parent / "uploads"

# Will be injected
db = None
SECRET_KEY = None

def init_routes(database, secret):
    global db, SECRET_KEY
    db = database
    SECRET_KEY = secret

from models import ReviewCreate, WishlistAdd, StockAlertCreate, ShippingCalculation, ShippingResult

async def get_current_user_from_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_email = payload.get("sub")
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"email": user_email}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============ REVIEWS ============

@router.get("/products/{product_id}/reviews")
async def get_product_reviews(
    product_id: str,
    rating: Optional[int] = None,
    has_photo: Optional[bool] = None,
    verified_only: Optional[bool] = None,
    sort: str = "recent",
    skip: int = 0,
    limit: int = 20
):
    query = {"product_id": product_id}
    if rating:
        query["rating"] = rating
    if has_photo:
        query["photos.0"] = {"$exists": True}
    if verified_only:
        query["verified_purchase"] = True
    
    sort_opts = {"recent": [("created_at", -1)], "helpful": [("helpful_count", -1)], 
                 "rating_high": [("rating", -1)], "rating_low": [("rating", 1)]}
    
    reviews = await db.reviews.find(query, {"_id": 0}).sort(sort_opts.get(sort, [("created_at", -1)])).skip(skip).limit(limit).to_list(length=limit)
    
    total = await db.reviews.count_documents(query)
    return {"reviews": reviews, "total": total, "page": skip // limit + 1, "pages": (total + limit - 1) // limit}

@router.post("/reviews", status_code=status.HTTP_201_CREATED)
async def create_review(review_data: ReviewCreate, authorization: str = Header(None)):
    current_user = await get_current_user_from_token(authorization)
    
    product = await db.products.find_one({"id": review_data.product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing = await db.reviews.find_one({"product_id": review_data.product_id, "user_id": current_user['id']}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")
    
    order = await db.orders.find_one({"user_id": current_user['id'], "items.product_id": review_data.product_id, "status": "delivered"}, {"_id": 0})
    
    review_dict = review_data.dict()
    review_dict.update({
        "id": str(__import__('uuid').uuid4()),
        "user_id": current_user['id'],
        "user_name": current_user.get('full_name', 'User'),
        "verified_purchase": bool(order),
        "helpful_count": 0,
        "helpful_voters": [],
        "created_at": datetime.now(timezone.utc)
    })
    
    await db.reviews.insert_one(review_dict)
    await update_product_reviews_summary(review_data.product_id)
    
    review_dict.pop('_id', None)
    return review_dict

@router.post("/reviews/{review_id}/helpful")
async def mark_review_helpful(review_id: str, authorization: str = Header(None)):
    current_user = await get_current_user_from_token(authorization)
    
    review = await db.reviews.find_one({"id": review_id}, {"_id": 0})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    helpful_voters = review.get("helpful_voters", [])
    user_id = current_user['id']
    
    if user_id in helpful_voters:
        await db.reviews.update_one({"id": review_id}, {"$pull": {"helpful_voters": user_id}, "$inc": {"helpful_count": -1}})
        return {"helpful": False, "count": review["helpful_count"] - 1}
    else:
        await db.reviews.update_one({"id": review_id}, {"$push": {"helpful_voters": user_id}, "$inc": {"helpful_count": 1}})
        return {"helpful": True, "count": review["helpful_count"] + 1}

async def update_product_reviews_summary(product_id: str):
    reviews = await db.reviews.find({"product_id": product_id}, {"_id": 0}).to_list(length=None)
    if not reviews:
        return
    
    total = len(reviews)
    average = round(sum(r["rating"] for r in reviews) / total, 1)
    distribution = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
    for review in reviews:
        distribution[str(review["rating"])] += 1
    
    await db.products.update_one({"id": product_id}, {"$set": {"reviews_summary": {"average_rating": average, "total_reviews": total, "rating_distribution": distribution}}})


# ============ REVIEW IMAGE UPLOAD ============

@router.post("/reviews/upload-image")
async def upload_review_image(
    file: UploadFile = File(...),
    authorization: str = Header(None)
):
    """Upload an image for a review (authenticated users)"""
    await get_current_user_from_token(authorization)
    
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG and WebP images are allowed")
    
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid_mod.uuid4()}.{ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    file_size = 0
    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await file.read(1024 * 64):
            file_size += len(chunk)
            if file_size > 5 * 1024 * 1024:
                if file_path.exists():
                    file_path.unlink()
                raise HTTPException(status_code=400, detail="Image size exceeds 5MB limit")
            await f.write(chunk)
    
    return {"url": f"/api/uploads/{unique_filename}", "filename": unique_filename}

# ============ WISHLIST ============

@router.get("/wishlist")
async def get_wishlist(authorization: str = Header(None)):
    current_user = await get_current_user_from_token(authorization)
    wishlist = await db.wishlists.find_one({"user_id": current_user['id']}, {"_id": 0})
    if not wishlist:
        return {"items": [], "total": 0}
    
    items_with_details = []
    for item in wishlist.get("items", []):
        product = await db.products.find_one({"id": item["product_id"]}, {"_id": 0})
        if product:
            items_with_details.append({**item, "product": product})
    
    return {"items": items_with_details, "total": len(items_with_details)}

@router.post("/wishlist")
async def add_to_wishlist(item: WishlistAdd, authorization: str = Header(None)):
    current_user = await get_current_user_from_token(authorization)
    
    product = await db.products.find_one({"id": item.product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    wishlist = await db.wishlists.find_one({"user_id": current_user['id']}, {"_id": 0})
    if not wishlist:
        wishlist_dict = {"id": str(__import__('uuid').uuid4()), "user_id": current_user['id'], "items": [], "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)}
        await db.wishlists.insert_one(wishlist_dict)
        wishlist = wishlist_dict
    
    existing = any(i["product_id"] == item.product_id and i.get("variant_id") == item.variant_id for i in wishlist.get("items", []))
    if existing:
        raise HTTPException(status_code=400, detail="Item already in wishlist")
    
    wishlist_item = {"product_id": item.product_id, "variant_id": item.variant_id, "added_at": datetime.now(timezone.utc)}
    await db.wishlists.update_one({"user_id": current_user['id']}, {"$push": {"items": wishlist_item}, "$set": {"updated_at": datetime.now(timezone.utc)}})
    
    return {"message": "Added to wishlist", "item": wishlist_item}

@router.delete("/wishlist/{product_id}")
async def remove_from_wishlist(product_id: str, variant_id: Optional[str] = None, authorization: str = Header(None)):
    current_user = await get_current_user_from_token(authorization)
    query = {"product_id": product_id}
    if variant_id: query["variant_id"] = variant_id
    
    result = await db.wishlists.update_one({"user_id": current_user['id']}, {"$pull": {"items": query}, "$set": {"updated_at": datetime.now(timezone.utc)}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found in wishlist")
    return {"message": "Removed from wishlist"}

# ============ STOCK ALERTS ============

@router.post("/stock-alerts")
async def create_stock_alert(alert_data: StockAlertCreate):
    product = await db.products.find_one({"id": alert_data.product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing = await db.stock_alerts.find_one({"email": alert_data.email, "product_id": alert_data.product_id, "variant_id": alert_data.variant_id, "notified": False}, {"_id": 0})
    if existing:
        return {"message": "Alert already exists", "alert": existing}
    
    alert_dict = alert_data.dict()
    alert_dict.update({"id": str(__import__('uuid').uuid4()), "notified": False, "created_at": datetime.now(timezone.utc)})
    await db.stock_alerts.insert_one(alert_dict)
    alert_dict.pop('_id', None)
    
    return {"message": "Stock alert created", "alert": alert_dict}

@router.get("/admin/stock-alerts")
async def get_pending_stock_alerts(authorization: str = Header(None)):
    current_user = await get_current_user_from_token(authorization)
    if current_user.get('role') != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    alerts = await db.stock_alerts.find({"notified": False}, {"_id": 0}).to_list(length=None)
    return {"alerts": alerts, "total": len(alerts)}

# ============ SHIPPING ============

@router.post("/shipping/calculate", response_model=ShippingResult)
async def calculate_shipping(calculation: ShippingCalculation):
    rule = await db.shipping_rules.find_one({"destination_country": calculation.destination_country}, {"_id": 0})
    if not rule:
        rule = {"weight_brackets": [{"max_kg": 1, "standard_price": 6.90, "express_price": 12.90}, {"max_kg": 5, "standard_price": 9.90, "express_price": 17.90}, {"max_kg": 999, "standard_price": 14.90, "express_price": 24.90}], "free_shipping_threshold": 50.0}
    
    total_weight = 0
    total_value = 0
    for item in calculation.items:
        product = await db.products.find_one({"id": item["product_id"]}, {"_id": 0})
        if product:
            variant = next((v for v in product.get("variants", []) if v["id"] == item.get("variant_id")), product.get("variants", [{}])[0] if product.get("variants") else {})
            total_weight += variant.get("weight_kg", 0.5) * item.get("quantity", 1)
            total_value += variant.get("price", 0) * item.get("quantity", 1)
    
    standard_price = 0
    express_price = 0
    for bracket in rule["weight_brackets"]:
        if total_weight <= bracket["max_kg"]:
            standard_price = bracket["standard_price"]
            express_price = bracket["express_price"]
            break
    
    free_threshold = rule.get("free_shipping_threshold", 50.0)
    if total_value >= free_threshold:
        standard_price = 0
    
    return ShippingResult(standard={"price": standard_price, "delivery_days": "5-7", "name": "Standard"}, express={"price": express_price, "delivery_days": "2-3", "name": "Express"}, free_threshold=free_threshold, current_total=total_value, amount_to_free_shipping=max(0, free_threshold - total_value))

# ============ REGIONS ============

@router.get("/regions")
async def get_regions():
    regions = await db.regions.find({}, {"_id": 0}).to_list(length=None)
    return regions

@router.get("/regions/{region_id}")
async def get_region(region_id: str):
    region = await db.regions.find_one({"id": region_id}, {"_id": 0})
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    products = await db.products.find({"origin.region_id": region_id}, {"_id": 0}).to_list(length=None)
    region["products"] = products
    return region

# ============ RECOMMENDATIONS ============

@router.get("/products/{product_id}/recommendations")
async def get_product_recommendations(product_id: str):
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    cached = await db.recommendations.find_one({"product_id": product_id}, {"_id": 0})
    if cached:
        frequently_bought = await db.products.find({"id": {"$in": cached.get("frequently_bought_together", [])}}, {"_id": 0}).to_list(length=4)
        similar = await db.products.find({"id": {"$in": cached.get("similar_products", [])}}, {"_id": 0}).to_list(length=4)
    else:
        similar = await db.products.find({"category": product.get("category"), "id": {"$ne": product_id}}, {"_id": 0}).limit(4).to_list(length=4)
        frequently_bought = []
    
    return {"frequently_bought_together": frequently_bought, "similar_products": similar}

@router.post("/cart/recommendations")
async def get_cart_recommendations(items: List[Dict]):
    product_ids = [item["product_id"] for item in items]
    recommendations = await db.recommendations.find({"product_id": {"$in": product_ids}}, {"_id": 0}).to_list(length=None)
    
    suggested_ids = set()
    for rec in recommendations:
        suggested_ids.update(rec.get("frequently_bought_together", []))
    suggested_ids -= set(product_ids)
    
    suggestions = await db.products.find({"id": {"$in": list(suggested_ids)}}, {"_id": 0}).limit(6).to_list(length=6)
    return {"recommendations": suggestions}

# ============ FILTERS ============

@router.get("/products/filter/advanced")
async def filter_products_advanced(
    category: Optional[str] = None, price_min: Optional[float] = None, price_max: Optional[float] = None,
    origin: Optional[str] = None, labels: Optional[str] = None, in_stock: Optional[bool] = None,
    rating_min: Optional[float] = None, search: Optional[str] = None, sort: str = "recent", skip: int = 0, limit: int = 20
):
    query = {}
    if search:
        query["$or"] = [
            {"name.fr": {"$regex": search, "$options": "i"}},
            {"name.en": {"$regex": search, "$options": "i"}},
            {"name.ar": {"$regex": search, "$options": "i"}},
            {"description.fr": {"$regex": search, "$options": "i"}},
        ]
    if category: query["category"] = category
    if origin: query["origin.region_id"] = origin
    if labels: query["labels"] = {"$in": labels.split(",")}
    if in_stock: query["variants.stock_quantity"] = {"$gt": 0}
    if rating_min: query["reviews_summary.average_rating"] = {"$gte": rating_min}
    if price_min is not None or price_max is not None:
        price_query = {}
        if price_min is not None: price_query["$gte"] = price_min
        if price_max is not None: price_query["$lte"] = price_max
        query["variants.price"] = price_query
    
    sort_opts = {"recent": [("created_at", -1)], "price_low": [("variants.0.price", 1)], "price_high": [("variants.0.price", -1)], "rating": [("reviews_summary.average_rating", -1)], "popular": [("reviews_summary.total_reviews", -1)]}
    products = await db.products.find(query, {"_id": 0}).sort(sort_opts.get(sort, [("created_at", -1)])).skip(skip).limit(limit).to_list(length=limit)
    
    total = await db.products.count_documents(query)
    return {"products": products, "total": total, "page": skip // limit + 1, "pages": (total + limit - 1) // limit}