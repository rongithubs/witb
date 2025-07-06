export type WITBItem = {
  category: string;
  brand: string;
  model: string;
  loft?: string;
  shaft?: string;
  product_url?: string;
};

export type Player = {
  id: string;
  name: string;
  country: string;
  tour: string;
  age?: number;
  ranking?: number;
  photo_url?: string;
  witb_items: WITBItem[];
};

export type PaginatedPlayersResponse = {
  items: Player[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
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
