import type { LeaderboardData } from "@/hooks/useLeaderboardData";

interface LeaderboardFooterProps {
  leaderboardData?: LeaderboardData;
}

export function LeaderboardFooter({ leaderboardData }: LeaderboardFooterProps) {
  if (!leaderboardData) return null;

  return (
    <div className="mt-6 pt-4 border-t border-hairline">
      <div className="text-center text-sm text-ink-muted">
        Data from professional tours
      </div>
    </div>
  );
}