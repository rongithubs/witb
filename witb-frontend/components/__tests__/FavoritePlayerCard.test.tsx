import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { FavoritePlayerCard } from '@/components/favorites/FavoritePlayerCard'
import type { FavoritePlayer } from '@/types/schemas'

const mockFavorite: FavoritePlayer = {
  id: 'fav-1',
  created_at: '2025-01-01T00:00:00Z',
  player: {
    id: 'player-1',
    name: 'Tiger Woods',
    country: 'USA',
    tour: 'PGA Tour',
    ranking: 1,
    witb_items: [
      {
        category: 'Driver',
        brand: 'TaylorMade',
        model: 'Stealth 2 Plus',
        loft: '9°',
        shaft: 'Mitsubishi Diamana D+ 60 TX'
      },
      {
        category: 'Putter',
        brand: 'Scotty Cameron',
        model: 'GSS Newport 2',
        loft: '3°'
      }
    ]
  }
}

describe('FavoritePlayerCard', () => {
  const mockOnRemove = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders player information correctly in bag view', () => {
    render(
      <FavoritePlayerCard 
        favorite={mockFavorite} 
        onRemove={mockOnRemove} 
        variant="bag" 
      />
    )

    expect(screen.getByText('Tiger Woods')).toBeInTheDocument()
    expect(screen.getByText('#1')).toBeInTheDocument()
    expect(screen.getByText(/🌍 USA/)).toBeInTheDocument()
    expect(screen.getByText(/🏌️ PGA Tour/)).toBeInTheDocument()
    expect(screen.getByText(/Primary: TaylorMade/)).toBeInTheDocument()
  })

  test('renders player information correctly in list view', () => {
    render(
      <FavoritePlayerCard 
        favorite={mockFavorite} 
        onRemove={mockOnRemove} 
        variant="list" 
      />
    )

    expect(screen.getByText('Tiger Woods')).toBeInTheDocument()
    expect(screen.getByText('USA • PGA Tour • Rank #1')).toBeInTheDocument()
    expect(screen.getByText('Remove')).toBeInTheDocument()
  })

  test('shows key equipment preview when collapsed', () => {
    render(
      <FavoritePlayerCard 
        favorite={mockFavorite} 
        onRemove={mockOnRemove} 
        variant="bag" 
      />
    )

    expect(screen.getByText('Key Equipment')).toBeInTheDocument()
    expect(screen.getByText('Driver')).toBeInTheDocument()
    expect(screen.getByText('TaylorMade Stealth 2 Plus')).toBeInTheDocument()
  })

  test('calls onRemove when remove button is clicked', async () => {
    render(
      <FavoritePlayerCard 
        favorite={mockFavorite} 
        onRemove={mockOnRemove} 
        variant="list" 
      />
    )

    const removeButton = screen.getByText('Remove')
    fireEvent.click(removeButton)

    await waitFor(() => {
      expect(mockOnRemove).toHaveBeenCalledWith('player-1')
    })
  })

  test('shows removing state when isRemoving is true', () => {
    render(
      <FavoritePlayerCard 
        favorite={mockFavorite} 
        onRemove={mockOnRemove} 
        isRemoving={true}
        variant="list" 
      />
    )

    expect(screen.getByText('Removing...')).toBeInTheDocument()
    expect(screen.getByRole('button')).toBeDisabled()
  })

  test('displays equipment count in bag view', () => {
    render(
      <FavoritePlayerCard 
        favorite={mockFavorite} 
        onRemove={mockOnRemove} 
        variant="bag" 
      />
    )

    expect(screen.getByText('2 clubs in bag')).toBeInTheDocument()
  })

  test('handles player with no equipment data', () => {
    const favoriteWithNoEquipment: FavoritePlayer = {
      ...mockFavorite,
      player: {
        ...mockFavorite.player,
        witb_items: []
      }
    }

    render(
      <FavoritePlayerCard 
        favorite={favoriteWithNoEquipment} 
        onRemove={mockOnRemove} 
        variant="bag" 
      />
    )

    expect(screen.getByText('Primary: N/A')).toBeInTheDocument()
    expect(screen.getByText('No equipment data available')).toBeInTheDocument()
  })
})