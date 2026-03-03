import { motion } from 'framer-motion'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { DashboardHeader } from '@/components/dashboard/DashboardHeader'
import { FileText, Download, Search } from 'lucide-react'

const records = [
  { id: 1, title: 'Blood Work Report', date: 'March 5, 2024', type: 'Lab Result' },
  { id: 2, title: 'General Checkup Notes', date: 'February 28, 2024', type: 'Consultation' },
  { id: 3, title: 'X-Ray Report', date: 'February 20, 2024', type: 'Imaging' },
  { id: 4, title: 'Prescription History', date: 'February 15, 2024', type: 'Prescription' },
]

export default function RecordsPage() {
  return (
    <div className="min-h-screen bg-[#0a0f1e]">
      <Sidebar />
      <DashboardHeader />

      <main className="ml-64 mt-16 p-8">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Medical Records</h1>
            <p className="text-[#a1a1a1]">Access and manage your health documents</p>
          </div>

          <div className="card">
            <div className="flex gap-3 mb-6">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#a1a1a1]" size={20} />
                <input
                  type="text"
                  placeholder="Search records..."
                  className="input-field pl-10"
                />
              </div>
              <select className="input-field w-40">
                <option>All Types</option>
                <option>Lab Result</option>
                <option>Consultation</option>
                <option>Imaging</option>
                <option>Prescription</option>
              </select>
            </div>

            <div className="space-y-3">
              {records.map((record) => (
                <motion.div
                  key={record.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center justify-between p-4 border border-[#2d2d2d] rounded-lg hover:border-[#00d4aa]/30 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <FileText className="text-[#00d4aa]" />
                    <div>
                      <p className="text-white font-bold">{record.title}</p>
                      <p className="text-[#a1a1a1] text-sm">{record.date}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="px-3 py-1 rounded-full bg-[#00d4aa]/10 text-[#00d4aa] text-xs font-medium">
                      {record.type}
                    </span>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="p-2 hover:bg-white/10 rounded-lg transition-all"
                    >
                      <Download size={20} className="text-[#00d4aa]" />
                    </motion.button>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  )
}
