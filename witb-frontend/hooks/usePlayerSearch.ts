import { useMemo } from 'react';
import { Player } from '@/types/schemas';

export function usePlayerSearch(players: Player[], query: string) {
  return useMemo(() => {
    if (!players) return [];
    
    if (!query.trim()) return players;
    
    const terms = query.toLowerCase().trim().split(/\s+/);
    
    return players.filter((player) => {
      return terms.every((term) =>
        player.name.toLowerCase().includes(term) ||
        player.witb_items?.some((club) =>
          club.category.toLowerCase().includes(term) ||
          club.brand.toLowerCase().includes(term) ||
          club.model.toLowerCase().includes(term)
        )
      );
    });
  }, [players, query]);
}