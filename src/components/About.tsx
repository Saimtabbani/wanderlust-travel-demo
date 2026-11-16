import { Globe, Users, ShieldCheck, Zap } from 'lucide-react'

const values = [
  {
    icon: Globe,
    title: 'Curated Demo Data',
    description: 'A focused set of Indian and international destinations for demonstrating search, filtering, and ranking.',
    color: 'text-sky-400',
    bg: 'bg-sky-500/10',
  },
  {
    icon: Users,
    title: 'Transparent Ranking',
    description: 'Results show how endorsement, rating, and keyword relevance contribute to an explainable score.',
    color: 'text-indigo-400',
    bg: 'bg-indigo-500/10',
  },
  {
    icon: ShieldCheck,
    title: 'Demo-Session Safety',
    description: 'A signed demo session prevents simple duplicate endorsements during a single demonstration.',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
  },
  {
    icon: Zap,
    title: 'Voice and Text Search',
    description: 'Use speech where supported, or type a travel preference to quickly explore matching destinations.',
    color: 'text-amber-400',
    bg: 'bg-amber-500/10',
  },
]

export default function About() {
  return (
    <section id="about" className="py-24 px-6 bg-[#0d1424] scroll-mt-20">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Left copy */}
          <div>
            <span className="inline-block text-xs font-semibold text-purple-400 uppercase tracking-widest mb-3">
              About Wanderlust
            </span>
            <h2 className="text-4xl md:text-5xl font-black text-white leading-tight mb-6">
              Travel recommendations{' '}
              <span className="gradient-text">reinvented.</span>
            </h2>
            <p className="text-slate-400 leading-relaxed mb-5">
              Wanderlust is a final-year project exploring an accessible travel discovery
              experience with voice input, filters, and transparent recommendation scores.
            </p>
            <p className="text-slate-400 leading-relaxed mb-8">
              This hosted build uses demonstration data. It is designed to show the product
              flow and ranking approach; it does not claim live traveller verification,
              real-time prices, or booking availability.
            </p>
            <div className="flex flex-wrap gap-4">
              <button className="px-6 py-3 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-500 text-white font-bold text-sm hover:opacity-90 hover:scale-105 transition-all shadow-lg shadow-indigo-500/20">
                Explore the Demo
              </button>
              <button className="px-6 py-3 rounded-xl glass text-slate-300 hover:text-white font-bold text-sm transition-all hover:border-white/15">
                How It Works
              </button>
            </div>
          </div>

          {/* Right grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            {values.map((v) => {
              const Icon = v.icon
              return (
                <div
                  key={v.title}
                  className="glass-card rounded-2xl p-6 hover:border-white/15 hover:scale-[1.02] transition-all duration-300"
                >
                  <div className={`w-10 h-10 rounded-xl ${v.bg} flex items-center justify-center mb-4`}>
                    <Icon className={`w-5 h-5 ${v.color}`} />
                  </div>
                  <h3 className="text-base font-bold text-white mb-2">{v.title}</h3>
                  <p className="text-slate-400 text-sm leading-relaxed">{v.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
