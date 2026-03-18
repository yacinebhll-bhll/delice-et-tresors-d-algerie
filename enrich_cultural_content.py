#!/usr/bin/env python3
"""
Script pour enrichir le contenu culturel et historique de Soumam Heritage
"""
import requests
import json
from datetime import datetime

# Configuration
API_BASE = "https://api-fix-preview-2.preview.emergentagent.com/api"

# Données admin
ADMIN_EMAIL = "admin@soumam.com"
ADMIN_PASSWORD = "admin123"

def get_auth_token():
    """Obtenir un token d'authentification admin"""
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Échec de l'authentification: {response.text}")

def add_historical_content(token, content_data):
    """Ajouter du contenu historique"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{API_BASE}/historical-content", json=content_data, headers=headers)
    if response.status_code == 200:
        print(f"✅ Contenu ajouté: {content_data['title']['fr']}")
        return True
    else:
        print(f"❌ Erreur pour {content_data['title']['fr']}: {response.text}")
        return False

# Contenu culturel et historique enrichi
CULTURAL_CONTENT = [
    {
        "title": {
            "fr": "Les Traditions Culinaires de Kabylie",
            "ar": "التقاليد الطهوية في القبائل",
            "en": "Culinary Traditions of Kabylie"
        },
        "content": {
            "fr": "La cuisine kabyle puise ses racines dans une tradition millénaire amazighe. Les femmes kabyles, gardiennes de ces savoirs ancestraux, transmettent de mère en fille les secrets des recettes traditionnelles. Le couscous, préparé chaque vendredi, constitue le plat emblématique de cette culture. Les épices utilisées proviennent des jardins familiaux : coriandre, menthe, persil frais. La préparation du pain traditionnel, cuit dans le four en terre, rythme la vie quotidienne des villages. Les conserves d'olives, de piments et de légumes permettent de traverser les saisons. Cette cuisine reflète l'harmonie entre l'homme et la nature, caractéristique de la culture berbère.",
            "ar": "تستمد المأكولات القبائلية جذورها من تقاليد أمازيغية عريقة. النساء القبائليات، حارسات هذه المعارف الأجدادية، ينقلن من الأم إلى البنت أسرار الوصفات التقليدية. الكسكس، المحضر كل يوم جمعة، يشكل الطبق الرمزي لهذه الثقافة. البهارات المستخدمة تأتي من الحدائق العائلية: كزبرة، نعناع، بقدونس طازج. تحضير الخبز التقليدي، المخبوز في الفرن الطيني، ينظم الحياة اليومية للقرى. مخللات الزيتون والفلفل والخضار تساعد على تجاوز الفصول. هذا المطبخ يعكس الانسجام بين الإنسان والطبيعة، سمة مميزة للثقافة البربرية.",
            "en": "Kabyle cuisine draws its roots from an ancient Amazigh tradition. Kabyle women, guardians of this ancestral knowledge, pass down the secrets of traditional recipes from mother to daughter. Couscous, prepared every Friday, is the emblematic dish of this culture. The spices used come from family gardens: coriander, mint, fresh parsley. The preparation of traditional bread, baked in clay ovens, punctuates daily village life. Preserved olives, peppers and vegetables help get through the seasons. This cuisine reflects the harmony between man and nature, characteristic of Berber culture."
        },
        "region": "kabylie",
        "image_urls": [
            "https://images.unsplash.com/photo-1716823141581-12b24feb01ea",
            "https://images.unsplash.com/photo-1713007009692-c055a4a5e2df"
        ]
    },
    {
        "title": {
            "fr": "Ath M'lickech : Village Ancestral de la Vallée de Soumam",
            "ar": "آث مليكش: قرية أجدادية في وادي الصومام",
            "en": "Ath M'lickech: Ancestral Village of the Soumam Valley"
        },
        "content": {
            "fr": "Ath M'lickech, dont le nom signifie 'les enfants de Mlickech' en berbère, est un village emblématique de la vallée de Soumam. Niché sur les contreforts des montagnes kabyles, ce village a préservé son authenticité architecturale avec ses maisons en pierre traditionnelles. Les ruelles pavées serpentent entre les habitations séculaires, témoins d'un mode de vie ancestral. Le village est réputé pour ses oliviers centenaires et ses jardins en terrasses qui produisent les légumes les plus savoureux de la région. Les femmes d'Ath M'lickech perpétuent l'art du tissage traditionnel, créant des tapis et des vêtements aux motifs berbères authentiques. Les soirées résonnent encore des chants traditionnels kabyles, transmis oralement depuis des générations.",
            "ar": "آث مليكش، الذي يعني 'أبناء مليكش' بالبربرية، قرية رمزية في وادي الصومام. متربع على سفوح الجبال القبائلية، حافظ هذا القرية على أصالته المعمارية ببيوته الحجرية التقليدية. الأزقة المرصوفة تتعرج بين المساكن العريقة، شواهد على نمط حياة أجدادي. القرية مشهورة بأشجار الزيتون المعمرة وحدائقها المدرجة التي تنتج أشهى الخضار في المنطقة. نساء آث مليكش يواصلن فن النسيج التقليدي، ينتجن سجاد وملابس بزخارف بربرية أصيلة. الأمسيات لا تزال تتردد فيها الأغاني القبائلية التقليدية، المتوارثة شفهياً منذ أجيال.",
            "en": "Ath M'lickech, whose name means 'the children of Mlickech' in Berber, is an emblematic village of the Soumam valley. Nestled on the foothills of the Kabyle mountains, this village has preserved its architectural authenticity with its traditional stone houses. Cobbled streets wind between century-old dwellings, witnesses to an ancestral way of life. The village is renowned for its century-old olive trees and terraced gardens that produce the most flavorful vegetables in the region. The women of Ath M'lickech perpetuate the art of traditional weaving, creating carpets and clothing with authentic Berber motifs. The evenings still resonate with traditional Kabyle songs, transmitted orally for generations."
        },
        "region": "vallee-soumam",
        "image_urls": [
            "https://images.pexels.com/photos/21847351/pexels-photo-21847351.jpeg",
            "https://images.unsplash.com/photo-1646486087126-20435bad3b76"
        ]
    },
    {
        "title": {
            "fr": "Tazmalt : Carrefour Commercial Historique",
            "ar": "تازمالت: ملتقى تجاري تاريخي",
            "en": "Tazmalt: Historic Commercial Crossroads"
        },
        "content": {
            "fr": "Tazmalt occupe une position stratégique dans la vallée de Soumam, ayant servi de carrefour commercial depuis l'époque romaine. Son nom berbère évoque 'l'endroit des échanges', reflétant sa vocation marchande ancestrale. La ville a conservé des vestiges de son passé prestigieux : anciennes fondouks (caravansérails), marchés traditionnels et architectures ottomanes. Les artisans de Tazmalt sont réputés pour leur savoir-faire dans la bijouterie kabyle, créant des parures en argent ornées de corail et d'émaux colorés. La poterie locale, aux motifs géométriques berbères, témoigne d'une tradition artisanale multiséculaire. Chaque jeudi, le marché hebdomadaire rassemble les producteurs de toute la vallée, perpétuant une tradition commerciale millénaire.",
            "ar": "تحتل تازمالت موقعاً استراتيجياً في وادي الصومام، خدمت كملتقى تجاري منذ العهد الروماني. اسمها البربري يشير إلى 'مكان التبادل'، مما يعكس دعوتها التجارية الأجدادية. حافظت المدينة على بقايا ماضيها المرموق: فنادق قديمة (خانات)، أسواق تقليدية ومعمار عثماني. حرفيو تازمالت مشهورون بمهارتهم في صناعة المجوهرات القبائلية، ينتجون حلي فضية مزينة بالمرجان والمينا الملونة. الفخار المحلي، بزخارفه الهندسية البربرية، يشهد على تقليد حرفي متعدد القرون. كل خميس، السوق الأسبوعي يجمع منتجي كامل الوادي، مواصلاً تقليداً تجارياً ألفياً.",
            "en": "Tazmalt occupies a strategic position in the Soumam valley, having served as a commercial crossroads since Roman times. Its Berber name evokes 'the place of exchanges', reflecting its ancestral merchant vocation. The city has preserved vestiges of its prestigious past: ancient fondouks (caravanserais), traditional markets and Ottoman architecture. Tazmalt artisans are renowned for their expertise in Kabyle jewelry, creating silver ornaments decorated with coral and colored enamels. Local pottery, with geometric Berber motifs, testifies to a multi-century artisanal tradition. Every Thursday, the weekly market brings together producers from throughout the valley, perpetuating a millennial commercial tradition."
        },
        "region": "vallee-soumam",
        "image_urls": [
            "https://images.unsplash.com/photo-1720718517204-a66cc17a1052",
            "https://images.unsplash.com/photo-1578985545062-69928b1d9587"
        ]
    },
    {
        "title": {
            "fr": "Les Femmes Kabyles : Gardiennes du Patrimoine",
            "ar": "النساء القبائليات: حارسات التراث",
            "en": "Kabyle Women: Guardians of Heritage"
        },
        "content": {
            "fr": "Les femmes kabyles jouent un rôle central dans la préservation du patrimoine culturel amazigh. Détentrices des savoirs ancestraux, elles transmettent la langue tamazight, les chants traditionnels et l'art culinaire. Leurs robes traditionnelles, ornées de motifs géométriques et de bijoux en argent, sont des œuvres d'art vivantes. L'artisanat féminin kabyle inclut le tissage de tapis aux couleurs vives, la poterie décorée et la broderie fine. Les femmes organisent les cérémonies traditionnelles, gardant vivantes les coutumes liées aux cycles de la vie : naissance, mariage, récoltes. Leur rôle dans l'économie familiale est essentiel : gestion des jardins, élevage, transformation des produits agricoles. Cette transmission matrilinéaire assure la continuité culturelle berbère à travers les générations.",
            "ar": "تلعب النساء القبائليات دوراً محورياً في حفظ التراث الثقافي الأمازيغي. حاملات المعارف الأجدادية، ينقلن اللغة التامازيغت والأغاني التقليدية وفن الطبخ. فساتينهن التقليدية، المزينة بزخارف هندسية ومجوهرات فضية، أعمال فنية حية. الحرفة النسائية القبائلية تشمل نسج السجاد بألوان زاهية، الفخار المزخرف والتطريز الناعم. النساء ينظمن الاحتفالات التقليدية، يبقين العادات المرتبطة بدورات الحياة حية: الولادة، الزواج، المحاصيل. دورهن في الاقتصاد العائلي أساسي: إدارة الحدائق، تربية المواشي، تحويل المنتجات الزراعية. هذا النقل الأمومي يضمن الاستمرارية الثقافية البربرية عبر الأجيال.",
            "en": "Kabyle women play a central role in preserving Amazigh cultural heritage. Holders of ancestral knowledge, they transmit the Tamazight language, traditional songs and culinary art. Their traditional dresses, decorated with geometric motifs and silver jewelry, are living works of art. Kabyle women's crafts include weaving brightly colored carpets, decorated pottery and fine embroidery. Women organize traditional ceremonies, keeping alive customs related to life cycles: birth, marriage, harvests. Their role in the family economy is essential: garden management, livestock, processing of agricultural products. This matrilineal transmission ensures Berber cultural continuity across generations."
        },
        "region": "kabylie",
        "image_urls": [
            "https://images.unsplash.com/photo-1713007009692-c055a4a5e2df",
            "https://images.unsplash.com/photo-1720718517204-a66cc17a1052"
        ]
    },
    {
        "title": {
            "fr": "L'Architecture Traditionnelle Kabyle",
            "ar": "العمارة التقليدية القبائلية",
            "en": "Traditional Kabyle Architecture"
        },
        "content": {
            "fr": "L'architecture kabyle traditionnelle témoigne d'une adaptation parfaite au climat méditerranéen montagnard. Les maisons en pierre locale, aux toits de tuiles rouges, s'intègrent harmonieusement dans le paysage. La disposition des villages suit la topographie des collines, créant des ensembles urbains organiques. Chaque habitation comprend une cour centrale (rahba) autour de laquelle s'organisent les pièces de vie. Les murs épais en pierre sèche assurent une isolation naturelle. Les ouvertures, savamment orientées, favorisent la ventilation naturelle. Les greniers surélevés (ikhouban) protègent les réserves alimentaires. Cette architecture vernaculaire, développée au fil des siècles, représente un patrimoine architectural unique en Méditerranée, alliant fonctionnalité et esthétique.",
            "ar": "العمارة القبائلية التقليدية تشهد على تكيف مثالي مع المناخ المتوسطي الجبلي. البيوت من الحجر المحلي، بأسقف القرميد الأحمر، تندمج بانسجام في المشهد. ترتيب القرى يتبع طوبوغرافية التلال، منشئاً مجمعات حضرية عضوية. كل مسكن يتضمن فناء مركزي (رحبة) تتنظم حوله غرف المعيشة. الجدران السميكة من الحجر الجاف تؤمن عزلة طبيعية. الفتحات، موجهة بحكمة، تفضل التهوية الطبيعية. المخازن المرتفعة (إخوبان) تحمي الاحتياطيات الغذائية. هذه العمارة العامية، المطورة عبر القرون، تمثل تراثاً معمارياً فريداً في المتوسط، يوحد الوظيفية والجمالية.",
            "en": "Traditional Kabyle architecture testifies to perfect adaptation to the Mediterranean mountain climate. Houses built with local stone and red tile roofs integrate harmoniously into the landscape. Village layout follows hill topography, creating organic urban ensembles. Each dwelling includes a central courtyard (rahba) around which living spaces are organized. Thick dry stone walls provide natural insulation. Openings, skillfully oriented, promote natural ventilation. Elevated granaries (ikhouban) protect food reserves. This vernacular architecture, developed over centuries, represents unique architectural heritage in the Mediterranean, combining functionality and aesthetics."
        },
        "region": "kabylie",
        "image_urls": [
            "https://images.unsplash.com/photo-1716823141581-12b24feb01ea",
            "https://images.pexels.com/photos/21847351/pexels-photo-21847351.jpeg"
        ]
    },
    {
        "title": {
            "fr": "L'Olivier en Kabylie : Arbre Sacré et Pilier Économique",
            "ar": "الزيتون في القبائل: شجرة مقدسة وركيزة اقتصادية",
            "en": "The Olive Tree in Kabylie: Sacred Tree and Economic Pillar"
        },
        "content": {
            "fr": "L'olivier occupe une place sacrée dans la culture kabyle. Ces arbres centenaires, parfois millénaires, structurent le paysage en terrasses de la région. Chaque famille possède ses oliviers, héritage transmis de génération en génération. L'huile d'olive kabyle, au goût fruité incomparable, constitue la base de la cuisine locale. La récolte des olives, en novembre, mobilise toute la communauté dans une ambiance festive. Les méthodes traditionnelles de pressurage, dans les moulins à huile ancestraux, préservent les qualités nutritionnelles du fruit. Au-delà de l'aspect économique, l'olivier symbolise la permanence et la résistance du peuple kabyle. Les vieux oliviers marquent les limites des propriétés et servent de repères géographiques. Cette oléiculture traditionnelle, respectueuse de l'environnement, fait de la Kabylie l'une des régions productrices d'huile d'olive les plus réputées du Maghreb.",
            "ar": "الزيتون يحتل مكانة مقدسة في الثقافة القبائلية. هذه الأشجار المعمرة، أحياناً ألفية، تنظم مشهد المدرجات في المنطقة. كل عائلة تملك أشجار زيتونها، ميراث متوارث من جيل إلى جيل. زيت الزيتون القبائلي، بطعمه الثمري المتفرد، يشكل أساس المطبخ المحلي. قطف الزيتون، في نوفمبر، يحرك كامل المجتمع في جو احتفالي. طرق العصر التقليدية، في معاصر الزيت الأجدادية، تحافظ على الخصائص الغذائية للثمرة. ما وراء الجانب الاقتصادي، الزيتون يرمز للدوام ومقاومة الشعب القبائلي. الزيتون العتيق يحدد حدود الممتلكات ويخدم كمعالم جغرافية. زراعة الزيتون التقليدية هذه، المحترمة للبيئة، تجعل القبائل واحدة من مناطق إنتاج زيت الزيتون الأكثر شهرة في المغرب العربي.",
            "en": "The olive tree holds a sacred place in Kabyle culture. These century-old, sometimes millennial trees structure the region's terraced landscape. Each family owns its olive trees, a heritage passed down from generation to generation. Kabyle olive oil, with its incomparable fruity taste, forms the basis of local cuisine. The olive harvest in November mobilizes the entire community in a festive atmosphere. Traditional pressing methods in ancestral oil mills preserve the fruit's nutritional qualities. Beyond the economic aspect, the olive tree symbolizes the permanence and resistance of the Kabyle people. Old olive trees mark property boundaries and serve as geographical landmarks. This traditional olive growing, respectful of the environment, makes Kabylie one of the most renowned olive oil producing regions in the Maghreb."
        },
        "region": "kabylie",
        "image_urls": [
            "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "https://images.unsplash.com/photo-1544787219-7f47ccb76574"
        ]
    }
]

def main():
    """Fonction principale d'enrichissement culturel"""
    print("🚀 Enrichissement du contenu culturel et historique de Soumam Heritage")
    print("=" * 80)
    
    try:
        # Obtenir le token d'authentification
        print("🔐 Connexion à l'API...")
        token = get_auth_token()
        print(f"✅ Authentification réussie")
        
        # Ajouter chaque contenu historique
        success_count = 0
        failed_count = 0
        
        for i, content in enumerate(CULTURAL_CONTENT, 1):
            print(f"\n📖 Ajout du contenu {i}/{len(CULTURAL_CONTENT)}...")
            if add_historical_content(token, content):
                success_count += 1
            else:
                failed_count += 1
        
        # Résumé final
        print("\n" + "=" * 80)
        print(f"📊 RÉSUMÉ FINAL:")
        print(f"✅ Contenus ajoutés avec succès: {success_count}")
        print(f"❌ Échecs: {failed_count}")
        print(f"📈 Total: {len(CULTURAL_CONTENT)} contenus traités")
        
        if success_count > 0:
            print(f"\n🎉 {success_count} nouveaux contenus culturels ont été ajoutés!")
            print("📍 Régions couvertes: Algérie, Kabylie, Vallée de Soumam")
            print("🌍 Langues: Français, Arabe, Anglais")
            print("Vous pouvez les voir sur: https://api-fix-preview-2.preview.emergentagent.com/history")
        
    except Exception as e:
        print(f"❌ Erreur générale: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()