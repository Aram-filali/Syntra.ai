import { useEffect, useState } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import { Search, ArrowLeft, Calendar, Sparkles, ListTodo, FileText, AlertCircle } from 'lucide-react';
import { meetingsAPI } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import Sidebar from '../components/Sidebar';

export default function SearchResults() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const query = searchParams.get('q') || '';

    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!query || query.trim().length < 2) {
            setError('Veuillez entrer une recherche valide (minimum 2 caractères)');
            return;
        }

        const performSearch = async () => {
            setLoading(true);
            setError(null);
            try {
                const data = await meetingsAPI.search(query);
                setResults(data);
            } catch (err) {
                setError(err.response?.data?.detail || 'Erreur lors de la recherche');
                setResults(null);
            } finally {
                setLoading(false);
            }
        };

        performSearch();
    }, [query]);

    const formatDate = (dateString) => {
        if (!dateString) return '--';
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
        });
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed':
                return 'bg-emerald-100 text-emerald-700';
            case 'in_progress':
                return 'bg-amber-100 text-amber-700';
            case 'scheduled':
                return 'bg-blue-100 text-blue-700';
            default:
                return 'bg-gray-100 text-gray-700';
        }
    };

    const getStatusLabel = (status) => {
        switch (status) {
            case 'completed':
                return '✓ Finalisé';
            case 'in_progress':
                return '⚡ En cours';
            case 'scheduled':
                return '📅 Programmé';
            default:
                return status;
        }
    };

    return (
        <div className="min-h-screen bg-[#fafafa] flex">
            <Sidebar />
            <div className="flex-1">
                <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                    {/* Header */}
                    <div className="mb-10">
                        <Link
                            to="/dashboard"
                            className="inline-flex items-center text-sm font-bold text-indigo-600 hover:text-indigo-700 mb-6 transition-all group"
                        >
                            <ArrowLeft size={16} className="mr-2 group-hover:-translate-x-1 transition-transform" />
                            Retour au Dashboard
                        </Link>

                        <div className="flex items-center gap-4 mb-4">
                            <div className="w-12 h-12 rounded-2xl bg-indigo-100 flex items-center justify-center text-indigo-600 shadow-sm">
                                <Search size={24} />
                            </div>
                            <div>
                                <h1 className="text-4xl font-black text-gray-900">Résultats de recherche</h1>
                                <p className="text-gray-500 font-medium mt-1">Pour : <span className="font-black text-indigo-600">"{query}"</span></p>
                            </div>
                        </div>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="mb-8">
                            <ErrorMessage message={error} />
                        </div>
                    )}

                    {/* Loading */}
                    {loading && (
                        <div className="bg-white rounded-3xl p-12 shadow-sm">
                            <LoadingSpinner message="Recherche en cours..." />
                        </div>
                    )}

                    {/* No Results */}
                    {!loading && results && results.total_results === 0 && (
                        <div className="bg-white rounded-3xl border border-gray-100 p-12 shadow-sm text-center">
                            <div className="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-6">
                                <AlertCircle size={40} className="text-gray-400" />
                            </div>
                            <h3 className="text-2xl font-black text-gray-900 mb-2">Aucun résultat</h3>
                            <p className="text-gray-500 font-medium mb-6">Nous n'avons trouvé aucun meeting correspondant à "<span className="font-black">{query}</span>"</p>
                            <Link
                                to="/dashboard"
                                className="inline-block px-6 py-3 bg-indigo-600 text-white font-black rounded-xl hover:bg-indigo-700 transition-colors"
                            >
                                Retour aux meetings
                            </Link>
                        </div>
                    )}

                    {/* Results Grid */}
                    {!loading && results && results.total_results > 0 && (
                        <div>
                            {/* Summary */}
                            <div className="mb-8 p-6 bg-indigo-50 rounded-2xl border border-indigo-100">
                                <p className="text-indigo-900 font-black text-lg">
                                    {results.total_results === 1
                                        ? '1 résultat trouvé'
                                        : `${results.total_results} résultats trouvés`}
                                </p>
                            </div>

                            {/* Results List */}
                            <div className="space-y-4">
                                {results.results.map((meeting) => (
                                    <Link
                                        key={meeting.id}
                                        to={`/meetings/${meeting.id}`}
                                        className="group block bg-white rounded-2xl border border-gray-100 p-6 hover:border-indigo-200 hover:shadow-lg transition-all"
                                    >
                                        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                                            {/* Left */}
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-start gap-4 mb-3">
                                                    <div className={`px-3 py-1 rounded-lg text-xs font-black uppercase tracking-widest ${getStatusColor(meeting.status)} whitespace-nowrap`}>
                                                        {getStatusLabel(meeting.status)}
                                                    </div>
                                                    {meeting.has_summary && (
                                                        <div className="px-3 py-1 rounded-lg text-xs font-black uppercase tracking-widest bg-emerald-100 text-emerald-700 whitespace-nowrap">
                                                            ✓ Analysé
                                                        </div>
                                                    )}
                                                </div>

                                                <h3 className="text-xl font-black text-gray-900 mb-3 group-hover:text-indigo-600 transition-colors line-clamp-2">
                                                    {meeting.title}
                                                </h3>

                                                {/* Match Fields */}
                                                <div className="flex flex-wrap gap-2 mb-4">
                                                    {meeting.match_fields.map((field, idx) => (
                                                        <span
                                                            key={idx}
                                                            className="text-xs px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700 font-medium border border-indigo-100"
                                                        >
                                                            {field}
                                                        </span>
                                                    ))}
                                                </div>

                                                {/* Meta Info */}
                                                <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 font-medium">
                                                    <div className="flex items-center gap-2">
                                                        <Calendar size={16} />
                                                        {formatDate(meeting.scheduled_time)}
                                                    </div>
                                                    {meeting.has_transcription && (
                                                        <div className="flex items-center gap-2">
                                                            <FileText size={16} />
                                                            Transcription
                                                        </div>
                                                    )}
                                                    {meeting.actions_count > 0 && (
                                                        <div className="flex items-center gap-2">
                                                            <ListTodo size={16} />
                                                            {meeting.actions_count} action{meeting.actions_count > 1 ? 's' : ''}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>

                                            {/* Right - Arrow */}
                                            <div className="flex-shrink-0 text-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <Sparkles size={24} />
                                            </div>
                                        </div>
                                    </Link>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
