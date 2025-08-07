import { useMemo } from "react";
import { Player } from "@/types/schemas";

export function useTourFilter(players: Player[]) {
  const availableTours = useMemo(() => {
    // For now, hard-code the tours since we know what's available
    // This ensures they show up even when filtering by a specific tour
    return ["All Tours", "OGWR", "PGA Tour", "LPGA"];
  }, [players]);

  return {
    availableTours,
  };
}
