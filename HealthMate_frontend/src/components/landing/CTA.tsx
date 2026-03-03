import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

export function CTA() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
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

  const buttonVariants = {
    hover: {
      scale: 1.05,
      transition: { duration: 0.2 },
    },
    tap: {
      scale: 0.95,
    },
  }

  return (
    <section className="py-20 bg-gradient-to-r from-[#151d2e] to-[#0a0f1e] relative overflow-hidden">
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-[#00d4aa]/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-[#0ea5e9]/10 rounded-full blur-3xl animate-pulse" />
      </div>

      <motion.div
        className="container-max relative z-10 text-center"
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
      >
        <motion.h2
          variants={itemVariants}
          className="text-5xl lg:text-6xl font-bold mb-6"
        >
          <span className="text-white">Ready to transform </span>
          <br />
          <span className="gradient-text">your healthcare experience?</span>
        </motion.h2>

        <motion.p
          variants={itemVariants}
          className="text-lg text-[#a1a1a1] mb-8 max-w-2xl mx-auto"
        >
          Join thousands of patients and healthcare providers who trust Health Mate for their digital healthcare needs.
        </motion.p>

        <motion.div
          variants={itemVariants}
          className="flex flex-col sm:flex-row gap-4 justify-center"
        >
          <motion.div
            variants={buttonVariants}
            whileHover="hover"
            whileTap="tap"
          >
            <Link to="/signup" className="btn-primary inline-block">
              Start Free Trial
            </Link>
          </motion.div>

          <motion.div
            variants={buttonVariants}
            whileHover="hover"
            whileTap="tap"
          >
            <a href="#" className="btn-secondary inline-block">
              Contact Sales
            </a>
          </motion.div>
        </motion.div>
      </motion.div>
    </section>
  )
}
