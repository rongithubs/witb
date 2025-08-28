import { render, screen, fireEvent } from '@testing-library/react'
import { WITBContainer } from '@/components/witb/WITBContainer'
import type { WITBItem } from '@/types/schemas'

const mockWITBItems: WITBItem[] = [
  {
    category: 'Driver',
    brand: 'TaylorMade',
    model: 'Stealth 2 Plus',
    loft: '9°'
  }
]

describe('WITBContainer', () => {
  test('renders in card variant with expansion controls', () => {
    render(
      <WITBContainer 
        items={mockWITBItems} 
        playerName="Tiger Woods" 
        variant="card" 
      />
    )

    expect(screen.getByText('Equipment Bag')).toBeInTheDocument()
    expect(screen.getByText('View Full Bag')).toBeInTheDocument()
  })

  test('renders in table variant', () => {
    render(
      <WITBContainer 
        items={mockWITBItems} 
        playerName="Tiger Woods" 
        variant="table" 
        initialExpanded={true}
      />
    )

    expect(screen.getByText('Complete WITB - Tiger Woods')).toBeInTheDocument()
  })

  test('handles expansion toggle in card variant', () => {
    const mockOnExpansionChange = jest.fn()
    
    render(
      <WITBContainer 
        items={mockWITBItems} 
        playerName="Tiger Woods" 
        variant="card"
        onExpansionChange={mockOnExpansionChange}
      />
    )

    const expandButton = screen.getByText('View Full Bag')
    fireEvent.click(expandButton)

    expect(mockOnExpansionChange).toHaveBeenCalledWith(true)
    expect(screen.getByText('Hide Full Bag')).toBeInTheDocument()
  })

  test('shows expanded content when initialExpanded is true', () => {
    render(
      <WITBContainer 
        items={mockWITBItems} 
        playerName="Tiger Woods" 
        variant="card"
        initialExpanded={true}
      />
    )

    expect(screen.getByText('Complete WITB - Tiger Woods')).toBeInTheDocument()
    expect(screen.getByText('Driver')).toBeInTheDocument()
  })

  test('starts collapsed when initialExpanded is false', () => {
    render(
      <WITBContainer 
        items={mockWITBItems} 
        playerName="Tiger Woods" 
        variant="card"
        initialExpanded={false}
      />
    )

    expect(screen.getByText('View Full Bag')).toBeInTheDocument()
    expect(screen.queryByText('Complete WITB - Tiger Woods')).not.toBeInTheDocument()
  })
})