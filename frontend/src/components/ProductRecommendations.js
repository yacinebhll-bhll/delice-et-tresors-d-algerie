import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ShoppingCart, Heart } from 'lucide-react';
import { useCart } from '../contexts/CartContext';
import { useWishlist } from '../contexts/WishlistContext';
import { useToast } from '../hooks/use-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const ProductRecommendations = ({ productId, type = 'product' }) => {
  const [recommendations, setRecommendations] = useState({
    frequentlyBought: [],
    similar: []
  });
  const [loading, setLoading] = useState(true);
  const { addToCart } = useCart();
  const { addToWishlist, isInWishlist } = useWishlist();
  const { toast } = useToast();

  useEffect(() => {
    if (type === 'product' && productId) {
      fetchProductRecommendations();
    }
  }, [productId, type]);

  const fetchProductRecommendations = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/products/${productId}/recommendations`);
      setRecommendations({
        frequentlyBought: response.data.frequently_bought_together || [],
        similar: response.data.similar_products || []
      });
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = (product) => {
    const variant = product.variants?.[0];
    if (variant) {
      addToCart({
        id: product.id,
        name: product.name,
        price: variant.price,
        image: product.image_urls?.[0],
        variant: {
          id: variant.id,
          name: variant.name
        }
      });
      toast({
        title: 'Ajouté au panier',
        description: `${product.name.fr} a été ajouté au panier`
      });
    }
  };

  const handleAddToWishlist = async (product) => {
    try {
      await addToWishlist(product.id, product.variants?.[0]?.id);
      toast({
        title: 'Ajouté à la wishlist',
        description: `${product.name.fr} a été ajouté à votre liste de souhaits`
      });
    } catch (error) {
      toast({
        title: 'Erreur',
        description: error.response?.data?.detail || 'Veuillez vous connecter',
        variant: 'destructive'
      });
    }
  };

  const ProductCard = ({ product }) => {
    const variant = product.variants?.[0];
    const inWishlist = isInWishlist(product.id);

    return (
      <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow">
        <div className="relative mb-3">
          <img
            src={product.image_urls?.[0] || '/placeholder.jpg'}
            alt={product.name.fr}
            className="w-full h-40 object-cover rounded-lg"
          />
          <button
            onClick={() => handleAddToWishlist(product)}
            className={`absolute top-2 right-2 p-2 rounded-full bg-white shadow-md hover:bg-gray-50 ${
              inWishlist ? 'text-red-500' : 'text-gray-400'
            }`}
          >
            <Heart size={18} fill={inWishlist ? 'currentColor' : 'none'} />
          </button>
        </div>
        
        <h4 className="font-semibold mb-2 text-sm line-clamp-2">{product.name.fr}</h4>
        
        <div className="flex items-center justify-between mb-3">
          <span className="text-lg font-bold text-green-700">
            {variant?.price.toFixed(2)} €
          </span>
          {product.reviews_summary?.average_rating > 0 && (
            <span className="text-sm text-gray-600">
              ⭐ {product.reviews_summary.average_rating}
            </span>
          )}
        </div>
        
        <button
          onClick={() => handleAddToCart(product)}
          className="w-full btn-primary flex items-center justify-center gap-2"
        >
          <ShoppingCart size={16} />
          Ajouter
        </button>
      </div>
    );
  };

  if (loading) {
    return <div className="text-center py-8">Chargement des recommandations...</div>;
  }

  return (
    <div className="space-y-8">
      {/* Frequently Bought Together */}
      {recommendations.frequentlyBought.length > 0 && (
        <div>
          <h3 className="text-2xl font-bold mb-4">Souvent achetés ensemble</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {recommendations.frequentlyBought.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </div>
      )}

      {/* Similar Products */}
      {recommendations.similar.length > 0 && (
        <div>
          <h3 className="text-2xl font-bold mb-4">Produits similaires</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {recommendations.similar.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </div>
      )}

      {recommendations.frequentlyBought.length === 0 && recommendations.similar.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          Aucune recommandation disponible pour le moment
        </div>
      )}
    </div>
  );
};

export default ProductRecommendations;