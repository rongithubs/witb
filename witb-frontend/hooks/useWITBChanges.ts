import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import type { BagChangesResponse } from "@/types/schemas";

export function useWITBChanges(limit: number = 50) {
  const {
    data: changesResponse,
    error,
    isLoading,
    mutate,
  } = useSWR<BagChangesResponse>(`/witb/changes?limit=${limit}`, fetcher);

  return {
    changesResponse,
    changes: changesResponse?.changes ?? [],
    error,
    isLoading,
    isEmpty: !changesResponse?.changes?.length && !isLoading,
    refetch: mutate,
  };
}
