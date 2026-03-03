import { motion } from 'framer-motion'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { DashboardHeader } from '@/components/dashboard/DashboardHeader'
import { Beaker, ShoppingCart } from 'lucide-react'

const tests = [
  { id: 1, name: 'Complete Blood Count', price: '₹500', time: '24 hours' },
  { id: 2, name: 'Lipid Profile', price: '₹800', time: '24 hours' },
  { id: 3, name: 'Thyroid Function Test', price: '₹600', time: '24 hours' },
  { id: 4, name: 'Liver Function Test', price: '₹700', time: '24 hours' },
  { id: 5, name: 'Kidney Function Test', price: '₹700', time: '24 hours' },
  { id: 6, name: 'COVID-19 RT-PCR', price: '₹400', time: '12 hours' },
]

export default function LabTestsPage() {
  return (
    <div className="min-h-screen bg-[#0a0f1e]">
      <Sidebar />
      <DashboardHeader />

      <main className="ml-64 mt-16 p-8">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Lab Tests</h1>
            <p className="text-[#a1a1a1]">Book and track your laboratory tests</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tests.map((test) => (
              <motion.div
                key={test.id}
                whileHover={{ y: -4 }}
                className="card group hover:border-[#00d4aa]/50"
              >
                <div className="flex items-start justify-between mb-4">
                  <Beaker className="w-8 h-8 text-[#00d4aa]" />
                  <span className="px-3 py-1 rounded-full bg-[#00d4aa]/10 text-[#00d4aa] text-xs font-medium">
                    {test.time}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{test.name}</h3>
                <div className="mb-4">
                  <p className="text-2xl font-bold text-[#00d4aa]">{test.price}</p>
                  <p className="text-[#a1a1a1] text-sm">Results in {test.time}</p>
                </div>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full btn-primary flex items-center justify-center gap-2"
                >
                  <ShoppingCart size={18} />
                  Add to Cart
                </motion.button>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </main>
    </div>
  )
}
