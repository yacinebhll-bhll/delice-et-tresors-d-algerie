import React, { useState, useEffect } from 'react';
import { Star, Quote } from 'lucide-react';
import { useLanguage } from '../App';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

export default function TestimonialsSection() {
  const { language } = useLanguage();
  const [testimonials, setTestimonials] = useState([]);
  const [loading, setLoading] = useState(true);

  const translations = {
    fr: {
      title: 'Ce que disent nos clients',
      subtitle: 'Découvrez les avis de ceux qui ont déjà goûté à nos produits',
      noTestimonials: 'Aucun témoignage pour le moment'
    },
    en: {
      title: 'What Our Customers Say',
      subtitle: 'Discover reviews from those who have already tasted our products',
      noTestimonials: 'No testimonials yet'
    },
    ar: {
      title: 'ماذا يقول عملاؤنا',
      subtitle: 'اكتشف آراء الذين جربوا منتجاتنا بالفعل',
      noTestimonials: 'لا توجد شهادات حتى الآن'
    }
  };

  const t = translations[language] || translations.fr;

  useEffect(() => {
    fetchTestimonials();
  }, []);

  const fetchTestimonials = async () => {
    try {
      const response = await axios.get(`${API}/testimonials?limit=6`);
      setTestimonials(response.data);
    } catch (error) {
      console.error('Error fetching testimonials:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderStars = (rating) => {
    return (
      <div className="flex items-center space-x-1">
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

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    
    switch (language) {
      case 'ar':
        return date.toLocaleDateString('ar-DZ', options);
      case 'en':
        return date.toLocaleDateString('en-US', options);
      default:
        return date.toLocaleDateString('fr-FR', options);
    }
  };

  if (loading) {
    return (
      <div className="py-16 bg-gradient-to-br from-amber-50 to-orange-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#6B8E23]"></div>
          </div>
        </div>
      </div>
    );
  }

  if (testimonials.length === 0) {
    return null; // Don't show section if no testimonials
  }

  return (
    <div className="py-16 bg-gradient-to-br from-amber-50 to-orange-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">{t.title}</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">{t.subtitle}</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {testimonials.map((testimonial) => (
            <div
              key={testimonial.id}
              className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow relative"
            >
              <Quote className="absolute top-4 right-4 text-[#6B8E23] opacity-20" size={40} />
              
              <div className="mb-4">
                {renderStars(testimonial.rating)}
              </div>

              <p className="text-gray-700 mb-6 italic leading-relaxed">
                "{testimonial.content?.[language] || testimonial.content?.fr || testimonial.comment || ''}"
              </p>

              <div className="border-t pt-4">
                <p className="font-semibold text-gray-900">{testimonial.user_name || testimonial.customer_name || 'Client'}</p>
                <p className="text-sm text-gray-500">{formatDate(testimonial.approved_at || testimonial.created_at)}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
