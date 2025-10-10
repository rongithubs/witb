"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { ExternalLink, Loader2 } from 'lucide-react';
import { WITBItem } from '@/types/schemas';
import { useEBayPricing } from '@/hooks/useEBayPricing';
import { PricingModal } from './PricingModal';

interface PriceButtonProps {
  witbItem: WITBItem;
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'default' | 'sm' | 'lg';
  className?: string;
}

export function PriceButton({ 
  witbItem, 
  variant = 'outline', 
  size = 'sm',
  className = ''
}: PriceButtonProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { priceSummary, searchResponse, isLoading, hasError, fetchPriceData } = useEBayPricing(witbItem);

  const handlePriceCheck = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Fetch data if we don't have it yet or if there was an error
    if (!priceSummary && !isLoading || hasError && !isLoading) {
      await fetchPriceData();
    }
    
    setIsModalOpen(true);
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(price);
  };

  const formatPriceRange = () => {
    if (hasError) {
      return 'Error';
    }
    
    if (!priceSummary) {
      return 'Check Price';
    }
    
    if (priceSummary.listingCount === 0) {
      return 'No Data';
    }

    if (priceSummary.minPrice === priceSummary.maxPrice) {
      return formatPrice(priceSummary.minPrice);
    }

    return `${formatPrice(priceSummary.minPrice)} - ${formatPrice(priceSummary.maxPrice)}`;
  };

  return (
    <>
      <Button
        onClick={handlePriceCheck}
        variant={variant}
        size={size}
        disabled={isLoading}
        className={`
          transition-all duration-200 
          hover:scale-105 hover:shadow-sm
          ${hasError ? 'border-red-200 hover:border-red-300 hover:bg-red-50 dark:border-red-800 dark:hover:bg-red-900/20 text-red-700 dark:text-red-300' : 
            variant === 'outline' ? 'border-emerald-200 hover:border-emerald-300 hover:bg-emerald-50 dark:border-emerald-800 dark:hover:bg-emerald-900/20' : ''}
          ${className}
        `}
        title={hasError ? `Error loading prices - click to retry` : `Check current eBay prices for ${witbItem.brand} ${witbItem.model}`}
      >
        <div className="flex items-center gap-1.5">
          {isLoading && (
            <Loader2 className={`${size === 'sm' ? 'h-3 w-3' : 'h-4 w-4'} animate-spin ${hasError ? 'text-red-600 dark:text-red-400' : 'text-emerald-600 dark:text-emerald-400'}`} />
          )}
          <span className={`${size === 'sm' ? 'text-xs' : 'text-sm'} font-medium`}>
            {isLoading ? 'Loading...' : formatPriceRange()}
          </span>
          {!isLoading && (
            <ExternalLink className={`${size === 'sm' ? 'h-2.5 w-2.5' : 'h-3 w-3'} text-gray-400`} />
          )}
        </div>
      </Button>

      <PricingModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        witbItem={witbItem}
        initialPriceSummary={priceSummary}
        initialSearchResponse={searchResponse}
      />
    </>
  );
}