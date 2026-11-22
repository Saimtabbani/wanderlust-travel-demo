import { useEffect, useState } from 'react'
import { Globe, LogOut, Menu, Mic, UserRound, X } from 'lucide-react'
import AuthDialog from './AuthDialog'
import type { Account } from '../types'
import { logoutAccount } from '../api/auth'
import { clearStoredAuth, getStoredAuth } from '../utils/auth'
import { clearSignedSession } from '../utils/session'

const navLinks = [
  { label: 'Discover', href: '#discover' },
  { label: 'My Trips', href: '#my-trips' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'About', href: '#about' },
]

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [authOpen, setAuthOpen] = useState(false)
  const [account, setAccount] = useState<Account | null>(() => getStoredAuth()?.account ?? null)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 32)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const signOut = async () => {
    const current = getStoredAuth()
    clearStoredAuth()
    window.dispatchEvent(new Event('wanderlust:auth-changed'))
    clearSignedSession()
    setAccount(null)
    setMobileOpen(false)
    if (current) { try { await logoutAccount(current.access_token) } catch { /* A local sign-out still succeeds offline. */ } }
  }

  const startVoice = () => {
    setMobileOpen(false)
    window.dispatchEvent(new CustomEvent('wanderlust:start-voice-search'))
  }

  return <>
    <header className={`relative z-50 transition-all duration-300 ${scrolled || mobileOpen ? 'glass border-b border-white/5 py-3' : 'bg-[#0a0f1e] border-b border-white/5 py-4 sm:py-5'}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between gap-3">
        <a href="#" className="flex items-center gap-2 group shrink-0" aria-label="Wanderlust home"><div className="w-8 h-8 rounded-lg bg-gradient-to-br from-sky-400 to-indigo-500 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform"><Globe className="w-4 h-4 text-white" /></div><span className="text-lg font-bold tracking-tight"><span className="gradient-text">Wander</span><span className="text-white">lust</span></span></a>
        <nav className="hidden lg:flex items-center gap-8" aria-label="Main navigation">{navLinks.map((link) => <a key={link.label} href={link.href} className="text-sm text-slate-400 hover:text-white transition-colors font-medium">{link.label}</a>)}</nav>
        <div className="hidden md:flex items-center gap-2 shrink-0">
          {account ? <button onClick={signOut} className="flex items-center gap-2 text-sm text-slate-300 hover:text-white px-3 py-2 font-medium" title="Sign out"><UserRound className="w-4 h-4" /><span className="max-w-24 truncate">{account.display_name}</span><LogOut className="w-4 h-4" /></button> : <button onClick={() => setAuthOpen(true)} className="text-sm text-slate-300 hover:text-white transition-colors px-4 py-2 font-medium">Sign In</button>}
          <button onClick={startVoice} className="flex items-center gap-2 text-sm font-semibold px-4 py-2 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-500 text-white hover:opacity-90 transition-all hover:scale-105 shadow-lg shadow-indigo-500/20 cursor-pointer"><Mic className="w-4 h-4" />Try Voice Search</button>
        </div>
        <button className="md:hidden p-2 -mr-2 text-slate-300 hover:text-white" onClick={() => setMobileOpen((open) => !open)} aria-label="Toggle menu" aria-expanded={mobileOpen}>{mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}</button>
      </div>
      {mobileOpen && <div className="md:hidden border-t border-white/10 mt-3 px-4 py-4 flex flex-col gap-3 shadow-2xl bg-[#0d1424]/95">
        {navLinks.map((link) => <a key={link.label} href={link.href} onClick={() => setMobileOpen(false)} className="rounded-lg px-2 py-2 text-sm text-slate-200 hover:bg-white/5">{link.label}</a>)}
        <div className="flex flex-col gap-2 pt-3 border-t border-white/10">{account ? <button onClick={signOut} className="text-sm text-slate-200 text-left px-2 py-2">Sign out ({account.display_name})</button> : <button onClick={() => { setMobileOpen(false); setAuthOpen(true) }} className="text-sm text-slate-200 text-left px-2 py-2">Sign In</button>}<button onClick={startVoice} className="flex items-center gap-2 justify-center text-sm font-semibold px-4 py-3 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-500 text-white"><Mic className="w-4 h-4" />Try Voice Search</button></div>
      </div>}
    </header>
    {authOpen && <AuthDialog onClose={() => setAuthOpen(false)} onAuthenticated={setAccount} />}
  </>
}
