import { useState, useRef } from 'react';
import { Copy, Check, Download } from 'lucide-react';

export default function TranscriptionViewer({ transcription }) {
    const [copiedId, setCopiedId] = useState(null);
    const [selectedSegment, setSelectedSegment] = useState(null);

    if (!transcription) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-500 font-medium">Aucune transcription disponible</p>
            </div>
        );
    }

    const segments = transcription.speaker_segments || [];

    const formatTime = (milliseconds) => {
        if (!milliseconds && milliseconds !== 0) return '--:--';
        const totalSeconds = Math.floor(milliseconds / 1000);
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;

        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    };

    const copyToClipboard = (text, id) => {
        navigator.clipboard.writeText(text);
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 2000);
    };

    const downloadTranscription = () => {
        // Format transcription as readable text
        let content = `TRANSCRIPTION\nDate: ${new Date().toLocaleDateString('fr-FR')}\n\n`;
        content += `========================================\n\n`;

        segments.forEach((segment, idx) => {
            const time = formatTime(segment.start);
            content += `[${time}] ${segment.speaker}:\n`;
            content += `${segment.text}\n\n`;
        });

        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `transcription-${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    // Color palette for speakers
    const speakerColors = {
        'Speaker A': 'from-indigo-100 to-indigo-50 border-indigo-200 text-indigo-700',
        'Speaker B': 'from-emerald-100 to-emerald-50 border-emerald-200 text-emerald-700',
        'Speaker C': 'from-purple-100 to-purple-50 border-purple-200 text-purple-700',
        'Speaker D': 'from-amber-100 to-amber-50 border-amber-200 text-amber-700',
        'Speaker E': 'from-rose-100 to-rose-50 border-rose-200 text-rose-700',
        'Speaker F': 'from-cyan-100 to-cyan-50 border-cyan-200 text-cyan-700',
    };

    const getColor = (speaker) => {
        // Extract speaker number (e.g., "Speaker 0" -> "Speaker A")
        if (speaker && speaker.includes('Speaker')) {
            const num = parseInt(speaker.match(/\d+/)?.[0] || 0);
            const letters = ['A', 'B', 'C', 'D', 'E', 'F'];
            const letter = letters[num % letters.length];
            const key = `Speaker ${letter}`;
            return speakerColors[key] || 'from-gray-100 to-gray-50 border-gray-200 text-gray-700';
        }
        return 'from-gray-100 to-gray-50 border-gray-200 text-gray-700';
    };

    return (
        <div className="h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between pb-6 border-b border-gray-200">
                <div>
                    <h3 className="text-lg font-black text-gray-900">Transcription Formatée</h3>
                    <p className="text-sm text-gray-500 mt-1">{segments.length} segments détectés</p>
                </div>
                <button
                    onClick={downloadTranscription}
                    className="flex items-center gap-2 px-4 py-2 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 transition-colors font-medium text-sm"
                >
                    <Download size={16} />
                    Télécharger
                </button>
            </div>

            {/* Transcription Content */}
            <div className="flex-1 overflow-y-auto mt-6">
                {segments.length > 0 ? (
                    <div className="space-y-6 pb-8">
                        {segments.map((segment, idx) => {
                            const isSelected = selectedSegment === idx;
                            const colorClasses = getColor(segment.speaker);

                            return (
                                <div
                                    key={idx}
                                    className={`group p-6 border-2 rounded-2xl transition-all cursor-pointer ${
                                        isSelected
                                            ? `bg-gradient-to-r ${colorClasses} border-opacity-100 shadow-md`
                                            : `bg-white border-gray-100 hover:border-indigo-200 hover:shadow-sm`
                                    }`}
                                    onClick={() => setSelectedSegment(isSelected ? null : idx)}
                                >
                                    {/* Speaker Badge & Time */}
                                    <div className="flex items-center justify-between mb-4">
                                        <div className="flex items-center gap-3">
                                            <span className={`px-3 py-1 rounded-lg font-black text-xs uppercase tracking-widest ${
                                                isSelected ? 'bg-white/50' : 'bg-gray-100'
                                            } ${isSelected ? '' : 'text-gray-600'}`}>
                                                {segment.speaker}
                                            </span>
                                            <span className={`text-xs font-bold ${isSelected ? 'text-gray-700' : 'text-gray-400'}`}>
                                                {formatTime(segment.start)}
                                            </span>
                                        </div>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                copyToClipboard(segment.text, idx);
                                            }}
                                            className={`opacity-0 group-hover:opacity-100 transition-opacity p-2 rounded-lg ${
                                                isSelected ? 'bg-white/30 hover:bg-white/50' : 'bg-gray-100 hover:bg-gray-200'
                                            }`}
                                        >
                                            {copiedId === idx ? (
                                                <Check size={16} className="text-emerald-600" />
                                            ) : (
                                                <Copy size={16} className={isSelected ? 'text-gray-700' : 'text-gray-500'} />
                                            )}
                                        </button>
                                    </div>

                                    {/* Text Content */}
                                    <p className={`leading-relaxed text-base ${
                                        isSelected
                                            ? 'font-medium text-gray-800'
                                            : 'text-gray-600 group-hover:text-gray-700'
                                    }`}>
                                        {segment.text}
                                    </p>

                                    {/* Confidence Badge (if available) */}
                                    {segment.confidence && (
                                        <div className="mt-3 flex items-center gap-2">
                                            <div className="h-1.5 flex-1 bg-gray-200 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-emerald-500 rounded-full transition-all"
                                                    style={{ width: `${Math.round(segment.confidence * 100)}%` }}
                                                />
                                            </div>
                                            <span className="text-xs text-gray-500 font-medium">
                                                {Math.round(segment.confidence * 100)}%
                                            </span>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <div className="text-center py-12">
                        <p className="text-gray-500 font-medium">Aucun segment de transcription</p>
                    </div>
                )}
            </div>

            {/* Full Text Preview */}
            {transcription.full_text && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                    <details className="group">
                        <summary className="cursor-pointer font-black text-gray-900 text-sm uppercase tracking-widest hover:text-indigo-600 transition-colors">
                            📄 Texte Complet
                        </summary>
                        <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200 max-h-48 overflow-y-auto">
                            <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap font-mono">
                                {transcription.full_text}
                            </p>
                        </div>
                    </details>
                </div>
            )}
        </div>
    );
}
