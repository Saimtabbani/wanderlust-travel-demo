import { apiClient } from './client';
import type { Destination, PaginatedDestinations, RecommendationResponse } from '../types';

export interface DestinationFilterParams {
  page?: number;
  page_size?: number;
  region?: string;
  category?: string;
  max_budget?: number;
  sort_by?: string;
  signal?: AbortSignal;
}

export interface RecommendationParams {
  q?: string;
  region?: string;
  category?: string;
  max_budget?: number;
  limit?: number;
  weight_endorsement?: number;
  weight_rating?: number;
  weight_relevance?: number;
  signal?: AbortSignal;
}

export async function fetchDestinations(params: DestinationFilterParams = {}): Promise<PaginatedDestinations> {
  const query = new URLSearchParams();
  if (params.page) query.append('page', params.page.toString());
  if (params.page_size) query.append('page_size', params.page_size.toString());
  if (params.region && params.region !== 'All') query.append('region', params.region);
  if (params.category && params.category !== 'All') query.append('category', params.category);
  if (params.max_budget) query.append('max_budget', params.max_budget.toString());
  if (params.sort_by) query.append('sort_by', params.sort_by);

  const qs = query.toString();
  return apiClient<PaginatedDestinations>(`/destinations${qs ? `?${qs}` : ''}`, {
    signal: params.signal,
  });
}

export async function fetchRecommendations(params: RecommendationParams = {}): Promise<RecommendationResponse> {
  const query = new URLSearchParams();
  if (params.q) query.append('q', params.q.trim());
  if (params.region && params.region !== 'All') query.append('region', params.region);
  if (params.category && params.category !== 'All') query.append('category', params.category);
  if (params.max_budget) query.append('max_budget', params.max_budget.toString());
  if (params.limit) query.append('limit', params.limit.toString());
  if (params.weight_endorsement !== undefined) query.append('weight_endorsement', params.weight_endorsement.toString());
  if (params.weight_rating !== undefined) query.append('weight_rating', params.weight_rating.toString());
  if (params.weight_relevance !== undefined) query.append('weight_relevance', params.weight_relevance.toString());

  const qs = query.toString();
  return apiClient<RecommendationResponse>(`/recommendations${qs ? `?${qs}` : ''}`, {
    signal: params.signal,
  });
}

export async function fetchDestinationById(id: number, signal?: AbortSignal): Promise<Destination> {
  return apiClient<Destination>(`/destinations/${id}`, { signal });
}

export interface TravelEstimate {
  destination_id: number;
  distance_km: number;
  estimated_flight_hours: number;
  assumptions: string;
}

export async function fetchTravelEstimate(id: number, signal?: AbortSignal): Promise<TravelEstimate> {
  return apiClient<TravelEstimate>(`/destinations/${id}/travel-estimate`, { signal });
}
