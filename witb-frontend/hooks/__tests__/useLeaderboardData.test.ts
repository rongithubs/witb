import { describe, expect, test, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useLeaderboardData } from '../useLeaderboardData';

// Mock SWR
vi.mock('swr', () => ({
  default: vi.fn()
}));

// Mock fetcher
vi.mock('@/lib/fetcher', () => ({
  fetcher: vi.fn()
}));

describe('useLeaderboardData', () => {
  const mockSWR = vi.mocked(await import('swr')).default;

  test('returns expected structure from SWR', () => {
    const mockData = {
      categories: { Driver: [] },
      total_categories: 1,
      total_unique_combinations: 5
    };

    mockSWR.mockReturnValue({
      data: mockData,
      error: null,
      isLoading: false,
      mutate: vi.fn()
    });

    const { result } = renderHook(() => useLeaderboardData(3));

    expect(result.current.leaderboardData).toEqual(mockData);
    expect(result.current.error).toBeNull();
    expect(result.current.isLoading).toBe(false);
    expect(result.current.isEmpty).toBe(false);
    expect(typeof result.current.refetch).toBe('function');
  });

  test('handles loading state', () => {
    mockSWR.mockReturnValue({
      data: undefined,
      error: null,
      isLoading: true,
      mutate: vi.fn()
    });

    const { result } = renderHook(() => useLeaderboardData(3));

    expect(result.current.leaderboardData).toBeUndefined();
    expect(result.current.isLoading).toBe(true);
    expect(result.current.isEmpty).toBe(false);
  });

  test('handles error state', () => {
    const mockError = new Error('Network error');
    mockSWR.mockReturnValue({
      data: undefined,
      error: mockError,
      isLoading: false,
      mutate: vi.fn()
    });

    const { result } = renderHook(() => useLeaderboardData(3));

    expect(result.current.error).toEqual(mockError);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.isEmpty).toBe(true);
  });

  test('calls SWR with correct URL and limit', () => {
    mockSWR.mockReturnValue({
      data: undefined,
      error: null,
      isLoading: false,
      mutate: vi.fn()
    });

    renderHook(() => useLeaderboardData(5));

    expect(mockSWR).toHaveBeenCalledWith(
      '/witb/leaderboard?limit=5',
      expect.any(Function)
    );
  });

  test('uses default limit of 3', () => {
    mockSWR.mockReturnValue({
      data: undefined,
      error: null,
      isLoading: false,
      mutate: vi.fn()
    });

    renderHook(() => useLeaderboardData());

    expect(mockSWR).toHaveBeenCalledWith(
      '/witb/leaderboard?limit=3',
      expect.any(Function)
    );
  });
});