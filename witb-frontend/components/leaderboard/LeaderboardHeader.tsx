import { Badge } from "@/components/ui/badge";
import { TrophyIcon } from "lucide-react";
import type { LeaderboardData } from "@/hooks/useLeaderboardData";
import styles from "@/components/ui/glassmorphism.module.css";

interface LeaderboardHeaderProps {
  leaderboardData?: LeaderboardData;
}

export function LeaderboardHeader({ leaderboardData }: LeaderboardHeaderProps) {
  return (
    <div className="flex items-center gap-3 mb-6">
      <div className={styles.glassIcon}>
        <TrophyIcon className="h-6 w-6 text-yellow-400" />
      </div>
      <h2 className="text-2xl font-bold text-gray-800 dark:text-white/90">
        Club Usage Leaderboard
      </h2>
      <Badge className={styles.glassBadge}>
        {leaderboardData?.total_categories} categories
      </Badge>
    </div>
  );
}