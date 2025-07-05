import { useState, useCallback, useMemo } from 'react';
import { Player } from '@/types/schemas';

export function useTourFilter(players: Player[]) {
  const [selectedTour, setSelectedTour] = useState<string>("All Tours");

  const availableTours = useMemo(() => {
    if (!players) return ["All Tours"];
    return ["All Tours", ...Array.from(new Set(players.map((p) => p.tour))).sort()];
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
    resetTour
  };
}