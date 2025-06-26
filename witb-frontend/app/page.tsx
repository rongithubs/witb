"use client";

import Header from "@/components/ui/Header";
import { Card } from "@/components/ui/card";
import TournamentWinner from "@/components/TournamentWinner";
import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import { Player } from "@/types/schemas";
import { useState, useCallback } from "react";

export default function Home() {
  const { data: players, error, isLoading } = useSWR<Player[]>(
    "http://localhost:8000/players",
    fetcher
  );
  const [query, setQuery] = useState("");
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [selectedTour, setSelectedTour] = useState<string>("All Tours");

  const handlePlayerSelect = useCallback((player: Player) => {
    setSelectedPlayer(player);
  }, []);

  const handleTourFilter = useCallback((tour: string) => {
    setSelectedTour(tour);
    setSelectedPlayer(null); // Clear selection when changing filter
  }, []);

  // Get unique tours for the dropdown
  const availableTours = players ? [
    "All Tours",
    ...Array.from(new Set(players.map(player => player.tour))).sort()
  ] : ["All Tours"];

  const filteredPlayers = players?.filter((player) => {
    // Filter by tour first
    const matchesTour = selectedTour === "All Tours" || player.tour === selectedTour;
    
    // Then filter by search query
    if (!query.trim()) return matchesTour;
    
    const searchTerms = query.toLowerCase().trim().split(/\s+/);
    
    const matchesSearch = searchTerms.every(term => {
      // Match player name
      const matchesPlayer = player.name.toLowerCase().includes(term);
      
      // Match any WITB item fields
      const matchesClub = player.witb_items?.some(
        (club) =>
          club.category.toLowerCase().includes(term) ||
          club.brand.toLowerCase().includes(term) ||
          club.model.toLowerCase().includes(term)
      );
      
      return matchesPlayer || matchesClub;
    });
    
    return matchesTour && matchesSearch;
  });

  return (
    <>
      <Header onSearch={setQuery} />
      
      {/* Tournament Winner - Full Width */}
      <div className="max-w-7xl mx-auto px-4">
        <TournamentWinner />
      </div>

      {/* Main Layout - Sidebar + Detail View */}
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="grid grid-cols-12 gap-6" style={{ height: 'calc(100vh - 220px)' }}>
          
          {/* Left Sidebar - Player List */}
          <div className="col-span-12 md:col-span-4 lg:col-span-3">
            <div className="bg-white border rounded-lg shadow-sm h-full flex flex-col">
              <div className="p-4 border-b">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-lg font-semibold text-gray-900">Players</h2>
                </div>
                
                {/* Tour Filter Dropdown */}
                <div className="mb-3">
                  <select
                    value={selectedTour}
                    onChange={(e) => handleTourFilter(e.target.value)}
                    className="w-full text-sm border border-gray-300 rounded-md px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {availableTours.map((tour) => (
                      <option key={tour} value={tour}>
                        {tour}
                      </option>
                    ))}
                  </select>
                </div>
                
                <p className="text-sm text-gray-500">
                  {filteredPlayers?.length || 0} players
                  {selectedTour !== "All Tours" && (
                    <span className="text-blue-600 ml-1">in {selectedTour}</span>
                  )}
                </p>
              </div>
              
              <div className="flex-1 overflow-y-scroll" style={{ maxHeight: 'calc(100vh - 320px)' }}>
                {isLoading && (
                  <div className="p-4 text-center text-gray-500">Loading...</div>
                )}
                {error && (
                  <div className="p-4 text-center text-red-500">Failed to load</div>
                )}
                
                <div className="space-y-1 p-2 pb-4">
                  {filteredPlayers?.map((player) => (
                    <div
                      key={player.id}
                      onClick={() => handlePlayerSelect(player)}
                      className={`p-3 rounded-lg cursor-pointer transition-all hover:bg-blue-50 ${
                        selectedPlayer?.id === player.id 
                          ? 'bg-blue-100 border-blue-200 border' 
                          : 'hover:shadow-sm'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 text-xs font-medium shrink-0">
                          {player.name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div className="min-w-0 flex-1">
                          <h3 className="text-sm font-medium text-gray-900 truncate">
                            {player.name}
                          </h3>
                          <p className="text-xs text-gray-500">
                            {player.tour} • {player.country}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {player.witb_items.length} clubs
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Player Detail View */}
          <div className="col-span-12 md:col-span-8 lg:col-span-9">
            <div className="bg-white border rounded-lg shadow-sm h-full">
              {selectedPlayer ? (
                <div className="h-full flex flex-col">
                  {/* Player Header */}
                  <div className="p-6 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-16 rounded-full bg-blue-200 flex items-center justify-center text-blue-700 text-xl font-bold">
                        {selectedPlayer.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div>
                        <h1 className="text-2xl font-bold text-gray-900">
                          {selectedPlayer.name}
                        </h1>
                        <p className="text-gray-600">
                          {selectedPlayer.tour} • {selectedPlayer.country}
                        </p>
                        <p className="text-sm text-gray-500 mt-1">
                          {selectedPlayer.witb_items.length} clubs in bag
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* WITB Items */}
                  <div className="flex-1 overflow-y-auto p-6">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">
                      What's In The Bag
                    </h2>
                    
                    {selectedPlayer.witb_items.length === 0 ? (
                      <div className="text-center py-12">
                        <div className="text-gray-400 text-4xl mb-4">⛳</div>
                        <p className="text-gray-500">No equipment data available</p>
                      </div>
                    ) : (
                      <div className="grid gap-3">
                        {(() => {
                          // Group clubs by type for better display
                          const groupedClubs: { [key: string]: any[] } = {};
                          const ironCategories = ['4-Iron', '5-Iron', '6-Iron', '7-Iron', '8-Iron', '9-Iron', 'Pitching Wedge'];
                          
                          selectedPlayer.witb_items.forEach(club => {
                            if (ironCategories.includes(club.category)) {
                              if (!groupedClubs['Irons']) {
                                groupedClubs['Irons'] = [];
                              }
                              groupedClubs['Irons'].push(club);
                            } else {
                              groupedClubs[club.category] = [club];
                            }
                          });
                          
                          return Object.entries(groupedClubs).map(([category, clubs]) => (
                            <Card key={category} className="p-4 hover:shadow-md transition-shadow">
                              <div className="flex justify-between items-start">
                                <div className="flex-1">
                                  <h3 className="font-semibold text-gray-900 text-base">
                                    {category === 'Irons' ? (() => {
                                      // Determine iron range for display
                                      const ironCategories = ['4-Iron', '5-Iron', '6-Iron', '7-Iron', '8-Iron', '9-Iron', 'Pitching Wedge'];
                                      const presentIrons = clubs.map(club => club.category).filter(cat => ironCategories.includes(cat));
                                      const sortedIrons = presentIrons.sort((a, b) => ironCategories.indexOf(a) - ironCategories.indexOf(b));
                                      
                                      if (sortedIrons.length === 0) return 'Irons';
                                      
                                      const firstIron = sortedIrons[0].replace('-Iron', '');
                                      const lastIron = sortedIrons[sortedIrons.length - 1];
                                      const lastDisplay = lastIron === 'Pitching Wedge' ? 'P' : lastIron.replace('-Iron', '');
                                      
                                      return `Irons (${firstIron}-${lastDisplay})`;
                                    })() : category}
                                  </h3>
                                  
                                  {category === 'Irons' ? (
                                    // Special handling for iron sets
                                    <div className="mt-2">
                                      <p className="text-blue-600 font-medium">
                                        {clubs[0]?.brand} {clubs[0]?.model}
                                      </p>
                                      <div className="mt-2">
                                        <div className="text-sm text-gray-600 mb-2">
                                          <span className="bg-gray-100 px-2 py-1 rounded mr-2">
                                            {clubs[0]?.shaft}
                                          </span>
                                        </div>
                                        <div className="grid grid-cols-2 gap-1 text-xs">
                                          {clubs
                                            .sort((a, b) => {
                                              const order = ['4-Iron', '5-Iron', '6-Iron', '7-Iron', '8-Iron', '9-Iron', 'Pitching Wedge'];
                                              return order.indexOf(a.category) - order.indexOf(b.category);
                                            })
                                            .map((iron, idx) => (
                                              <span key={idx} className="text-gray-600">
                                                {iron.category.replace('-Iron', '').replace('Pitching Wedge', 'PW')}: {iron.loft}
                                              </span>
                                            ))}
                                        </div>
                                      </div>
                                    </div>
                                  ) : (
                                    // Regular club display
                                    <div className="mt-1">
                                      <p className="text-blue-600 font-medium">
                                        {clubs[0]?.brand} {clubs[0]?.model}
                                      </p>
                                      <div className="flex gap-4 mt-2 text-sm text-gray-600">
                                        {clubs[0]?.loft && (
                                          <span className="bg-gray-100 px-2 py-1 rounded">
                                            {clubs[0].loft}
                                          </span>
                                        )}
                                        {clubs[0]?.shaft && (
                                          <span className="bg-gray-100 px-2 py-1 rounded">
                                            {clubs[0].shaft}
                                          </span>
                                        )}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </Card>
                          ));
                        })()}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="h-full flex items-center justify-center text-center">
                  <div>
                    <div className="text-gray-300 text-6xl mb-4">⛳</div>
                    <h2 className="text-xl font-semibold text-gray-600 mb-2">
                      Select a Player
                    </h2>
                    <p className="text-gray-500">
                      Choose a player from the list to view their equipment
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
