import { motion } from 'framer-motion'
import { Star } from 'lucide-react'

const testimonials = [
  {
    name: 'Sarah Johnson',
    role: 'Patient',
    content: 'Health Mate made it so easy to manage my healthcare. I can book appointments, access my records, and consult with doctors all from one app.',
    image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop',
    rating: 5,
  },
  {
    name: 'Dr. Michael Chen',
    role: 'Physician',
    content: 'As a healthcare provider, I appreciate how Health Mate streamlines patient management and improves communication with my patients.',
    image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop',
    rating: 5,
  },
  {
    name: 'Emily Rodriguez',
    role: 'Patient',
    content: 'The telehealth feature saved me time and money. I got a consultation without leaving my home, and the entire process was seamless.',
    image: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop',
    rating: 5,
  },
]

export function Testimonials() {
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
            <span className="text-white">Loved by </span>
            <span className="gradient-text">Patients & Doctors</span>
          </h2>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-8"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="card group hover:border-[#00d4aa]/50 transition-all"
            >
              <div className="flex items-center gap-4 mb-4">
                <img
                  src={testimonial.image}
                  alt={testimonial.name}
                  className="w-12 h-12 rounded-full object-cover"
                />
                <div>
                  <h3 className="text-white font-bold">{testimonial.name}</h3>
                  <p className="text-sm text-[#a1a1a1]">{testimonial.role}</p>
                </div>
              </div>

              <div className="flex gap-1 mb-4">
                {Array.from({ length: testimonial.rating }).map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-[#00d4aa] text-[#00d4aa]" />
                ))}
              </div>

              <p className="text-[#a1a1a1] italic">{`"${testimonial.content}"`}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
