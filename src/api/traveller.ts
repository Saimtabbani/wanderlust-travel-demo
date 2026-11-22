import { apiClient } from './client'
import type { Destination } from '../types'

export interface SavedDestination {
  id: number
  destination: Destination
  created_at: string
}

export interface TripPlan {
  id: number
  title: string
  notes: string
  created_at: string
  updated_at: string
  destinations: Destination[]
}

const authHeader = (token: string) => ({ Authorization: `Bearer ${token}` })

export const saveDestination = (destinationId: number, token: string) =>
  apiClient<SavedDestination>(`/traveller/favorites/${destinationId}`, { method: 'POST', headers: authHeader(token) })

export const unsaveDestination = (destinationId: number, token: string) =>
  apiClient<void>(`/traveller/favorites/${destinationId}`, { method: 'DELETE', headers: authHeader(token) })

export const fetchSavedDestinations = (token: string) =>
  apiClient<SavedDestination[]>('/traveller/favorites', { headers: authHeader(token) })

export const fetchTripPlans = (token: string) =>
  apiClient<TripPlan[]>('/traveller/trips', { headers: authHeader(token) })

export const createTripPlan = (payload: { title: string; notes?: string }, token: string) =>
  apiClient<TripPlan>('/traveller/trips', { method: 'POST', headers: authHeader(token), body: JSON.stringify(payload) })

export const addDestinationToTrip = (tripId: number, destinationId: number, token: string) =>
  apiClient<TripPlan>(`/traveller/trips/${tripId}/destinations/${destinationId}`, { method: 'POST', headers: authHeader(token) })
