"use client";

import { useState } from "react";
import { useLeaderboardData } from "@/hooks/useLeaderboardData";
import { 
  getAvailableCategories, 
  getDisplayItems, 
  MAJOR_CATEGORIES,
  validateLeaderboardData 
} from "@/lib/leaderboard-utils";
import {
  LeaderboardCard,
  LeaderboardTabs,
  LeaderboardHeader,
  LeaderboardSkeleton,
  LeaderboardFooter
} from "@/components/leaderboard";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import styles from "@/components/ui/glassmorphism.module.css";

export function ClubLeaderboard() {
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const { leaderboardData, error, isLoading, refetch } = useLeaderboardData(3);

  // Validate data when it arrives
  const validatedData = leaderboardData && validateLeaderboardData(leaderboardData) 
    ? leaderboardData 
    : undefined;

  // Check for data corruption
  const hasInvalidData = leaderboardData && !validatedData;

  const availableCategories = getAvailableCategories(validatedData);
  const displayItems = getDisplayItems(validatedData, selectedCategory, MAJOR_CATEGORIES);

  if (isLoading) {
    return <LeaderboardSkeleton />;
  }

  if (error) {
    return (
      <div className={styles.glassContainer + " p-6"}>
        <div className="text-center">
          <h3 className="text-lg font-semibold text-red-600 dark:text-red-400 mb-2">
            Failed to load leaderboard data
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            {error.message || "Network error occurred"}
          </p>
          <button
            onClick={() => refetch()}
            className={styles.glassButton + " px-4 py-2 text-sm"}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (hasInvalidData) {
    return (
      <div className={styles.glassContainer + " p-6"}>
        <div className="text-center">
          <h3 className="text-lg font-semibold text-amber-600 dark:text-amber-400 mb-2">
            Invalid data received
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            The server returned malformed data. Please try again.
          </p>
          <button
            onClick={() => refetch()}
            className={styles.glassButton + " px-4 py-2 text-sm"}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!validatedData || displayItems.length === 0) {
    return (
      <div className={styles.glassContainer + " p-6"}>
        <div className="text-center text-gray-500 dark:text-gray-400">
          No leaderboard data available
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className={styles.glassContainer + " relative overflow-hidden"}>
        {/* Glass background with gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/5 to-pink-500/10"></div>
        <div className="relative z-10 p-6">
          
          <LeaderboardHeader leaderboardData={validatedData} />

          <LeaderboardTabs
            selectedCategory={selectedCategory}
            onCategoryChange={setSelectedCategory}
            availableCategories={availableCategories}
          >
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {displayItems.map((item, index) => (
                <LeaderboardCard
                  key={`${item.brand}-${item.model}-${index}`}
                  item={item}
                  index={index}
                  showCategory={selectedCategory === "all"}
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