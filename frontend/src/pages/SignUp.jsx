import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function SignUp() {
    const navigate = useNavigate();
    const { register } = useAuth();

    const [formData, setFormData] = useState({
        email: '',
        username: '',
        fullName: '',
        password: '',
        confirmPassword: ''
    });
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const validateForm = () => {
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return false;
        }

        if (formData.password.length < 8) {
            setError('Password must be at least 8 characters');
            return false;
        }

        if (!/(?=.*[a-z])/.test(formData.password)) {
            setError('Password must contain at least one lowercase letter');
            return false;
        }

        if (!/(?=.*[A-Z])/.test(formData.password)) {
            setError('Password must contain at least one uppercase letter');
            return false;
        }

        if (!/(?=.*\d)/.test(formData.password)) {
            setError('Password must contain at least one number');
            return false;
        }

        if (formData.username.length < 3) {
            setError('Username must be at least 3 characters');
            return false;
        }

        return true;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!validateForm()) {
            return;
        }

        setLoading(true);

        const result = await register(
            formData.email,
            formData.username,
            formData.password,
            formData.fullName
        );

        if (result.success) {
            if (result.requiresEmailVerification) {
                navigate('/awaiting-email-verification');
            } else {
                navigate('/dashboard');
            }
        } else {
            setError(result.error);
        }

        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-white flex flex-col">
            {/* Header */}
            <div className="flex justify-between items-center px-8 py-6">
                <div className="flex items-center gap-2">
                    <div className=""></div>
                    <span className="text-2xl font-bold"></span>
                </div>
                <div className="text-sm">
                    <span className="text-gray-600">Déjà sur Syntra.ai ? </span>
                    <Link to="/signin" className="text-blue-600 hover:underline">
                        Connectez-vous à votre espace
                    </Link>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-grow flex items-center justify-center px-4 py-8">
                <div className="w-full max-w-md">
                    {/* Title */}
                    <div className="text-center mb-8">
                        <h1 className="text-5xl font-bold text-gray-900 mb-3">
                            First of all, enter your email address
                        </h1>
                        <p className="text-gray-600">
                            We suggest using the <strong>email address that you use at work</strong>.
                        </p>
                    </div>

                    {/* Sign Up Form */}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {/* Email Input */}
                        <div>
                            <input
                                type="email"
                                name="email"
                                placeholder="name@work-email.com"
                                value={formData.email}
                                onChange={handleChange}
                                required
                                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-purple-600 focus:outline-none text-gray-900 placeholder-gray-400"
                            />
                        </div>

                        {/* Username Input */}
                        <div>
                            <input
                                type="text"
                                name="username"
                                placeholder="Username (min. 3 characters)"
                                value={formData.username}
                                onChange={handleChange}
                                required
                                minLength={3}
                                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-purple-600 focus:outline-none text-gray-900 placeholder-gray-400"
                            />
                        </div>

                        {/* Full Name Input */}
                        <div>
                            <input
                                type="text"
                                name="fullName"
                                placeholder="Full Name (optional)"
                                value={formData.fullName}
                                onChange={handleChange}
                                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-purple-600 focus:outline-none text-gray-900 placeholder-gray-400"
                            />
                        </div>

                        {/* Password Input */}
                        <div className="relative">
                            <input
                                type={showPassword ? "text" : "password"}
                                name="password"
                                placeholder="Password (min. 8 chars, 1 uppercase, 1 lowercase, 1 number)"
                                value={formData.password}
                                onChange={handleChange}
                                required
                                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-purple-600 focus:outline-none text-gray-900 placeholder-gray-400"
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-sm text-gray-500 hover:text-gray-700"
                            >
                                {showPassword ? 'Hide' : 'Show'}
                            </button>
                        </div>

                        {/* Confirm Password Input */}
                        <div>
                            <input
                                type={showPassword ? "text" : "password"}
                                name="confirmPassword"
                                placeholder="Confirm Password"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                required
                                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-purple-600 focus:outline-none text-gray-900 placeholder-gray-400"
                            />
                        </div>

                        {/* Error Message */}
                        {error && (
                            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
                                {error}
                            </div>
                        )}

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-purple-700 hover:bg-purple-800 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Creating account...' : 'Continue'}
                        </button>
                    </form>

                    {/* Terms */}
                    <div className="mt-6 text-center text-xs text-gray-600">
                        <p>
                            By continuing, you're agreeing to our{' '}
                            <a href="#" className="text-blue-600 hover:underline">Customer Terms of Service</a>,{' '}
                            <a href="#" className="text-blue-600 hover:underline">User Terms of Service</a>, and{' '}
                            <a href="#" className="text-blue-600 hover:underline">Privacy Policy</a>.
                        </p>
                    </div>
                </div>
            </div>

        </div>
    );
}

export default SignUp;
