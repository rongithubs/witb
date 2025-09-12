"use client";

import { useState } from "react";
import { useLeaderboardData } from "@/hooks/useLeaderboardData";
import {
  getAvailableCategories,
  getDisplayItems,
  MAJOR_CATEGORIES,
  validateLeaderboardData,
} from "@/lib/leaderboard-utils";
import {
  LeaderboardCard,
  LeaderboardTabs,
  LeaderboardHeader,
  LeaderboardSkeleton,
  LeaderboardFooter,
} from "@/components/leaderboard";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";

export function ClubLeaderboard() {
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const { leaderboardData, error, isLoading, refetch } = useLeaderboardData(3);

  // Validate data when it arrives
  const validatedData =
    leaderboardData && validateLeaderboardData(leaderboardData)
      ? leaderboardData
      : undefined;

  // Check for data corruption
  const hasInvalidData = leaderboardData && !validatedData;

  const availableCategories = getAvailableCategories(validatedData);
  const displayItems = getDisplayItems(
    validatedData,
    selectedCategory,
    MAJOR_CATEGORIES,
  );

  if (isLoading) {
    return <LeaderboardSkeleton />;
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-red-600 dark:text-red-400 mb-2">
            Failed to load leaderboard data
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            {error.message || "Network error occurred"}
          </p>
          <button
            onClick={() => refetch()}
            className="bg-gray-900 hover:bg-gray-800 text-white px-4 py-2 text-sm rounded-md"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (hasInvalidData) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-amber-600 dark:text-amber-400 mb-2">
            Invalid data received
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            The server returned malformed data. Please try again.
          </p>
          <button
            onClick={() => refetch()}
            className="bg-gray-900 hover:bg-gray-800 text-white px-4 py-2 text-sm rounded-md"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!validatedData || displayItems.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="text-center text-gray-500 dark:text-gray-400">
          No leaderboard data available
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div
        data-testid="club-leaderboard"
        className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700"
      >
        <div className="p-6">
          <LeaderboardHeader leaderboardData={validatedData} />

          <LeaderboardTabs
            selectedCategory={selectedCategory}
            onCategoryChange={setSelectedCategory}
            availableCategories={availableCategories}
          >
            <div className="grid grid-cols-1 gap-4">
              {displayItems.map((item, index) => (
                <LeaderboardCard
                  key={`${item.brand}-${item.model}-${index}`}
                  item={item}
                  index={index}
                />
              ))}
            </div>
          </LeaderboardTabs>

          <LeaderboardFooter leaderboardData={validatedData} />
        </div>
      </div>
    </ErrorBoundary>
  );
}
