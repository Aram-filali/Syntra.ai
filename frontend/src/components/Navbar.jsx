import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { Search } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
    const location = useLocation();
    const navigate = useNavigate();
    const { user, isAuthenticated, logout } = useAuth();
    const [activeDropdown, setActiveDropdown] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');



    const isActive = (path) => {
        return location.pathname === path;
    };

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    const handleSearch = (e) => {
        e.preventDefault();
        if (searchQuery.trim().length >= 2) {
            navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
            setSearchQuery('');
        }
    };

    const menuItems = [
        {
            label: 'Fonctionnalités',
            hasDropdown: true,
            items: ['Analyse IA', 'Transcription', 'Rapports']
        },
        {
            label: 'Intégrations',
            hasDropdown: true,
            items: ['Zoom', 'Teams', 'Google Meet']
        },
        {
            label: 'Solutions',
            hasDropdown: true,
            items: ['Entreprises', 'Équipes', 'Particuliers']
        },
        {
            label: 'Ressources',
            hasDropdown: false,
            path: '/resources'
        },
        {
            label: 'Documentation',
            hasDropdown: false,
            path: '/docs'
        },
        {
            label: 'À propos',
            hasDropdown: true,
            items: ['Notre mission', 'Équipe', 'Contact']
        }
    ];

    return (
        <nav className="bg-white/80 backdrop-blur-xl border-b border-gray-100 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-20">
                    {/* Logo */}
                    <div className="flex items-center">
                        <Link to="/" className="flex items-center group">
                            <img 
                                src="/syntra-logo.png" 
                                alt="Syntra.ai Logo" 
                                className="h-12 w-auto group-hover:scale-110 transition-transform duration-300"
                            />
                        </Link>
                    </div>

                    {/* Navigation Menu - Only show on landing page */}
                    {location.pathname === '/' && (
                        <div className="hidden lg:flex items-center space-x-2">
                            {menuItems.map((item, index) => (
                                <div
                                    key={index}
                                    className="relative"
                                    onMouseEnter={() => item.hasDropdown && setActiveDropdown(index)}
                                    onMouseLeave={() => setActiveDropdown(null)}
                                >
                                    {item.hasDropdown ? (
                                        <>
                                            <button className="flex items-center space-x-1 px-4 py-2 text-sm font-bold text-gray-600 hover:text-indigo-600 transition-colors rounded-lg hover:bg-gray-50">
                                                <span>{item.label}</span>
                                                <svg
                                                    className={`w-4 h-4 transition-transform duration-200 ${activeDropdown === index ? 'rotate-180' : ''}`}
                                                    fill="none"
                                                    stroke="currentColor"
                                                    viewBox="0 0 24 24"
                                                >
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                                </svg>
                                            </button>

                                            {/* Dropdown Menu */}
                                            {activeDropdown === index && (
                                                <div className="absolute left-0 mt-1 w-56 bg-white rounded-2xl shadow-xl border border-gray-100 py-3 px-2">
                                                    {item.items.map((subItem, subIndex) => (
                                                        <a
                                                            key={subIndex}
                                                            href="#"
                                                            className="flex items-center px-4 py-3 text-sm font-semibold text-gray-600 hover:bg-indigo-50 hover:text-indigo-600 transition-all rounded-xl"
                                                        >
                                                            {subItem}
                                                        </a>
                                                    ))}
                                                </div>
                                            )}
                                        </>
                                    ) : (
                                        <Link
                                            to={item.path || '#'}
                                            className="px-4 py-2 text-sm font-bold text-gray-600 hover:text-indigo-600 transition-colors rounded-lg hover:bg-gray-50"
                                        >
                                            {item.label}
                                        </Link>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Right Side - Auth Buttons or User Menu */}
                    <div className="flex items-center space-x-6">
                        {/* Search Bar - Show when authenticated and not on landing page */}
                        {isAuthenticated && location.pathname !== '/' && (
                            <form onSubmit={handleSearch} className="hidden md:block">
                                <div className="relative">
                                    <input
                                        type="text"
                                        placeholder="Chercher un meeting..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        className="pl-10 pr-4 py-2.5 bg-gray-100 rounded-full text-sm font-medium text-gray-700 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all w-64"
                                    />
                                    <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                                </div>
                            </form>
                        )}

                        {isAuthenticated ? (
                            <>
                                {/* User Menu */}
                                <div className="flex items-center space-x-4">
                                    <div className="flex flex-col items-end hidden sm:flex">
                                        <span className="text-xs font-black text-gray-400 uppercase tracking-widest">Connecté</span>
                                        <span className="text-sm font-bold text-gray-900">{user?.username || user?.email}</span>
                                    </div>
                                    <Link to="/dashboard" className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center text-gray-600 hover:bg-indigo-50 hover:text-indigo-600 transition-colors">
                                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                        </svg>
                                    </Link>
                                    <button
                                        onClick={handleLogout}
                                        className="px-4 py-2 text-xs font-black uppercase tracking-widest text-red-500 hover:bg-red-50 rounded-lg transition-colors border border-transparent hover:border-red-100"
                                    >
                                        Logout
                                    </button>
                                </div>
                            </>
                        ) : (
                            <>
                                {location.pathname !== '/signin' && (
                                    <Link
                                        to="/signin"
                                        className="text-sm font-bold text-gray-600 hover:text-indigo-600 transition-colors"
                                    >
                                        Sign In
                                    </Link>
                                )}
                                {location.pathname !== '/signup' && (
                                    <Link
                                        to="/signup"
                                        className="btn-primary py-2.5 px-6 shadow-indigo-100 shadow-lg text-sm"
                                    >
                                        Get Started
                                    </Link>
                                )}
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}

