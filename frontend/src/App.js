import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';
import { CartProvider } from './contexts/CartContext';
import { CustomizationProvider, useCustomization } from './contexts/CustomizationContext';
import { WishlistProvider } from './contexts/WishlistContext';
import { FiltersProvider } from './contexts/FiltersContext';
import ScrollToTop from './components/ScrollToTop';

// Configure axios defaults for CORS
axios.defaults.withCredentials = true;

// Components
import Header from './components/Header';
import HomePage from './components/HomePageNew';
// RecipesPage removed - focusing on dates and olive oil
import ShopPage from './components/ShopPage';
import ShopPageExtended from './components/ShopPageExtended';
import ProductDetailPageExtended from './components/ProductDetailPageExtended';
import WishlistPage from './components/WishlistPage';
import HistoryPage from './components/HistoryPage';
import ContactPage from './components/ContactPage';
import AuthPage from './components/AuthPage';
import ProfilePage from './components/ProfilePage';
import { Toaster } from './components/ui/toaster';
import Cart from './components/Cart';
import CheckoutPage from './components/CheckoutPage';
import MyOrders from './components/MyOrders';

// Admin Components
import AdminLayout from './components/AdminLayout';
import AdminDashboard from './components/AdminDashboardNew';
// AdminRecipes removed - focus on dates and olive oil products
import AdminProducts from './components/AdminProducts';
import AdminCategories from './components/AdminCategories';
import AdminPages from './components/AdminPages';
import AdminOrders from './components/AdminOrders';
import AdminUsers from './components/AdminUsers';
import AdminHistory from './components/AdminHistory';
import AdminContact from './components/AdminContact';
import AdminContactInfo from './components/AdminContactInfo';
import CustomPageView from './components/CustomPageView';
// AdminRecipeForm removed
import AdminProductForm from './components/AdminProductForm';
import AdminHistoryForm from './components/AdminHistoryForm';
import AdminAnalytics from './components/AdminAnalytics';
import AdminSettings from './components/AdminSettings';
import AdminSettingsTest from './components/AdminSettingsTest';
import AdminCustomization from './components/AdminCustomization';
import AdminTestimonials from './components/AdminTestimonials';
import AdminNavigation from './components/AdminNavigation';
import AdminFooter from './components/AdminFooter';
import AdminBanners from './components/AdminBanners';
import AdminPromoCodes from './components/AdminPromoCodes';
import AdminInventory from './components/AdminInventory';
import AdminSEO from './components/AdminSEO';
import AdminMediaLibrary from './components/AdminMediaLibrary';
import TestimonialsPage from './components/TestimonialsPage';
import AccountSettings from './components/AccountSettings';
import PromotionsPage from './components/PromotionsPage';
import ForgotPasswordPage from './components/ForgotPasswordPage';
import Footer from './components/Footer';

// Use relative URLs if BACKEND_URL is not set (works on any domain)
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

// Language Context
const LanguageContext = createContext();
export const useLanguage = () => useContext(LanguageContext);

// Auth Context
const AuthContext = createContext();
export const useAuth = () => useContext(AuthContext);

// Translations
const translations = {
  fr: {
    welcome: 'Bienvenue chez Soumam Heritage',
    recipes: 'Recettes',
    shop: 'Boutique',
    history: 'Histoire',
    login: 'Connexion',
    profile: 'Profil',
    logout: 'Déconnexion',
    home: 'Accueil',
    discover: 'Découvrez les saveurs authentiques de l\'Algérie',
    exploreRecipes: 'Explorer les recettes',
    visitShop: 'Visiter la boutique',
    learnHistory: 'Apprendre l\'histoire'
  },
  ar: {
    welcome: 'مرحباً بكم في تراث سومام',
    recipes: 'الوصفات',
    shop: 'المتجر',
    history: 'التاريخ',
    login: 'تسجيل الدخول',
    profile: 'الملف الشخصي',
    logout: 'تسجيل الخروج',
    home: 'الرئيسية',
    discover: 'اكتشف النكهات الأصيلة للجزائر',
    exploreRecipes: 'استكشاف الوصفات',
    visitShop: 'زيارة المتجر',
    learnHistory: 'تعلم التاريخ'
  },
  en: {
    welcome: 'Welcome to Soumam Heritage',
    recipes: 'Recipes',
    shop: 'Shop',
    history: 'History',
    login: 'Login',
    profile: 'Profile',
    logout: 'Logout',
    home: 'Home',
    discover: 'Discover the authentic flavors of Algeria',
    exploreRecipes: 'Explore recipes',
    visitShop: 'Visit shop',
    learnHistory: 'Learn history'
  }
};

function App() {
  const [language, setLanguage] = useState('fr');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check for existing auth token on app start
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token with backend
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUserProfile();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserProfile = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await fetchUserProfile();
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const register = async (email, password, fullName) => {
    try {
      await axios.post(`${API}/auth/register`, {
        email,
        password,
        full_name: fullName
      });
      
      // Auto login after registration
      return await login(email, password);
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const t = (key) => translations[language][key] || key;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-amber-50 to-orange-100">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-amber-600"></div>
      </div>
    );
  }

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      <AuthContext.Provider value={{ user, login, register, logout }}>
        <CustomizationProvider>
          <WishlistProvider>
            <FiltersProvider>
              <CartProvider>
                <div className="App">
                  <Toaster />
                  <BrowserRouter>
                    <ScrollToTop />
                    <Cart />
            <Routes>
              {/* Admin Routes */}
              <Route path="/admin" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminDashboard />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/products" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminProducts />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/categories" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminCategories />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/pages" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminPages />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/orders" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminOrders />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/users" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminUsers />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/history" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminHistory />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/contact" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminContact />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/contact-info" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminContactInfo />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/analytics" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminAnalytics />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/settings" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminSettings />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/customization" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminCustomization />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/testimonials" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminTestimonials />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/navigation" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminNavigation />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/footer" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminFooter />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/banners" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminBanners />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              
              <Route path="/admin/promo-codes" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminPromoCodes />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              
              <Route path="/admin/inventory" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminInventory />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              
              <Route path="/admin/seo" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminSEO />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              
              <Route path="/admin/media" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminMediaLibrary />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              
              {/* Admin Form Routes */}
              <Route path="/admin/products/new" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminProductForm />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/products/edit/:id" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminProductForm />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/history/new" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminHistoryForm />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              <Route path="/admin/history/edit/:id" element={
                user?.role === 'admin' ? (
                  <AdminLayout>
                    <AdminHistoryForm />
                  </AdminLayout>
                ) : (
                  <Navigate to="/auth" />
                )
              } />
              
              {/* Public Routes */}
              <Route path="/*" element={
                <>
                  <Header />
                  <main className="min-h-screen">
                    <Routes>
                      <Route path="/" element={<HomePage />} />
                      {/* Recipes removed - Délices et Trésors d'Algérie focuses on dates and olive oil */}
                      <Route path="/shop" element={<ShopPageExtended />} />
                      <Route path="/product/:id" element={<ProductDetailPageExtended />} />
                      <Route path="/wishlist" element={<WishlistPage />} />
                      <Route path="/history" element={<HistoryPage />} />
                      <Route path="/contact" element={<ContactPage />} />
                      <Route path="/testimonials" element={<TestimonialsPage />} />
                      <Route path="/promotions" element={<PromotionsPage />} />
                      <Route path="/checkout" element={<CheckoutPage />} />
                      <Route path="/page/:slug" element={<CustomPageView />} />
                      <Route path="/auth" element={<AuthPage />} />
                      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                      <Route path="/reset-password" element={<ForgotPasswordPage />} />
                      <Route 
                        path="/profile" 
                        element={user ? <ProfilePage /> : <Navigate to="/auth" />} 
                      />
                      <Route 
                        path="/account-settings" 
                        element={user ? <AccountSettings /> : <Navigate to="/auth" />} 
                      />
                      <Route 
                        path="/profile/orders" 
                        element={user ? <MyOrders /> : <Navigate to="/auth" />} 
                      />
                    </Routes>
                  </main>
                  <Footer />
                </>
              } />
            </Routes>
          </BrowserRouter>
        </div>
              </CartProvider>
            </FiltersProvider>
          </WishlistProvider>
        </CustomizationProvider>
      </AuthContext.Provider>
    </LanguageContext.Provider>
  );
}

export default App;