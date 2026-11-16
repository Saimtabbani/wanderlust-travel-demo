import { useState, useEffect } from 'react'
import { Menu, X, Globe, Mic } from 'lucide-react'

const navLinks = [
  { label: 'Discover', href: '#discover' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'About', href: '#about' },
]

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 32)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? 'glass border-b border-white/5 py-3' : 'py-5'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        {/* Logo */}
        <a href="#" className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-sky-400 to-indigo-500 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
            <Globe className="w-4 h-4 text-white" />
          </div>
          <span className="text-lg font-bold tracking-tight">
            <span className="gradient-text">Wander</span>
            <span className="text-white">lust</span>
          </span>
        </a>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="text-sm text-slate-400 hover:text-white transition-colors font-medium"
            >
              {link.label}
            </a>
          ))}
        </nav>

        {/* CTA Buttons */}
        <div className="hidden md:flex items-center gap-3">
          <button className="text-sm text-slate-400 hover:text-white transition-colors px-4 py-2 font-medium">
            Sign In
          </button>
          <button
            onClick={() => {
              window.dispatchEvent(new CustomEvent('wanderlust:start-voice-search'))
            }}
            className="flex items-center gap-2 text-sm font-semibold px-4 py-2 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-500 text-white hover:opacity-90 transition-all hover:scale-105 shadow-lg shadow-indigo-500/20 cursor-pointer"
          >
            <Mic className="w-4 h-4" />
            Try Voice Search
          </button>
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden text-slate-400 hover:text-white transition-colors"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden glass border-t border-white/5 mt-2 px-6 py-4 flex flex-col gap-4">
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              onClick={() => setMobileOpen(false)}
              className="text-sm text-slate-300 hover:text-white transition-colors font-medium"
            >
              {link.label}
            </a>
          ))}
          <div className="flex flex-col gap-2 pt-2 border-t border-white/10">
            <button className="text-sm text-slate-400 hover:text-white transition-colors text-left font-medium">
              Sign In
            </button>
            <button
              onClick={() => {
                setMobileOpen(false)
                window.dispatchEvent(new CustomEvent('wanderlust:start-voice-search'))
              }}
              className="flex items-center gap-2 justify-center text-sm font-semibold px-4 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-500 text-white cursor-pointer"
            >
              <Mic className="w-4 h-4" />
              Try Voice Search
            </button>
          </div>
        </div>
      )}
    </header>
  )
}
