import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    // On ne fixe pas de Content-Type global ici, Axios s'en occupe par type de données
});

// Intercepteur pour ajouter le token aux requêtes
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Intercepteur pour gérer les erreurs globalement
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

// ===== MEETINGS API =====

export const meetingsAPI = {
    // Récupérer tous les meetings
    getAll: async () => {
        const response = await apiClient.get('/meetings/');
        return response.data;
    },

    // Récupérer un meeting spécifique
    getById: async (id) => {
        const response = await apiClient.get(`/meetings/${id}`);
        return response.data;
    },

    // Créer un nouveau meeting
    create: async (meetingData) => {
        const response = await apiClient.post('/meetings/', meetingData);
        return response.data;
    },

    // Créer un meeting avec upload de fichier
    createWithFile: async (formData) => {
        const response = await apiClient.post('/meetings/upload', formData);
        return response.data;
    },

    // Supprimer un meeting
    delete: async (id) => {
        const response = await apiClient.delete(`/meetings/${id}`);
        return response.data;
    },

    // Ajouter une transcription
    addTranscription: async (id, transcriptionData) => {
        const response = await apiClient.post(
            `/meetings/${id}/transcription`,
            transcriptionData
        );
        return response.data;
    },

    // Récupérer la transcription
    getTranscription: async (id) => {
        const response = await apiClient.get(`/meetings/${id}/transcription`);
        return response.data;
    },

    // Analyser un meeting avec IA
    analyze: async (id) => {
        const response = await apiClient.post(`/meetings/${id}/analyze`);
        return response.data;
    },

    // Récupérer le summary
    getSummary: async (id) => {
        const response = await apiClient.get(`/meetings/${id}/summary`);
        return response.data;
    },

    // Récupérer les actions
    getActions: async (id, status = null) => {
        const params = status ? { status } : {};
        const response = await apiClient.get(`/meetings/${id}/actions`, { params });
        return response.data;
    },

    // Mettre à jour le statut d'une action
    updateActionStatus: async (actionId, status) => {
        const response = await apiClient.patch(`/meetings/actions/${actionId}`, { status });
        return response.data;
    },

    // Mettre à jour complètement une action item
    updateActionItem: async (actionId, updateData) => {
        const response = await apiClient.patch(`/meetings/actions/${actionId}`, updateData);
        return response.data;
    },

    // Recherche globale dans les meetings
    search: async (query) => {
        const response = await apiClient.get('/meetings/search/global', { params: { q: query } });
        return response.data;
    },

    // Partager un meeting par email
    shareMeeting: async (meetingId, recipientEmails) => {
        const response = await apiClient.post(`/meetings/${meetingId}/share`, {
            recipient_emails: recipientEmails
        });
        return response.data;
    },

    // Mettre à jour les participants d'un meeting
    updateMeetingParticipants: async (meetingId, participants) => {
        const response = await apiClient.patch(`/meetings/${meetingId}`, {
            participants: participants
        });
        return response.data;
    },

    // Email verification methods
    verifyEmail: async (verifyData) => {
        const response = await apiClient.post('/auth/verify-email', verifyData);
        return response.data;
    },

    resendVerificationEmail: async (email) => {
        const response = await apiClient.post('/auth/resend-verification-email', {
            email: email
        });
        return response.data;
    },

    // Password reset methods
    forgotPassword: async (data) => {
        const response = await apiClient.post('/auth/forgot-password', data);
        return response.data;
    },

    resetPassword: async (data) => {
        const response = await apiClient.post('/auth/reset-password', data);
        return response.data;
    },
};

// ===== ZOOM API =====

export const zoomAPI = {
    // Récupérer l'URL de connexion Zoom
    getLoginUrl: async () => {
        const response = await apiClient.get('/zoom/login');
        return response.data.url;
    },

    // Échanger le code contre un token (si besoin côté client, sinon géré par callback backend)
    exchangeCode: async (code) => {
        const response = await apiClient.get(`/zoom/callback?code=${code}`);
        return response.data;
    },

    // Récupérer les enregistrements Zoom
    getRecordings: async () => {
        const response = await apiClient.get('/zoom/me/recordings');
        return response.data;
    },

    // Importer un enregistrement spécifique (automatique)
    importRecording: async (recordingData) => {
        const response = await apiClient.post('/zoom/import', recordingData);
        return response.data;
    },

    // Importer en mode hybride (manuel + meta Zoom)
    uploadHybrid: async (formData) => {
        const response = await apiClient.post('/zoom/upload-hybrid', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    },

    // Récupérer le type de compte Zoom (basic, pro, business)
    getAccountType: async () => {
        const response = await apiClient.get('/zoom/account-type');
        return response.data.account_type;
    }
};

// ===== POLLING HELPER =====

/**
 * Fonction helper pour implémenter le polling intelligent
 * @param {Function} fetchFunction - Fonction async qui récupère les données
 * @param {Function} shouldContinue - Fonction qui retourne true si on doit continuer le polling
 * @param {number} interval - Intervalle en millisecondes (default 10000 = 10s)
 * @param {number} maxRetries - Nombre max de tentatives (default Infinity)
 * @returns {Object} - { pollingId, stop } pour control du polling
 */
export const createPolling = (fetchFunction, shouldContinue, interval = 10000, maxRetries = Infinity) => {
    let pollingId = null;
    let retryCount = 0;
    let isRunning = true;

    const poll = async () => {
        if (!isRunning || retryCount >= maxRetries) {
            if (pollingId) clearInterval(pollingId);
            return;
        }

        try {
            const data = await fetchFunction();
            retryCount = 0; // Reset retry counter on success
            
            // Check if we should continue polling
            if (!shouldContinue(data)) {
                isRunning = false;
                if (pollingId) clearInterval(pollingId);
            }
        } catch (error) {
            retryCount++;
            console.error(`Polling error (attempt ${retryCount}):`, error.message);
            
            if (retryCount >= maxRetries) {
                isRunning = false;
                if (pollingId) clearInterval(pollingId);
            }
        }
    };

    // Initial fetch
    poll();

    // Start polling interval
    pollingId = setInterval(poll, interval);

    return {
        pollingId,
        stop: () => {
            isRunning = false;
            if (pollingId) clearInterval(pollingId);
        }
    };
};

export default apiClient;
