"use client";

import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ExternalLink, Star, MapPin, Truck } from 'lucide-react';
import { EBayProduct } from '@/types/schemas';

interface PriceCardProps {
  product: EBayProduct;
  className?: string;
}

export function PriceCard({ product, className = '' }: PriceCardProps) {
  const handleViewListing = () => {
    window.open(product.listing_url, '_blank', 'noopener,noreferrer');
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const getConditionColor = (condition: string) => {
    const conditionLower = condition.toLowerCase();
    if (conditionLower.includes('new')) return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
    if (conditionLower.includes('excellent') || conditionLower.includes('like new')) return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
    if (conditionLower.includes('good') || conditionLower.includes('very good')) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
    return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
  };

  const formatFeedbackPercentage = (percentage?: number) => {
    if (!percentage) return null;
    return `${percentage}%`;
  };

  return (
    <div className={`
      bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 
      p-4 hover:shadow-lg transition-all duration-300 hover:border-emerald-200 dark:hover:border-emerald-800
      ${className}
    `}>
      {/* Header with Image and Title */}
      <div className="flex gap-3 mb-3">
        {product.image_url && (
          <div className="flex-shrink-0">
            <img 
              src={product.image_url} 
              alt={product.title}
              className="w-16 h-16 object-cover rounded-lg border border-gray-200 dark:border-gray-600"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
              }}
            />
          </div>
        )}
        <div className="flex-1 min-w-0 overflow-hidden">
          <h3 className="font-medium text-gray-900 dark:text-white text-sm mb-1 overflow-hidden">
            <div 
              className="leading-tight"
              style={{
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}
            >
              {product.title}
            </div>
          </h3>
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <Badge className={`text-xs px-2 py-0.5 flex-shrink-0 ${getConditionColor(product.price_info.condition)}`}>
              {product.price_info.condition}
            </Badge>
            <Badge variant="outline" className="text-xs px-2 py-0.5 flex-shrink-0">
              {product.listing_type}
            </Badge>
          </div>
        </div>
      </div>

      {/* Price Section */}
      <div className="mb-3">
        <div className="flex items-baseline justify-between">
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
              {formatPrice(product.price_info.current_price)}
            </span>
            {product.price_info.currency !== 'USD' && (
              <span className="text-sm text-gray-500">{product.price_info.currency}</span>
            )}
          </div>
          {product.price_info.buy_it_now_price && 
           product.price_info.buy_it_now_price !== product.price_info.current_price && (
            <span className="text-sm text-gray-500 line-through">
              {formatPrice(product.price_info.buy_it_now_price)}
            </span>
          )}
        </div>
        
        {product.price_info.shipping_cost && product.price_info.shipping_cost > 0 && (
          <div className="flex items-center gap-1 mt-1">
            <Truck className="h-3 w-3 text-gray-400" />
            <span className="text-sm text-gray-500">
              +{formatPrice(product.price_info.shipping_cost)} shipping
            </span>
          </div>
        )}

        {product.price_info.shipping_cost === 0 && (
          <div className="flex items-center gap-1 mt-1">
            <Truck className="h-3 w-3 text-green-500" />
            <span className="text-sm text-green-600 dark:text-green-400 font-medium">
              Free shipping
            </span>
          </div>
        )}
      </div>

      {/* Seller Info */}
      {product.seller_info && (
        <div className="flex items-center justify-between mb-3 text-sm text-gray-600 dark:text-gray-400 min-w-0">
          <div className="flex items-center gap-1 min-w-0 flex-1">
            <span className="font-medium truncate max-w-24">{product.seller_info.username}</span>
            {product.seller_info.feedback_percentage && (
              <div className="flex items-center gap-0.5 flex-shrink-0">
                <Star className="h-3 w-3 text-yellow-400 fill-current" />
                <span>{formatFeedbackPercentage(product.seller_info.feedback_percentage)}</span>
                {product.seller_info.feedback_score && (
                  <span className="text-gray-400 hidden sm:inline">
                    ({product.seller_info.feedback_score.toLocaleString()})
                  </span>
                )}
              </div>
            )}
          </div>
          {product.location && (
            <div className="flex items-center gap-1 flex-shrink-0">
              <MapPin className="h-3 w-3" />
              <span className="text-xs">{product.location}</span>
            </div>
          )}
        </div>
      )}

      {/* Action Button */}
      <Button
        onClick={handleViewListing}
        className="w-full bg-emerald-600 hover:bg-emerald-700 text-white"
        size="sm"
      >
        <ExternalLink className="h-3 w-3 mr-1.5" />
        View on eBay
      </Button>
    </div>
  );
}