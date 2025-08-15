import { describe, expect, test, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ClubLeaderboard } from '../ClubLeaderboard';
import type { LeaderboardData } from '@/hooks/useLeaderboardData';

// Mock the hook
vi.mock('@/hooks/useLeaderboardData', () => ({
  useLeaderboardData: vi.fn()
}));

// Mock the utils
vi.mock('@/lib/leaderboard-utils', async () => {
  const actual = await vi.importActual('@/lib/leaderboard-utils');
  return {
    ...actual,
    validateLeaderboardData: vi.fn()
  };
});

describe('ClubLeaderboard', () => {
  const mockUseLeaderboardData = vi.mocked(await import('@/hooks/useLeaderboardData')).useLeaderboardData;
  const mockValidateLeaderboardData = vi.mocked(await import('@/lib/leaderboard-utils')).validateLeaderboardData;

  const mockLeaderboardData: LeaderboardData = {
    categories: {
      'Driver': [
        {
          brand: 'Titleist',
          model: 'TSR3',
          count: 15,
          percentage: 30.0,
          rank: 1,
          brand_url: 'https://titleist.com'
        }
      ],
      'Iron': [
        {
          brand: 'Ping',
          model: 'i230',
          count: 12,
          percentage: 24.0,
          rank: 1,
          brand_url: 'https://ping.com'
        }
      ],
      'Putter': [
        {
          brand: 'Scotty Cameron',
          model: 'Newport 2',
          count: 10,
          percentage: 20.0,
          rank: 1,
          brand_url: 'https://scottycameron.com'
        }
      ]
    },
    total_categories: 3,
    total_unique_combinations: 15
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockValidateLeaderboardData.mockReturnValue(true);
  });

  test('renders loading skeleton when loading', () => {
    mockUseLeaderboardData.mockReturnValue({
      leaderboardData: undefined,
      error: null,
      isLoading: true,
      isEmpty: false,
      refetch: vi.fn()
    });

    render(<ClubLeaderboard />);
    
    expect(screen.getByRole('status', { hidden: true })).toBeInTheDocument();
  });

  test('renders error state with retry button', async () => {
    const mockRefetch = vi.fn();
    const mockError = new Error('Network error');
    
    mockUseLeaderboardData.mockReturnValue({
      leaderboardData: undefined,
      error: mockError,
      isLoading: false,
      isEmpty: true,
      refetch: mockRefetch
    });

    render(<ClubLeaderboard />);
    
    expect(screen.getByText('Failed to load leaderboard data')).toBeInTheDocument();
    expect(screen.getByText('Network error')).toBeInTheDocument();
    
    const retryButton = screen.getByRole('button', { name: /retry/i });
    await userEvent.click(retryButton);
    expect(mockRefetch).toHaveBeenCalledOnce();
  });

  test('renders invalid data state', () => {
    mockUseLeaderboardData.mockReturnValue({
      leaderboardData: { invalid: 'data' } as any,
      error: null,
      isLoading: false,
      isEmpty: false,
      refetch: vi.fn()
    });
    mockValidateLeaderboardData.mockReturnValue(false);

    render(<ClubLeaderboard />);
    
    expect(screen.getByText('Invalid data received')).toBeInTheDocument();
    expect(screen.getByText('The server returned malformed data. Please try again.')).toBeInTheDocument();
  });

  test('renders no data state', () => {
    mockUseLeaderboardData.mockReturnValue({
      leaderboardData: {
        categories: {},
        total_categories: 0,
        total_unique_combinations: 0
      },
      error: null,
      isLoading: false,
      isEmpty: false,
      refetch: vi.fn()
    });

    render(<ClubLeaderboard />);
    
    expect(screen.getByText('No leaderboard data available')).toBeInTheDocument();
  });

  test('renders leaderboard with data', () => {
    mockUseLeaderboardData.mockReturnValue({
      leaderboardData: mockLeaderboardData,
      error: null,
      isLoading: false,
      isEmpty: false,
      refetch: vi.fn()
    });

    render(<ClubLeaderboard />);
    
    expect(screen.getByText('Club Usage Leaderboard')).toBeInTheDocument();
    expect(screen.getByText('3 categories')).toBeInTheDocument();
    
    // Check tabs are rendered
    expect(screen.getByRole('tab', { name: 'All' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Driver' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Iron' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Putter' })).toBeInTheDocument();
  });

  test('shows category data when specific category is selected', async () => {
    mockUseLeaderboardData.mockReturnValue({
      leaderboardData: mockLeaderboardData,
      error: null,
      isLoading: false,
      isEmpty: false,
      refetch: vi.fn()
    });

    render(<ClubLeaderboard />);
    
    const driverTab = screen.getByRole('tab', { name: 'Driver' });
    await userEvent.click(driverTab);
    
    await waitFor(() => {
      expect(screen.getByText('Titleist')).toBeInTheDocument();
      expect(screen.getByText('TSR3')).toBeInTheDocument();
      expect(screen.getByText('15 players (30%)')).toBeInTheDocument();
    });
  });

  test('renders champion cards with special styling', () => {
    mockUseLeaderboardData.mockReturnValue({
      leaderboardData: mockLeaderboardData,
      error: null,
      isLoading: false,
      isEmpty: false,
      refetch: vi.fn()
    });

    render(<ClubLeaderboard />);
    
    // All items in mock data have rank 1, so they should all be champions
    const rankBadges = screen.getAllByText('#1');
    expect(rankBadges.length).toBeGreaterThan(0);
  });

  test('renders footer with statistics', () => {
    mockUseLeaderboardData.mockReturnValue({
      leaderboardData: mockLeaderboardData,
      error: null,
      isLoading: false,
      isEmpty: false,
      refetch: vi.fn()
    });

    render(<ClubLeaderboard />);
    
    expect(screen.getByText('3 categories analyzed')).toBeInTheDocument();
    expect(screen.getByText('15 unique combinations')).toBeInTheDocument();
    expect(screen.getByText('Data from professional tours')).toBeInTheDocument();
  });

  test('handles brand URL clicks', async () => {
    // Mock window.open
    const mockOpen = vi.fn();
    vi.stubGlobal('open', mockOpen);

    mockUseLeaderboardData.mockReturnValue({
      leaderboardData: mockLeaderboardData,
      error: null,
      isLoading: false,
      isEmpty: false,
      refetch: vi.fn()
    });

    render(<ClubLeaderboard />);
    
    const driverTab = screen.getByRole('tab', { name: 'Driver' });
    await userEvent.click(driverTab);
    
    await waitFor(() => {
      const viewBrandButton = screen.getByRole('button', { name: /view brand/i });
      expect(viewBrandButton).toBeInTheDocument();
    });

    const viewBrandButton = screen.getByRole('button', { name: /view brand/i });
    await userEvent.click(viewBrandButton);
    
    expect(mockOpen).toHaveBeenCalledWith('https://titleist.com', '_blank');
    
    vi.unstubAllGlobals();
  });
});