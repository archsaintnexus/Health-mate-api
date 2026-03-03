import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

const stats = [
  { label: 'Active Patients', value: 50000 },
  { label: 'Verified Doctors', value: 200 },
  { label: 'Consultations Done', value: 100000 },
  { label: 'Cities Covered', value: 50 },
]

function CountUp({ target, duration = 2 }: { target: number; duration?: number }) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let start = 0
    const increment = target / (duration * 60)
    const timer = setInterval(() => {
      start += increment
      if (start >= target) {
        setCount(target)
        clearInterval(timer)
      } else {
        setCount(Math.floor(start))
      }
    }, 16)

    return () => clearInterval(timer)
  }, [target, duration])

  return <span>{count.toLocaleString()}+</span>
}

export function Stats() {
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
    hidden: { opacity: 0, scale: 0.8 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: { duration: 0.6 },
    },
  }

  return (
    <section className="py-20 bg-[#0a0f1e] border-y border-[#2d2d2d]">
      <div className="container-max">
        <motion.div
          className="grid grid-cols-2 md:grid-cols-4 gap-8"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="text-center"
            >
              <div className="text-4xl sm:text-5xl font-bold gradient-text mb-2">
                <CountUp target={stat.value} duration={2} />
              </div>
              <p className="text-[#a1a1a1] text-sm sm:text-base">{stat.label}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
