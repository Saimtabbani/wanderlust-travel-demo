import { apiClient } from './client'
import type { Account, AuthSession } from '../types'

export const registerAccount = (payload: { email: string; display_name: string; password: string }) =>
  apiClient<AuthSession>('/auth/register', { method: 'POST', body: JSON.stringify(payload) })

export const loginAccount = (payload: { email: string; password: string }) =>
  apiClient<AuthSession>('/auth/login', { method: 'POST', body: JSON.stringify(payload) })

export const logoutAccount = (token: string) =>
  apiClient<void>('/auth/logout', { method: 'POST', headers: { Authorization: `Bearer ${token}` } })

export const fetchCurrentAccount = (token: string) =>
  apiClient<Account>('/auth/me', { headers: { Authorization: `Bearer ${token}` } })
