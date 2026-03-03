import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { DashboardHeader } from '@/components/dashboard/DashboardHeader'
import { Calendar, Video, FileText, Beaker, Pill, Home } from 'lucide-react'

const services = [
  {
    icon: Calendar,
    title: 'Appointments',
    description: 'Book and manage consultations',
    path: '/dashboard/appointments',
    color: 'from-[#00d4aa] to-[#0ea5e9]',
  },
  {
    icon: Video,
    title: 'Telehealth',
    description: 'Video consultations with doctors',
    path: '/dashboard/telehealth',
    color: 'from-[#0ea5e9] to-[#00d4aa]',
  },
  {
    icon: FileText,
    title: 'Medical Records',
    description: 'Access your health history',
    path: '/dashboard/records',
    color: 'from-[#00d4aa] to-[#0ea5e9]',
  },
  {
    icon: Beaker,
    title: 'Lab Tests',
    description: 'Book and track test results',
    path: '/dashboard/lab-tests',
    color: 'from-[#0ea5e9] to-[#00d4aa]',
  },
  {
    icon: Pill,
    title: 'Pharmacy',
    description: 'Order and refill medications',
    path: '/dashboard/pharmacy',
    color: 'from-[#00d4aa] to-[#0ea5e9]',
  },
  {
    icon: Home,
    title: 'Home Care',
    description: 'Professional care at home',
    path: '/dashboard/home-care',
    color: 'from-[#0ea5e9] to-[#00d4aa]',
  },
]

export default function DashboardPage() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6 },
    },
  }

  return (
    <div className="min-h-screen bg-[#0a0f1e]">
      <Sidebar />
      <DashboardHeader />

      <main className="ml-64 mt-16 p-8">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-12"
        >
          <motion.div variants={itemVariants}>
            <h1 className="text-4xl font-bold text-white mb-2">Dashboard</h1>
            <p className="text-[#a1a1a1]">Manage all your healthcare services in one place</p>
          </motion.div>

          <motion.div
            variants={itemVariants}
            className="bg-gradient-to-r from-[#00d4aa]/10 to-[#0ea5e9]/10 border border-[#00d4aa]/30 rounded-lg p-8"
          >
            <h2 className="text-2xl font-bold text-white mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="btn-primary text-left"
              >
                Schedule Appointment
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="btn-secondary text-left"
              >
                Start Telehealth
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="btn-secondary text-left"
              >
                View Records
              </motion.button>
            </div>
          </motion.div>

          <motion.div variants={itemVariants}>
            <h2 className="text-2xl font-bold text-white mb-6">Our Services</h2>
            <motion.div
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
              variants={containerVariants}
            >
              {services.map((service, index) => {
                const Icon = service.icon
                return (
                  <Link key={index} to={service.path}>
                    <motion.div
                      variants={itemVariants}
                      whileHover={{ y: -8 }}
                      className="card group hover:border-[#00d4aa]/50 transition-all cursor-pointer"
                    >
                      <div
                        className={`w-14 h-14 rounded-lg bg-gradient-to-br ${service.color} p-0.5 mb-4`}
                      >
                        <div className="w-full h-full rounded-lg bg-[#0a0f1e] flex items-center justify-center">
                          <Icon className="w-7 h-7 text-[#00d4aa]" />
                        </div>
                      </div>
                      <h3 className="text-xl font-bold text-white mb-2">{service.title}</h3>
                      <p className="text-[#a1a1a1] text-sm">{service.description}</p>
                    </motion.div>
                  </Link>
                )
              })}
            </motion.div>
          </motion.div>

          <motion.div variants={itemVariants}>
            <h2 className="text-2xl font-bold text-white mb-6">Recent Activity</h2>
            <div className="card space-y-4">
              {[1, 2, 3].map((i) => (
                <motion.div
                  key={i}
                  className="pb-4 border-b border-[#2d2d2d] last:border-0 last:pb-0 flex justify-between items-center"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                >
                  <div>
                    <p className="text-white font-medium">Appointment with Dr. Smith</p>
                    <p className="text-[#a1a1a1] text-sm">March 10, 2024 at 2:00 PM</p>
                  </div>
                  <span className="px-3 py-1 rounded-full bg-[#00d4aa]/10 text-[#00d4aa] text-sm font-medium">
                    Completed
                  </span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </motion.div>
      </main>
    </div>
  )
}
