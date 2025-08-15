import { describe, expect, test } from 'vitest';
import {
  validateLeaderboardData,
  getAvailableCategories,
  getDisplayItems,
  isChampionItem,
  getRankBadgeVariant,
  MAJOR_CATEGORIES
} from '../leaderboard-utils';
import type { LeaderboardData, ClubUsageItem } from '@/hooks/useLeaderboardData';

describe('leaderboard-utils', () => {
  const mockClubItem: ClubUsageItem = {
    brand: 'Titleist',
    model: 'Pro V1',
    count: 10,
    percentage: 25.0,
    rank: 1,
    brand_url: 'https://titleist.com'
  };

  const mockLeaderboardData: LeaderboardData = {
    categories: {
      'Driver': [mockClubItem],
      'Iron': [{ ...mockClubItem, rank: 2 }],
      'Putter': [{ ...mockClubItem, rank: 3 }]
    },
    total_categories: 3,
    total_unique_combinations: 10
  };

  describe('validateLeaderboardData', () => {
    test('returns true for valid leaderboard data', () => {
      expect(validateLeaderboardData(mockLeaderboardData)).toBe(true);
    });

    test('returns false for null data', () => {
      expect(validateLeaderboardData(null)).toBe(false);
    });

    test('returns false for undefined data', () => {
      expect(validateLeaderboardData(undefined)).toBe(false);
    });

    test('returns false for non-object data', () => {
      expect(validateLeaderboardData('string')).toBe(false);
      expect(validateLeaderboardData(123)).toBe(false);
      expect(validateLeaderboardData([])).toBe(false);
    });

    test('returns false for missing categories', () => {
      const invalidData = {
        total_categories: 3,
        total_unique_combinations: 10
      };
      expect(validateLeaderboardData(invalidData)).toBe(false);
    });

    test('returns false for missing total_categories', () => {
      const invalidData = {
        categories: {},
        total_unique_combinations: 10
      };
      expect(validateLeaderboardData(invalidData)).toBe(false);
    });

    test('returns false for missing total_unique_combinations', () => {
      const invalidData = {
        categories: {},
        total_categories: 3
      };
      expect(validateLeaderboardData(invalidData)).toBe(false);
    });
  });

  describe('getAvailableCategories', () => {
    test('returns empty array for undefined data', () => {
      expect(getAvailableCategories(undefined)).toEqual([]);
    });

    test('filters major categories that have data', () => {
      const result = getAvailableCategories(mockLeaderboardData);
      expect(result).toEqual(['Driver', 'Iron', 'Putter']);
    });

    test('maintains major category order', () => {
      const dataWithAllCategories: LeaderboardData = {
        categories: {
          'Ball': [mockClubItem],
          'Driver': [mockClubItem],
          'Putter': [mockClubItem],
          'Iron': [mockClubItem],
          'Wedge': [mockClubItem],
          '3-wood': [mockClubItem],
          '5-wood': [mockClubItem]
        },
        total_categories: 7,
        total_unique_combinations: 20
      };
      
      const result = getAvailableCategories(dataWithAllCategories);
      expect(result).toEqual(['Driver', '3-wood', '5-wood', 'Iron', 'Wedge', 'Putter', 'Ball']);
    });

    test('excludes categories with empty arrays', () => {
      const dataWithEmptyCategories: LeaderboardData = {
        categories: {
          'Driver': [mockClubItem],
          'Iron': [],
          'Putter': [mockClubItem]
        },
        total_categories: 2,
        total_unique_combinations: 5
      };
      
      const result = getAvailableCategories(dataWithEmptyCategories);
      expect(result).toEqual(['Driver', 'Putter']);
    });
  });

  describe('getDisplayItems', () => {
    test('returns empty array for undefined data', () => {
      expect(getDisplayItems(undefined, 'Driver')).toEqual([]);
    });

    test('returns specific category items', () => {
      const result = getDisplayItems(mockLeaderboardData, 'Driver');
      expect(result).toEqual([mockClubItem]);
    });

    test('returns empty array for non-existent category', () => {
      const result = getDisplayItems(mockLeaderboardData, 'NonExistent');
      expect(result).toEqual([]);
    });

    test('returns all categories display for "all" selection', () => {
      const result = getDisplayItems(mockLeaderboardData, 'all');
      expect(result).toHaveLength(3);
      expect(result[0]).toHaveProperty('category');
    });

    test('sorts "all" items by count descending', () => {
      const dataWithDifferentCounts: LeaderboardData = {
        categories: {
          'Driver': [{ ...mockClubItem, count: 5 }],
          'Iron': [{ ...mockClubItem, count: 15 }],
          'Putter': [{ ...mockClubItem, count: 10 }]
        },
        total_categories: 3,
        total_unique_combinations: 10
      };
      
      const result = getDisplayItems(dataWithDifferentCounts, 'all');
      expect(result[0].count).toBe(15); // Iron should be first
      expect(result[1].count).toBe(10); // Putter should be second
      expect(result[2].count).toBe(5);  // Driver should be third
    });

    test('limits "all" items to 6', () => {
      const dataWithManyCategories: LeaderboardData = {
        categories: Object.fromEntries(
          MAJOR_CATEGORIES.map((cat, i) => [cat, [{ ...mockClubItem, count: i + 1 }]])
        ),
        total_categories: 7,
        total_unique_combinations: 20
      };
      
      const result = getDisplayItems(dataWithManyCategories, 'all');
      expect(result).toHaveLength(6);
    });
  });

  describe('isChampionItem', () => {
    test('returns true for rank 1 items', () => {
      expect(isChampionItem(mockClubItem)).toBe(true);
    });

    test('returns false for non-rank 1 items', () => {
      expect(isChampionItem({ ...mockClubItem, rank: 2 })).toBe(false);
      expect(isChampionItem({ ...mockClubItem, rank: 3 })).toBe(false);
      expect(isChampionItem({ ...mockClubItem, rank: 10 })).toBe(false);
    });
  });

  describe('getRankBadgeVariant', () => {
    test('returns specific rank classes for top 3', () => {
      expect(getRankBadgeVariant(1)).toBe('rank-1');
      expect(getRankBadgeVariant(2)).toBe('rank-2');
      expect(getRankBadgeVariant(3)).toBe('rank-3');
    });

    test('returns other class for ranks > 3', () => {
      expect(getRankBadgeVariant(4)).toBe('rank-other');
      expect(getRankBadgeVariant(10)).toBe('rank-other');
      expect(getRankBadgeVariant(100)).toBe('rank-other');
    });
  });
});