#!/usr/bin/env python3
"""
Worker script for generating product recommendations
Analyzes order history to find frequently bought together products
Run daily to update recommendations
"""
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def generate_recommendations():
    try:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        print('🤖 Generating product recommendations...')
        
        # Get all orders
        orders = await db.orders.find({"status": {"$in": ["confirmed", "delivered"]}}).to_list(length=None)
        
        if not orders:
            print('No orders found')
            return
        
        # Analyze co-purchases
        co_purchases = defaultdict(lambda: defaultdict(int))
        
        for order in orders:
            items = order.get('items', [])
            product_ids = [item['product_id'] for item in items]
            
            # For each product, count what was bought with it
            for i, product_id in enumerate(product_ids):
                for j, other_product_id in enumerate(product_ids):
                    if i != j:
                        co_purchases[product_id][other_product_id] += 1
        
        # Update recommendations in database
        updated_count = 0
        for product_id, related in co_purchases.items():
            # Sort by frequency and take top 4
            frequently_bought = sorted(related.items(), key=lambda x: x[1], reverse=True)[:4]
            frequently_bought_ids = [pid for pid, count in frequently_bought]
            
            # Update or create recommendation
            await db.recommendations.update_one(
                {"product_id": product_id},
                {
                    "$set": {
                        "frequently_bought_together": frequently_bought_ids,
                        "updated_at": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
            
            # Also update product document
            await db.products.update_one(
                {"id": product_id},
                {"$set": {"frequently_bought_with": frequently_bought_ids}}
            )
            
            updated_count += 1
        
        print(f'✅ Updated recommendations for {updated_count} products')
        
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()
    finally:
        client.close()

async def main():
    await generate_recommendations()

if __name__ == "__main__":
    asyncio.run(main())
