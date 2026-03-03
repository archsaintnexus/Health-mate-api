import { motion } from 'framer-motion'
import { Calendar, Video, FileText, Beaker, Pill, Home } from 'lucide-react'

const features = [
  {
    icon: Calendar,
    title: 'Appointment Booking',
    description: 'Schedule consultations with doctors at your convenience',
    color: 'from-[#00d4aa] to-[#0ea5e9]',
  },
  {
    icon: Video,
    title: 'Telehealth',
    description: 'Connect with healthcare professionals via secure video calls',
    color: 'from-[#0ea5e9] to-[#00d4aa]',
  },
  {
    icon: FileText,
    title: 'Medical Records',
    description: 'Access and manage your complete medical history',
    color: 'from-[#00d4aa] to-[#0ea5e9]',
  },
  {
    icon: Beaker,
    title: 'Lab Tests',
    description: 'Book tests and receive results digitally',
    color: 'from-[#0ea5e9] to-[#00d4aa]',
  },
  {
    icon: Pill,
    title: 'Pharmacy',
    description: 'Order medications and get home delivery',
    color: 'from-[#00d4aa] to-[#0ea5e9]',
  },
  {
    icon: Home,
    title: 'Home Care',
    description: 'Professional caregivers at your doorstep',
    color: 'from-[#0ea5e9] to-[#00d4aa]',
  },
]

export function Features() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
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

  const hoverVariants = {
    hover: {
      y: -8,
      transition: { duration: 0.3 },
    },
  }

  return (
    <section id="features" className="py-20 bg-[#0a0f1e]">
      <div className="container-max">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
        >
          <h2 className="text-5xl lg:text-6xl font-bold mb-6">
            <span className="text-white">Comprehensive</span>
            <br />
            <span className="gradient-text">Healthcare Services</span>
          </h2>
          <p className="text-lg text-[#a1a1a1] max-w-2xl mx-auto">
            All the healthcare services you need in one integrated platform
          </p>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <motion.div
                key={index}
                variants={itemVariants}
                whileHover="hover"
                variants={hoverVariants}
                className="group card hover:border-[#00d4aa]/50 transition-all cursor-pointer"
              >
                <div className={`w-14 h-14 rounded-lg bg-gradient-to-br ${feature.color} p-0.5 mb-4`}>
                  <div className="w-full h-full rounded-lg bg-[#0a0f1e] flex items-center justify-center">
                    <Icon className="w-7 h-7 text-[#00d4aa]" />
                  </div>
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-[#a1a1a1]">{feature.description}</p>
              </motion.div>
            )
          })}
        </motion.div>
      </div>
    </section>
  )
}
