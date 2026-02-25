import useSWR from "swr";
import { fetcher } from "@/lib/api";

interface BrandResponse {
  brands: string[];
  total: number;
}

export function useBrands() {
  const { data, error, isLoading } = useSWR<BrandResponse>(
    "/witb/brands",
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      dedupingInterval: 3600000, // Cache for 1 hour (brands don't change often)
    },
  );

  return {
    brands: data?.brands || [],
    total: data?.total || 0,
    error,
    isLoading,
  };
}
