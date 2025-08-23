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
import { useAuth } from "@/providers/auth-provider";

export default function Home() {
  const [query, setQuery] = useState("");
  const { user } = useAuth();
  
  // Custom hooks for state management
  const { page, setPage } = usePagination();
  
  // Data fetching - only OGWR data
  const { playersResponse, players, error, isLoading } = usePlayersData(page, "OGWR");
  
  // Player search
  const filteredPlayers = usePlayerSearch(players, query);

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Header onSearch={setQuery} />
        
        <main className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Sign-in Banner for non-authenticated users */}
          {!user && (
            <div className="py-4">
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <p className="text-blue-800 dark:text-blue-200">
                  Sign in to save your favorite players and get personalized golf equipment recommendations!
                </p>
              </div>
            </div>
          )}
          
          {/* Tournament Winner Banner */}
          <div className="mb-6 pt-6">
            <ErrorBoundary>
              <TournamentWinnerWithBag isCollapsed={true} />
            </ErrorBoundary>
          </div>

          {/* Mobile-First Layout */}
          <div className="space-y-6 lg:space-y-0 lg:grid lg:grid-cols-12 lg:gap-8">
            {/* Main Content: Player Rankings */}
            <div className="lg:col-span-8 xl:col-span-9">
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

            {/* Sidebar: Club Leaderboard */}
            <div className="lg:col-span-4 xl:col-span-3">
              <div className="sticky top-24">
                <ErrorBoundary>
                  <ClubLeaderboard />
                </ErrorBoundary>
              </div>
            </div>
          </div>

          {/* Bottom Spacing */}
          <div className="h-8"></div>
        </main>
      </div>
    </ErrorBoundary>
  );
}
