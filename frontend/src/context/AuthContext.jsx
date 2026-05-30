import { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext();

const DEFAULT_API_BASE_URL = import.meta.env.PROD
    ? 'https://syntraai-production.up.railway.app/api'
    : 'http://localhost:8000/api';

const API_BASE_URL = (import.meta.env.VITE_API_URL || DEFAULT_API_BASE_URL).replace(/\/$/, '');
const API_URL = `${API_BASE_URL}/auth`;

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (token) {
            verifyToken();
        } else {
            setLoading(false);
        }
    }, []);

    const verifyToken = async () => {
        try {
            const response = await fetch(`${API_URL}/verify-token`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setUser(data);
            } else {
                logout();
            }
        } catch (error) {
            console.error('Token verification failed:', error);
            logout();
        } finally {
            setLoading(false);
        }
    };

    const login = async (email, password) => {
        try {
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                setToken(data.access_token);
                setUser(data.user);
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('user', JSON.stringify(data.user));
                return { success: true, user: data.user };
            } else {
                return { success: false, error: data.detail || 'Login failed' };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: 'Network error. Please try again.' };
        }
    };

    const register = async (email, username, password, fullName) => {
        try {
            const response = await fetch(`${API_URL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email,
                    username,
                    password,
                    full_name: fullName
                }),
            });

            const data = await response.json();

            if (response.ok) {
                // Store pending verification info
                localStorage.setItem('pending_verification_email', data.email);
                localStorage.setItem('pending_verification_user_id', data.user_id);
                
                return { 
                    success: true, 
                    requiresEmailVerification: true,
                    email: data.email,
                    user_id: data.user_id
                };
            } else {
                return { success: false, error: data.detail || 'Registration failed' };
            }
        } catch (error) {
            console.error('Registration error:', error);
            return { success: false, error: 'Network error. Please try again.' };
        }
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    };

    const value = {
        user,
        token,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!token
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
