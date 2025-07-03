"use client";

import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import { useState } from "react";
import { Player, PaginatedPlayersResponse } from "@/types/schemas";
import { TournamentWinnerSkeleton } from "@/components/skeletons";

type TournamentWinner = {
  winner: string;
  tournament: string;
  date: string;
  score: string;
};

export default function TournamentWinner() {
  const [isExpanded, setIsExpanded] = useState(false);
  const { data: winnerData, error, isLoading } = useSWR<TournamentWinner>(
    "/tournament-winner",
    fetcher
  );

  // Fetch all players to find the winner's equipment
  const { data: playersResponse } = useSWR<PaginatedPlayersResponse>(
    "/players?per_page=100",
    fetcher
  );

  // Find the winner's player data
  const winnerPlayer = playersResponse?.items?.find(player => 
    player.name.toLowerCase() === winnerData?.winner.toLowerCase()
  );

  if (isLoading) {
    return <TournamentWinnerSkeleton />;
  }

  if (error || !winnerData) {
    return null; // Don't show anything if there's an error
  }

  return (
    <div className="bg-green-50 dark:bg-green-900/20 border-l-4 border-green-400 dark:border-green-500 p-4 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-green-400 dark:text-green-500" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-green-800 dark:text-green-200">
              Latest Tournament Winner
            </h3>
            <div className="mt-1 text-sm text-green-700 dark:text-green-300">
              <span className="font-semibold">{winnerData.winner}</span> won{" "}
              <span className="font-medium">{winnerData.tournament}</span>
              {winnerData.score && (
                <span className="ml-1">
                  at <span className="font-medium">{winnerData.score}</span>
                </span>
              )}
              {winnerData.date && (
                <span className="ml-2 text-green-600 dark:text-green-400">• {winnerData.date}</span>
              )}
            </div>
          </div>
        </div>
        
        {winnerPlayer && winnerPlayer.witb_items.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-green-700 dark:text-green-300">See what&apos;s in their bag</span>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="w-8 h-8 rounded-full bg-green-100 dark:bg-green-800 hover:bg-green-200 dark:hover:bg-green-700 flex items-center justify-center transition-colors"
            >
              <svg 
                className={`w-4 h-4 text-green-600 dark:text-green-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        )}
      </div>
      
      {isExpanded && winnerPlayer && (
        <div className="mt-4 pt-4 border-t border-green-200 dark:border-green-700">
          <h4 className="text-sm font-medium text-green-800 dark:text-green-200 mb-3">What&apos;s In The Bag</h4>
          <div className="space-y-2">
            {winnerPlayer.witb_items.length === 0 ? (
              <p className="text-green-600 dark:text-green-400 italic text-xs">No equipment data available</p>
            ) : (
              winnerPlayer.witb_items.map((club, index) => (
                <div key={index} className="border border-green-200 dark:border-green-700 p-3 rounded bg-green-25 dark:bg-green-900/30">
                  <div className="font-medium text-green-800 dark:text-green-200 text-sm">{club.category}</div>
                  <div className="text-green-700 dark:text-green-300 text-sm">{club.brand} {club.model}</div>
                  {club.loft && <div className="text-green-600 dark:text-green-400 text-xs">Loft: {club.loft}</div>}
                  {club.shaft && <div className="text-green-600 dark:text-green-400 text-xs">Shaft: {club.shaft}</div>}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}