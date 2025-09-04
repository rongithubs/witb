"use client";

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Filter, TrendingUp, Package } from 'lucide-react';
import { WITBItem, EBaySearchResponse } from '@/types/schemas';
import { ebayApi } from '@/utils/ebayApi';
import { PriceCard } from './PriceCard';
import { PricingSkeleton } from './PricingSkeleton';

interface PricingModalProps {
  isOpen: boolean;
  onClose: () => void;
  witbItem: WITBItem;
  initialPriceSummary?: {
    minPrice: number;
    maxPrice: number;
    averagePrice: number;
    listingCount: number;
  } | null;
  initialSearchResponse?: EBaySearchResponse | null;
}

export function PricingModal({ 
  isOpen, 
  onClose, 
  witbItem,
  initialPriceSummary,
  initialSearchResponse
}: PricingModalProps) {
  const [searchResponse, setSearchResponse] = useState<EBaySearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCondition, setSelectedCondition] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'price-asc' | 'price-desc' | 'condition'>('price-asc');

  const fetchPricingData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await ebayApi.searchForWITBItem(
        witbItem.brand,
        witbItem.model,
        witbItem.category
      );
      setSearchResponse(response);
    } catch (err) {
      setError('Failed to load pricing data. Please try again.');
      console.error('Error fetching pricing data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      // Use initialSearchResponse if available, otherwise fetch
      if (initialSearchResponse) {
        setSearchResponse(initialSearchResponse);
        setError(null);
      } else if (!searchResponse) {
        fetchPricingData();
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, initialSearchResponse]);

  // Reset data when modal closes or witbItem changes
  useEffect(() => {
    if (!isOpen) {
      setSearchResponse(null);
      setError(null);
    }
  }, [isOpen, witbItem]);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const filteredAndSortedProducts = () => {
    if (!searchResponse) return [];
    
    let products = [...searchResponse.products];

    // Filter by condition
    if (selectedCondition !== 'all') {
      products = products.filter(p => 
        p.price_info.condition.toLowerCase().includes(selectedCondition.toLowerCase())
      );
    }

    // Sort products
    products.sort((a, b) => {
      switch (sortBy) {
        case 'price-asc':
          return a.price_info.current_price - b.price_info.current_price;
        case 'price-desc':
          return b.price_info.current_price - a.price_info.current_price;
        case 'condition':
          return a.price_info.condition.localeCompare(b.price_info.condition);
        default:
          return 0;
      }
    });

    return products;
  };

  const getPriceStats = () => {
    const products = filteredAndSortedProducts();
    if (products.length === 0) {
      // Use initial summary if available and no filtered products
      if (initialPriceSummary && initialPriceSummary.listingCount > 0) {
        return {
          min: initialPriceSummary.minPrice,
          max: initialPriceSummary.maxPrice,
          average: initialPriceSummary.averagePrice,
          count: initialPriceSummary.listingCount,
        };
      }
      return null;
    }

    const prices = products.map(p => p.price_info.current_price);
    return {
      min: Math.min(...prices),
      max: Math.max(...prices),
      average: Math.round(prices.reduce((sum, price) => sum + price, 0) / prices.length),
      count: products.length,
    };
  };

  const priceStats = getPriceStats();
  const products = filteredAndSortedProducts();

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[85vh] overflow-hidden flex flex-col">
        <DialogHeader className="flex-shrink-0 border-b border-gray-200 dark:border-gray-700 pb-4">
          <div>
            <DialogTitle className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Current Market Pricing
            </DialogTitle>
            <div className="space-y-2">
              <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300">
                {witbItem.brand} {witbItem.model}
              </h3>
              <div className="flex items-center gap-2">
                <Badge className="bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300">
                  {witbItem.category}
                </Badge>
                {witbItem.loft && (
                  <Badge variant="outline" className="text-xs">
                    {witbItem.loft} loft
                  </Badge>
                )}
                {witbItem.shaft && (
                  <Badge variant="outline" className="text-xs">
                    {witbItem.shaft} shaft
                  </Badge>
                )}
              </div>
            </div>
          </div>

          {/* Price Summary */}
          {priceStats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <TrendingUp className="h-4 w-4 text-emerald-600" />
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Lowest</span>
                </div>
                <span className="text-lg font-semibold text-emerald-600 dark:text-emerald-400">
                  {formatPrice(priceStats.min)}
                </span>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <TrendingUp className="h-4 w-4 text-blue-600" />
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Highest</span>
                </div>
                <span className="text-lg font-semibold text-blue-600 dark:text-blue-400">
                  {formatPrice(priceStats.max)}
                </span>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <TrendingUp className="h-4 w-4 text-purple-600" />
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Average</span>
                </div>
                <span className="text-lg font-semibold text-purple-600 dark:text-purple-400">
                  {formatPrice(priceStats.average)}
                </span>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Package className="h-4 w-4 text-gray-600" />
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Listings</span>
                </div>
                <span className="text-lg font-semibold text-gray-700 dark:text-gray-300">
                  {priceStats.count}
                </span>
              </div>
            </div>
          )}

          {/* Filters */}
          <div className="flex items-center gap-4 mt-4">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Filters:</span>
            </div>
            <Select value={selectedCondition} onValueChange={setSelectedCondition}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Condition" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Conditions</SelectItem>
                <SelectItem value="new">New</SelectItem>
                <SelectItem value="excellent">Excellent</SelectItem>
                <SelectItem value="good">Good</SelectItem>
                <SelectItem value="used">Used</SelectItem>
              </SelectContent>
            </Select>
            <Select value={sortBy} onValueChange={(value) => setSortBy(value as 'price-asc' | 'price-desc' | 'condition')}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="price-asc">Price: Low to High</SelectItem>
                <SelectItem value="price-desc">Price: High to Low</SelectItem>
                <SelectItem value="condition">Condition</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </DialogHeader>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(6)].map((_, i) => (
                <PricingSkeleton key={i} />
              ))}
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <div className="text-red-500 text-4xl mb-4">⚠️</div>
              <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
              <Button onClick={fetchPricingData} variant="outline">
                Try Again
              </Button>
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 text-4xl mb-4">🔍</div>
              <p className="text-gray-600 dark:text-gray-400 mb-2">
                No listings found for your current filters
              </p>
              <p className="text-sm text-gray-500">
                Try adjusting your condition filter or search criteria
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {products.map((product) => (
                <PriceCard key={product.product_id} product={product} />
              ))}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}