import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Landing() {
    const { isAuthenticated } = useAuth();
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
    const [targetPosition, setTargetPosition] = useState({ x: 0, y: 0 });
    const [expandedFaq, setExpandedFaq] = useState(0);

    const getStartedLink = isAuthenticated ? "/create" : "/signup";

    // Smooth cursor following with delay (lerp interpolation)
    useEffect(() => {
        const handleMouseMove = (e) => {
            setTargetPosition({ x: e.clientX, y: e.clientY });
        };

        window.addEventListener('mousemove', handleMouseMove);

        // Smooth animation with lerp (linear interpolation)
        const animatePosition = () => {
            setMousePosition(prev => ({
                x: prev.x + (targetPosition.x - prev.x) * 0.1, // 0.1 = smooth factor
                y: prev.y + (targetPosition.y - prev.y) * 0.1
            }));
        };

        const interval = setInterval(animatePosition, 16); // ~60fps

        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            clearInterval(interval);
        };
    }, [targetPosition]);

    const howItWorks = [
        {
            step: "1",
            title: "Enregistrez Votre Réunion",
            description: "Connectez simplement votre compte Zoom. Vos réunions sont automatiquement capturées sans que vous ayez à faire quoi que ce soit. Concentrez-vous sur votre discussion, nous nous occupons du reste."
        },
        {
            step: "2",
            title: "L'Intelligence Artificielle Analyse",
            description: "Une fois votre réunion terminée, notre système transforme automatiquement l'enregistrement en texte puis l'analyse. Il identifie les tâches à faire, les décisions prises et les questions soulevées."
        },
        {
            step: "3",
            title: "Recevez Votre Rapport",
            description: "Vous recevez un rapport complet contenant tout ce qui s'est dit d'important. Téléchargez-le, consultez-le en ligne, et partagez-le avec votre équipe. Les tâches sont automatiquement assignées aux bonnes personnes."
        }
    ];

    const features = [
        {
            title: "Capture Automatique des Réunions",
            description: "Vos réunions Zoom sont enregistrées automatiquement. Plus besoin de penser à appuyer sur un bouton."
        },
        {
            title: "Transformation en Texte",
            description: "L'audio de vos réunions est converti en texte écrit avec une grande précision, même avec plusieurs personnes qui parlent."
        },
        {
            title: "Extraction des Tâches",
            description: "Le système identifie automatiquement qui doit faire quoi et pour quand. Chacun reçoit sa liste de tâches."
        },
        {
            title: "Historique des Décisions",
            description: "Toutes les décisions importantes sont sauvegardées et facilement retrouvables. Fini les 'qui a décidé ça ?'"
        },
        {
            title: "Rapports Détaillés",
            description: "Obtenez un compte-rendu professionnel de chaque réunion, prêt à être partagé ou archivé."
        },
        {
            title: "Alertes par Email",
            description: "Les participants reçoivent automatiquement un email avec leurs actions à réaliser après chaque réunion."
        }
    ];

    const offers = [
        {
            title: "Analyse Intelligente Approfondie",
            description: "Notre système utilise plusieurs assistants spécialisés qui travaillent ensemble pour extraire chaque information importante de vos réunions."
        },
        {
            title: "Conversion Audio Précise",
            description: "L'audio de vos réunions est transformé en texte avec une très grande précision, même dans des conditions difficiles."
        },
        {
            title: "Suivi Simplifié",
            description: "Recevez des rappels automatiques pour ne jamais oublier une tâche ou une décision importante prise en réunion."
        }
    ];

    const useCases = [
        { label: "Réunions d'Équipe" },
        { label: "Rendez-vous Client" },
        { label: "Comités de Direction" },
        { label: "Revues de Projet" },
        { label: "Réunions Quotidiennes" },
        { label: "Sessions de Brainstorming" }
    ];

    const faqs = [
        {
            question: "Qu'est-ce que Syntra.ai ?",
            answer: "Syntra.ai est une solution qui vous aide à tirer le meilleur parti de vos réunions. Elle enregistre vos réunions Zoom, les transforme en texte, puis identifie automatiquement les informations importantes : qui doit faire quoi, quelles décisions ont été prises, et quelles questions restent sans réponse."
        },
        {
            question: "En quoi est-ce différent des autres outils ?",
            answer: "Contrairement aux outils qui font simplement un résumé basique, Syntra.ai utilise plusieurs assistants intelligents spécialisés. Chacun se concentre sur un aspect précis : les tâches, les décisions, les questions. Le résultat est beaucoup plus précis et utile."
        },
        {
            question: "Mes conversations sont-elles en sécurité ?",
            answer: "Absolument. Vos données sont protégées et chiffrées. Personne d'autre que vous ne peut accéder au contenu de vos réunions. Pour les organisations ayant des besoins spécifiques, nous proposons même des solutions sur vos propres serveurs."
        },
        {
            question: "Comment je commence à utiliser Syntra.ai ?",
            answer: "C'est très simple ! Créez votre compte, connectez votre compte Zoom, et c'est tout. Dès votre prochaine réunion, Syntra.ai s'occupent de tout. Vous recevrez automatiquement un rapport détaillé après chaque réunion."
        }
    ];

    return (
        <div className="relative min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 overflow-hidden">
            {/* Animated cursor follower */}
            <div
                className="fixed pointer-events-none z-50 w-96 h-96 rounded-full blur-3xl opacity-30 transition-opacity duration-300"
                style={{
                    background: 'radial-gradient(circle, rgba(139, 92, 246, 0.4) 0%, rgba(236, 72, 153, 0.3) 50%, transparent 70%)',
                    left: `${mousePosition.x - 192}px`,
                    top: `${mousePosition.y - 192}px`,
                }}
            />


            {/* Hero Section */}
            <section className="relative pt-20 pb-32 px-4 sm:px-6 lg:px-8">
                <div className="max-w-7xl mx-auto text-center">
                    <p className="text-sm font-medium text-purple-600 mb-4 tracking-wide uppercase">
                        Propulsé par l'Intelligence Artificielle
                    </p>
                    <h1 className="text-5xl md:text-7xl font-bold mb-6">
                        Ne perdez plus jamais{' '}
                        <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                            une information
                        </span>{' '}
                        de vos réunions
                    </h1>
                    <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
                        Enregistrez, analysez et transformez vos réunions en rapports exploitables automatiquement
                    </p>
                    <Link
                        to={getStartedLink}
                        className="inline-flex items-center px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-full transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
                    >
                        Commencer Maintenant
                    </Link>

                    {/* Hero Image Mockup - Linear Style */}
                    <div className="mt-20 relative perspective-container">
                        <div
                            className="relative mx-auto max-w-5xl transition-transform duration-500 ease-out"
                            style={{
                                transform: `
                                    perspective(2000px) 
                                    rotateX(${12 + (mousePosition.y / window.innerHeight - 0.5) * -3}deg) 
                                    rotateY(${-8 + (mousePosition.x / window.innerWidth - 0.5) * 5}deg)
                                    translateZ(0)
                                `,
                                transformStyle: 'preserve-3d'
                            }}
                        >
                            {/* Enhanced shadow layers for depth */}
                            <div className="absolute inset-0 bg-black/40 rounded-2xl blur-3xl translate-y-8 scale-95 -z-10"></div>
                            <div className="absolute inset-0 bg-gradient-to-br from-purple-600/20 via-pink-600/20 to-blue-600/20 rounded-2xl blur-2xl -z-10"></div>

                            {/* Dashboard Interface Image */}
                            <div className="relative rounded-2xl overflow-hidden shadow-2xl border border-gray-800/50">
                                <img
                                    src="/dashboard-mockup.png"
                                    alt="Syntra.ai Interface"
                                    className="w-full h-auto"
                                    style={{
                                        boxShadow: '0 50px 100px -20px rgba(0, 0, 0, 0.5), 0 30px 60px -30px rgba(0, 0, 0, 0.35)'
                                    }}
                                />

                                {/* Subtle overlay gradient for depth */}
                                <div className="absolute inset-0 bg-gradient-to-t from-black/10 via-transparent to-transparent pointer-events-none"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>


            {/* What We Offer Section */}
            <section className="relative py-20 px-4 sm:px-6 lg:px-8 bg-white/50 backdrop-blur-sm">
                <div className="max-w-7xl mx-auto">
                    <div className="grid md:grid-cols-2 gap-16 items-center">
                        {/* Left side - Browser Mockup */}
                        <div className="relative">
                            {/* Browser Chrome */}
                            <div className="bg-gray-900 rounded-t-2xl px-4 py-3 flex items-center justify-between">
                                <div className="flex space-x-2">
                                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                                    <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                                </div>
                                <div className="flex-1 mx-4">
                                    <div className="bg-gray-800 rounded px-3 py-1 text-xs text-gray-400 text-center max-w-xs mx-auto">
                                        syntra.ai
                                    </div>
                                </div>
                                <div className="w-3 h-3"></div>
                            </div>

                            {/* Interface Content */}
                            <div className="bg-white rounded-b-2xl shadow-2xl overflow-hidden border-x border-b border-gray-200">
                                <img
                                    src="/mockup-interface.png"
                                    alt="Syntra.ai Interface"
                                    className="w-full h-auto"
                                />
                            </div>
                        </div>

                        {/* Right side - Content */}
                        <div>
                            <p className="text-sm font-medium text-gray-500 mb-4">
                                Discover Our Value
                            </p>
                            <h2 className="text-4xl font-bold text-gray-900 mb-12">
                                What We{' '}
                                <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                                    Offer
                                </span>?
                            </h2>

                            <div className="space-y-8">
                                {offers.map((offer, index) => (
                                    <div key={index} className="border-l-4 border-purple-600 pl-6">
                                        <h3 className="text-xl font-bold text-gray-900 mb-2">
                                            {offer.title}
                                        </h3>
                                        <p className="text-gray-600 leading-relaxed">
                                            {offer.description}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </section>



            {/* Features Grid Section */}
            <section className="relative py-20 px-4 sm:px-6 lg:px-8">
                <div className="max-w-7xl mx-auto text-center">
                    <p className="text-sm font-medium text-purple-600 mb-4 tracking-wide uppercase">
                        Fonctionnalités Complètes
                    </p>
                    <h2 className="text-4xl font-bold text-gray-900 mb-16">
                        Tout ce dont vous avez besoin
                    </h2>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {features.map((feature, index) => (
                            <div
                                key={index}
                                className="group bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 hover:border-purple-200 hover:-translate-y-2"
                            >
                                <h3 className="text-xl font-bold text-gray-900 mb-4">
                                    {feature.title}
                                </h3>
                                <p className="text-gray-600 leading-relaxed">
                                    {feature.description}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>


            {/* How It Works Section */}
            <section className="relative py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-900 via-gray-900 to-slate-800">
                <div className="max-w-5xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                            Comment Utiliser{' '}
                            <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                                Syntra.ai
                            </span>
                        </h2>
                    </div>

                    <div className="space-y-8">
                        {howItWorks.map((step, index) => (
                            <div key={index} className="flex items-start space-x-6 group">
                                <div className="flex-shrink-0">
                                    <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center shadow-lg group-hover:from-purple-400 group-hover:to-pink-400 transition-all duration-300">
                                        <span className="text-2xl font-bold text-white">{step.step}</span>
                                    </div>
                                </div>
                                <div className="flex-grow">
                                    <h3 className="text-2xl font-bold text-white mb-3">{step.title}</h3>
                                    <p className="text-lg text-gray-300 leading-relaxed">{step.description}</p>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="mt-12 text-center">
                        <p className="text-gray-400 text-sm">
                            Et vous êtes prêt ! Vous avez maintenant la transcription de votre réunion, disponible en quelques minutes.
                            De plus, avec notre service d'analyse, bénéficiez d'une analyse approfondie sans effort.
                        </p>
                    </div>
                </div>
            </section>

            {/* Use Cases Section */}
            <section className="relative py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-white to-purple-50/30">
                <div className="max-w-7xl mx-auto text-center">
                    <p className="text-sm font-medium text-purple-600 mb-4 tracking-wide uppercase">
                        Adaptable à Tous Types de Réunions
                    </p>
                    <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
                        Où que vous soyez,{' '}
                        <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                            quoi que vous fassiez
                        </span>
                    </h2>
                    <p className="text-xl text-gray-600 mb-16 max-w-3xl mx-auto">
                        Syntra.ai s'adapte à toutes vos situations professionnelles
                    </p>

                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 max-w-6xl mx-auto">
                        {useCases.map((useCase, index) => (
                            <div
                                key={index}
                                className="group bg-white rounded-xl px-6 py-8 shadow-sm hover:shadow-lg transition-all duration-300 border border-gray-100 hover:border-purple-200 cursor-pointer"
                            >
                                <p className="font-medium text-sm text-gray-800 text-center leading-tight">
                                    {useCase.label}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* FAQ Section */}
            <section className="relative py-20 px-4 sm:px-6 lg:px-8">
                <div className="max-w-4xl mx-auto">
                    <div className="text-center mb-16">
                        <p className="text-sm font-medium text-purple-600 mb-4 tracking-wide uppercase">
                            Aide & Support
                        </p>
                        <h2 className="text-4xl font-bold text-gray-900">
                            Questions Fréquemment Posées
                        </h2>
                    </div>

                    <div className="space-y-4">
                        {faqs.map((faq, index) => (
                            <div
                                key={index}
                                className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden"
                            >
                                <button
                                    onClick={() => setExpandedFaq(expandedFaq === index ? null : index)}
                                    className="w-full px-6 py-5 flex items-center justify-between hover:bg-gray-50 transition-colors duration-200"
                                >
                                    <span className="font-semibold text-left text-gray-900">
                                        {index + 1}. {faq.question}
                                    </span>
                                    <span className={`text-2xl font-light text-purple-600 transition-transform duration-300 ${expandedFaq === index ? 'rotate-45' : ''}`}>
                                        +
                                    </span>
                                </button>
                                {expandedFaq === index && (
                                    <div className="px-6 pb-5 text-gray-600 border-t border-gray-100 pt-4">
                                        {faq.answer}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </section>
            <section className="relative bg-white overflow-hidden">

                {/* CTA Content */}
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 relative z-10">
                    <div className="max-w-2xl">
                        <h2 className="text-5xl font-bold text-gray-900 mb-6">
                            Prêt à transformer vos réunions ?
                        </h2>
                        <p className="text-xl text-gray-600 mb-8">
                            Commencez dès maintenant et ne perdez plus jamais une information importante
                        </p>
                        <Link
                            to={getStartedLink}
                            className="inline-flex items-center px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl"
                        >
                            Commencer Gratuitement
                        </Link>
                    </div>
                </div>
            </section>
        </div>
    );
}
