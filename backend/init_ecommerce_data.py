#!/usr/bin/env python3
"""
Initialize E-commerce Extended Data
Creates sample data for regions, shipping rules, and recommendations
"""
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def init_ecommerce_data():
    try:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        print('🚀 Initialisation des données e-commerce étendues...')
        print('=' * 60)
        
        # 1. Create Regions
        regions = [
            {
                "id": str(uuid.uuid4()),
                "name": {
                    "fr": "Kabylie - Taksebt",
                    "en": "Kabylie - Taksebt",
                    "ar": "القبائل - تاكسيبت"
                },
                "coordinates": {"lat": 36.7064, "lng": 4.5328},
                "description": {
                    "fr": "Région montagneuse réputée pour son huile d'olive",
                    "en": "Mountainous region renowned for its olive oil",
                    "ar": "منطقة جبلية مشهورة بزيت الزيتون"
                },
                "images": [],
                "producers": [],
                "product_ids": [],
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "name": {
                    "fr": "Biskra",
                    "en": "Biskra",
                    "ar": "بسكرة"
                },
                "coordinates": {"lat": 34.8514, "lng": 5.7248},
                "description": {
                    "fr": "Capitale des dattes Deglet Nour",
                    "en": "Capital of Deglet Nour dates",
                    "ar": "عاصمة تمور دقلة نور"
                },
                "images": [],
                "producers": [],
                "product_ids": [],
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "name": {
                    "fr": "Tlemcen",
                    "en": "Tlemcen",
                    "ar": "تلمسان"
                },
                "coordinates": {"lat": 34.8780, "lng": -1.3150},
                "description": {
                    "fr": "Région des épices et du miel",
                    "en": "Region of spices and honey",
                    "ar": "منطقة التوابل والعسل"
                },
                "images": [],
                "producers": [],
                "product_ids": [],
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        # Check if regions already exist
        existing_regions = await db.regions.count_documents({})
        if existing_regions == 0:
            await db.regions.insert_many(regions)
            print(f'✅ {len(regions)} régions créées')
        else:
            print(f'⏭️  {existing_regions} région(s) déjà existante(s)')
        
        # 2. Create Shipping Rules
        shipping_rules = [
            {
                "id": str(uuid.uuid4()),
                "destination_country": "FR",
                "destination_zone": "metropolitaine",
                "weight_brackets": [
                    {"max_kg": 1.0, "standard_price": 6.90, "express_price": 12.90},
                    {"max_kg": 5.0, "standard_price": 9.90, "express_price": 17.90},
                    {"max_kg": 999.0, "standard_price": 14.90, "express_price": 24.90}
                ],
                "free_shipping_threshold": 50.0,
                "currency": "EUR"
            },
            {
                "id": str(uuid.uuid4()),
                "destination_country": "DZ",
                "destination_zone": None,
                "weight_brackets": [
                    {"max_kg": 1.0, "standard_price": 500.0, "express_price": 800.0},
                    {"max_kg": 5.0, "standard_price": 700.0, "express_price": 1200.0},
                    {"max_kg": 999.0, "standard_price": 1000.0, "express_price": 1800.0}
                ],
                "free_shipping_threshold": 5000.0,
                "currency": "DZD"
            }
        ]
        
        existing_rules = await db.shipping_rules.count_documents({})
        if existing_rules == 0:
            await db.shipping_rules.insert_many(shipping_rules)
            print(f'✅ {len(shipping_rules)} règles de livraison créées')
        else:
            print(f'⏭️  {existing_rules} règle(s) de livraison déjà existante(s)')
        
        # 3. Update existing products with extended fields
        products = await db.products.find().to_list(length=None)
        updated_count = 0
        
        for product in products:
            update_fields = {}
            
            # Add variants if missing
            if 'variants' not in product or not product.get('variants'):
                update_fields['variants'] = [{
                    "id": str(uuid.uuid4()),
                    "name": "Standard",
                    "sku": f"{product['id'][:8]}-STD",
                    "price": product.get('price', 10.0),
                    "compare_at_price": None,
                    "weight_kg": 0.5,
                    "dimensions": None,
                    "stock_quantity": 100,
                    "low_stock_threshold": 5,
                    "image_url": product.get('image_urls', [None])[0]
                }]
            
            # Add reviews summary if missing
            if 'reviews_summary' not in product:
                update_fields['reviews_summary'] = {
                    "average_rating": 0,
                    "total_reviews": 0,
                    "rating_distribution": {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
                }
            
            # Add origin if missing and assign random region
            if 'origin' not in product or not product.get('origin'):
                region = regions[updated_count % len(regions)]
                update_fields['origin'] = {
                    "region_id": region['id'],
                    "region_name": region['name'],
                    "coordinates": region['coordinates'],
                    "producer_name": None,
                    "producer_story": None,
                    "images": []
                }
            
            # Add empty arrays for recommendations
            if 'frequently_bought_with' not in product:
                update_fields['frequently_bought_with'] = []
            if 'similar_products' not in product:
                update_fields['similar_products'] = []
            
            # Add videos array if missing
            if 'videos' not in product:
                update_fields['videos'] = []
            
            # Add labels if missing
            if 'labels' not in product or not product.get('labels'):
                update_fields['labels'] = ['artisanal']
            
            if update_fields:
                await db.products.update_one(
                    {'_id': product['_id']},
                    {'$set': update_fields}
                )
                updated_count += 1
        
        print(f'✅ {updated_count} produit(s) mis à jour avec les champs étendus')
        
        print('\n' + '=' * 60)
        print('🎉 Initialisation terminée!')
        print('\nFonctionnalités activées:')
        print('  ✅ Régions/Origines des produits')
        print('  ✅ Variantes de produits')
        print('  ✅ Calcul automatique de livraison')
        print('  ✅ Système d\'avis (prêt)')
        print('  ✅ Wishlist (prêt)')
        print('  ✅ Alertes stock (prêt)')
        print('  ✅ Recommandations (structure)')
        print('  ✅ Vidéos produits (structure)')
        
    except Exception as e:
        print(f'❌ Erreur: {str(e)}')
        import traceback
        traceback.print_exc()
    finally:
        client.close()

async def main():
    await init_ecommerce_data()

if __name__ == "__main__":
    asyncio.run(main())
