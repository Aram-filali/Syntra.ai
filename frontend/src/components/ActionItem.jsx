import { CheckCircle, Circle, Edit2, Save, X } from 'lucide-react';
import { meetingsAPI } from '../api/client';
import { useState } from 'react';

export default function ActionItem({ action, onStatusChange }) {
    const [isUpdating, setIsUpdating] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [editData, setEditData] = useState({
        status: action.status || 'todo',
        priority: action.priority || 'medium',
        assigned_to: action.assigned_to || '',
        due_date: action.due_date ? new Date(action.due_date).toISOString().split('T')[0] : ''
    });

    const handleToggle = async () => {
        setIsUpdating(true);
        try {
            const newStatus = action.status === 'completed' ? 'todo' : 'completed';
            await meetingsAPI.updateActionItem(action.id, { status: newStatus });
            onStatusChange && onStatusChange(action.id, newStatus);
        } catch (error) {
            console.error('Error updating action:', error);
        } finally {
            setIsUpdating(false);
        }
    };

    const handleSaveEdit = async () => {
        setIsUpdating(true);
        try {
            await meetingsAPI.updateActionItem(action.id, {
                status: editData.status,
                priority: editData.priority,
                assigned_to: editData.assigned_to,
                due_date: editData.due_date ? new Date(editData.due_date).toISOString() : null
            });
            setIsEditing(false);
            onStatusChange && onStatusChange(action.id, editData.status);
        } catch (error) {
            console.error('Error updating action:', error);
        } finally {
            setIsUpdating(false);
        }
    };

    const getPriorityLabel = (priority) => {
        const labels = {
            high: 'Haute',
            medium: 'Moyenne',
            low: 'Basse',
        };
        return labels[priority?.toLowerCase()] || priority;
    };

    const getPriorityClasses = (priority) => {
        const classes = {
            high: 'bg-red-50 text-red-700 border-red-100',
            medium: 'bg-amber-50 text-amber-700 border-amber-100',
            low: 'bg-emerald-50 text-emerald-700 border-emerald-100',
        };
        return classes[priority?.toLowerCase()] || 'bg-gray-50 text-gray-700 border-gray-100';
    };

    const getStatusLabel = (status) => {
        const labels = {
            todo: 'À faire',
            in_progress: 'En cours',
            completed: 'Complété'
        };
        return labels[status?.toLowerCase()] || status;
    };

    if (isEditing) {
        return (
            <div className="p-6 bg-indigo-50 border-2 border-indigo-200 rounded-2xl space-y-4">
                <h4 className="font-black text-indigo-900">Modifier l'action</h4>
                
                <div>
                    <label className="block text-xs font-black text-indigo-600 uppercase mb-2">Statut</label>
                    <select
                        value={editData.status}
                        onChange={(e) => setEditData({...editData, status: e.target.value})}
                        className="w-full px-3 py-2 border border-indigo-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                        <option value="todo">À faire</option>
                        <option value="in_progress">En cours</option>
                        <option value="completed">Complété</option>
                    </select>
                </div>

                <div>
                    <label className="block text-xs font-black text-indigo-600 uppercase mb-2">Priorité</label>
                    <select
                        value={editData.priority}
                        onChange={(e) => setEditData({...editData, priority: e.target.value})}
                        className="w-full px-3 py-2 border border-indigo-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                        <option value="low">Basse</option>
                        <option value="medium">Moyenne</option>
                        <option value="high">Haute</option>
                    </select>
                </div>

                <div>
                    <label className="block text-xs font-black text-indigo-600 uppercase mb-2">Assigné à</label>
                    <input
                        type="text"
                        value={editData.assigned_to}
                        onChange={(e) => setEditData({...editData, assigned_to: e.target.value})}
                        placeholder="Nom de la personne"
                        className="w-full px-3 py-2 border border-indigo-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                </div>

                <div>
                    <label className="block text-xs font-black text-indigo-600 uppercase mb-2">Date limite</label>
                    <input
                        type="date"
                        value={editData.due_date}
                        onChange={(e) => setEditData({...editData, due_date: e.target.value})}
                        className="w-full px-3 py-2 border border-indigo-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={handleSaveEdit}
                        disabled={isUpdating}
                        className="flex-1 px-4 py-2 bg-indigo-600 text-white font-black rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                        <Save size={16} /> Enregistrer
                    </button>
                    <button
                        onClick={() => setIsEditing(false)}
                        disabled={isUpdating}
                        className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 font-black rounded-lg hover:bg-gray-300 disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                        <X size={16} /> Annuler
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className={`flex items-start gap-4 p-5 bg-white border border-gray-100 rounded-2xl transition-all group hover:border-indigo-200 hover:shadow-sm ${action.status === 'completed' ? 'bg-gray-50/50' : ''}`}>
            <button
                onClick={handleToggle}
                disabled={isUpdating}
                className={`mt-1 flex-shrink-0 transition-all active:scale-95 ${isUpdating ? 'opacity-50 cursor-not-allowed' : ''}`}
                title={action.status === 'completed' ? 'Marquer comme non terminé' : 'Marquer comme terminé'}
            >
                {action.status === 'completed' ? (
                    <div className="w-6 h-6 bg-emerald-600 rounded-full flex items-center justify-center shadow-lg shadow-emerald-100 group-hover:bg-emerald-700 transition-colors">
                        <CheckCircle className="w-4 h-4 text-white" />
                    </div>
                ) : (
                    <div className="w-6 h-6 rounded-full border-2 border-gray-200 group-hover:border-indigo-500 group-hover:bg-indigo-50 flex items-center justify-center transition-all">
                        <Circle className="w-4 h-4 text-transparent group-hover:text-indigo-400 transition-colors" />
                    </div>
                )}
            </button>

            <div className="flex-1 min-w-0">
                <p
                    className={`text-base font-bold leading-relaxed mb-3 ${action.status === 'completed'
                        ? 'text-gray-400 line-through'
                        : 'text-gray-900'
                        }`}
                >
                    {action.description}
                </p>

                <div className="flex flex-wrap items-center gap-2">
                    <span className={`text-[10px] font-black uppercase tracking-widest px-2 py-1 rounded-lg border ${getPriorityClasses(action.priority)}`}>
                        {getPriorityLabel(action.priority)}
                    </span>

                    <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest bg-gray-50 px-2 py-1 rounded-lg border border-gray-100">
                        {getStatusLabel(action.status)}
                    </span>

                    {action.assigned_to && (
                        <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest bg-blue-50 px-2 py-1 rounded-lg border border-blue-100">
                            👤 {action.assigned_to}
                        </span>
                    )}

                    {action.due_date && (
                        <span className="text-[10px] font-black text-purple-600 uppercase tracking-widest bg-purple-50 px-2 py-1 rounded-lg border border-purple-100">
                            📅 {new Date(action.due_date).toLocaleDateString('fr-FR')}
                        </span>
                    )}
                </div>
            </div>

            <button
                onClick={() => setIsEditing(true)}
                className="mt-1 flex-shrink-0 text-gray-400 hover:text-indigo-600 transition-colors opacity-0 group-hover:opacity-100"
                title="Modifier l'action"
            >
                <Edit2 size={18} />
            </button>
        </div>
    );
}
