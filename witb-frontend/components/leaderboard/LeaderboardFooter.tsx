import type { LeaderboardData } from "@/hooks/useLeaderboardData";

interface LeaderboardFooterProps {
  leaderboardData?: LeaderboardData;
}

export function LeaderboardFooter({ leaderboardData }: LeaderboardFooterProps) {
  if (!leaderboardData) return null;

  return (
    <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div className="text-center text-sm text-gray-500 dark:text-gray-400">
        Data from professional tours
      </div>
    </div>
  );
}