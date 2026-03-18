#!/usr/bin/env python3
"""
Worker script for stock alerts notifications
Runs every hour to check for restocked products and send emails
"""
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def send_stock_alerts():
    try:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        print('🔔 Checking stock alerts...')
        
        # Get all pending alerts
        alerts = await db.stock_alerts.find({"notified": False}).to_list(length=None)
        
        if not alerts:
            print('No pending alerts')
            return
        
        # Group by product
        alerts_by_product = {}
        for alert in alerts:
            product_id = alert['product_id']
            if product_id not in alerts_by_product:
                alerts_by_product[product_id] = []
            alerts_by_product[product_id].append(alert)
        
        # Check each product
        notified_count = 0
        for product_id, product_alerts in alerts_by_product.items():
            product = await db.products.find_one({"id": product_id})
            if not product:
                continue
            
            # Check if any variant is back in stock
            for alert in product_alerts:
                variant_id = alert.get('variant_id')
                is_in_stock = False
                
                if variant_id:
                    # Check specific variant
                    variant = next((v for v in product.get('variants', []) if v['id'] == variant_id), None)
                    if variant and variant.get('stock_quantity', 0) > 0:
                        is_in_stock = True
                else:
                    # Check if any variant is in stock
                    for variant in product.get('variants', []):
                        if variant.get('stock_quantity', 0) > 0:
                            is_in_stock = True
                            break
                
                if is_in_stock:
                    # Mark as notified
                    await db.stock_alerts.update_one(
                        {"_id": alert['_id']},
                        {
                            "$set": {
                                "notified": True,
                                "notified_at": datetime.now(timezone.utc)
                            }
                        }
                    )
                    notified_count += 1
                    print(f'✉️  Notified {alert["email"]} for product {product["name"]["fr"]}')
        
        print(f'✅ Sent {notified_count} stock alert notifications')
        
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()
    finally:
        client.close()

async def main():
    await send_stock_alerts()

if __name__ == "__main__":
    asyncio.run(main())
