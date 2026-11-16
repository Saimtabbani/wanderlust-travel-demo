import { useState } from 'react'
import { Star, ThumbsUp, TrendingUp, MapPin, Check, Loader2, Sparkles, ShieldCheck } from 'lucide-react'
import type { Destination } from '../types'
import { formatINR } from '../utils/currency'
import { postEndorsement, deleteEndorsement } from '../api/endorsements'
import { getOrFetchSessionToken, getEndorsedDestinations, markDestinationEndorsed, unmarkDestinationEndorsed } from '../utils/session'

interface DestinationCardProps {
  destination: Destination
  delay?: number
  onEndorsementSuccess?: (destinationId: number, newCount: number) => void
}

export default function DestinationCard({ destination, delay = 0, onEndorsementSuccess }: DestinationCardProps) {
  const {
    id,
    name,
    country,
    tags = [],
    description,
    rating = 4.5,
    trending,
    scores,
  } = destination

  // Handle both backend API field names and fallback aliases
  const imageUrl = destination.image_url || destination.image || ''
  const price = destination.price_inr ?? destination.priceINR ?? 0
  const reviews = destination.review_count ?? destination.reviews ?? 0
  const initialEndorsements = destination.endorsement_count ?? destination.endorsements ?? 0
  const season = destination.best_season || destination.season || 'Year-round'

  const numericId = typeof id === 'number' ? id : parseInt(String(id), 10)

  // Session endorsement state
  const isInitiallyEndorsed = !isNaN(numericId) && getEndorsedDestinations().has(numericId)
  const [isEndorsed, setIsEndorsed] = useState<boolean>(isInitiallyEndorsed)
  const [endorsementCount, setEndorsementCount] = useState<number>(initialEndorsements)
  const [isActionInProgress, setIsActionInProgress] = useState<boolean>(false)
  const [actionNotice, setActionNotice] = useState<string | null>(null)

  const handleToggleEndorse = async (e: React.MouseEvent) => {
    e.stopPropagation()
    if (isActionInProgress || isNaN(numericId)) return

    setIsActionInProgress(true)
    setActionNotice(null)

    try {
      const sessionId = await getOrFetchSessionToken()

      if (!isEndorsed) {
        // ── Case A: Cast New Endorsement ──
        const optimisticCount = endorsementCount + 1
        setEndorsementCount(optimisticCount)
        setIsEndorsed(true)
        markDestinationEndorsed(numericId)

        const res = await postEndorsement(numericId, sessionId)
        if (res && res.new_count !== undefined) {
          setEndorsementCount(res.new_count)
          if (onEndorsementSuccess) {
            onEndorsementSuccess(numericId, res.new_count)
          }
        }
      } else {
        // ── Case B: Withdraw Existing Endorsement ──
        const optimisticCount = Math.max(0, endorsementCount - 1)
        setEndorsementCount(optimisticCount)
        setIsEndorsed(false)
        unmarkDestinationEndorsed(numericId)

        const res = await deleteEndorsement(numericId, sessionId)
        if (res && res.new_count !== undefined) {
          setEndorsementCount(res.new_count)
          if (onEndorsementSuccess) {
            onEndorsementSuccess(numericId, res.new_count)
          }
        }
      }
    } catch (err: any) {
      // Handle known 409 or network failures
      if (err?.status === 409) {
        setIsEndorsed(true)
        markDestinationEndorsed(numericId)
        setActionNotice('Already endorsed in this session')
      } else {
        // Revert on error
        setEndorsementCount(initialEndorsements)
        setIsEndorsed(isInitiallyEndorsed)
        setActionNotice(err?.message || 'Action could not be completed')
      }
    } finally {
      setIsActionInProgress(false)
    }
  }

  return (
    <div
      className="card-shine glass-card rounded-2xl overflow-hidden hover:scale-[1.02] hover:border-white/15 transition-all duration-300 cursor-pointer group flex flex-col h-full"
      style={{ animationDelay: `${delay}s` }}
    >
      {/* ── Image (fixed height, never squishes) ── */}
      <div className="relative h-52 flex-shrink-0 overflow-hidden">
        <img
          src={imageUrl}
          alt={`${name}, ${country}`}
          loading="lazy"
          decoding="async"
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />

        {/* Badges container */}
        <div className="absolute top-3 left-3 flex flex-wrap gap-1.5 items-center">
          {/* Trending badge */}
          {trending && (
            <div className="flex items-center gap-1 bg-orange-500/90 backdrop-blur-sm text-white text-xs font-bold px-2.5 py-1 rounded-full whitespace-nowrap">
              <TrendingUp className="w-3 h-3 flex-shrink-0" />
              Trending
            </div>
          )}

          {/* Stage 3 Trust-Aware Recommendation match badge */}
          {scores && scores.final_score > 0 && (
            <div
              className="flex items-center gap-1 bg-gradient-to-r from-sky-500/90 to-indigo-600/90 backdrop-blur-sm text-white text-xs font-bold px-2.5 py-1 rounded-full shadow-lg shadow-indigo-500/20 whitespace-nowrap"
              title={`Recommendation Score: ${scores.final_score}% (Trust-Weighted Endorsements: ${scores.endorsement_score}%, Rating: ${scores.rating_score}%, Relevance: ${scores.relevance_score}%)`}
            >
              <Sparkles className="w-3 h-3 text-sky-200 flex-shrink-0" />
              <span>{scores.final_score}% Match</span>
            </div>
          )}
        </div>

        {/* Price badge — INR, en-IN locale */}
        <div className="absolute top-3 right-3 glass text-white text-xs font-bold px-2.5 py-1 rounded-full whitespace-nowrap">
          from {formatINR(price)}
        </div>

        {/* Location */}
        <div className="absolute bottom-3 left-3 flex items-center gap-1 text-white text-sm font-bold min-w-0 pr-3">
          <MapPin className="w-3.5 h-3.5 text-sky-300 flex-shrink-0" />
          <span className="truncate">{name}, {country}</span>
        </div>
      </div>

      {/* ── Card body (grows to fill remaining height) ── */}
      <div className="p-5 flex flex-col flex-1">
        {/* Tags — fixed row, no overflow wrap beyond 2 lines */}
        <div className="flex flex-wrap gap-1.5 mb-3">
          {tags.map((tag) => (
            <span
              key={tag}
              className="text-xs px-2.5 py-0.5 rounded-full bg-sky-500/10 text-sky-300 border border-sky-500/20 font-medium whitespace-nowrap"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Description */}
        <p className="text-slate-400 text-sm leading-relaxed line-clamp-2 mb-4 min-h-[2.75rem] flex-1">
          {description}
        </p>

        {/* ── Stats & Endorsement footer ── */}
        <div className="mt-auto pt-3 border-t border-white/5 space-y-2.5">
          {/* Row 1: Rating stars + Best season */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1">
              <Star className="w-4 h-4 text-amber-400 fill-amber-400 flex-shrink-0" />
              <span className="text-sm font-bold text-white">{rating}</span>
              <span className="text-xs text-slate-500 ml-0.5">
                ({reviews.toLocaleString('en-IN')})
              </span>
            </div>

            <div className="text-right">
              <p className="text-xs text-slate-500 leading-none">Best season</p>
              <p className="text-xs text-slate-300 font-medium mt-0.5 whitespace-nowrap">{season}</p>
            </div>
          </div>

          {/* Row 2: Live Endorsement count + Interactive Endorse/Withdraw Button */}
          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center gap-1.5 text-indigo-400" title="Community endorsements weighted by contributor credibility">
              <ThumbsUp className="w-3.5 h-3.5 flex-shrink-0" />
              <span className="text-xs font-semibold whitespace-nowrap">
                {endorsementCount.toLocaleString('en-IN')} endorsements
              </span>
              <span title="Trust-weighted system enabled">
                <ShieldCheck className="w-3 h-3 text-sky-400/80 ml-0.5" />
              </span>
            </div>

            <button
              onClick={handleToggleEndorse}
              disabled={isActionInProgress}
              className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-xl transition-all cursor-pointer ${
                isEndorsed
                  ? 'bg-emerald-500/20 hover:bg-rose-500/20 text-emerald-300 hover:text-rose-300 border border-emerald-500/30 hover:border-rose-500/30'
                  : 'bg-indigo-500/15 hover:bg-indigo-500/25 text-indigo-300 border border-indigo-500/30 hover:scale-105 active:scale-95 shadow-sm'
              }`}
              title={isEndorsed ? 'Click to withdraw your endorsement' : 'Endorse this destination (trust-weighted)'}
            >
              {isActionInProgress ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : isEndorsed ? (
                <>
                  <Check className="w-3 h-3 text-emerald-400" />
                  <span>Endorsed</span>
                </>
              ) : (
                <>
                  <ThumbsUp className="w-3 h-3" />
                  <span>Endorse</span>
                </>
              )}
            </button>
          </div>

          {actionNotice && (
            <p className="text-[11px] text-amber-400 text-right">{actionNotice}</p>
          )}
        </div>
      </div>
    </div>
  )
}
