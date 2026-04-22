import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { Loader2, CheckCircle, AlertCircle, Eye, EyeOff } from 'lucide-react';
import { meetingsAPI } from '../api/client';

export default function ResetPassword() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    
    const [status, setStatus] = useState('form'); // form, loading, success, error
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [formData, setFormData] = useState({
        newPassword: '',
        confirmPassword: ''
    });
    const [errors, setErrors] = useState({});
    const [message, setMessage] = useState('');
    
    useEffect(() => {
        // Vérifier que nous avons un token
        const token = searchParams.get('token');
        if (!token) {
            setStatus('error');
            setMessage('Token de réinitialisation manquant');
        }
    }, [searchParams]);
    
    const validatePassword = (password) => {
        const newErrors = {};
        
        if (password.length < 8) {
            newErrors.password = 'Le mot de passe doit contenir au moins 8 caractères';
        }
        
        if (!/[A-Z]/.test(password)) {
            newErrors.password = 'Le mot de passe doit contenir au moins une majuscule';
        }
        
        if (!/[a-z]/.test(password)) {
            newErrors.password = 'Le mot de passe doit contenir au moins une minuscule';
        }
        
        if (!/\d/.test(password)) {
            newErrors.password = 'Le mot de passe doit contenir au moins un chiffre';
        }
        
        return newErrors;
    };
    
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        
        // Valider en temps réel
        if (name === 'newPassword') {
            const passwordErrors = validatePassword(value);
            setErrors(prev => ({
                ...prev,
                ...passwordErrors
            }));
        }
        
        // Vérifier que les mots de passe correspondent
        if (name === 'confirmPassword' && value !== formData.newPassword) {
            setErrors(prev => ({
                ...prev,
                match: 'Les mots de passe ne correspondent pas'
            }));
        } else if (name === 'confirmPassword') {
            setErrors(prev => {
                const newErrors = { ...prev };
                delete newErrors.match;
                return newErrors;
            });
        }
    };
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Validation finale
        if (formData.newPassword !== formData.confirmPassword) {
            setErrors({ match: 'Les mots de passe ne correspondent pas' });
            return;
        }
        
        const passwordErrors = validatePassword(formData.newPassword);
        if (Object.keys(passwordErrors).length > 0) {
            setErrors(passwordErrors);
            return;
        }
        
        setStatus('loading');
        const token = searchParams.get('token');
        const userId = localStorage.getItem('pending_password_reset_user_id') || '1';
        
        try {
            const response = await meetingsAPI.resetPassword({
                token,
                user_id: parseInt(userId),
                new_password: formData.newPassword
            });
            
            if (response.status === 'success') {
                setStatus('success');
                setMessage('Mot de passe réinitialisé avec succès!');
                
                // Nettoyer localStorage
                localStorage.removeItem('pending_password_reset_user_id');
                
                // Redirection après 3 secondes
                setTimeout(() => {
                    navigate('/signin');
                }, 3000);
            } else {
                setStatus('error');
                setMessage(response.message || 'Erreur lors de la réinitialisation');
            }
        } catch (error) {
            setStatus('error');
            setMessage(error.response?.data?.detail || 'Erreur lors de la réinitialisation');
        }
    };
    
    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-50/40 via-white to-purple-50/40 flex items-center justify-center p-4">
            <div className="max-w-md w-full">
                {/* Card */}
                <div className="bg-white rounded-[2.5rem] p-10 border border-indigo-100 shadow-xl shadow-indigo-100/20">
                    {/* Status Icon */}
                    {status === 'loading' && (
                        <div className="w-20 h-20 bg-gradient-to-br from-yellow-100 to-amber-100 rounded-full flex items-center justify-center mx-auto mb-8">
                            <Loader2 className="w-10 h-10 text-amber-600 animate-spin" />
                        </div>
                    )}
                    
                    {status === 'success' && (
                        <div className="w-20 h-20 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-full flex items-center justify-center mx-auto mb-8">
                            <CheckCircle className="w-10 h-10 text-emerald-600" />
                        </div>
                    )}
                    
                    {status === 'error' && (
                        <div className="w-20 h-20 bg-gradient-to-br from-red-100 to-orange-100 rounded-full flex items-center justify-center mx-auto mb-8">
                            <AlertCircle className="w-10 h-10 text-red-600" />
                        </div>
                    )}
                    
                    {status === 'form' && (
                        <div className="w-20 h-20 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-8">
                            <span className="text-2xl">🔐</span>
                        </div>
                    )}
                    
                    {/* Title */}
                    <h1 className="text-3xl font-black text-gray-900 mb-4 text-center">
                        {status === 'loading' && 'Réinitialisation en cours...'}
                        {status === 'success' && 'Succès!'}
                        {status === 'error' && 'Erreur'}
                        {status === 'form' && 'Réinitialiser le Mot de Passe'}
                    </h1>
                    
                    {/* Message */}
                    {message && (
                        <p className={`text-center mb-6 font-bold ${
                            status === 'success' ? 'text-emerald-700' :
                            status === 'error' ? 'text-red-700' :
                            status === 'loading' ? 'text-amber-700' :
                            'text-gray-600'
                        }`}>
                            {message}
                        </p>
                    )}
                    
                    {/* Form */}
                    {status === 'form' && (
                        <form onSubmit={handleSubmit} className="space-y-4">
                            {/* New Password */}
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                    Nouveau Mot de Passe
                                </label>
                                <div className="relative">
                                    <input
                                        type={showPassword ? 'text' : 'password'}
                                        name="newPassword"
                                        value={formData.newPassword}
                                        onChange={handleInputChange}
                                        placeholder="Entrez votre nouveau mot de passe"
                                        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-indigo-600 focus:outline-none text-gray-900 placeholder-gray-400"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPassword(!showPassword)}
                                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                    >
                                        {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                    </button>
                                </div>
                                {errors.password && (
                                    <p className="text-red-600 text-sm mt-2">{errors.password}</p>
                                )}
                                
                                {/* Password Requirements */}
                                <div className="mt-3 space-y-1 text-xs text-gray-600">
                                    <div className={formData.newPassword.length >= 8 ? 'text-emerald-600' : ''}>
                                        ✓ Au moins 8 caractères
                                    </div>
                                    <div className={/[A-Z]/.test(formData.newPassword) ? 'text-emerald-600' : ''}>
                                        ✓ Au moins une majuscule
                                    </div>
                                    <div className={/[a-z]/.test(formData.newPassword) ? 'text-emerald-600' : ''}>
                                        ✓ Au moins une minuscule
                                    </div>
                                    <div className={/\d/.test(formData.newPassword) ? 'text-emerald-600' : ''}>
                                        ✓ Au moins un chiffre
                                    </div>
                                </div>
                            </div>
                            
                            {/* Confirm Password */}
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                    Confirmer le Mot de Passe
                                </label>
                                <div className="relative">
                                    <input
                                        type={showConfirmPassword ? 'text' : 'password'}
                                        name="confirmPassword"
                                        value={formData.confirmPassword}
                                        onChange={handleInputChange}
                                        placeholder="Confirmez votre mot de passe"
                                        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-indigo-600 focus:outline-none text-gray-900 placeholder-gray-400"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                    >
                                        {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                    </button>
                                </div>
                                {errors.match && (
                                    <p className="text-red-600 text-sm mt-2">{errors.match}</p>
                                )}
                            </div>
                            
                            {/* Submit Button */}
                            <button
                                type="submit"
                                disabled={status === 'loading' || Object.keys(errors).length > 0 || !formData.newPassword || !formData.confirmPassword}
                                className="w-full px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-black rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-6"
                            >
                                Réinitialiser le Mot de Passe
                            </button>
                        </form>
                    )}
                    
                    {/* Success Actions */}
                    {status === 'success' && (
                        <div className="space-y-4">
                            <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6">
                                <p className="text-emerald-900 font-medium">
                                    ✓ Votre mot de passe a été réinitialisé avec succès
                                </p>
                                <p className="text-sm text-emerald-700 mt-2">
                                    Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.
                                </p>
                            </div>
                            <p className="text-sm text-gray-600 text-center">
                                Redirection vers la connexion dans quelques secondes...
                            </p>
                            <Link
                                to="/signin"
                                className="w-full px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-black rounded-xl hover:shadow-lg transition-all text-center block"
                            >
                                Aller à la Connexion
                            </Link>
                        </div>
                    )}
                    
                    {/* Error Actions */}
                    {status === 'error' && (
                        <div className="space-y-4">
                            <div className="bg-red-50 border border-red-200 rounded-2xl p-6">
                                <p className="text-red-900 font-medium mb-2">
                                    Erreur de Réinitialisation
                                </p>
                                <p className="text-sm text-red-700">
                                    {message}
                                </p>
                            </div>
                            <div className="space-y-2">
                                <Link
                                    to="/signin?tab=forgot"
                                    className="w-full px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-black rounded-xl hover:shadow-lg transition-all text-center block"
                                >
                                    Nouvelle Demande
                                </Link>
                                <Link
                                    to="/signin"
                                    className="w-full px-6 py-3 bg-gray-200 text-gray-700 font-black rounded-xl hover:bg-gray-300 transition-all text-center block"
                                >
                                    Retour à la Connexion
                                </Link>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
