import React, { createContext, useContext, useState } from 'react';

const FiltersContext = createContext();

export const useFilters = () => {
  const context = useContext(FiltersContext);
  if (!context) {
    throw new Error('useFilters must be used within FiltersProvider');
  }
  return context;
};

export const FiltersProvider = ({ children }) => {
  const [filters, setFilters] = useState({
    category: null,
    priceMin: null,
    priceMax: null,
    origin: null,
    labels: [],
    inStock: null,
    ratingMin: null,
    sort: 'recent',
    search: ''
  });

  const updateFilter = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const updateFilters = (newFilters) => {
    setFilters(prev => ({
      ...prev,
      ...newFilters
    }));
  };

  const clearFilters = () => {
    setFilters({
      category: null,
      priceMin: null,
      priceMax: null,
      origin: null,
      labels: [],
      inStock: null,
      ratingMin: null,
      sort: 'recent',
      search: ''
    });
  };

  const toggleLabel = (label) => {
    setFilters(prev => {
      const labels = prev.labels.includes(label)
        ? prev.labels.filter(l => l !== label)
        : [...prev.labels, label];
      return { ...prev, labels };
    });
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.category) count++;
    if (filters.priceMin !== null || filters.priceMax !== null) count++;
    if (filters.origin) count++;
    if (filters.labels.length > 0) count++;
    if (filters.inStock !== null) count++;
    if (filters.ratingMin !== null) count++;
    return count;
  };

  const value = {
    filters,
    updateFilter,
    updateFilters,
    clearFilters,
    toggleLabel,
    getActiveFiltersCount
  };

  return (
    <FiltersContext.Provider value={value}>
      {children}
    </FiltersContext.Provider>
  );
};