import React, { useState } from 'react';
import { Play, X } from 'lucide-react';

const ProductVideoPlayer = ({ videos, productName }) => {
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  if (!videos || videos.length === 0) {
    return null;
  }

  const handlePlayVideo = (video) => {
    setSelectedVideo(video);
    setIsPlaying(true);
  };

  const handleCloseVideo = () => {
    setSelectedVideo(null);
    setIsPlaying(false);
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Vidéos du produit</h3>
      
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {videos.map((video, index) => (
          <div
            key={video.id || index}
            className="relative group cursor-pointer"
            onClick={() => handlePlayVideo(video)}
          >
            <div className="relative aspect-video bg-gray-200 rounded-lg overflow-hidden">
              {video.thumbnail_url ? (
                <img
                  src={video.thumbnail_url}
                  alt={video.title?.fr || `Vidéo ${index + 1}`}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-green-100 to-green-200">
                  <Play size={48} className="text-green-700" />
                </div>
              )}
              
              {/* Play overlay */}
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all flex items-center justify-center">
                <div className="transform scale-0 group-hover:scale-100 transition-transform">
                  <div className="bg-white rounded-full p-3">
                    <Play size={32} className="text-green-700" />
                  </div>
                </div>
              </div>
              
              {video.duration_seconds && (
                <span className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
                  {Math.floor(video.duration_seconds / 60)}:{(video.duration_seconds % 60).toString().padStart(2, '0')}
                </span>
              )}
            </div>
            
            <p className="mt-2 text-sm font-medium line-clamp-2">
              {video.title?.fr || `Vidéo ${index + 1}`}
            </p>
          </div>
        ))}
      </div>

      {/* Video Modal */}
      {isPlaying && selectedVideo && (
        <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4">
          <div className="relative w-full max-w-4xl">
            <button
              onClick={handleCloseVideo}
              className="absolute -top-12 right-0 text-white hover:text-gray-300 transition-colors"
            >
              <X size={32} />
            </button>
            
            <div className="bg-black rounded-lg overflow-hidden">
              <video
                src={selectedVideo.url}
                controls
                autoPlay
                className="w-full"
              >
                Votre navigateur ne supporte pas la lecture de vidéos.
              </video>
            </div>
            
            {selectedVideo.title && (
              <div className="mt-4 text-white">
                <h3 className="text-xl font-semibold">{selectedVideo.title.fr}</h3>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductVideoPlayer;