import { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { X, Loader2, Calendar, FileText, CheckCircle, Sparkles, Video, Plus } from 'lucide-react';
import { meetingsAPI, zoomAPI } from '../api/client';
import ErrorMessage from '../components/ErrorMessage';

export default function CreateMeeting() {
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        title: '',
        scheduled_time: '',
        duration_minutes: 60,
    });
    const [uploadFile, setUploadFile] = useState(null);

    const [loading, setLoading] = useState(false);
    const [isCreating, setIsCreating] = useState(false);
    const [analyzing, setAnalyzing] = useState(false);
    const [analysisDone, setAnalysisDone] = useState(false);
    const [createdMeetingId, setCreatedMeetingId] = useState(null);
    const [error, setError] = useState(null);
    const [notifications, setNotifications] = useState([
        { id: 1, visible: false, type: 'tip' },
        { id: 2, visible: false, type: 'ai' }
    ]);
    const [zoomLoading, setZoomLoading] = useState(false);

    const [zoomAccountType, setZoomAccountType] = useState(null);
    const [loadingZoomType, setLoadingZoomType] = useState(true);

    const location = useLocation();

    // Check for Zoom import data
    useEffect(() => {
        if (location.state?.zoomData) {
            const { title, scheduled_time, duration_minutes } = location.state.zoomData;
            setFormData(prev => ({
                ...prev,
                title: title || '',
                scheduled_time: scheduled_time ? scheduled_time.slice(0, 16) : '',
                duration_minutes: duration_minutes || 60
            }));
        }
    }, [location.state]);

    // Fetch Zoom account type
    useEffect(() => {
        const fetchZoomAccountType = async () => {
            setLoadingZoomType(true);
            try {
                const type = await zoomAPI.getAccountType();
                setZoomAccountType(type);
            } catch (err) {
                // User might not have Zoom connected yet, that's ok
                console.debug("Zoom account type not available yet");
                setZoomAccountType(null);
            } finally {
                setLoadingZoomType(false);
            }
        };

        fetchZoomAccountType();
    }, []);

    // Show notifications after 5 seconds, auto-hide after 30 seconds
    useEffect(() => {
        const showTimer = setTimeout(() => {
            setNotifications(prev => prev.map(n => ({ ...n, visible: true })));
        }, 5000);

        const hideTimer = setTimeout(() => {
            setNotifications(prev => prev.map(n => ({ ...n, visible: false })));
        }, 35000); // 5s + 30s

        return () => {
            clearTimeout(showTimer);
            clearTimeout(hideTimer);
        };
    }, []);

    const dismissNotification = (id) => {
        setNotifications(prev => prev.map(n =>
            n.id === id ? { ...n, visible: false } : n
        ));
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleZoomConnect = async () => {
        setZoomLoading(true);
        setError(null);
        console.log("Initiating Zoom connection...");
        try {
            const url = await zoomAPI.getLoginUrl();
            console.log("Redirecting to Zoom:", url);
            window.location.href = url;
        } catch (err) {
            console.error("Zoom connection error:", err);
            setError("Impossible d'initier la connexion Zoom. Vérifiez que le backend est lancé.");
            setZoomLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setIsCreating(true);
        setError(null);

        try {
            if (uploadFile) {
                // Création avec fichier
                const submitData = new FormData();
                submitData.append('title', formData.title);
                submitData.append('scheduled_time', formData.scheduled_time);
                submitData.append('duration_minutes', formData.duration_minutes);
                submitData.append('file', uploadFile);

                const meeting = await meetingsAPI.createWithFile(submitData);
                setCreatedMeetingId(meeting.id);
                // On va à la page de détails pour voir la progression
                navigate(`/meetings/${meeting.id}`);
            } else {
                // Création simple sans fichier (comme avant mais sans transcription)
                const meeting = await meetingsAPI.create({
                    title: formData.title,
                    scheduled_time: formData.scheduled_time,
                    duration_minutes: parseInt(formData.duration_minutes),
                });
                navigate(`/meetings/${meeting.id}`);
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Erreur lors de la création du meeting');
        } finally {
            setLoading(false);
            setIsCreating(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#fafafa] relative overflow-hidden">
            {/* Modal de Création / Upload */}
            {isCreating && (
                <div className="fixed inset-0 z-[110] flex items-center justify-center p-4">
                    <div className="absolute inset-0 bg-indigo-900/10 backdrop-blur-2xl"></div>
                    <div className="relative bg-white/80 backdrop-blur-xl rounded-[40px] shadow-2xl border border-white p-12 max-w-lg w-full text-center animate-scale-up">
                        <div className="relative w-24 h-24 mx-auto mb-8">
                            <div className="absolute inset-0 bg-indigo-500/20 rounded-full animate-ping"></div>
                            <div className="relative w-24 h-24 bg-gradient-to-br from-indigo-600 to-purple-700 rounded-full flex items-center justify-center shadow-xl">
                                <Video className="w-12 h-12 text-white animate-pulse" />
                            </div>
                        </div>
                        <h2 className="text-3xl font-black text-gray-900 mb-4 tracking-tight uppercase">Création en cours</h2>
                        <p className="text-gray-500 font-medium leading-relaxed mb-8">
                            Nous préparons votre espace de réunion et sécurisons vos fichiers sur nos serveurs.
                        </p>
                        <div className="flex flex-col items-center gap-4">
                            <div className="w-full h-3 bg-indigo-50 rounded-full overflow-hidden p-1 border border-indigo-100/50">
                                <div className="h-full bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full animate-shimmer" style={{ width: '100%', backgroundSize: '200% 100%' }}></div>
                            </div>
                            <span className="text-[10px] font-black text-indigo-600 uppercase tracking-[0.3em]">Initialisation sécurisée...</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Modal d'Analyse */}
            {(analyzing || analysisDone) && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                    <div className="absolute inset-0 bg-white/40 backdrop-blur-xl transition-all duration-500"></div>

                    <div className="relative bg-white rounded-[40px] shadow-2xl border border-indigo-100 p-10 max-w-lg w-full text-center transform animate-float transition-all duration-500 scale-100">
                        {!analysisDone ? (
                            <>
                                <div className="relative w-24 h-24 mx-auto mb-8">
                                    <div className="absolute inset-0 bg-indigo-500/20 rounded-full animate-ping"></div>
                                    <div className="relative w-24 h-24 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-xl">
                                        <Sparkles className="w-12 h-12 text-white animate-pulse" />
                                    </div>
                                </div>
                                <h2 className="text-3xl font-black text-gray-900 mb-4 tracking-tight">Analyse IA en cours</h2>
                                <p className="text-gray-500 font-medium leading-relaxed mb-8">
                                    Notre intelligence artificielle extrait les points clés, les décisions et les prochaines actions de votre réunion.
                                </p>
                                <div className="flex flex-col items-center gap-4">
                                    <div className="w-full h-2 bg-indigo-50 rounded-full overflow-hidden">
                                        <div className="h-full bg-indigo-600 rounded-full animate-shimmer" style={{ width: '60%', backgroundSize: '200% 100%' }}></div>
                                    </div>
                                    <span className="text-xs font-black text-indigo-600 uppercase tracking-widest">Traitement intelligent...</span>
                                </div>
                            </>
                        ) : (
                            <>
                                <div className="w-24 h-24 bg-emerald-500 rounded-full flex items-center justify-center mx-auto mb-8 shadow-xl shadow-emerald-100">
                                    <CheckCircle className="w-14 h-14 text-white" />
                                </div>
                                <h2 className="text-3xl font-black text-gray-900 mb-4 tracking-tight">Analyse Terminée !</h2>
                                <p className="text-gray-500 font-medium leading-relaxed mb-10">
                                    Votre compte-rendu est prêt. Vous pouvez maintenant consulter le résumé et le plan d'action généré.
                                </p>
                                <button
                                    onClick={() => navigate(`/meetings/${createdMeetingId}`, { state: { openSummary: true } })}
                                    className="w-full py-5 bg-indigo-600 text-white rounded-2xl font-black text-lg shadow-xl shadow-indigo-200 hover:scale-105 transition-all flex items-center justify-center gap-3"
                                >
                                    VOIR LE RÉSUMÉ
                                    <span className="text-2xl">→</span>
                                </button>
                            </>
                        )}
                    </div>
                </div>
            )}

            {/* Toast Notifications - Top Right */}
            <div className="fixed top-8 right-4 z-50 space-y-3 max-w-sm">
                {notifications[0].visible && (
                    <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-xl animate-slide-in-right">
                        <div className="flex items-start justify-between">
                            <div className="flex-1">
                                <p className="text-xs text-gray-600 font-medium">
                                    Vous pouvez créer le meeting maintenant et uploader l'enregistrement plus tard. L'IA lancera l'analyse automatiquement après l'upload.
                                </p>
                            </div>
                            <button
                                onClick={() => dismissNotification(1)}
                                className="ml-3 text-gray-400 hover:text-gray-600 transition-colors flex-shrink-0"
                            >
                                <X size={18} />
                            </button>
                        </div>
                    </div>
                )}

                {notifications[1].visible && (
                    <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-xl animate-slide-in-right animation-delay-200">
                        <div className="flex items-start justify-between">
                            <div className="flex-1">
                                <p className="text-xs text-gray-600 font-medium">
                                    Notre IA analyse l'audio de votre réunion pour extraire les tâches, décisions et points clés automatiquement.
                                </p>
                            </div>
                            <button
                                onClick={() => dismissNotification(2)}
                                className="ml-3 text-gray-400 hover:text-gray-600 transition-colors flex-shrink-0"
                            >
                                <X size={18} />
                            </button>
                        </div>
                    </div>
                )}
            </div>

            <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                {/* Header Section */}
                <div className="mb-12">
                    <Link
                        to="/dashboard"
                        className="inline-flex items-center text-sm font-bold text-indigo-600 hover:text-indigo-700 mb-8 transition-all group"
                    >
                        <span className="mr-2 transform group-hover:-translate-x-1 transition-transform">←</span>
                        Retour au tableau de bord
                    </Link>

                    <div className="text-left">
                        <h1 className="text-4xl font-black text-gray-900 mb-4 tracking-tight">
                            Nouveau <span className="text-indigo-600">Meeting</span>
                        </h1>
                        <p className="text-base text-gray-500 font-medium max-w-2xl leading-relaxed">
                            Configurez votre réunion et préparez l'analyse IA.
                        </p>
                    </div>
                </div>

                {error && (
                    <div className="mb-8">
                        <ErrorMessage message={error} />
                    </div>
                )}

                {/* Main Form/Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                    <form onSubmit={handleSubmit} className="lg:col-span-2 space-y-10">
                        {/* Meeting Details Card */}
                        <div className="bg-white rounded-3xl border border-gray-100 p-10 shadow-sm">
                            <h2 className="text-2xl font-black text-gray-900 mb-8 flex items-center gap-4">
                                <div className="w-12 h-12 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 shadow-sm">
                                    <Calendar size={24} />
                                </div>
                                Informations de base
                            </h2>

                            <div className="space-y-8">
                                <div>
                                    <label htmlFor="title" className="block text-xs font-black text-indigo-500 mb-3 uppercase tracking-[0.2em]">
                                        Nom de la réunion
                                    </label>
                                    <input
                                        type="text"
                                        id="title"
                                        name="title"
                                        value={formData.title}
                                        onChange={handleChange}
                                        required
                                        className="input-field py-4 text-lg font-bold"
                                        placeholder="Ex: Weekly Sync - Design Team"
                                    />
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                    <div>
                                        <label htmlFor="scheduled_time" className="block text-xs font-black text-indigo-500 mb-3 uppercase tracking-[0.2em]">
                                            Date et Heure
                                        </label>
                                        <input
                                            type="datetime-local"
                                            id="scheduled_time"
                                            name="scheduled_time"
                                            value={formData.scheduled_time}
                                            onChange={handleChange}
                                            required
                                            className="input-field py-4 font-bold"
                                        />
                                    </div>

                                    <div>
                                        <label htmlFor="duration_minutes" className="block text-xs font-black text-indigo-500 mb-3 uppercase tracking-[0.2em]">
                                            Durée (min)
                                        </label>
                                        <input
                                            type="number"
                                            id="duration_minutes"
                                            name="duration_minutes"
                                            value={formData.duration_minutes}
                                            onChange={handleChange}
                                            min="1"
                                            className="input-field py-4 font-bold"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Upload Card */}
                        <div className="bg-white rounded-3xl border border-gray-100 p-10 shadow-sm">
                            <div className="flex justify-between items-center mb-8">
                                <h2 className="text-2xl font-black text-gray-900 flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 shadow-sm">
                                        <Video className="w-6 h-6" />
                                    </div>
                                    Fichier de Réunion
                                </h2>
                                <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest bg-gray-50 px-4 py-2 rounded-xl">
                                    Audio ou Vidéo
                                </span>
                            </div>

                            <div className="mb-8 p-6 bg-indigo-50/50 rounded-2xl border border-indigo-100">
                                <div className="flex gap-4">
                                    <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center text-indigo-600 shadow-sm flex-shrink-0">
                                        <Sparkles size={20} className="animate-pulse" />
                                    </div>
                                    <p className="text-sm text-gray-600 leading-relaxed font-medium">
                                        Notre <span className="font-black text-indigo-900 uppercase text-[10px]">Analyse IA</span> transcrira automatiquement votre fichier pour en extraire l'intelligence.
                                    </p>
                                </div>
                            </div>

                            <div
                                onClick={() => document.getElementById('meeting-file-upload').click()}
                                className={`group relative border-2 border-dashed rounded-[2rem] p-12 flex flex-col items-center justify-center transition-all cursor-pointer ${uploadFile ? 'border-emerald-400 bg-emerald-50/30' : 'border-gray-100 hover:border-indigo-400 hover:bg-indigo-50/30'}`}
                            >
                                <input
                                    id="meeting-file-upload"
                                    type="file"
                                    className="hidden"
                                    accept="video/*,audio/*"
                                    onChange={(e) => setUploadFile(e.target.files[0])}
                                />
                                <div className={`w-20 h-20 rounded-3xl flex items-center justify-center mb-6 shadow-xl transition-transform group-hover:scale-110 ${uploadFile ? 'bg-emerald-500 text-white' : 'bg-white text-indigo-600'}`}>
                                    {uploadFile ? <CheckCircle size={40} /> : <Plus size={40} />}
                                </div>
                                <h4 className="text-xl font-black text-gray-900 mb-2">
                                    {uploadFile ? uploadFile.name : 'Déposez votre enregistrement'}
                                </h4>
                                <p className="text-sm text-gray-500 font-medium text-center max-w-xs leading-relaxed">
                                    {uploadFile
                                        ? `Taille: ${(uploadFile.size / (1024 * 1024)).toFixed(2)} MB • Cliquez pour changer`
                                        : 'Cliquez ou glissez-déposez votre fichier MP4, MP3, WAV ou M4A'}
                                </p>

                                {uploadFile && (
                                    <div className="mt-8 flex items-center gap-3">
                                        <div className="flex items-center gap-2 text-[10px] font-black uppercase text-emerald-600 bg-white px-3 py-1.5 rounded-xl shadow-sm border border-emerald-100">
                                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                            FICHIER PRÊT
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex items-center gap-6 pt-4">
                            <button
                                type="submit"
                                disabled={loading}
                                className="flex-grow py-5 bg-indigo-600 text-white rounded-3xl font-black text-xl shadow-2xl shadow-indigo-100 hover:shadow-indigo-200 transition-all active:scale-[0.98] flex items-center justify-center gap-3"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 size={24} className="animate-spin" />
                                        <span>PRÉPARATION...</span>
                                    </>
                                ) : (
                                    <>
                                        <span>CRÉER LE MEETING</span>
                                        <Sparkles size={24} />
                                    </>
                                )}
                            </button>
                            <Link
                                to="/dashboard"
                                className="px-10 py-5 bg-gray-50 text-gray-500 font-black rounded-3xl hover:bg-gray-100 transition-all uppercase tracking-widest text-xs"
                            >
                                Annuler
                            </Link>
                        </div>
                    </form>

                    {/* Sidebar / Integrations */}
                    <div className="space-y-8">
                        <div className="bg-indigo-900 rounded-[40px] p-10 text-white relative overflow-hidden group shadow-2xl shadow-indigo-100">
                            <div className="absolute -right-10 -top-10 w-40 h-40 bg-white/10 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700" />
                            <h3 className="text-2xl font-black mb-6 flex items-center gap-3 relative">
                                <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                                    <Sparkles size={20} className="text-white" />
                                </div>
                                Zoom Sync
                            </h3>
                            
                            {zoomAccountType === 'basic' && (
                                <div className="mb-6 p-4 bg-yellow-400/20 border border-yellow-300/50 rounded-2xl">
                                    <p className="text-sm text-yellow-100 font-medium leading-relaxed">
                                        ⚠️ Votre compte Zoom Basic ne permet pas l'accès au Cloud. Veuillez uploader l'enregistrement local (MP4/MP3) ci-dessous.
                                    </p>
                                </div>
                            )}
                            
                            <p className="text-indigo-200 font-medium leading-relaxed mb-8 relative">
                                {zoomAccountType === 'basic'
                                    ? 'Pour synchroniser automatiquement vos réunions, vous avez besoin d\'un compte Zoom Pro ou Business.'
                                    : 'Connectez votre compte Zoom pour synchroniser vos réunions automatiquement.'}
                            </p>
                            <button
                                onClick={handleZoomConnect}
                                type="button"
                                disabled={zoomLoading || zoomAccountType === 'basic'}
                                className={`w-full py-4 font-black rounded-2xl text-sm shadow-xl transition-all active:scale-95 relative flex items-center justify-center gap-3 ${
                                    zoomAccountType === 'basic'
                                        ? 'bg-gray-400 text-gray-600 cursor-not-allowed opacity-50'
                                        : 'bg-white text-indigo-900 hover:bg-indigo-50'
                                }`}
                            >
                                {zoomLoading ? (
                                    <>
                                        <Loader2 size={18} className="animate-spin" />
                                        <span>CONNEXION...</span>
                                    </>
                                ) : zoomAccountType === 'basic' ? (
                                    "ZOOM BASIC (Non supporté)"
                                ) : (
                                    "ACTIVER MAINTENANT"
                                )}
                            </button>
                            <div className="mt-6 flex items-center gap-3 relative">
                                <span className={`w-2 h-2 rounded-full animate-pulse ${
                                    zoomAccountType === 'basic' ? 'bg-yellow-400' : 'bg-emerald-400'
                                }`} />
                                <span className="text-[10px] font-black text-indigo-300 uppercase tracking-[0.2em]">
                                    {zoomAccountType === 'basic' ? 'Compte Basic' : 'Disponible'}
                                </span>
                            </div>
                        </div>

                        <div className="bg-white rounded-[40px] p-10 border border-gray-100 shadow-sm">
                            <h3 className="text-xl font-black text-gray-900 mb-8 uppercase tracking-widest text-xs">Aide & Astuces</h3>
                            <ul className="space-y-6">
                                <li className="flex gap-4">
                                    <div className="w-6 h-6 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center flex-shrink-0 text-xs font-black">1</div>
                                    <p className="text-sm text-gray-500 font-medium leading-relaxed italic">"Uploadez votre enregistrement brut, notre IA s'occupe de la transcription et de la mise en forme."</p>
                                </li>
                                <li className="flex gap-4">
                                    <div className="w-6 h-6 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center flex-shrink-0 text-xs font-black">2</div>
                                    <p className="text-sm text-gray-500 font-medium leading-relaxed italic">"Plus la qualité audio est bonne, plus l'analyse sera précise."</p>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
