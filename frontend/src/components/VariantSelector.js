import React, { useState, useEffect } from 'react';
import { ChevronDown, Package, TrendingUp } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const VariantSelector = ({ variants, selectedVariant, onSelectVariant, showStock = true }) => {
  const [selected, setSelected] = useState(selectedVariant || variants[0]);
  const { toast } = useToast();

  useEffect(() => {
    if (selectedVariant) {
      setSelected(selectedVariant);
    }
  }, [selectedVariant]);

  const handleSelect = (variant) => {
    setSelected(variant);
    if (onSelectVariant) {
      onSelectVariant(variant);
    }
  };

  const calculateSavings = (variant) => {
    if (!variant.compare_at_price || variant.compare_at_price <= variant.price) {
      return null;
    }
    const savings = variant.compare_at_price - variant.price;
    const percentage = ((savings / variant.compare_at_price) * 100).toFixed(0);
    return { amount: savings, percentage };
  };

  const getStockStatus = (variant) => {
    if (variant.stock_quantity === 0) {
      return { text: 'Rupture de stock', color: 'text-red-600', bg: 'bg-red-50', available: false };
    } else if (variant.stock_quantity <= variant.low_stock_threshold) {
      return { text: `Stock faible - ${variant.stock_quantity} restant(s)`, color: 'text-orange-600', bg: 'bg-orange-50', available: true };
    } else {
      return { text: 'En stock', color: 'text-green-600', bg: 'bg-green-50', available: true };
    }
  };

  if (!variants || variants.length === 0) {
    return null;
  }

  if (variants.length === 1) {
    const variant = variants[0];
    const savings = calculateSavings(variant);
    const stockStatus = getStockStatus(variant);

    return (
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-3xl font-bold text-green-700">{variant.price.toFixed(2)} €</p>
            {savings && (
              <p className="text-sm text-gray-500 line-through">
                {variant.compare_at_price.toFixed(2)} €
              </p>
            )}
          </div>
          {savings && (
            <div className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm font-semibold">
              -{savings.percentage}%
            </div>
          )}
        </div>
        
        {showStock && (
          <div className={`${stockStatus.bg} ${stockStatus.color} px-4 py-2 rounded-lg flex items-center gap-2`}>
            <Package size={16} />
            <span className="font-medium">{stockStatus.text}</span>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Choisissez votre format
        </label>
        
        <div className="space-y-2">
          {variants.map((variant) => {
            const savings = calculateSavings(variant);
            const stockStatus = getStockStatus(variant);
            const isSelected = selected?.id === variant.id;

            return (
              <button
                key={variant.id}
                onClick={() => stockStatus.available && handleSelect(variant)}
                disabled={!stockStatus.available}
                className={`w-full text-left border-2 rounded-lg p-4 transition-all ${
                  isSelected
                    ? 'border-green-600 bg-green-50'
                    : stockStatus.available
                    ? 'border-gray-200 hover:border-gray-300 bg-white'
                    : 'border-gray-100 bg-gray-50 opacity-60 cursor-not-allowed'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold text-lg">{variant.name}</h4>
                      {isSelected && (
                        <span className="bg-green-600 text-white text-xs px-2 py-1 rounded-full">
                          Sélectionné
                        </span>
                      )}
                    </div>
                    {variant.sku && (
                      <p className="text-xs text-gray-500">SKU: {variant.sku}</p>
                    )}
                  </div>
                  
                  <div className="text-right">
                    <p className="text-2xl font-bold text-green-700">
                      {variant.price.toFixed(2)} €
                    </p>
                    {savings && (
                      <div className="flex items-center gap-2 justify-end">
                        <p className="text-sm text-gray-500 line-through">
                          {variant.compare_at_price.toFixed(2)} €
                        </p>
                        <span className="bg-red-100 text-red-700 text-xs px-2 py-1 rounded-full font-semibold">
                          -{savings.percentage}%
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                
                {savings && (
                  <div className="flex items-center gap-1 text-sm text-green-700 mb-2">
                    <TrendingUp size={14} />
                    <span>Économisez {savings.amount.toFixed(2)} €</span>
                  </div>
                )}
                
                {showStock && (
                  <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${
                    stockStatus.bg
                  } ${stockStatus.color}`}>
                    <Package size={12} />
                    {stockStatus.text}
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {selected && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-900">
            <span className="font-semibold">Sélection actuelle:</span> {selected.name} - {selected.price.toFixed(2)} €
          </p>
        </div>
      )}
    </div>
  );
};

export default VariantSelector;