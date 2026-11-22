import { useCallback, useEffect, useState } from 'react'
import { Bookmark, Heart, Loader2, MapPin, Plus, Trash2 } from 'lucide-react'
import { addDestinationToTrip, createTripPlan, deleteTripPlan, fetchSavedDestinations, fetchTripPlans, type SavedDestination, type TripPlan } from '../api/traveller'
import { getStoredAuth } from '../utils/auth'

export default function MyTrips() {
  const [saved, setSaved] = useState<SavedDestination[]>([])
  const [plans, setPlans] = useState<TripPlan[]>([])
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [selectedPlan, setSelectedPlan] = useState<number | null>(null)

  const refresh = useCallback(async () => {
    const auth = getStoredAuth()
    if (!auth) { setSaved([]); setPlans([]); setLoading(false); return }
    setLoading(true)
    try {
      const [nextSaved, nextPlans] = await Promise.all([fetchSavedDestinations(auth.access_token), fetchTripPlans(auth.access_token)])
      setSaved(nextSaved); setPlans(nextPlans)
      setSelectedPlan((current) => current ?? nextPlans[0]?.id ?? null)
    } catch { setMessage('Your saved travel data could not load. Please sign in again.') }
    finally { setLoading(false) }
  }, [])

  useEffect(() => {
    refresh()
    window.addEventListener('wanderlust:auth-changed', refresh)
    return () => window.removeEventListener('wanderlust:auth-changed', refresh)
  }, [refresh])

  const createPlan = async (event: React.FormEvent) => {
    event.preventDefault()
    const auth = getStoredAuth(); if (!auth || !title.trim()) return
    try {
      const plan = await createTripPlan({ title: title.trim() }, auth.access_token)
      setPlans((current) => [plan, ...current]); setSelectedPlan(plan.id); setTitle(''); setMessage('New trip plan created.')
    } catch (error: any) { setMessage(error?.message || 'Could not create this plan.') }
  }

  const addSavedPlace = async (destinationId: number) => {
    const auth = getStoredAuth(); if (!auth || !selectedPlan) { setMessage('Create or choose a trip plan first.'); return }
    try {
      const updated = await addDestinationToTrip(selectedPlan, destinationId, auth.access_token)
      setPlans((current) => current.map((plan) => plan.id === updated.id ? updated : plan)); setMessage('Destination added to your plan.')
    } catch (error: any) { setMessage(error?.message || 'Could not add this destination.') }
  }

  const removePlan = async (tripId: number) => {
    const auth = getStoredAuth(); if (!auth) return
    try { await deleteTripPlan(tripId, auth.access_token); setPlans((current) => current.filter((plan) => plan.id !== tripId)); setSelectedPlan(null); setMessage('Trip plan deleted.') }
    catch (error: any) { setMessage(error?.message || 'Could not delete this plan.') }
  }

  const signedIn = Boolean(getStoredAuth())
  return <section id="my-trips" className="py-24 px-6 bg-[#0a0f1e] scroll-mt-6">
    <div className="max-w-7xl mx-auto">
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6 mb-10">
        <div><span className="inline-flex items-center gap-2 text-xs font-semibold text-sky-400 uppercase tracking-widest"><Bookmark className="w-3.5 h-3.5" />Traveller space</span><h2 className="mt-3 text-4xl md:text-5xl font-black text-white">My saved trips</h2><p className="mt-3 text-slate-400 max-w-2xl">Save places from search results, then collect them into private trip plans that follow your account.</p></div>
        {signedIn && <form onSubmit={createPlan} className="flex flex-col sm:flex-row gap-2"><input value={title} onChange={(event) => setTitle(event.target.value)} maxLength={100} placeholder="e.g. Delhi heritage weekend" className="min-w-64 rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white outline-none focus:border-sky-400" /><button className="inline-flex justify-center items-center gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-500 px-4 py-3 text-sm font-bold text-white"><Plus className="w-4 h-4" />Create plan</button></form>}
      </div>
      {!signedIn ? <div className="glass-card rounded-3xl p-8 md:p-10 text-center"><Heart className="w-8 h-8 mx-auto text-rose-300 mb-4" /><h3 className="text-xl font-bold text-white">Sign in to keep your travel ideas</h3><p className="mt-2 text-slate-400">Your saved destinations and trip plans are private to your Wanderlust account.</p></div> : loading ? <div className="glass-card rounded-3xl p-10 flex items-center justify-center gap-3 text-slate-300"><Loader2 className="w-5 h-5 animate-spin" />Loading your travel space…</div> : <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-6">
        <div className="glass-card rounded-3xl p-6"><div className="flex items-center gap-2 text-white font-bold"><Heart className="w-4 h-4 text-rose-300" />Saved destinations <span className="text-slate-500 text-sm">{saved.length}</span></div>{saved.length ? <div className="mt-5 space-y-3">{saved.map(({ destination }) => <div key={destination.id} className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-2xl bg-white/[0.03] border border-white/5 p-4"><div><p className="font-semibold text-white">{destination.name}</p><p className="text-sm text-slate-400 flex items-center gap-1"><MapPin className="w-3.5 h-3.5" />{destination.country}</p></div><button onClick={() => addSavedPlace(Number(destination.id))} className="text-sm font-semibold rounded-xl border border-sky-400/25 px-3 py-2 text-sky-200 hover:bg-sky-500/10">Add to selected plan</button></div>)}</div> : <p className="mt-5 text-sm text-slate-400">Save a destination from any result card to start planning.</p>}</div>
        <div className="glass-card rounded-3xl p-6"><div className="flex items-center gap-2 text-white font-bold"><Bookmark className="w-4 h-4 text-sky-300" />Trip plans</div>{plans.length ? <div className="mt-5 space-y-3">{plans.map((plan) => <div key={plan.id} className={`rounded-2xl border p-4 ${selectedPlan === plan.id ? 'border-sky-400/40 bg-sky-500/10' : 'border-white/5 bg-white/[0.03]'}`}><div className="flex items-start justify-between gap-3"><button onClick={() => setSelectedPlan(plan.id)} className="text-left"><p className="font-semibold text-white">{plan.title}</p><p className="text-xs text-slate-400 mt-1">{plan.destinations.length} destination{plan.destinations.length === 1 ? '' : 's'} · {selectedPlan === plan.id ? 'Selected' : 'Select to add saved places'}</p></button><button onClick={() => removePlan(plan.id)} className="p-2 text-slate-500 hover:text-rose-300" aria-label={`Delete ${plan.title}`}><Trash2 className="w-4 h-4" /></button></div>{plan.destinations.length > 0 && <p className="mt-3 text-sm text-slate-300">{plan.destinations.map((destination) => destination.name).join(' · ')}</p>}</div>)}</div> : <p className="mt-5 text-sm text-slate-400">Create a plan, then add your saved destinations.</p>}</div>
      </div>}
      {message && <p className="mt-5 text-sm text-sky-200" role="status">{message}</p>}
    </div>
  </section>
}
