import { motion } from 'framer-motion'
import { Bell, User } from 'lucide-react'
import { useAuth } from '@/lib/auth-context'

export function DashboardHeader() {
  const { firstName } = useAuth()

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="fixed top-0 right-0 left-64 bg-[#151d2e] border-b border-[#2d2d2d] h-16 flex items-center justify-between px-8 z-30"
    >
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
        <h2 className="text-xl font-bold text-white">
          Welcome back, <span className="text-[#00d4aa]">{firstName}</span>!
        </h2>
      </motion.div>

      <div className="flex items-center gap-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="relative p-2 text-[#a1a1a1] hover:text-white hover:bg-white/5 rounded-lg transition-all"
        >
          <Bell size={20} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-[#00d4aa] rounded-full" />
        </motion.button>

        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="p-2 text-[#a1a1a1] hover:text-white hover:bg-white/5 rounded-lg transition-all cursor-pointer"
        >
          <User size={20} />
        </motion.div>
      </div>
    </motion.header>
  )
}
