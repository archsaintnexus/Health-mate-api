import { motion } from 'framer-motion'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { DashboardHeader } from '@/components/dashboard/DashboardHeader'
import { Pill, Search, ShoppingCart } from 'lucide-react'

const medications = [
  { id: 1, name: 'Aspirin 500mg', dosage: '100 tablets', price: '₹120', rating: 4.8 },
  { id: 2, name: 'Ibuprofen 400mg', dosage: '50 tablets', price: '₹85', rating: 4.7 },
  { id: 3, name: 'Paracetamol 650mg', dosage: '60 tablets', price: '₹65', rating: 4.9 },
  { id: 4, name: 'Vitamin C 1000mg', dosage: '30 tablets', price: '₹145', rating: 4.6 },
  { id: 5, name: 'Calcium + Vitamin D', dosage: '60 tablets', price: '₹250', rating: 4.8 },
  { id: 6, name: 'Multivitamin', dosage: '30 capsules', price: '₹180', rating: 4.7 },
]

export default function PharmacyPage() {
  return (
    <div className="min-h-screen bg-[#0a0f1e]">
      <Sidebar />
      <DashboardHeader />

      <main className="ml-64 mt-16 p-8">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Pharmacy</h1>
            <p className="text-[#a1a1a1]">Order medications with home delivery</p>
          </div>

          <div className="card mb-8">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#a1a1a1]" size={20} />
              <input
                type="text"
                placeholder="Search medications..."
                className="input-field pl-10"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {medications.map((med) => (
              <motion.div
                key={med.id}
                whileHover={{ y: -4 }}
                className="card group hover:border-[#00d4aa]/50"
              >
                <div className="flex items-center justify-between mb-4">
                  <Pill className="w-8 h-8 text-[#00d4aa]" />
                  <div className="flex items-center gap-1">
                    <span className="text-yellow-400">★</span>
                    <span className="text-white font-medium">{med.rating}</span>
                  </div>
                </div>
                <h3 className="text-lg font-bold text-white mb-1">{med.name}</h3>
                <p className="text-[#a1a1a1] text-sm mb-4">{med.dosage}</p>
                <div className="flex justify-between items-center">
                  <p className="text-2xl font-bold text-[#00d4aa]">{med.price}</p>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    className="p-2 bg-[#00d4aa]/10 rounded-lg text-[#00d4aa] hover:bg-[#00d4aa]/20 transition-all"
                  >
                    <ShoppingCart size={20} />
                  </motion.button>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </main>
    </div>
  )
}
