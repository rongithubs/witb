import { render, screen, fireEvent } from '@testing-library/react'
import { WITBItemList } from '@/components/witb/WITBItemList'
import type { WITBItem } from '@/types/schemas'

const mockWITBItems: WITBItem[] = [
  {
    category: 'Driver',
    brand: 'TaylorMade',
    model: 'Stealth 2 Plus',
    loft: '9°',
    shaft: 'Mitsubishi Diamana D+ 60 TX',
    product_url: 'https://example.com/driver'
  },
  {
    category: 'Putter',
    brand: 'Scotty Cameron',
    model: 'GSS Newport 2',
    loft: '3°'
  }
]

// Mock window.open
const mockWindowOpen = jest.fn()
Object.defineProperty(window, 'open', {
  value: mockWindowOpen,
})

describe('WITBItemList', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders equipment items correctly on mobile view', () => {
    render(<WITBItemList items={mockWITBItems} />)

    // Check that items are rendered
    expect(screen.getByText('Driver')).toBeInTheDocument()
    expect(screen.getByText('TaylorMade')).toBeInTheDocument()
    expect(screen.getByText('Stealth 2 Plus')).toBeInTheDocument()
    expect(screen.getByText('9°')).toBeInTheDocument()
    
    expect(screen.getByText('Putter')).toBeInTheDocument()
    expect(screen.getByText('Scotty Cameron')).toBeInTheDocument()
    expect(screen.getByText('GSS Newport 2')).toBeInTheDocument()
  })

  test('renders desktop table view', () => {
    render(<WITBItemList items={mockWITBItems} />)

    // Check table headers
    expect(screen.getByText('Club')).toBeInTheDocument()
    expect(screen.getByText('Brand')).toBeInTheDocument()
    expect(screen.getByText('Model')).toBeInTheDocument()
    expect(screen.getByText('Loft/Grind')).toBeInTheDocument()
    expect(screen.getByText('Shaft')).toBeInTheDocument()
    expect(screen.getByText('Action')).toBeInTheDocument()
  })

  test('shows product links when available', () => {
    render(<WITBItemList items={mockWITBItems} />)

    const viewProductButtons = screen.getAllByText('View Product')
    expect(viewProductButtons).toHaveLength(1)

    const viewButtons = screen.getAllByText('View')
    expect(viewButtons).toHaveLength(1)
  })

  test('opens product URL when view button is clicked', () => {
    render(<WITBItemList items={mockWITBItems} />)

    const viewProductButton = screen.getByText('View Product')
    fireEvent.click(viewProductButton)

    expect(mockWindowOpen).toHaveBeenCalledWith('https://example.com/driver', '_blank')
  })

  test('shows empty state when no items provided', () => {
    render(<WITBItemList items={[]} />)

    expect(screen.getByText('⛳')).toBeInTheDocument()
    expect(screen.getByText('No equipment data available')).toBeInTheDocument()
  })

  test('displays shaft information when available', () => {
    render(<WITBItemList items={mockWITBItems} />)

    expect(screen.getByText('Shaft:')).toBeInTheDocument()
    expect(screen.getByText('Mitsubishi Diamana D+ 60 TX')).toBeInTheDocument()
  })

  test('handles items without optional fields', () => {
    const itemsWithoutOptionalFields: WITBItem[] = [
      {
        category: 'Iron',
        brand: 'Titleist',
        model: 'T100'
      }
    ]

    render(<WITBItemList items={itemsWithoutOptionalFields} />)

    expect(screen.getByText('Iron')).toBeInTheDocument()
    expect(screen.getByText('Titleist')).toBeInTheDocument()
    expect(screen.getByText('T100')).toBeInTheDocument()
    
    // Should show dash for missing fields in table
    const dashElements = screen.getAllByText('-')
    expect(dashElements.length).toBeGreaterThan(0)
  })
})