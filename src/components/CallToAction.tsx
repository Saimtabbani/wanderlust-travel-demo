import { Mic, ArrowRight } from 'lucide-react'

export default function CallToAction() {
  const startVoiceSearch = () => {
    window.dispatchEvent(new Event('wanderlust:start-voice-search'))
  }

  const browseDestinations = () => {
    document.getElementById('discover')?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <section className="py-24 px-6 bg-[#0a0f1e] relative overflow-hidden">
      {/* BG glow */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-96 h-96 bg-indigo-500/15 rounded-full blur-3xl" />
      </div>

      <div className="max-w-4xl mx-auto relative text-center">
        <div className="glass-card rounded-3xl px-8 py-14 md:px-16">
          <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/30 mic-pulse">
            <Mic className="w-7 h-7 text-white" />
          </div>

          <h2 className="text-4xl md:text-5xl font-black text-white leading-tight mb-4">
            Ready to explore?
          </h2>
          <p className="text-slate-400 text-lg leading-relaxed mb-8 max-w-lg mx-auto">
            Try a voice or text search, adjust the filters, and inspect the transparent
            recommendation breakdown for each destination.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button onClick={startVoiceSearch} className="flex items-center justify-center gap-2 px-8 py-4 rounded-2xl bg-gradient-to-r from-sky-500 to-indigo-500 text-white font-bold hover:opacity-90 hover:scale-105 transition-all shadow-xl shadow-indigo-500/30">
              <Mic className="w-5 h-5" />
              Start Voice Search
            </button>
            <button onClick={browseDestinations} className="flex items-center justify-center gap-2 px-8 py-4 rounded-2xl glass text-slate-300 hover:text-white font-bold transition-all hover:border-white/15">
              Browse Destinations
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}
