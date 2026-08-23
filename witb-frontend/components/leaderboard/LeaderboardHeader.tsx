import { TrophyIcon } from "lucide-react";

interface LeaderboardHeaderProps {
  leaderboardData?: any; // Not used anymore but keeping interface for compatibility
}

export function LeaderboardHeader({ leaderboardData }: LeaderboardHeaderProps) {
  return (
    <div className="flex items-center gap-3 mb-6">
      <div className="bg-surface-subtle p-2 rounded-lg">
        <TrophyIcon className="h-5 w-5 text-ink" />
      </div>
      <h2 className="text-xl font-bold text-ink">
        Club Usage Leaderboard
      </h2>
    </div>
  );
}