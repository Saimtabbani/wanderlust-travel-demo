import { Globe, ExternalLink } from 'lucide-react'

const footerLinks = {
  Product: ['Discover', 'Voice Search', 'Endorsements', 'Itinerary Planner'],
  Company: ['About Us', 'Blog', 'Careers', 'Press'],
  Support: ['Help Center', 'Privacy Policy', 'Terms of Service', 'Contact'],
}

const socials = [
  { label: 'Twitter / X' },
  { label: 'Instagram' },
  { label: 'YouTube' },
  { label: 'GitHub' },
]

export default function Footer() {
  return (
    <footer className="bg-[#070c18] border-t border-white/5 px-6 py-16">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-10 mb-12">
          {/* Brand */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-sky-400 to-indigo-500 flex items-center justify-center">
                <Globe className="w-4 h-4 text-white" />
              </div>
              <span className="text-lg font-bold">
                <span className="gradient-text">Wander</span>
                <span className="text-white">lust</span>
              </span>
            </div>
            <p className="text-slate-500 text-sm leading-relaxed max-w-xs">
              The voice-enabled, endorsement-based travel platform that puts real travellers at the centre of every recommendation.
            </p>
            <div className="flex gap-3 mt-5">
              {socials.map(({ label }) => (
                <button
                  key={label}
                  aria-label={label}
                  className="w-9 h-9 rounded-xl glass text-slate-500 hover:text-white hover:border-white/15 flex items-center justify-center transition-all"
                >
                  <ExternalLink className="w-4 h-4" />
                </button>
              ))}
            </div>
          </div>

          {/* Link columns */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">
                {category}
              </h4>
              <ul className="space-y-2.5">
                {links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-sm text-slate-500 hover:text-white transition-colors"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-xs text-slate-600">
            © 2026 Wanderlust. All rights reserved.
          </p>
          <p className="text-xs text-slate-600">
            Built with ❤️ for the Final Year Project · React + Vite + TypeScript
          </p>
        </div>
      </div>
    </footer>
  )
}
