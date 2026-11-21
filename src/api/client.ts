/**
 * Base HTTP Client for Wanderlust API
 * Uses relative /api endpoint via Vite proxy, supporting AbortSignal for request cancellation.
 */
const API_BASE = (import.meta as any).env?.VITE_API_URL || '/api';

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(status: number, message: string, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

export async function apiClient<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${API_BASE}${path}`;

  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { detail: response.statusText };
      }
      const message = errorData?.detail || `HTTP Error ${response.status}`;
      throw new ApiError(response.status, message, errorData);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    // Handle request abortion cleanly
    if ((error as any)?.name === 'AbortError') {
      throw error;
    }
    // Network error or fetch failure
    throw new ApiError(0, 'Unable to connect to Wanderlust backend service. Ensure FastAPI is running on port 8000.');
  }
}
