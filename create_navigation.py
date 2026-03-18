#!/usr/bin/env python3
"""
Script pour créer les items de navigation par défaut
"""
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def create_navigation_items():
    try:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        print('🧭 Création des items de navigation...')
        print('=' * 60)
        
        # Vérifier si des items existent déjà
        existing_count = await db.navigation.count_documents({})
        
        if existing_count > 0:
            print(f'⚠️  {existing_count} item(s) de navigation existe(nt) déjà')
            print('   Suppression des anciens items...')
            await db.navigation.delete_many({})
        
        # Créer les items de navigation par défaut
        navigation_items = [
            {
                "id": str(uuid.uuid4()),
                "label": {
                    "fr": "Accueil",
                    "en": "Home",
                    "ar": "الرئيسية"
                },
                "url": "/",
                "is_external": False,
                "is_active": True,
                "order": 0,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "label": {
                    "fr": "Boutique",
                    "en": "Shop",
                    "ar": "المتجر"
                },
                "url": "/shop",
                "is_external": False,
                "is_active": True,
                "order": 1,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "label": {
                    "fr": "Histoire",
                    "en": "History",
                    "ar": "التاريخ"
                },
                "url": "/history",
                "is_external": False,
                "is_active": True,
                "order": 2,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "label": {
                    "fr": "Témoignages",
                    "en": "Testimonials",
                    "ar": "الشهادات"
                },
                "url": "/testimonials",
                "is_external": False,
                "is_active": True,
                "order": 3,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "label": {
                    "fr": "Promotions",
                    "en": "Promotions",
                    "ar": "العروض"
                },
                "url": "/promotions",
                "is_external": False,
                "is_active": True,
                "order": 4,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "label": {
                    "fr": "Contact",
                    "en": "Contact",
                    "ar": "اتصل بنا"
                },
                "url": "/contact",
                "is_external": False,
                "is_active": True,
                "order": 5,
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        # Insérer les items
        await db.navigation.insert_many(navigation_items)
        
        print(f'\n✅ {len(navigation_items)} items de navigation créés:')
        for item in navigation_items:
            print(f'   • {item["label"]["fr"]} ({item["url"]})')
        
        print('\n' + '=' * 60)
        print('🎉 Navigation configurée avec succès!')
        
    except Exception as e:
        print(f'❌ Erreur: {str(e)}')
        import traceback
        traceback.print_exc()
    finally:
        client.close()

async def main():
    await create_navigation_items()

if __name__ == "__main__":
    asyncio.run(main())
