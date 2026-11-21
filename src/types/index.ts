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
  latitude?: number;
  longitude?: number;
  source_name?: string;
  source_url?: string;
  source_license?: string;
  source_checked_at?: string;
  source_record_id?: string;
  population?: number;
  timezone?: string;
  data_quality?: string;
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

export interface Account {
  id: number;
  email: string;
  display_name: string;
  created_at: string;
}

export interface AuthSession {
  access_token: string;
  token_type: string;
  expires_at: string;
  account: Account;
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

