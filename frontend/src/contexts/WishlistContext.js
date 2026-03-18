import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../App';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const WishlistContext = createContext();

export const useWishlist = () => {
  const context = useContext(WishlistContext);
  if (!context) {
    throw new Error('useWishlist must be used within WishlistProvider');
  }
  return context;
};

export const WishlistProvider = ({ children }) => {
  const [wishlistItems, setWishlistItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchWishlist();
    } else {
      setWishlistItems([]);
    }
  }, [user]);

  const fetchWishlist = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/wishlist`);
      setWishlistItems(response.data.items || []);
    } catch (error) {
      console.error('Error fetching wishlist:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToWishlist = async (productId, variantId = null) => {
    if (!user) {
      throw new Error('Please login to add to wishlist');
    }

    try {
      await axios.post(`${API}/wishlist`, {
        product_id: productId,
        variant_id: variantId
      });
      await fetchWishlist();
      return true;
    } catch (error) {
      console.error('Error adding to wishlist:', error);
      throw error;
    }
  };

  const removeFromWishlist = async (productId, variantId = null) => {
    try {
      const params = variantId ? `?variant_id=${variantId}` : '';
      await axios.delete(`${API}/wishlist/${productId}${params}`);
      await fetchWishlist();
      return true;
    } catch (error) {
      console.error('Error removing from wishlist:', error);
      throw error;
    }
  };

  const isInWishlist = (productId, variantId = null) => {
    return wishlistItems.some(
      item => 
        item.product_id === productId && 
        (variantId ? item.variant_id === variantId : true)
    );
  };

  const getWishlistCount = () => wishlistItems.length;

  const value = {
    wishlistItems,
    loading,
    addToWishlist,
    removeFromWishlist,
    isInWishlist,
    getWishlistCount,
    refreshWishlist: fetchWishlist
  };

  return (
    <WishlistContext.Provider value={value}>
      {children}
    </WishlistContext.Provider>
  );
};