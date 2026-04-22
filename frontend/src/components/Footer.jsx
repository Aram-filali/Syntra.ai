import { Link, useLocation } from 'react-router-dom'

const Footer = () => {
    const location = useLocation();

    // Pages where the footer should be hidden (Dashboard, Create Meeting, Details)
    const hiddenRoutes = ['/dashboard', '/create', '/signin', '/signup'];
    const isMeetingDetailPage = location.pathname.startsWith('/meetings/');

    if (hiddenRoutes.includes(location.pathname) || isMeetingDetailPage) {
        return null;
    }

    return (

        <footer className="border-t border-gray-200 relative z-10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="grid grid-cols-2 md:grid-cols-5 gap-8">
                    {/* Logo & Description */}
                    <div className="col-span-2 md:col-span-1">
                        <Link to="/" className="flex items-center space-x-1 mb-4">
                            <span className="text-xl font-bold text-gray-900">
                                syntra
                            </span>
                            <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                                .ai
                            </span>
                        </Link>
                        <p className="text-sm text-gray-600">
                            Intelligence artificielle pour vos réunions professionnelles
                        </p>
                    </div>

                    {/* Product Links */}
                    <div>
                        <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
                            Produit
                        </h3>
                        <ul className="space-y-3">
                            <li>
                                <Link to="/features" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                    Fonctionnalités
                                </Link>
                            </li>
                            <li>
                                <Link to="/integrations" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                    Intégrations
                                </Link>
                            </li>
                            <li>
                                <Link to="/pricing" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                    Tarifs
                                </Link>
                            </li>
                            <li>
                                <Link to="/security" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                    Sécurité
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Solutions Links */}
                    <div>
                        <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
                            Solutions
                        </h3>
                        <ul className="space-y-3">
                            <li>
                                <Link to="/enterprises" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                    Entreprises
                                </Link>
                            </li>
                            <li>
                                <Link to="/teams" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                    Équipes
                                </Link>
                            </li>
                            <li>
                                <Link to="/education" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                    Éducation
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Resources Links */}
                    <div>
                        <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
                            Ressources
                        </h3>
                        <ul className="space-y-3">
                            <li>
                                <Link to="/docs" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                    Documentation
                                </Link>
                            </li>
                            <li>
                                <Link to="/blog" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                    Blog
                                </Link>
                            </li>
                            <li>
                                <Link to="/guides" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                    Guides
                                </Link>
                            </li>
                            <li>
                                <Link to="/support" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                    Support
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Company Links */}
                    <div>
                        <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
                            Entreprise
                        </h3>
                        <ul className="space-y-3">
                            <li>
                                <Link to="/about" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                    À propos
                                </Link>
                            </li>
                            <li>
                                <Link to="/careers" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                    Carrières
                                </Link>
                            </li>
                            <li>
                                <Link to="/contact" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                    Contact
                                </Link>
                            </li>
                            <li>
                                <Link to="/privacy" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                    Confidentialité
                                </Link>
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div className="mt-12 pt-8 border-t border-gray-200">
                    <div className="flex flex-col md:flex-row justify-between items-center">
                        <p className="text-sm text-gray-500">
                            © 2026 Syntra.ai. Tous droits réservés.
                        </p>
                        <div className="flex space-x-6 mt-4 md:mt-0">
                            <a href="#" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                Conditions d'utilisation
                            </a>
                            <a href="#" className="text-sm text-gray-600 hover:text-purple-600 transition-colors">
                                Politique de confidentialité
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </footer>
    )
}

export default Footer
