export type WITBItem = {
  category: string;
  brand: string;
  model: string;
  loft?: string;
  shaft?: string;
  product_url?: string;
  source_url?: string;
};

export type Player = {
  id: string;
  name: string;
  country: string;
  tour: string;
  age?: number;
  ranking?: number;
  photo_url?: string;
  last_updated?: string;
  witb_items: WITBItem[];
};

export type SystemInfo = {
  owgr_last_updated?: string;
  owgr_updated_count?: number;
  owgr_total_processed?: number;
};

export type PaginatedPlayersResponse = {
  items: Player[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  system_info?: SystemInfo;
};

export type AsyncState<T> = {
  data: T | null;
  error: Error | null;
  isLoading: boolean;
};

export type DataHookReturn<T> = {
  data: T | null;
  error: Error | null;
  isLoading: boolean;
  isEmpty: boolean;
  refetch: () => void;
};

export type User = {
  id: string;
  supabase_user_id: string;
  email?: string;
  phone?: string;
  created_at: string;
  updated_at: string;
};

export type FavoritePlayer = {
  id: string;
  player: Player;
  created_at: string;
};

export type UserFavoritesResponse = {
  favorites: FavoritePlayer[];
  total: number;
};

// eBay API Integration Types
export type EBayPriceInfo = {
  current_price: number;
  currency: string;
  condition: string;
  shipping_cost?: number;
  buy_it_now_price?: number;
  auction_end_time?: string;
};

export type EBayProduct = {
  product_id: string;
  title: string;
  brand?: string;
  model?: string;
  category?: string;
  price_info: EBayPriceInfo;
  listing_url: string;
  image_url?: string;
  seller_info?: {
    username: string;
    feedback_percentage?: number;
    feedback_score?: number;
  };
  location?: string;
  listing_type: string;
};

export type EBaySearchResponse = {
  products: EBayProduct[];
  total_found: number;
  page: number;
  per_page: number;
  search_query: string;
};

export type EBaySearchParams = {
  brand?: string;
  model?: string;
  category?: string;
  condition?: string;
  max_price?: number;
  min_price?: number;
  limit?: number;
};
