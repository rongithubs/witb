import type { ClubUsageItem, LeaderboardData } from "@/hooks/useLeaderboardData";

// Club categories ordered from longest to shortest clubs
export const MAJOR_CATEGORIES = [
  "Driver", 
  "3-wood", 
  "5-wood", 
  "Iron", 
  "Wedge", 
  "Putter", 
  "Ball"
] as const;

export type MajorCategory = typeof MAJOR_CATEGORIES[number];

/**
 * Validates that leaderboard data has the expected structure
 */
export function validateLeaderboardData(data: unknown): data is LeaderboardData {
  if (!data || typeof data !== 'object') return false;
  
  const typedData = data as Record<string, unknown>;
  
  return (
    typeof typedData.categories === 'object' &&
    typedData.categories !== null &&
    typeof typedData.total_categories === 'number' &&
    typeof typedData.total_unique_combinations === 'number'
  );
}

/**
 * Filters available categories to only include major categories that have data
 */
export function getAvailableCategories(
  leaderboardData: LeaderboardData | undefined
): string[] {
  if (!leaderboardData) return [];
  
  return MAJOR_CATEGORIES.filter(cat => 
    leaderboardData.categories[cat] && 
    leaderboardData.categories[cat].length > 0
  );
}

/**
 * Gets display items for the selected category
 */
export function getDisplayItems(
  leaderboardData: LeaderboardData | undefined,
  selectedCategory: string,
  majorCategories: readonly string[] = MAJOR_CATEGORIES
): Array<ClubUsageItem & { category?: string }> {
  if (!leaderboardData) return [];
  
  if (selectedCategory === "all") {
    return getAllCategoriesDisplay(leaderboardData, majorCategories);
  }
  
  return leaderboardData.categories[selectedCategory] || [];
}

/**
 * Gets top items from each major category for "all" view
 */
function getAllCategoriesDisplay(
  leaderboardData: LeaderboardData,
  majorCategories: readonly string[]
): Array<ClubUsageItem & { category: string }> {
  const allItems: Array<ClubUsageItem & { category: string }> = [];
  
  majorCategories.forEach(cat => {
    if (leaderboardData.categories[cat]) {
      leaderboardData.categories[cat].slice(0, 1).forEach(item => {
        allItems.push({ ...item, category: cat });
      });
    }
  });
  
  return allItems.sort((a, b) => b.count - a.count).slice(0, 6);
}

/**
 * Determines if an item is a champion (rank 1)
 */
export function isChampionItem(item: ClubUsageItem): boolean {
  return item.rank === 1;
}

/**
 * Gets the rank badge variant for styling
 */
export function getRankBadgeVariant(rank: number): string {
  if (rank <= 3) return `rank-${rank}`;
  return 'rank-other';
}