"use client";

import type {
  Player,
  WITBItem,
  PaginatedPlayersResponse,
} from "@/types/schemas";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ChevronDownIcon, ChevronUpIcon, Heart } from "lucide-react";
import { useOWGRInfo } from "@/hooks/useOWGRInfo";
import { useAuth } from "@/providers/auth-provider";
import { useFavorites } from "@/providers/favorites-provider";
import { PriceButton } from "@/components/pricing/PriceButton";
import heartStyles from "@/components/ui/heartAnimations.module.css";

interface PlayerTableProps {
  players: Player[];
  isLoading: boolean;
  error: Error | null;
  playersResponse?: PaginatedPlayersResponse;
  page: number;
  onPageChange: (page: number) => void;
  onWitbExpansionChange?: (hasExpanded: boolean) => void;
}

export function PlayerTable({
  players,
  isLoading,
  error,
  playersResponse,
  page,
  onPageChange,
  onWitbExpansionChange,
}: PlayerTableProps) {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const { owgrInfo, formatLastUpdated } = useOWGRInfo(
    playersResponse?.system_info,
  );
  const { user } = useAuth();
  const { addFavorite, removeFavorite, isFavorite } = useFavorites();
  const [togglingFavorites, setTogglingFavorites] = useState<Set<string>>(
    new Set(),
  );
  const [animatingFavorites, setAnimatingFavorites] = useState<Set<string>>(
    new Set(),
  );
  const [favoriteAnimations, setFavoriteAnimations] = useState<
    Map<string, "filling" | "unfilling" | "success">
  >(new Map());

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

    const currentlyFavorited = isFavorite(playerId);

    // Start animation immediately for better UX
    setTogglingFavorites((prev) => new Set(prev).add(playerId));
    setAnimatingFavorites((prev) => new Set(prev).add(playerId));
    setFavoriteAnimations((prev) =>
      new Map(prev).set(playerId, currentlyFavorited ? "unfilling" : "filling"),
    );

    try {
      if (currentlyFavorited) {
        await removeFavorite(playerId);
      } else {
        await addFavorite(playerId);
      }

      // Add success animation after API call
      setFavoriteAnimations((prev) => new Map(prev).set(playerId, "success"));
    } catch (error) {
      console.error("Failed to toggle favorite:", error);
    } finally {
      // Clean up animations and loading states
      setTimeout(() => {
        setTogglingFavorites((prev) => {
          const newSet = new Set(prev);
          newSet.delete(playerId);
          return newSet;
        });
        setAnimatingFavorites((prev) => {
          const newSet = new Set(prev);
          newSet.delete(playerId);
          return newSet;
        });
        setFavoriteAnimations((prev) => {
          const newMap = new Map(prev);
          newMap.delete(playerId);
          return newMap;
        });
      }, 600);
    }
  };

  const getHeartClasses = (playerId: string, size: "sm" | "md" = "md") => {
    const sizeClasses = size === "sm" ? "h-3 w-3" : "h-4 w-4";
    const baseClasses = `${sizeClasses} ${heartStyles.heartIcon} transition-all duration-200`;
    const isFav = isFavorite(playerId);
    const animation = favoriteAnimations.get(playerId);
    const isAnimating = animatingFavorites.has(playerId);

    let classes = `${baseClasses} text-red-500`;

    // Add animation classes
    if (animation === "filling") {
      classes += ` ${heartStyles.heartFavoriting}`;
    } else if (animation === "unfilling") {
      classes += ` ${heartStyles.heartUnfavoriting}`;
    } else if (animation === "success") {
      classes += ` ${heartStyles.heartSuccess}`;
    }

    // Add state classes
    if (isFav) {
      classes += ` fill-current ${heartStyles.favorited}`;
      if (!isAnimating) {
        classes += ` ${heartStyles.heartFavorited}`;
      }
    } else {
      classes += ` ${heartStyles.unfavorited}`;
    }

    // Add loading state
    if (isAnimating && !animation) {
      classes += ` ${heartStyles.heartLoading}`;
    }

    return classes;
  };

  const getButtonClasses = (playerId: string, baseClasses: string) => {
    const isAnimating = animatingFavorites.has(playerId);
    let classes = `${baseClasses} ${heartStyles.favoriteButton}`;

    if (isAnimating) {
      classes += ` ${heartStyles.favoriteButtonAnimating}`;
    }

    return classes;
  };

  const getKeyClubs = (witbItems: WITBItem[]) => {
    const keyCategories = ["Driver", "Putter", "Ball"];
    return witbItems
      .filter((item) =>
        keyCategories.some((category) =>
          item.category.toLowerCase().includes(category.toLowerCase()),
        ),
      )
      .slice(0, 3);
  };

  const getPrimaryBrand = (witbItems: WITBItem[]) => {
    if (witbItems.length === 0) return "N/A";

    // Count brand frequency
    const brandCounts = witbItems.reduce(
      (acc, item) => {
        acc[item.brand] = (acc[item.brand] || 0) + 1;
        return acc;
      },
      {} as Record<string, number>,
    );

    // Return most frequent brand
    return (
      Object.entries(brandCounts).sort(([, a], [, b]) => b - a)[0]?.[0] || "N/A"
    );
  };

  const getLastUpdated = (player: Player) => {
    if (player.last_updated) {
      return new Date(player.last_updated).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    }
    return "Not updated";
  };

  const getCompactDate = (player: Player) => {
    if (player.last_updated) {
      const date = new Date(player.last_updated);
      return date
        .toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
        })
        .replace(" ", "");
    }
    return "None";
  };

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="h-16 bg-gray-200 dark:bg-gray-700 rounded"
              ></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="text-center text-red-500">
          Error loading players: {error.message}
        </div>
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
            <div className="md:py-2 md:px-4 md:pr-6 sm:md:pr-8 md:lg:pr-12 md:hover:bg-gray-50 md:dark:hover:bg-gray-700/50 md:transition-colors">
              {/* Mobile Minimal List Layout */}
              <div className="md:hidden">
                <div className="flex items-center justify-between py-3 px-4 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors">
                  {/* Left side: Rank + Name + Date */}
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <span className="text-sm font-bold text-emerald-600 w-7 flex-shrink-0">
                      #{player.ranking || "-"}
                    </span>
                    <div className="flex-1 min-w-0">
                      <span className="font-medium text-gray-900 dark:text-white block truncate text-sm">
                        {player.name}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500 dark:text-gray-400 flex-shrink-0">
                      {getCompactDate(player)}
                    </span>
                  </div>

                  {/* Right side: Actions */}
                  <div className="flex items-center gap-1 ml-3 flex-shrink-0">
                    <Button
                      onClick={() => toggleFavorite(player.id)}
                      variant="ghost"
                      size="sm"
                      disabled={togglingFavorites.has(player.id) || !user}
                      className="h-8 w-8 p-0 hover:bg-red-50 dark:hover:bg-red-900/20"
                      title={
                        !user
                          ? "Sign in to add favorites"
                          : isFavorite(player.id)
                            ? "Remove from favorites"
                            : "Add to favorites"
                      }
                    >
                      <Heart className={getHeartClasses(player.id, "sm")} />
                    </Button>
                    <Button
                      onClick={() => toggleRowExpansion(player.id)}
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 hover:bg-emerald-50 dark:hover:bg-emerald-900/20"
                    >
                      {expandedRows.has(player.id) ? (
                        <ChevronUpIcon className="h-4 w-4 text-emerald-600" />
                      ) : (
                        <ChevronDownIcon className="h-4 w-4 text-emerald-600" />
                      )}
                    </Button>
                  </div>
                </div>
              </div>

              {/* Desktop Grid Layout */}
              <div className="hidden md:grid grid-cols-12 gap-4">
                {/* Rank */}
                <div className="col-span-1 flex items-center">
                  <span className="font-bold text-gray-900 dark:text-white">
                    {player.ranking ? `#${player.ranking}` : "-"}
                  </span>
                </div>

                {/* Player */}
                <div className="col-span-3 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-blue-200 dark:bg-blue-800 flex items-center justify-center text-blue-700 dark:text-blue-200 text-xs font-bold flex-shrink-0">
                    {player.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900 dark:text-white">
                      {player.name}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
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
                        className="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs px-1.5 py-0.5"
                      >
                        {club.category}: {club.brand} {club.model.slice(0, 10)}
                        {club.model.length > 10 ? "..." : ""}
                      </Badge>
                    ))}
                    {getKeyClubs(player.witb_items).length === 0 && (
                      <span className="text-sm text-gray-400 dark:text-gray-500">
                        No key clubs
                      </span>
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
                    className={getButtonClasses(
                      player.id,
                      "h-8 px-2 border-gray-200 dark:border-gray-700 hover:border-red-300 hover:bg-red-50 dark:hover:bg-red-900/20",
                    )}
                    title={
                      !user
                        ? "Sign in to add favorites"
                        : isFavorite(player.id)
                          ? "Remove from favorites"
                          : "Add to favorites"
                    }
                  >
                    <Heart className={getHeartClasses(player.id, "sm")} />
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
                  ? "max-h-[3000px] opacity-100"
                  : "max-h-0 opacity-0"
              }`}
            >
              <div className="bg-gray-50 dark:bg-gray-900/30 border-t border-gray-200 dark:border-gray-700">
                <div
                  className={`p-4 md:p-6 transition-all duration-300 delay-200 ${
                    expandedRows.has(player.id)
                      ? "translate-y-0"
                      : "translate-y-4"
                  }`}
                >
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Complete WITB - {player.name}
                  </h3>

                  {/* Player Details - Mobile Only */}
                  <div className="md:hidden mb-6 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                    <div className="space-y-2">
                      <div className="flex items-center gap-4">
                        <span className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                          <span className="text-lg">🌍</span>
                          <span className="font-medium">{player.country}</span>
                        </span>
                        <span className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                          <span className="text-lg">🏌️</span>
                          <span className="font-medium">
                            {getPrimaryBrand(player.witb_items)}
                          </span>
                        </span>
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        <span className="font-medium">Last Updated:</span>{" "}
                        {getLastUpdated(player)}
                      </div>
                    </div>
                  </div>

                  {player.witb_items.length === 0 ? (
                    <div className="text-center py-8">
                      <div className="text-gray-400 text-3xl mb-2">⛳</div>
                      <p className="text-gray-500 dark:text-gray-400">
                        No equipment data available
                      </p>
                    </div>
                  ) : (
                    <>
                      {/* Mobile Equipment List - Simple List */}
                      <div className="md:hidden">
                        {player.witb_items.map((club, index) => (
                          <div
                            key={index}
                            className="flex items-start justify-between py-4 px-4 border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50/30 dark:hover:bg-gray-700/10 transition-colors last:border-b-0"
                            style={{
                              animationDelay: `${index * 50}ms`,
                              animation: expandedRows.has(player.id)
                                ? "fadeInUp 0.3s ease-out forwards"
                                : "none",
                            }}
                          >
                            {/* Left: Category + Brand/Model + Specs */}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-start gap-3">
                                <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 dark:bg-emerald-900/30 dark:text-emerald-300 px-2 py-1 rounded-md w-16 text-center flex-shrink-0">
                                  {club.category}
                                </span>
                                <div className="flex-1 min-w-0">
                                  <div className="font-semibold text-gray-900 dark:text-white text-sm">
                                    {club.brand}
                                  </div>
                                  <div className="text-sm text-gray-600 dark:text-gray-400 truncate">
                                    {club.model}
                                  </div>
                                  {(club.loft || club.shaft) && (
                                    <div className="text-xs text-gray-500 dark:text-gray-400 truncate mt-1">
                                      {club.loft}
                                      {club.loft && club.shaft && " • "}
                                      {club.shaft}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>

                            {/* Right: Price Action */}
                            <div className="flex items-start gap-1 flex-shrink-0">
                              <PriceButton
                                witbItem={club}
                                variant="ghost"
                                size="sm"
                                className="text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-900/20"
                              />
                            </div>
                          </div>
                        ))}
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
                                Actions
                              </th>
                            </tr>
                          </thead>

                          {/* Table Body */}
                          <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
                            {player.witb_items.map((club, index) => (
                              <tr
                                key={index}
                                className="hover:bg-gray-50 dark:hover:bg-gray-800/50"
                              >
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
                                  {club.loft || "-"}
                                </td>
                                <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                                  {club.shaft || "-"}
                                </td>
                                <td className="py-3 px-4">
                                  <div className="flex items-center gap-2">
                                    <PriceButton
                                      witbItem={club}
                                      variant="outline"
                                      size="sm"
                                      className="text-xs px-2 py-1 h-6"
                                    />
                                    {club.product_url ? (
                                      <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() =>
                                          window.open(
                                            club.product_url,
                                            "_blank",
                                          )
                                        }
                                        className="text-xs px-2 py-1 h-6"
                                      >
                                        View
                                      </Button>
                                    ) : (
                                      <span className="text-xs text-gray-400">
                                        -
                                      </span>
                                    )}
                                  </div>
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
                {isLoading
                  ? "Loading..."
                  : `Page ${page} of ${playersResponse.total_pages}`}
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
                {isLoading
                  ? "Loading..."
                  : `Page ${page} of ${playersResponse.total_pages}`}
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
          Equipment data scraped from PGA Club Tracker with intelligent sync
          technology.
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
