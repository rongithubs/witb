"use client";

import { memo } from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Player } from "@/types/schemas";
import { getCountryFlag, formatAge } from "@/utils/countryFlags";
import { PlayerDetailsSkeleton } from "@/components/skeletons";

interface PlayerDetailsProps {
  selectedPlayer: Player | null;
  isLoading: boolean;
}

export const PlayerDetails = memo(function PlayerDetails({
  selectedPlayer,
  isLoading
}: PlayerDetailsProps) {
  if (isLoading) {
    return <PlayerDetailsSkeleton />;
  }

  if (!selectedPlayer) {
    return (
      <div className="h-full flex flex-col min-h-[60vh]">
        <div className="flex-1 flex items-center justify-center text-center">
          <div>
            <div className="text-gray-300 dark:text-gray-600 text-6xl mb-4">⛳</div>
            <h2 className="text-xl font-semibold text-gray-600 dark:text-gray-300 mb-2">Select a Player</h2>
            <p className="text-gray-500 dark:text-gray-400">Choose a player from the list to view their equipment</p>
          </div>
        </div>
      </div>
    );
  }

  return (
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm flex flex-col">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-blue-200 dark:bg-blue-800 flex items-center justify-center text-blue-700 dark:text-blue-200 text-xl font-bold">
              {selectedPlayer.name.split(" ").map(n => n[0]).join("")}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                {selectedPlayer.ranking && `#${selectedPlayer.ranking} `}{selectedPlayer.name}
              </h1>
              <p className="text-gray-600 dark:text-gray-300 flex items-center gap-2">
                {selectedPlayer.tour} • 
                <span className="flex items-center gap-1">
                  <span className="text-lg">{getCountryFlag(selectedPlayer.country)}</span>
                  {selectedPlayer.country}
                </span>
                {selectedPlayer.age && <span>• {formatAge(selectedPlayer.age)}</span>}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {selectedPlayer.witb_items.length} clubs in bag
              </p>
            </div>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">What&apos;s In The Bag</h2>
          {selectedPlayer.witb_items.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 text-4xl mb-4">⛳</div>
              <p className="text-gray-500 dark:text-gray-400">No equipment data available</p>
            </div>
          ) : (
            <div className="grid gap-3">
              {selectedPlayer.witb_items.map((club, index) => (
                <Card key={index} className="p-4 hover:shadow-md transition-shadow bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 dark:text-white text-base">{club.category}</h3>
                      <p className="text-blue-600 dark:text-blue-400 font-medium">{club.brand} {club.model}</p>
                      <div className="flex gap-4 mt-2 text-sm text-gray-600 dark:text-gray-300">
                        {club.loft && (
                          <span className="bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-200 px-2 py-1 rounded">{club.loft}</span>
                        )}
                        {club.shaft && (
                          <span className="bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-200 px-2 py-1 rounded">{club.shaft}</span>
                        )}
                      </div>
                    </div>
                    {club.product_url && (
                      <div className="ml-4">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => window.open(club.product_url, '_blank')}
                          className="text-xs"
                        >
                          View Product
                        </Button>
                      </div>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
  );
});