import React from 'react';
import { describe, expect, test, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PlayerTable } from '../PlayerTable';
import type { Player, WITBItem, PaginatedPlayersResponse } from '@/types/schemas';

// Mock all dependencies
vi.mock('@/hooks/useOWGRInfo', () => ({
  useOWGRInfo: vi.fn()
}));

vi.mock('@/providers/auth-provider', () => ({
  useAuth: vi.fn()
}));

vi.mock('@/providers/favorites-provider', () => ({
  useFavorites: vi.fn()
}));

vi.mock('@/hooks/usePlayerSearch', () => ({
  usePlayerSearch: vi.fn()
}));

describe('PlayerTable', async () => {
  const mockUseOWGRInfo = vi.mocked((await import('@/hooks/useOWGRInfo')).useOWGRInfo);
  const mockUseAuth = vi.mocked((await import('@/providers/auth-provider')).useAuth);  
  const mockUseFavorites = vi.mocked((await import('@/providers/favorites-provider')).useFavorites);

  // Test data following schema patterns
  const mockWITBItems: WITBItem[] = [
    {
      id: 'witb-1',
      category: 'Driver',
      brand: 'Titleist',
      model: 'TSR3',
      loft: '9.0°',
      shaft: 'Mitsubishi Tensei AV Raw White 65 TX',
      product_url: 'https://titleist.com/golf-clubs/drivers/tsr3'
    },
    {
      id: 'witb-2', 
      category: 'Putter',
      brand: 'Scotty Cameron',
      model: 'Newport 2',
      loft: '3.0°',
      shaft: null,
      product_url: 'https://scottycameron.com'
    }
  ];

  const mockPlayers: Player[] = [
    {
      id: 'player-1',
      name: 'Tiger Woods',
      country: 'USA',
      tour: 'OGWR',
      age: 48,
      ranking: 1,
      photo_url: 'https://example.com/tiger.jpg',
      last_updated: new Date('2024-01-15T10:30:00Z'),
      witb_items: mockWITBItems
    },
    {
      id: 'player-2',
      name: 'Rory McIlroy',
      country: 'NIR',
      tour: 'OGWR', 
      age: 34,
      ranking: 2,
      photo_url: 'https://example.com/rory.jpg',
      last_updated: new Date('2024-01-10T14:20:00Z'),
      witb_items: []
    }
  ];

  const mockPlayersResponse: PaginatedPlayersResponse = {
    items: mockPlayers,
    total: 2,
    page: 1,
    per_page: 10,
    total_pages: 1,
    system_info: {
      owgr_last_updated: new Date('2024-01-15T12:00:00Z'),
      owgr_updated_count: 50,
      owgr_total_processed: 50
    }
  };

  const defaultProps = {
    players: mockPlayers,
    isLoading: false,
    error: null,
    playersResponse: mockPlayersResponse,
    page: 1,
    onPageChange: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();

    // Default mock implementations
    mockUseOWGRInfo.mockReturnValue({
      owgrInfo: 'Last updated: Jan 15, 2024',
      formatLastUpdated: vi.fn((date: Date | null) => date?.toLocaleDateString() || 'Not updated')
    });

    mockUseAuth.mockReturnValue({
      user: { id: 'user-1', email: 'test@example.com' },
      session: { access_token: 'token' },
      loading: false,
      signInWithGoogle: vi.fn(),
      signOut: vi.fn()
    });

    mockUseFavorites.mockReturnValue({
      favorites: [],
      isLoading: false,
      error: null,
      addFavorite: vi.fn().mockResolvedValue(true),
      removeFavorite: vi.fn().mockResolvedValue(true),
      isFavorite: vi.fn().mockReturnValue(false),
      refreshFavorites: vi.fn()
    });
  });

  describe('toggleFavorite function logic', () => {
    test('calls addFavorite when player is not favorited', async () => {
      const mockAddFavorite = vi.fn().mockResolvedValue(true);
      const mockIsFavorite = vi.fn().mockReturnValue(false);
      
      mockUseFavorites.mockReturnValue({
        favorites: [],
        isLoading: false,
        error: null,
        addFavorite: mockAddFavorite,
        removeFavorite: vi.fn(),
        isFavorite: mockIsFavorite,
        refreshFavorites: vi.fn()
      });

      render(<PlayerTable {...defaultProps} />);
      
      const heartButtons = screen.getAllByTitle('Add to favorites');
      await userEvent.click(heartButtons[0]);

      await waitFor(() => {
        expect(mockAddFavorite).toHaveBeenCalledWith('player-1');
      });
    });

    test('calls removeFavorite when player is already favorited', async () => {
      const mockRemoveFavorite = vi.fn().mockResolvedValue(true);
      const mockIsFavorite = vi.fn().mockReturnValue(true);
      
      mockUseFavorites.mockReturnValue({
        favorites: [{ 
          id: 'fav-1', 
          player: mockPlayers[0], 
          created_at: new Date() 
        }],
        isLoading: false,
        error: null,
        addFavorite: vi.fn(),
        removeFavorite: mockRemoveFavorite,
        isFavorite: mockIsFavorite,
        refreshFavorites: vi.fn()
      });

      render(<PlayerTable {...defaultProps} />);
      
      const heartButtons = screen.getAllByTitle('Remove from favorites');
      await userEvent.click(heartButtons[0]);

      await waitFor(() => {
        expect(mockRemoveFavorite).toHaveBeenCalledWith('player-1');
      });
    });

    test('does nothing when user is not authenticated', async () => {
      const mockAddFavorite = vi.fn();
      
      mockUseAuth.mockReturnValue({
        user: null,
        session: null,
        loading: false,
        signInWithGoogle: vi.fn(),
        signOut: vi.fn()
      });

      mockUseFavorites.mockReturnValue({
        favorites: [],
        isLoading: false,
        error: null,
        addFavorite: mockAddFavorite,
        removeFavorite: vi.fn(),
        isFavorite: vi.fn().mockReturnValue(false),
        refreshFavorites: vi.fn()
      });

      render(<PlayerTable {...defaultProps} />);
      
      const heartButtons = screen.getAllByTitle('Sign in to add favorites');
      await userEvent.click(heartButtons[0]);

      // Should not call addFavorite when user is null
      expect(mockAddFavorite).not.toHaveBeenCalled();
    });

    test('handles loading state during toggle operation', async () => {
      const mockAddFavorite = vi.fn(() => 
        new Promise(resolve => setTimeout(() => resolve(true), 100))
      );
      
      mockUseFavorites.mockReturnValue({
        favorites: [],
        isLoading: false,
        error: null,
        addFavorite: mockAddFavorite,
        removeFavorite: vi.fn(),
        isFavorite: vi.fn().mockReturnValue(false),
        refreshFavorites: vi.fn()
      });

      render(<PlayerTable {...defaultProps} />);
      
      const heartButtons = screen.getAllByTitle('Add to favorites');
      const heartButton = heartButtons[0];
      
      // Button should be enabled initially
      expect(heartButton).not.toBeDisabled();
      
      // Click and check loading state
      await userEvent.click(heartButton);
      
      // Button should be disabled during operation
      expect(heartButton).toBeDisabled();
      
      // Wait for operation to complete
      await waitFor(() => {
        expect(heartButton).not.toBeDisabled();
      });
    });
  });

  describe('heart button rendering and interactions', () => {
    test('renders heart button with correct state for unfavorited player', () => {
      mockUseFavorites.mockReturnValue({
        favorites: [],
        isLoading: false,
        error: null,
        addFavorite: vi.fn(),
        removeFavorite: vi.fn(),
        isFavorite: vi.fn().mockReturnValue(false),
        refreshFavorites: vi.fn()
      });

      render(<PlayerTable {...defaultProps} />);
      
      // Check heart buttons exist and have correct titles
      const addToFavoriteButtons = screen.getAllByTitle('Add to favorites');
      expect(addToFavoriteButtons).toHaveLength(4); // 2 players × 2 views (desktop + mobile)
      
      // Check heart icons are not filled (unfavorited state)
      const heartIcons = document.querySelectorAll('svg[data-lucide="heart"]');
      heartIcons.forEach(icon => {
        expect(icon.classList.contains('fill-current')).toBe(false);
      });
    });

    test('renders heart button with correct state for favorited player', () => {
      mockUseFavorites.mockReturnValue({
        favorites: [{ 
          id: 'fav-1', 
          player: mockPlayers[0], 
          created_at: new Date() 
        }],
        isLoading: false,
        error: null,
        addFavorite: vi.fn(),
        removeFavorite: vi.fn(),
        isFavorite: vi.fn().mockReturnValue(true),
        refreshFavorites: vi.fn()
      });

      render(<PlayerTable {...defaultProps} />);
      
      // Check heart buttons show remove tooltip
      const removeFromFavoriteButtons = screen.getAllByTitle('Remove from favorites');
      expect(removeFromFavoriteButtons).toHaveLength(2); // Only for favorited player
      
      // Check other player still shows add tooltip
      const addToFavoriteButtons = screen.getAllByTitle('Add to favorites');
      expect(addToFavoriteButtons).toHaveLength(2); // Only for unfavorited player
    });

    test('shows sign in prompt when user not authenticated', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        session: null,
        loading: false,
        signInWithGoogle: vi.fn(),
        signOut: vi.fn()
      });

      render(<PlayerTable {...defaultProps} />);
      
      const signInButtons = screen.getAllByTitle('Sign in to add favorites');
      expect(signInButtons).toHaveLength(4); // 2 players × 2 views
      
      // All heart buttons should be disabled
      signInButtons.forEach((button: any) => {
        expect(button).toBeDisabled();
      });
    });

    test('both desktop and mobile heart buttons work identically', async () => {
      const mockAddFavorite = vi.fn().mockResolvedValue(true);
      
      mockUseFavorites.mockReturnValue({
        favorites: [],
        isLoading: false,
        error: null,
        addFavorite: mockAddFavorite,
        removeFavorite: vi.fn(),
        isFavorite: vi.fn().mockReturnValue(false),
        refreshFavorites: vi.fn()
      });

      render(<PlayerTable {...defaultProps} />);
      
      const heartButtons = screen.getAllByTitle('Add to favorites');
      
      // Click first heart button (should be desktop view)
      await userEvent.click(heartButtons[0]);
      
      await waitFor(() => {
        expect(mockAddFavorite).toHaveBeenCalledWith('player-1');
      });
      
      mockAddFavorite.mockClear();
      
      // Click third heart button (should be mobile view for same player)
      await userEvent.click(heartButtons[2]);
      
      await waitFor(() => {
        expect(mockAddFavorite).toHaveBeenCalledWith('player-1');
      });
    });
  });

  describe('edge cases and error handling', () => {
    test('handles error from favorites provider gracefully', async () => {
      const mockAddFavorite = vi.fn().mockRejectedValue(new Error('Network error'));
      
      mockUseFavorites.mockReturnValue({
        favorites: [],
        isLoading: false,
        error: null,
        addFavorite: mockAddFavorite,
        removeFavorite: vi.fn(),
        isFavorite: vi.fn().mockReturnValue(false),
        refreshFavorites: vi.fn()
      });

      render(<PlayerTable {...defaultProps} />);
      
      const heartButtons = screen.getAllByTitle('Add to favorites');
      
      // Click should not crash the component
      await userEvent.click(heartButtons[0]);
      
      await waitFor(() => {
        expect(mockAddFavorite).toHaveBeenCalled();
      });
      
      // Component should still be rendered
      expect(screen.getByText('Tiger Woods')).toBeInTheDocument();
    });

    test('handles rapid successive clicks without breaking state', async () => {
      let callCount = 0;
      const mockAddFavorite = vi.fn(() => {
        callCount++;
        return new Promise(resolve => 
          setTimeout(() => resolve(true), 50)
        );
      });
      
      mockUseFavorites.mockReturnValue({
        favorites: [],
        isLoading: false,
        error: null,
        addFavorite: mockAddFavorite,
        removeFavorite: vi.fn(),
        isFavorite: vi.fn().mockReturnValue(false),
        refreshFavorites: vi.fn()
      });

      render(<PlayerTable {...defaultProps} />);
      
      const heartButton = screen.getAllByTitle('Add to favorites')[0];
      
      // Rapid clicks
      await userEvent.click(heartButton);
      await userEvent.click(heartButton);
      await userEvent.click(heartButton);
      
      // Wait for all operations to complete
      await waitFor(() => {
        // Should be disabled during operations
        expect(heartButton).toBeDisabled();
      });
      
      // Wait for button to be re-enabled
      await waitFor(() => {
        expect(heartButton).not.toBeDisabled();
      });
      
      // Should have been called multiple times
      expect(callCount).toBeGreaterThan(1);
    });

    test('renders loading skeleton when isLoading prop is true', () => {
      render(<PlayerTable {...{ ...defaultProps, isLoading: true }} />);
      
      // Should show loading skeleton instead of player data
      const skeletons = document.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
      
      // Should not show player names
      expect(screen.queryByText('Tiger Woods')).not.toBeInTheDocument();
    });

    test('renders error state when error prop is provided', () => {
      const testError = new Error('Failed to load players');
      
      render(<PlayerTable {...{ ...defaultProps, error: testError }} />);
      
      // Should show error message
      expect(screen.getByText(/failed to load/i)).toBeInTheDocument();
      
      // Should not show player data
      expect(screen.queryByText('Tiger Woods')).not.toBeInTheDocument();
    });
  });

  describe('property-based tests for toggle idempotence', () => {
    const testCases = [
      { 
        playerName: 'Tiger Woods', 
        playerId: 'player-1',
        initiallyFavorited: false, 
        expectedFirstAction: 'add',
        expectedSecondAction: 'remove'
      },
      { 
        playerName: 'Rory McIlroy',
        playerId: 'player-2', 
        initiallyFavorited: true, 
        expectedFirstAction: 'remove',
        expectedSecondAction: 'add'
      },
    ];

    testCases.forEach(({ playerName, playerId, initiallyFavorited, expectedFirstAction, expectedSecondAction }) => {
      test(`toggle idempotence for ${playerName} (initially ${initiallyFavorited ? 'favorited' : 'unfavorited'})`, async () => {
        const mockAddFavorite = vi.fn().mockResolvedValue(true);
        const mockRemoveFavorite = vi.fn().mockResolvedValue(true);
        let isFavorited = initiallyFavorited;
        
        const mockIsFavorite = vi.fn(() => isFavorited);
        
        mockUseFavorites.mockReturnValue({
          favorites: initiallyFavorited ? [{ 
            id: 'fav-1', 
            player: mockPlayers.find(p => p.id === playerId)!, 
            created_at: new Date() 
          }] : [],
          isLoading: false,
          error: null,
          addFavorite: mockAddFavorite.mockImplementation(() => {
            isFavorited = true;
            return Promise.resolve(true);
          }),
          removeFavorite: mockRemoveFavorite.mockImplementation(() => {
            isFavorited = false;
            return Promise.resolve(true);
          }),
          isFavorite: mockIsFavorite,
          refreshFavorites: vi.fn()
        });

        render(<PlayerTable {...defaultProps} />);
        
        const initialTitle = initiallyFavorited ? 'Remove from favorites' : 'Add to favorites';
        const heartButton = screen.getAllByTitle(initialTitle)[0];
        
        // First click
        await userEvent.click(heartButton);
        
        await waitFor(() => {
          if (expectedFirstAction === 'add') {
            expect(mockAddFavorite).toHaveBeenCalledWith(playerId);
          } else {
            expect(mockRemoveFavorite).toHaveBeenCalledWith(playerId);
          }
        });
        
        // Re-render with updated state
        mockUseFavorites.mockReturnValue({
          favorites: !initiallyFavorited ? [{ 
            id: 'fav-1', 
            player: mockPlayers.find(p => p.id === playerId)!, 
            created_at: new Date() 
          }] : [],
          isLoading: false,
          error: null,
          addFavorite: mockAddFavorite,
          removeFavorite: mockRemoveFavorite,
          isFavorite: mockIsFavorite,
          refreshFavorites: vi.fn()
        });
        
        // Wait for state update and second click
        await waitFor(() => {
          const secondTitle = !initiallyFavorited ? 'Remove from favorites' : 'Add to favorites';
          const updatedButton = screen.getAllByTitle(secondTitle)[0];
          return userEvent.click(updatedButton);
        });
        
        // Verify second action
        await waitFor(() => {
          if (expectedSecondAction === 'add') {
            expect(mockAddFavorite).toHaveBeenCalledTimes(2);
          } else {
            expect(mockRemoveFavorite).toHaveBeenCalledTimes(1);
          }
        });
      });
    });
  });
});