import type { LeaderboardData } from "@/hooks/useLeaderboardData";

interface LeaderboardFooterProps {
  leaderboardData?: LeaderboardData;
}

export function LeaderboardFooter({ leaderboardData }: LeaderboardFooterProps) {
  if (!leaderboardData) return null;

  return (
    <div className="mt-8 pt-4 border-t border-gray-300/50 dark:border-white/10">
      <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-gray-500 dark:text-white/60">
        <span>{leaderboardData.total_categories} categories analyzed</span>
        <span>{leaderboardData.total_unique_combinations} unique combinations</span>
        <span>Data from professional tours</span>
      </div>
    </div>
  );
}