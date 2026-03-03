import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Home,
  Calendar,
  Video,
  FileText,
  Beaker,
  Pill,
  Home as HomeIcon,
  Settings,
  LogOut,
} from 'lucide-react'
import { useAuth } from '@/lib/auth-context'

const menuItems = [
  { icon: Home, label: 'Dashboard', path: '/dashboard' },
  { icon: Calendar, label: 'Appointments', path: '/dashboard/appointments' },
  { icon: Video, label: 'Telehealth', path: '/dashboard/telehealth' },
  { icon: FileText, label: 'Records', path: '/dashboard/records' },
  { icon: Beaker, label: 'Lab Tests', path: '/dashboard/lab-tests' },
  { icon: Pill, label: 'Pharmacy', path: '/dashboard/pharmacy' },
  { icon: HomeIcon, label: 'Home Care', path: '/dashboard/home-care' },
]

export function Sidebar() {
  const location = useLocation()
  const { logout } = useAuth()

  return (
    <motion.aside
      initial={{ x: -256 }}
      animate={{ x: 0 }}
      className="fixed left-0 top-0 h-screen w-64 bg-[#151d2e] border-r border-[#2d2d2d] flex flex-col p-6 z-40"
    >
      <Link to="/" className="mb-8">
        <h1 className="text-2xl font-bold gradient-text">Health Mate</h1>
      </Link>

      <nav className="flex-1 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          return (
            <Link key={item.path} to={item.path}>
              <motion.div
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all relative ${
                  isActive
                    ? 'bg-[#00d4aa]/10 text-[#00d4aa]'
                    : 'text-[#a1a1a1] hover:bg-white/5 hover:text-white'
                }`}
                whileHover={{ x: 4 }}
              >
                <Icon size={20} />
                <span className="font-medium">{item.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="absolute right-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-[#00d4aa] rounded-l-full"
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}
              </motion.div>
            </Link>
          )
        })}
      </nav>

      <div className="space-y-2 border-t border-[#2d2d2d] pt-4">
        <Link to="/dashboard/profile">
          <motion.div
            className="flex items-center gap-3 px-4 py-3 rounded-lg text-[#a1a1a1] hover:bg-white/5 hover:text-white transition-all"
            whileHover={{ x: 4 }}
          >
            <Settings size={20} />
            <span className="font-medium">Profile</span>
          </motion.div>
        </Link>

        <motion.button
          onClick={logout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-[#a1a1a1] hover:bg-red-500/10 hover:text-red-400 transition-all text-left"
          whileHover={{ x: 4 }}
        >
          <LogOut size={20} />
          <span className="font-medium">Logout</span>
        </motion.button>
      </div>
    </motion.aside>
  )
}
