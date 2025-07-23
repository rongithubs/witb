"use client";

import Header from "@/components/ui/Header";
import TournamentWinnerWithBag from "@/components/TournamentWinnerWithBag";
import { Player } from "@/types/schemas";
import { useState } from "react";
import { PlayerList } from "@/components/PlayerList";
import { PlayerDetails } from "@/components/PlayerDetails";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { usePlayerSelection } from "@/hooks/usePlayerSelection";
import { usePlayerSearch } from "@/hooks/usePlayerSearch";
import { usePagination } from "@/hooks/usePagination";
import { useMobileMenu } from "@/hooks/useMobileMenu";
import { useTourFilter } from "@/hooks/useTourFilter";
import { usePlayersData } from "@/hooks/usePlayersData";

export default function Home() {
  const [query, setQuery] = useState("");
  
  // Custom hooks for state management
  const { page, setPage } = usePagination();
  const { selectedPlayer, handlePlayerSelect, clearSelection } = usePlayerSelection();
  const { isMobileMenuOpen, toggleMobileMenu, closeMobileMenu } = useMobileMenu();
  
  // Data fetching
  const { playersResponse, players, error, isLoading } = usePlayersData(page);
  
  // Tour filtering
  const { selectedTour, availableTours, handleTourFilter } = useTourFilter(players);
  
  // Player search and filtering
  const filteredPlayers = usePlayerSearch(players, query, selectedTour);
  
  // Handle tour filter change
  const handleTourChange = (tour: string) => {
    handleTourFilter(tour);
    clearSelection();
  };
  
  // Handle player selection
  const handlePlayerClick = (player: Player) => {
    handlePlayerSelect(player);
    closeMobileMenu();
  };

  return (
    <ErrorBoundary>
      <div className="max-w-7xl mx-auto px-4">
        <Header 
          onSearch={setQuery} 
          isMobileMenuOpen={isMobileMenuOpen}
          onToggleMobileMenu={toggleMobileMenu}
        />
        
        <div className="my-6">
          <ErrorBoundary>
            <TournamentWinnerWithBag />
          </ErrorBoundary>
        </div>

        <div className="grid grid-cols-12 gap-4 py-4">
          <ErrorBoundary>
            <PlayerList
              players={filteredPlayers}
              selectedPlayer={selectedPlayer}
              onPlayerSelect={handlePlayerClick}
              isLoading={isLoading}
              error={error}
              playersResponse={playersResponse}
              selectedTour={selectedTour}
              availableTours={availableTours}
              onTourChange={handleTourChange}
              isMobileMenuOpen={isMobileMenuOpen}
              onCloseMobileMenu={closeMobileMenu}
              page={page}
              onPageChange={setPage}
            />
          </ErrorBoundary>
          
          <div className={`col-span-12 md:col-span-8 lg:col-span-9 ${
            isMobileMenuOpen ? 'md:block hidden' : ''
          }`}>
            <ErrorBoundary>
              <PlayerDetails
                selectedPlayer={selectedPlayer}
                isLoading={isLoading}
              />
            </ErrorBoundary>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
