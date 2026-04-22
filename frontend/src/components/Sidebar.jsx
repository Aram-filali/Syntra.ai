import { Link } from 'react-router-dom';
import { Home, Sparkles, ListTodo, PieChart, Settings } from 'lucide-react';

export default function Sidebar() {
    return (
        <aside className="hidden lg:flex w-72 bg-white border-r border-gray-100 flex-col sticky top-0 h-screen">
            <div className="p-8">


                <nav className="space-y-2">
                    <button className="w-full flex items-center space-x-3 px-4 py-3 bg-indigo-50 text-indigo-700 rounded-xl font-bold transition-all">
                        <Home size={20} />
                        <span>Vue d'ensemble</span>
                    </button>
                    <button className="w-full flex items-center space-x-3 px-4 py-3 text-gray-500 hover:bg-gray-50 hover:text-gray-900 rounded-xl font-bold transition-all group">
                        <Sparkles size={20} className="group-hover:text-indigo-500" />
                        <span>Analyses IA</span>
                    </button>
                    <button className="w-full flex items-center space-x-3 px-4 py-3 text-gray-500 hover:bg-gray-50 hover:text-gray-900 rounded-xl font-bold transition-all group">
                        <ListTodo size={20} className="group-hover:text-indigo-500" />
                        <span>Actions à faire</span>
                    </button>
                    <button className="w-full flex items-center space-x-3 px-4 py-3 text-gray-500 hover:bg-gray-50 hover:text-gray-900 rounded-xl font-bold transition-all group">
                        <PieChart size={20} className="group-hover:text-indigo-500" />
                        <span>Statistiques</span>
                    </button>
                </nav>

                <div className="mt-10 pt-10 border-t border-gray-100">
                    <p className="px-4 text-[10px] font-black text-gray-400 uppercase tracking-widest mb-4">Préférences</p>
                    <button className="w-full flex items-center space-x-3 px-4 py-3 text-gray-500 hover:bg-gray-50 hover:text-gray-900 rounded-xl font-bold transition-all group">
                        <Settings size={20} className="group-hover:text-indigo-500" />
                        <span>Paramètres</span>
                    </button>
                </div>
            </div>

            <div className="mt-auto p-8">
                <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-2xl p-5 text-white relative overflow-hidden shadow-xl shadow-indigo-200">
                    <div className="absolute -right-4 -bottom-4 w-20 h-20 bg-white/10 rounded-full blur-2xl"></div>
                    <p className="text-xs font-bold text-indigo-100 uppercase tracking-widest mb-2">Plan Pro</p>
                    <p className="text-sm font-medium leading-relaxed mb-4">Boostez vos réunions avec le pack illimité.</p>
                    <button className="w-full py-2 bg-white text-indigo-600 rounded-lg text-xs font-black uppercase tracking-wider hover:bg-indigo-50 transition-colors">
                        Upgrade
                    </button>
                </div>
            </div>
        </aside>
    );
}
