'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'
import { usePathname } from 'next/navigation'

export default function Header() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const pathname = usePathname()

  const isAppPage = pathname?.startsWith('/app')
  const isDocsPage = pathname?.startsWith('/docs')
  const isLandingPage = pathname === '/'

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      setIsMobileMenuOpen(false)
    }
  }

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-slate-900/80 backdrop-blur-xl border-b border-white/10 shadow-lg'
          : 'bg-transparent'
      }`}
    >
      <nav className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="relative">
                <div className="absolute -inset-1 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 opacity-0 blur transition duration-300 group-hover:opacity-75" />
                <div className="relative flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600">
                  <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
              </div>
              <span className="text-lg font-semibold text-white transition-colors group-hover:text-indigo-300">
                Migration Studio
              </span>
            </Link>
          </div>

          {/* Desktop Navigation - Only on Landing Page */}
          {isLandingPage && (
            <div className="hidden md:flex items-center gap-1">
              {[
                { label: 'Features', id: 'features' },
                { label: 'How it Works', id: 'how-it-works' },
                { label: 'Pricing', id: 'pricing' },
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => scrollToSection(item.id)}
                  className="px-4 py-2 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
                >
                  {item.label}
                </button>
              ))}
              <Link
                href="/docs"
                className="px-4 py-2 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
              >
                Docs
              </Link>
            </div>
          )}

          {/* App Navigation - Only on App Pages */}
          {isAppPage && (
            <div className="hidden md:flex items-center gap-1">
              <Link
                href="/app"
                className="px-4 py-2 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
              >
                Dashboard
              </Link>
              <Link
                href="/app/analytics"
                className="px-4 py-2 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
              >
                Analytics
              </Link>
              <Link
                href="/app/universes"
                className="px-4 py-2 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
              >
                Universes
              </Link>
              <Link
                href="/app/runs"
                className="px-4 py-2 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
              >
                Runs
              </Link>
              <Link
                href="/docs"
                className="px-4 py-2 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
              >
                Docs
              </Link>
            </div>
          )}

          {/* Docs Navigation */}
          {isDocsPage && (
            <div className="hidden md:flex items-center gap-1">
              <Link
                href="/"
                className="px-4 py-2 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
              >
                Home
              </Link>
              <Link
                href="/app"
                className="px-4 py-2 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
              >
                Dashboard
              </Link>
            </div>
          )}

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center gap-3">
            {!isAppPage ? (
              <Link
                href="/app"
                className="group relative inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600 px-5 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 transition-all hover:shadow-xl hover:shadow-indigo-500/40 hover:scale-105"
              >
                <span>Launch Studio</span>
                <svg className="h-4 w-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Link>
            ) : (
              <Link
                href="/"
                className="px-4 py-2 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
              >
                Back to Home
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden relative inline-flex h-10 w-10 items-center justify-center rounded-lg text-slate-300 transition-colors hover:bg-white/5 hover:text-white"
            aria-label="Toggle menu"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isMobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        <div
          className={`md:hidden overflow-hidden transition-all duration-300 ${
            isMobileMenuOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
          }`}
        >
          <div className="space-y-1 pb-4 pt-2">
            {isLandingPage && (
              <>
                {[
                  { label: 'Features', id: 'features' },
                  { label: 'How it Works', id: 'how-it-works' },
                  { label: 'Pricing', id: 'pricing' },
                ].map((item) => (
                  <button
                    key={item.id}
                    onClick={() => scrollToSection(item.id)}
                    className="block w-full text-left px-4 py-3 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
                  >
                    {item.label}
                  </button>
                ))}
                <Link
                  href="/docs"
                  className="block w-full text-left px-4 py-3 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
                >
                  Docs
                </Link>
              </>
            )}

            {isAppPage && (
              <>
                <Link
                  href="/app"
                  className="block w-full text-left px-4 py-3 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
                >
                  Dashboard
                </Link>
                <Link
                  href="/app/analytics"
                  className="block w-full text-left px-4 py-3 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
                >
                  Analytics
                </Link>
                <Link
                  href="/app/universes"
                  className="block w-full text-left px-4 py-3 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
                >
                  Universes
                </Link>
                <Link
                  href="/app/runs"
                  className="block w-full text-left px-4 py-3 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
                >
                  Runs
                </Link>
                <Link
                  href="/docs"
                  className="block w-full text-left px-4 py-3 text-sm font-medium text-slate-300 transition-all duration-200 hover:text-white hover:bg-white/5 rounded-lg"
                >
                  Docs
                </Link>
              </>
            )}

            <div className="pt-3">
              {!isAppPage ? (
                <Link
                  href="/app"
                  className="flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30"
                >
                  <span>Launch Studio</span>
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </Link>
              ) : (
                <Link
                  href="/"
                  className="flex items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-800/50 px-5 py-3 text-sm font-semibold text-white"
                >
                  Back to Home
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>
    </header>
  )
}
