"use client";

import { memo } from 'react';
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { X } from "lucide-react";

interface PlayerFiltersProps {
  selectedTour: string;
  availableTours: string[];
  onTourChange: (tour: string) => void;
  playerCount: number;
  totalPlayers?: number;
  currentPage?: number;
  totalPages?: number;
  onCloseMobileMenu?: () => void;
}

export const PlayerFilters = memo(function PlayerFilters({
  selectedTour,
  availableTours,
  onTourChange,
  playerCount,
  totalPlayers,
  currentPage,
  totalPages,
  onCloseMobileMenu
}: PlayerFiltersProps) {
  return (
    <div className="p-4 md:p-4 border-b border-gray-200 dark:border-gray-700 space-y-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 md:bg-none">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Players</h2>
        {onCloseMobileMenu && (
          <button 
            onClick={onCloseMobileMenu}
            className="md:hidden p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          >
            <X size={20} className="text-gray-500 dark:text-gray-400" />
          </button>
        )}
      </div>
      
      <Tabs value={selectedTour} onValueChange={onTourChange}>
        <TabsList variant="pills" className="grid w-full grid-cols-3">
          {availableTours.map((tour) => (
            <TabsTrigger key={tour} value={tour} variant="pills" className="text-sm">
              {tour}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>
      
      <p className="text-sm text-gray-500 dark:text-gray-400">
        {playerCount} players
        {selectedTour !== "All Tours" && ` in ${selectedTour}`}
        {totalPlayers && currentPage && totalPages && (
          <span className="block text-xs mt-1">
            Page {currentPage} of {totalPages} ({totalPlayers} total)
          </span>
        )}
      </p>
    </div>
  );
});