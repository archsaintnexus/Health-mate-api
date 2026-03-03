import { motion } from 'framer-motion'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { DashboardHeader } from '@/components/dashboard/DashboardHeader'
import { Calendar, MapPin, Clock } from 'lucide-react'

const mockDoctors = [
  {
    id: 1,
    name: 'Dr. Sarah Anderson',
    specialty: 'Cardiology',
    available: ['2024-03-10', '2024-03-11'],
    image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop',
  },
  {
    id: 2,
    name: 'Dr. James Mitchell',
    specialty: 'Orthopedics',
    available: ['2024-03-10', '2024-03-12'],
    image: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop',
  },
  {
    id: 3,
    name: 'Dr. Emily Chen',
    specialty: 'Pediatrics',
    available: ['2024-03-11', '2024-03-13'],
    image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop',
  },
]

export default function AppointmentsPage() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
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
          className="space-y-8"
        >
          <motion.div variants={itemVariants}>
            <h1 className="text-4xl font-bold text-white mb-2">Book Appointment</h1>
            <p className="text-[#a1a1a1]">Schedule a consultation with our healthcare professionals</p>
          </motion.div>

          <motion.div variants={itemVariants} className="card">
            <h2 className="text-2xl font-bold text-white mb-6">Search & Book</h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
              <div className="space-y-2">
                <label className="text-white font-medium text-sm">Specialty</label>
                <select className="input-field">
                  <option>Cardiology</option>
                  <option>Orthopedics</option>
                  <option>Pediatrics</option>
                  <option>Neurology</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-white font-medium text-sm">Date</label>
                <input type="date" className="input-field" />
              </div>
              <div className="space-y-2">
                <label className="text-white font-medium text-sm">Time</label>
                <select className="input-field">
                  <option>Morning (9-12)</option>
                  <option>Afternoon (12-5)</option>
                  <option>Evening (5-8)</option>
                </select>
              </div>
            </div>
            <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} className="btn-primary">
              Search Appointments
            </motion.button>
          </motion.div>

          <motion.div variants={itemVariants}>
            <h2 className="text-2xl font-bold text-white mb-6">Available Doctors</h2>
            <motion.div
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
              variants={containerVariants}
            >
              {mockDoctors.map((doctor) => (
                <motion.div
                  key={doctor.id}
                  variants={itemVariants}
                  whileHover={{ y: -4 }}
                  className="card group hover:border-[#00d4aa]/50"
                >
                  <img
                    src={doctor.image}
                    alt={doctor.name}
                    className="w-full h-40 rounded-lg object-cover mb-4"
                  />
                  <h3 className="text-xl font-bold text-white mb-1">{doctor.name}</h3>
                  <p className="text-[#00d4aa] text-sm font-medium mb-4">{doctor.specialty}</p>

                  <div className="space-y-3 mb-4">
                    <div className="flex items-center gap-2 text-[#a1a1a1] text-sm">
                      <Clock size={16} />
                      <span>Available appointments</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {doctor.available.map((date) => (
                        <span key={date} className="px-3 py-1 rounded bg-white/5 text-white text-xs">
                          {date}
                        </span>
                      ))}
                    </div>
                  </div>

                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full btn-primary text-sm"
                  >
                    Book Now
                  </motion.button>
                </motion.div>
              ))}
            </motion.div>
          </motion.div>

          <motion.div variants={itemVariants}>
            <h2 className="text-2xl font-bold text-white mb-6">Upcoming Appointments</h2>
            <div className="card space-y-4">
              {[1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="pb-4 border-b border-[#2d2d2d] last:border-0 last:pb-0 flex justify-between items-start"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                >
                  <div className="flex-1">
                    <p className="text-white font-bold">Dr. Sarah Anderson - Cardiology</p>
                    <div className="flex gap-4 mt-2 text-[#a1a1a1] text-sm">
                      <span className="flex items-center gap-1">
                        <Calendar size={14} /> March 15, 2024
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock size={14} /> 10:00 AM
                      </span>
                    </div>
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-4 py-2 rounded bg-white/10 text-white hover:bg-white/20 transition-all"
                  >
                    Reschedule
                  </motion.button>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </motion.div>
      </main>
    </div>
  )
}
