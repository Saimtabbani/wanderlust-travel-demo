import { useState, useEffect, useRef } from 'react'
import { Search, Mic, Sparkles, AlertCircle, X, Square } from 'lucide-react'
import { useVoiceRecognition } from '../hooks/useVoiceRecognition'

interface HeroProps {
  onSearch?: (query: string) => void
}

export default function Hero({ onSearch }: HeroProps) {
  const [searchValue, setSearchValue] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const handleSearchTrigger = (term: string) => {
    if (onSearch) {
      onSearch(term)
    }
    const discoverSection = document.getElementById('discover')
    if (discoverSection) {
      discoverSection.scrollIntoView({ behavior: 'smooth' })
    }
  }

  // Voice recognition hook
  const {
    isListening,
    isSupported,
    interimTranscript,
    error,
    errorMessage,
    startListening,
    stopListening,
    resetError,
  } = useVoiceRecognition({
    lang: 'en-IN',
    onResult: (text, isFinal) => {
      if (isFinal) {
        setSearchValue(text)
      }
    },
    onFinalResult: (finalText) => {
      setSearchValue(finalText)
      handleSearchTrigger(finalText)
    },
  })

  // Listen for global voice search trigger (from Navbar or CallToAction buttons)
  useEffect(() => {
    const handleGlobalVoiceTrigger = () => {
      window.scrollTo({ top: 0, behavior: 'smooth' })
      if (!isListening) {
        startListening()
      }
      inputRef.current?.focus()
    }

    window.addEventListener('wanderlust:start-voice-search', handleGlobalVoiceTrigger)
    return () => {
      window.removeEventListener('wanderlust:start-voice-search', handleGlobalVoiceTrigger)
    }
  }, [isListening, startListening])

  const suggestions = [
    'beaches in Goa & Bali',
    'mountain trekking adventure',
    'heritage palaces in Rajasthan',
    'tranquil nature & backwaters',
  ]

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (isListening) {
      stopListening()
    }
    handleSearchTrigger(searchValue)
  }

  const handleMicClick = () => {
    if (isListening) {
      stopListening()
    } else {
      startListening()
    }
  }

  return (
    <section className="relative min-h-[calc(100svh-72px)] hero-gradient flex flex-col items-center justify-center px-4 sm:px-6 py-16 sm:py-20 overflow-hidden">
      {/* Background orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/3 right-1/4 w-72 h-72 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-1/2 right-1/3 w-56 h-56 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Badge */}
      <div className="fade-in-up mb-6" style={{ animationDelay: '0.1s' }}>
        <span className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full text-xs font-semibold text-sky-300 border-sky-500/20">
          <Sparkles className="w-3.5 h-3.5" />
          Voice-Enabled · Demo Recommendation Engine
        </span>
      </div>

      {/* Heading */}
      <h1
        className="fade-in-up text-5xl md:text-6xl lg:text-7xl font-black text-center leading-tight tracking-tight max-w-4xl"
        style={{ animationDelay: '0.2s' }}
      >
        Discover the World{' '}
        <span className="gradient-text">Through Your Voice.</span>
      </h1>

      {/* Sub-heading */}
      <p
        className="fade-in-up mt-6 text-lg md:text-xl text-slate-400 text-center max-w-2xl leading-relaxed"
        style={{ animationDelay: '0.35s' }}
      >
        Speak or type your travel dream. Wanderlust surfaces source-documented places
        with transparent prototype recommendations and planning estimates.
      </p>

      {/* Search Bar Form */}
      <form
        onSubmit={handleSubmit}
        className="fade-in-up mt-10 w-full max-w-2xl"
        style={{ animationDelay: '0.5s' }}
      >
        <div
          className={`glass rounded-2xl p-1.5 shadow-2xl transition-all duration-300 ${
            isListening
              ? 'border-indigo-500/60 ring-2 ring-indigo-500/30 shadow-indigo-500/20'
              : 'shadow-black/40 hover:border-white/15'
          }`}
        >
          <div className="flex items-center gap-2">
            <div className="flex-1 flex items-center gap-3 px-4 min-w-0">
              <Search className="w-5 h-5 text-slate-500 flex-shrink-0" />
              <input
                ref={inputRef}
                type="text"
                value={isListening && interimTranscript ? interimTranscript : searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                placeholder={isListening ? 'Listening... Speak your destination or vibe...' : 'Say or type a destination, vibe, or experience...'}
                className={`flex-1 bg-transparent text-sm outline-none py-3 font-medium min-w-0 ${
                  isListening && interimTranscript ? 'text-sky-300 italic' : 'text-white placeholder-slate-500'
                }`}
              />
              {searchValue && !isListening && (
                <button
                  type="button"
                  onClick={() => setSearchValue('')}
                  className="text-slate-500 hover:text-slate-300 p-1"
                  title="Clear text"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* Sound Wave Indicator (active while listening) */}
            {isListening && (
              <div className="flex items-center gap-1 px-2" title="Recording speech...">
                <span className="sound-wave-bar w-1 bg-rose-400 rounded-full" style={{ animationDelay: '0s' }} />
                <span className="sound-wave-bar w-1 bg-indigo-400 rounded-full" style={{ animationDelay: '0.2s' }} />
                <span className="sound-wave-bar w-1 bg-sky-400 rounded-full" style={{ animationDelay: '0.4s' }} />
                <span className="sound-wave-bar w-1 bg-purple-400 rounded-full" style={{ animationDelay: '0.1s' }} />
              </div>
            )}

            {/* Mic Toggle Button */}
            <button
              type="button"
              onClick={handleMicClick}
              className={`flex items-center justify-center w-12 h-12 rounded-xl text-white transition-all shadow-lg flex-shrink-0 cursor-pointer ${
                isListening
                  ? 'bg-gradient-to-br from-rose-500 to-red-600 scale-105 shadow-rose-500/40 animate-pulse'
                  : 'bg-gradient-to-br from-sky-500 to-indigo-600 hover:scale-105 shadow-indigo-500/30'
              }`}
              aria-label={isListening ? 'Stop listening' : 'Start voice search'}
              title={
                !isSupported
                  ? 'Voice recognition not supported in this browser'
                  : isListening
                  ? 'Click to stop listening'
                  : 'Click to start voice search'
              }
            >
              {isListening ? (
                <Square className="w-4 h-4 fill-white" />
              ) : (
                <Mic className="w-5 h-5" />
              )}
            </button>

            {/* Search Submit Button */}
            <button
              type="submit"
              className="flex items-center gap-2 px-5 py-3 rounded-xl bg-white text-slate-900 text-sm font-bold hover:bg-slate-100 transition-all flex-shrink-0 cursor-pointer"
            >
              Search
            </button>
          </div>
        </div>

        {/* Listening Active Notice */}
        {isListening && (
          <div className="mt-3 flex items-center justify-between px-4 py-2 rounded-xl glass border-indigo-500/30 animate-fade-in text-xs text-indigo-300">
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
              Listening to voice input in English (India / US)...
            </span>
            <button
              type="button"
              onClick={stopListening}
              className="text-slate-400 hover:text-white underline cursor-pointer"
            >
              Stop recording
            </button>
          </div>
        )}

        {/* Error / Permission Guidance Banner */}
        {error && (
          <div className="mt-3 flex items-center justify-between px-4 py-2.5 rounded-xl glass border-rose-500/30 text-xs text-rose-300 bg-rose-950/20">
            <div className="flex items-center gap-2 pr-2">
              <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              type="button"
              onClick={resetError}
              className="text-slate-400 hover:text-white p-1 flex-shrink-0 cursor-pointer"
              title="Dismiss notice"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Suggestion chips */}
        <div className="mt-4 flex flex-wrap gap-2 justify-center">
          {suggestions.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => {
                setSearchValue(s)
                handleSearchTrigger(s)
              }}
              className="text-xs px-3 py-1.5 rounded-full glass text-slate-400 hover:text-white hover:border-white/15 transition-all cursor-pointer"
            >
              {s}
            </button>
          ))}
        </div>
      </form>

      {/* Stats row */}
      <div
        className="fade-in-up mt-14 flex flex-wrap justify-center gap-10 text-center"
        style={{ animationDelay: '0.65s' }}
      >
        {[
          { value: '28', label: 'Catalogue places' },
          { value: '3', label: 'Ranking signals' },
          { value: 'CC0', label: 'Place metadata licence' },
          { value: 'β', label: 'Research prototype' },
        ].map((stat) => (
          <div key={stat.label}>
            <p className="text-2xl font-black gradient-text">{stat.value}</p>
            <p className="text-xs text-slate-500 mt-0.5 font-medium">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Scroll cue */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 opacity-40">
        <span className="text-xs text-slate-500 font-medium">Scroll to explore</span>
        <div className="w-px h-8 bg-gradient-to-b from-slate-500 to-transparent" />
      </div>
    </section>
  )
}

