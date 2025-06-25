"use client";

import Header from "@/components/ui/Header";
import { Card, CardContent } from "@/components/ui/card";
import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import { Player } from "@/types/schemas";
import { useState } from "react";

export default function Home() {
  const { data: players, error, isLoading } = useSWR<Player[]>(
    "http://localhost:8000/players",
    fetcher
  );
  const [query, setQuery] = useState("");

  const filteredPlayers = players?.filter((p) =>
    p.name.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <>
      <Header onSearch={setQuery} />
      <main className="p-4 max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {isLoading && <div>Loading...</div>}
        {error && <div className="text-red-500">Failed to load</div>}
        {filteredPlayers?.map((player) => (
          <Card key={player.id} className="p-3 shadow-sm border rounded-md text-sm">
            <h2 className="text-base font-semibold">{player.name}</h2>
            <p className="text-xs text-gray-500">{player.tour} • {player.country}</p>
            <CardContent className="mt-2 space-y-1">
              {player.witb_items.length === 0 ? (
                <p className="text-gray-400 italic text-xs">No clubs available</p>
              ) : (
                player.witb_items.map((club, index) => (
                  <div key={index} className="border p-1 rounded text-xs bg-gray-50">
                    <strong>{club.category}</strong>: {club.brand} {club.model}
                    {club.loft && <span> ({club.loft})</span>}
                    {club.shaft && <div className="text-[10px] text-gray-500">Shaft: {club.shaft}</div>}
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        ))}
      </main>
    </>
  );
}
