"use client";

import Header from "@/components/ui/Header";
import { Card } from "@/components/ui/card";
import TournamentWinner from "@/components/TournamentWinner";
import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import { Player } from "@/types/schemas";
import { useState, useCallback } from "react";
import { getCountryFlag, formatAge } from "@/utils/countryFlags";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

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
    setSelectedPlayer(null);
  }, []);

  const availableTours = players
    ? ["All Tours", ...Array.from(new Set(players.map((p) => p.tour))).sort()]
    : ["All Tours"];

  const filteredPlayers = players?.filter((player) => {
    const matchesTour = selectedTour === "All Tours" || player.tour === selectedTour;
    if (!query.trim()) return matchesTour;
    const terms = query.toLowerCase().trim().split(/\s+/);
    const matches = terms.every((term) =>
      player.name.toLowerCase().includes(term) ||
      player.witb_items?.some((club) =>
        club.category.toLowerCase().includes(term) ||
        club.brand.toLowerCase().includes(term) ||
        club.model.toLowerCase().includes(term)
      )
    );
    return matchesTour && matches;
  });

  return (
    <div className="max-w-7xl mx-auto px-4">
      <Header onSearch={setQuery} />
      <div className="my-4">
        <TournamentWinner />
      </div>

      <div className="grid grid-cols-12 gap-4 py-4">
        <div className="col-span-12 md:col-span-4 lg:col-span-3">
          <div className="bg-white border rounded-lg shadow-sm h-[80vh] flex flex-col transition-all duration-300 animate-in fade-in slide-in-from-bottom-4">
            <div className="p-4 border-b space-y-4">
              <h2 className="text-lg font-semibold">Players</h2>
              <Select value={selectedTour} onValueChange={handleTourFilter}>
                <SelectTrigger className="w-full text-sm">
                  <SelectValue placeholder="Select a tour" />
                </SelectTrigger>
                <SelectContent className="text-sm">
                  {availableTours.map((tour) => (
                    <SelectItem key={tour} value={tour}>
                      {tour}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-sm text-gray-500">
                {filteredPlayers?.length || 0} players
                {selectedTour !== "All Tours" && ` in ${selectedTour}`}
              </p>
            </div>

            <ScrollArea className="flex-1" style={{ maxHeight: "calc(80vh - 160px)" }}>
              <div className="p-2 space-y-1">
                {isLoading && <div className="p-2 text-gray-500">Loading...</div>}
                {error && <p className="text-red-500">Failed to load players.</p>}
                {filteredPlayers?.map((player) => (
                  <div
                    key={player.id}
                    onClick={() => handlePlayerSelect(player)}
                    className={`p-3 rounded-md cursor-pointer transition-colors hover:bg-blue-50 ${
                      selectedPlayer?.id === player.id ? "bg-blue-100 border border-blue-200" : "hover:shadow-sm"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-xs font-medium">
                        {player.name.split(" ").map((n) => n[0]).join("")}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between">
                          <h3 className="text-sm font-medium truncate">{player.name}</h3>
                          {player.ranking && (
                            <Badge className="text-xs px-2 py-0.5 bg-gradient-to-r from-blue-500 to-indigo-500 text-white">
                              #{player.ranking}
                            </Badge>
                          )}
                        </div>
                        <p className="text-xs text-gray-500">{player.tour}</p>
                        <p className="text-xs text-gray-400 mt-1">{player.witb_items.length} clubs</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </div>
        </div>

        <div className="col-span-12 md:col-span-8 lg:col-span-9">
          {selectedPlayer ? (
            <div className="bg-white border rounded-lg shadow-sm flex flex-col">
              <div className="p-6 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-blue-200 flex items-center justify-center text-blue-700 text-xl font-bold">
                    {selectedPlayer.name.split(" ").map(n => n[0]).join("")}
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900">
                      {selectedPlayer.ranking && `#${selectedPlayer.ranking} `}{selectedPlayer.name}
                    </h1>
                    <p className="text-gray-600 flex items-center gap-2">
                      {selectedPlayer.tour} • 
                      <span className="flex items-center gap-1">
                        <span className="text-lg">{getCountryFlag(selectedPlayer.country)}</span>
                        {selectedPlayer.country}
                      </span>
                      {selectedPlayer.age && <span>• {formatAge(selectedPlayer.age)}</span>}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      {selectedPlayer.witb_items.length} clubs in bag
                    </p>
                  </div>
                </div>
              </div>
              <div className="flex-1 overflow-y-auto p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">What's In The Bag</h2>
                {selectedPlayer.witb_items.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-gray-400 text-4xl mb-4">⛳</div>
                    <p className="text-gray-500">No equipment data available</p>
                  </div>
                ) : (
                  <div className="grid gap-3">
                    {selectedPlayer.witb_items.map((club, index) => (
                      <Card key={index} className="p-4 hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900 text-base">{club.category}</h3>
                            <p className="text-blue-600 font-medium">{club.brand} {club.model}</p>
                            <div className="flex gap-4 mt-2 text-sm text-gray-600">
                              {club.loft && (
                                <span className="bg-gray-100 px-2 py-1 rounded">{club.loft}</span>
                              )}
                              {club.shaft && (
                                <span className="bg-gray-100 px-2 py-1 rounded">{club.shaft}</span>
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
          ) : (
            <div className="h-full flex items-center justify-center text-center">
              <div>
                <div className="text-gray-300 text-6xl mb-4">⛳</div>
                <h2 className="text-xl font-semibold text-gray-600 mb-2">Select a Player</h2>
                <p className="text-gray-500">Choose a player from the list to view their equipment</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
