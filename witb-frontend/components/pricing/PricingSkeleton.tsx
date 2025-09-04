"use client";

interface PricingSkeletonProps {
  className?: string;
}

export function PricingSkeleton({ className = '' }: PricingSkeletonProps) {
  return (
    <div className={`
      bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 
      p-4 animate-pulse ${className}
    `}>
      {/* Header with Image and Title */}
      <div className="flex gap-3 mb-3">
        {/* Image placeholder */}
        <div className="flex-shrink-0">
          <div className="w-16 h-16 bg-gray-200 dark:bg-gray-700 rounded-lg" />
        </div>
        <div className="flex-1 min-w-0">
          {/* Title placeholder */}
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2" />
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2" />
          {/* Badges placeholder */}
          <div className="flex items-center gap-2">
            <div className="h-5 w-16 bg-gray-200 dark:bg-gray-700 rounded" />
            <div className="h-5 w-20 bg-gray-200 dark:bg-gray-700 rounded" />
          </div>
        </div>
      </div>

      {/* Price Section */}
      <div className="mb-3">
        <div className="flex items-baseline justify-between mb-2">
          <div className="h-8 w-24 bg-gray-200 dark:bg-gray-700 rounded" />
          <div className="h-4 w-16 bg-gray-200 dark:bg-gray-700 rounded" />
        </div>
        <div className="flex items-center gap-1">
          <div className="h-3 w-3 bg-gray-200 dark:bg-gray-700 rounded" />
          <div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded" />
        </div>
      </div>

      {/* Seller Info */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-1">
          <div className="h-4 w-16 bg-gray-200 dark:bg-gray-700 rounded" />
          <div className="h-3 w-3 bg-gray-200 dark:bg-gray-700 rounded" />
          <div className="h-4 w-12 bg-gray-200 dark:bg-gray-700 rounded" />
        </div>
        <div className="flex items-center gap-1">
          <div className="h-3 w-3 bg-gray-200 dark:bg-gray-700 rounded" />
          <div className="h-4 w-8 bg-gray-200 dark:bg-gray-700 rounded" />
        </div>
      </div>

      {/* Action Button */}
      <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded" />
    </div>
  );
}