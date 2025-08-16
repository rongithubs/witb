import { TrophyIcon } from "lucide-react";

interface LeaderboardHeaderProps {
  leaderboardData?: any; // Not used anymore but keeping interface for compatibility
}

export function LeaderboardHeader({ leaderboardData }: LeaderboardHeaderProps) {
  return (
    <div className="flex items-center gap-3 mb-6">
      <div className="bg-gray-100 dark:bg-gray-700 p-2 rounded-lg">
        <TrophyIcon className="h-5 w-5 text-yellow-500 dark:text-yellow-400" />
      </div>
      <h2 className="text-xl font-bold text-gray-800 dark:text-white">
        Club Usage Leaderboard
      </h2>
    </div>
  );
}