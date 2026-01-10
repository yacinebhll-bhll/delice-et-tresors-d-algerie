#!/bin/bash
# ===========================================
# Script d'import MongoDB Atlas
# Délices et Trésors d'Algérie
# ===========================================

# INSTRUCTIONS:
# 1. Installez MongoDB Database Tools: https://www.mongodb.com/try/download/database-tools
# 2. Remplacez MONGODB_ATLAS_URI par votre URI MongoDB Atlas
# 3. Exécutez: chmod +x import_to_atlas.sh && ./import_to_atlas.sh

# Configuration
MONGODB_ATLAS_URI="mongodb+srv://USERNAME:PASSWORD@cluster.xxxxx.mongodb.net/"
DB_NAME="delices_algerie"

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Import MongoDB Atlas - Délices et Trésors"
echo "=========================================="
echo ""

# Vérifier que mongoimport est installé
if ! command -v mongoimport &> /dev/null; then
    echo -e "${RED}ERREUR: mongoimport n'est pas installé${NC}"
    echo "Installez MongoDB Database Tools depuis:"
    echo "https://www.mongodb.com/try/download/database-tools"
    exit 1
fi

# Liste des collections à importer
collections=(
    "users"
    "products"
    "categories"
    "orders"
    "banners"
    "promo_codes"
    "testimonials"
    "contact_messages"
    "newsletter_subscribers"
    "navigation"
    "footer_settings"
    "custom_pages"
    "historical_content"
    "settings"
    "customization"
    "seo_settings"
)

# Importer chaque collection
for collection in "${collections[@]}"; do
    file="${collection}.json"
    
    if [ -f "$file" ]; then
        echo "Importing ${collection}..."
        mongoimport --uri "${MONGODB_ATLAS_URI}${DB_NAME}" \
                    --collection "$collection" \
                    --file "$file" \
                    --drop
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ ${collection} imported successfully${NC}"
        else
            echo -e "${RED}✗ Error importing ${collection}${NC}"
        fi
    else
        echo -e "${RED}✗ File ${file} not found${NC}"
    fi
done

echo ""
echo "=========================================="
echo "Import terminé!"
echo "=========================================="
echo ""
echo "N'oubliez pas de:"
echo "1. Mettre à jour MONGO_URL dans votre backend/.env"
echo "2. Changer le mot de passe admin si nécessaire"
echo ""
