import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../App';
import { 
  ShoppingCart, Search, Heart, Star, 
  Droplets, TreePalm, Flame, Gem, ShoppingBag, X
} from 'lucide-react';
import axios from 'axios';
import { useCart } from '../contexts/CartContext';
import { useWishlist } from '../contexts/WishlistContext';
import { useFilters } from '../contexts/FiltersContext';
import { useToast } from '../hooks/use-toast';
import AdvancedFilters from './AdvancedFilters';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const CATEGORY_ICONS = {
  'huiles': Droplets,
  'dattes': TreePalm,
  'epices': Flame,
  'robes-kabyles': ShoppingBag,
  'poterie': ShoppingBag,
  'accessoires': Gem,
};

const CATEGORY_COLORS = {
  'huiles': { bg: 'bg-emerald-50', border: 'border-emerald-400', text: 'text-emerald-700', iconBg: 'bg-emerald-100' },
  'dattes': { bg: 'bg-amber-50', border: 'border-amber-400', text: 'text-amber-700', iconBg: 'bg-amber-100' },
  'epices': { bg: 'bg-red-50', border: 'border-red-400', text: 'text-red-700', iconBg: 'bg-red-100' },
  'robes-kabyles': { bg: 'bg-violet-50', border: 'border-violet-400', text: 'text-violet-700', iconBg: 'bg-violet-100' },
  'poterie': { bg: 'bg-orange-50', border: 'border-orange-400', text: 'text-orange-700', iconBg: 'bg-orange-100' },
  'accessoires': { bg: 'bg-sky-50', border: 'border-sky-400', text: 'text-sky-700', iconBg: 'bg-sky-100' },
};

const DEFAULT_COLOR = { bg: 'bg-green-50', border: 'border-green-400', text: 'text-green-700', iconBg: 'bg-green-100' };

const ShopPageExtended = () => {
  const navigate = useNavigate();
  const { language } = useLanguage();
  const { addToCart } = useCart();
  const { addToWishlist, isInWishlist, removeFromWishlist } = useWishlist();
  const { filters, updateFilter } = useFilters();
  const { toast } = useToast();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0 });

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [filters]);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      if (filters.category) params.append('category', filters.category);
      if (filters.priceMin !== null) params.append('price_min', filters.priceMin);
      if (filters.priceMax !== null) params.append('price_max', filters.priceMax);
      if (filters.origin) params.append('origin', filters.origin);
      if (filters.labels.length > 0) params.append('labels', filters.labels.join(','));
      if (filters.inStock !== null) params.append('in_stock', 'true');
      if (filters.ratingMin !== null) params.append('rating_min', filters.ratingMin);
      if (filters.search) params.append('search', filters.search);
      params.append('sort', filters.sort);
      
      const response = await axios.get(`${API}/products/filter/advanced?${params}`);
      setProducts(response.data.products || []);
      setPagination({
        page: response.data.page || 1,
        pages: response.data.pages || 1,
        total: response.data.total || 0
      });
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    updateFilter('search', searchTerm);
  };

  const handleCategoryClick = (slug) => {
    if (filters.category === slug) {
      updateFilter('category', null);
    } else {
      updateFilter('category', slug);
    }
  };

  const handleAddToCart = (product) => {
    const variant = product.variants?.[0];
    if (!variant) return;
    
    addToCart({
      id: product.id,
      name: product.name,
      price: variant.price,
      image: product.image_urls?.[0],
      variant: { id: variant.id, name: variant.name },
      quantity: 1
    });
    
    toast({
      title: 'Ajouté au panier',
      description: `${product.name?.[language] || product.name?.fr || 'Produit'} a été ajouté au panier`
    });
  };

  const handleToggleWishlist = async (product) => {
    try {
      if (isInWishlist(product.id)) {
        await removeFromWishlist(product.id);
        toast({ title: 'Retiré', description: 'Produit retiré de la wishlist' });
      } else {
        await addToWishlist(product.id, product.variants?.[0]?.id);
        toast({ title: 'Ajouté', description: 'Produit ajouté à la wishlist' });
      }
    } catch (error) {
      toast({ title: 'Erreur', description: error.message || 'Veuillez vous connecter', variant: 'destructive' });
    }
  };

  const renderStars = (rating) => (
    <div className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <Star key={star} size={13} className={star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-200'} />
      ))}
    </div>
  );

  const selectedCategoryName = useMemo(() => {
    if (!filters.category) return null;
    const cat = categories.find(c => c.slug === filters.category);
    return cat?.name?.[language] || cat?.name?.fr || filters.category;
  }, [filters.category, categories, language]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-[#6B8E23] to-[#8B7355] text-white py-12">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-4xl font-bold mb-3" data-testid="shop-title">
            Boutique Délices et Trésors d'Algérie
          </h1>
          <p className="text-lg opacity-90">
            Découvrez nos trésors : dattes Deglet Nour et huile d'olive kabyle authentique
          </p>
        </div>
      </div>

      {/* Search Bar */}
      <div className="max-w-3xl mx-auto px-4 -mt-6 relative z-10">
        <form onSubmit={handleSearch} className="relative" data-testid="search-form">
          <div className="flex items-center bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
            <div className="pl-5 text-gray-400">
              <Search size={20} />
            </div>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Rechercher un produit..."
              className="flex-1 px-4 py-4 text-base outline-none bg-transparent placeholder-gray-400"
              data-testid="search-input"
            />
            {searchTerm && (
              <button
                type="button"
                onClick={() => { setSearchTerm(''); updateFilter('search', ''); }}
                className="pr-2 text-gray-400 hover:text-gray-600"
              >
                <X size={18} />
              </button>
            )}
            <button
              type="submit"
              className="bg-[#6B8E23] hover:bg-[#5a7a1d] text-white px-6 py-4 font-medium transition-colors"
              data-testid="search-submit"
            >
              Rechercher
            </button>
          </div>
        </form>
      </div>

      {/* Category Visual Selector */}
      <div className="max-w-5xl mx-auto px-4 mt-8 mb-6">
        <div className="flex flex-wrap justify-center gap-3" data-testid="category-selector">
          {/* "All" button */}
          <button
            onClick={() => updateFilter('category', null)}
            className={`flex flex-col items-center gap-2 px-5 py-4 rounded-xl border-2 transition-all duration-200 min-w-[100px]
              ${!filters.category 
                ? 'border-green-500 bg-green-50 shadow-md scale-105' 
                : 'border-gray-200 bg-white hover:border-green-300 hover:shadow-sm'
              }`}
            data-testid="category-all"
          >
            <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${!filters.category ? 'bg-green-100' : 'bg-gray-100'}`}>
              <ShoppingBag size={22} className={!filters.category ? 'text-green-600' : 'text-gray-500'} />
            </div>
            <span className={`text-sm font-semibold ${!filters.category ? 'text-green-700' : 'text-gray-600'}`}>
              Tous
            </span>
          </button>

          {categories.map((cat) => {
            const isActive = filters.category === cat.slug;
            const IconComponent = CATEGORY_ICONS[cat.slug] || ShoppingBag;
            const colors = CATEGORY_COLORS[cat.slug] || DEFAULT_COLOR;

            return (
              <button
                key={cat.id}
                onClick={() => handleCategoryClick(cat.slug)}
                className={`flex flex-col items-center gap-2 px-5 py-4 rounded-xl border-2 transition-all duration-200 min-w-[100px]
                  ${isActive 
                    ? `${colors.border} ${colors.bg} shadow-md scale-105` 
                    : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
                  }`}
                data-testid={`category-${cat.slug}`}
              >
                <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${isActive ? colors.iconBg : 'bg-gray-100'}`}>
                  <IconComponent size={22} className={isActive ? colors.text : 'text-gray-500'} />
                </div>
                <span className={`text-sm font-semibold ${isActive ? colors.text : 'text-gray-600'}`}>
                  {cat.name?.[language] || cat.name?.fr}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Active Search Tag */}
      {filters.search && (
        <div className="max-w-7xl mx-auto px-4 mb-2">
          <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-3 py-1.5 rounded-lg text-sm">
            <Search size={14} />
            <span>Recherche : "<strong>{filters.search}</strong>"</span>
            <button onClick={() => { setSearchTerm(''); updateFilter('search', ''); }} className="hover:text-blue-900">
              <X size={14} />
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Filters */}
          <div className="lg:col-span-1">
            <AdvancedFilters onApply={fetchProducts} />
          </div>
          
          {/* Products Grid */}
          <div className="lg:col-span-3">
            <div className="flex items-center justify-between mb-5">
              <p className="text-gray-600 font-medium" data-testid="product-count">
                {pagination.total} produit{pagination.total > 1 ? 's' : ''} trouvé{pagination.total > 1 ? 's' : ''}
                {selectedCategoryName && (
                  <span className="text-gray-400 ml-1">
                    dans <span className="text-gray-600">{selectedCategoryName}</span>
                  </span>
                )}
              </p>
            </div>

            {loading ? (
              <div className="text-center py-16">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-700 mx-auto"></div>
                <p className="text-gray-500 mt-4">Chargement des produits...</p>
              </div>
            ) : products.length === 0 ? (
              <div className="bg-white rounded-xl shadow-sm p-12 text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Search size={24} className="text-gray-400" />
                </div>
                <p className="text-gray-600 text-lg font-medium">Aucun produit trouvé</p>
                <p className="text-gray-500 mt-2">Essayez de modifier vos filtres ou votre recherche</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
                {products.map((product) => {
                  const variant = product.variants?.[0];
                  const inWishlist = isInWishlist(product.id);
                  const isOutOfStock = variant?.stock_quantity === 0;
                  const hasDiscount = variant?.original_price && variant.original_price > variant.price;
                  const discount = hasDiscount ? Math.round((1 - variant.price / variant.original_price) * 100) : 0;
                  
                  return (
                    <div
                      key={product.id}
                      className="bg-white rounded-xl border border-gray-100 hover:shadow-lg hover:border-gray-200 transition-all duration-200 overflow-hidden group"
                      data-testid={`product-card-${product.id}`}
                    >
                      {/* Image */}
                      <div className="relative overflow-hidden">
                        <img
                          src={product.image_urls?.[0] || '/placeholder.jpg'}
                          alt={product.name?.[language] || product.name?.fr || 'Product'}
                          className="w-full h-52 object-cover cursor-pointer group-hover:scale-105 transition-transform duration-300"
                          onClick={() => navigate(`/product/${product.id}`)}
                        />
                        
                        {/* Wishlist Button */}
                        <button
                          onClick={() => handleToggleWishlist(product)}
                          className={`absolute top-3 right-3 p-2 rounded-full bg-white/90 backdrop-blur-sm shadow-sm hover:bg-white transition-all ${
                            inWishlist ? 'text-red-500' : 'text-gray-400 hover:text-red-400'
                          }`}
                          data-testid={`wishlist-btn-${product.id}`}
                        >
                          <Heart size={18} fill={inWishlist ? 'currentColor' : 'none'} />
                        </button>

                        {/* Stock Badge */}
                        {!isOutOfStock ? (
                          <span className="absolute top-3 left-3 bg-green-500 text-white text-xs font-bold px-2.5 py-1 rounded-md">
                            En stock
                          </span>
                        ) : (
                          <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
                            <span className="bg-red-600 text-white text-sm font-semibold px-4 py-1.5 rounded-md">
                              Rupture de stock
                            </span>
                          </div>
                        )}

                        {/* Discount Badge */}
                        {hasDiscount && (
                          <span className="absolute bottom-3 right-3 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-md">
                            -{discount}%
                          </span>
                        )}
                      </div>
                      
                      {/* Content */}
                      <div className="p-4">
                        <h3 
                          className="font-semibold text-base mb-1.5 line-clamp-2 cursor-pointer hover:text-green-700 transition-colors leading-snug"
                          onClick={() => navigate(`/product/${product.id}`)}
                        >
                          {product.name?.[language] || product.name?.fr || product.name || 'Produit'}
                        </h3>
                        
                        {/* Reviews */}
                        {product.reviews_summary && product.reviews_summary.total_reviews > 0 && (
                          <div className="flex items-center gap-1.5 mb-2">
                            {renderStars(product.reviews_summary.average_rating)}
                            <span className="text-xs text-gray-500">
                              ({product.reviews_summary.total_reviews})
                            </span>
                          </div>
                        )}
                        
                        {/* Labels */}
                        {product.labels && product.labels.length > 0 && (
                          <div className="flex flex-wrap gap-1 mb-2.5">
                            {product.labels.slice(0, 3).map((label) => (
                              <span
                                key={label}
                                className="bg-green-50 text-green-700 text-[11px] font-medium px-2 py-0.5 rounded-full border border-green-200"
                              >
                                {label}
                              </span>
                            ))}
                          </div>
                        )}
                        
                        {/* Price */}
                        {variant && (
                          <div className="flex items-baseline gap-2 mb-3">
                            <p className="text-xl font-bold text-green-700">
                              {variant.price.toFixed(2)} €
                            </p>
                            {hasDiscount && (
                              <p className="text-sm text-gray-400 line-through">
                                {variant.original_price.toFixed(2)} €
                              </p>
                            )}
                          </div>
                        )}
                        
                        {/* Add to Cart */}
                        <button
                          onClick={() => !isOutOfStock && handleAddToCart(product)}
                          disabled={isOutOfStock}
                          className="w-full btn-primary flex items-center justify-center gap-2 text-sm py-2.5 disabled:opacity-50 disabled:cursor-not-allowed"
                          data-testid={`add-to-cart-${product.id}`}
                        >
                          <ShoppingCart size={16} />
                          {isOutOfStock ? 'Indisponible' : 'Ajouter au panier'}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Pagination */}
            {pagination.pages > 1 && (
              <div className="flex justify-center gap-2 mt-8" data-testid="pagination">
                {Array.from({ length: pagination.pages }, (_, i) => i + 1).map((page) => (
                  <button
                    key={page}
                    onClick={() => {
                      updateFilter('skip', (page - 1) * 20);
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      pagination.page === page 
                        ? 'bg-green-700 text-white' 
                        : 'bg-white text-gray-600 border border-gray-200 hover:border-green-300'
                    }`}
                  >
                    {page}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShopPageExtended;
