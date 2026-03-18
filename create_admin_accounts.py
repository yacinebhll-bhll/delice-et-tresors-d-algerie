#!/usr/bin/env python3
"""
Script pour créer les comptes administrateurs
"""
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from passlib.context import CryptContext
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin_accounts():
    try:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Mot de passe à hasher
        password = "Mazi@go"
        hashed_password = pwd_context.hash(password)
        
        # Comptes à créer
        admins = [
            {
                "email": "yacbhll@gmail.com",
                "full_name": "Yacine Bhll (Admin 1)"
            },
            {
                "email": "yacinebhll@gmail.com",
                "full_name": "Yacine Bhll (Admin 2)"
            }
        ]
        
        print('🔧 Création des comptes administrateurs...')
        print('=' * 60)
        
        for admin_data in admins:
            # Vérifier si l'utilisateur existe déjà
            existing = await db.users.find_one({"email": admin_data["email"]})
            
            if existing:
                print(f'\n⚠️  L\'utilisateur {admin_data["email"]} existe déjà')
                # Mettre à jour le rôle et le mot de passe
                await db.users.update_one(
                    {"email": admin_data["email"]},
                    {
                        "$set": {
                            "role": "admin",
                            "password": hashed_password,
                            "is_active": True
                        }
                    }
                )
                print(f'✅ Mis à jour en tant qu\'admin avec nouveau mot de passe')
            else:
                # Créer un nouvel utilisateur
                user_doc = {
                    "id": str(uuid.uuid4()),
                    "email": admin_data["email"],
                    "full_name": admin_data["full_name"],
                    "password": hashed_password,
                    "role": "admin",
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc)
                }
                
                await db.users.insert_one(user_doc)
                print(f'\n✅ Compte créé: {admin_data["email"]}')
                print(f'   Nom: {admin_data["full_name"]}')
                print(f'   Rôle: admin')
        
        print('\n' + '=' * 60)
        print('🎉 Tous les comptes administrateurs ont été créés!')
        print('\n📝 Informations de connexion:')
        print('   Email 1: yacbhll@gmail.com')
        print('   Email 2: yacinebhll@gmail.com')
        print('   Mot de passe: Mazi@go')
        print('\n🔐 Vous pouvez maintenant vous connecter au panel admin!')
        
    except Exception as e:
        print(f'❌ Erreur: {str(e)}')
        import traceback
        traceback.print_exc()
    finally:
        client.close()

async def main():
    await create_admin_accounts()

if __name__ == "__main__":
    asyncio.run(main())
