import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ExternalLinkIcon } from "lucide-react";
import { isChampionItem, getRankBadgeVariant } from "@/lib/leaderboard-utils";
import type { ClubUsageItem } from "@/hooks/useLeaderboardData";

interface LeaderboardCardProps {
  item: ClubUsageItem & { category?: string };
  index: number;
}

export function LeaderboardCard({ 
  item, 
  index
}: LeaderboardCardProps) {
  const isChampion = isChampionItem(item);
  const rankVariant = getRankBadgeVariant(item.rank);
  
  const cardClassName = `
    bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors
    group transition-all duration-300
    ${isChampion ? 'overflow-hidden' : 'p-3'}
  `.trim();

  const spotlightStyle = isChampion ? {
    border: '1px solid rgba(255, 215, 0, 0.4)',
    borderRadius: '12px',
    boxShadow: '0 0 10px rgba(255, 215, 0, 0.3), 0 0 20px rgba(255, 215, 0, 0.2)',
    background: 'linear-gradient(145deg, rgba(255, 215, 0, 0.05), rgba(255, 215, 0, 0))',
  } : {};

  return (
    <div
      className={cardClassName}
      style={{
        animationDelay: `${index * 50}ms`,
        animation: "fadeInUp 0.6s ease-out forwards",
        ...spotlightStyle
      }}
    >
      {isChampion ? (
        <>
          {/* Featured #1 Design */}
          <div className="bg-gradient-to-r from-yellow-50 to-amber-50 dark:from-yellow-400/10 dark:to-amber-400/10 p-4 border-b border-yellow-200 dark:border-yellow-700/30">
            <div className="flex items-start gap-3 mb-2">
              <div className="bg-yellow-600 dark:bg-yellow-500 text-white text-lg font-bold rounded flex items-center justify-center w-12 h-12">
                #{item.rank}
              </div>
              <div className="text-sm font-medium text-yellow-700 dark:text-yellow-300 uppercase tracking-wide flex flex-col justify-center h-12">
                <div className="whitespace-nowrap">Most Played</div>
                <div className="whitespace-nowrap">{item.category}</div>
              </div>
            </div>
            
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {item.brand}
            </h3>
            <p className="text-lg font-semibold text-blue-600 dark:text-blue-400 mb-3">
              {item.model}
            </p>
            <p className="text-sm text-yellow-600 dark:text-gray-300">
              Trusted by {item.percentage}% of Tour Players
            </p>
          </div>
          <div className="p-4">
            {item.brand_url && (
              <Button
                variant="default"
                size="sm"
                className="w-full bg-gray-900 hover:bg-gray-800 text-white"
                onClick={() => window.open(item.brand_url, '_blank')}
              >
                <ExternalLinkIcon className="h-3 w-3 mr-2" />
                Shop Now
              </Button>
            )}
          </div>
        </>
      ) : (
        <>
          {/* Regular Card Design */}
          <div className="flex items-center gap-3 mb-3">
            <span className="font-bold text-xs px-2 py-1 rounded text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700">
              #{item.rank}
            </span>
            <div>
              <h3 className="font-bold text-lg leading-tight text-gray-900 dark:text-white">
                {item.brand}
              </h3>
              <p className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                {item.model}
              </p>
            </div>
          </div>
        </>
      )}

      {/* Usage Stats - Only for non-champion cards */}
      {!isChampion && (
        <>
          <div className="mb-3">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-gray-600 dark:text-white/70">Usage</span>
              <span className="text-gray-800 dark:text-white/90 font-semibold">
                {item.count} players ({item.percentage}%)
              </span>
            </div>
            
            {/* Usage bar */}
            <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 overflow-hidden">
              <div 
                className="bg-blue-600 dark:bg-blue-500 h-full rounded-full transition-all duration-300"
                style={{ width: `${Math.min(item.percentage, 100)}%` }}
              />
            </div>
          </div>

          {/* Brand URL Link */}
          {item.brand_url && (
            <Button
              variant="outline"
              size="sm"
              className="w-full"
              onClick={() => window.open(item.brand_url, '_blank')}
            >
              <ExternalLinkIcon className="h-3 w-3 mr-1" />
              View Brand
            </Button>
          )}
        </>
      )}
    </div>
  );
}