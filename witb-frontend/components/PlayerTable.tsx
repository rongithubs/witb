"use client";

import type { Player, WITBItem, PaginatedPlayersResponse } from "@/types/schemas";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ChevronDownIcon, ChevronUpIcon, Heart } from "lucide-react";
import { useOWGRInfo } from "@/hooks/useOWGRInfo";
import { useAuth } from "@/providers/auth-provider";
import { useFavorites } from "@/providers/favorites-provider";

interface PlayerTableProps {
  players: Player[];
  isLoading: boolean;
  error: Error | null;
  playersResponse?: PaginatedPlayersResponse;
  page: number;
  onPageChange: (page: number) => void;
  onWitbExpansionChange?: (hasExpanded: boolean) => void;
}

export function PlayerTable({ players, isLoading, error, playersResponse, page, onPageChange, onWitbExpansionChange }: PlayerTableProps) {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const { owgrInfo, formatLastUpdated } = useOWGRInfo(playersResponse?.system_info);
  const { user } = useAuth();
  const { addFavorite, removeFavorite, isFavorite } = useFavorites();
  const [togglingFavorites, setTogglingFavorites] = useState<Set<string>>(new Set());

  const toggleRowExpansion = (playerId: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(playerId)) {
      newExpanded.delete(playerId);
    } else {
      newExpanded.add(playerId);
    }
    setExpandedRows(newExpanded);
    
    // Notify parent component about expansion state change
    onWitbExpansionChange?.(newExpanded.size > 0);
  };

  const toggleFavorite = async (playerId: string) => {
    if (!user) return;
    
    setTogglingFavorites(prev => new Set(prev).add(playerId));
    
    try {
      if (isFavorite(playerId)) {
        await removeFavorite(playerId);
      } else {
        await addFavorite(playerId);
      }
    } finally {
      setTogglingFavorites(prev => {
        const newSet = new Set(prev);
        newSet.delete(playerId);
        return newSet;
      });
    }
  };

  const getKeyClubs = (witbItems: WITBItem[]) => {
    const keyCategories = ["Driver", "Putter", "Ball"];
    return witbItems.filter(item => 
      keyCategories.some(category => 
        item.category.toLowerCase().includes(category.toLowerCase())
      )
    ).slice(0, 3);
  };

  const getPrimaryBrand = (witbItems: WITBItem[]) => {
    if (witbItems.length === 0) return "N/A";
    
    // Count brand frequency
    const brandCounts = witbItems.reduce((acc, item) => {
      acc[item.brand] = (acc[item.brand] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    // Return most frequent brand
    return Object.entries(brandCounts)
      .sort(([,a], [,b]) => b - a)[0]?.[0] || "N/A";
  };

  const getLastUpdated = (player: Player) => {
    if (player.last_updated) {
      return new Date(player.last_updated).toLocaleDateString('en-US', { 
        month: 'short', day: 'numeric', year: 'numeric' 
      });
    }
    return 'Not updated';
  };

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="text-center text-red-500">Error loading players: {error.message}</div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Desktop Table Header */}
      <div className="hidden md:grid grid-cols-12 gap-4 p-4 pr-8 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50 text-sm font-semibold text-gray-700 dark:text-gray-300">
        <div className="col-span-1">Rank</div>
        <div className="col-span-3">Player</div>
        <div className="col-span-1">Country</div>
        <div className="col-span-3">Key Clubs</div>
        <div className="col-span-2">Updated</div>
        <div className="col-span-2">Actions</div>
      </div>

      {/* OWGR Update Info Subheader - Mobile */}
      {owgrInfo && (
        <div className="md:hidden bg-blue-50 dark:bg-blue-950/30 border-b border-blue-200 dark:border-blue-800 px-4 py-3">
          <div className="text-center text-sm text-blue-700 dark:text-blue-300">
            <div className="font-medium">OWGR Rankings</div>
            <div className="text-xs mt-1">Last updated {formatLastUpdated}</div>
          </div>
        </div>
      )}

      {/* OWGR Update Info Subheader - Desktop */}
      {owgrInfo && (
        <div className="hidden md:block bg-blue-50 dark:bg-blue-950/30 border-b border-blue-200 dark:border-blue-800 px-4 py-3">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2 text-blue-700 dark:text-blue-300">
              <span className="font-medium">OWGR Rankings:</span>
              <span>Last updated {formatLastUpdated}</span>
            </div>
            <div className="flex items-center gap-4 text-xs text-blue-600 dark:text-blue-400">
              <span>{owgrInfo.updated_count} players updated</span>
            </div>
          </div>
        </div>
      )}

      {/* Table Body */}
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {players.map((player) => (
          <div key={player.id}>
            {/* Player Row */}
            <div className="p-4 pr-6 sm:pr-8 md:pr-10 lg:pr-12 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              {/* Mobile Card Layout - Redesigned */}
              <div className="md:hidden">
                <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 space-y-4">
                  {/* Header: Rank + Player Info */}
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center text-white font-bold text-sm shadow-sm">
                        {player.name.split(" ").map(n => n[0]).join("")}
                      </div>
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-lg text-gray-900 dark:text-white truncate">
                          {player.name}
                        </h3>
                        <span className="flex-shrink-0 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 text-xs font-bold px-2 py-1 rounded-full">
                          #{player.ranking || '-'}
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400">
                        <span className="inline-flex items-center gap-1">
                          🌍 {player.country}
                        </span>
                        <span className="inline-flex items-center gap-1">
                          🏌️ {getPrimaryBrand(player.witb_items)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Key Equipment Preview */}
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Key Equipment</h4>
                    <div className="flex flex-wrap gap-2">
                      {getKeyClubs(player.witb_items).map((club, index) => (
                        <div 
                          key={index}
                          className="bg-gray-50 dark:bg-gray-700 rounded-lg px-3 py-2 text-xs"
                        >
                          <div className="font-medium text-gray-900 dark:text-white">
                            {club.category}
                          </div>
                          <div className="text-gray-600 dark:text-gray-400">
                            {club.brand}
                          </div>
                        </div>
                      ))}
                      {getKeyClubs(player.witb_items).length === 0 && (
                        <div className="text-sm text-gray-400 dark:text-gray-500 italic">
                          No equipment data available
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Footer: Last Updated + Actions */}
                  <div className="flex items-center justify-between pt-2 border-t border-gray-100 dark:border-gray-700">
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Updated {getLastUpdated(player)}
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        onClick={() => toggleFavorite(player.id)}
                        variant="outline"
                        size="sm"
                        disabled={togglingFavorites.has(player.id) || !user}
                        className="h-9 px-3 border-gray-200 dark:border-gray-700 hover:border-red-300 hover:bg-red-50 dark:hover:bg-red-900/20"
                        title={!user ? "Sign in to add favorites" : isFavorite(player.id) ? "Remove from favorites" : "Add to favorites"}
                      >
                        <Heart className={`h-4 w-4 text-red-500 ${isFavorite(player.id) ? 'fill-current' : ''}`} />
                      </Button>
                      <Button
                        onClick={() => toggleRowExpansion(player.id)}
                        variant="default"
                        size="sm"
                        className="bg-emerald-600 hover:bg-emerald-700 text-white text-sm px-4 py-2 h-9 rounded-lg font-medium shadow-sm transition-all duration-200"
                      >
                        <span className="mr-2">
                          {expandedRows.has(player.id) ? "Hide" : "View"} Full Bag
                        </span>
                        {expandedRows.has(player.id) ? (
                          <ChevronUpIcon className="h-4 w-4" />
                        ) : (
                          <ChevronDownIcon className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Desktop Grid Layout */}
              <div className="hidden md:grid grid-cols-12 gap-4">
                {/* Rank */}
                <div className="col-span-1 flex items-center">
                  <span className="font-bold text-gray-900 dark:text-white">
                    {player.ranking ? `#${player.ranking}` : '-'}
                  </span>
                </div>

                {/* Player */}
                <div className="col-span-3 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-blue-200 dark:bg-blue-800 flex items-center justify-center text-blue-700 dark:text-blue-200 text-sm font-bold flex-shrink-0">
                    {player.name.split(" ").map(n => n[0]).join("")}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900 dark:text-white">
                      {player.name}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      Primary brand: {getPrimaryBrand(player.witb_items)}
                    </div>
                  </div>
                </div>

                {/* Country */}
                <div className="col-span-1 flex items-center">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300 uppercase">
                    {player.country.slice(0, 3)}
                  </span>
                </div>

                {/* Key Clubs */}
                <div className="col-span-3 flex items-center">
                  <div className="flex flex-wrap gap-1">
                    {getKeyClubs(player.witb_items).map((club, index) => (
                      <Badge 
                        key={index} 
                        variant="secondary"
                        className="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs px-2 py-1"
                      >
                        {club.category}: {club.brand} {club.model.slice(0, 10)}{club.model.length > 10 ? '...' : ''}
                      </Badge>
                    ))}
                    {getKeyClubs(player.witb_items).length === 0 && (
                      <span className="text-sm text-gray-400 dark:text-gray-500">No key clubs</span>
                    )}
                  </div>
                </div>

                {/* Updated */}
                <div className="col-span-2 flex items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {getLastUpdated(player)}
                  </span>
                </div>

                {/* Actions */}
                <div className="col-span-2 flex items-center justify-start pr-6 gap-2">
                  <Button
                    onClick={() => toggleFavorite(player.id)}
                    variant="outline"
                    size="sm"
                    disabled={togglingFavorites.has(player.id) || !user}
                    className="h-8 px-2 border-gray-200 dark:border-gray-700 hover:border-red-300 hover:bg-red-50 dark:hover:bg-red-900/20"
                    title={!user ? "Sign in to add favorites" : isFavorite(player.id) ? "Remove from favorites" : "Add to favorites"}
                  >
                    <Heart className={`h-3 w-3 text-red-500 ${isFavorite(player.id) ? 'fill-current' : ''}`} />
                  </Button>
                  <Button
                    onClick={() => toggleRowExpansion(player.id)}
                    variant="default"
                    size="sm"
                    className="bg-gray-900 hover:bg-gray-800 text-white text-xs px-3 py-1 h-8"
                  >
                    <span className="mr-1">View WITB</span>
                    {expandedRows.has(player.id) ? (
                      <ChevronUpIcon className="h-3 w-3" />
                    ) : (
                      <ChevronDownIcon className="h-3 w-3" />
                    )}
                  </Button>
                </div>
              </div>
            </div>

            {/* Expanded WITB Details */}
            <div 
              className={`transition-all duration-500 ease-in-out overflow-hidden ${
                expandedRows.has(player.id) 
                  ? 'max-h-[3000px] opacity-100' 
                  : 'max-h-0 opacity-0'
              }`}
            >
              <div className="bg-gray-50 dark:bg-gray-900/30 border-t border-gray-200 dark:border-gray-700">
                <div 
                  className={`p-4 md:p-6 transition-all duration-300 delay-200 ${
                    expandedRows.has(player.id) ? 'translate-y-0' : 'translate-y-4'
                  }`}
                >
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Complete WITB - {player.name}
                  </h3>
                  
                  {player.witb_items.length === 0 ? (
                    <div className="text-center py-8">
                      <div className="text-gray-400 text-3xl mb-2">⛳</div>
                      <p className="text-gray-500 dark:text-gray-400">No equipment data available</p>
                    </div>
                  ) : (
                    <>
                      {/* Mobile Equipment Grid - Redesigned */}
                      <div className="md:hidden space-y-4">
                        <div className="grid grid-cols-1 gap-4">
                          {player.witb_items.map((club, index) => (
                            <div
                              key={index}
                              className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm hover:shadow-md transition-all duration-300"
                              style={{
                                animationDelay: `${index * 75}ms`,
                                animation: expandedRows.has(player.id)
                                  ? "fadeInUp 0.5s ease-out forwards"
                                  : "none",
                              }}
                            >
                              {/* Club Header */}
                              <div className="flex items-start justify-between mb-4">
                                <div className="flex-1">
                                  <div className="inline-flex items-center px-3 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 rounded-full text-sm font-medium mb-2">
                                    {club.category}
                                  </div>
                                  <h4 className="font-bold text-lg text-gray-900 dark:text-white mb-1">
                                    {club.brand}
                                  </h4>
                                  <p className="text-base text-gray-700 dark:text-gray-300 font-medium">
                                    {club.model}
                                  </p>
                                </div>
                                
                                {club.product_url && (
                                  <Button 
                                    size="sm" 
                                    variant="outline"
                                    onClick={() => window.open(club.product_url, '_blank')}
                                    className="flex-shrink-0 text-sm px-3 py-2 rounded-lg border-emerald-200 dark:border-emerald-700 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-50 dark:hover:bg-emerald-900/20"
                                  >
                                    View Product
                                  </Button>
                                )}
                              </div>

                              {/* Specifications */}
                              {(club.loft || club.shaft) && (
                                <div className="space-y-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                                  {club.loft && (
                                    <div className="flex items-center justify-between">
                                      <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Loft:</span>
                                      <span className="text-sm font-semibold text-gray-900 dark:text-white">{club.loft}</span>
                                    </div>
                                  )}
                                  {club.shaft && (
                                    <div className="flex items-start justify-between">
                                      <span className="text-sm font-medium text-gray-600 dark:text-gray-400 flex-shrink-0">Shaft:</span>
                                      <span className="text-sm font-semibold text-gray-900 dark:text-white text-right ml-2">{club.shaft}</span>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Desktop Table Layout */}
                      <div className="hidden md:block overflow-x-auto">
                        <table className="w-full">
                          {/* Table Header */}
                          <thead>
                            <tr className="border-b border-gray-200 dark:border-gray-600">
                              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                                Club
                              </th>
                              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                                Brand
                              </th>
                              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                                Model
                              </th>
                              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                                Loft/Grind
                              </th>
                              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                                Shaft
                              </th>
                              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                                Action
                              </th>
                            </tr>
                          </thead>
                          
                          {/* Table Body */}
                          <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
                            {player.witb_items.map((club, index) => (
                              <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                                <td className="py-3 px-4 text-sm font-medium text-gray-900 dark:text-white">
                                  {club.category}
                                </td>
                                <td className="py-3 px-4 text-sm text-gray-700 dark:text-gray-300">
                                  {club.brand}
                                </td>
                                <td className="py-3 px-4 text-sm text-blue-600 dark:text-blue-400 font-medium">
                                  {club.model}
                                </td>
                                <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                                  {club.loft || '-'}
                                </td>
                                <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                                  {club.shaft || '-'}
                                </td>
                                <td className="py-3 px-4">
                                  {club.product_url ? (
                                    <Button 
                                      size="sm" 
                                      variant="outline"
                                      onClick={() => window.open(club.product_url, '_blank')}
                                      className="text-xs px-2 py-1 h-6"
                                    >
                                      View
                                    </Button>
                                  ) : (
                                    <span className="text-xs text-gray-400">-</span>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination Controls - Mobile-Optimized */}
      {playersResponse && playersResponse.total_pages > 1 && (
        <div className="border-t border-gray-200 dark:border-gray-700 p-4 sm:p-6">
          {/* Mobile Pagination */}
          <div className="flex sm:hidden flex-col gap-4">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900 dark:text-white">
                {isLoading ? "Loading..." : `Page ${page} of ${playersResponse.total_pages}`}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {isLoading ? "" : `${playersResponse.total} players total`}
              </div>
            </div>
            <div className="flex gap-3">
              <Button
                variant="outline"
                size="lg"
                onClick={() => onPageChange(page - 1)}
                disabled={page <= 1 || isLoading}
                className="flex-1 h-12 text-base font-medium disabled:opacity-50 disabled:cursor-not-allowed rounded-xl"
              >
                {isLoading ? "..." : "← Previous"}
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={() => onPageChange(page + 1)}
                disabled={page >= playersResponse.total_pages || isLoading}
                className="flex-1 h-12 text-base font-medium disabled:opacity-50 disabled:cursor-not-allowed rounded-xl"
              >
                {isLoading ? "..." : "Next →"}
              </Button>
            </div>
          </div>

          {/* Desktop Pagination */}
          <div className="hidden sm:flex justify-between items-center">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1 || isLoading}
              className="disabled:opacity-50 disabled:cursor-not-allowed px-6 py-3 rounded-lg"
            >
              {isLoading ? "..." : "← Previous"}
            </Button>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {isLoading ? "Loading..." : `Page ${page} of ${playersResponse.total_pages}`}
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {isLoading ? "" : `${playersResponse.total} players total`}
              </span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(page + 1)}
              disabled={page >= playersResponse.total_pages || isLoading}
              className="disabled:opacity-50 disabled:cursor-not-allowed px-6 py-3 rounded-lg"
            >
              {isLoading ? "..." : "Next →"}
            </Button>
          </div>
        </div>
      )}

      {/* Data Source Disclaimer */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-900/30">
        <p className="text-sm text-gray-500 dark:text-gray-400 italic text-center">
          Equipment data scraped from PGA Club Tracker with intelligent sync technology.
        </p>
      </div>

      {/* CSS Animations */}
      <style jsx>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}