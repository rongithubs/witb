"use client";

import Header from "@/components/ui/Header";
import TournamentWinnerWithBag from "@/components/TournamentWinnerWithBag";
import { ClubLeaderboard } from "@/components/ClubLeaderboard";
import { useState } from "react";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { usePlayerSearch } from "@/hooks/usePlayerSearch";
import { usePagination } from "@/hooks/usePagination";
import { usePlayersData } from "@/hooks/usePlayersData";
import { PlayerTable } from "@/components/PlayerTable";

export default function Home() {
  const [query, setQuery] = useState("");
  
  // Custom hooks for state management
  const { page, setPage } = usePagination();
  
  // Data fetching - only OGWR data
  const { playersResponse, players, error, isLoading } = usePlayersData(page, "OGWR");
  
  // Player search
  const filteredPlayers = usePlayerSearch(players, query);

  return (
    <ErrorBoundary>
      <div className="max-w-screen-2xl mx-auto px-6">
        <Header 
          onSearch={setQuery} 
        />
        
        <div className="my-4">
          <ErrorBoundary>
            <TournamentWinnerWithBag isCollapsed={true} />
          </ErrorBoundary>
        </div>

        {/* Side-by-side layout: OGWR Rankings (70%) and Club Leaderboard (30%) */}
        <div className="py-6">
          <div className="grid grid-cols-1 lg:grid-cols-10 gap-6">
            {/* OGWR Rankings - Left Column (70%) */}
            <div className="lg:col-span-7">
              <ErrorBoundary>
                <PlayerTable
                  players={filteredPlayers}
                  isLoading={isLoading}
                  error={error}
                  playersResponse={playersResponse}
                  page={page}
                  onPageChange={setPage}
                />
              </ErrorBoundary>
            </div>

            {/* Club Usage Leaderboard - Right Column (30%) */}
            <div className="lg:col-span-3">
              <ErrorBoundary>
                <ClubLeaderboard />
              </ErrorBoundary>
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
