import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth, useLanguage } from '../App';
import { 
  LayoutDashboard, 
  ChefHat, 
  ShoppingBag, 
  BookOpen, 
  Users, 
  Settings,
  LogOut,
  Menu,
  X,
  Home,
  BarChart3,
  Mail,
  Palette,
  Layers,
  FileText,
  MessageSquare,
  Navigation,
  Image,
  Tag,
  Package,
  Search,
  Phone,
  FolderOpen
} from 'lucide-react';

const AdminLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const { t, language } = useLanguage();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Check if user is admin
  if (!user || user.role !== 'admin') {
    navigate('/');
    return null;
  }

  const menuItems = [
    {
      name: language === 'ar' ? 'لوحة التحكم' : language === 'en' ? 'Dashboard' : 'Tableau de bord',
      href: '/admin',
      icon: LayoutDashboard
    },
    // Recipes removed - focusing on dates and olive oil products
    {
      name: language === 'ar' ? 'المنتجات' : language === 'en' ? 'Products' : 'Produits',
      href: '/admin/products',
      icon: ShoppingBag
    },
    {
      name: language === 'ar' ? 'الفئات' : language === 'en' ? 'Categories' : 'Catégories',
      href: '/admin/categories',
      icon: Layers
    },
    {
      name: language === 'ar' ? 'الصفحات' : language === 'en' ? 'Pages' : 'Pages',
      href: '/admin/pages',
      icon: FileText
    },
    {
      name: language === 'ar' ? 'الطلبات' : language === 'en' ? 'Orders' : 'Commandes',
      href: '/admin/orders',
      icon: ShoppingBag
    },
    {
      name: language === 'ar' ? 'المحتوى التاريخي' : language === 'en' ? 'Historical Content' : 'Contenu Historique',
      href: '/admin/history',
      icon: BookOpen
    },
    {
      name: language === 'ar' ? 'المستخدمون' : language === 'en' ? 'Users' : 'Utilisateurs',
      href: '/admin/users',
      icon: Users
    },
    {
      name: language === 'ar' ? 'رسائل الاتصال' : language === 'en' ? 'Contact Messages' : 'Messages de Contact',
      href: '/admin/contact',
      icon: Mail
    },
    {
      name: language === 'ar' ? 'معلومات الاتصال' : language === 'en' ? 'Contact Info' : 'Infos Contact',
      href: '/admin/contact-info',
      icon: Phone
    },
    {
      name: language === 'ar' ? 'الشهادات' : language === 'en' ? 'Testimonials' : 'Témoignages',
      href: '/admin/testimonials',
      icon: MessageSquare
    },
    {
      name: language === 'ar' ? 'قائمة التنقل' : language === 'en' ? 'Navigation Menu' : 'Menu Navigation',
      href: '/admin/navigation',
      icon: Navigation
    },
    {
      name: language === 'ar' ? 'تذييل الصفحة' : language === 'en' ? 'Footer' : 'Footer',
      href: '/admin/footer',
      icon: Layers
    },
    {
      name: language === 'ar' ? 'اللافتات' : language === 'en' ? 'Banners' : 'Bannières',
      href: '/admin/banners',
      icon: Image
    },
    {
      name: language === 'ar' ? 'رموز الترويج' : language === 'en' ? 'Promo Codes' : 'Codes Promo',
      href: '/admin/promo-codes',
      icon: Tag
    },
    {
      name: language === 'ar' ? 'المخزون' : language === 'en' ? 'Inventory' : 'Inventaire',
      href: '/admin/inventory',
      icon: Package
    },
    {
      name: language === 'ar' ? 'التحليلات' : language === 'en' ? 'Analytics' : 'Analyses',
      href: '/admin/analytics',
      icon: BarChart3
    },
    {
      name: language === 'ar' ? 'تحسين محركات البحث' : language === 'en' ? 'SEO' : 'SEO',
      href: '/admin/seo',
      icon: Search
    },
    {
      name: language === 'ar' ? 'التخصيص' : language === 'en' ? 'Customization' : 'Personnalisation',
      href: '/admin/customization',
      icon: Palette
    },
    {
      name: language === 'ar' ? 'الإعدادات' : language === 'en' ? 'Settings' : 'Paramètres',
      href: '/admin/settings',
      icon: Settings
    }
  ];

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-gray-600 bg-opacity-75 transition-opacity z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-30 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out 3xl:translate-x-0 3xl:static 3xl:inset-0 flex flex-col ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        {/* Header */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200 flex-shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-olive to-green-700 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">DT</span>
            </div>
            <span className="text-lg font-semibold text-gray-900">Admin Panel</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="3xl:hidden text-gray-500 hover:text-gray-700"
          >
            <X size={20} />
          </button>
        </div>

        <nav className="mt-4 px-3 flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href;
            
            return (
              <Link
                key={item.href}
                to={item.href}
                className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 mb-1 ${
                  isActive
                    ? 'bg-gradient-to-r from-amber-100 to-orange-50 text-amber-700 shadow-sm'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-amber-600 hover:shadow-sm'
                }`}
                onClick={() => setSidebarOpen(false)}
              >
                <Icon size={18} className="mr-3 flex-shrink-0" />
                <span className="truncate">{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* User section at bottom */}
        <div className="p-3 border-t border-gray-200 flex-shrink-0 bg-gray-50">
          <div className="flex items-center space-x-2 mb-2">
            <div className="w-8 h-8 bg-gradient-to-br from-amber-400 to-orange-500 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-white font-bold text-xs">
                {user.full_name?.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-gray-900 truncate" title={user.full_name}>
                {user.full_name}
              </p>
              <p className="text-xs text-gray-500 capitalize">
                {user.role === 'admin' 
                  ? (language === 'ar' ? 'مسؤول' : language === 'en' ? 'Admin' : 'Admin')
                  : (language === 'ar' ? 'مستخدم' : language === 'en' ? 'User' : 'Utilisateur')
                }
              </p>
            </div>
          </div>
          
          <div className="flex space-x-2">
            <Link
              to="/"
              className="flex-1 flex items-center justify-center px-2 py-1.5 text-xs text-gray-600 hover:text-amber-600 hover:bg-gray-50 rounded-lg transition-colors duration-200"
            >
              <Home size={14} className="mr-1" />
              {language === 'ar' ? 'الموقع' : language === 'en' ? 'Site' : 'Site'}
            </Link>
            <button
              onClick={handleLogout}
              className="flex-1 flex items-center justify-center px-2 py-1.5 text-xs text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors duration-200"
            >
              <LogOut size={14} className="mr-1" />
              {language === 'ar' ? 'خروج' : language === 'en' ? 'Out' : 'Quitter'}
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="3xl:pl-64 min-h-screen bg-gray-50">
        {/* Mobile/Tablet Header with Menu Button */}
        <div className="3xl:hidden sticky top-0 z-10 bg-white shadow-sm border-b border-gray-200 px-4 py-3 flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 text-gray-700 hover:text-amber-600 hover:bg-gray-100 rounded-lg transition-colors duration-200"
          >
            <Menu size={24} />
          </button>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-olive to-green-700 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">DT</span>
            </div>
            <span className="text-lg font-semibold text-gray-900">Admin Panel</span>
          </div>
          <div className="w-10"></div> {/* Spacer for centering */}
        </div>
        
        {/* Page content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;