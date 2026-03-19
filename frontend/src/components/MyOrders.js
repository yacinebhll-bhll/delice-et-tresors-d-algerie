import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Package, Eye, Clock, Truck, CheckCircle, XCircle, ChevronRight, MapPin, Star, ArrowLeft } from 'lucide-react';
import { useAuth, useLanguage } from '../App';
import { useNavigate } from 'react-router-dom';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const ORDER_STEPS = [
  { key: 'pending', icon: Clock, label: { fr: 'En attente', en: 'Pending', ar: 'قيد الانتظار' } },
  { key: 'confirmed', icon: CheckCircle, label: { fr: 'Confirmée', en: 'Confirmed', ar: 'تم التأكيد' } },
  { key: 'processing', icon: Package, label: { fr: 'Préparation', en: 'Processing', ar: 'قيد المعالجة' } },
  { key: 'shipped', icon: Truck, label: { fr: 'Expédiée', en: 'Shipped', ar: 'تم الشحن' } },
  { key: 'delivered', icon: CheckCircle, label: { fr: 'Livrée', en: 'Delivered', ar: 'تم التسليم' } },
];

function OrderTimeline({ status, language }) {
  const currentIdx = ORDER_STEPS.findIndex(s => s.key === status);
  const isCancelled = status === 'cancelled';

  if (isCancelled) {
    return (
      <div className="flex items-center gap-3 p-4 bg-red-50 rounded-xl border border-red-200">
        <XCircle className="text-red-500 flex-shrink-0" size={28} />
        <div>
          <p className="font-semibold text-red-700">
            {language === 'ar' ? 'تم إلغاء الطلب' : language === 'en' ? 'Order Cancelled' : 'Commande annulée'}
          </p>
          <p className="text-sm text-red-600">
            {language === 'ar' ? 'تم إلغاء هذا الطلب' : language === 'en' ? 'This order has been cancelled' : 'Cette commande a été annulée'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="py-2" data-testid="order-timeline">
      <div className="flex items-center justify-between relative">
        {/* Progress bar */}
        <div className="absolute top-5 left-5 right-5 h-1 bg-gray-200 rounded-full -z-0">
          <div
            className="h-full bg-green-500 rounded-full transition-all duration-500"
            style={{ width: `${Math.max(0, (currentIdx / (ORDER_STEPS.length - 1)) * 100)}%` }}
          />
        </div>

        {ORDER_STEPS.map((step, idx) => {
          const StepIcon = step.icon;
          const isCompleted = idx <= currentIdx;
          const isCurrent = idx === currentIdx;

          return (
            <div key={step.key} className="flex flex-col items-center relative z-10">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all ${
                  isCompleted
                    ? 'bg-green-500 border-green-500 text-white'
                    : 'bg-white border-gray-300 text-gray-400'
                } ${isCurrent ? 'ring-4 ring-green-100 scale-110' : ''}`}
              >
                <StepIcon size={18} />
              </div>
              <span className={`mt-2 text-xs font-medium text-center max-w-[70px] ${
                isCompleted ? 'text-green-700' : 'text-gray-400'
              }`}>
                {step.label[language] || step.label.fr}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function MyOrders() {
  const { user } = useAuth();
  const { language } = useLanguage();
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState(null);

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }
    fetchOrders();
  }, [user]);

  const fetchOrders = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/my-orders`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setOrders(response.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-700',
      confirmed: 'bg-blue-100 text-blue-700',
      processing: 'bg-purple-100 text-purple-700',
      shipped: 'bg-teal-100 text-teal-700',
      delivered: 'bg-green-100 text-green-700',
      cancelled: 'bg-red-100 text-red-700',
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  const getStatusLabel = (status) => {
    const labels = {
      fr: { pending: 'En attente', confirmed: 'Confirmée', processing: 'En préparation', shipped: 'Expédiée', delivered: 'Livrée', cancelled: 'Annulée' },
      en: { pending: 'Pending', confirmed: 'Confirmed', processing: 'Processing', shipped: 'Shipped', delivered: 'Delivered', cancelled: 'Cancelled' },
      ar: { pending: 'قيد الانتظار', confirmed: 'تم التأكيد', processing: 'قيد المعالجة', shipped: 'تم الشحن', delivered: 'تم التسليم', cancelled: 'ملغى' }
    };
    return labels[language]?.[status] || status;
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString(
      language === 'ar' ? 'ar-DZ' : language === 'en' ? 'en-US' : 'fr-FR',
      { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' }
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#6B8E23]"></div>
      </div>
    );
  }

  // Detail view
  if (selectedOrder) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-3xl mx-auto px-4">
          <button
            onClick={() => setSelectedOrder(null)}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6 transition"
            data-testid="back-to-orders"
          >
            <ArrowLeft size={18} />
            <span className="font-medium">
              {language === 'en' ? 'Back to Orders' : language === 'ar' ? 'العودة للطلبات' : 'Retour aux commandes'}
            </span>
          </button>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            {/* Header */}
            <div className="px-6 py-5 bg-gradient-to-r from-[#6B8E23]/10 to-[#8B7355]/10 border-b">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900" data-testid="order-number">
                    #{selectedOrder.order_number}
                  </h2>
                  <p className="text-sm text-gray-500 mt-1">{formatDate(selectedOrder.created_at)}</p>
                </div>
                <span className={`px-4 py-1.5 rounded-full text-sm font-semibold ${getStatusColor(selectedOrder.status)}`}>
                  {getStatusLabel(selectedOrder.status)}
                </span>
              </div>
            </div>

            {/* Timeline */}
            <div className="px-6 py-6 border-b">
              <h3 className="font-semibold text-gray-700 mb-4">
                {language === 'en' ? 'Order Tracking' : language === 'ar' ? 'تتبع الطلب' : 'Suivi de commande'}
              </h3>
              <OrderTimeline status={selectedOrder.status} language={language} />
            </div>

            {/* Products */}
            <div className="px-6 py-5 border-b">
              <h3 className="font-semibold text-gray-700 mb-4">
                {language === 'en' ? 'Products' : language === 'ar' ? 'المنتجات' : 'Articles'}
              </h3>
              <div className="space-y-3">
                {selectedOrder.items.map((item, idx) => (
                  <div key={idx} className="flex items-center gap-4 p-3 bg-gray-50 rounded-xl">
                    {item.image_url && (
                      <img src={item.image_url} alt="" className="w-16 h-16 object-cover rounded-lg" />
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">
                        {typeof item.product_name === 'object'
                          ? (item.product_name[language] || item.product_name.fr || 'Produit')
                          : item.product_name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {language === 'ar' ? 'الكمية' : language === 'en' ? 'Qty' : 'Qté'}: {item.quantity} x {item.price.toFixed(2)} EUR
                      </p>
                    </div>
                    <p className="font-bold text-gray-900">{(item.price * item.quantity).toFixed(2)} EUR</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Delivery Info */}
            <div className="px-6 py-5 border-b">
              <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <MapPin size={16} />
                {language === 'en' ? 'Delivery Address' : language === 'ar' ? 'عنوان التسليم' : 'Adresse de livraison'}
              </h3>
              <div className="text-gray-600 bg-gray-50 p-3 rounded-xl">
                <p className="font-medium">{selectedOrder.customer_name}</p>
                <p>{selectedOrder.shipping_address}</p>
                <p>{selectedOrder.shipping_city} {selectedOrder.shipping_postal_code}</p>
                <p className="text-sm mt-1">{selectedOrder.customer_phone}</p>
              </div>
            </div>

            {/* Total */}
            <div className="px-6 py-5">
              <div className="space-y-2">
                <div className="flex justify-between text-sm text-gray-500">
                  <span>{language === 'en' ? 'Subtotal' : language === 'ar' ? 'المجموع الفرعي' : 'Sous-total'}</span>
                  <span>{selectedOrder.subtotal?.toFixed(2) || selectedOrder.total?.toFixed(2)} EUR</span>
                </div>
                {selectedOrder.discount_amount > 0 && (
                  <div className="flex justify-between text-sm text-green-600">
                    <span>{language === 'en' ? 'Discount' : language === 'ar' ? 'الخصم' : 'Réduction'} ({selectedOrder.promo_code})</span>
                    <span>-{selectedOrder.discount_amount.toFixed(2)} EUR</span>
                  </div>
                )}
                {selectedOrder.shipping_cost > 0 && (
                  <div className="flex justify-between text-sm text-gray-500">
                    <span>{language === 'en' ? 'Shipping' : language === 'ar' ? 'الشحن' : 'Livraison'}</span>
                    <span>{selectedOrder.shipping_cost.toFixed(2)} EUR</span>
                  </div>
                )}
                <div className="flex justify-between text-lg font-bold border-t pt-2">
                  <span>{language === 'en' ? 'Total' : language === 'ar' ? 'المجموع' : 'Total'}</span>
                  <span className="text-[#6B8E23]">{selectedOrder.total.toFixed(2)} EUR</span>
                </div>
              </div>

              {/* Leave Review CTA for delivered orders */}
              {selectedOrder.status === 'delivered' && (
                <div className="mt-5 p-4 bg-amber-50 border border-amber-200 rounded-xl">
                  <div className="flex items-center gap-3">
                    <Star className="text-amber-500 flex-shrink-0" size={24} />
                    <div className="flex-1">
                      <p className="font-semibold text-amber-800">
                        {language === 'en' ? 'Rate your products!' : language === 'ar' ? 'قيم منتجاتك!' : 'Donnez votre avis !'}
                      </p>
                      <p className="text-sm text-amber-600">
                        {language === 'en' ? 'Your feedback helps other customers' : language === 'ar' ? 'ملاحظاتك تساعد الآخرين' : 'Votre avis aide les autres clients'}
                      </p>
                    </div>
                    <button
                      onClick={() => navigate(`/product/${selectedOrder.items[0]?.product_id}`)}
                      className="bg-amber-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-amber-600 transition flex-shrink-0"
                      data-testid="leave-review-btn"
                    >
                      {language === 'en' ? 'Review' : language === 'ar' ? 'تقييم' : 'Donner un avis'}
                    </button>
                  </div>
                </div>
              )}

              {selectedOrder.notes && (
                <div className="mt-4 p-3 bg-gray-50 rounded-xl">
                  <p className="text-sm font-medium text-gray-500 mb-1">Notes</p>
                  <p className="text-gray-700">{selectedOrder.notes}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // List view
  return (
    <div className="min-h-screen bg-gray-50 py-8" data-testid="my-orders-page">
      <div className="max-w-3xl mx-auto px-4">
        <h1 className="text-3xl font-bold mb-6">
          {language === 'ar' ? 'طلباتي' : language === 'en' ? 'My Orders' : 'Mes Commandes'}
        </h1>

        {orders.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-sm p-12 text-center">
            <Package className="mx-auto text-gray-300 mb-4" size={64} />
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              {language === 'ar' ? 'لا توجد طلبات' : language === 'en' ? 'No orders yet' : 'Aucune commande'}
            </h2>
            <p className="text-gray-500 mb-6">
              {language === 'en' ? 'Start shopping now!' : language === 'ar' ? 'ابدأ التسوق الآن!' : 'Commencez vos achats maintenant !'}
            </p>
            <button
              onClick={() => navigate('/shop')}
              className="bg-[#6B8E23] text-white px-8 py-3 rounded-lg hover:bg-[#5a7a1d] transition"
              data-testid="go-to-shop"
            >
              {language === 'en' ? 'Shop Now' : language === 'ar' ? 'تسوق الآن' : 'Voir la boutique'}
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {orders.map((order) => (
              <div
                key={order.id}
                onClick={() => setSelectedOrder(order)}
                className="bg-white rounded-xl border border-gray-100 hover:border-gray-200 hover:shadow-md transition-all cursor-pointer overflow-hidden"
                data-testid={`order-card-${order.id}`}
              >
                <div className="p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-bold text-lg text-gray-900">#{order.order_number}</h3>
                      <p className="text-sm text-gray-500 mt-0.5">
                        {new Date(order.created_at).toLocaleDateString(
                          language === 'ar' ? 'ar-DZ' : language === 'en' ? 'en-US' : 'fr-FR',
                          { year: 'numeric', month: 'long', day: 'numeric' }
                        )}
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(order.status)}`}>
                      {getStatusLabel(order.status)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-gray-500 text-sm">
                      {order.items.length} {language === 'ar' ? 'منتج' : language === 'en' ? 'item(s)' : 'article(s)'}
                    </span>
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-[#6B8E23] text-lg">{order.total.toFixed(2)} EUR</span>
                      <ChevronRight size={18} className="text-gray-400" />
                    </div>
                  </div>
                </div>

                {/* Mini timeline */}
                <div className="px-5 pb-4">
                  <div className="flex gap-1">
                    {ORDER_STEPS.map((step, idx) => {
                      const currentIdx = ORDER_STEPS.findIndex(s => s.key === order.status);
                      const isActive = idx <= currentIdx && order.status !== 'cancelled';
                      return (
                        <div
                          key={step.key}
                          className={`flex-1 h-1.5 rounded-full ${isActive ? 'bg-green-500' : 'bg-gray-200'}`}
                        />
                      );
                    })}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
