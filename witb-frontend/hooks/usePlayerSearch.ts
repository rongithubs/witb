import { useMemo } from 'react';
import { Player } from '@/types/schemas';

export function usePlayerSearch(players: Player[], query: string, selectedTour: string) {
  return useMemo(() => {
    if (!players) return [];
    
    return players.filter((player) => {
      const matchesTour = selectedTour === "All Tours" || player.tour === selectedTour;
      
      if (!query.trim()) return matchesTour;
      
      const terms = query.toLowerCase().trim().split(/\s+/);
      const matches = terms.every((term) =>
        player.name.toLowerCase().includes(term) ||
        player.witb_items?.some((club) =>
          club.category.toLowerCase().includes(term) ||
          club.brand.toLowerCase().includes(term) ||
          club.model.toLowerCase().includes(term)
        )
      );
      
      return matchesTour && matches;
    });
  }, [players, query, selectedTour]);
}