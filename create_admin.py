#!/usr/bin/env python3
"""
Script pour créer un utilisateur administrateur par défaut
"""
import requests
import json

# Configuration
API_BASE = "https://api-fix-preview-2.preview.emergentagent.com/api"

# Données de l'admin par défaut
ADMIN_EMAIL = "admin@soumam.com"
ADMIN_PASSWORD = "admin123"
ADMIN_NAME = "Admin Soumam Heritage"

def create_admin():
    """Créer un utilisateur admin par défaut"""
    print("🔐 Création de l'utilisateur administrateur par défaut...")
    
    # Données d'inscription admin
    register_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
        "full_name": ADMIN_NAME,
        "role": "admin"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=register_data)
        if response.status_code == 200:
            print(f"✅ Utilisateur admin créé avec succès!")
            print(f"📧 Email: {ADMIN_EMAIL}")
            print(f"🔑 Mot de passe: {ADMIN_PASSWORD}")
            print(f"🌐 Accès admin: https://api-fix-preview-2.preview.emergentagent.com/admin")
            return True
        else:
            print(f"⚠️  L'utilisateur admin existe peut-être déjà: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'admin: {str(e)}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Configuration de l'administrateur système pour Soumam Heritage")
    print("=" * 70)
    
    success = create_admin()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 Configuration terminée! Vous pouvez maintenant vous connecter en tant qu'admin.")
    else:
        print("⚠️  Vérifiez si l'admin existe déjà ou contactez le support.")
    
    return success

if __name__ == "__main__":
    main()