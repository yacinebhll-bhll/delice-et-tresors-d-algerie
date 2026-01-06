import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth, useLanguage } from '../App';
import { Eye, EyeOff, User, Mail, Lock, LogIn, UserPlus } from 'lucide-react';

const AuthPage = () => {
  const { login, register, user } = useAuth();
  const { t, language } = useLanguage();
  const navigate = useNavigate();
  
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    fullName: '',
    confirmPassword: ''
  });

  // Redirect if already logged in
  if (user) {
    navigate('/profile');
    return null;
  }

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        const result = await login(formData.email, formData.password);
        if (result.success) {
          navigate('/profile');
        } else {
          setError(result.error);
        }
      } else {
        // Registration validation
        if (formData.password !== formData.confirmPassword) {
          setError(language === 'ar' ? 'كلمات المرور غير متطابقة' :
                   language === 'en' ? 'Passwords do not match' :
                   'Les mots de passe ne correspondent pas');
          setLoading(false);
          return;
        }
        
        if (formData.password.length < 6) {
          setError(language === 'ar' ? 'كلمة المرور يجب أن تكون 6 أحرف على الأقل' :
                   language === 'en' ? 'Password must be at least 6 characters' :
                   'Le mot de passe doit contenir au moins 6 caractères');
          setLoading(false);
          return;
        }

        const result = await register(formData.email, formData.password, formData.fullName);
        if (result.success) {
          navigate('/profile');
        } else {
          setError(result.error);
        }
      }
    } catch (err) {
      setError('Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError('');
    setFormData({
      email: '',
      password: '',
      fullName: '',
      confirmPassword: ''
    });
  };

  const getTitle = () => {
    if (isLogin) {
      return language === 'ar' ? 'تسجيل الدخول' :
             language === 'en' ? 'Sign In' :
             'Connexion';
    } else {
      return language === 'ar' ? 'إنشاء حساب' :
             language === 'en' ? 'Create Account' :
             'Créer un Compte';
    }
  };

  const getSubtitle = () => {
    if (isLogin) {
      return language === 'ar' ? 'مرحباً بعودتك إلى سومام هيريتاج' :
             language === 'en' ? 'Welcome back to Délices et Trésors' :
             'Bienvenue sur Délices et Trésors d\'Algérie';
    } else {
      return language === 'ar' ? 'انضم إلى مجتمع سومام هيريتاج' :
             language === 'en' ? 'Join the Délices et Trésors community' :
             'Rejoignez la communauté Délices et Trésors';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-gradient-to-r from-amber-600 to-orange-600 rounded-2xl flex items-center justify-center mb-6">
            <span className="text-white font-bold text-2xl">SH</span>
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            {getTitle()}
          </h2>
          <p className="text-gray-600">
            {getSubtitle()}
          </p>
        </div>

        {/* Form */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="bg-white p-8 rounded-2xl shadow-xl space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            {!isLogin && (
              <div className="form-group">
                <label className="form-label flex items-center">
                  <User size={18} className="mr-2 text-gray-500" />
                  {language === 'ar' ? 'الاسم الكامل' :
                   language === 'en' ? 'Full Name' :
                   'Nom Complet'}
                </label>
                <input
                  type="text"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleInputChange}
                  className="form-input"
                  required={!isLogin}
                  placeholder={language === 'ar' ? 'أدخل اسمك الكامل' :
                              language === 'en' ? 'Enter your full name' :
                              'Entrez votre nom complet'}
                />
              </div>
            )}

            <div className="form-group">
              <label className="form-label flex items-center">
                <Mail size={18} className="mr-2 text-gray-500" />
                {language === 'ar' ? 'البريد الإلكتروني' :
                 language === 'en' ? 'Email' :
                 'Email'}
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className="form-input"
                required
                placeholder={language === 'ar' ? 'أدخل بريدك الإلكتروني' :
                            language === 'en' ? 'Enter your email' :
                            'Entrez votre email'}
              />
            </div>

            <div className="form-group">
              <label className="form-label flex items-center">
                <Lock size={18} className="mr-2 text-gray-500" />
                {language === 'ar' ? 'كلمة المرور' :
                 language === 'en' ? 'Password' :
                 'Mot de passe'}
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="form-input pr-12"
                  required
                  placeholder={language === 'ar' ? 'أدخل كلمة المرور' :
                              language === 'en' ? 'Enter your password' :
                              'Entrez votre mot de passe'}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {isLogin && (
                <div className="text-right mt-2">
                  <Link
                    to="/forgot-password"
                    className="text-sm text-amber-600 hover:text-amber-700 font-medium"
                  >
                    {language === 'ar' ? 'نسيت كلمة المرور؟' :
                     language === 'en' ? 'Forgot password?' :
                     'Mot de passe oublié ?'}
                  </Link>
                </div>
              )}
            </div>

            {!isLogin && (
              <div className="form-group">
                <label className="form-label flex items-center">
                  <Lock size={18} className="mr-2 text-gray-500" />
                  {language === 'ar' ? 'تأكيد كلمة المرور' :
                   language === 'en' ? 'Confirm Password' :
                   'Confirmer le mot de passe'}
                </label>
                <input
                  type={showPassword ? "text" : "password"}
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="form-input"
                  required={!isLogin}
                  placeholder={language === 'ar' ? 'أعد إدخال كلمة المرور' :
                              language === 'en' ? 'Confirm your password' :
                              'Confirmez votre mot de passe'}
                />
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary flex items-center justify-center py-4 text-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
              ) : (
                <>
                  {isLogin ? <LogIn className="mr-2" size={20} /> : <UserPlus className="mr-2" size={20} />}
                  {isLogin ? 
                    (language === 'ar' ? 'تسجيل الدخول' :
                     language === 'en' ? 'Sign In' :
                     'Se connecter') :
                    (language === 'ar' ? 'إنشاء حساب' :
                     language === 'en' ? 'Create Account' :
                     'Créer un compte')
                  }
                </>
              )}
            </button>
          </div>

          {/* Toggle Mode */}
          <div className="text-center">
            <p className="text-gray-600 mb-4">
              {isLogin ? 
                (language === 'ar' ? 'ليس لديك حساب؟' :
                 language === 'en' ? 'Don\'t have an account?' :
                 'Vous n\'avez pas de compte ?') :
                (language === 'ar' ? 'لديك حساب بالفعل؟' :
                 language === 'en' ? 'Already have an account?' :
                 'Vous avez déjà un compte ?')
              }
            </p>
            <button
              type="button"
              onClick={toggleMode}
              className="text-amber-600 hover:text-amber-700 font-semibold transition-colors duration-200"
            >
              {isLogin ? 
                (language === 'ar' ? 'إنشاء حساب جديد' :
                 language === 'en' ? 'Create new account' :
                 'Créer un nouveau compte') :
                (language === 'ar' ? 'تسجيل الدخول' :
                 language === 'en' ? 'Sign in instead' :
                 'Se connecter plutôt')
              }
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AuthPage;