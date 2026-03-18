import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart, ShoppingCart, Trash2, ArrowLeft } from 'lucide-react';
import { useWishlist } from '../contexts/WishlistContext';
import { useCart } from '../contexts/CartContext';
import { useLanguage } from '../App';
import { useToast } from '../hooks/use-toast';
import Header from './Header';
import Footer from './Footer';

const WishlistPage = () => {
  const navigate = useNavigate();
  const { wishlistItems, loading, removeFromWishlist } = useWishlist();
  const { addToCart } = useCart();
  const { language } = useLanguage();
  const { toast } = useToast();

  const handleAddToCart = (item) => {
    const product = item.product;
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
      description: `${product.name[language]} a été ajouté au panier`
    });
  };

  const handleRemove = async (productId, variantId) => {
    try {
      await removeFromWishlist(productId, variantId);
      toast({
        title: 'Retiré',
        description: 'Produit retiré de votre liste de souhaits'
      });
    } catch (error) {
      toast({
        title: 'Erreur',
        description: 'Impossible de retirer le produit',
        variant: 'destructive'
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-12">
          <div className="text-center">Chargement...</div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        <button
          onClick={() => navigate('/shop')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft size={20} />
          Retour à la boutique
        </button>

        <div className="flex items-center gap-3 mb-8">
          <Heart size={32} className="text-red-500" fill="currentColor" />
          <h1 className="text-3xl font-bold">Ma Liste de Souhaits</h1>
          <span className="bg-red-100 text-red-700 px-3 py-1 rounded-full font-semibold">
            {wishlistItems.length}
          </span>
        </div>

        {wishlistItems.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <Heart size={64} className="mx-auto text-gray-300 mb-4" />
            <h2 className="text-2xl font-semibold mb-2 text-gray-800">Votre liste est vide</h2>
            <p className="text-gray-600 mb-6">
              Ajoutez des produits à votre liste de souhaits pour les retrouver facilement
            </p>
            <button
              onClick={() => navigate('/shop')}
              className="btn-primary"
            >
              Découvrir nos produits
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {wishlistItems.map((item) => {
              const product = item.product;
              const variant = product.variants?.[0];
              
              return (
                <div key={`${item.product_id}-${item.variant_id}`} className="bg-white rounded-lg shadow-sm hover:shadow-lg transition-shadow overflow-hidden">
                  <div className="relative">
                    <img
                      src={product.image_urls?.[0] || '/placeholder.jpg'}
                      alt={product.name[language]}
                      className="w-full h-48 object-cover cursor-pointer"
                      onClick={() => navigate(`/product/${product.id}`)}
                    />
                    <button
                      onClick={() => handleRemove(item.product_id, item.variant_id)}
                      className="absolute top-2 right-2 p-2 bg-white rounded-full shadow-md hover:bg-red-50 text-red-500 transition-colors"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                  
                  <div className="p-4">
                    <h3 
                      className="font-semibold text-lg mb-2 line-clamp-2 cursor-pointer hover:text-green-700"
                      onClick={() => navigate(`/product/${product.id}`)}
                    >
                      {product.name[language]}
                    </h3>
                    
                    {variant && (
                      <div className="mb-3">
                        <p className="text-sm text-gray-600 mb-1">{variant.name}</p>
                        <p className="text-2xl font-bold text-green-700">
                          {variant.price.toFixed(2)} €
                        </p>
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
                    
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleAddToCart(item)}
                        className="flex-1 btn-primary flex items-center justify-center gap-2"
                      >
                        <ShoppingCart size={16} />
                        Ajouter au panier
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
};

export default WishlistPage;