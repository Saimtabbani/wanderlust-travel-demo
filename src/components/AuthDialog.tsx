import { useState } from 'react'
import { X, LockKeyhole, Loader2 } from 'lucide-react'
import { loginAccount, registerAccount } from '../api/auth'
import type { Account } from '../types'
import { storeAuth } from '../utils/auth'
import { clearSignedSession } from '../utils/session'

interface AuthDialogProps { onClose: () => void; onAuthenticated: (account: Account) => void }

export default function AuthDialog({ onClose, onAuthenticated }: AuthDialogProps) {
  const [mode, setMode] = useState<'sign-in' | 'create'>('sign-in')
  const [email, setEmail] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const submit = async (event: React.FormEvent) => {
    event.preventDefault(); setSubmitting(true); setError(null)
    try {
      const session = mode === 'create'
        ? await registerAccount({ email, display_name: displayName, password })
        : await loginAccount({ email, password })
      clearSignedSession(); storeAuth(session); onAuthenticated(session.account); onClose()
    } catch (caught: any) { setError(caught?.message || 'We could not complete that request.') }
    finally { setSubmitting(false) }
  }
  return <div className="fixed inset-0 z-[70] flex items-end sm:items-center justify-center p-0 sm:p-5 bg-slate-950/75 backdrop-blur-sm" role="dialog" aria-modal="true" aria-labelledby="auth-title">
    <form onSubmit={submit} className="w-full sm:max-w-md rounded-t-3xl sm:rounded-3xl glass-card border-white/15 p-6 sm:p-8 shadow-2xl">
      <div className="flex items-start justify-between gap-4"><div><div className="w-10 h-10 rounded-xl bg-sky-500/15 text-sky-300 flex items-center justify-center mb-4"><LockKeyhole className="w-5 h-5" /></div><h2 id="auth-title" className="text-xl font-bold text-white">{mode === 'create' ? 'Create your traveller account' : 'Welcome back'}</h2><p className="mt-1 text-sm text-slate-400">{mode === 'create' ? 'Use 12 or more characters for your password.' : 'Sign in to keep your traveller profile.'}</p></div><button type="button" onClick={onClose} className="p-2 text-slate-400 hover:text-white" aria-label="Close account dialog"><X className="w-5 h-5" /></button></div>
      <div className="mt-6 space-y-4">{mode === 'create' && <label className="block text-sm text-slate-300">Display name<input required value={displayName} onChange={(event) => setDisplayName(event.target.value)} className="mt-1.5 w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2.5 text-white outline-none focus:border-sky-400" /></label>}<label className="block text-sm text-slate-300">Email<input required type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} className="mt-1.5 w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2.5 text-white outline-none focus:border-sky-400" /></label><label className="block text-sm text-slate-300">Password<input required minLength={mode === 'create' ? 12 : undefined} type="password" autoComplete={mode === 'create' ? 'new-password' : 'current-password'} value={password} onChange={(event) => setPassword(event.target.value)} className="mt-1.5 w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2.5 text-white outline-none focus:border-sky-400" /></label></div>
      {error && <p role="alert" className="mt-4 text-sm text-rose-300">{error}</p>}<button disabled={submitting} className="mt-6 w-full inline-flex justify-center items-center gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-500 px-4 py-3 font-semibold text-white disabled:opacity-60">{submitting && <Loader2 className="w-4 h-4 animate-spin" />}{mode === 'create' ? 'Create account' : 'Sign in'}</button><button type="button" onClick={() => { setMode(mode === 'create' ? 'sign-in' : 'create'); setError(null) }} className="mt-4 w-full text-sm text-sky-300 hover:text-sky-200">{mode === 'create' ? 'Already have an account? Sign in' : 'New to Wanderlust? Create an account'}</button>
    </form>
  </div>
}
