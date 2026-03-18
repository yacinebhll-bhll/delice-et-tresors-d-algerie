import React, { useState, useEffect } from 'react';
import { Slider } from './ui/slider';
import { Checkbox } from './ui/checkbox';
import { Label } from './ui/label';
import { X, Filter, Star } from 'lucide-react';
import { useFilters } from '../contexts/FiltersContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const AdvancedFilters = ({ onApply }) => {
  const { filters, updateFilter, updateFilters, clearFilters, toggleLabel, getActiveFiltersCount } = useFilters();
  const [categories, setCategories] = useState([]);
  const [regions, setRegions] = useState([]);
  const [expanded, setExpanded] = useState({
    price: true,
    origin: false,
    labels: false,
    rating: false
  });

  useEffect(() => {
    fetchCategories();
    fetchRegions();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchRegions = async () => {
    try {
      const response = await axios.get(`${API}/regions`);
      setRegions(response.data);
    } catch (error) {
      console.error('Error fetching regions:', error);
    }
  };

  const availableLabels = [
    { id: 'bio', label: 'Bio' },
    { id: 'aoc', label: 'AOC' },
    { id: 'artisanal', label: 'Artisanal' },
    { id: 'commerce-equitable', label: 'Commerce équitable' },
    { id: 'vegan', label: 'Vegan' },
    { id: 'sans-gluten', label: 'Sans gluten' }
  ];

  const handlePriceChange = (values) => {
    updateFilters({
      priceMin: values[0],
      priceMax: values[1]
    });
  };

  const toggleSection = (section) => {
    setExpanded(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const activeCount = getActiveFiltersCount();

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 sticky top-20">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Filter size={20} />
          <h3 className="text-lg font-bold">Filtres</h3>
          {activeCount > 0 && (
            <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full font-semibold">
              {activeCount}
            </span>
          )}
        </div>
        {activeCount > 0 && (
          <button
            onClick={clearFilters}
            className="text-sm text-red-600 hover:text-red-700 font-medium"
          >
            Réinitialiser
          </button>
        )}
      </div>

      <div className="space-y-6">
        {/* Category Filter */}
        <div>
          <label className="block text-sm font-semibold mb-3">Catégorie</label>
          <select
            value={filters.category || ''}
            onChange={(e) => updateFilter('category', e.target.value || null)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Toutes les catégories</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.slug}>
                {cat.name.fr}
              </option>
            ))}
          </select>
        </div>

        {/* Price Range Filter */}
        <div>
          <button
            onClick={() => toggleSection('price')}
            className="w-full flex items-center justify-between text-sm font-semibold mb-3"
          >
            <span>Prix</span>
            <span className={`transform transition-transform ${
              expanded.price ? 'rotate-180' : ''
            }`}>▼</span>
          </button>
          
          {expanded.price && (
            <div className="space-y-3">
              <Slider
                defaultValue={[filters.priceMin || 0, filters.priceMax || 100]}
                max={100}
                step={1}
                onValueChange={handlePriceChange}
                className="w-full"
              />
              <div className="flex items-center justify-between text-sm text-gray-600">
                <span>{filters.priceMin || 0} €</span>
                <span>{filters.priceMax || 100} €</span>
              </div>
            </div>
          )}
        </div>

        {/* Origin/Region Filter */}
        <div>
          <button
            onClick={() => toggleSection('origin')}
            className="w-full flex items-center justify-between text-sm font-semibold mb-3"
          >
            <span>Origine</span>
            <span className={`transform transition-transform ${
              expanded.origin ? 'rotate-180' : ''
            }`}>▼</span>
          </button>
          
          {expanded.origin && (
            <div className="space-y-2">
              {regions.map((region) => (
                <label key={region.id} className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded">
                  <input
                    type="radio"
                    name="origin"
                    checked={filters.origin === region.id}
                    onChange={() => updateFilter('origin', region.id)}
                    className="w-4 h-4 text-green-600"
                  />
                  <span className="text-sm">{region.name.fr}</span>
                </label>
              ))}
              {filters.origin && (
                <button
                  onClick={() => updateFilter('origin', null)}
                  className="text-sm text-gray-600 hover:text-gray-800 flex items-center gap-1"
                >
                  <X size={14} />
                  Effacer
                </button>
              )}
            </div>
          )}
        </div>

        {/* Labels Filter */}
        <div>
          <button
            onClick={() => toggleSection('labels')}
            className="w-full flex items-center justify-between text-sm font-semibold mb-3"
          >
            <span>Labels & Certifications</span>
            <span className={`transform transition-transform ${
              expanded.labels ? 'rotate-180' : ''
            }`}>▼</span>
          </button>
          
          {expanded.labels && (
            <div className="space-y-2">
              {availableLabels.map((label) => (
                <label key={label.id} className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded">
                  <Checkbox
                    checked={filters.labels.includes(label.id)}
                    onCheckedChange={() => toggleLabel(label.id)}
                  />
                  <span className="text-sm">{label.label}</span>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Rating Filter */}
        <div>
          <button
            onClick={() => toggleSection('rating')}
            className="w-full flex items-center justify-between text-sm font-semibold mb-3"
          >
            <span>Note minimum</span>
            <span className={`transform transition-transform ${
              expanded.rating ? 'rotate-180' : ''
            }`}>▼</span>
          </button>
          
          {expanded.rating && (
            <div className="space-y-2">
              {[4, 3, 2].map((rating) => (
                <label key={rating} className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded">
                  <input
                    type="radio"
                    name="rating"
                    checked={filters.ratingMin === rating}
                    onChange={() => updateFilter('ratingMin', rating)}
                    className="w-4 h-4 text-green-600"
                  />
                  <div className="flex items-center gap-1">
                    {Array.from({ length: rating }).map((_, i) => (
                      <Star key={i} size={14} className="fill-yellow-400 text-yellow-400" />
                    ))}
                    <span className="text-sm ml-1">& plus</span>
                  </div>
                </label>
              ))}
              {filters.ratingMin && (
                <button
                  onClick={() => updateFilter('ratingMin', null)}
                  className="text-sm text-gray-600 hover:text-gray-800 flex items-center gap-1"
                >
                  <X size={14} />
                  Effacer
                </button>
              )}
            </div>
          )}
        </div>

        {/* Stock Filter */}
        <div>
          <label className="flex items-center gap-2 cursor-pointer">
            <Checkbox
              checked={filters.inStock === true}
              onCheckedChange={(checked) => updateFilter('inStock', checked ? true : null)}
            />
            <span className="text-sm font-medium">En stock uniquement</span>
          </label>
        </div>

        {/* Sort */}
        <div>
          <label className="block text-sm font-semibold mb-3">Trier par</label>
          <select
            value={filters.sort}
            onChange={(e) => updateFilter('sort', e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="recent">Plus récents</option>
            <option value="price_low">Prix croissant</option>
            <option value="price_high">Prix décroissant</option>
            <option value="rating">Meilleures notes</option>
            <option value="popular">Plus populaires</option>
          </select>
        </div>
      </div>

      <button
        onClick={() => onApply && onApply(filters)}
        className="w-full btn-primary mt-6"
      >
        Appliquer les filtres
      </button>
    </div>
  );
};

export default AdvancedFilters;