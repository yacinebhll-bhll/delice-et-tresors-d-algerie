#!/usr/bin/env python3
"""
Script pour corriger les mots de passe des utilisateurs
Renomme 'password' en 'hashed_password'
"""
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def fix_user_passwords():
    try:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        print('🔧 Correction des mots de passe utilisateurs...')
        print('=' * 60)
        
        # Récupérer tous les utilisateurs
        users = await db.users.find().to_list(length=None)
        
        for user in users:
            if 'password' in user and 'hashed_password' not in user:
                # Renommer password en hashed_password
                await db.users.update_one(
                    {'_id': user['_id']},
                    {
                        '$set': {'hashed_password': user['password']},
                        '$unset': {'password': ''}
                    }
                )
                print(f'✅ Corrigé: {user["email"]}')
            elif 'hashed_password' in user:
                print(f'⏭️  Déjà correct: {user["email"]}')
        
        print('\n' + '=' * 60)
        print('🎉 Correction terminée!')
        
    except Exception as e:
        print(f'❌ Erreur: {str(e)}')
        import traceback
        traceback.print_exc()
    finally:
        client.close()

async def main():
    await fix_user_passwords()

if __name__ == "__main__":
    asyncio.run(main())
