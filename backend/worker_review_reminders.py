#!/usr/bin/env python3
"""
Worker script for review reminders.
Checks for delivered orders and sends reminders to leave reviews.
Runs every 6 hours.
"""
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')


async def send_review_reminders():
    try:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']

        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]

        print(f'[{datetime.now(timezone.utc).isoformat()}] Checking for review reminders...')

        # Find delivered orders from 3-14 days ago that haven't been reminded
        now = datetime.now(timezone.utc)
        three_days_ago = now - timedelta(days=3)
        fourteen_days_ago = now - timedelta(days=14)

        orders = await db.orders.find({
            "status": "delivered",
            "review_reminder_sent": {"$ne": True},
            "updated_at": {"$gte": fourteen_days_ago, "$lte": three_days_ago}
        }, {"_id": 0}).to_list(length=100)

        if not orders:
            print('No orders need review reminders')
            return

        reminded_count = 0
        for order in orders:
            customer_email = order.get('customer_email', '')
            if not customer_email:
                continue

            # Check if user already reviewed any of the products
            for item in order.get('items', []):
                product_id = item.get('product_id')
                existing_review = await db.reviews.find_one({
                    "product_id": product_id,
                    "$or": [
                        {"user_id": order.get('user_id', '')},
                        {"user_email": customer_email}
                    ]
                })
                if existing_review:
                    continue

                # Log the reminder (actual email sending depends on SMTP config)
                print(f'  Reminder: {customer_email} -> review product {product_id}')
                reminded_count += 1

            # Mark order as reminded
            await db.orders.update_one(
                {"id": order['id']},
                {"$set": {"review_reminder_sent": True, "review_reminder_at": now}}
            )

        print(f'Processed {reminded_count} review reminders for {len(orders)} orders')

    except Exception as e:
        print(f'Error: {str(e)}')
        import traceback
        traceback.print_exc()
    finally:
        client.close()


async def main():
    while True:
        await send_review_reminders()
        print('Sleeping 6 hours...')
        await asyncio.sleep(6 * 3600)

if __name__ == "__main__":
    asyncio.run(main())
