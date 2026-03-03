import { motion } from 'framer-motion'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { DashboardHeader } from '@/components/dashboard/DashboardHeader'
import { Video, Clock, User } from 'lucide-react'

export default function TelehealthPage() {
  return (
    <div className="min-h-screen bg-[#0a0f1e]">
      <Sidebar />
      <DashboardHeader />

      <main className="ml-64 mt-16 p-8">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Telehealth Consultations</h1>
            <p className="text-[#a1a1a1]">Connect with doctors via secure video calls</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <motion.div whileHover={{ y: -4 }} className="card">
              <Video className="w-8 h-8 text-[#00d4aa] mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">Schedule Video Call</h3>
              <p className="text-[#a1a1a1] mb-4">Book a video consultation with a healthcare provider</p>
              <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} className="btn-primary w-full">
                Schedule Now
              </motion.button>
            </motion.div>

            <motion.div whileHover={{ y: -4 }} className="card">
              <Clock className="w-8 h-8 text-[#00d4aa] mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">Upcoming Sessions</h3>
              <p className="text-[#a1a1a1] mb-4">View your scheduled telehealth sessions</p>
              <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} className="btn-secondary w-full">
                View Sessions
              </motion.button>
            </motion.div>

            <motion.div whileHover={{ y: -4 }} className="card">
              <User className="w-8 h-8 text-[#00d4aa] mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">My Doctors</h3>
              <p className="text-[#a1a1a1] mb-4">Access your trusted healthcare providers</p>
              <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} className="btn-secondary w-full">
                View List
              </motion.button>
            </motion.div>
          </div>

          <div className="card">
            <h2 className="text-2xl font-bold text-white mb-4">How Telehealth Works</h2>
            <div className="space-y-3 text-[#a1a1a1]">
              <p>✓ Book an appointment with a qualified doctor</p>
              <p>✓ Receive a video call link before your scheduled time</p>
              <p>✓ Connect securely via video call</p>
              <p>✓ Get prescriptions or medical advice digitally</p>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  )
}
