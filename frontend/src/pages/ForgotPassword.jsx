import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, ArrowRight, CheckCircle, AlertCircle } from 'lucide-react';
import { meetingsAPI } from '../api/client';

export default function ForgotPassword() {
    const navigate = useNavigate();
    
    const [status, setStatus] = useState('form'); // form, loading, sent, error
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setStatus('loading');
        setMessage('');
        
        try {
            const response = await meetingsAPI.forgotPassword({ email });
            
            if (response.status === 'success') {
                setStatus('sent');
                setMessage(`Un email de réinitialisation a été envoyé à ${email}`);
                
                // Sauvegarder l'email pour référence
                localStorage.setItem('forgot_password_email', email);
            } else {
                setStatus('error');
                setMessage(response.message || 'Erreur lors de l\'envoi du lien');
            }
        } catch (error) {
            setStatus('error');
            setMessage(error.response?.data?.detail || 'Erreur lors de la demande');
        }
    };
    
    const handleBackClick = () => {
        navigate('/signin');
    };
    
    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-50/40 via-white to-purple-50/40 flex items-center justify-center p-4">
            <div className="max-w-md w-full">
                {/* Card */}
                <div className="bg-white rounded-[2.5rem] p-10 border border-indigo-100 shadow-xl shadow-indigo-100/20">
                    {/* Icon */}
                    {status === 'form' && (
                        <div className="w-20 h-20 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-8">
                            <Mail className="w-10 h-10 text-indigo-600" />
                        </div>
                    )}
                    
                    {status === 'loading' && (
                        <div className="w-20 h-20 bg-gradient-to-br from-yellow-100 to-amber-100 rounded-full flex items-center justify-center mx-auto mb-8">
                            <div className="animate-spin">
                                <Mail className="w-10 h-10 text-amber-600" />
                            </div>
                        </div>
                    )}
                    
                    {status === 'sent' && (
                        <div className="w-20 h-20 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-full flex items-center justify-center mx-auto mb-8">
                            <CheckCircle className="w-10 h-10 text-emerald-600" />
                        </div>
                    )}
                    
                    {status === 'error' && (
                        <div className="w-20 h-20 bg-gradient-to-br from-red-100 to-orange-100 rounded-full flex items-center justify-center mx-auto mb-8">
                            <AlertCircle className="w-10 h-10 text-red-600" />
                        </div>
                    )}
                    
                    {/* Title */}
                    <h1 className="text-3xl font-black text-gray-900 mb-3 text-center">
                        {status === 'form' && 'Mot de Passe Oublié?'}
                        {status === 'loading' && 'Envoi en cours...'}
                        {status === 'sent' && 'Email Envoyé!'}
                        {status === 'error' && 'Erreur'}
                    </h1>
                    
                    {/* Description */}
                    {status === 'form' && (
                        <p className="text-gray-600 text-center mb-8">
                            Entrez votre adresse email et nous vous enverrons un lien pour réinitialiser votre mot de passe.
                        </p>
                    )}
                    
                    {/* Form */}
                    {(status === 'form' || status === 'loading') && (
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                    Adresse Email
                                </label>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="votre.email@exemple.com"
                                    required
                                    disabled={status === 'loading'}
                                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-indigo-600 focus:outline-none text-gray-900 placeholder-gray-400 disabled:bg-gray-100"
                                />
                            </div>
                            
                            <button
                                type="submit"
                                disabled={status === 'loading' || !email}
                                className="w-full px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-black rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {status === 'loading' ? 'Envoi en cours...' : 'Envoyer le Lien'}
                            </button>
                        </form>
                    )}
                    
                    {/* Sent State */}
                    {status === 'sent' && (
                        <div className="space-y-6">
                            <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6">
                                <p className="text-emerald-900 font-bold mb-2">✓ Email envoyé avec succès</p>
                                <p className="text-sm text-emerald-700">
                                    Un lien de réinitialisation a été envoyé à <strong>{email}</strong>
                                </p>
                            </div>
                            
                            <div className="space-y-3 bg-blue-50 border border-blue-200 rounded-2xl p-6">
                                <p className="text-sm font-bold text-blue-900">Next steps:</p>
                                <ol className="text-sm text-blue-700 space-y-2 list-decimal list-inside">
                                    <li>Ouvrez votre email</li>
                                    <li>Cliquez sur le lien de réinitialisation</li>
                                    <li>Choisissez votre nouveau mot de passe</li>
                                    <li>Connectez-vous avec vos identifiants</li>
                                </ol>
                            </div>
                            
                            <p className="text-xs text-gray-600 text-center">
                                Le lien reste valide <strong>24 heures</strong>
                            </p>
                            
                            <div className="space-y-2">
                                <button
                                    onClick={handleBackClick}
                                    className="w-full px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-black rounded-xl hover:shadow-lg transition-all flex items-center justify-center gap-2"
                                >
                                    Retour à la Connexion
                                    <ArrowRight size={18} />
                                </button>
                                
                                <button
                                    onClick={() => {
                                        setStatus('form');
                                        setEmail('');
                                        setMessage('');
                                    }}
                                    className="w-full px-6 py-3 bg-gray-200 text-gray-700 font-black rounded-xl hover:bg-gray-300 transition-all"
                                >
                                    Réessayer avec un autre email
                                </button>
                            </div>
                        </div>
                    )}
                    
                    {/* Error State */}
                    {status === 'error' && (
                        <div className="space-y-6">
                            <div className="bg-red-50 border border-red-200 rounded-2xl p-6">
                                <p className="text-red-900 font-bold mb-2">Erreur</p>
                                <p className="text-sm text-red-700">{message}</p>
                            </div>
                            
                            <div className="space-y-2">
                                <button
                                    onClick={() => {
                                        setStatus('form');
                                        setEmail('');
                                        setMessage('');
                                    }}
                                    className="w-full px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-black rounded-xl hover:shadow-lg transition-all"
                                >
                                    Réessayer
                                </button>
                                
                                <button
                                    onClick={handleBackClick}
                                    className="w-full px-6 py-3 bg-gray-200 text-gray-700 font-black rounded-xl hover:bg-gray-300 transition-all"
                                >
                                    Retour à la Connexion
                                </button>
                            </div>
                        </div>
                    )}
                    
                    {/* Footer */}
                    {status === 'form' && (
                        <div className="mt-8 pt-8 border-t border-gray-100 text-center">
                            <p className="text-sm text-gray-600">
                                Vous avez votre mot de passe?{' '}
                                <Link to="/signin" className="text-indigo-600 hover:text-indigo-700 font-bold">
                                    Se connecter
                                </Link>
                            </p>
                            <p className="text-sm text-gray-600 mt-2">
                                Pas encore de compte?{' '}
                                <Link to="/signup" className="text-indigo-600 hover:text-indigo-700 font-bold">
                                    S'inscrire
                                </Link>
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
