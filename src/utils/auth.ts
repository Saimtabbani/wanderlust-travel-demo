import type { AuthSession } from '../types'

const AUTH_STORAGE_KEY = 'wanderlust.auth.v1'

export function getStoredAuth(): AuthSession | null {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY)
    if (!raw) return null
    const session = JSON.parse(raw) as AuthSession
    if (!session.access_token || new Date(session.expires_at) <= new Date()) {
      localStorage.removeItem(AUTH_STORAGE_KEY)
      return null
    }
    return session
  } catch { return null }
}

export function storeAuth(session: AuthSession) { localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session)) }
export function clearStoredAuth() { localStorage.removeItem(AUTH_STORAGE_KEY) }
