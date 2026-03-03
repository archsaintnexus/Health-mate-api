import { useState } from 'react'
import { motion } from 'framer-motion'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { DashboardHeader } from '@/components/dashboard/DashboardHeader'
import { User, Mail, Phone, MapPin, Edit2, Save } from 'lucide-react'
import { useAuth } from '@/lib/auth-context'

export default function ProfilePage() {
  const { firstName } = useAuth()
  const [isEditing, setIsEditing] = useState(false)

  return (
    <div className="min-h-screen bg-[#0a0f1e]">
      <Sidebar />
      <DashboardHeader />

      <main className="ml-64 mt-16 p-8">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-2xl">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Profile Settings</h1>
            <p className="text-[#a1a1a1] mb-8">Manage your personal information</p>
          </div>

          <div className="card mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Personal Information</h2>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsEditing(!isEditing)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
                  isEditing
                    ? 'bg-[#00d4aa] text-[#0a0f1e]'
                    : 'bg-white/10 text-white hover:bg-white/20'
                } transition-all`}
              >
                {isEditing ? (
                  <>
                    <Save size={18} /> Save Changes
                  </>
                ) : (
                  <>
                    <Edit2 size={18} /> Edit Profile
                  </>
                )}
              </motion.button>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="block text-white font-medium text-sm">First Name</label>
                  <input
                    type="text"
                    defaultValue={firstName || 'John'}
                    disabled={!isEditing}
                    className={`input-field ${!isEditing ? 'bg-[#0a0f1e] cursor-not-allowed' : ''}`}
                  />
                </div>
                <div className="space-y-2">
                  <label className="block text-white font-medium text-sm">Last Name</label>
                  <input
                    type="text"
                    defaultValue="Doe"
                    disabled={!isEditing}
                    className={`input-field ${!isEditing ? 'bg-[#0a0f1e] cursor-not-allowed' : ''}`}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="block text-white font-medium text-sm flex items-center gap-2">
                  <Mail size={16} /> Email
                </label>
                <input
                  type="email"
                  defaultValue="john@example.com"
                  disabled={!isEditing}
                  className={`input-field ${!isEditing ? 'bg-[#0a0f1e] cursor-not-allowed' : ''}`}
                />
              </div>

              <div className="space-y-2">
                <label className="block text-white font-medium text-sm flex items-center gap-2">
                  <Phone size={16} /> Phone Number
                </label>
                <input
                  type="tel"
                  defaultValue="+91 98765 43210"
                  disabled={!isEditing}
                  className={`input-field ${!isEditing ? 'bg-[#0a0f1e] cursor-not-allowed' : ''}`}
                />
              </div>

              <div className="space-y-2">
                <label className="block text-white font-medium text-sm flex items-center gap-2">
                  <MapPin size={16} /> Address
                </label>
                <textarea
                  defaultValue="123 Main Street, City, State 12345"
                  disabled={!isEditing}
                  className={`input-field resize-none ${!isEditing ? 'bg-[#0a0f1e] cursor-not-allowed' : ''}`}
                  rows={3}
                />
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-2xl font-bold text-white mb-6">Security</h2>
            <div className="space-y-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full py-3 text-left px-4 rounded-lg border border-[#2d2d2d] hover:border-[#00d4aa]/50 text-white hover:text-[#00d4aa] transition-all"
              >
                Change Password
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full py-3 text-left px-4 rounded-lg border border-[#2d2d2d] hover:border-[#00d4aa]/50 text-white hover:text-[#00d4aa] transition-all"
              >
                Two-Factor Authentication
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full py-3 text-left px-4 rounded-lg border border-red-500/30 hover:border-red-500 hover:bg-red-500/10 text-white transition-all"
              >
                Delete Account
              </motion.button>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  )
}
