export interface DestinationScores {
  final_score: number;
  endorsement_score: number;
  rating_score: number;
  relevance_score: number;
}

export interface Destination {
  id: number | string;
  name: string;
  country: string;
  region: string;
  description: string;
  category?: string;
  tags: string[];
  rating: number;
  review_count?: number;
  endorsement_count?: number;
  price_inr?: number;
  best_season?: string;
  image_url?: string;
  created_at?: string;
  scores?: DestinationScores;

  // Backward compatibility convenience aliases if needed
  image?: string;
  priceINR?: number;
  reviews?: number;
  endorsements?: number;
  season?: string;
  trending?: boolean;
}

export interface PaginatedDestinations {
  items: Destination[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface RecommendationResponse {
  query?: string;
  total: number;
  results: Destination[];
}

export interface EndorsementResponse {
  status: string;
  destination_id: number;
  new_count: number;
  already_endorsed: boolean;
}

export interface NavLink {
  label: string;
  href: string;
}

export interface HowItWorksStep {
  id: number;
  icon: string;
  title: string;
  description: string;
}

export type VoiceErrorType =
  | 'permission-denied'
  | 'no-speech'
  | 'audio-capture'
  | 'network'
  | 'unsupported'
  | 'unknown';

