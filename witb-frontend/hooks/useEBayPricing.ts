import { useState, useCallback } from 'react';
import { WITBItem, EBaySearchResponse, EBayProduct } from '@/types/schemas';
import { ebayApi } from '@/utils/ebayApi';

export type PriceSummary = {
  minPrice: number;
  maxPrice: number;
  averagePrice: number;
  listingCount: number;
};

export type EBayPricingState = {
  priceSummary: PriceSummary | null;
  searchResponse: EBaySearchResponse | null;
  isLoading: boolean;
  hasError: boolean;
};

export type EBayPricingActions = {
  fetchPriceData: () => Promise<void>;
  reset: () => void;
};

export function useEBayPricing(witbItem: WITBItem): EBayPricingState & EBayPricingActions {
  const [priceSummary, setPriceSummary] = useState<PriceSummary | null>(null);
  const [searchResponse, setSearchResponse] = useState<EBaySearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasError, setHasError] = useState(false);

  const createEmptySummary = (): PriceSummary => ({
    minPrice: 0,
    maxPrice: 0,
    averagePrice: 0,
    listingCount: 0,
  });

  const calculatePriceSummary = (products: EBayProduct[]): PriceSummary => {
    if (products.length === 0) {
      return createEmptySummary();
    }
    
    const prices = products.map(p => p.price_info.current_price);
    return {
      minPrice: Math.min(...prices),
      maxPrice: Math.max(...prices),
      averagePrice: Math.round(prices.reduce((sum, price) => sum + price, 0) / prices.length),
      listingCount: products.length,
    };
  };

  const fetchPriceData = useCallback(async () => {
    if (isLoading) return; // Prevent concurrent requests

    setIsLoading(true);
    setHasError(false);
    
    try {
      const response = await ebayApi.searchForWITBItem(
        witbItem.brand,
        witbItem.model,
        witbItem.category
      );
      
      setSearchResponse(response);
      setPriceSummary(calculatePriceSummary(response.products));
    } catch (error) {
      console.error('Error fetching price data:', error);
      setHasError(true);
      setPriceSummary(createEmptySummary());
      setSearchResponse(null);
    } finally {
      setIsLoading(false);
    }
  }, [witbItem.brand, witbItem.model, witbItem.category, isLoading]);

  const reset = useCallback(() => {
    setPriceSummary(null);
    setSearchResponse(null);
    setIsLoading(false);
    setHasError(false);
  }, []);

  return {
    priceSummary,
    searchResponse,
    isLoading,
    hasError,
    fetchPriceData,
    reset,
  };
}