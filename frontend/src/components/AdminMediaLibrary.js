import React, { useState, useEffect, useCallback } from 'react';
import { useLanguage } from '../App';
import { 
  Upload, Trash2, Search, Grid, List, Image as ImageIcon, 
  FileText, Film, Music, Copy, Check, X, FolderPlus, Filter
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminMediaLibrary = () => {
  const { language } = useLanguage();
  const [media, setMedia] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedMedia, setSelectedMedia] = useState(null);
  const [copiedUrl, setCopiedUrl] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const mediaTypes = [
    { value: 'all', label: language === 'ar' ? 'الكل' : language === 'en' ? 'All' : 'Tous' },
    { value: 'image', label: language === 'ar' ? 'صور' : language === 'en' ? 'Images' : 'Images' },
    { value: 'document', label: language === 'ar' ? 'مستندات' : language === 'en' ? 'Documents' : 'Documents' },
    { value: 'video', label: language === 'ar' ? 'فيديو' : language === 'en' ? 'Videos' : 'Vidéos' },
    { value: 'audio', label: language === 'ar' ? 'صوت' : language === 'en' ? 'Audio' : 'Audio' }
  ];

  useEffect(() => {
    fetchMedia();
  }, []);

  const fetchMedia = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/admin/media`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMedia(response.data || []);
    } catch (error) {
      console.error('Error fetching media:', error);
      setMedia([]);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    setUploading(true);
    setUploadProgress(0);

    const token = localStorage.getItem('token');
    const totalFiles = files.length;
    let uploadedCount = 0;

    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        await axios.post(`${API}/admin/media/upload`, formData, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            const fileProgress = (progressEvent.loaded / progressEvent.total) * 100;
            const overallProgress = ((uploadedCount + fileProgress / 100) / totalFiles) * 100;
            setUploadProgress(Math.round(overallProgress));
          }
        });
        uploadedCount++;
      } catch (error) {
        console.error(`Error uploading ${file.name}:`, error);
      }
    }

    setUploading(false);
    setUploadProgress(0);
    fetchMedia();
    event.target.value = '';
  };

  const handleDelete = async (mediaId) => {
    if (!window.confirm(
      language === 'ar' ? 'هل أنت متأكد من حذف هذا الملف؟' :
      language === 'en' ? 'Are you sure you want to delete this file?' :
      'Êtes-vous sûr de vouloir supprimer ce fichier ?'
    )) return;

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/admin/media/${mediaId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMedia(media.filter(m => m.id !== mediaId));
      if (selectedMedia?.id === mediaId) setSelectedMedia(null);
    } catch (error) {
      console.error('Error deleting media:', error);
    }
  };

  const copyToClipboard = (url) => {
    navigator.clipboard.writeText(url);
    setCopiedUrl(url);
    setTimeout(() => setCopiedUrl(null), 2000);
  };

  const getFileIcon = (type) => {
    switch (type) {
      case 'image': return <ImageIcon size={24} className="text-blue-500" />;
      case 'video': return <Film size={24} className="text-purple-500" />;
      case 'audio': return <Music size={24} className="text-green-500" />;
      default: return <FileText size={24} className="text-gray-500" />;
    }
  };

  const getFileType = (mimeType) => {
    if (mimeType?.startsWith('image/')) return 'image';
    if (mimeType?.startsWith('video/')) return 'video';
    if (mimeType?.startsWith('audio/')) return 'audio';
    return 'document';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const filteredMedia = media.filter(item => {
    const matchesSearch = item.filename?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          item.original_name?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedType === 'all' || getFileType(item.mime_type) === selectedType;
    return matchesSearch && matchesType;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {language === 'ar' ? 'مكتبة الوسائط' : language === 'en' ? 'Media Library' : 'Bibliothèque média'}
          </h1>
          <p className="text-gray-600 mt-1">
            {language === 'ar' ? `${media.length} ملف` : 
             language === 'en' ? `${media.length} files` : 
             `${media.length} fichiers`}
          </p>
        </div>

        <label className="btn-primary flex items-center cursor-pointer">
          <Upload size={20} className="mr-2" />
          {uploading ? (
            <span>{uploadProgress}%</span>
          ) : (
            language === 'ar' ? 'رفع ملفات' : language === 'en' ? 'Upload Files' : 'Télécharger'
          )}
          <input
            type="file"
            multiple
            accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.xls,.xlsx"
            onChange={handleUpload}
            className="hidden"
            disabled={uploading}
          />
        </label>
      </div>

      {/* Upload Progress */}
      {uploading && (
        <div className="bg-white rounded-lg p-4 shadow">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              {language === 'ar' ? 'جاري الرفع...' : language === 'en' ? 'Uploading...' : 'Téléchargement...'}
            </span>
            <span className="text-sm text-gray-500">{uploadProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-amber-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Filters & View Toggle */}
      <div className="bg-white rounded-xl shadow-lg p-4">
        <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
          {/* Search */}
          <div className="relative flex-1 w-full md:max-w-md">
            <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder={language === 'ar' ? 'بحث...' : language === 'en' ? 'Search...' : 'Rechercher...'}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="form-input pl-10 w-full"
            />
          </div>

          <div className="flex items-center gap-4 w-full md:w-auto">
            {/* Type Filter */}
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="form-input"
            >
              {mediaTypes.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>

            {/* View Toggle */}
            <div className="flex border border-gray-300 rounded-lg overflow-hidden">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 ${viewMode === 'grid' ? 'bg-amber-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'}`}
              >
                <Grid size={20} />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 ${viewMode === 'list' ? 'bg-amber-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'}`}
              >
                <List size={20} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Media Grid/List */}
      {filteredMedia.length === 0 ? (
        <div className="bg-white rounded-xl shadow-lg p-12 text-center">
          <ImageIcon size={48} className="mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {language === 'ar' ? 'لا توجد ملفات' : language === 'en' ? 'No files found' : 'Aucun fichier trouvé'}
          </h3>
          <p className="text-gray-500">
            {language === 'ar' ? 'ابدأ برفع ملفاتك' : 
             language === 'en' ? 'Start by uploading your files' : 
             'Commencez par télécharger vos fichiers'}
          </p>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {filteredMedia.map((item) => (
            <div
              key={item.id}
              className={`bg-white rounded-lg shadow-md overflow-hidden cursor-pointer transition-all hover:shadow-lg ${
                selectedMedia?.id === item.id ? 'ring-2 ring-amber-500' : ''
              }`}
              onClick={() => setSelectedMedia(item)}
            >
              <div className="aspect-square bg-gray-100 flex items-center justify-center overflow-hidden">
                {getFileType(item.mime_type) === 'image' ? (
                  <img
                    src={item.url}
                    alt={item.original_name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="p-4">
                    {getFileIcon(getFileType(item.mime_type))}
                  </div>
                )}
              </div>
              <div className="p-2">
                <p className="text-xs font-medium text-gray-900 truncate">
                  {item.original_name || item.filename}
                </p>
                <p className="text-xs text-gray-500">
                  {formatFileSize(item.size || 0)}
                </p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  {language === 'ar' ? 'الملف' : language === 'en' ? 'File' : 'Fichier'}
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">
                  {language === 'ar' ? 'النوع' : language === 'en' ? 'Type' : 'Type'}
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">
                  {language === 'ar' ? 'الحجم' : language === 'en' ? 'Size' : 'Taille'}
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  {language === 'ar' ? 'إجراءات' : language === 'en' ? 'Actions' : 'Actions'}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredMedia.map((item) => (
                <tr 
                  key={item.id}
                  className={`hover:bg-gray-50 cursor-pointer ${
                    selectedMedia?.id === item.id ? 'bg-amber-50' : ''
                  }`}
                  onClick={() => setSelectedMedia(item)}
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0 w-10 h-10 bg-gray-100 rounded flex items-center justify-center overflow-hidden">
                        {getFileType(item.mime_type) === 'image' ? (
                          <img src={item.url} alt="" className="w-full h-full object-cover" />
                        ) : (
                          getFileIcon(getFileType(item.mime_type))
                        )}
                      </div>
                      <span className="text-sm font-medium text-gray-900 truncate max-w-xs">
                        {item.original_name || item.filename}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 hidden sm:table-cell">
                    <span className="text-sm text-gray-500 capitalize">
                      {getFileType(item.mime_type)}
                    </span>
                  </td>
                  <td className="px-4 py-3 hidden md:table-cell">
                    <span className="text-sm text-gray-500">
                      {formatFileSize(item.size || 0)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={(e) => { e.stopPropagation(); copyToClipboard(item.url); }}
                        className="p-1 text-gray-400 hover:text-amber-600"
                        title={language === 'ar' ? 'نسخ الرابط' : language === 'en' ? 'Copy URL' : 'Copier l\'URL'}
                      >
                        {copiedUrl === item.url ? <Check size={18} className="text-green-500" /> : <Copy size={18} />}
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }}
                        className="p-1 text-gray-400 hover:text-red-600"
                        title={language === 'ar' ? 'حذف' : language === 'en' ? 'Delete' : 'Supprimer'}
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Media Details Sidebar */}
      {selectedMedia && (
        <div className="fixed inset-y-0 right-0 w-80 bg-white shadow-xl z-50 overflow-y-auto">
          <div className="p-4 border-b flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">
              {language === 'ar' ? 'تفاصيل الملف' : language === 'en' ? 'File Details' : 'Détails du fichier'}
            </h3>
            <button onClick={() => setSelectedMedia(null)} className="text-gray-400 hover:text-gray-600">
              <X size={20} />
            </button>
          </div>

          <div className="p-4 space-y-4">
            {/* Preview */}
            <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden flex items-center justify-center">
              {getFileType(selectedMedia.mime_type) === 'image' ? (
                <img src={selectedMedia.url} alt="" className="w-full h-full object-contain" />
              ) : getFileType(selectedMedia.mime_type) === 'video' ? (
                <video src={selectedMedia.url} controls className="w-full h-full" />
              ) : getFileType(selectedMedia.mime_type) === 'audio' ? (
                <audio src={selectedMedia.url} controls className="w-full" />
              ) : (
                <div className="text-center p-4">
                  {getFileIcon(getFileType(selectedMedia.mime_type))}
                  <p className="mt-2 text-sm text-gray-500">
                    {language === 'ar' ? 'معاينة غير متاحة' : language === 'en' ? 'Preview not available' : 'Aperçu non disponible'}
                  </p>
                </div>
              )}
            </div>

            {/* Info */}
            <div className="space-y-3">
              <div>
                <label className="text-xs text-gray-500 uppercase">
                  {language === 'ar' ? 'اسم الملف' : language === 'en' ? 'Filename' : 'Nom du fichier'}
                </label>
                <p className="text-sm font-medium text-gray-900 break-all">
                  {selectedMedia.original_name || selectedMedia.filename}
                </p>
              </div>

              <div>
                <label className="text-xs text-gray-500 uppercase">
                  {language === 'ar' ? 'النوع' : language === 'en' ? 'Type' : 'Type'}
                </label>
                <p className="text-sm text-gray-900">{selectedMedia.mime_type}</p>
              </div>

              <div>
                <label className="text-xs text-gray-500 uppercase">
                  {language === 'ar' ? 'الحجم' : language === 'en' ? 'Size' : 'Taille'}
                </label>
                <p className="text-sm text-gray-900">{formatFileSize(selectedMedia.size || 0)}</p>
              </div>

              <div>
                <label className="text-xs text-gray-500 uppercase">URL</label>
                <div className="flex items-center gap-2 mt-1">
                  <input
                    type="text"
                    value={selectedMedia.url}
                    readOnly
                    className="form-input text-sm flex-1"
                  />
                  <button
                    onClick={() => copyToClipboard(selectedMedia.url)}
                    className="p-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700"
                  >
                    {copiedUrl === selectedMedia.url ? <Check size={18} /> : <Copy size={18} />}
                  </button>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="pt-4 border-t space-y-2">
              <a
                href={selectedMedia.url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary w-full flex items-center justify-center"
              >
                {language === 'ar' ? 'فتح في نافذة جديدة' : language === 'en' ? 'Open in new tab' : 'Ouvrir dans un nouvel onglet'}
              </a>
              <button
                onClick={() => handleDelete(selectedMedia.id)}
                className="w-full py-2 px-4 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 flex items-center justify-center"
              >
                <Trash2 size={18} className="mr-2" />
                {language === 'ar' ? 'حذف' : language === 'en' ? 'Delete' : 'Supprimer'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminMediaLibrary;
