import { Link } from 'react-router-dom';
import { Calendar, Clock, CheckCircle, FileText, ListTodo, Trash2 } from 'lucide-react';

export default function MeetingCard({ meeting, onDelete, isSelected, onSelect }) {
    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            day: '2-digit',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const getStatusBadge = (status) => {
        const statuses = {
            scheduled: { label: 'Planifié', color: 'bg-indigo-100 text-indigo-700 border-indigo-200' },
            in_progress: { label: 'En cours', color: 'bg-amber-100 text-amber-700 border-amber-200' },
            completed: { label: 'Terminé', color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
        };
        const s = statuses[status] || statuses.scheduled;
        return (
            <span className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full border ${s.color}`}>
                {s.label}
            </span>
        );
    };

    return (
        <div className={`card group relative overflow-hidden flex flex-col h-full transition-all ${isSelected ? 'ring-2 ring-indigo-500 bg-indigo-50/10' : ''}`}>
            {/* Checkbox and Delete Button */}
            <div className="flex justify-between items-center mb-4">
                <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => onSelect(meeting.id)}
                    className="w-5 h-5 rounded-lg border-gray-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                />
                <button
                    onClick={(e) => {
                        e.preventDefault();
                        onDelete(meeting.id);
                    }}
                    className="p-2 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-xl transition-all"
                >
                    <Trash2 size={18} />
                </button>
            </div>

            <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-black text-gray-900 group-hover:text-indigo-600 transition-colors line-clamp-2">
                    {meeting.title}
                </h3>
            </div>

            <div className="space-y-3 mb-6 flex-grow">
                <div className="flex items-center text-sm text-gray-500 font-medium">
                    <Calendar className="w-4 h-4 mr-2 text-indigo-500" />
                    {formatDate(meeting.scheduled_time)}
                </div>

                {meeting.duration_minutes && (
                    <div className="flex items-center text-sm text-gray-500 font-medium">
                        <Clock className="w-4 h-4 mr-2 text-indigo-400" />
                        {meeting.duration_minutes} minutes
                    </div>
                )}

                <div className="flex flex-wrap gap-2 mt-4">
                    {meeting.has_transcription && (
                        <div className="flex items-center px-2 py-1 bg-gray-50 rounded-md text-[11px] font-semibold text-gray-600 border border-gray-100">
                            <FileText className="w-3 h-3 mr-1 text-emerald-500" />
                            Transcription
                        </div>
                    )}

                    {meeting.has_summary && (
                        <div className="flex items-center px-2 py-1 bg-gray-50 rounded-md text-[11px] font-semibold text-gray-600 border border-gray-100">
                            <CheckCircle className="w-3 h-3 mr-1 text-blue-500" />
                            Analysé
                        </div>
                    )}

                    {meeting.actions_count > 0 && (
                        <div className="flex items-center px-2 py-1 bg-gray-50 rounded-md text-[11px] font-semibold text-gray-600 border border-gray-100">
                            <ListTodo className="w-3 h-3 mr-1 text-purple-500" />
                            {meeting.actions_count} actions
                        </div>
                    )}
                </div>
            </div>

            <div className="mt-auto pt-4 border-t border-gray-50 flex items-center justify-between">
                {getStatusBadge(meeting.status)}
                <Link
                    to={`/meetings/${meeting.id}`}
                    className="text-sm font-bold text-indigo-600 hover:text-indigo-700 flex items-center group/link"
                >
                    Voir détails
                    <span className="ml-1 transform group-hover/link:translate-x-1 transition-transform">→</span>
                </Link>
            </div>
        </div>
    );
}

