import { apiClient } from './client';
import type { EndorsementResponse } from '../types';

export async function postEndorsement(
  destinationId: number,
  sessionId: string,
  contributorId?: number
): Promise<EndorsementResponse> {
  return apiClient<EndorsementResponse>('/endorsements', {
    method: 'POST',
    body: JSON.stringify({
      destination_id: destinationId,
      session_id: sessionId,
      contributor_id: contributorId,
    }),
  });
}

export async function deleteEndorsement(
  destinationId: number,
  sessionId: string
): Promise<EndorsementResponse> {
  return apiClient<EndorsementResponse>('/endorsements', {
    method: 'DELETE',
    body: JSON.stringify({
      destination_id: destinationId,
      session_id: sessionId,
    }),
  });
}

export async function fetchEndorsementCount(
  destinationId: number,
  signal?: AbortSignal
): Promise<{ destination_id: number; count: number }> {
  return apiClient<{ destination_id: number; count: number }>(`/destinations/${destinationId}/endorsements`, {
    signal,
  });
}
