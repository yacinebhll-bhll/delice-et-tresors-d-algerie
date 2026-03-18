import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Star, ThumbsUp, Camera, Check, Filter } from 'lucide-react';
import { useAuth } from '../App';
import { useToast } from '../hooks/use-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const ProductReviews = ({ productId }) => {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [filters, setFilters] = useState({
    rating: null,
    hasPhoto: false,
    verifiedOnly: false,
    sort: 'recent'
  });
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [newReview, setNewReview] = useState({
    rating: 5,
    title: '',
    comment: '',
    photos: []
  });
  const { user } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    fetchReviews();
  }, [productId, filters]);

  const fetchReviews = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.rating) params.append('rating', filters.rating);
      if (filters.hasPhoto) params.append('has_photo', 'true');
      if (filters.verifiedOnly) params.append('verified_only', 'true');
      params.append('sort', filters.sort);

      const response = await axios.get(`${API}/products/${productId}/reviews?${params}`);
      setReviews(response.data.reviews);
    } catch (error) {
      console.error('Error fetching reviews:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    if (!user) {
      toast({
        title: 'Connexion requise',
        description: 'Veuillez vous connecter pour laisser un avis',
        variant: 'destructive'
      });
      return;
    }

    try {
      await axios.post(`${API}/reviews`, {
        product_id: productId,
        ...newReview
      });
      
      toast({
        title: 'Avis ajouté',
        description: 'Merci pour votre contribution !'
      });
      
      setShowReviewForm(false);
      setNewReview({ rating: 5, title: '', comment: '', photos: [] });
      fetchReviews();
    } catch (error) {
      toast({
        title: 'Erreur',
        description: error.response?.data?.detail || 'Impossible d\'ajouter l\'avis',
        variant: 'destructive'
      });
    }
  };

  const handleMarkHelpful = async (reviewId) => {
    if (!user) {
      toast({
        title: 'Connexion requise',
        description: 'Veuillez vous connecter',
        variant: 'destructive'
      });
      return;
    }

    try {
      await axios.post(`${API}/reviews/${reviewId}/helpful`);
      fetchReviews();
    } catch (error) {
      console.error('Error marking helpful:', error);
    }
  };

  const renderStars = (rating, interactive = false, onSelect = null) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            size={interactive ? 24 : 16}
            className={`${
              star <= rating
                ? 'fill-yellow-400 text-yellow-400'
                : 'text-gray-300'
            } ${interactive ? 'cursor-pointer hover:scale-110 transition-transform' : ''}`}
            onClick={() => interactive && onSelect && onSelect(star)}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="mt-12">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Avis Clients</h2>
        {user && (
          <button
            onClick={() => setShowReviewForm(!showReviewForm)}
            className="btn-primary"
          >
            Laisser un avis
          </button>
        )}
      </div>

      {/* Review Form */}
      {showReviewForm && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
          <h3 className="text-xl font-semibold mb-4">Votre avis</h3>
          <form onSubmit={handleSubmitReview}>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Note</label>
              {renderStars(newReview.rating, true, (rating) => 
                setNewReview({ ...newReview, rating })
              )}
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Titre</label>
              <input
                type="text"
                value={newReview.title}
                onChange={(e) => setNewReview({ ...newReview, title: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                required
              />
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Commentaire</label>
              <textarea
                value={newReview.comment}
                onChange={(e) => setNewReview({ ...newReview, comment: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-4 py-2 h-32"
                required
              />
            </div>
            
            <div className="flex gap-3">
              <button type="submit" className="btn-primary">
                Publier l'avis
              </button>
              <button
                type="button"
                onClick={() => setShowReviewForm(false)}
                className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Annuler
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <select
          value={filters.sort}
          onChange={(e) => setFilters({ ...filters, sort: e.target.value })}
          className="border border-gray-300 rounded-lg px-4 py-2"
        >
          <option value="recent">Plus récents</option>
          <option value="helpful">Plus utiles</option>
          <option value="rating_high">Note: élevée</option>
          <option value="rating_low">Note: faible</option>
        </select>
        
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={filters.hasPhoto}
            onChange={(e) => setFilters({ ...filters, hasPhoto: e.target.checked })}
            className="w-4 h-4"
          />
          <Camera size={16} />
          <span>Avec photos</span>
        </label>
        
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={filters.verifiedOnly}
            onChange={(e) => setFilters({ ...filters, verifiedOnly: e.target.checked })}
            className="w-4 h-4"
          />
          <Check size={16} />
          <span>Achats vérifiés</span>
        </label>
      </div>

      {/* Reviews List */}
      <div className="space-y-6">
        {loading ? (
          <div className="text-center py-12">Chargement...</div>
        ) : reviews.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            Aucun avis pour le moment. Soyez le premier à donner votre avis !
          </div>
        ) : (
          reviews.map((review) => (
            <div key={review.id} className="border-b border-gray-200 pb-6">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-semibold">{review.user_name}</span>
                    {review.verified_purchase && (
                      <span className="flex items-center gap-1 text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                        <Check size={12} />
                        Achat vérifié
                      </span>
                    )}
                  </div>
                  {renderStars(review.rating)}
                </div>
                <span className="text-sm text-gray-500">
                  {new Date(review.created_at).toLocaleDateString('fr-FR')}
                </span>
              </div>
              
              <h4 className="font-semibold mb-2">{review.title}</h4>
              <p className="text-gray-700 mb-3">{review.comment}</p>
              
              {review.photos && review.photos.length > 0 && (
                <div className="flex gap-2 mb-3">
                  {review.photos.map((photo, idx) => (
                    <img
                      key={idx}
                      src={photo}
                      alt="Review"
                      className="w-20 h-20 object-cover rounded-lg"
                    />
                  ))}
                </div>
              )}
              
              <button
                onClick={() => handleMarkHelpful(review.id)}
                className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
              >
                <ThumbsUp size={16} />
                Utile ({review.helpful_count})
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ProductReviews;