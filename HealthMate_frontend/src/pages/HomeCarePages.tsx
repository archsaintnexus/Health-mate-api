import { motion } from 'framer-motion'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { DashboardHeader } from '@/components/dashboard/DashboardHeader'
import { Home, Clock, Users } from 'lucide-react'

const services = [
  {
    id: 1,
    title: 'Nursing Care',
    description: 'Professional nurses for wound care and monitoring',
    price: '₹2000/visit',
  },
  {
    id: 2,
    title: 'Physical Therapy',
    description: 'Rehabilitation and physiotherapy at your home',
    price: '₹1500/session',
  },
  {
    id: 3,
    title: 'Elderly Care',
    description: 'Compassionate care for senior citizens',
    price: '₹1800/day',
  },
  {
    id: 4,
    title: 'Post-Surgery Care',
    description: 'Professional care during recovery period',
    price: '₹3000/visit',
  },
]

export default function HomeCarePages() {
  return (
    <div className="min-h-screen bg-[#0a0f1e]">
      <Sidebar />
      <DashboardHeader />

      <main className="ml-64 mt-16 p-8">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Home Care Services</h1>
            <p className="text-[#a1a1a1]">Professional care at your doorstep</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {services.map((service) => (
              <motion.div
                key={service.id}
                whileHover={{ y: -4 }}
                className="card group hover:border-[#00d4aa]/50"
              >
                <Home className="w-8 h-8 text-[#00d4aa] mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">{service.title}</h3>
                <p className="text-[#a1a1a1] mb-4">{service.description}</p>
                <div className="mb-4">
                  <p className="text-2xl font-bold text-[#00d4aa]">{service.price}</p>
                </div>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full btn-primary"
                >
                  Book Service
                </motion.button>
              </motion.div>
            ))}
          </div>

          <div className="card">
            <h2 className="text-2xl font-bold text-white mb-6">Why Choose Our Home Care?</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <Users className="w-8 h-8 text-[#00d4aa] mb-3" />
                <h3 className="text-lg font-bold text-white mb-2">Trained Professionals</h3>
                <p className="text-[#a1a1a1] text-sm">Certified and experienced healthcare providers</p>
              </div>
              <div>
                <Clock className="w-8 h-8 text-[#00d4aa] mb-3" />
                <h3 className="text-lg font-bold text-white mb-2">Flexible Scheduling</h3>
                <p className="text-[#a1a1a1] text-sm">Services available 24/7 as per your needs</p>
              </div>
              <div>
                <Home className="w-8 h-8 text-[#00d4aa] mb-3" />
                <h3 className="text-lg font-bold text-white mb-2">Comfort of Home</h3>
                <p className="text-[#a1a1a1] text-sm">Receive care in the comfort of your own home</p>
              </div>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  )
}
