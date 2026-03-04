import Header from '@/components/landing/Header'
import Hero from '@/components/landing/Hero'
import Features from '@/components/landing/Features'
import Testimonials from '@/components/landing/Testimonials'
import CTA from '@/components/landing/CTA'
import Footer from '@/components/landing/Footer'

export default function LandingPage() {
  return (
    <>
      <Header />
      <main className="min-h-screen">
        <Hero />
        <div id="features">
          <Features />
        </div>
        <div id="how-it-works">
          <Testimonials />
        </div>
        <div id="pricing">
          <CTA />
        </div>
        <div id="resources">
          <Footer />
        </div>
      </main>
    </>
  )
}
