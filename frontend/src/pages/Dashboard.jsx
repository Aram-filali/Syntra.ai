import { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, ArrowRight, Calendar, Sparkles, ListTodo, X, ChevronLeft, ChevronRight, CheckCircle, AlertCircle, Video, Trash2 } from 'lucide-react';
import { meetingsAPI, zoomAPI, createPolling } from '../api/client';
import { useNavigate, useLocation } from 'react-router-dom';
import MeetingCard from '../components/MeetingCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import Sidebar from '../components/Sidebar';

export default function Dashboard() {
    const [meetings, setMeetings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [viewDate, setViewDate] = useState(new Date());
    const [selectedDate, setSelectedDate] = useState(new Date());

    // Zoom States
    const [isZoomModalOpen, setIsZoomModalOpen] = useState(false);
    const [zoomRecordings, setZoomRecordings] = useState([]);
    const [loadingZoom, setLoadingZoom] = useState(false);
    const [zoomModalView, setZoomModalView] = useState('list'); // 'list' | 'upload'
    const [uploadFile, setUploadFile] = useState(null);
    const [selectedZoomMeeting, setSelectedZoomMeeting] = useState(null);

    const [notifications, setNotifications] = useState([]);
    const [selectedIds, setSelectedIds] = useState([]);
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
    const [deleteTargets, setDeleteTargets] = useState(null);

    // Ref to prevent duplicate notification
    const hasShownZoomNotification = useRef(false);

    // Ref for polling management
    const pollingRef = useRef(null);

    const navigate = useNavigate();
    const location = useLocation();

    // Helper functions for deletion
    const handleSelectMeeting = (id) => {
        setSelectedIds(prev =>
            prev.includes(id) ? prev.filter(mid => mid !== id) : [...prev, id]
        );
    };

    const handleSelectAll = () => {
        if (selectedIds.length === filteredMeetings.length) {
            setSelectedIds([]);
        } else {
            setSelectedIds(filteredMeetings.map(m => m.id));
        }
    };

    const handleDeleteMeetings = (idsToDelete = null) => {
        const targets = idsToDelete || selectedIds;
        if (targets.length === 0) return;
        setDeleteTargets(targets);
        setIsDeleteModalOpen(true);
    };

    const confirmDelete = async () => {
        if (!deleteTargets) return;

        const targets = deleteTargets;
        // Mise à jour optimiste
        setMeetings(prev => prev.filter(m => !targets.includes(m.id)));
        setSelectedIds([]);
        setIsDeleteModalOpen(false);
        setDeleteTargets(null);

        try {
            await Promise.all(targets.map(id => meetingsAPI.delete(id)));
            showNotification('success', `${targets.length} meeting(s) supprimé(s)`);
        } catch (err) {
            showNotification('error', "Erreur lors de la suppression sur le serveur");
            fetchMeetings();
        }
    };

    // Helper function to show notifications
    const showNotification = (type, message) => {
        const id = Date.now();
        setNotifications(prev => [...prev, { id, type, message, visible: true }]);

        // Auto-hide after 5 seconds
        setTimeout(() => {
            setNotifications(prev => prev.map(n =>
                n.id === id ? { ...n, visible: false } : n
            ));
            // Remove from array after animation
            setTimeout(() => {
                setNotifications(prev => prev.filter(n => n.id !== id));
            }, 300);
        }, 5000);
    };

    const dismissNotification = (id) => {
        setNotifications(prev => prev.map(n =>
            n.id === id ? { ...n, visible: false } : n
        ));
        setTimeout(() => {
            setNotifications(prev => prev.filter(n => n.id !== id));
        }, 300);
    };

    // Check for Zoom connection success
    useEffect(() => {
        if (location.search.includes('zoom=connected') && !hasShownZoomNotification.current) {
            hasShownZoomNotification.current = true;
            // Remove the query param to allow clean refresh
            navigate(location.pathname, { replace: true });
            // Show success notification
            showNotification('success', 'Compte Zoom connecté avec succès !');
        }
    }, [location, navigate]);

    const handleOpenZoomSync = async () => {
        setIsZoomModalOpen(true);
        setZoomModalView('list');
        setLoadingZoom(true);
        try {
            const data = await zoomAPI.getRecordings();
            // Zoom API returns an object { meetings: [] }
            setZoomRecordings(data.meetings || []);
        } catch (err) {
            console.error(err);
            showNotification('error', 'Erreur lors de la récupération des enregistrements Zoom. Vérifiez votre connexion.');
            setIsZoomModalOpen(false);
        } finally {
            setLoadingZoom(false);
        }
    };

    const handleImportZoom = (recording) => {
        setSelectedZoomMeeting(recording);
        setZoomModalView('upload'); // On passe à l'étape upload
        setUploadFile(null);
    };

    const handleHybridUpload = async () => {
        if (!uploadFile || !selectedZoomMeeting) return;

        setLoadingZoom(true);
        const formData = new FormData();
        formData.append('file', uploadFile);

        formData.append('zoom_id', selectedZoomMeeting.id);
        formData.append('topic', selectedZoomMeeting.topic || 'Réunion Zoom');
        formData.append('start_time', selectedZoomMeeting.start_time);
        formData.append('duration', selectedZoomMeeting.duration);

        try {
            await zoomAPI.uploadHybrid(formData);
            showNotification('success', 'Importation lancée ! Notre IA analyse votre fichier.');
            setIsZoomModalOpen(false);
            setZoomModalView('list');
            setSelectedZoomMeeting(null);
            setUploadFile(null);
            fetchMeetings();
        } catch (err) {
            console.error(err);
            showNotification('error', "Erreur lors de l'envoi du fichier.");
        } finally {
            setLoadingZoom(false);
        }
    };

    const fetchMeetings = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await meetingsAPI.getAll();
            setMeetings(data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Erreur lors du chargement des meetings');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // Initial fetch
        fetchMeetings();

        // Setup polling - polls every 10 seconds while meetings are processing
        pollingRef.current = createPolling(
            async () => {
                const data = await meetingsAPI.getAll();
                setMeetings(data);
                return data;
            },
            (meetings) => {
                // Continue polling if any meeting is still processing (has_summary = false) 
                return meetings.some(m => !m.has_summary && m.status !== 'cancelled');
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
    }, []);

    const filteredMeetings = meetings.filter((meeting) =>
        meeting.title.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const recentMeetings = meetings.slice(0, 3);
    const upcomingMeetings = meetings.filter(m => m.status === 'scheduled').slice(0, 3);

    // Calendar logic helpers
    const getDaysInMonth = (date) => {
        const year = date.getFullYear();
        const month = date.getMonth();
        const days = new Date(year, month + 1, 0).getDate();
        const firstDay = new Date(year, month, 1).getDay();
        return { days, firstDay };
    };

    const isSameDay = (d1, d2) => {
        if (!d1 || !d2) return false;
        return d1.getFullYear() === d2.getFullYear() &&
            d1.getMonth() === d2.getMonth() &&
            d1.getDate() === d2.getDate();
    };

    const hasMeetingOnDay = (day) => {
        const checkDate = new Date(viewDate.getFullYear(), viewDate.getMonth(), day);
        return meetings.some(m => m.scheduled_time && isSameDay(new Date(m.scheduled_time), checkDate));
    };

    const calendarData = getDaysInMonth(viewDate);
    const monthNames = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"];

    const changeMonth = (offset) => {
        const newDate = new Date(viewDate);
        newDate.setMonth(viewDate.getMonth() + offset);
        setViewDate(newDate);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-50/40 via-white to-purple-50/40">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                    <LoadingSpinner message="Chargement des meetings..." />
                </div>
            </div>
        );
    }

    const stats = [
        {
            label: 'Total Réunions',
            value: meetings.length,
        },
        {
            label: 'Analysés',
            value: meetings.filter(m => m.has_summary).length,
        },
        {
            label: 'À venir',
            value: meetings.filter(m => m.status === 'scheduled').length,
        },
        {
            label: 'Actions totales',
            value: meetings.reduce((acc, m) => acc + (m.actions_count || 0), 0),
        }
    ];

    return (
        <div className="min-h-screen bg-[#fafafa] flex">
            {/* Toast Notifications - Top Right */}
            <div className="fixed top-8 right-8 z-50 space-y-3 max-w-sm">
                {notifications.map((notification) => (
                    <div
                        key={notification.id}
                        className={`transform transition-all duration-300 ${notification.visible
                            ? 'translate-x-0 opacity-100'
                            : 'translate-x-full opacity-0'
                            }`}
                    >
                        <div className={`bg-white border rounded-2xl p-5 shadow-xl ${notification.type === 'success'
                            ? 'border-emerald-100'
                            : 'border-red-100'
                            }`}>
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex items-start gap-3 flex-1">
                                    {notification.type === 'success' ? (
                                        <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center flex-shrink-0">
                                            <CheckCircle className="w-5 h-5 text-emerald-600" />
                                        </div>
                                    ) : (
                                        <div className="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center flex-shrink-0">
                                            <AlertCircle className="w-5 h-5 text-red-600" />
                                        </div>
                                    )}
                                    <div className="flex-1 pt-1">
                                        <p className={`text-sm font-bold mb-1 ${notification.type === 'success'
                                            ? 'text-emerald-900'
                                            : 'text-red-900'
                                            }`}>
                                            {notification.type === 'success' ? 'Succès' : 'Erreur'}
                                        </p>
                                        <p className="text-xs text-gray-600 font-medium leading-relaxed">
                                            {notification.message}
                                        </p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => dismissNotification(notification.id)}
                                    className="ml-2 text-gray-400 hover:text-gray-600 transition-colors flex-shrink-0"
                                >
                                    <X size={18} />
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Sidebar Component */}
            <Sidebar />

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto">
                <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    {/* Header */}
                    <div className="mb-10">
                        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-8">
                            <div className="space-y-1">
                                <h1 className="text-4xl font-black text-gray-900 tracking-tight">
                                    Tableau de Bord
                                </h1>
                                <p className="text-base text-gray-500 font-medium">
                                    Bienvenue, voici le résumé de vos activités.
                                </p>
                            </div>
                            <div className="flex gap-3">
                                <button
                                    onClick={handleOpenZoomSync}
                                    className="px-6 py-3 bg-white text-indigo-900 border border-indigo-100 rounded-xl font-bold shadow-sm hover:bg-indigo-50 transition-all flex items-center gap-2"
                                >
                                    <Sparkles size={18} className="text-indigo-600" />
                                    <span>Sync Zoom</span>
                                </button>
                                <Link
                                    to="/create"
                                    className="group relative px-6 py-3 bg-indigo-600 text-white rounded-xl font-bold shadow-lg shadow-indigo-500/30 hover:shadow-xl hover:shadow-indigo-500/40 transition-all duration-300 hover:scale-105 flex items-center gap-2"
                                >
                                    <Plus size={20} className="group-hover:rotate-90 transition-transform duration-300" />
                                    <span>Nouveau Meeting</span>
                                </Link>
                            </div>
                        </div>

                        {/* Stats Cards */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                            {stats.map((stat, index) => (
                                <div
                                    key={index}
                                    className="group relative bg-white rounded-2xl p-6 border border-gray-100"
                                >


                                    <div className="relative">
                                        <p className="text-[10px] font-black text-indigo-500 uppercase tracking-widest mb-2">
                                            {stat.label}
                                        </p>
                                        <div className="flex items-center justify-between">
                                            <p className="text-3xl font-black text-gray-900">
                                                {stat.value}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Content Sections */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">
                        {/* Activité récente */}
                        <div className="lg:col-span-2 space-y-5">
                            <div className="flex items-center justify-between">
                                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                                    <span className="w-1.5 h-6 rounded-full"></span>
                                    Activité récente
                                </h2>
                                <Link to="/meetings" className="text-sm font-bold text-indigo-600 hover:text-indigo-700 flex items-center gap-1">
                                    Voir tout <ArrowRight size={14} />
                                </Link>
                            </div>

                            {recentMeetings.length > 0 ? (
                                <div className="space-y-4">
                                    {recentMeetings.map((meeting) => (
                                        <div key={meeting.id} className="group bg-white p-4 rounded-2xl border border-gray-100 flex items-center gap-4">
                                            <div className="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center text-indigo-600">
                                                <Calendar size={20} />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <h3 className="font-bold text-gray-900 truncate group-hover:text-indigo-600 transition-colors">{meeting.title}</h3>
                                                <p className="text-xs text-gray-500 font-medium">
                                                    Créé le {meeting.created_at ? new Date(meeting.created_at).toLocaleDateString('fr-FR') : 'Date inconnue'}
                                                </p>
                                            </div>
                                            {meeting.has_summary && (
                                                <span className="px-3 py-1 bg-emerald-50 text-emerald-700 text-[10px] font-black uppercase tracking-widest rounded-lg border border-emerald-100">
                                                    Analysé
                                                </span>
                                            )}
                                            <Link to={`/meetings/${meeting.id}`} className="p-2 text-gray-400 hover:text-indigo-600 transition-colors">
                                                <ArrowRight size={20} />
                                            </Link>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="bg-white rounded-3xl p-10 border border-gray-100 border-dashed text-center">
                                    <p className="text-gray-400 font-bold text-sm">AUCUNE ACTIVITÉ RÉCENTE</p>
                                </div>
                            )}
                        </div>

                        {/* Calendrier Intégré */}
                        <div className="space-y-5">
                            <h2 className="text-xl font-bold text-gray-900 px-2 italic">Calendrier</h2>
                            <div className="bg-white rounded-3xl p-6 border border-gray-100 shadow-sm">
                                <div className="flex items-center justify-between mb-6">
                                    <div>
                                        <h3 className="text-lg font-black text-gray-900">{monthNames[viewDate.getMonth()]}</h3>
                                        <p className="text-[10px] font-bold text-indigo-500 uppercase tracking-widest">{viewDate.getFullYear()}</p>
                                    </div>
                                    <div className="flex gap-1">
                                        <button
                                            onClick={() => changeMonth(-1)}
                                            className="p-1.5 hover:bg-indigo-50 rounded-lg transition-colors text-gray-600"
                                        >
                                            <ChevronLeft size={16} />
                                        </button>
                                        <button
                                            onClick={() => changeMonth(1)}
                                            className="p-1.5 hover:bg-indigo-50 rounded-lg transition-colors text-gray-600"
                                        >
                                            <ChevronRight size={16} />
                                        </button>
                                    </div>
                                </div>

                                <div className="grid grid-cols-7 gap-1 mb-2">
                                    {['L', 'M', 'M', 'J', 'V', 'S', 'D'].map((day, idx) => (
                                        <div key={idx} className="text-center text-[10px] font-black text-gray-300 uppercase py-1">
                                            {day}
                                        </div>
                                    ))}
                                </div>

                                <div className="grid grid-cols-7 gap-1">
                                    {Array.from({ length: calendarData.firstDay === 0 ? 6 : calendarData.firstDay - 1 }).map((_, i) => (
                                        <div key={`empty-${i}`} className="aspect-square"></div>
                                    ))}

                                    {Array.from({ length: calendarData.days }).map((_, i) => {
                                        const day = i + 1;
                                        const checkDate = new Date(viewDate.getFullYear(), viewDate.getMonth(), day);
                                        const hasMeeting = hasMeetingOnDay(day);
                                        const isToday = isSameDay(new Date(), checkDate);
                                        const isSelected = isSameDay(selectedDate, checkDate);

                                        return (
                                            <button
                                                key={day}
                                                onClick={() => setSelectedDate(checkDate)}
                                                className={`aspect-square flex flex-col items-center justify-center rounded-xl text-xs font-bold relative transition-all ${isSelected ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' :
                                                    isToday ? 'bg-indigo-50 text-indigo-600 border border-indigo-200' :
                                                        hasMeeting ? 'bg-gray-50 text-indigo-600 border border-gray-100 hover:bg-gray-100' : 'text-gray-600 hover:bg-gray-50'
                                                    }`}
                                            >
                                                {day}
                                                {hasMeeting && !isSelected && (
                                                    <div className="absolute bottom-1 w-1 h-1 rounded-full bg-indigo-500"></div>
                                                )}
                                            </button>
                                        );
                                    })}
                                </div>

                                <div className="mt-6 pt-6 border-t border-gray-50">
                                    <h4 className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">
                                        {isSameDay(selectedDate, new Date()) ? "Aujourd'hui" : selectedDate.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })}
                                    </h4>
                                    <div className="space-y-2">
                                        {meetings
                                            .filter(m => m.scheduled_time && isSameDay(new Date(m.scheduled_time), selectedDate))
                                            .length > 0 ? (
                                            meetings
                                                .filter(m => m.scheduled_time && isSameDay(new Date(m.scheduled_time), selectedDate))
                                                .slice(0, 2)
                                                .map(m => (
                                                    <Link
                                                        key={m.id}
                                                        to={`/meetings/${m.id}`}
                                                        className="flex items-center gap-2 p-2 bg-gray-50 rounded-xl hover:bg-indigo-50 transition-colors group text-left"
                                                    >
                                                        <div className="w-1.5 h-1.5 rounded-full bg-indigo-500"></div>
                                                        <p className="text-[11px] font-bold text-gray-900 truncate flex-1">{m.title}</p>
                                                        <ArrowRight size={12} className="text-gray-400 group-hover:text-indigo-600 transition-colors" />
                                                    </Link>
                                                ))
                                        ) : (
                                            <p className="text-[10px] font-bold text-gray-400 italic">Aucun meeting</p>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Barre de recherche */}
                    <div className="mb-10">
                        <div className="relative">
                            <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                            <input
                                type="text"
                                placeholder="Rechercher une réunion par titre..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full pl-14 pr-6 py-4 bg-white border border-gray-100 rounded-2xl shadow-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all font-medium"
                            />
                        </div>
                    </div>

                    {/* All Meetings Grid */}
                    <div>
                        <div className="flex items-center gap-3 mb-8">
                            <h2 className="text-2xl font-black text-gray-900 tracking-tight">
                                {searchTerm ? 'Résultats de recherche' : 'Tous vos meetings'}
                            </h2>
                            <div className="h-px flex-1 bg-gray-100"></div>

                            {filteredMeetings.length > 0 && (
                                <div className="flex items-center gap-4 bg-white px-4 py-2 rounded-xl border border-gray-100 shadow-sm">
                                    <div className="flex items-center gap-2 pr-4 border-r border-gray-100">
                                        <input
                                            type="checkbox"
                                            checked={selectedIds.length === filteredMeetings.length && filteredMeetings.length > 0}
                                            onChange={handleSelectAll}
                                            className="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                                        />
                                        <span className="text-xs font-black text-gray-500 uppercase tracking-widest whitespace-nowrap">Tout sélectionner</span>
                                    </div>

                                    <button
                                        disabled={selectedIds.length === 0}
                                        onClick={() => handleDeleteMeetings()}
                                        className={`flex items-center gap-2 transition-all ${selectedIds.length > 0 ? 'text-red-500 hover:scale-105' : 'text-gray-300 cursor-not-allowed'}`}
                                    >
                                        <Trash2 size={18} />
                                        {selectedIds.length > 0 && <span className="text-xs font-black">{selectedIds.length}</span>}
                                    </button>
                                </div>
                            )}

                            <span className="px-3 py-1 bg-indigo-600 text-white text-xs font-black rounded-lg shadow-lg shadow-indigo-100">
                                {filteredMeetings.length}
                            </span>
                        </div>

                        {filteredMeetings.length === 0 ? (
                            <div className="text-center py-20 bg-white rounded-3xl border-2 border-dashed border-gray-100">
                                <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-indigo-50 mb-6 transform rotate-3">
                                    <Plus className="w-10 h-10 text-indigo-500" strokeWidth={3} />
                                </div>
                                <h3 className="text-2xl font-black text-gray-900 mb-2">
                                    {searchTerm ? 'Aucun résultat trouvé' : 'Commençons l\'aventure'}
                                </h3>
                                <p className="text-gray-500 mb-8 max-w-sm mx-auto font-medium">
                                    {searchTerm
                                        ? `Désolé, nous n'avons rien trouvé pour "${searchTerm}"`
                                        : 'Créez votre première réunion et laissez notre IA faire le travail difficile pour vous.'}
                                </p>
                                {!searchTerm && (
                                    <Link
                                        to="/create"
                                        className="inline-flex items-center gap-2 px-8 py-4 bg-indigo-600 text-white rounded-2xl font-black shadow-xl shadow-indigo-200 hover:scale-105 transition-all"
                                    >
                                        <Plus size={20} />
                                        <span>CRÉER MON PREMIER MEETING</span>
                                    </Link>
                                )}
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                                {filteredMeetings.map((meeting) => (
                                    <MeetingCard
                                        key={meeting.id}
                                        meeting={meeting}
                                        isSelected={selectedIds.includes(meeting.id)}
                                        onSelect={handleSelectMeeting}
                                        onDelete={(id) => handleDeleteMeetings([id])}
                                    />
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </main>

            {/* Modal Zoom */}
            {isZoomModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <div className="absolute inset-0 bg-gray-900/60 backdrop-blur-md" onClick={() => { setIsZoomModalOpen(false); setZoomModalView('list'); setSelectedZoomMeeting(null); }}></div>
                    <div className="relative bg-white rounded-[2.5rem] w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl flex flex-col border border-white/20">
                        {/* Header Dynamique */}
                        <div className="p-8 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                            <div>
                                <h3 className="text-2xl font-black text-gray-900 flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-200">
                                        <Video className="text-white" size={24} />
                                    </div>
                                    {zoomModalView === 'list' && "Réunions Programmées"}
                                    {zoomModalView === 'upload' && "Uploader l'enregistrement"}
                                </h3>
                                <p className="text-sm text-gray-500 font-medium mt-1">
                                    {zoomModalView === 'list' && "Sélectionnez la session correspondante"}
                                    {zoomModalView === 'upload' && `Fichier pour : ${selectedZoomMeeting?.topic}`}
                                </p>
                            </div>
                            <button onClick={() => { setIsZoomModalOpen(false); setZoomModalView('list'); setSelectedZoomMeeting(null); }} className="p-3 hover:bg-white hover:shadow-md rounded-2xl transition-all text-gray-400 hover:text-gray-600">
                                <X size={20} />
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto p-8">
                            {loadingZoom ? (
                                <div className="py-20 flex flex-col items-center">
                                    <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-6 shadow-xl shadow-blue-100"></div>
                                    <p className="text-gray-900 font-black text-lg animate-pulse">Recherche en cours...</p>
                                </div>
                            ) : zoomModalView === 'list' ? (
                                <div className="space-y-4 animate-in slide-in-from-right duration-300">
                                    {zoomRecordings.length === 0 ? (
                                        <div className="text-center py-10">
                                            <p className="text-gray-500 font-medium">Aucune donnée trouvée.</p>
                                            <button onClick={handleOpenZoomSync} className="text-blue-600 font-black text-xs uppercase mt-4">Réessayer</button>
                                        </div>
                                    ) : (
                                        <>
                                            <div className="grid grid-cols-1 gap-3 max-h-[400px] overflow-y-auto pr-2 scrollbar-thin">
                                                {zoomRecordings.map((rec) => (
                                                    <button
                                                        key={`${rec.id}_${rec.start_time}`}
                                                        onClick={() => handleImportZoom(rec)}
                                                        className="group flex items-center justify-between p-5 bg-white border border-gray-100 rounded-[1.5rem] hover:border-blue-400 hover:shadow-lg transition-all text-left"
                                                    >
                                                        <div className="flex items-center gap-4">
                                                            <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-blue-600 font-black group-hover:bg-blue-600 group-hover:text-white transition-colors">
                                                                {new Date(rec.start_time).getDate()}
                                                            </div>
                                                            <div>
                                                                <h4 className="font-bold text-gray-900 group-hover:text-blue-600 truncate max-w-[250px]">{rec.topic}</h4>
                                                                <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                                                                    {new Date(rec.start_time).toLocaleDateString()} • {rec.duration} min
                                                                </p>
                                                            </div>
                                                        </div>
                                                        <ArrowRight className="text-gray-300 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" size={20} />
                                                    </button>
                                                ))}
                                            </div>

                                            {/* Aide Secours */}
                                            <div className="mt-8 pt-6 border-t border-gray-100">
                                                <div className="bg-indigo-50/50 rounded-2xl p-4 flex items-center gap-4">
                                                    <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center text-indigo-600 shadow-sm flex-shrink-0">
                                                        <Sparkles size={18} />
                                                    </div>
                                                    <div className="flex-1">
                                                        <p className="text-xs text-gray-600 font-medium">
                                                            Votre réunion Zoom est introuvable ? Les sessions lancées instantanément via "Nouvelle réunion" ne sont pas toujours listées.
                                                        </p>
                                                        <Link to="/create" className="text-[10px] font-black text-indigo-600 uppercase tracking-widest hover:underline mt-1 block">
                                                            Uploader l'enregistrement local →
                                                        </Link>
                                                    </div>
                                                </div>
                                            </div>
                                        </>
                                    )}
                                </div>
                            ) : (
                                /* Vue Upload (Pour le mode Liste) */
                                <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-300">
                                    <div className="bg-blue-50/50 border border-blue-100 rounded-3xl p-6 flex gap-4">
                                        <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center text-blue-600 shadow-sm flex-shrink-0">
                                            <AlertCircle />
                                        </div>
                                        <p className="text-sm text-blue-900 font-medium leading-relaxed">
                                            Veuillez glisser le fichier audio/vidéo correspondant à la réunion : <br />
                                            <span className="font-black">"{selectedZoomMeeting?.topic}"</span>
                                        </p>
                                    </div>
                                    <div
                                        onClick={() => document.getElementById('meeting-upload-sync').click()}
                                        className={`group relative border-2 border-dashed rounded-[2rem] p-10 flex flex-col items-center justify-center transition-all cursor-pointer ${uploadFile ? 'border-emerald-400 bg-emerald-50/30' : 'border-gray-100 hover:border-blue-400 hover:bg-blue-50/30'}`}
                                    >
                                        <input id="meeting-upload-sync" type="file" className="hidden" accept="video/*,audio/*" onChange={(e) => setUploadFile(e.target.files[0])} />
                                        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 shadow-xl transition-transform group-hover:scale-110 ${uploadFile ? 'bg-emerald-500 text-white' : 'bg-white text-blue-600'}`}>
                                            {uploadFile ? <CheckCircle size={32} /> : <Plus size={32} />}
                                        </div>
                                        <h4 className="text-lg font-black text-gray-900">{uploadFile ? uploadFile.name : 'Déposez votre fichier ici'}</h4>
                                        <p className="text-sm text-gray-500 font-medium">Cliquez pour parcourir vos documents</p>
                                    </div>
                                    <div className="flex gap-4">
                                        <button onClick={() => setZoomModalView('list')} className="px-8 py-4 bg-gray-100 text-gray-600 rounded-2xl font-black text-xs uppercase tracking-widest">Retour</button>
                                        <button
                                            onClick={handleHybridUpload}
                                            disabled={!uploadFile}
                                            className={`flex-1 py-4 rounded-2xl font-black text-xs uppercase tracking-widest transition-all shadow-xl ${uploadFile ? 'bg-blue-600 text-white hover:scale-[1.02]' : 'bg-gray-200 text-gray-400 cursor-not-allowed'}`}
                                        >
                                            Démarrer l'Analyse Inteligente
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}


            {/* Modal de Confirmation de Suppression */}
            {isDeleteModalOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 animate-in fade-in duration-300">
                    <div
                        className="absolute inset-0 bg-gray-900/40 backdrop-blur-md"
                        onClick={() => setIsDeleteModalOpen(false)}
                    ></div>
                    <div className="relative bg-white/70 backdrop-blur-xl rounded-[2.5rem] w-full max-w-md overflow-hidden shadow-2xl border border-white/50 animate-in zoom-in-95 duration-300">
                        <div className="p-10 text-center">
                            <div className="w-20 h-20 bg-red-50 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-xl shadow-red-100">
                                <Trash2 size={40} className="text-red-500" />
                            </div>
                            <h3 className="text-2xl font-black text-gray-900 mb-2">Suppression définitive</h3>
                            <p className="text-gray-500 font-medium mb-10 leading-relaxed">
                                Êtes-vous sûr de vouloir supprimer {deleteTargets?.length === 1 ? "ce meeting" : `ces ${deleteTargets?.length} meetings`} ? <br />Cette action est irréversible.
                            </p>

                            <div className="flex gap-4">
                                <button
                                    onClick={() => setIsDeleteModalOpen(false)}
                                    className="flex-1 py-4 bg-gray-100 text-gray-600 rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-gray-200 transition-all"
                                >
                                    Annuler
                                </button>
                                <button
                                    onClick={confirmDelete}
                                    className="flex-1 py-4 bg-red-500 text-white rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-red-600 shadow-xl shadow-red-200 hover:scale-105 active:scale-95 transition-all"
                                >
                                    Supprimer
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
