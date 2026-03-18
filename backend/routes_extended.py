from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import os
from models import (
    Review, ReviewCreate, ReviewHelpful,
    Wishlist, WishlistAdd,
    StockAlert, StockAlertCreate,
    ShippingCalculation, ShippingResult,
    Region, Recommendation
)
from server import db, get_current_user, User

router = APIRouter(prefix="/api")

# ============ REVIEWS ROUTES ============

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
    
    sort_options = {
        "recent": [("created_at", -1)],
        "helpful": [("helpful_count", -1)],
        "rating_high": [("rating", -1)],
        "rating_low": [("rating", 1)]
    }
    
    reviews = await db.reviews.find(query).sort(
        sort_options.get(sort, [("created_at", -1)])
    ).skip(skip).limit(limit).to_list(length=limit)
    
    # Remove _id from all reviews
    for review in reviews:
        if '_id' in review:
            del review['_id']
    
    total = await db.reviews.count_documents(query)
    
    return {
        "reviews": reviews,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }

@router.post("/reviews", status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user)
):
    # Check if product exists
    product = await db.products.find_one({"id": review_data.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if user already reviewed this product
    existing = await db.reviews.find_one({
        "product_id": review_data.product_id,
        "user_id": current_user.id
    })
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")
    
    # Check if verified purchase
    order = await db.orders.find_one({
        "user_id": current_user.id,
        "items.product_id": review_data.product_id,
        "status": "delivered"
    })
    
    review = Review(
        **review_data.dict(),
        user_id=current_user.id,
        user_name=current_user.full_name,
        verified_purchase=bool(order)
    )
    
    await db.reviews.insert_one(review.dict())
    
    # Update product reviews summary
    await update_product_reviews_summary(review_data.product_id)
    
    return review

@router.post("/reviews/{review_id}/helpful")
async def mark_review_helpful(
    review_id: str,
    current_user: User = Depends(get_current_user)
):
    review = await db.reviews.find_one({"id": review_id})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    helpful_voters = review.get("helpful_voters", [])
    
    if current_user.id in helpful_voters:
        # Remove vote
        await db.reviews.update_one(
            {"id": review_id},
            {
                "$pull": {"helpful_voters": current_user.id},
                "$inc": {"helpful_count": -1}
            }
        )
        return {"helpful": False, "count": review["helpful_count"] - 1}
    else:
        # Add vote
        await db.reviews.update_one(
            {"id": review_id},
            {
                "$push": {"helpful_voters": current_user.id},
                "$inc": {"helpful_count": 1}
            }
        )
        return {"helpful": True, "count": review["helpful_count"] + 1}

async def update_product_reviews_summary(product_id: str):
    reviews = await db.reviews.find({"product_id": product_id}).to_list(length=None)
    
    if not reviews:
        return
    
    total = len(reviews)
    rating_sum = sum(r["rating"] for r in reviews)
    average = round(rating_sum / total, 1)
    
    distribution = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
    for review in reviews:
        distribution[str(review["rating"])] += 1
    
    await db.products.update_one(
        {"id": product_id},
        {"$set": {
            "reviews_summary": {
                "average_rating": average,
                "total_reviews": total,
                "rating_distribution": distribution
            }
        }}
    )

# ============ WISHLIST ROUTES ============

@router.get("/wishlist")
async def get_wishlist(current_user: User = Depends(get_current_user)):
    wishlist = await db.wishlists.find_one({"user_id": current_user.id})
    
    if not wishlist:
        return {"items": [], "total": 0}
    
    # Populate product details
    items_with_details = []
    for item in wishlist.get("items", []):
        product = await db.products.find_one({"id": item["product_id"]})
        if product:
            item_detail = {
                **item,
                "product": product
            }
            items_with_details.append(item_detail)
    
    return {
        "items": items_with_details,
        "total": len(items_with_details)
    }

@router.post("/wishlist")
async def add_to_wishlist(
    item: WishlistAdd,
    current_user: User = Depends(get_current_user)
):
    product = await db.products.find_one({"id": item.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    wishlist = await db.wishlists.find_one({"user_id": current_user.id})
    
    if not wishlist:
        wishlist = Wishlist(user_id=current_user.id, items=[])
        await db.wishlists.insert_one(wishlist.dict())
    
    # Check if item already exists
    existing = any(
        i["product_id"] == item.product_id and 
        i.get("variant_id") == item.variant_id
        for i in wishlist.get("items", [])
    )
    
    if existing:
        raise HTTPException(status_code=400, detail="Item already in wishlist")
    
    wishlist_item = {
        "product_id": item.product_id,
        "variant_id": item.variant_id,
        "added_at": datetime.now(timezone.utc)
    }
    
    await db.wishlists.update_one(
        {"user_id": current_user.id},
        {
            "$push": {"items": wishlist_item},
            "$set": {"updated_at": datetime.now(timezone.utc)}
        }
    )
    
    return {"message": "Added to wishlist", "item": wishlist_item}

@router.delete("/wishlist/{product_id}")
async def remove_from_wishlist(
    product_id: str,
    variant_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    query = {"product_id": product_id}
    if variant_id:
        query["variant_id"] = variant_id
    
    result = await db.wishlists.update_one(
        {"user_id": current_user.id},
        {
            "$pull": {"items": query},
            "$set": {"updated_at": datetime.now(timezone.utc)}
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found in wishlist")
    
    return {"message": "Removed from wishlist"}

# ============ STOCK ALERTS ROUTES ============

@router.post("/stock-alerts")
async def create_stock_alert(
    alert_data: StockAlertCreate,
    background_tasks: BackgroundTasks
):
    product = await db.products.find_one({"id": alert_data.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if alert already exists
    existing = await db.stock_alerts.find_one({
        "email": alert_data.email,
        "product_id": alert_data.product_id,
        "variant_id": alert_data.variant_id,
        "notified": False
    })
    
    if existing:
        return {"message": "Alert already exists", "alert": existing}
    
    alert = StockAlert(**alert_data.dict())
    await db.stock_alerts.insert_one(alert.dict())
    
    return {"message": "Stock alert created", "alert": alert}

@router.get("/admin/stock-alerts")
async def get_pending_stock_alerts(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    alerts = await db.stock_alerts.find({"notified": False}).to_list(length=None)
    return {"alerts": alerts, "total": len(alerts)}

# ============ SHIPPING CALCULATION ROUTES ============

@router.post("/shipping/calculate", response_model=ShippingResult)
async def calculate_shipping(calculation: ShippingCalculation):
    # Get shipping rules for destination
    rule = await db.shipping_rules.find_one({
        "destination_country": calculation.destination_country
    })
    
    if not rule:
        # Default rule
        rule = {
            "weight_brackets": [
                {"max_kg": 1, "standard_price": 6.90, "express_price": 12.90},
                {"max_kg": 5, "standard_price": 9.90, "express_price": 17.90},
                {"max_kg": 999, "standard_price": 14.90, "express_price": 24.90}
            ],
            "free_shipping_threshold": 50.0
        }
    
    # Calculate total weight and value
    total_weight = 0
    total_value = 0
    
    for item in calculation.items:
        product = await db.products.find_one({"id": item["product_id"]})
        if product:
            variant = next(
                (v for v in product.get("variants", []) if v["id"] == item.get("variant_id")),
                product.get("variants", [{}])[0] if product.get("variants") else {}
            )
            weight = variant.get("weight_kg", 0.5)
            price = variant.get("price", 0)
            quantity = item.get("quantity", 1)
            
            total_weight += weight * quantity
            total_value += price * quantity
    
    # Find applicable bracket
    standard_price = 0
    express_price = 0
    
    for bracket in rule["weight_brackets"]:
        if total_weight <= bracket["max_kg"]:
            standard_price = bracket["standard_price"]
            express_price = bracket["express_price"]
            break
    
    # Check free shipping
    free_threshold = rule.get("free_shipping_threshold", 50.0)
    if total_value >= free_threshold:
        standard_price = 0
    
    amount_to_free = max(0, free_threshold - total_value)
    
    return ShippingResult(
        standard={
            "price": standard_price,
            "delivery_days": "5-7",
            "name": "Standard"
        },
        express={
            "price": express_price,
            "delivery_days": "2-3",
            "name": "Express"
        },
        free_threshold=free_threshold,
        current_total=total_value,
        amount_to_free_shipping=amount_to_free
    )

# ============ REGIONS/ORIGINS ROUTES ============

@router.get("/regions")
async def get_regions():
    regions = await db.regions.find().to_list(length=None)
    # Remove MongoDB _id field
    for region in regions:
        if '_id' in region:
            del region['_id']
    return regions

@router.get("/regions/{region_id}")
async def get_region(region_id: str):
    region = await db.regions.find_one({"id": region_id})
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    # Remove MongoDB _id
    if '_id' in region:
        del region['_id']
    
    # Get products from this region
    products = await db.products.find(
        {"origin.region_id": region_id}
    ).to_list(length=None)
    
    for product in products:
        if '_id' in product:
            del product['_id']
    
    region["products"] = products
    return region

# ============ RECOMMENDATIONS ROUTES ============

@router.get("/products/{product_id}/recommendations")
async def get_product_recommendations(product_id: str):
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get cached recommendations
    cached = await db.recommendations.find_one({"product_id": product_id})
    
    if cached:
        frequently_bought = await db.products.find(
            {"id": {"$in": cached.get("frequently_bought_together", [])}}
        ).to_list(length=4)
        
        similar = await db.products.find(
            {"id": {"$in": cached.get("similar_products", [])}}
        ).to_list(length=4)
    else:
        # Fallback: same category
        category = product.get("category")
        similar = await db.products.find(
            {"category": category, "id": {"$ne": product_id}}
        ).limit(4).to_list(length=4)
        
        frequently_bought = []
    
    return {
        "frequently_bought_together": frequently_bought,
        "similar_products": similar
    }

@router.post("/cart/recommendations")
async def get_cart_recommendations(items: List[Dict]):
    product_ids = [item["product_id"] for item in items]
    
    # Get all recommendations for products in cart
    recommendations = await db.recommendations.find(
        {"product_id": {"$in": product_ids}}
    ).to_list(length=None)
    
    # Aggregate frequently bought together
    suggested_ids = set()
    for rec in recommendations:
        suggested_ids.update(rec.get("frequently_bought_together", []))
    
    # Remove items already in cart
    suggested_ids -= set(product_ids)
    
    # Get product details
    suggestions = await db.products.find(
        {"id": {"$in": list(suggested_ids)}}
    ).limit(6).to_list(length=6)
    
    return {"recommendations": suggestions}

# ============ ADVANCED FILTERS ROUTE ============

@router.get("/products/filter/advanced")
async def filter_products_advanced(
    category: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    origin: Optional[str] = None,
    labels: Optional[str] = None,
    in_stock: Optional[bool] = None,
    rating_min: Optional[float] = None,
    sort: str = "recent",
    skip: int = 0,
    limit: int = 20
):
    query = {}
    
    if category:
        query["category"] = category
    
    if origin:
        query["origin.region_id"] = origin
    
    if labels:
        label_list = labels.split(",")
        query["labels"] = {"$in": label_list}
    
    if in_stock:
        query["variants.stock_quantity"] = {"$gt": 0}
    
    if rating_min:
        query["reviews_summary.average_rating"] = {"$gte": rating_min}
    
    # Price filter on variants
    if price_min is not None or price_max is not None:
        price_query = {}
        if price_min is not None:
            price_query["$gte"] = price_min
        if price_max is not None:
            price_query["$lte"] = price_max
        query["variants.price"] = price_query
    
    sort_options = {
        "recent": [("created_at", -1)],
        "price_low": [("variants.0.price", 1)],
        "price_high": [("variants.0.price", -1)],
        "rating": [("reviews_summary.average_rating", -1)],
        "popular": [("reviews_summary.total_reviews", -1)]
    }
    
    products = await db.products.find(query).sort(
        sort_options.get(sort, [("created_at", -1)])
    ).skip(skip).limit(limit).to_list(length=limit)
    
    # Remove _id from all products
    for product in products:
        if '_id' in product:
            del product['_id']
    
    total = await db.products.count_documents(query)
    
    return {
        "products": products,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }
