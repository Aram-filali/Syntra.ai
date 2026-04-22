import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, ArrowRight, RefreshCw } from 'lucide-react';
import { meetingsAPI } from '../api/client';

export default function AwaitingEmailVerification() {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [isResending, setIsResending] = useState(false);
    const [resendMessage, setResendMessage] = useState('');
    const [resendError, setResendError] = useState('');

    useEffect(() => {
        // Get email from localStorage (set after registration)
        const storedEmail = localStorage.getItem('pending_verification_email');
        if (storedEmail) {
            setEmail(storedEmail);
        } else {
            // Redirect to signup if no pending verification
            navigate('/signup');
        }
    }, [navigate]);

    const handleResendEmail = async () => {
        if (!email) return;

        setIsResending(true);
        setResendMessage('');
        setResendError('');

        try {
            const response = await meetingsAPI.resendVerificationEmail(email);
            setResendMessage('Email renvoyé! Vérifiez votre boîte de réception');
            setResendError('');
        } catch (error) {
            setResendError('Erreur lors de l\'envoi de l\'email');
            setResendMessage('');
        } finally {
            setIsResending(false);
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
                    <span className="text-gray-600">Besoin d'aide ? </span>
                    <a href="mailto:support@syntra.ai" className="text-blue-600 hover:underline">
                        Contactez le support
                    </a>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-grow flex items-center justify-center px-4 py-8">
                <div className="w-full max-w-2xl text-center">
                    {/* Icon */}
                    <div className="w-24 h-24 bg-purple-50 rounded-full flex items-center justify-center mx-auto mb-8">
                        <Mail className="w-12 h-12 text-purple-600" />
                    </div>

                    {/* Title */}
                    <h1 className="text-5xl font-bold text-gray-900 mb-6">
                        Vérifiez votre boîte de réception
                    </h1>

                    {/* Description */}
                    <div className="mb-10">
                        <p className="text-xl text-gray-600 mb-2">
                            Nous avons envoyé un lien de confirmation à :
                        </p>
                        <p className="text-2xl font-bold text-purple-700">
                            {email}
                        </p>
                    </div>

                    {/* Instructions Card */}
                    <div className="max-w-md mx-auto bg-gray-50 border-2 border-gray-100 rounded-3xl p-8 mb-10">
                        <div className="space-y-6 text-left">
                            <div className="flex items-start gap-4">
                                <div className="w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center flex-shrink-0 font-black text-sm">1</div>
                                <div>
                                    <p className="font-bold text-gray-900 text-lg">Ouvrez l'email</p>
                                    <p className="text-gray-600">L'expéditeur est "Syntra.ai"</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-4">
                                <div className="w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center flex-shrink-0 font-black text-sm">2</div>
                                <div>
                                    <p className="font-bold text-gray-900 text-lg">Cliquez sur le bouton</p>
                                    <p className="text-gray-600">Pour confirmer votre adresse</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Action Area */}
                    <div className="max-w-md mx-auto space-y-6">
                        {resendMessage && (
                            <div className="bg-emerald-50 border-2 border-emerald-100 text-emerald-700 px-4 py-3 rounded-xl font-bold text-sm">
                                {resendMessage}
                            </div>
                        )}

                        {resendError && (
                            <div className="bg-red-50 border-2 border-red-100 text-red-600 px-4 py-3 rounded-xl font-bold text-sm">
                                {resendError}
                            </div>
                        )}

                        <button
                            onClick={handleResendEmail}
                            disabled={isResending}
                            className="w-full bg-purple-700 hover:bg-purple-800 text-white font-bold py-4 px-6 rounded-xl transition-all disabled:opacity-50 flex items-center justify-center gap-3 text-lg shadow-lg shadow-purple-200"
                        >
                            <RefreshCw size={22} className={isResending ? 'animate-spin' : ''} />
                            {isResending ? 'Envoi en cours...' : 'Renvoyer l\'email de confirmation'}
                        </button>

                        <div className="pt-4">
                            <Link
                                to="/signin"
                                className="text-gray-500 hover:text-gray-700 font-bold flex items-center justify-center gap-2 transition-colors"
                            >
                                <ArrowRight size={18} className="rotate-180" />
                                Retour à la connexion
                            </Link>
                        </div>
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
