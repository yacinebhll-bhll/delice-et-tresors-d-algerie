import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useLanguage, useAuth } from '../App';
import { Menu, X, Globe, User, LogOut, ShoppingCart, ExternalLink } from 'lucide-react';
import { useCart } from '../contexts/CartContext';
import { useCustomization } from '../contexts/CustomizationContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Header = () => {
  const { language, setLanguage, t } = useLanguage();
  const { user, logout } = useAuth();
  const { setIsCartOpen, getCartCount } = useCart();
  const { customization } = useCustomization();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLanguageMenuOpen, setIsLanguageMenuOpen] = useState(false);
  const [navigationItems, setNavigationItems] = useState([]);
  const navigate = useNavigate();

  const languages = [
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'ar', name: 'العربية', flag: '🇩🇿' },
    { code: 'en', name: 'English', flag: '🇬🇧' }
  ];

  useEffect(() => {
    fetchNavigationItems();
  }, []);

  const fetchNavigationItems = async () => {
    try {
      const response = await axios.get(`${API}/navigation`);
      setNavigationItems(response.data);
    } catch (error) {
      console.error('Error fetching navigation items:', error);
      // Fallback to default navigation if API fails
      setNavigationItems([
        { id: '1', label: { fr: 'Accueil', en: 'Home', ar: 'الرئيسية' }, url: '/', is_external: false, is_active: true, order: 0 },
        { id: '2', label: { fr: 'Boutique', en: 'Shop', ar: 'المتجر' }, url: '/shop', is_external: false, is_active: true, order: 1 },
        { id: '3', label: { fr: 'Histoire', en: 'History', ar: 'التاريخ' }, url: '/history', is_external: false, is_active: true, order: 2 },
        { id: '4', label: { fr: 'Contact', en: 'Contact', ar: 'اتصل بنا' }, url: '/contact', is_external: false, is_active: true, order: 3 }
      ]);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
    setIsMenuOpen(false);
  };

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);
  const toggleLanguageMenu = () => setIsLanguageMenuOpen(!isLanguageMenuOpen);

  return (
    <header className="header">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 flex-shrink-0">
            {customization.logo_url ? (
              <img 
                src={customization.logo_url} 
                alt="Logo" 
                className="h-10 w-auto object-contain"
              />
            ) : (
              <div 
                className="w-10 h-10 rounded-lg flex items-center justify-center"
                style={{ background: `linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%)` }}
              >
                <span className="text-white font-bold text-lg">DT</span>
              </div>
            )}
            <span className="text-lg sm:text-xl font-bold text-gray-900 hidden sm:block" style={{ fontFamily: 'var(--font-heading)' }}>
              {customization.site_name || (language === 'ar' ? 
                'لذائذ وكنوز الجزائر' :
                language === 'en' ?
                'Delights & Treasures' :
                'Délices et Trésors')}
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-8">
            {navigationItems.map((item) => {
              const label = item.label[language] || item.label.fr;
              
              if (item.is_external) {
                return (
                  <a
                    key={item.id}
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-1 text-gray-700 hover:text-[#6B8E23] font-medium transition-colors duration-200 hover:underline underline-offset-4 whitespace-nowrap"
                  >
                    <span>{label}</span>
                    <ExternalLink size={14} />
                  </a>
                );
              }
              
              return (
                <Link
                  key={item.id}
                  to={item.url}
                  className="text-gray-700 hover:text-[#6B8E23] font-medium transition-colors duration-200 hover:underline underline-offset-4 whitespace-nowrap"
                >
                  {label}
                </Link>
              );
            })}
          </div>

          {/* Right Side - Language Selector & Auth */}
          <div className="hidden lg:flex items-center space-x-3">
            {/* Language Selector */}
            <div className="relative">
              <button
                onClick={toggleLanguageMenu}
                className="flex items-center space-x-2 px-3 py-2 text-gray-700 hover:text-olive transition-colors duration-200"
              >
                <Globe size={20} />
                <span className="text-sm">
                  {languages.find(lang => lang.code === language)?.flag}
                </span>
              </button>
              
              {isLanguageMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                  {languages.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => {
                        setLanguage(lang.code);
                        setIsLanguageMenuOpen(false);
                      }}
                      className={`w-full text-left px-4 py-2 hover:bg-olive-light transition-colors duration-200 flex items-center space-x-3 ${
                        language === lang.code ? 'bg-olive-light text-olive' : 'text-gray-700'
                      }`}
                    >
                      <span>{lang.flag}</span>
                      <span>{lang.name}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Cart Button */}
            <button
              onClick={() => setIsCartOpen(true)}
              className="relative p-2 text-gray-700 hover:text-olive transition-colors duration-200"
            >
              <ShoppingCart size={24} />
              {getCartCount() > 0 && (
                <span className="absolute -top-1 -right-1 bg-[#6B8E23] text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                  {getCartCount()}
                </span>
              )}
            </button>

            {/* Auth Section */}
            {user ? (
              <div className="flex items-center space-x-4">
                <Link
                  to="/profile"
                  className="flex items-center space-x-2 px-3 py-2 text-gray-700 hover:text-olive transition-colors duration-200"
                >
                  <User size={20} />
                  <span className="text-sm">{user.full_name}</span>
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 px-3 py-2 text-gray-700 hover:text-red-600 transition-colors duration-200"
                >
                  <LogOut size={20} />
                  <span className="text-sm">{t('logout')}</span>
                </button>
              </div>
            ) : (
              <Link
                to="/auth"
                className="btn-primary text-sm"
              >
                {t('login')}
              </Link>
            )}
          </div>

          {/* Mobile & Tablet Menu Button */}
          <button
            onClick={toggleMenu}
            className="lg:hidden p-2 text-gray-700 hover:text-olive transition-colors duration-200"
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile & Tablet Menu */}
        {isMenuOpen && (
          <div className="lg:hidden bg-white border-t border-gray-200">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navigationItems.map((item) => {
                const label = item.label[language] || item.label.fr;
                
                if (item.is_external) {
                  return (
                    <a
                      key={item.id}
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between px-3 py-2 text-gray-700 hover:text-[#6B8E23] hover:bg-olive-light rounded-md transition-colors duration-200"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      <span>{label}</span>
                      <ExternalLink size={14} />
                    </a>
                  );
                }
                
                return (
                  <Link
                    key={item.id}
                    to={item.url}
                    className="block px-3 py-2 text-gray-700 hover:text-[#6B8E23] hover:bg-olive-light rounded-md transition-colors duration-200"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    {label}
                  </Link>
                );
              })}
              
              <div className="border-t border-gray-200 pt-4">
                {/* Mobile Language Selector */}
                <div className="px-3 py-2">
                  <p className="text-sm font-medium text-gray-900 mb-2">Langue / Language</p>
                  <div className="space-y-1">
                    {languages.map((lang) => (
                      <button
                        key={lang.code}
                        onClick={() => {
                          setLanguage(lang.code);
                          setIsMenuOpen(false);
                        }}
                        className={`w-full text-left px-3 py-2 rounded-md flex items-center space-x-3 transition-colors duration-200 ${
                          language === lang.code ? 'bg-olive-light text-olive' : 'text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        <span>{lang.flag}</span>
                        <span>{lang.name}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Mobile Auth */}
                <div className="px-3 py-2 border-t border-gray-200 mt-4">
                  {user ? (
                    <div className="space-y-2">
                      <Link
                        to="/profile"
                        className="block w-full text-left px-3 py-2 text-gray-700 hover:text-olive hover:bg-olive-light rounded-md transition-colors duration-200"
                        onClick={() => setIsMenuOpen(false)}
                      >
                        {t('profile')} - {user.full_name}
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="block w-full text-left px-3 py-2 text-gray-700 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors duration-200"
                      >
                        {t('logout')}
                      </button>
                    </div>
                  ) : (
                    <Link
                      to="/auth"
                      className="block w-full text-center btn-primary"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      {t('login')}
                    </Link>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
};

export default Header;