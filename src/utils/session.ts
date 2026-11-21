/**
 * Client Session and Contributor Identity Management (Stage 3).
 * Fetches and persists server-signed HMAC session tokens to prevent client forgery.
 */
import { apiClient } from '../api/client';
import { getStoredAuth } from './auth';

const SESSION_TOKEN_KEY = 'wanderlust_signed_session_token';
const ENDORSED_SET_KEY = 'wanderlust_endorsed_destinations';

let cachedSessionPromise: Promise<string> | null = null;

export function clearSignedSession(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(SESSION_TOKEN_KEY);
  localStorage.removeItem(ENDORSED_SET_KEY);
  cachedSessionPromise = null;
}

export async function getOrFetchSessionToken(): Promise<string> {
  if (typeof window === 'undefined') {
    return 'demo-session-ssr';
  }

  const existing = localStorage.getItem(SESSION_TOKEN_KEY);
  if (existing && existing.startsWith('wl_sec_')) {
    return existing;
  }

  // Prevent multiple concurrent fetch calls for session token
  if (!cachedSessionPromise) {
    cachedSessionPromise = (async () => {
      try {
        const authToken = getStoredAuth()?.access_token;
        const res = await apiClient<{ session_id: string }>('/session', {
          headers: authToken ? { Authorization: `Bearer ${authToken}` } : undefined,
        });
        if (res && res.session_id) {
          localStorage.setItem(SESSION_TOKEN_KEY, res.session_id);
          return res.session_id;
        }
      } catch (err) {
        console.warn('Could not fetch a signed demo-session token', err);
      }
      throw new Error('Could not start a demo session. Please check that the Wanderlust API is available.');
    })().finally(() => {
      cachedSessionPromise = null;
    });
  }

  return cachedSessionPromise;
}

export function getEndorsedDestinations(): Set<number> {
  if (typeof window === 'undefined') {
    return new Set();
  }
  try {
    const raw = localStorage.getItem(ENDORSED_SET_KEY);
    return raw ? new Set(JSON.parse(raw)) : new Set();
  } catch {
    return new Set();
  }
}

export function markDestinationEndorsed(destinationId: number): void {
  if (typeof window === 'undefined') return;
  try {
    const set = getEndorsedDestinations();
    set.add(destinationId);
    localStorage.setItem(ENDORSED_SET_KEY, JSON.stringify(Array.from(set)));
  } catch (e) {
    console.error('Failed to save endorsed destination to localStorage', e);
  }
}

export function unmarkDestinationEndorsed(destinationId: number): void {
  if (typeof window === 'undefined') return;
  try {
    const set = getEndorsedDestinations();
    set.delete(destinationId);
    localStorage.setItem(ENDORSED_SET_KEY, JSON.stringify(Array.from(set)));
  } catch (e) {
    console.error('Failed to update endorsed destination in localStorage', e);
  }
}
