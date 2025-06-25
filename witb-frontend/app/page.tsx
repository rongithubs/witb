"use client";



import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

import useSWR from "swr"; 
import { fetcher } from "@/lib/fetcher";
import { Player } from "@/types/schemas"; // adjust path if needed


export default function Home() {
  const { data: players, error, isLoading } = useSWR<Player[]>(
    "http://localhost:8000/players",
    fetcher
  );

  if (isLoading) return <div className="p-6">Loading...</div>;
  if (error) return <div className="p-6 text-red-500">Failed to load players</div>;

  return (
    <main className="p-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {players?.map((player) => (
        <Card key={player.id} className="p-4">
          <h2 className="text-xl font-semibold mb-1">{player.name}</h2>
          <p className="text-sm text-gray-500">{player.tour} • {player.country}</p>

          <CardContent className="mt-4 space-y-2">
            {player.witb_items.length === 0 ? (
              <p className="text-gray-400 italic">No clubs available</p>
            ) : (
              player.witb_items.map((club, index) => (
                <div key={index} className="border p-2 rounded text-sm">
                  <strong>{club.category}</strong>: {club.brand} {club.model} {club.loft && `(${club.loft})`}
                  {club.shaft && <div className="text-xs text-gray-500">Shaft: {club.shaft}</div>}
                </div>
              ))
            )}
          </CardContent>
        </Card>
      ))}
    </main>
  );
}
