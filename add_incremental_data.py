#!/usr/bin/env python3
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def add_incremental_data():
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Check existing categories
    existing_cats = await db.categories.find().to_list(length=None)
    existing_slugs = {cat['slug'] for cat in existing_cats}
    
    regions = await db.regions.find().to_list(length=None)
    region_kabylie = next((r for r in regions if 'Kabylie' in r['name']['fr']), regions[0] if regions else None)
    region_biskra = next((r for r in regions if 'Biskra' in r['name']['fr']), regions[1] if len(regions) > 1 else None)
    region_tlemcen = next((r for r in regions if 'Tlemcen' in r['name']['fr']), regions[2] if len(regions) > 2 else None)
    
    # Categories to create
    categories_to_create = [
        {"slug": "huiles", "name": {"fr": "Huile d'olive", "en": "Olive Oil", "ar": "زيت الزيتون"}, "icon": "🫒"},
        {"slug": "dattes", "name": {"fr": "Dattes", "en": "Dates", "ar": "تمور"}, "icon": "🌴"},
        {"slug": "epices", "name": {"fr": "Épices", "en": "Spices", "ar": "توابل"}, "icon": "🌶️"},
        {"slug": "robes-kabyles", "name": {"fr": "Robes kabyles", "en": "Kabyle Dresses", "ar": "فساتين قبائلية"}, "icon": "👗"},
        {"slug": "poterie", "name": {"fr": "Poterie berbère", "en": "Berber Pottery", "ar": "فخار بربري"}, "icon": "🏺"},
        {"slug": "accessoires", "name": {"fr": "Accessoires", "en": "Accessories", "ar": "إكسسوارات"}, "icon": "💍"}
    ]
    
    new_categories = []
    for cat_data in categories_to_create:
        if cat_data['slug'] not in existing_slugs:
            cat_id = str(uuid.uuid4())
            category = {
                "id": cat_id,
                "slug": cat_data['slug'],
                "name": cat_data['name'],
                "icon": cat_data['icon'],
                "image_url": f"https://images.unsplash.com/photo-{1500000000 + len(new_categories)}?w=400",
                "description": cat_data['name'],
                "order": len(existing_cats) + len(new_categories),
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            }
            await db.categories.insert_one(category)
            new_categories.append(category)
            print(f"✅ Catégorie créée: {cat_data['name']['fr']}")
    
    # Products by category
    products_data = {
        "huiles": [
            {
                "name": {"fr": "Huile d'olive extra vierge Kabylie", "en": "Extra Virgin Olive Oil Kabylia", "ar": "زيت زيتون بكر ممتاز قبائلي"},
                "description": {"fr": "Huile d'olive pressée à froid des montagnes de Kabylie. Fruité intense avec notes d'herbes fraîches.", "en": "Cold-pressed olive oil from Kabylia mountains. Intense fruity with fresh herb notes.", "ar": "زيت زيتون معصور على البارد من جبال القبائل. فاكهي مكثف مع نكهات الأعشاب الطازجة."},
                "variants": [
                    {"name": "250ml", "sku": "OLIVE-250", "price": 12.90, "compare_at_price": 15.90, "weight_kg": 0.25, "stock_quantity": 45},
                    {"name": "500ml", "sku": "OLIVE-500", "price": 22.90, "compare_at_price": 26.90, "weight_kg": 0.5, "stock_quantity": 38},
                    {"name": "1L", "sku": "OLIVE-1L", "price": 39.90, "compare_at_price": 48.90, "weight_kg": 1.0, "stock_quantity": 22}
                ],
                "labels": ["bio", "aoc", "artisanal"],
                "origin": region_kabylie,
                "images": ["https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600", "https://images.unsplash.com/photo-1608877907149-a206d75ba011?w=600"]
            },
            {
                "name": {"fr": "Huile d'olive douce premium", "en": "Premium Mild Olive Oil", "ar": "زيت زيتون حلو متميز"},
                "description": {"fr": "Huile douce et équilibrée, parfaite pour assaisonnements délicats. Première pression à froid.", "en": "Mild and balanced oil, perfect for delicate dressings. First cold press.", "ar": "زيت حلو ومتوازن، مثالي للصلصات الرقيقة. عصرة أولى على البارد."},
                "variants": [
                    {"name": "500ml", "sku": "OLIVE-DOUX-500", "price": 19.90, "weight_kg": 0.5, "stock_quantity": 52}
                ],
                "labels": ["bio", "artisanal"],
                "origin": region_kabylie,
                "images": ["https://images.unsplash.com/photo-1612528443702-f6741f70a049?w=600"]
            },
            {
                "name": {"fr": "Huile d'olive au citron", "en": "Lemon Infused Olive Oil", "ar": "زيت زيتون بالليمون"},
                "description": {"fr": "Huile d'olive infusée au citron de Kabylie. Parfaite pour poissons et salades.", "en": "Olive oil infused with Kabylia lemon. Perfect for fish and salads.", "ar": "زيت زيتون منقوع بليمون القبائل. مثالي للأسماك والسلطات."},
                "variants": [
                    {"name": "250ml", "sku": "OLIVE-CITRON-250", "price": 14.90, "weight_kg": 0.25, "stock_quantity": 28}
                ],
                "labels": ["artisanal"],
                "origin": region_kabylie,
                "images": ["https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600"]
            }
        ],
        "dattes": [
            {
                "name": {"fr": "Dattes Deglet Nour premium", "en": "Premium Deglet Nour Dates", "ar": "تمور دقلة نور ممتازة"},
                "description": {"fr": "Dattes Deglet Nour de Biskra, surnommées 'doigts de lumière'. Sucrées et fondantes.", "en": "Deglet Nour dates from Biskra, called 'fingers of light'. Sweet and melting.", "ar": "تمور دقلة نور من بسكرة، الملقبة بـ 'أصابع النور'. حلوة وذائبة."},
                "variants": [
                    {"name": "500g", "sku": "DATTE-DEG-500", "price": 9.90, "compare_at_price": 12.90, "weight_kg": 0.5, "stock_quantity": 65},
                    {"name": "1kg", "sku": "DATTE-DEG-1K", "price": 17.90, "compare_at_price": 22.90, "weight_kg": 1.0, "stock_quantity": 42}
                ],
                "labels": ["bio", "artisanal"],
                "origin": region_biskra,
                "images": ["https://images.unsplash.com/photo-1577003833154-a7e6d8e8a7e3?w=600", "https://images.unsplash.com/photo-1610832745704-5293e8c6d5ee?w=600"]
            },
            {
                "name": {"fr": "Dattes Medjool géantes", "en": "Giant Medjool Dates", "ar": "تمور المجهول العملاقة"},
                "description": {"fr": "Dattes Medjool extra-larges, moelleuses et caramélisées. Le caviar des dattes.", "en": "Extra-large Medjool dates, soft and caramelized. The caviar of dates.", "ar": "تمور مجهول كبيرة جداً، طرية وكراميلية. كافيار التمور."},
                "variants": [
                    {"name": "500g", "sku": "DATTE-MED-500", "price": 15.90, "weight_kg": 0.5, "stock_quantity": 31}
                ],
                "labels": ["bio"],
                "origin": region_biskra,
                "images": ["https://images.unsplash.com/photo-1610832745704-5293e8c6d5ee?w=600"]
            },
            {
                "name": {"fr": "Dattes fourrées aux amandes", "en": "Almond Stuffed Dates", "ar": "تمور محشوة باللوز"},
                "description": {"fr": "Dattes Deglet Nour fourrées d'amandes entières. Plaisir gourmand et authentique.", "en": "Deglet Nour dates stuffed with whole almonds. Authentic gourmet pleasure.", "ar": "تمور دقلة نور محشوة باللوز الكامل. متعة أصيلة للذواقة."},
                "variants": [
                    {"name": "250g", "sku": "DATTE-AMANDE-250", "price": 12.90, "weight_kg": 0.25, "stock_quantity": 28}
                ],
                "labels": ["artisanal"],
                "origin": region_biskra,
                "images": ["https://images.unsplash.com/photo-1577003833154-a7e6d8e8a7e3?w=600"]
            }
        ],
        "epices": [
            {
                "name": {"fr": "Ras el Hanout authentique", "en": "Authentic Ras el Hanout", "ar": "راس الحانوت الأصيل"},
                "description": {"fr": "Mélange traditionnel de 27 épices. Parfait pour tajines et couscous. Recette ancestrale.", "en": "Traditional blend of 27 spices. Perfect for tagines and couscous. Ancestral recipe.", "ar": "مزيج تقليدي من 27 نوعاً من التوابل. مثالي للطاجين والكسكس. وصفة أجدادية."},
                "variants": [
                    {"name": "50g", "sku": "EPICE-RAS-50", "price": 7.90, "weight_kg": 0.05, "stock_quantity": 88},
                    {"name": "100g", "sku": "EPICE-RAS-100", "price": 13.90, "weight_kg": 0.1, "stock_quantity": 54}
                ],
                "labels": ["bio", "artisanal"],
                "origin": region_tlemcen,
                "images": ["https://images.unsplash.com/photo-1596040033229-a0b959a33b44?w=600"]
            },
            {
                "name": {"fr": "Cumin de Kabylie", "en": "Kabylia Cumin", "ar": "كمون قبائلي"},
                "description": {"fr": "Cumin cultivé en altitude, au goût intense et parfumé. Moulu artisanalement.", "en": "High-altitude grown cumin, intense and aromatic. Artisanally ground.", "ar": "كمون مزروع في المرتفعات، بطعم مكثف وعطري. مطحون حرفياً."},
                "variants": [
                    {"name": "50g", "sku": "EPICE-CUM-50", "price": 5.90, "weight_kg": 0.05, "stock_quantity": 72}
                ],
                "labels": ["bio"],
                "origin": region_kabylie,
                "images": ["https://images.unsplash.com/photo-1599909533801-e02a1d5c6e2f?w=600"]
            },
            {
                "name": {"fr": "Harissa artisanale", "en": "Artisanal Harissa", "ar": "هريسة حرفية"},
                "description": {"fr": "Pâte de piment rouge traditionnelle. Puissante et aromatique, préparée à la main.", "en": "Traditional red chili paste. Powerful and aromatic, handmade.", "ar": "معجون الفلفل الأحمر التقليدي. قوي وعطري، محضر يدوياً."},
                "variants": [
                    {"name": "200g", "sku": "EPICE-HAR-200", "price": 8.90, "weight_kg": 0.2, "stock_quantity": 45}
                ],
                "labels": ["artisanal"],
                "origin": region_tlemcen,
                "images": ["https://images.unsplash.com/photo-1599909533801-e02a1d5c6e2f?w=600"]
            }
        ],
        "robes-kabyles": [
            {
                "name": {"fr": "Robe kabyle traditionnelle velours", "en": "Traditional Velvet Kabyle Dress", "ar": "فستان قبائلي تقليدي مخملي"},
                "description": {"fr": "Robe kabyle en velours brodée main. Motifs géométriques berbères en fil d'or. Pièce unique.", "en": "Hand-embroidered velvet Kabyle dress. Berber geometric patterns in gold thread. Unique piece.", "ar": "فستان قبائلي مخملي مطرز يدوياً. أنماط هندسية بربرية بخيط ذهبي. قطعة فريدة."},
                "variants": [
                    {"name": "Taille S", "sku": "ROBE-VEL-S", "price": 189.00, "weight_kg": 0.8, "stock_quantity": 5},
                    {"name": "Taille M", "sku": "ROBE-VEL-M", "price": 189.00, "weight_kg": 0.8, "stock_quantity": 8},
                    {"name": "Taille L", "sku": "ROBE-VEL-L", "price": 189.00, "weight_kg": 0.8, "stock_quantity": 3}
                ],
                "labels": ["artisanal", "fait-main"],
                "origin": region_kabylie,
                "images": ["https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600"]
            },
            {
                "name": {"fr": "Robe kabyle moderne coton", "en": "Modern Cotton Kabyle Dress", "ar": "فستان قبائلي عصري قطني"},
                "description": {"fr": "Robe légère en coton avec broderies traditionnelles modernisées. Parfaite pour l'été.", "en": "Light cotton dress with modernized traditional embroidery. Perfect for summer.", "ar": "فستان قطني خفيف بتطريز تقليدي معاصر. مثالي للصيف."},
                "variants": [
                    {"name": "Taille M", "sku": "ROBE-COT-M", "price": 79.90, "weight_kg": 0.4, "stock_quantity": 12}
                ],
                "labels": ["artisanal"],
                "origin": region_kabylie,
                "images": ["https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=600"]
            },
            {
                "name": {"fr": "Ensemble kabyle complet", "en": "Complete Kabyle Set", "ar": "طقم قبائلي كامل"},
                "description": {"fr": "Ensemble traditionnel: robe, ceinture argentée et foulard assorti. Idéal pour événements.", "en": "Traditional set: dress, silver belt and matching scarf. Ideal for events.", "ar": "طقم تقليدي: فستان، حزام فضي ووشاح متناسق. مثالي للمناسبات."},
                "variants": [
                    {"name": "Complet", "sku": "ROBE-ENS-C", "price": 259.00, "weight_kg": 1.2, "stock_quantity": 6}
                ],
                "labels": ["artisanal", "fait-main"],
                "origin": region_kabylie,
                "images": ["https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600"]
            }
        ],
        "poterie": [
            {
                "name": {"fr": "Plat tajine berbère artisanal", "en": "Artisanal Berber Tajine Dish", "ar": "طبق طاجين بربري حرفي"},
                "description": {"fr": "Plat tajine en terre cuite fait main. Décorations géométriques berbères traditionnelles.", "en": "Handmade terracotta tajine dish. Traditional Berber geometric decorations.", "ar": "طبق طاجين من الطين مصنوع يدوياً. زخارف هندسية بربرية تقليدية."},
                "variants": [
                    {"name": "Diamètre 28cm", "sku": "POT-TAJ-28", "price": 45.00, "weight_kg": 2.5, "stock_quantity": 18},
                    {"name": "Diamètre 32cm", "sku": "POT-TAJ-32", "price": 55.00, "weight_kg": 3.2, "stock_quantity": 12}
                ],
                "labels": ["artisanal", "fait-main"],
                "origin": region_tlemcen,
                "images": ["https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=600"]
            },
            {
                "name": {"fr": "Vase berbère décoratif", "en": "Decorative Berber Vase", "ar": "مزهرية بربرية زخرفية"},
                "description": {"fr": "Vase en poterie peint à la main. Motifs kabyles authentiques en rouge et noir.", "en": "Hand-painted pottery vase. Authentic Kabyle patterns in red and black.", "ar": "مزهرية فخارية مرسومة يدوياً. أنماط قبائلية أصيلة بالأحمر والأسود."},
                "variants": [
                    {"name": "Moyen", "sku": "POT-VAS-M", "price": 38.00, "weight_kg": 1.8, "stock_quantity": 15}
                ],
                "labels": ["artisanal"],
                "origin": region_kabylie,
                "images": ["https://images.unsplash.com/photo-1610701596007-11502861dcfa?w=600"]
            },
            {
                "name": {"fr": "Service à thé berbère complet", "en": "Complete Berber Tea Set", "ar": "طقم شاي بربري كامل"},
                "description": {"fr": "Service à thé traditionnel: théière et 6 verres décorés. Artisanat d'exception.", "en": "Traditional tea set: teapot and 6 decorated glasses. Exceptional craftsmanship.", "ar": "طقم شاي تقليدي: إبريق و6 أكواب مزخرفة. حرفية استثنائية."},
                "variants": [
                    {"name": "Set complet", "sku": "POT-THE-SET", "price": 89.00, "weight_kg": 3.5, "stock_quantity": 8}
                ],
                "labels": ["artisanal", "fait-main"],
                "origin": region_tlemcen,
                "images": ["https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=600"]
            }
        ],
        "accessoires": [
            {
                "name": {"fr": "Collier berbère en argent", "en": "Silver Berber Necklace", "ar": "عقد بربري فضي"},
                "description": {"fr": "Collier en argent massif travaillé à la main. Motifs berbères ancestraux. Pièce d'orfèvrerie.", "en": "Handcrafted solid silver necklace. Ancestral Berber patterns. Goldsmith piece.", "ar": "عقد فضة خالصة مشغول يدوياً. أنماط بربرية أجدادية. قطعة صياغة."},
                "variants": [
                    {"name": "Unique", "sku": "ACC-COL-ARG", "price": 245.00, "weight_kg": 0.15, "stock_quantity": 4}
                ],
                "labels": ["artisanal", "fait-main"],
                "origin": region_kabylie,
                "images": ["https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=600"]
            },
            {
                "name": {"fr": "Fibule kabyle traditionnelle", "en": "Traditional Kabyle Fibula", "ar": "تازرزيت قبائلية تقليدية"},
                "description": {"fr": "Fibule en argent émaillé. Bijou traditionnel kabyle transmis de génération en génération.", "en": "Enameled silver fibula. Traditional Kabyle jewelry passed down through generations.", "ar": "تازرزيت فضة مينائية. حلي قبائلي تقليدي منقول عبر الأجيال."},
                "variants": [
                    {"name": "Taille standard", "sku": "ACC-FIB-STD", "price": 189.00, "weight_kg": 0.12, "stock_quantity": 6}
                ],
                "labels": ["artisanal", "fait-main"],
                "origin": region_kabylie,
                "images": ["https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600"]
            },
            {
                "name": {"fr": "Sac berbère tissé main", "en": "Hand-Woven Berber Bag", "ar": "حقيبة بربرية منسوجة يدوياً"},
                "description": {"fr": "Sac en laine tissée main avec motifs géométriques colorés. Authentique et pratique.", "en": "Hand-woven wool bag with colorful geometric patterns. Authentic and practical.", "ar": "حقيبة صوفية منسوجة يدوياً بأنماط هندسية ملونة. أصيلة وعملية."},
                "variants": [
                    {"name": "Taille M", "sku": "ACC-SAC-M", "price": 65.00, "weight_kg": 0.4, "stock_quantity": 14}
                ],
                "labels": ["artisanal", "fait-main"],
                "origin": region_kabylie,
                "images": ["https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=600"]
            }
        ]
    }
    
    # Add products for each new category
    products_added = []
    for category in new_categories:
        if category['slug'] in products_data:
            for prod_data in products_data[category['slug']]:
                product = {
                    "id": str(uuid.uuid4()),
                    "name": prod_data['name'],
                    "description": prod_data['description'],
                    "category": category['slug'],
                    "labels": prod_data['labels'],
                    "origin": {
                        "region_id": prod_data['origin']['id'],
                        "region_name": prod_data['origin']['name'],
                        "coordinates": prod_data['origin']['coordinates']
                    } if prod_data['origin'] else None,
                    "variants": prod_data['variants'],
                    "image_urls": prod_data['images'],
                    "videos": [],
                    "reviews_summary": {"average_rating": 0, "total_reviews": 0, "rating_distribution": {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}},
                    "frequently_bought_with": [],
                    "similar_products": [],
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
                await db.products.insert_one(product)
                products_added.append(product)
                print(f"  ✅ Produit ajouté: {prod_data['name']['fr']}")
    
    # Add promotional products
    promo_products = [
        {
            "name": {"fr": "Coffret Découverte Algérie", "en": "Algeria Discovery Box", "ar": "صندوق اكتشاف الجزائر"},
            "description": {"fr": "Coffret comprenant: huile 500ml, dattes 250g, épices 50g. Idéal pour découvrir nos saveurs.", "en": "Box including: 500ml oil, 250g dates, 50g spices. Ideal to discover our flavors.", "ar": "صندوق يتضمن: زيت 500مل، تمور 250غ، توابل 50غ. مثالي لاكتشاف نكهاتنا."},
            "variants": [{"name": "Coffret", "sku": "PROMO-DECOU", "price": 29.90, "compare_at_price": 45.70, "weight_kg": 0.8, "stock_quantity": 35}],
            "labels": ["promo", "bio"],
            "images": ["https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600"]
        },
        {
            "name": {"fr": "Lot 3 huiles aromatisées", "en": "3 Flavored Oils Pack", "ar": "مجموعة 3 زيوت معطرة"},
            "description": {"fr": "3 bouteilles 250ml: nature, citron, basilic. -30% sur le lot.", "en": "3 bottles 250ml: plain, lemon, basil. -30% on the set.", "ar": "3 زجاجات 250مل: طبيعي، ليمون، ريحان. -30% على المجموعة."},
            "variants": [{"name": "Lot de 3", "sku": "PROMO-HUILE-3", "price": 27.00, "compare_at_price": 38.70, "weight_kg": 0.75, "stock_quantity": 24}],
            "labels": ["promo"],
            "images": ["https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600"]
        },
        {
            "name": {"fr": "Pack Épices essentielles", "en": "Essential Spices Pack", "ar": "حزمة التوابل الأساسية"},
            "description": {"fr": "5 épices incontournables: ras el hanout, cumin, coriandre, paprika, harissa. Économisez 25%.", "en": "5 must-have spices: ras el hanout, cumin, coriander, paprika, harissa. Save 25%.", "ar": "5 توابل أساسية: راس الحانوت، كمون، كزبرة، بابريكا، هريسة. وفّر 25%."},
            "variants": [{"name": "Pack 5", "sku": "PROMO-EPICE-5", "price": 29.90, "compare_at_price": 39.90, "weight_kg": 0.3, "stock_quantity": 42}],
            "labels": ["promo", "bio"],
            "images": ["https://images.unsplash.com/photo-1596040033229-a0b959a33b44?w=600"]
        },
        {
            "name": {"fr": "Dattes Medjool 2kg - Format familial", "en": "Medjool Dates 2kg - Family Size", "ar": "تمور مجهول 2كغ - حجم عائلي"},
            "description": {"fr": "Format économique 2kg de dattes Medjool premium. Remise spéciale -20%.", "en": "Economical 2kg format of premium Medjool dates. Special discount -20%.", "ar": "حجم اقتصادي 2كغ من تمور المجهول الممتازة. خصم خاص -20%."},
            "variants": [{"name": "2kg", "sku": "PROMO-DATTE-2K", "price": 49.90, "compare_at_price": 63.60, "weight_kg": 2.0, "stock_quantity": 18}],
            "labels": ["promo", "bio"],
            "images": ["https://images.unsplash.com/photo-1610832745704-5293e8c6d5ee?w=600"]
        },
        {
            "name": {"fr": "Ensemble cadeau Artisanat berbère", "en": "Berber Craft Gift Set", "ar": "طقم هدية حرفية بربرية"},
            "description": {"fr": "Petit vase + bracelet argenté. Parfait pour offrir. Prix doux -40%.", "en": "Small vase + silver bracelet. Perfect gift. Sweet price -40%.", "ar": "مزهرية صغيرة + سوار فضي. هدية مثالية. سعر لطيف -40%."},
            "variants": [{"name": "Set cadeau", "sku": "PROMO-CADEAU", "price": 59.00, "compare_at_price": 99.00, "weight_kg": 0.8, "stock_quantity": 15}],
            "labels": ["promo", "artisanal"],
            "images": ["https://images.unsplash.com/photo-1610701596007-11502861dcfa?w=600"]
        }
    ]
    
    for promo_data in promo_products:
        product = {
            "id": str(uuid.uuid4()),
            "name": promo_data['name'],
            "description": promo_data['description'],
            "category": "promotions",
            "labels": promo_data['labels'],
            "origin": region_kabylie if region_kabylie else None,
            "variants": promo_data['variants'],
            "image_urls": promo_data['images'],
            "videos": [],
            "reviews_summary": {"average_rating": 0, "total_reviews": 0, "rating_distribution": {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}},
            "frequently_bought_with": [],
            "similar_products": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await db.products.insert_one(product)
        products_added.append(product)
        print(f"  ✅ Promo ajoutée: {promo_data['name']['fr']}")
    
    # Add testimonials
    all_products = products_added
    testimonials_data = []
    
    # 2 testimonials per category
    testimonial_templates = [
        {"user": "Sarah M.", "text_fr": "Produit exceptionnel ! La qualité est au rendez-vous. Je recommande vivement.", "text_en": "Exceptional product! Quality is there. Highly recommend.", "text_ar": "منتج استثنائي! الجودة موجودة. أوصي بشدة.", "rating": 5},
        {"user": "Karim B.", "text_fr": "Très satisfait de mon achat. Livraison rapide et produit conforme à la description.", "text_en": "Very satisfied with my purchase. Fast delivery and product as described.", "text_ar": "راضٍ جداً عن شرائي. توصيل سريع والمنتج كما هو موصوف.", "rating": 5},
        {"user": "Amina L.", "text_fr": "Excellent rapport qualité-prix. L'authenticité des produits est remarquable.", "text_en": "Excellent value for money. Product authenticity is remarkable.", "text_ar": "قيمة ممتازة مقابل المال. أصالة المنتج ملحوظة.", "rating": 5},
        {"user": "Mehdi T.", "text_fr": "Produit de qualité supérieure. Le goût est authentique et délicieux.", "text_en": "Superior quality product. Taste is authentic and delicious.", "text_ar": "منتج بجودة عالية. الطعم أصيل ولذيذ.", "rating": 4},
        {"user": "Fatima R.", "text_fr": "Je suis conquise ! Vraiment artisanal et fait avec soin.", "text_en": "I'm won over! Truly artisanal and made with care.", "text_ar": "أنا مقتنعة! حقاً حرفي ومصنوع بعناية.", "rating": 5},
        {"user": "Yacine A.", "text_fr": "Très beau produit, conforme à mes attentes. Emballage soigné.", "text_en": "Very beautiful product, meets my expectations. Neat packaging.", "text_ar": "منتج جميل جداً، يلبي توقعاتي. تغليف أنيق.", "rating": 5}
    ]
    
    idx = 0
    for cat in new_categories:
        cat_products = [p for p in products_added if p['category'] == cat['slug']]
        for i in range(2):
            if cat_products and idx < len(testimonial_templates):
                tpl = testimonial_templates[idx % len(testimonial_templates)]
                testimonial = {
                    "id": str(uuid.uuid4()),
                    "user_name": tpl['user'],
                    "content": {
                        "fr": tpl['text_fr'],
                        "en": tpl['text_en'],
                        "ar": tpl['text_ar']
                    },
                    "rating": tpl['rating'],
                    "product_id": cat_products[0]['id'] if cat_products else None,
                    "is_approved": True,
                    "created_at": datetime.now(timezone.utc)
                }
                await db.testimonials.insert_one(testimonial)
                testimonials_data.append(testimonial)
                idx += 1
    
    # 2 testimonials for promotions
    promo_products_added = [p for p in products_added if p['category'] == "promotions"]
    for i in range(2):
        if promo_products_added and idx < len(testimonial_templates):
            tpl = testimonial_templates[idx % len(testimonial_templates)]
            testimonial = {
                "id": str(uuid.uuid4()),
                "user_name": tpl['user'],
                "content": {
                    "fr": tpl['text_fr'],
                    "en": tpl['text_en'],
                    "ar": tpl['text_ar']
                },
                "rating": tpl['rating'],
                "product_id": promo_products_added[i % len(promo_products_added)]['id'],
                "is_approved": True,
                "created_at": datetime.now(timezone.utc)
            }
            await db.testimonials.insert_one(testimonial)
            testimonials_data.append(testimonial)
            idx += 1
    
    print(f"\n✅ {len(testimonials_data)} témoignages ajoutés")
    print(f"\n📊 RÉSUMÉ:")
    print(f"  - {len(new_categories)} nouvelles catégories")
    print(f"  - {len(products_added)} produits ajoutés ({len(promo_products)} promotions)")
    print(f"  - {len(testimonials_data)} témoignages créés")
    
    client.close()

asyncio.run(add_incremental_data())
