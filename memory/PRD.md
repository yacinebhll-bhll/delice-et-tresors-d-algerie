# Mazigho - Délices et Trésors d'Algérie - PRD

## Original Problem Statement
Application e-commerce full-stack pour vendre des produits algériens premium (dattes, huile d'olive, épices, artisanat berbère). L'application comprend un panneau d'administration complet, 9 fonctionnalités e-commerce avancées, et un système multilingue (fr/en/ar).

## Tech Stack
- **Frontend**: React (CRA), Tailwind CSS, Shadcn UI, react-leaflet, Lucide React
- **Backend**: FastAPI (Python), Motor (async MongoDB)
- **Database**: MongoDB (db: mazigho)
- **Auth**: JWT (email/password)
- **Workers**: 3 background workers (supervisor-managed)

## Architecture
```
/app/backend/server.py             - Main FastAPI app (~2500 lines)
/app/backend/routes_extended.py    - Extended e-commerce routes
/app/backend/models.py             - Pydantic models
/app/backend/email_service.py      - Email sending (Gmail SMTP)
/app/backend/worker_stock_alerts.py     - Stock alert notifications (every 1h)
/app/backend/worker_recommendations.py  - Product recommendations (every 24h)
/app/backend/worker_review_reminders.py - Review reminders (every 6h)
/app/frontend/src/App.js           - Main routing with global Header/Footer
/app/frontend/src/components/      - All page components
/app/frontend/src/contexts/        - React contexts (Auth, Cart, Wishlist, Filters)
```

## What's Been Implemented

### Core Features
- User auth (register, login, JWT)
- Product CRUD with multilingual support (fr/en/ar)
- Category management (6 categories)
- Shopping cart with promo codes
- Order system (create, track, manage)
- Contact form, Testimonials (6)
- Newsletter, Navigation, Banners (4 hero slides)
- Media library, Inventory management
- Password reset, SEO, Site customization

### 9 Advanced E-commerce Features
1. Product reviews with image upload (max 4 photos)
2. Wishlist
3. Advanced filters + search bar
4. Product variants (size, weight)
5. Stock alerts
6. Shipping calculator
7. Interactive origin map (Leaflet)
8. Product recommendations
9. Product video player

### UI Enhancements
- Hero carousel with 4 AI-generated images (Dattes, Huile d'Olive, Épices, Artisanat)
- Visual category selector with Lucide icons on shop page
- Search bar with real-time filtering
- CTA buttons redirect to shop with category pre-selected
- Order tracking timeline (5 steps: En attente → Confirmée → Préparation → Expédiée → Livrée)
- Mini timeline on order list cards

### Background Workers (Active)
- **worker_stock_alerts**: Checks low stock products, notifies subscribers (every 1h)
- **worker_recommendations**: Generates product recommendations from order patterns (every 24h)
- **worker_review_reminders**: Sends reminders 3-14 days after delivery for unreviewed products (every 6h)

### Data
- 6 categories, 25 products (5 on promo), 6 testimonials, 4 hero banners, 6 nav items

## Bugs Fixed
1. P0 - ObjectId serialization ({"_id": 0} on all queries)
2. Nested ObjectId in origin field
3. Pydantic model mismatch for extended fields
4. Testimonials field names
5. InteractiveOriginMap null coordinates
6. Double Header/Footer
7. Stock check with variant support
8. Duplicate order routes removed

## Testing Status
- **Iteration 1**: Backend 100%, Frontend 95%+
- **Iteration 2**: Backend 15/15 (100%), Frontend 100%

## Credentials
- Admin: yacbhll@gmail.com / Mazi@go

## Prioritized Backlog

### P1 - Next
- Fix minor React warning in AuthPage (setState during render)
- SMTP App Password configuration for real email sending

### P2 - Future
- Order email notifications (confirmation, status updates)
- Product image management in admin
- Performance optimization (pagination, caching)
- Advanced analytics dashboard
