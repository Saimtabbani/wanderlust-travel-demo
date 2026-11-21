import { useState, useEffect, useCallback } from 'react'
import { SlidersHorizontal, AlertCircle, RefreshCw, Sparkles, X, Compass, Volume2, Square } from 'lucide-react'
import DestinationCard from './DestinationCard'
import type { Destination } from '../types'
import { fetchDestinations, fetchRecommendations } from '../api/destinations'
import { useSpeechSynthesis } from '../hooks/useSpeechSynthesis'

const regions = ['All', 'India', 'Asia', 'Europe', 'South America']

const budgetOptions = [
  { label: 'All Budgets', value: undefined },
  { label: 'Under ₹15,000', value: 15000 },
  { label: 'Under ₹30,000', value: 30000 },
  { label: 'Under ₹70,000', value: 70000 },
  { label: 'Under ₹1,20,000', value: 120000 },
]

interface DestinationsSectionProps {
  searchQuery?: string
  onClearSearch?: () => void
}

export default function DestinationsSection({ searchQuery = '', onClearSearch }: DestinationsSectionProps) {
  const [activeRegion, setActiveRegion] = useState('All')
  const [maxBudget, setMaxBudget] = useState<number | undefined>(undefined)
  const [showFilters, setShowFilters] = useState(false)

  const [destinations, setDestinations] = useState<Destination[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState<number>(1)
  const [totalPages, setTotalPages] = useState<number>(1)
  const [totalCount, setTotalCount] = useState<number>(0)

  // Speech synthesis for voice assistant audio response
  const { isSpeaking, isSupported: ttsSupported, speak, stop: stopSpeaking } = useSpeechSynthesis()

  const handleToggleSpeech = () => {
    if (isSpeaking) {
      stopSpeaking()
    } else if (destinations.length > 0) {
      const count = destinations.length
      const topDest = destinations[0]
      const names = destinations.slice(0, 3).map((destination) => `${destination.name} in ${destination.country}`).join(', ')
      const speechText = `I found ${count} recommendation${count > 1 ? 's' : ''} for your trip. Your top choice is ${topDest.name} in ${topDest.country}, with a ${topDest.rating} out of 5 prototype rating and a best season of ${topDest.best_season}. Other strong matches include ${names}. Open any card to hear a fuller destination summary and see its coordinate-based planning estimate. Remember that prices, ratings, and endorsements in this research prototype are not live booking data.`
      speak(speechText)
    }
  }

  // Cancel ongoing speech when search query changes
  useEffect(() => {
    stopSpeaking()
  }, [searchQuery, stopSpeaking])

  // Fetch destinations from backend with request cancellation support (AbortController)
  const loadDestinations = useCallback(
    async (currentPage: number, append: boolean = false, signal?: AbortSignal) => {
      setLoading(true)
      setError(null)

      try {
        if (searchQuery.trim()) {
          // Use Stage 3 Trust-Aware Recommendation Engine
          const res = await fetchRecommendations({
            q: searchQuery.trim(),
            region: activeRegion !== 'All' ? activeRegion : undefined,
            max_budget: maxBudget,
            limit: 12,
            signal,
          })
          setDestinations(res.results || [])
          setTotalCount(res.total || 0)
          setTotalPages(1)
        } else {
          // Standard paginated listing with filters
          const res = await fetchDestinations({
            page: currentPage,
            page_size: 9,
            region: activeRegion !== 'All' ? activeRegion : undefined,
            max_budget: maxBudget,
            sort_by: 'endorsements',
            signal,
          })
          if (append) {
            setDestinations((prev) => [...prev, ...res.items])
          } else {
            setDestinations(res.items)
          }
          setTotalCount(res.total)
          setTotalPages(res.pages)
        }
      } catch (err: any) {
        if (err?.name === 'AbortError') {
          // Request was cancelled due to a newer filter/search action; ignore
          return
        }
        console.error('Failed to load destinations:', err)
        setError(err?.message || 'Could not connect to Wanderlust backend service. Ensure FastAPI is running on port 8000.')
      } finally {
        setLoading(false)
      }
    },
    [searchQuery, activeRegion, maxBudget]
  )

  // Reset page and reload whenever filters or search query changes, cancelling obsolete in-flight requests
  useEffect(() => {
    const controller = new AbortController()
    setPage(1)
    loadDestinations(1, false, controller.signal)

    return () => {
      controller.abort()
    }
  }, [loadDestinations])

  const handleLoadMore = () => {
    if (page < totalPages && !loading) {
      const nextPage = page + 1
      setPage(nextPage)
      loadDestinations(nextPage, true)
    }
  }

  // Handle immediate count update when user endorses a card
  const handleEndorsementSuccess = (destinationId: number, newCount: number) => {
    setDestinations((prev) =>
      prev.map((dest) => {
        const destId = typeof dest.id === 'number' ? dest.id : parseInt(String(dest.id), 10)
        if (destId === destinationId) {
          return {
            ...dest,
            endorsement_count: newCount,
            endorsements: newCount,
          }
        }
        return dest
      })
    )
  }

  const handleResetFilters = () => {
    setActiveRegion('All')
    setMaxBudget(undefined)
    if (onClearSearch) onClearSearch()
  }

  return (
    <section id="discover" className="py-24 px-6 bg-[#0d1424] scroll-mt-20">
      <div className="max-w-7xl mx-auto">
        {/* Section header */}
        <div className="text-center mb-10">
          <span className="inline-block text-xs font-semibold text-sky-400 uppercase tracking-widest mb-3">
            {searchQuery ? 'Recommendation Results' : 'Featured Destinations'}
          </span>
          <h2 className="text-4xl md:text-5xl font-black text-white leading-tight">
            {searchQuery ? 'Top Matches for Your Search' : 'Explore Demo Destinations'}
          </h2>
          <p className="mt-4 text-slate-400 max-w-xl mx-auto leading-relaxed">
            {searchQuery
              ? 'Ranked with a transparent 3-factor demo: endorsements, rating, and keyword relevance.'
              : 'Source-documented place identities with transparent prototype scores. Prices, ratings, and endorsements remain research-demo fields.'}
          </p>
        </div>

        {/* Active Search & Voice Assistant Summary Badge */}
        {searchQuery && (
          <div className="flex flex-wrap items-center justify-center gap-3 mb-8">
            <div className="glass px-4 py-2 rounded-2xl flex items-center gap-2.5 border-sky-500/30 text-sm">
              <Sparkles className="w-4 h-4 text-sky-400 flex-shrink-0" />
              <span className="text-slate-300">Searching for:</span>
              <span className="font-bold text-white">"{searchQuery}"</span>
              {onClearSearch && (
                <button
                  onClick={onClearSearch}
                  className="ml-2 w-5 h-5 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-slate-300 hover:text-white transition-colors cursor-pointer"
                  title="Clear search"
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>

            {/* Voice Assistant TTS Speaker Button */}
            {ttsSupported && destinations.length > 0 && (
              <button
                onClick={handleToggleSpeech}
                className={`glass px-4 py-2 rounded-2xl flex items-center gap-2 text-sm font-semibold transition-all cursor-pointer ${
                  isSpeaking
                    ? 'border-indigo-500/60 bg-indigo-500/20 text-indigo-200 animate-pulse'
                    : 'text-slate-300 hover:text-white hover:border-white/20'
                }`}
                title={isSpeaking ? 'Click to stop voice playback' : 'Listen to voice summary of recommendations'}
              >
                {isSpeaking ? (
                  <>
                    <Square className="w-3.5 h-3.5 fill-current text-indigo-400 flex-shrink-0" />
                    <span>Stop Voice</span>
                  </>
                ) : (
                  <>
                    <Volume2 className="w-4 h-4 text-sky-400 flex-shrink-0" />
                    <span>Read Summary</span>
                  </>
                )}
              </button>
            )}
          </div>
        )}

        {/* Filter bar */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          {/* Region Tabs */}
          <div className="flex flex-wrap gap-2">
            {regions.map((region) => (
              <button
                key={region}
                onClick={() => setActiveRegion(region)}
                className={`text-sm font-semibold px-4 py-2 rounded-xl transition-all cursor-pointer ${
                  activeRegion === region
                    ? 'bg-gradient-to-r from-sky-500 to-indigo-500 text-white shadow-lg shadow-indigo-500/20'
                    : 'glass text-slate-400 hover:text-white hover:border-white/15'
                }`}
              >
                {region}
              </button>
            ))}
          </div>

          {/* Budget & Advanced Filter Toggle */}
          <div className="flex items-center gap-3">
            {/* Budget Presets */}
            <div className="hidden sm:flex items-center gap-1.5 glass rounded-xl px-2 py-1">
              <span className="text-xs text-slate-400 px-2 font-medium">Budget:</span>
              {budgetOptions.map((opt) => (
                <button
                  key={opt.label}
                  onClick={() => setMaxBudget(opt.value)}
                  className={`text-xs px-2.5 py-1 rounded-lg transition-all cursor-pointer font-medium ${
                    maxBudget === opt.value
                      ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>

            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`sm:hidden flex items-center gap-2 glass px-4 py-2 rounded-xl text-sm font-semibold transition-all cursor-pointer ${
                showFilters || maxBudget !== undefined ? 'text-sky-300 border-sky-500/30' : 'text-slate-400 hover:text-white'
              }`}
            >
              <SlidersHorizontal className="w-4 h-4" />
              Budget
            </button>
          </div>
        </div>

        {/* Mobile Budget Filter dropdown */}
        {showFilters && (
          <div className="sm:hidden glass rounded-2xl p-4 mb-6 flex flex-wrap gap-2">
            <span className="w-full text-xs text-slate-400 font-semibold mb-1">Select Maximum Trip Budget:</span>
            {budgetOptions.map((opt) => (
              <button
                key={opt.label}
                onClick={() => {
                  setMaxBudget(opt.value)
                  setShowFilters(false)
                }}
                className={`text-xs px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
                  maxBudget === opt.value
                    ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                    : 'glass text-slate-400 hover:text-white'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        )}

        {/* ── ERROR STATE ── */}
        {error && (
          <div className="glass-card rounded-2xl p-8 my-10 max-w-xl mx-auto text-center border-rose-500/20">
            <div className="w-12 h-12 rounded-xl bg-rose-500/10 text-rose-400 flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Backend Connection Notice</h3>
            <p className="text-slate-400 text-sm mb-6 leading-relaxed">{error}</p>
            <button
              onClick={() => loadDestinations(1, false)}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-500 text-white font-semibold text-sm hover:opacity-90 transition-all cursor-pointer"
            >
              <RefreshCw className="w-4 h-4" />
              Retry Connection
            </button>
          </div>
        )}

        {/* ── LOADING SKELETON STATE ── */}
        {loading && destinations.length === 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 items-stretch">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="glass-card rounded-2xl overflow-hidden h-[420px] animate-pulse flex flex-col">
                <div className="h-52 bg-white/5" />
                <div className="p-5 flex-1 flex flex-col justify-between">
                  <div className="space-y-3">
                    <div className="flex gap-2">
                      <div className="h-5 w-16 bg-white/5 rounded-full" />
                      <div className="h-5 w-20 bg-white/5 rounded-full" />
                    </div>
                    <div className="h-4 bg-white/5 rounded w-3/4" />
                    <div className="h-4 bg-white/5 rounded w-full" />
                  </div>
                  <div className="pt-4 border-t border-white/5 flex justify-between items-center">
                    <div className="h-4 w-20 bg-white/5 rounded" />
                    <div className="h-4 w-24 bg-white/5 rounded" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ── EMPTY STATE ── */}
        {!loading && !error && destinations.length === 0 && (
          <div className="glass-card rounded-3xl p-12 text-center max-w-md mx-auto my-12">
            <div className="w-16 h-16 rounded-2xl bg-sky-500/10 text-sky-400 flex items-center justify-center mx-auto mb-4">
              <Compass className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">No Destinations Found</h3>
            <p className="text-slate-400 text-sm mb-6 leading-relaxed">
              We couldn't find destinations matching your criteria. Try adjusting the region or budget filters.
            </p>
            <button
              onClick={handleResetFilters}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl glass text-sky-300 hover:text-white font-semibold text-sm transition-all cursor-pointer hover:border-white/20"
            >
              Reset All Filters
            </button>
          </div>
        )}

        {/* ── DESTINATIONS GRID ── */}
        {!error && destinations.length > 0 && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 items-stretch">
              {destinations.map((dest, i) => (
                <DestinationCard
                  key={dest.id}
                  destination={dest}
                  delay={i * 0.05}
                  onEndorsementSuccess={handleEndorsementSuccess}
                />
              ))}
            </div>

            {/* Load More Button for paginated view */}
            {!searchQuery && page < totalPages && (
              <div className="mt-12 text-center">
                <button
                  onClick={handleLoadMore}
                  disabled={loading}
                  className="inline-flex items-center gap-2 px-8 py-3.5 rounded-2xl glass text-slate-300 hover:text-white hover:border-white/15 font-semibold text-sm transition-all hover:scale-105 cursor-pointer disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Loading Destinations...
                    </>
                  ) : (
                    `Load More Destinations (${destinations.length} of ${totalCount})`
                  )}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </section>
  )
}
