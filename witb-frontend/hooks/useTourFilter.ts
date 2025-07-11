import { useState, useCallback, useMemo } from "react";
import { Player } from "@/types/schemas";

export function useTourFilter(players: Player[]) {
  const [selectedTour, setSelectedTour] = useState<string>("All Tours");

  const availableTours = useMemo(() => {
    if (!players) return ["All Tours"];

    const uniqueTours = Array.from(new Set(players.map((p) => p.tour)));
    const orderedTours = ["All Tours"];

    // Add tours in specific order: PGA first, then LPGA, then others
    if (uniqueTours.includes("PGA Tour")) {
      orderedTours.push("PGA Tour");
    }
    if (uniqueTours.includes("LPGA")) {
      orderedTours.push("LPGA");
    }

    // Add any other tours alphabetically
    const otherTours = uniqueTours
      .filter((tour) => tour !== "PGA Tour" && tour !== "LPGA")
      .sort();
    orderedTours.push(...otherTours);

    return orderedTours;
  }, [players]);

  const handleTourFilter = useCallback((tour: string) => {
    setSelectedTour(tour);
  }, []);

  const resetTour = useCallback(() => {
    setSelectedTour("All Tours");
  }, []);

  return {
    selectedTour,
    availableTours,
    handleTourFilter,
    resetTour,
  };
}
