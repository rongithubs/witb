import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ExternalLinkIcon } from "lucide-react";
import { isChampionItem, getRankBadgeVariant } from "@/lib/leaderboard-utils";
import type { ClubUsageItem } from "@/hooks/useLeaderboardData";
import styles from "@/components/ui/glassmorphism.module.css";

interface LeaderboardCardProps {
  item: ClubUsageItem & { category?: string };
  index: number;
  showCategory?: boolean;
}

export function LeaderboardCard({ 
  item, 
  index, 
  showCategory = false 
}: LeaderboardCardProps) {
  const isChampion = isChampionItem(item);
  const rankVariant = getRankBadgeVariant(item.rank);
  
  const cardClassName = `
    ${styles.glassCard} 
    ${isChampion ? styles.glassCardChampion : ''} 
    group transition-all duration-300
  `.trim();

  return (
    <div
      className={cardClassName}
      style={{
        animationDelay: `${index * 50}ms`,
        animation: "fadeInUp 0.6s ease-out forwards"
      }}
    >
      {/* Rank badge */}
      <div className="flex items-center justify-between mb-3">
        <div className={`${styles.rankBadge} ${styles[rankVariant]}`}>
          #{item.rank}
        </div>
        {showCategory && item.category && (
          <Badge variant="secondary" className={styles.glassCategoryBadge}>
            {item.category}
          </Badge>
        )}
      </div>

      {/* Brand & Model */}
      <div className="mb-4">
        <h3 className="font-bold text-gray-800 dark:text-white/90 text-lg leading-tight mb-1">
          {item.brand}
        </h3>
        <p className="text-blue-600 dark:text-blue-200/80 text-sm font-medium">
          {item.model}
        </p>
      </div>

      {/* Usage Stats */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-gray-600 dark:text-white/70">Usage</span>
          <span className="text-gray-800 dark:text-white/90 font-semibold">
            {item.count} players ({item.percentage}%)
          </span>
        </div>
        
        {/* Usage bar */}
        <div className={styles.glassProgressBg}>
          <div 
            className={styles.glassProgressFill}
            style={{ width: `${Math.min(item.percentage, 100)}%` }}
          />
        </div>
      </div>

      {/* Brand URL Link */}
      {item.brand_url && (
        <Button
          variant="ghost"
          size="sm"
          className={styles.glassButton + " w-full"}
          onClick={() => window.open(item.brand_url, '_blank')}
        >
          <ExternalLinkIcon className="h-3 w-3 mr-1" />
          View Brand
        </Button>
      )}
    </div>
  );
}