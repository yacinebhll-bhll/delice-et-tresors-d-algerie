import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Truck, Package } from 'lucide-react';
import { useCart } from '../contexts/CartContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const ShippingCalculator = ({ items, onShippingCalculated }) => {
  const [shippingOptions, setShippingOptions] = useState(null);
  const [selectedOption, setSelectedOption] = useState('standard');
  const [loading, setLoading] = useState(true);
  const [destination, setDestination] = useState({
    country: 'FR',
    zone: null
  });

  useEffect(() => {
    if (items && items.length > 0) {
      calculateShipping();
    }
  }, [items, destination]);

  const calculateShipping = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/shipping/calculate`, {
        items: items.map(item => ({
          product_id: item.id,
          variant_id: item.variant?.id,
          quantity: item.quantity || 1
        })),
        destination_country: destination.country,
        destination_zone: destination.zone
      });
      
      setShippingOptions(response.data);
      
      if (onShippingCalculated) {
        onShippingCalculated({
          option: selectedOption,
          cost: response.data[selectedOption].price
        });
      }
    } catch (error) {
      console.error('Error calculating shipping:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOptionSelect = (option) => {
    setSelectedOption(option);
    if (onShippingCalculated && shippingOptions) {
      onShippingCalculated({
        option,
        cost: shippingOptions[option].price
      });
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  if (!shippingOptions) {
    return null;
  }

  const progressPercentage = Math.min(
    (shippingOptions.current_total / shippingOptions.free_threshold) * 100,
    100
  );

  return (
    <div className="space-y-4">
      {/* Free Shipping Progress */}
      {shippingOptions.amount_to_free_shipping > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-900">
              Livraison gratuite dès {shippingOptions.free_threshold} €
            </span>
            <span className="text-sm font-bold text-blue-900">
              Plus que {shippingOptions.amount_to_free_shipping.toFixed(2)} €
            </span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
        </div>
      )}

      {shippingOptions.amount_to_free_shipping === 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
          <Package className="text-green-600" size={24} />
          <span className="text-green-900 font-medium">
            🎉 Félicitations ! Vous bénéficiez de la livraison gratuite
          </span>
        </div>
      )}

      {/* Shipping Options */}
      <div className="space-y-3">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Truck size={20} />
          Mode de livraison
        </h3>

        {/* Standard Shipping */}
        <label
          className={`border-2 rounded-lg p-4 cursor-pointer transition-all block ${
            selectedOption === 'standard'
              ? 'border-green-600 bg-green-50'
              : 'border-gray-200 hover:border-gray-300 bg-white'
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <input
                type="radio"
                name="shipping"
                value="standard"
                checked={selectedOption === 'standard'}
                onChange={() => handleOptionSelect('standard')}
                className="w-4 h-4 text-green-600"
              />
              <div>
                <p className="font-semibold">{shippingOptions.standard.name}</p>
                <p className="text-sm text-gray-600">
                  Livraison en {shippingOptions.standard.delivery_days} jours
                </p>
              </div>
            </div>
            <div className="text-right">
              {shippingOptions.standard.price === 0 ? (
                <p className="font-bold text-green-600">GRATUIT</p>
              ) : (
                <p className="font-bold">{shippingOptions.standard.price.toFixed(2)} €</p>
              )}
            </div>
          </div>
        </label>

        {/* Express Shipping */}
        <label
          className={`border-2 rounded-lg p-4 cursor-pointer transition-all block ${
            selectedOption === 'express'
              ? 'border-green-600 bg-green-50'
              : 'border-gray-200 hover:border-gray-300 bg-white'
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <input
                type="radio"
                name="shipping"
                value="express"
                checked={selectedOption === 'express'}
                onChange={() => handleOptionSelect('express')}
                className="w-4 h-4 text-green-600"
              />
              <div>
                <div className="flex items-center gap-2">
                  <p className="font-semibold">{shippingOptions.express.name}</p>
                  <span className="bg-orange-100 text-orange-700 text-xs px-2 py-1 rounded-full">
                    Rapide
                  </span>
                </div>
                <p className="text-sm text-gray-600">
                  Livraison en {shippingOptions.express.delivery_days} jours
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-bold">{shippingOptions.express.price.toFixed(2)} €</p>
            </div>
          </div>
        </label>
      </div>
    </div>
  );
};

export default ShippingCalculator;