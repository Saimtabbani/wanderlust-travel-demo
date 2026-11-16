import { Mic, Brain, ThumbsUp, Map } from 'lucide-react'

const steps = [
  {
    id: 1,
    icon: Mic,
    title: 'Speak or Type',
    description:
      'Tell Wanderlust what you\'re looking for — "relaxing beach with great food" or "adventure trekking in mountains" — in plain, natural language.',
    color: 'from-sky-500 to-cyan-500',
    glow: 'shadow-sky-500/30',
  },
  {
    id: 2,
    icon: Brain,
    title: 'Search and Filter',
    description:
      'Wanderlust uses the search terms, destination tags, region, and budget filters to narrow the demonstration catalogue.',
    color: 'from-indigo-500 to-purple-500',
    glow: 'shadow-indigo-500/30',
  },
  {
    id: 3,
    icon: ThumbsUp,
    title: 'Review the Ranking',
    description:
      'Each result includes its score breakdown, illustrating how endorsement, rating, and keyword relevance are combined.',
    color: 'from-purple-500 to-pink-500',
    glow: 'shadow-purple-500/30',
  },
  {
    id: 4,
    icon: Map,
    title: 'Explore Responsibly',
    description:
      'Use the demo as a starting point, then verify current prices, travel requirements, and safety guidance through official sources.',
    color: 'from-orange-500 to-amber-500',
    glow: 'shadow-orange-500/30',
  },
]

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24 px-6 bg-[#0a0f1e] relative overflow-hidden scroll-mt-20">
      {/* BG decoration */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-px h-24 bg-gradient-to-b from-transparent to-indigo-500/50" />

      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <span className="inline-block text-xs font-semibold text-indigo-400 uppercase tracking-widest mb-3">
            How It Works
          </span>
          <h2 className="text-4xl md:text-5xl font-black text-white leading-tight">
            From Voice to Voyage
          </h2>
          <p className="mt-4 text-slate-400 max-w-xl mx-auto leading-relaxed">
            Four simple steps from your first word to your next adventure.
          </p>
        </div>

        {/* Steps grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 relative">
          {/* connector line (desktop) */}
          <div className="absolute top-10 left-[12.5%] right-[12.5%] h-px bg-gradient-to-r from-transparent via-white/10 to-transparent hidden lg:block pointer-events-none" />

          {steps.map((step) => {
            const Icon = step.icon
            return (
              <div
                key={step.id}
                className="glass-card rounded-2xl p-7 flex flex-col items-center text-center hover:border-white/15 hover:scale-[1.02] transition-all duration-300"
              >
                {/* Number badge */}
                <div className="relative mb-5">
                  <div
                    className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center shadow-lg ${step.glow} float-anim`}
                    style={{ animationDelay: `${step.id * 0.5}s` }}
                  >
                    <Icon className="w-7 h-7 text-white" />
                  </div>
                  <span className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-slate-800 border border-white/10 text-xs font-black text-white flex items-center justify-center">
                    {step.id}
                  </span>
                </div>

                <h3 className="text-lg font-bold text-white mb-3">{step.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{step.description}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
