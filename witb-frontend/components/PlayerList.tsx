"use client";

import { memo } from 'react';
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Player, PaginatedPlayersResponse } from "@/types/schemas";
import { PlayerListSkeleton } from "@/components/skeletons";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { playerListClasses } from "@/lib/utils";

interface PlayerListProps {
  players: Player[];
  selectedPlayer: Player | null;
  onPlayerSelect: (player: Player) => void;
  isLoading: boolean;
  error: Error | null;
  playersResponse?: PaginatedPlayersResponse;
  isMobileMenuOpen: boolean;
  onCloseMobileMenu: () => void;
  page: number;
  onPageChange: (page: number) => void;
}

export const PlayerList = memo(function PlayerList({
  players,
  selectedPlayer,
  onPlayerSelect,
  isLoading,
  error,
  playersResponse,
  isMobileMenuOpen,
  onCloseMobileMenu,
  page,
  onPageChange
}: PlayerListProps) {
  const handlePlayerClick = (player: Player) => {
    onPlayerSelect(player);
    onCloseMobileMenu();
  };

  return (
    <div className={playerListClasses(isMobileMenuOpen)}>
      <div className="bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 md:border md:rounded-lg shadow-2xl md:shadow-sm h-full md:h-[80vh] flex flex-col">
        {/* OGWR Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
          <div className="text-center">
            <Badge className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-base px-4 py-2">
              Official World Golf Ranking
            </Badge>
            <p className="text-sm text-gray-600 dark:text-gray-300 mt-2">
             TOP {playersResponse?.total || players.length} players • Page {playersResponse?.page || page} of {playersResponse?.total_pages || 1}
            </p>
          </div>
        </div>

        <ScrollArea className="flex-1 overflow-hidden">
          <div className="relative">
            {isLoading && playersResponse && (
              <div className="absolute inset-0 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm z-10 flex items-center justify-center">
                <LoadingSpinner size="md" />
              </div>
            )}
            {isLoading && !playersResponse ? (
              <PlayerListSkeleton />
            ) : error ? (
              <div className="p-4 text-center">
                <p className="text-red-500 dark:text-red-400">Failed to load players.</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Please try again later</p>
              </div>
            ) : (
              <div className="p-2 space-y-1">
                {players.map((player) => (
                  <div
                    key={player.id}
                    onClick={() => handlePlayerClick(player)}
                    className={`p-3 rounded-md cursor-pointer transition-colors hover:bg-blue-50 dark:hover:bg-gray-700 ${
                      selectedPlayer?.id === player.id ? "bg-blue-100 dark:bg-blue-900 border border-blue-200 dark:border-blue-700" : "hover:shadow-sm"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center text-xs font-medium text-gray-700 dark:text-gray-200">
                        {player.name.split(" ").map((n) => n[0]).join("")}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between">
                          <h3 className="text-sm font-medium truncate text-gray-900 dark:text-white">{player.name}</h3>
                          {player.ranking && (
                            <Badge className="text-xs px-2 py-0.5 bg-gradient-to-r from-blue-500 to-indigo-500 text-white">
                              #{player.ranking}
                            </Badge>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{player.country}</p>
                        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">{player.witb_items.length} clubs</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </ScrollArea>
        
        {/* Pagination Controls */}
        {playersResponse && playersResponse.total_pages > 1 && (
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex justify-between items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange(page - 1)}
                disabled={page <= 1 || isLoading}
                className="disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? "..." : "Previous"}
              </Button>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {isLoading ? "Loading..." : `${page} / ${playersResponse.total_pages}`}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange(page + 1)}
                disabled={page >= playersResponse.total_pages || isLoading}
                className="disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? "..." : "Next"}
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});