import { Users, Plus, X } from 'lucide-react';
import { meetingsAPI } from '../api/client';
import { useState } from 'react';

export default function ParticipantsPanel({ meetingId, initialParticipants = [], onParticipantsChange }) {
    const [participants, setParticipants] = useState(initialParticipants);
    const [isEditing, setIsEditing] = useState(false);
    const [newParticipant, setNewParticipant] = useState('');
    const [newParticipantEmail, setNewParticipantEmail] = useState('');
    const [isUpdating, setIsUpdating] = useState(false);
    const [error, setError] = useState('');

    const normalizeParticipant = (participant) => {
        if (typeof participant === 'string') {
            if (participant.includes('@')) {
                return { name: participant, email: participant };
            }
            return { name: participant, email: '' };
        }

        if (participant && typeof participant === 'object') {
            return {
                ...participant,
                name: participant.name || participant.email || 'Participant',
                email: participant.email || ''
            };
        }

        return { name: 'Participant', email: '' };
    };

    const handleAddParticipant = async (e) => {
        e.preventDefault();
        if (!newParticipant.trim()) {
            setError('Veuillez entrer un nom');
            return;
        }

        if (newParticipantEmail.trim()) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(newParticipantEmail.trim())) {
                setError('Format email invalide');
                return;
            }
        }

        setIsUpdating(true);
        setError('');

        try {
            const updatedParticipants = [
                ...participants,
                {
                    name: newParticipant.trim(),
                    email: newParticipantEmail.trim(),
                    added_at: new Date().toISOString()
                }
            ];
            await meetingsAPI.updateMeetingParticipants(meetingId, updatedParticipants);
            setParticipants(updatedParticipants);
            if (onParticipantsChange) {
                onParticipantsChange(updatedParticipants);
            }
            setNewParticipant('');
            setNewParticipantEmail('');
        } catch (err) {
            setError('Erreur lors de l\'ajout du participant');
            console.error(err);
        } finally {
            setIsUpdating(false);
        }
    };

    const handleRemoveParticipant = async (index) => {
        setIsUpdating(true);
        try {
            const updatedParticipants = participants.filter((_, i) => i !== index);
            await meetingsAPI.updateMeetingParticipants(meetingId, updatedParticipants);
            setParticipants(updatedParticipants);
            if (onParticipantsChange) {
                onParticipantsChange(updatedParticipants);
            }
        } catch (err) {
            console.error('Erreur lors de la suppression du participant:', err);
        } finally {
            setIsUpdating(false);
        }
    };

    return (
        <div className="bg-white border border-gray-100 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <Users className="w-5 h-5 text-blue-600" />
                    </div>
                    <h3 className="text-lg font-black text-gray-900">Participants</h3>
                </div>
                <button
                    onClick={() => setIsEditing(!isEditing)}
                    className={`px-4 py-2 font-black rounded-lg transition-all text-sm uppercase tracking-widest ${
                        isEditing
                            ? 'bg-red-100 text-red-700 hover:bg-red-200'
                            : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                    }`}
                >
                    {isEditing ? 'Fermer' : 'Modifier'}
                </button>
            </div>

            {/* Participants List */}
            <div className="space-y-2 mb-6">
                {participants.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">Aucun participant ajouté</p>
                ) : (
                    participants.map((rawParticipant, index) => {
                        const participant = normalizeParticipant(rawParticipant);
                        return (
                            <div
                                key={index}
                                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100 hover:border-gray-200 group"
                            >
                                <div className="flex items-center gap-3">
                                    <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-indigo-600 rounded-full flex items-center justify-center text-white text-xs font-black">
                                        {participant.name.charAt(0).toUpperCase()}
                                    </div>
                                    <div>
                                        <p className="font-bold text-gray-900">{participant.name}</p>
                                        {participant.email && (
                                            <p className="text-xs text-gray-500">{participant.email}</p>
                                        )}
                                    </div>
                                </div>
                                {isEditing && (
                                    <button
                                        onClick={() => handleRemoveParticipant(index)}
                                        disabled={isUpdating}
                                        className="text-gray-400 hover:text-red-600 transition-colors opacity-0 group-hover:opacity-100 disabled:opacity-50"
                                        title="Supprimer"
                                    >
                                        <X size={18} />
                                    </button>
                                )}
                            </div>
                        );
                    })
                )}
            </div>

            {/* Add Participant Form */}
            {isEditing && (
                <form onSubmit={handleAddParticipant} className="space-y-3 border-t border-gray-200 pt-4">
                    {error && (
                        <p className="text-sm text-red-600 font-bold bg-red-50 p-2 rounded-lg">{error}</p>
                    )}
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={newParticipant}
                            onChange={(e) => setNewParticipant(e.target.value)}
                            placeholder="Nom du participant"
                            disabled={isUpdating}
                            className="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                        />
                        <input
                            type="email"
                            value={newParticipantEmail}
                            onChange={(e) => setNewParticipantEmail(e.target.value)}
                            placeholder="Email (optionnel)"
                            disabled={isUpdating}
                            className="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                        />
                        <button
                            type="submit"
                            disabled={isUpdating || !newParticipant.trim()}
                            className="px-4 py-2 bg-blue-600 text-white font-black rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2 transition-all"
                        >
                            <Plus size={18} />
                            Ajouter
                        </button>
                    </div>
                </form>
            )}
        </div>
    );
}
