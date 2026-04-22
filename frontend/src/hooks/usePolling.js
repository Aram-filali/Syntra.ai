import { useEffect, useRef, useState } from 'react';

/**
 * Custom React hook for intelligent polling
 * Automatically handles polling lifecycle and cleanup
 * 
 * @param {Function} fetchFunction - Async function that fetches data
 * @param {Function} shouldContinuePolling - Function that returns true if polling should continue
 * @param {Object} options - Configuration options
 * @returns {Object} - { data, isLoading, error, isPolling, stopPolling, startPolling }
 */
export const usePolling = (
    fetchFunction,
    shouldContinuePolling,
    options = {}
) => {
    const {
        interval = 10000, // Default 10 seconds
        enabled = true, // Start polling automatically
        maxRetries = Infinity,
    } = options;

    const [data, setData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isPolling, setIsPolling] = useState(enabled);

    const pollingRef = useRef(null);
    const retryCountRef = useRef(0);
    const isRunningRef = useRef(enabled);

    const stopPolling = () => {
        isRunningRef.current = false;
        setIsPolling(false);
        if (pollingRef.current) {
            clearInterval(pollingRef.current);
        }
    };

    const startPolling = () => {
        if (isRunningRef.current) return; // Already polling
        isRunningRef.current = true;
        setIsPolling(true);
        retryCountRef.current = 0;
        performPoll();
    };

    const performPoll = async () => {
        if (!isRunningRef.current) return;

        if (retryCountRef.current >= maxRetries) {
            stopPolling();
            return;
        }

        try {
            setIsLoading(true);
            setError(null);
            const result = await fetchFunction();
            setData(result);
            retryCountRef.current = 0; // Reset on success

            // Check if we should continue polling
            if (shouldContinuePolling && !shouldContinuePolling(result)) {
                stopPolling();
            }
        } catch (err) {
            retryCountRef.current++;
            console.error(`Polling error (attempt ${retryCountRef.current}):`, err.message);
            setError(err);

            if (retryCountRef.current >= maxRetries) {
                stopPolling();
            }
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (!enabled) return;

        // Initial fetch
        performPoll();

        // Setup interval for subsequent polls
        pollingRef.current = setInterval(() => {
            if (isRunningRef.current) {
                performPoll();
            }
        }, interval);

        // Cleanup
        return () => {
            if (pollingRef.current) {
                clearInterval(pollingRef.current);
            }
            isRunningRef.current = false;
        };
    }, [enabled, interval]); // Only depend on enabled and interval

    return {
        data,
        isLoading,
        error,
        isPolling,
        stopPolling,
        startPolling,
    };
};

export default usePolling;
