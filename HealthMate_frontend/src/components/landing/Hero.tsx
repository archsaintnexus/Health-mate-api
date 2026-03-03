import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { AnimatedBackground } from '@/components/AnimatedBackground'

export function Hero() {
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    setIsLoaded(true)
  }, [])

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.8, ease: 'easeOut' },
    },
  }

  const buttonVariants = {
    hidden: { opacity: 0, scale: 0.9 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: { duration: 0.6 },
    },
    hover: {
      scale: 1.05,
      transition: { duration: 0.2 },
    },
    tap: {
      scale: 0.95,
    },
  }

  return (
    <div className="relative w-full min-h-screen bg-[#0a0f1e] overflow-hidden flex items-center justify-center">
      <AnimatedBackground />

      <motion.div
        className="relative z-10 container-max text-center"
        variants={containerVariants}
        initial="hidden"
        animate={isLoaded ? 'visible' : 'hidden'}
      >
        <motion.div variants={itemVariants} className="mb-6">
          <span className="inline-block px-4 py-2 rounded-full bg-white/10 border border-white/20 text-sm font-medium text-[#00d4aa]">
            ✓ Trusted by 50,000+ Patients
          </span>
        </motion.div>

        <motion.h1
          variants={itemVariants}
          className="text-6xl sm:text-7xl lg:text-8xl font-bold mb-6 leading-tight tracking-tighter text-balance"
        >
          <span className="text-white">Your Health,</span>
          <br />
          <span className="gradient-text">Reimagined</span>
        </motion.h1>

        <motion.p
          variants={itemVariants}
          className="text-lg sm:text-xl text-[#a1a1a1] mb-8 max-w-2xl mx-auto leading-relaxed"
        >
          Experience seamless digital healthcare with appointments, telehealth consultations, medical records, lab tests, pharmacy services, and home care—all in one platform.
        </motion.p>

        <motion.div
          variants={itemVariants}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
        >
          <motion.div
            variants={buttonVariants}
            whileHover="hover"
            whileTap="tap"
          >
            <Link
              to="/signup"
              className="btn-primary inline-block"
            >
              Get Started Free
            </Link>
          </motion.div>

          <motion.div
            variants={buttonVariants}
            whileHover="hover"
            whileTap="tap"
          >
            <a
              href="#features"
              className="btn-secondary inline-block"
            >
              Learn More
            </a>
          </motion.div>
        </motion.div>
      </motion.div>
    </div>
  )
}
