# 📋 RAPPORT TECHNIQUE - MAZIGHO.COM
## Application E-commerce "Délices et Trésors d'Algérie"

---

## 1️⃣ RÉSUMÉ DU PROJET

### Type d'application
- **Boutique e-commerce complète** (fullstack)
- **Architecture monolithique** : Frontend + Backend + Base de données intégrés
- **100% autonome** : Aucune dépendance à Shopify ou autre plateforme e-commerce externe

### Objectif principal
- Vente en ligne de produits alimentaires algériens authentiques (dattes Deglet Nour, huile d'olive kabyle, épices, etc.)
- Site multilingue (Français, Anglais, Arabe)
- Panel d'administration complet pour gérer produits, commandes, clients, et contenus

### Domaines
- **Production** : https://mazigho.com
- **Preview** : https://api-fix-preview-2.preview.emergentagent.com

---

## 2️⃣ ARCHITECTURE TECHNIQUE

### Frontend
| Technologie | Version | Usage |
|-------------|---------|-------|
| **React** | 19.0.0 | Framework UI principal |
| **React Router DOM** | 7.5.1 | Routing SPA |
| **Tailwind CSS** | 3.x | Framework CSS utilitaire |
| **Shadcn/UI** | Latest | Composants UI (basés sur Radix) |
| **Axios** | 1.x | Client HTTP pour les appels API |
| **Lucide React** | Latest | Bibliothèque d'icônes |
| **React Hook Form** | 7.x | Gestion des formulaires |
| **Zod** | 3.x | Validation des données |

### Backend
| Technologie | Version | Usage |
|-------------|---------|-------|
| **Python** | 3.11 | Langage de programmation |
| **FastAPI** | 0.110.1 | Framework API REST |
| **Uvicorn** | 0.25.0 | Serveur ASGI |
| **Motor** | 3.3.1 | Driver MongoDB asynchrone |
| **Pydantic** | 2.x | Validation et sérialisation |
| **PyJWT** | 2.10.1 | Gestion des tokens JWT |
| **Passlib + bcrypt** | Latest | Hashage des mots de passe |

### Base de données
| Technologie | Version | Usage |
|-------------|---------|-------|
| **MongoDB** | 6.x | Base de données NoSQL |
| **Motor** | 3.3.1 | Driver asynchrone Python |

### Mode de fonctionnement
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Backend       │────▶│   MongoDB       │
│   (React SPA)   │ API │   (FastAPI)     │     │   (Database)    │
│   Port 3000     │ REST│   Port 8001     │     │   Port 27017    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │
         │              ┌───────┴───────┐
         │              │ Gmail SMTP    │
         │              │ (Emails)      │
         │              └───────────────┘
         ▼
    Navigateur utilisateur
```

**Note importante** : C'est un site **autonome**, PAS un frontend headless connecté à Shopify. Toute la logique e-commerce est gérée en interne.

---

## 3️⃣ GESTION DES DONNÉES (PAS SHOPIFY)

### ⚠️ Ce projet N'UTILISE PAS Shopify

Les produits, commandes, et clients sont **entièrement gérés en interne** :

### Récupération des produits
- **Collection MongoDB** : `products`
- **Endpoint** : `GET /api/products`
- **Données** : nom (multilingue), description, prix, stock, images, catégorie

### Gestion des commandes
- **Collection MongoDB** : `orders`
- **Création** : `POST /api/orders`
- **Workflow** : pending → confirmed → shipped → delivered / cancelled
- **Notifications** : Email automatique au client et à l'admin

### Variables d'environnement requises
```
# Backend (.env)
MONGO_URL              # URL de connexion MongoDB
DB_NAME                # Nom de la base de données
JWT_SECRET_KEY         # Clé secrète pour les tokens JWT
CORS_ORIGINS           # Origines autorisées (CORS)
GMAIL_USER             # Email Gmail pour l'envoi
GMAIL_APP_PASSWORD     # Mot de passe d'application Gmail
FRONTEND_URL           # URL du frontend (pour les emails)

# Frontend (.env)
REACT_APP_BACKEND_URL  # URL de l'API backend (vide = relatif)
```

---

## 4️⃣ STRUCTURE DES PAGES ET FONCTIONNALITÉS

### Pages publiques
| Page | Route | Description |
|------|-------|-------------|
| Accueil | `/` | Hero slider, catégories, produits vedettes, témoignages |
| Boutique | `/shop` | Catalogue produits avec filtres et recherche |
| Produit | `/product/:id` | Fiche produit détaillée |
| Panier | Modal sidebar | Panier avec quantités modifiables |
| Checkout | `/checkout` | Formulaire de commande + codes promo |
| Contact | `/contact` | Formulaire de contact |
| Histoire | `/history` | Histoire de l'entreprise |
| Témoignages | `/testimonials` | Avis clients |
| Promotions | `/promotions` | Codes promo actifs |
| Pages custom | `/page/:slug` | CGV, politique de confidentialité, etc. |

### Pages authentification
| Page | Route | Description |
|------|-------|-------------|
| Connexion/Inscription | `/auth` | Formulaire unifié |
| Mot de passe oublié | `/forgot-password` | Demande de réinitialisation |
| Réinitialisation | `/reset-password?token=...` | Nouveau mot de passe |
| Profil | `/profile` | Informations utilisateur |
| Mes commandes | `/profile/orders` | Historique des commandes |
| Paramètres | `/account-settings` | Modification du compte |

### Panel Administration (`/admin/*`)
| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/admin` | Statistiques, graphiques, aperçu |
| Produits | `/admin/products` | CRUD produits |
| Catégories | `/admin/categories` | CRUD catégories |
| Commandes | `/admin/orders` | Gestion des commandes |
| Utilisateurs | `/admin/users` | Gestion des clients |
| Codes promo | `/admin/promo-codes` | Création/gestion des promos |
| Bannières | `/admin/banners` | Slider page d'accueil |
| Pages | `/admin/pages` | CGV, mentions légales, etc. |
| Témoignages | `/admin/testimonials` | Modération des avis |
| Messages | `/admin/contact` | Messages de contact |
| Navigation | `/admin/navigation` | Menu du site |
| Footer | `/admin/footer` | Pied de page |
| Inventaire | `/admin/inventory` | Gestion des stocks |
| SEO | `/admin/seo` | Méta-données du site |
| Personnalisation | `/admin/customization` | Couleurs, polices, logo |
| Paramètres | `/admin/settings` | Infos de contact du site |
| Médias | `/admin/media` | Bibliothèque d'images |

### Fonctionnement du panier
```javascript
// Contexte React (CartContext)
- Stockage : localStorage (persiste entre les sessions)
- Fonctions : addToCart, removeFromCart, updateQuantity, clearCart
- Calcul automatique : sous-total, réductions, total
```

### Fonctionnement du checkout
1. **Saisie des informations client** : nom, email, téléphone, adresse
2. **Application code promo** (optionnel) : validation en temps réel
3. **Création de la commande** : `POST /api/orders`
4. **Confirmation** : Numéro de commande + email de confirmation
5. **Suivi** : Statut visible dans "Mes commandes"

### Fonctions spéciales
- **Filtres** : Par catégorie, par prix, par disponibilité
- **Recherche** : Recherche textuelle sur nom et description
- **Tri** : Prix croissant/décroissant, nouveautés, popularité
- **Multilingue** : Tous les textes en FR/EN/AR
- **Codes promo** : Pourcentage ou montant fixe, date d'expiration

---

## 5️⃣ DÉPENDANCES EXTERNES

### Services tiers utilisés

| Service | Usage | Intégration |
|---------|-------|-------------|
| **Gmail SMTP** | Envoi d'emails (commandes, reset password) | Bibliothèque Python `smtplib` |
| **Google Fonts** | Polices personnalisables | CDN, chargement dynamique |
| **Cloudflare** | CDN/DNS pour mazigho.com | Configuration DNS externe |

### Ce qui N'EST PAS utilisé
- ❌ Shopify (aucune intégration)
- ❌ Stripe/PayPal (paiement à la livraison uniquement)
- ❌ Analytics externe (pas de Google Analytics)
- ❌ Services d'authentification externe (JWT interne)

### Intégration Gmail SMTP
```python
# Configuration dans backend/.env
GMAIL_USER=votre-email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

# Utilisation
- Confirmation de commande
- Réinitialisation de mot de passe
- Notifications admin
```

---

## 6️⃣ LIMITATIONS ET POINTS IMPORTANTS

### Ce qui est stocké localement (MongoDB)
| Données | Collection | Contrôle total |
|---------|------------|----------------|
| Produits | `products` | ✅ Oui |
| Catégories | `categories` | ✅ Oui |
| Commandes | `orders` | ✅ Oui |
| Utilisateurs | `users` | ✅ Oui |
| Témoignages | `testimonials` | ✅ Oui |
| Pages personnalisées | `custom_pages` | ✅ Oui |
| Configuration du site | `settings`, `customization` | ✅ Oui |
| Médias uploadés | `media` + dossier `/uploads` | ✅ Oui |

### Ce qui dépend de services externes
| Service | Dépendance | Impact si indisponible |
|---------|------------|------------------------|
| Gmail SMTP | Envoi d'emails | ⚠️ Pas d'emails (commandes, reset) |
| Google Fonts | Polices web | ⚠️ Fallback sur polices système |
| MongoDB | Base de données | ❌ Site totalement hors ligne |

### Limitations actuelles
1. **Paiement** : Uniquement "paiement à la livraison" (pas de paiement en ligne)
2. **Stock** : Gestion manuelle (pas de sync automatique avec fournisseurs)
3. **Livraison** : Pas de calcul automatique des frais selon la zone
4. **Multi-vendeur** : Non supporté (une seule boutique)

### Points d'attention pour la migration
1. **Base de données** : Exporter MongoDB vers MongoDB Atlas ou autre
2. **Fichiers uploadés** : Copier le dossier `/app/backend/uploads/`
3. **Variables d'environnement** : Recréer les fichiers `.env`
4. **Domaine** : Reconfigurer DNS si changement d'hébergeur

---

## 7️⃣ RÉSUMÉ POUR IA EXTERNE

```
mazigho.com est une boutique e-commerce autonome (sans Shopify) construite avec :

FRONTEND : React 19 + Tailwind CSS + Shadcn/UI
BACKEND  : FastAPI (Python) + JWT Auth
DATABASE : MongoDB

Les produits, commandes et clients sont entièrement gérés en interne.
Pas de paiement en ligne (paiement à la livraison uniquement).
Emails envoyés via Gmail SMTP.
Site multilingue (FR/EN/AR).
Panel admin complet pour tout gérer.

Architecture : SPA React qui appelle une API REST FastAPI,
laquelle interagit avec MongoDB pour stocker/récupérer les données.
```

---

*Rapport généré le 11 janvier 2026*
