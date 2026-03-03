import { Hero } from '@/components/landing/Hero'
import { Features } from '@/components/landing/Features'
import { HowItWorks } from '@/components/landing/HowItWorks'
import { Stats } from '@/components/landing/Stats'
import { Testimonials } from '@/components/landing/Testimonials'
import { CTA } from '@/components/landing/CTA'
import { Footer } from '@/components/Footer'

export default function LandingPage() {
  return (
    <main className="w-full">
      <Hero />
      <Features />
      <HowItWorks />
      <Stats />
      <Testimonials />
      <CTA />
      <Footer />
    </main>
  )
}
