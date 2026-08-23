"use client";

interface PricingSkeletonProps {
  className?: string;
}

export function PricingSkeleton({ className = '' }: PricingSkeletonProps) {
  return (
    <div className={`
      bg-surface rounded-lg border border-hairline 
      p-4 animate-pulse ${className}
    `}>
      {/* Header with Image and Title */}
      <div className="flex gap-3 mb-3">
        {/* Image placeholder */}
        <div className="flex-shrink-0">
          <div className="w-16 h-16 bg-skeleton rounded-lg" />
        </div>
        <div className="flex-1 min-w-0">
          {/* Title placeholder */}
          <div className="h-4 bg-skeleton rounded-md mb-2" />
          <div className="h-4 bg-skeleton rounded-md w-3/4 mb-2" />
          {/* Badges placeholder */}
          <div className="flex items-center gap-2">
            <div className="h-5 w-16 bg-skeleton rounded-md" />
            <div className="h-5 w-20 bg-skeleton rounded-md" />
          </div>
        </div>
      </div>

      {/* Price Section */}
      <div className="mb-3">
        <div className="flex items-baseline justify-between mb-2">
          <div className="h-8 w-24 bg-skeleton rounded-md" />
          <div className="h-4 w-16 bg-skeleton rounded-md" />
        </div>
        <div className="flex items-center gap-1">
          <div className="h-3 w-3 bg-skeleton rounded-md" />
          <div className="h-4 w-20 bg-skeleton rounded-md" />
        </div>
      </div>

      {/* Seller Info */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-1">
          <div className="h-4 w-16 bg-skeleton rounded-md" />
          <div className="h-3 w-3 bg-skeleton rounded-md" />
          <div className="h-4 w-12 bg-skeleton rounded-md" />
        </div>
        <div className="flex items-center gap-1">
          <div className="h-3 w-3 bg-skeleton rounded-md" />
          <div className="h-4 w-8 bg-skeleton rounded-md" />
        </div>
      </div>

      {/* Action Button */}
      <div className="h-8 bg-skeleton rounded-md" />
    </div>
  );
}