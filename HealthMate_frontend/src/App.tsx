import { Routes, Route, Navigate } from 'react-router-dom'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import LandingPage from '@/pages/LandingPage'
import SignupPage from '@/pages/SignupPage'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import AppointmentsPage from '@/pages/AppointmentsPage'
import TelehealthPage from '@/pages/TelehealthPage'
import RecordsPage from '@/pages/RecordsPage'
import LabTestsPage from '@/pages/LabTestsPage'
import PharmacyPage from '@/pages/PharmacyPage'
import HomeCarePages from '@/pages/HomeCarePages'
import ProfilePage from '@/pages/ProfilePage'
import NotFoundPage from '@/pages/NotFoundPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/login" element={<LoginPage />} />
      
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/dashboard/appointments" element={<ProtectedRoute><AppointmentsPage /></ProtectedRoute>} />
      <Route path="/dashboard/telehealth" element={<ProtectedRoute><TelehealthPage /></ProtectedRoute>} />
      <Route path="/dashboard/records" element={<ProtectedRoute><RecordsPage /></ProtectedRoute>} />
      <Route path="/dashboard/lab-tests" element={<ProtectedRoute><LabTestsPage /></ProtectedRoute>} />
      <Route path="/dashboard/pharmacy" element={<ProtectedRoute><PharmacyPage /></ProtectedRoute>} />
      <Route path="/dashboard/home-care" element={<ProtectedRoute><HomeCarePages /></ProtectedRoute>} />
      <Route path="/dashboard/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
      
      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  )
}

export default App
