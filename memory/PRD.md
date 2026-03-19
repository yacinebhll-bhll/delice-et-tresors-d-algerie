# Mazigho - Délices et Trésors d'Algérie - PRD

## Original Problem Statement
Application e-commerce full-stack pour vendre des produits algériens (dattes, huile d'olive, artisanat). L'application comprend un panneau d'administration complet, 9 fonctionnalités e-commerce avancées, et un système multilingue (fr/en/ar).

## Tech Stack
- **Frontend**: React (CRA), Tailwind CSS, Shadcn UI, react-leaflet
- **Backend**: FastAPI (Python), Motor (async MongoDB)
- **Database**: MongoDB (db: mazigho)
- **Auth**: JWT (email/password)

## Architecture
```
/app/backend/server.py          - Main FastAPI app (~2578 lines)
/app/backend/routes_extended.py - Extended e-commerce routes (reviews, wishlist, filters, variants, etc.)
/app/backend/models.py          - Pydantic models for extended features
/app/frontend/src/App.js        - Main React routing with global Header/Footer
/app/frontend/src/components/   - All page components
/app/frontend/src/contexts/     - React contexts (Auth, Cart, Wishlist, Filters, Customization)
```

## What's Been Implemented

### Core Features
- User auth (register, login, JWT)
- Product CRUD with multilingual support (fr/en/ar)
- Category management
- Shopping cart
- Order system with promo codes
- Contact form
- Testimonials
- Navigation menu management
- Footer settings
- Banner/hero slider
- Newsletter subscriptions
- Custom pages
- SEO settings
- Site customization
- Media library
- Inventory management
- Password reset

### 9 Advanced E-commerce Features
1. Product reviews system
2. Wishlist
3. Advanced filters (category, price, origin, labels, rating)
4. Product variants (size, weight)
5. Stock alerts
6. Shipping calculator
7. Interactive origin map (Leaflet)
8. Product recommendations
9. Product video player

### Data
- 6 categories
- 25 products (including 5 on promotion)
- 6 testimonials
- 6 navigation items

## Bugs Fixed (March 18, 2026)
1. **P0 CRITICAL - ObjectId Serialization**: Fixed MongoDB ObjectId serialization error by adding `{"_id": 0}` projection to ALL queries in server.py and routes_extended.py
2. **Data Corruption**: Cleaned nested ObjectId in `origin` field of 5 products
3. **Pydantic Model Mismatch**: Removed strict Pydantic response models for endpoints that return data with extra fields (variants, labels, reviews_summary)
4. **Testimonials Field Names**: Fixed TestimonialsSection to use correct field names (user_name/content instead of customer_name/comment)
5. **InteractiveOriginMap Crash**: Added null checks for productOrigin.coordinates
6. **Double Header**: Removed duplicate Header/Footer from ProductDetailPageExtended and WishlistPage (App.js provides them globally)

## UI Enhancement (March 19, 2026)
- Added visual category selector with professional Lucide icons on the shop page
- Added search bar with real-time search functionality
- Backend search endpoint updated to support text search across product names and descriptions
- Category selector syncs with sidebar filters

## Credentials
- Admin: yacbhll@gmail.com / Mazi@go

## Prioritized Backlog

### P1 - Next
- Activate background workers (stock_alerts, recommendations) via supervisor
- Create and activate review reminder worker
- Full user flow testing (add to cart → checkout → review)

### P2 - Future
- Performance optimization
- Image upload for reviews
- Order tracking
- Email notifications (requires SMTP config)
- File cleanup / refactoring
