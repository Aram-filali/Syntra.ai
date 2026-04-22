import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { Loader2, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react';
import { meetingsAPI } from '../api/client';

export default function VerifyEmail() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState('loading'); // loading, success, error
    const [message, setMessage] = useState('');
    const [userId, setUserId] = useState('');

    useEffect(() => {
        verifyEmail();
    }, [searchParams]);

    const verifyEmail = async () => {
        setStatus('loading');
        const token = searchParams.get('token');
        const uid = searchParams.get('user_id');

        if (!token) {
            setStatus('error');
            setMessage('Token de vérification manquant');
            return;
        }

        try {
            // Extract user_id from localStorage if not in URL
            const storedUserId = localStorage.getItem('pending_verification_user_id');
            const actualUserId = uid || storedUserId || '1';
            setUserId(actualUserId);

            const response = await meetingsAPI.verifyEmail({
                token,
                user_id: parseInt(actualUserId)
            });

            setStatus('success');
            setMessage('Email vérifié avec succès!');

            // Clear localStorage
            localStorage.removeItem('pending_verification_email');
            localStorage.removeItem('pending_verification_user_id');
            
            // Redirection automatique supprimée à la demande de l'utilisateur
        } catch (error) {
            setStatus('error');
            setMessage(error.response?.data?.detail || 'Erreur lors de la vérification');
        }
    };

    return (
        <div className="min-h-screen bg-white flex flex-col">
            {/* Header */}
            <div className="flex justify-between items-center px-8 py-6">
                <div className="flex items-center gap-2">
                    <img src="/syntra-logo.png" alt="Syntra.ai Logo" className="h-10 w-auto" />
                </div>
                <div className="text-sm">
                    <span className="text-gray-600">Syntra.ai </span>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-grow flex items-center justify-center px-4 py-8">
                <div className="w-full max-w-2xl text-center">
                    {/* Status Icon */}
                    <div className={`w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-8 ${
                        status === 'loading' ? 'bg-amber-50' :
                        status === 'success' ? 'bg-emerald-50' :
                        'bg-red-50'
                    }`}>
                        {status === 'loading' && <Loader2 className="w-12 h-12 text-amber-500 animate-spin" />}
                        {status === 'success' && <CheckCircle className="w-12 h-12 text-emerald-500" />}
                        {status === 'error' && <AlertCircle className="w-12 h-12 text-red-500" />}
                    </div>

                    {/* Title */}
                    <h1 className="text-5xl font-bold text-gray-900 mb-6">
                        {status === 'loading' && 'Vérification en cours'}
                        {status === 'success' && 'Email Vérifié !'}
                        {status === 'error' && 'Échec de la vérification'}
                    </h1>

                    {/* Message Card */}
                    <div className="max-w-md mx-auto mb-10">
                        <p className={`text-xl font-bold mb-8 ${
                            status === 'success' ? 'text-emerald-600' :
                            status === 'error' ? 'text-red-600' :
                            'text-amber-600'
                        }`}>
                            {message}
                        </p>

                        {status === 'loading' && (
                            <div className="bg-gray-50 border-2 border-gray-100 rounded-3xl p-8">
                                <p className="text-gray-600">Veuillez patienter pendant que nous validons votre compte...</p>
                            </div>
                        )}

                        {status === 'success' && (
                            <div className="bg-emerald-50 border-2 border-emerald-100 rounded-3xl p-8">
                                <p className="text-emerald-900 font-bold mb-2">Félicitations !</p>
                                <p className="text-emerald-700">Votre compte est maintenant actif. Vous pouvez maintenant vous connecter.</p>
                            </div>
                        )}

                        {status === 'error' && (
                            <div className="bg-red-50 border-2 border-red-100 rounded-3xl p-8">
                                <p className="text-red-900 font-bold mb-2">Problème détecté</p>
                                <p className="text-red-700">Le lien semble invalide ou a déjà été utilisé.</p>
                            </div>
                        )}
                    </div>

                    {/* Action Area */}
                    <div className="max-w-md mx-auto">
                        {status === 'success' && (
                            <Link
                                to="/signin"
                                className="w-full bg-purple-700 hover:bg-purple-800 text-white font-bold py-4 px-6 rounded-xl transition-all flex items-center justify-center gap-3 text-lg shadow-lg shadow-purple-200"
                            >
                                Se connecter maintenant
                                <ArrowRight size={22} />
                            </Link>
                        )}

                        {status === 'error' && (
                            <div className="space-y-4">
                                <button
                                    onClick={verifyEmail}
                                    className="w-full bg-purple-700 hover:bg-purple-800 text-white font-bold py-4 px-6 rounded-xl transition-all flex items-center justify-center gap-3 text-lg"
                                >
                                    Réessayer la vérification
                                </button>
                                <Link
                                    to="/signup"
                                    className="block w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-4 px-6 rounded-xl transition-all"
                                >
                                    Retour à l'inscription
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="py-8 text-center text-xs text-gray-400">
                <p>© 2026 Syntra.ai. Tous droits réservés.</p>
            </div>
        </div>
    );
}
