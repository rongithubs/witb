import { useState, useCallback } from 'react';
import { Player } from '@/types/schemas';

export function usePlayerSelection() {
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);

  const handlePlayerSelect = useCallback((player: Player) => {
    setSelectedPlayer(player);
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedPlayer(null);
  }, []);

  return {
    selectedPlayer,
    handlePlayerSelect,
    clearSelection,
    setSelectedPlayer
  };
}