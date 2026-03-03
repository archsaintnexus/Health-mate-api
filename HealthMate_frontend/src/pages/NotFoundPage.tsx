import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { AlertCircle } from 'lucide-react'

export default function NotFoundPage() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.2 },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } },
  }

  return (
    <div className="min-h-screen bg-[#0a0f1e] flex items-center justify-center px-4">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="text-center"
      >
        <motion.div
          variants={itemVariants}
          className="mb-8"
        >
          <AlertCircle className="w-24 h-24 text-[#00d4aa] mx-auto mb-4 animate-pulse" />
        </motion.div>

        <motion.h1
          variants={itemVariants}
          className="text-6xl font-bold text-white mb-4"
        >
          404
        </motion.h1>

        <motion.p
          variants={itemVariants}
          className="text-2xl text-[#a1a1a1] mb-8"
        >
          Page Not Found
        </motion.p>

        <motion.p
          variants={itemVariants}
          className="text-lg text-[#a1a1a1] mb-8 max-w-md"
        >
          Sorry, the page you&apos;re looking for doesn&apos;t exist. It might have been moved or deleted.
        </motion.p>

        <motion.div
          variants={itemVariants}
          className="flex gap-4 justify-center"
        >
          <Link to="/">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn-primary"
            >
              Go Home
            </motion.button>
          </Link>
          <Link to="/dashboard">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn-secondary"
            >
              Go to Dashboard
            </motion.button>
          </Link>
        </motion.div>
      </motion.div>
    </div>
  )
}
