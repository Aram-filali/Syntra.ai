import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import MeetingDetail from './pages/MeetingDetail'
import CreateMeeting from './pages/CreateMeeting'
import SearchResults from './pages/SearchResults'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import AwaitingEmailVerification from './pages/AwaitingEmailVerification'
import VerifyEmail from './pages/VerifyEmail'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'

function App() {
    return (
        <Router>
            <AuthProvider>
                <div className="min-h-screen bg-white flex flex-col">
                    <Navbar />
                    <main className="flex-grow">
                        <Routes>
                            {/* Auth Routes */}
                            <Route path="/signin" element={<SignIn />} />
                            <Route path="/signup" element={<SignUp />} />
                            <Route path="/awaiting-email-verification" element={<AwaitingEmailVerification />} />
                            <Route path="/verify-email" element={<VerifyEmail />} />
                            <Route path="/forgot-password" element={<ForgotPassword />} />
                            <Route path="/reset-password" element={<ResetPassword />} />

                            {/* Main Routes */}
                            <Route path="/" element={<Landing />} />
                            <Route path="/dashboard" element={<Dashboard />} />
                            <Route path="/meetings/:id" element={<MeetingDetail />} />
                            <Route path="/create" element={<CreateMeeting />} />
                            <Route path="/search" element={<SearchResults />} />
                        </Routes>
                    </main>
                    <Footer />
                </div>
            </AuthProvider>
        </Router>
    )
}

export default App
