import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";

export interface ClubUsageItem {
  brand: string;
  model: string;
  count: number;
  percentage: number;
  rank: number;
  brand_url?: string;
}

export interface LeaderboardData {
  categories: Record<string, ClubUsageItem[]>;
  total_categories: number;
  total_unique_combinations: number;
}

export function useLeaderboardData(limit: number = 3) {
  const {
    data: leaderboardData,
    error,
    isLoading,
    mutate,
  } = useSWR<LeaderboardData>(
    `/witb/leaderboard?limit=${limit}`,
    fetcher,
  );

  return {
    leaderboardData,
    error,
    isLoading,
    isEmpty: !leaderboardData?.categories && !isLoading,
    refetch: mutate,
  };
}