import { AlertCircle } from 'lucide-react';

export default function ErrorMessage({ message, onRetry }) {
    return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start">
                <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 mr-3" />
                <div className="flex-1">
                    <h3 className="text-sm font-medium text-red-800">Erreur</h3>
                    <div className="mt-1 text-sm text-red-700">
                        {typeof message === 'string' ? (
                            <p>{message}</p>
                        ) : Array.isArray(message) ? (
                            <ul className="list-disc pl-5 space-y-1">
                                {message.map((err, i) => (
                                    <li key={i}>
                                        {typeof err === 'object'
                                            ? (err.msg || JSON.stringify(err))
                                            : err}
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p>{message?.msg || JSON.stringify(message)}</p>
                        )}
                    </div>
                    {onRetry && (
                        <button
                            onClick={onRetry}
                            className="mt-3 text-sm font-medium text-red-800 hover:text-red-900 underline"
                        >
                            Réessayer
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
