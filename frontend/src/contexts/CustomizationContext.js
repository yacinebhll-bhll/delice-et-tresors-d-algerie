import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CustomizationContext = createContext();

export const useCustomization = () => {
  const context = useContext(CustomizationContext);
  if (!context) {
    throw new Error('useCustomization must be used within a CustomizationProvider');
  }
  return context;
};

export const CustomizationProvider = ({ children }) => {
  const [customization, setCustomization] = useState({
    site_name: "Délices et Trésors d'Algérie",
    site_slogan: {
      fr: "Découvrez nos trésors : dattes Deglet Nour et huile d'olive kabyle authentique",
      en: "Discover our treasures: Deglet Nour dates and authentic Kabyle olive oil",
      ar: "اكتشف كنوزنا: تمور دقلة نور وزيت الزيتون القبائلي الأصيل"
    },
    logo_url: null,
    primary_color: '#6B8E23',
    secondary_color: '#8B7355',
    accent_color: '#F59E0B',
    font_heading: 'Inter',
    font_body: 'Inter'
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCustomization();
  }, []);

  const fetchCustomization = async () => {
    try {
      const response = await axios.get(`${API}/customization`);
      if (response.data) {
        setCustomization(prev => ({ ...prev, ...response.data }));
        applyStyles(response.data);
      }
    } catch (error) {
      console.error('Error fetching customization:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyStyles = (settings) => {
    const root = document.documentElement;
    if (!root) return;
    
    // Apply colors as CSS variables
    if (settings.primary_color) {
      root.style.setProperty('--color-primary', settings.primary_color);
      root.style.setProperty('--color-primary-rgb', hexToRgb(settings.primary_color));
    }
    if (settings.secondary_color) {
      root.style.setProperty('--color-secondary', settings.secondary_color);
      root.style.setProperty('--color-secondary-rgb', hexToRgb(settings.secondary_color));
    }
    if (settings.accent_color) {
      root.style.setProperty('--color-accent', settings.accent_color);
      root.style.setProperty('--color-accent-rgb', hexToRgb(settings.accent_color));
    }
    
    // Apply fonts
    if (settings.font_heading) {
      root.style.setProperty('--font-heading', settings.font_heading);
      loadGoogleFont(settings.font_heading);
    }
    if (settings.font_body) {
      root.style.setProperty('--font-body', settings.font_body);
      loadGoogleFont(settings.font_body);
    }
    
    // Apply favicon if set (with defensive check)
    if (settings.favicon_url) {
      try {
        updateFavicon(settings.favicon_url);
      } catch (e) {
        console.warn('Failed to update favicon:', e);
      }
    }
  };

  const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result
      ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}`
      : '0, 0, 0';
  };

  const loadGoogleFont = (fontName) => {
    if (!fontName || typeof document === 'undefined') return;
    
    try {
      const existingLink = document.querySelector(`link[href*="${fontName.replace(' ', '+')}"]`);
      if (existingLink) return;

      const link = document.createElement('link');
      link.href = `https://fonts.googleapis.com/css2?family=${fontName.replace(' ', '+')}:wght@300;400;500;600;700&display=swap`;
      link.rel = 'stylesheet';
      if (document.head) {
        document.head.appendChild(link);
      }
    } catch (e) {
      console.warn('Failed to load Google Font:', e);
    }
  };

  const updateFavicon = (url) => {
    if (!url || typeof document === 'undefined') return;
    
    try {
      let link = document.querySelector("link[rel*='icon']");
      if (!link) {
        link = document.createElement('link');
        link.rel = 'icon';
        if (document.head) {
          document.head.appendChild(link);
        }
      }
      if (link) {
        link.href = url;
      }
    } catch (e) {
      console.warn('Failed to update favicon:', e);
    }
  };

  const refreshCustomization = async () => {
    await fetchCustomization();
  };

  return (
    <CustomizationContext.Provider value={{ 
      customization, 
      loading, 
      refreshCustomization,
      applyStyles 
    }}>
      {children}
    </CustomizationContext.Provider>
  );
};

export default CustomizationContext;
