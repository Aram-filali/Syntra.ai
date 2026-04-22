import { useEffect, useState } from 'react';
import { X, Mail, Loader2, Check, AlertCircle } from 'lucide-react';

export default function ShareModal({
    isOpen,
    onClose,
    onShare,
    meetingTitle,
    isLoading,
    initialEmails = []
}) {
    const [emails, setEmails] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        if (!isOpen) return;
        setError(null);
        setSuccess(false);

        const uniqueEmails = [...new Set((initialEmails || []).map((e) => e.trim().toLowerCase()))];
        setEmails(uniqueEmails.join(', '));
    }, [isOpen, initialEmails]);

    const validateEmails = (emailString) => {
        if (!emailString.trim()) {
            setError('Veuillez entrer au moins une adresse email');
            return false;
        }

        const emailList = emailString
            .split(',')
            .map(email => email.trim())
            .filter(email => email.length > 0);

        for (let email of emailList) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                setError(`Format d'email invalide: ${email}`);
                return false;
            }
        }

        if (emailList.length === 0) {
            setError('Au moins une adresse email valide requise');
            return false;
        }

        return emailList;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(false);

        const emailList = validateEmails(emails);
        if (!emailList) return;

        try {
            await onShare(emailList);
            setSuccess(true);
            setEmails('');
            
            // Close after 2 seconds
            setTimeout(() => {
                onClose();
                setSuccess(false);
            }, 2000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Erreur lors du partage');
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/20 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative bg-white rounded-3xl shadow-2xl w-full max-w-md p-8 border border-gray-100">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600">
                            <Mail size={20} />
                        </div>
                        <h2 className="text-2xl font-black text-gray-900">Partager</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 transition-colors"
                    >
                        <X size={24} />
                    </button>
                </div>

                {/* Meeting Title */}
                <p className="text-sm text-gray-600 font-medium mb-6">
                    Partager : <span className="font-black text-indigo-600">{meetingTitle}</span>
                </p>

                {initialEmails.length > 0 && (
                    <div className="mb-6 p-4 bg-emerald-50 border border-emerald-200 rounded-xl">
                        <p className="text-xs text-emerald-800 font-bold uppercase tracking-widest">Participants détectés</p>
                        <p className="text-sm text-emerald-700 mt-1">
                            {initialEmails.length} email(s) pré-rempli(s). Vous pouvez modifier la liste avant l'envoi.
                        </p>
                    </div>
                )}

                {/* Success State */}
                {success && (
                    <div className="mb-6 p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex gap-3">
                        <Check className="text-emerald-600 flex-shrink-0" size={20} />
                        <div>
                            <p className="font-black text-emerald-900 text-sm">Partage réussi !</p>
                            <p className="text-xs text-emerald-700 mt-1">L'email a été envoyé avec succès.</p>
                        </div>
                    </div>
                )}

                {/* Error State */}
                {error && !success && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex gap-3">
                        <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
                        <div>
                            <p className="font-black text-red-900 text-sm">Erreur</p>
                            <p className="text-xs text-red-700 mt-1">{error}</p>
                        </div>
                    </div>
                )}

                {/* Form */}
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-xs font-black text-indigo-600 uppercase tracking-widest mb-2">
                            Adresses Email
                        </label>
                        <textarea
                            value={emails}
                            onChange={(e) => {
                                setEmails(e.target.value);
                                setError(null);
                            }}
                            placeholder="email1@example.com, email2@example.com"
                            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all resize-none"
                            rows="4"
                        />
                        <p className="text-xs text-gray-500 mt-2">
                            Séparez les emails par des virgules
                        </p>
                    </div>

                    {/* Buttons */}
                    <div className="flex gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-3 bg-gray-100 text-gray-700 font-black rounded-xl hover:bg-gray-200 transition-colors disabled:opacity-50"
                            disabled={isLoading}
                        >
                            Annuler
                        </button>
                        <button
                            type="submit"
                            disabled={isLoading || !emails.trim()}
                            className="flex-1 px-4 py-3 bg-indigo-600 text-white font-black rounded-xl hover:bg-indigo-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 size={18} className="animate-spin" />
                                    Envoi...
                                </>
                            ) : (
                                <>
                                    <Mail size={18} />
                                    Partager
                                </>
                            )}
                        </button>
                    </div>
                </form>

                {/* Info Box */}
                <div className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-100">
                    <p className="text-xs text-blue-700 font-medium leading-relaxed">
                        💡 Le meeting sera partagé avec un lien cliquable et un résumé complet. Les destinataires n'ont pas besoin d'un compte Syntra.ai.
                    </p>
                </div>
            </div>
        </div>
    );
}
