import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { MapPin } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

// Fix Leaflet icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const InteractiveOriginMap = ({ productOrigin, onRegionClick }) => {
  const [regions, setRegions] = useState([]);
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRegions();
  }, []);

  const fetchRegions = async () => {
    try {
      const response = await axios.get(`${API}/regions`);
      setRegions(response.data);
    } catch (error) {
      console.error('Error fetching regions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRegionClick = async (regionId) => {
    try {
      const response = await axios.get(`${API}/regions/${regionId}`);
      setSelectedRegion(response.data);
      if (onRegionClick) {
        onRegionClick(response.data);
      }
    } catch (error) {
      console.error('Error fetching region details:', error);
    }
  };

  // Default center on Algeria
  const defaultCenter = [28.0339, 1.6596];
  const defaultZoom = 5;

  if (loading) {
    return <div className="text-center py-8">Chargement de la carte...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="h-96 rounded-lg overflow-hidden border border-gray-200">
        <MapContainer
          center={productOrigin?.coordinates ? 
            [productOrigin.coordinates.lat, productOrigin.coordinates.lng] : 
            defaultCenter
          }
          zoom={productOrigin ? 8 : defaultZoom}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {productOrigin && (
            <Marker 
              position={[productOrigin.coordinates.lat, productOrigin.coordinates.lng]}
            >
              <Popup>
                <div className="p-2">
                  <h3 className="font-bold mb-1">{productOrigin.region_name.fr}</h3>
                  {productOrigin.producer_name && (
                    <p className="text-sm">Producteur: {productOrigin.producer_name}</p>
                  )}
                </div>
              </Popup>
            </Marker>
          )}
          
          {!productOrigin && regions.map((region) => (
            <Marker
              key={region.id}
              position={[region.coordinates.lat, region.coordinates.lng]}
              eventHandlers={{
                click: () => handleRegionClick(region.id)
              }}
            >
              <Popup>
                <div className="p-2">
                  <h3 className="font-bold mb-1">{region.name.fr}</h3>
                  <p className="text-sm">{region.product_ids?.length || 0} produits</p>
                  <button 
                    onClick={() => handleRegionClick(region.id)}
                    className="text-blue-600 text-sm mt-2 hover:underline"
                  >
                    Voir les produits
                  </button>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {selectedRegion && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-xl font-bold mb-2">{selectedRegion.name.fr}</h3>
          {selectedRegion.description && (
            <p className="text-gray-700 mb-3">{selectedRegion.description.fr}</p>
          )}
          <div className="text-sm text-gray-600">
            {selectedRegion.products?.length || 0} produit(s) de cette région
          </div>
        </div>
      )}
    </div>
  );
};

export default InteractiveOriginMap;