import { motion } from 'framer-motion'

const steps = [
  {
    number: '01',
    title: 'Create Account',
    description: 'Sign up in seconds with your email and basic information',
  },
  {
    number: '02',
    title: 'Choose Service',
    description: 'Select from our comprehensive range of healthcare services',
  },
  {
    number: '03',
    title: 'Get Care',
    description: 'Connect with healthcare professionals or access services instantly',
  },
]

export function HowItWorks() {
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
    hidden: { opacity: 0, x: -20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.6 },
    },
  }

  return (
    <section className="py-20 bg-gradient-to-b from-[#0a0f1e] to-[#151d2e]">
      <div className="container-max">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
        >
          <h2 className="text-5xl lg:text-6xl font-bold mb-6">
            <span className="text-white">How It </span>
            <span className="gradient-text">Works</span>
          </h2>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-8"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          {steps.map((step, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="relative"
            >
              <div className="card group hover:border-[#00d4aa]/50 transition-all">
                <div className="text-5xl font-bold text-[#00d4aa] mb-4 opacity-20 group-hover:opacity-40 transition-opacity">
                  {step.number}
                </div>
                <h3 className="text-2xl font-bold text-white mb-3">{step.title}</h3>
                <p className="text-[#a1a1a1]">{step.description}</p>
              </div>

              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-1/2 right-0 transform translate-x-1/2 -translate-y-1/2 w-12 h-1 bg-gradient-to-r from-[#00d4aa] to-transparent" />
              )}
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
