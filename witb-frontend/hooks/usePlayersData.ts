import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import { PaginatedPlayersResponse } from "@/types/schemas";

export function usePlayersData(page: number = 1, tour?: string) {
  const tourParam = tour && tour !== "All Tours" ? `&tour=${encodeURIComponent(tour)}` : "";
  
  const {
    data: playersResponse,
    error,
    isLoading,
    mutate,
  } = useSWR<PaginatedPlayersResponse>(
    `/players?page=${page}&per_page=20${tourParam}`,
    fetcher,
  );

  return {
    playersResponse,
    players: playersResponse?.items || [],
    error,
    isLoading,
    isEmpty: !playersResponse?.items?.length && !isLoading,
    refetch: mutate,
  };
}
