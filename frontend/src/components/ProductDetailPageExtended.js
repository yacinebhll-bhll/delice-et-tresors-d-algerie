import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Heart, Share2, ArrowLeft, ShoppingCart, Star } from 'lucide-react';
import { useCart } from '../contexts/CartContext';
import { useWishlist } from '../contexts/WishlistContext';
import { useLanguage } from '../App';
import { useToast } from '../hooks/use-toast';
import VariantSelector from './VariantSelector';
import ProductVideoPlayer from './ProductVideoPlayer';
import InteractiveOriginMap from './InteractiveOriginMap';
import ProductReviews from './ProductReviews';
import ProductRecommendations from './ProductRecommendations';
import StockAlert from './StockAlert';
import Header from './Header';
import Footer from './Footer';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const ProductDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { language } = useLanguage();
  const { addToCart } = useCart();
  const { addToWishlist, isInWishlist, removeFromWishlist } = useWishlist();
  const { toast } = useToast();
  const [product, setProduct] = useState(null);
  const [selectedVariant, setSelectedVariant] = useState(null);
  const [selectedImage, setSelectedImage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    fetchProduct();
  }, [id]);

  const fetchProduct = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/products/${id}`);
      setProduct(response.data);
      if (response.data.variants && response.data.variants.length > 0) {
        setSelectedVariant(response.data.variants[0]);
      }
    } catch (error) {
      console.error('Error fetching product:', error);
      toast({
        title: 'Erreur',
        description: 'Impossible de charger le produit',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = () => {
    if (!selectedVariant) return;
    
    if (selectedVariant.stock_quantity === 0) {
      toast({
        title: 'Rupture de stock',
        description: 'Ce produit n\'est pas disponible actuellement',
        variant: 'destructive'
      });
      return;
    }

    addToCart({
      id: product.id,
      name: product.name,
      price: selectedVariant.price,
      image: product.image_urls?.[0],
      variant: {
        id: selectedVariant.id,
        name: selectedVariant.name
      },
      quantity
    });

    toast({
      title: 'Ajouté au panier',
      description: `${product.name?.[language] || product.name?.fr || 'Produit'} a été ajouté au panier`
    });
  };

  const handleToggleWishlist = async () => {
    try {
      const inWishlist = isInWishlist(product.id, selectedVariant?.id);
      
      if (inWishlist) {
        await removeFromWishlist(product.id, selectedVariant?.id);
        toast({
          title: 'Retiré de la wishlist',
          description: 'Produit retiré de votre liste de souhaits'
        });
      } else {
        await addToWishlist(product.id, selectedVariant?.id);
        toast({
          title: 'Ajouté à la wishlist',
          description: 'Produit ajouté à votre liste de souhaits'
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
            size={16}
            className={star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}
          />
        ))}
      </div>
    );
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

  if (!product) {
    return (
      <div className="min-h-screen">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-12">
          <div className="text-center">Produit non trouvé</div>
        </div>
        <Footer />
      </div>
    );
  }

  const inWishlist = isInWishlist(product.id, selectedVariant?.id);
  const isOutOfStock = selectedVariant?.stock_quantity === 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <button
          onClick={() => navigate('/shop')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft size={20} />
          Retour à la boutique
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Left: Images & Videos */}
          <div>
            <div className="bg-white rounded-lg overflow-hidden mb-4">
              <img
                src={product.image_urls?.[selectedImage] || '/placeholder.jpg'}
                alt={product.name?.[language] || product.name?.fr || product.name || 'Product'}
                className="w-full h-96 object-cover"
              />
            </div>
            
            {/* Thumbnail gallery */}
            {product.image_urls && product.image_urls.length > 1 && (
              <div className="grid grid-cols-4 gap-2 mb-6">
                {product.image_urls.map((img, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedImage(idx)}
                    className={`border-2 rounded-lg overflow-hidden ${
                      selectedImage === idx ? 'border-green-600' : 'border-gray-200'
                    }`}
                  >
                    <img src={img} alt="" className="w-full h-20 object-cover" />
                  </button>
                ))}
              </div>
            )}

            {/* Videos */}
            {product.videos && product.videos.length > 0 && (
              <ProductVideoPlayer
                videos={product.videos}
                productName={product.name[language]}
              />
            )}
          </div>

          {/* Right: Product Info */}
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold mb-3">{product.name?.[language] || product.name?.fr || product.name || 'Produit'}</h1>
              
              {product.reviews_summary && product.reviews_summary.total_reviews > 0 && (
                <div className="flex items-center gap-3 mb-4">
                  {renderStars(product.reviews_summary.average_rating)}
                  <span className="text-sm text-gray-600">
                    {product.reviews_summary.average_rating} ({product.reviews_summary.total_reviews} avis)
                  </span>
                </div>
              )}

              {/* Labels */}
              {product.labels && product.labels.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {product.labels.map((label) => (
                    <span
                      key={label}
                      className="bg-green-100 text-green-700 text-xs px-3 py-1 rounded-full font-medium"
                    >
                      {label.toUpperCase()}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Variant Selector */}
            <VariantSelector
              variants={product.variants}
              selectedVariant={selectedVariant}
              onSelectVariant={setSelectedVariant}
            />

            {/* Description */}
            <div>
              <h3 className="font-semibold mb-2">Description</h3>
              <p className="text-gray-700">{product.description?.[language] || product.description?.fr || product.description || ''}</p>
            </div>

            {/* Origin */}
            {product.origin && (
              <div>
                <h3 className="font-semibold mb-2">Origine</h3>
                <p className="text-gray-700 mb-3">
                  {product.origin.region_name?.[language] || product.origin.region_name?.fr || product.origin.region_name || ''}
                </p>
              </div>
            )}

            {/* Quantity & Actions */}
            {isOutOfStock ? (
              <StockAlert
                productId={product.id}
                variantId={selectedVariant?.id}
                productName={product.name[language]}
              />
            ) : (
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <label className="text-sm font-medium">Quantité:</label>
                  <select
                    value={quantity}
                    onChange={(e) => setQuantity(parseInt(e.target.value))}
                    className="border border-gray-300 rounded-lg px-3 py-2"
                  >
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((q) => (
                      <option key={q} value={q}>{q}</option>
                    ))}
                  </select>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={handleAddToCart}
                    className="flex-1 btn-primary flex items-center justify-center gap-2"
                  >
                    <ShoppingCart size={20} />
                    Ajouter au panier
                  </button>
                  
                  <button
                    onClick={handleToggleWishlist}
                    className={`p-3 border-2 rounded-lg transition-colors ${
                      inWishlist
                        ? 'border-red-500 bg-red-50 text-red-500'
                        : 'border-gray-300 hover:border-gray-400 text-gray-600'
                    }`}
                  >
                    <Heart size={24} fill={inWishlist ? 'currentColor' : 'none'} />
                  </button>
                  
                  <button className="p-3 border-2 border-gray-300 rounded-lg hover:border-gray-400 text-gray-600">
                    <Share2 size={24} />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Origin Map */}
        {product.origin && (
          <div className="bg-white rounded-lg p-6 mb-12">
            <h2 className="text-2xl font-bold mb-6">Origine du produit</h2>
            <InteractiveOriginMap productOrigin={product.origin} />
          </div>
        )}

        {/* Reviews */}
        <div className="bg-white rounded-lg p-6 mb-12">
          <ProductReviews productId={product.id} />
        </div>

        {/* Recommendations */}
        <div className="bg-white rounded-lg p-6">
          <ProductRecommendations productId={product.id} />
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default ProductDetailPageExtended;