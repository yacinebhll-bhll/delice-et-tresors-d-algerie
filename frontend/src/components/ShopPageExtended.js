import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../App';
import { ShoppingCart, Search, Heart, Star } from 'lucide-react';
import axios from 'axios';
import { useCart } from '../contexts/CartContext';
import { useWishlist } from '../contexts/WishlistContext';
import { useFilters } from '../contexts/FiltersContext';
import { useToast } from '../hooks/use-toast';
import AdvancedFilters from './AdvancedFilters';
import Header from './Header';
import Footer from './Footer';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const ShopPageExtended = () => {
  const navigate = useNavigate();
  const { language } = useLanguage();
  const { addToCart } = useCart();
  const { addToWishlist, isInWishlist, removeFromWishlist } = useWishlist();
  const { filters } = useFilters();
  const { toast } = useToast();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0 });

  useEffect(() => {
    fetchProducts();
  }, [filters]);

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

  const handleAddToCart = (product) => {
    const variant = product.variants?.[0];
    if (!variant) return;
    
    addToCart({
      id: product.id,
      name: product.name,
      price: variant.price,
      image: product.image_urls?.[0],
      variant: {
        id: variant.id,
        name: variant.name
      },
      quantity: 1
    });
    
    toast({
      title: 'Ajouté au panier',
      description: `${product.name?.[language] || product.name?.fr || 'Produit'} a été ajouté au panier`
    });
  };

  const handleToggleWishlist = async (product) => {
    try {
      const inWishlist = isInWishlist(product.id);
      
      if (inWishlist) {
        await removeFromWishlist(product.id);
        toast({
          title: 'Retiré',
          description: 'Produit retiré de la wishlist'
        });
      } else {
        await addToWishlist(product.id, product.variants?.[0]?.id);
        toast({
          title: 'Ajouté',
          description: 'Produit ajouté à la wishlist'
        });
      }
    } catch (error) {
      toast({
        title: 'Erreur',
        description: error.message || 'Veuillez vous connecter',
        variant: 'destructive'
      });
    }
  };

  const renderStars = (rating) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            size={14}
            className={star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-gradient-to-r from-[#6B8E23] to-[#8B7355] text-white py-12">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-4xl font-bold mb-4">
            Boutique Délices et Trésors d'Algérie
          </h1>
          <p className="text-lg opacity-90">
            Découvrez nos trésors authentiques
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1">
            <AdvancedFilters onApply={fetchProducts} />
          </div>
          
          <div className="lg:col-span-3">
            <div className="mb-6">
              <p className="text-gray-600">
                {pagination.total} produit{pagination.total > 1 ? 's' : ''} trouvé{pagination.total > 1 ? 's' : ''}
              </p>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-700 mx-auto"></div>
              </div>
            ) : products.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                <p className="text-gray-600 text-lg">Aucun produit trouvé</p>
                <p className="text-gray-500 mt-2">Essayez de modifier vos filtres</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {products.map((product) => {
                  const variant = product.variants?.[0];
                  const inWishlist = isInWishlist(product.id);
                  const isOutOfStock = variant?.stock_quantity === 0;
                  
                  return (
                    <div key={product.id} className="bg-white rounded-lg shadow-sm hover:shadow-lg transition-shadow overflow-hidden">
                      <div className="relative">
                        <img
                          src={product.image_urls?.[0] || '/placeholder.jpg'}
                          alt={product.name?.[language] || product.name?.fr || product.name || 'Product'}
                          className="w-full h-48 object-cover cursor-pointer"
                          onClick={() => navigate(`/product/${product.id}`)}
                        />
                        <button
                          onClick={() => handleToggleWishlist(product)}
                          className={`absolute top-2 right-2 p-2 rounded-full bg-white shadow-md hover:bg-gray-50 ${
                            inWishlist ? 'text-red-500' : 'text-gray-400'
                          }`}
                        >
                          <Heart size={18} fill={inWishlist ? 'currentColor' : 'none'} />
                        </button>
                        
                        {isOutOfStock && (
                          <div className="absolute bottom-0 left-0 right-0 bg-red-600 text-white text-center py-1 text-sm font-semibold">
                            Rupture de stock
                          </div>
                        )}
                      </div>
                      
                      <div className="p-4">
                        <h3 
                          className="font-semibold text-lg mb-2 line-clamp-2 cursor-pointer hover:text-green-700"
                          onClick={() => navigate(`/product/${product.id}`)}
                        >
                          {product.name?.[language] || product.name?.fr || product.name || 'Produit'}
                        </h3>
                        
                        {product.reviews_summary && product.reviews_summary.total_reviews > 0 && (
                          <div className="flex items-center gap-2 mb-2">
                            {renderStars(product.reviews_summary.average_rating)}
                            <span className="text-sm text-gray-600">
                              ({product.reviews_summary.total_reviews})
                            </span>
                          </div>
                        )}
                        
                        {product.labels && product.labels.length > 0 && (
                          <div className="flex flex-wrap gap-1 mb-3">
                            {product.labels.slice(0, 2).map((label) => (
                              <span
                                key={label}
                                className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full"
                              >
                                {label}
                              </span>
                            ))}
                          </div>
                        )}
                        
                        {variant && (
                          <div className="mb-3">
                            <p className="text-2xl font-bold text-green-700">
                              {variant.price.toFixed(2)} €
                            </p>
                          </div>
                        )}
                        
                        <button
                          onClick={() => !isOutOfStock && handleAddToCart(product)}
                          disabled={isOutOfStock}
                          className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
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
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShopPageExtended;