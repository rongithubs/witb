"use client";

import Header from "@/components/ui/Header";
import TournamentWinnerWithBag from "@/components/TournamentWinnerWithBag";
import { useState } from "react";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { usePlayerSearch } from "@/hooks/usePlayerSearch";
import { usePagination } from "@/hooks/usePagination";
import { usePlayersData } from "@/hooks/usePlayersData";
import { PlayerTable } from "@/components/PlayerTable";

export default function Home() {
  const [query, setQuery] = useState("");
  const [isWitbExpanded, setIsWitbExpanded] = useState(false);
  
  // Custom hooks for state management
  const { page, setPage } = usePagination();
  
  // Data fetching - only OGWR data
  const { playersResponse, players, error, isLoading } = usePlayersData(page, "OGWR");
  
  // Player search
  const filteredPlayers = usePlayerSearch(players, query);

  return (
    <ErrorBoundary>
      <div className="max-w-7xl mx-auto px-4">
        <Header 
          onSearch={setQuery} 
        />
        
        <div className={`transition-all duration-500 ease-in-out ${
          isWitbExpanded ? 'my-2' : 'my-6'
        }`}>
          <ErrorBoundary>
            <TournamentWinnerWithBag isCollapsed={isWitbExpanded} />
          </ErrorBoundary>
        </div>

        <div className="py-4">
          <ErrorBoundary>
            <PlayerTable
              players={filteredPlayers}
              isLoading={isLoading}
              error={error}
              playersResponse={playersResponse}
              page={page}
              onPageChange={setPage}
              onWitbExpansionChange={setIsWitbExpanded}
            />
          </ErrorBoundary>
        </div>
      </div>
    </ErrorBoundary>
  );
}
