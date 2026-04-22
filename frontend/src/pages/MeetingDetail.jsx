import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import { ArrowLeft, Loader2, X, Maximize2, FileDown, Download, ListChecks, FileText, Send, Sparkles, Video, Calendar, Users, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { meetingsAPI, createPolling } from '../api/client';
import ActionItem from '../components/ActionItem';
import TranscriptionViewer from '../components/TranscriptionViewer';
import ShareModal from '../components/ShareModal';
import ParticipantsPanel from '../components/ParticipantsPanel';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function MeetingDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const location = useLocation();

    const [meeting, setMeeting] = useState(null);
    const [transcription, setTranscription] = useState(null);
    const [summary, setSummary] = useState(null);
    const [actions, setActions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [analyzing, setAnalyzing] = useState(false);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('summary');
    const [newTranscription, setNewTranscription] = useState('');
    const [savingTranscription, setSavingTranscription] = useState(false);
    const [isShareModalOpen, setIsShareModalOpen] = useState(false);
    const [isSharing, setIsSharing] = useState(false);
    const [directShareSuccess, setDirectShareSuccess] = useState(false);

    // Ref for polling management
    const pollingRef = useRef(null);

    useEffect(() => {
        fetchMeetingData();

        // Setup polling - polls every 10 seconds while analysis is in progress
        pollingRef.current = createPolling(
            async () => {
                const meetingData = await meetingsAPI.getById(id);
                setMeeting(meetingData);

                if (meetingData.has_transcription) {
                    const transcriptionData = await meetingsAPI.getTranscription(id);
                    setTranscription(transcriptionData);
                }

                if (meetingData.has_summary) {
                    const summaryData = await meetingsAPI.getSummary(id);
                    setSummary(summaryData);

                    const actionsData = await meetingsAPI.getActions(id);
                    setActions(actionsData);
                }

                return meetingData;
            },
            (meetingData) => {
                // Continue polling if analysis is not done yet
                return !meetingData.has_summary && meetingData.status !== 'cancelled';
            },
            10000, // Poll every 10 seconds
            Infinity // Retry indefinitely
        );

        // Cleanup on unmount
        return () => {
            if (pollingRef.current?.stop) {
                pollingRef.current.stop();
            }
        };
    }, [id]);

    useEffect(() => {
        if (location.state?.openSummary && !loading && summary) {
            handleExportPDF();
            // Clear the state so it doesn't trigger again on refresh
            window.history.replaceState({}, document.title);
        }
    }, [location.state, loading, summary]);

    const fetchMeetingData = async () => {
        setLoading(true);
        setError(null);

        try {
            const meetingData = await meetingsAPI.getById(id);
            setMeeting(meetingData);

            if (meetingData.has_transcription) {
                const transcriptionData = await meetingsAPI.getTranscription(id);
                setTranscription(transcriptionData);
            }

            if (meetingData.has_summary) {
                const summaryData = await meetingsAPI.getSummary(id);
                setSummary(summaryData);

                const actionsData = await meetingsAPI.getActions(id);
                setActions(actionsData);
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Erreur lors du chargement');
        } finally {
            setLoading(false);
        }
    };

    const handleAnalyze = async () => {
        setAnalyzing(true);
        setError(null);

        try {
            await meetingsAPI.analyze(id);
            await fetchMeetingData();
        } catch (err) {
            setError(err.response?.data?.detail || 'Erreur lors de l\'analyse');
        } finally {
            setAnalyzing(false);
        }
    };

    const handleActionStatusChange = (actionId, newStatus) => {
        setActions((prevActions) =>
            prevActions.map((action) =>
                action.id === actionId ? { ...action, status: newStatus } : action
            )
        );
    };

    const handleExportPDF = () => {
        window.print();
    };

    const handleSaveTranscription = async () => {
        if (!newTranscription.trim()) return;
        setSavingTranscription(true);
        try {
            await meetingsAPI.addTranscription(id, {
                full_text: newTranscription,
                speaker_segments: {},
            });
            await fetchMeetingData();
            setActiveTab('actions');
        } catch (err) {
            setError(err.response?.data?.detail || 'Erreur lors de l\'ajout');
        } finally {
            setSavingTranscription(false);
        }
    };

    const handleDownloadTranscription = () => {
        if (transcription) {
            const blob = new Blob([transcription.full_text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `transcription-${meeting.title}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    };

    const handleShare = async (recipientEmails) => {
        setIsSharing(true);
        try {
            await meetingsAPI.shareMeeting(id, recipientEmails);
            // Success is shown in the modal
        } catch (err) {
            throw err;
        } finally {
            setIsSharing(false);
        }
    };

    const handleDirectShare = async () => {
        if (participantEmails.length === 0) return;
        setIsSharing(true);
        setDirectShareSuccess(false);
        try {
            await meetingsAPI.shareMeeting(id, participantEmails);
            setDirectShareSuccess(true);
            setTimeout(() => setDirectShareSuccess(false), 3000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Erreur lors de l\'envoi aux participants');
        } finally {
            setIsSharing(false);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return '--';
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            day: '2-digit',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const completedActions = actions.filter(a => a.status === 'completed').length;
    const progressPercentage = actions.length > 0 ? (completedActions / actions.length) * 100 : 0;

    const participantEmails = (meeting?.participants || [])
        .map((participant) => {
            if (participant && typeof participant === 'object') {
                return participant.email || null;
            }
            if (typeof participant === 'string' && participant.includes('@')) {
                return participant;
            }
            return null;
        })
        .filter(Boolean);

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-50/40 via-white to-purple-50/40">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                    <LoadingSpinner message="Chargement du meeting..." />
                </div>
            </div>
        );
    }

    if (analyzing) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-50/40 via-white to-purple-50/40 flex flex-col items-center justify-center p-8">
                <div className="w-24 h-24 bg-white rounded-3xl shadow-xl flex items-center justify-center mb-8">
                    <Loader2 size={48} className="text-indigo-600 animate-spin" />
                </div>
                <h2 className="text-4xl font-black text-gray-900 mb-4 animate-pulse uppercase tracking-tighter">L'IA extrait l'intelligence...</h2>
                <div className="max-w-md text-center">
                    <p className="text-gray-500 font-medium leading-relaxed">
                        Nous analysons chaque seconde de votre réunion pour en extraire l'essentiel.
                    </p>
                </div>
            </div>
        );
    }

    if (!meeting) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-50/40 via-white to-purple-50/40">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                    <ErrorMessage message="Meeting introuvable" />
                </div>
            </div>
        );
    }

    return (
        <>
            <style>{`
                @media print {
                    @page { margin: 2cm; }
                    body * { visibility: hidden !important; }
                    #print-content, #print-content * { visibility: visible !important; }
                    #print-content {
                        position: absolute; left: 0; top: 0; width: 100%; background: white; padding: 0; margin: 0; display: block !important;
                    }
                    .print-header { border-bottom: 3px solid #4f46e5; padding-bottom: 20px; margin-bottom: 30px; display: block !important; }
                    .print-title { font-size: 24pt; font-weight: 800; color: #111827; margin: 0 0 8px 0; }
                    .print-meta { font-size: 11pt; color: #6b7280; }
                    #print-content .prose { max-width: none !important; display: block !important; }
                    #print-content h1 { font-size: 22pt !important; font-weight: 800 !important; margin: 30pt 0 15pt 0 !important; border-bottom: 1pt solid #eee !important; padding-bottom: 5pt !important; }
                    #print-content h2 { font-size: 18pt !important; font-weight: 700 !important; margin: 25pt 0 12pt 0 !important; }
                    #print-content p { font-size: 11pt !important; line-height: 1.6 !important; margin-bottom: 12pt !important; }
                    #print-content ul, #print-content ol { margin: 10pt 0 20pt 0 !important; padding-left: 25pt !important; }
                    #print-content li { font-size: 11pt !important; margin-bottom: 6pt !important; }
                }
            `}</style>

            <div className="min-h-screen bg-gradient-to-br from-indigo-50/40 via-white to-purple-50/40 print:bg-white pb-20">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 print:hidden">
                    <Link
                        to="/dashboard"
                        className="inline-flex items-center text-sm font-bold text-indigo-600 hover:text-indigo-700 mb-8 transition-all group"
                    >
                        <span className="mr-2 transform group-hover:-translate-x-1 transition-transform">←</span>
                        Retour au tableau de bord
                    </Link>

                    {/* Header Card */}
                    <div className="bg-white rounded-[2.5rem] p-10 border border-indigo-100 shadow-xl shadow-indigo-100/20 mb-10 overflow-hidden relative">
                        <div className="absolute top-0 right-0 p-10 opacity-5">
                            <Video size={120} />
                        </div>

                        <div className="relative z-10 flex flex-col xl:flex-row justify-between items-center gap-10">
                            <div className="flex-grow text-center xl:text-left">
                                <span className={`inline-block px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] mb-4 ${summary ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
                                    }`}>
                                    {summary ? '✓ Intelligence extraite' : '⚡ En attente d\'analyse'}
                                </span>
                                <h1 className="text-5xl font-black text-gray-900 mb-6 leading-tight max-w-3xl">{meeting.title}</h1>

                                <div className="flex flex-wrap items-center justify-center xl:justify-start gap-4 text-xs font-bold text-gray-500 mb-8">
                                    <div className="flex items-center gap-2 bg-gray-50 px-4 py-2 rounded-xl border border-gray-100 italic">
                                        <Calendar size={14} />
                                        <span>{formatDate(meeting.scheduled_time)}</span>
                                    </div>
                                    <div className="flex items-center gap-2 bg-gray-50 px-4 py-2 rounded-xl border border-gray-100 italic">
                                        <Loader2 size={14} />
                                        <span>{meeting.duration_minutes || '--'} min</span>
                                    </div>
                                </div>

                                {/* Stats */}
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-8 border-t border-gray-100">
                                    <div className="text-center">
                                        <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Actions</p>
                                        <p className="text-lg font-black text-gray-900">{actions.length}</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Progression</p>
                                        <p className="text-lg font-black text-indigo-600">{Math.round(progressPercentage)}%</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Complétées</p>
                                        <p className="text-lg font-black text-gray-900">{completedActions}</p>
                                    </div>
                                </div>
                            </div>

                            <div className="flex flex-col gap-4 w-full xl:w-auto xl:min-w-[280px]">
                                {transcription && !summary && (
                                    <button
                                        onClick={handleAnalyze}
                                        disabled={analyzing}
                                        className="group w-full py-5 px-8 bg-blue-600 text-white rounded-[1.5rem] font-black text-sm uppercase tracking-widest hover:bg-blue-700 transition-all flex items-center justify-center gap-3 shadow-2xl shadow-blue-200 hover:scale-105 active:scale-95"
                                    >
                                        <Sparkles size={20} className="group-hover:rotate-12 transition-transform" />
                                        Lancer l'Analyse IA
                                    </button>
                                )}

                                {summary && (
                                    <>
                                        {participantEmails.length > 0 && (
                                            <button
                                                onClick={handleDirectShare}
                                                disabled={isSharing}
                                                className={`w-full py-5 px-8 ${directShareSuccess ? 'bg-emerald-600' : 'bg-emerald-500'} text-white rounded-[1.5rem] font-black text-sm uppercase tracking-widest hover:bg-emerald-600 transition-all flex items-center justify-center gap-3 shadow-2xl shadow-emerald-200 hover:scale-105 active:scale-95`}
                                            >
                                                {isSharing ? (
                                                    <Loader2 size={20} className="animate-spin" />
                                                ) : directShareSuccess ? (
                                                    <Check size={20} />
                                                ) : (
                                                    <Users size={20} />
                                                )}
                                                {directShareSuccess ? 'Envoyé !' : `Envoyer aux ${participantEmails.length} participants`}
                                            </button>
                                        )}
                                        <button
                                            onClick={() => setIsShareModalOpen(true)}
                                            className="w-full py-5 px-8 bg-indigo-600 text-white rounded-[1.5rem] font-black text-sm uppercase tracking-widest hover:bg-indigo-700 transition-all flex items-center justify-center gap-3 shadow-2xl shadow-indigo-200 hover:scale-105 active:scale-95"
                                        >
                                            <Send size={20} />
                                            Partager par email
                                        </button>
                                        <button
                                            onClick={handleExportPDF}
                                            className="w-full py-4 px-8 bg-gray-100 text-gray-700 rounded-[1.5rem] font-black text-xs uppercase tracking-widest hover:bg-gray-200 transition-all flex items-center justify-center gap-2"
                                        >
                                            <FileDown size={16} />
                                            Imprimer/PDF
                                        </button>
                                    </>
                                )}

                                {transcription && (
                                    <button
                                        onClick={handleDownloadTranscription}
                                        className="w-full py-4 px-8 bg-white text-gray-400 rounded-[1.5rem] font-black text-[10px] uppercase tracking-widest hover:text-gray-900 border border-gray-100 hover:border-gray-200 transition-all flex items-center justify-center gap-2"
                                    >
                                        <Download size={14} />
                                        Transcription brute
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="mb-10">
                            <ErrorMessage message={error} />
                        </div>
                    )}

                    {/* Main Content */}
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                        {/* Tabs */}
                        <div className="lg:col-span-1 space-y-3">
                            <button
                                onClick={() => setActiveTab('summary')}
                                className={`w-full px-6 py-5 rounded-2xl font-black text-xs uppercase tracking-widest transition-all flex items-center gap-4 ${activeTab === 'summary'
                                    ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-100'
                                    : 'bg-white text-gray-400 hover:bg-indigo-50 border border-indigo-100 hover:text-indigo-600'
                                    }`}
                            >
                                <Sparkles size={18} />
                                <span className="flex-grow text-left">Résumé IA</span>
                                {summary && (
                                    <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                                )}
                            </button>

                            <button
                                onClick={() => setActiveTab('actions')}
                                className={`w-full px-6 py-5 rounded-2xl font-black text-xs uppercase tracking-widest transition-all flex items-center gap-4 ${activeTab === 'actions'
                                    ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-100'
                                    : 'bg-white text-gray-400 hover:bg-indigo-50 border border-indigo-100 hover:text-indigo-600'
                                    }`}
                            >
                                <ListChecks size={18} />
                                <span className="flex-grow text-left">Plan d'action</span>
                                {actions.length > 0 && (
                                    <span className={`text-[10px] px-2 py-1 rounded-lg font-black ${activeTab === 'actions' ? 'bg-white/20 text-white' : 'bg-indigo-100 text-indigo-600'
                                        }`}>
                                        {actions.length}
                                    </span>
                                )}
                            </button>
                            <button
                                onClick={() => setActiveTab('transcription')}
                                className={`w-full px-6 py-5 rounded-2xl font-black text-xs uppercase tracking-widest transition-all flex items-center gap-4 ${activeTab === 'transcription'
                                    ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-100'
                                    : 'bg-white text-gray-400 hover:bg-indigo-50 border border-indigo-100 hover:text-indigo-600'
                                    }`}
                            >
                                <FileText size={18} />
                                <span className="flex-grow text-left">Transcription</span>
                                {!transcription && (
                                    <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
                                )}
                            </button>

                            <button
                                onClick={() => setActiveTab('participants')}
                                className={`w-full px-6 py-5 rounded-2xl font-black text-xs uppercase tracking-widest transition-all flex items-center gap-4 ${activeTab === 'participants'
                                    ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-100'
                                    : 'bg-white text-gray-400 hover:bg-indigo-50 border border-indigo-100 hover:text-indigo-600'
                                    }`}
                            >
                                <Users size={18} />
                                <span className="flex-grow text-left">Participants</span>
                                {meeting?.participants?.length > 0 && (
                                    <span className={`text-[10px] px-2 py-1 rounded-lg font-black ${activeTab === 'participants' ? 'bg-white/20 text-white' : 'bg-blue-100 text-blue-600'
                                        }`}>
                                        {meeting.participants.length}
                                    </span>
                                )}
                            </button>
                        </div>

                        {/* Content Area */}
                        <div className="lg:col-span-3">
                            <div className="bg-white rounded-[2.5rem] border border-indigo-100 overflow-hidden min-h-[600px] shadow-sm">
                                {activeTab === 'summary' && (
                                    <div className="p-10">
                                        <div className="flex items-center justify-between mb-8">
                                            <h2 className="text-3xl font-black text-gray-900">Résumé Exécutif</h2>
                                        </div>

                                        {summary ? (
                                            <div className="prose prose-indigo max-w-none prose-lg">
                                                <div className="bg-indigo-50 rounded-3xl p-8 mb-8">
                                                    <h3 className="text-indigo-800 font-bold mb-4 uppercase text-xs tracking-widest">Synthèse</h3>
                                                    <p className="text-gray-700 leading-relaxed font-medium">
                                                        {summary.executive_summary}
                                                    </p>
                                                </div>

                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                                                    <div className="bg-emerald-50 rounded-3xl p-8">
                                                        <h3 className="text-emerald-800 font-bold mb-4 uppercase text-xs tracking-widest flex items-center gap-2">
                                                            <span>✨</span> Décisions Actées
                                                        </h3>
                                                        <ul className="space-y-3">
                                                            {summary && Array.isArray(summary.decisions) && summary.decisions.map((d, i) => (
                                                                <li key={i} className="flex items-start gap-3 text-sm font-medium text-gray-700">
                                                                    <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-emerald-400 flex-shrink-0"></span>
                                                                    {typeof d === 'object' ? (d.description || JSON.stringify(d)) : d}
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    </div>

                                                    <div className="bg-purple-50 rounded-3xl p-8">
                                                        <h3 className="text-purple-800 font-bold mb-4 uppercase text-xs tracking-widest flex items-center gap-2">
                                                            <span>❓</span> Questions Clés
                                                        </h3>
                                                        <ul className="space-y-3">
                                                            {summary && Array.isArray(summary.questions) && summary.questions.map((q, i) => (
                                                                <li key={i} className="flex items-start gap-3 text-sm font-medium text-gray-700">
                                                                    <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-purple-400 flex-shrink-0"></span>
                                                                    {typeof q === 'object' ? (q.question || JSON.stringify(q)) : q}
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                </div>

                                                <hr className="my-8 border-gray-100" />

                                                <div className="markdown-content">
                                                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                        {summary.full_markdown}
                                                    </ReactMarkdown>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="py-20 text-center bg-gray-50 rounded-[2rem] border-2 border-dashed border-gray-200">
                                                <Sparkles className="mx-auto h-12 w-12 text-gray-300 mb-4" />
                                                <p className="text-gray-400 font-bold uppercase text-[10px] tracking-widest mb-2">Pas encore de résumé</p>
                                                <p className="text-gray-400 text-sm">Lancez l'analyse IA ci-dessus pour générer le résumé.</p>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {activeTab === 'actions' && (
                                    <div className="p-10">
                                        <div className="space-y-6">
                                            {actions.length > 0 ? (
                                                <div className="space-y-4">
                                                    {actions.map((action) => (
                                                        <ActionItem
                                                            key={action.id}
                                                            action={action}
                                                            onStatusChange={handleActionStatusChange}
                                                        />
                                                    ))}
                                                </div>
                                            ) : (
                                                <div className="py-20 text-center bg-gray-50 rounded-[2rem] border-2 border-dashed border-gray-200">
                                                    <p className="text-gray-400 font-bold uppercase text-[10px] tracking-widest">Aucune action planifiée pour le moment</p>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}

                                {activeTab === 'transcription' && (
                                    <div className="p-10 h-[70vh] flex flex-col">
                                        {transcription ? (
                                            <TranscriptionViewer transcription={transcription} />
                                        ) : (
                                            <div className="space-y-8 flex flex-col items-center justify-center h-full">
                                                <div className="p-8 bg-amber-50 rounded-[2rem] border border-amber-100 flex gap-6 max-w-md">
                                                    <div className="w-14 h-14 rounded-2xl bg-white flex items-center justify-center text-amber-600 shadow-sm flex-shrink-0">
                                                        <FileText size={28} />
                                                    </div>
                                                    <div>
                                                        <h3 className="text-xl font-black text-amber-900">Transcription en cours...</h3>
                                                        <p className="text-sm text-amber-700 mt-2 font-medium">
                                                            Nous préparons le texte formaté. Dès qu'il sera prêt, vous pourrez le consulter ici.
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {activeTab === 'participants' && (
                                    <div className="p-10">
                                        <ParticipantsPanel
                                            meetingId={id}
                                            initialParticipants={meeting?.participants || []}
                                            onParticipantsChange={(updatedParticipants) => {
                                                setMeeting(prev => ({ ...prev, participants: updatedParticipants }));
                                            }}
                                        />
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Print-only container */}
            {summary && (
                <div id="print-content" className="hidden">
                    <div className="print-header">
                        <h1 className="print-title">{meeting.title}</h1>
                        <p className="print-meta">
                            {formatDate(meeting.scheduled_time)} • {meeting.duration_minutes || '--'} minutes
                        </p>
                    </div>
                    <div className="markdown-content">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {summary.full_markdown}
                        </ReactMarkdown>

                        <h2 className="mt-12 text-2xl font-black text-gray-800 mb-6">Plan d'action détaillé</h2>
                        <div className="space-y-4">
                            {actions.map(a => (
                                <div key={a.id} className="border-b border-gray-100 pb-4">
                                    <div className="flex justify-between items-start">
                                        <div className="flex-1">
                                            <span className="font-black text-indigo-600 mr-2">[{a.priority.toUpperCase()}]</span>
                                            <span className="font-bold text-gray-700">{a.description}</span>
                                        </div>
                                        <div className="text-xs bg-gray-50 px-3 py-1 rounded-full font-bold text-gray-500 border border-gray-100 italic">
                                            👤 {a.assigned_to}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Share Modal */}
            <ShareModal
                isOpen={isShareModalOpen}
                onClose={() => setIsShareModalOpen(false)}
                onShare={handleShare}
                meetingTitle={meeting?.title || 'Meeting'}
                isLoading={isSharing}
                initialEmails={participantEmails}
            />
        </>
    );
}

const AlertCircle = ({ size = 24 }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
);
