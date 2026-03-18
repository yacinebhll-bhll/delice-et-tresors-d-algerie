import React, { useState } from 'react';
import axios from 'axios';
import { Bell, Check } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const StockAlert = ({ productId, variantId, productName }) => {
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubscribe = async (e) => {
    e.preventDefault();
    
    if (!email) {
      toast({
        title: 'Email requis',
        description: 'Veuillez entrer votre adresse email',
        variant: 'destructive'
      });
      return;
    }

    try {
      setLoading(true);
      await axios.post(`${API}/stock-alerts`, {
        email,
        product_id: productId,
        variant_id: variantId
      });
      
      setSubscribed(true);
      toast({
        title: 'Alerte activée',
        description: 'Vous serez notifié par email dès que le produit sera disponible'
      });
    } catch (error) {
      toast({
        title: 'Erreur',
        description: error.response?.data?.detail || 'Impossible de créer l\'alerte',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  if (subscribed) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center gap-3 text-green-700">
          <Check size={24} />
          <div>
            <p className="font-semibold">Alerte activée</p>
            <p className="text-sm">Nous vous préviendrons dès que {productName} sera de nouveau en stock</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
      <div className="flex items-start gap-3 mb-4">
        <Bell className="text-orange-600 mt-1" size={24} />
        <div>
          <h3 className="font-semibold text-gray-900 mb-1">Produit en rupture de stock</h3>
          <p className="text-sm text-gray-600">
            Recevez un email dès que ce produit sera de nouveau disponible
          </p>
        </div>
      </div>
      
      <form onSubmit={handleSubscribe} className="flex gap-2">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Votre adresse email"
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="btn-primary whitespace-nowrap disabled:opacity-50"
        >
          {loading ? 'Envoi...' : 'Me prévenir'}
        </button>
      </form>
    </div>
  );
};

export default StockAlert;