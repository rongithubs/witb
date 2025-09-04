import React from 'react';
import { describe, expect, test, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PriceButton } from '../PriceButton';
import type { WITBItem } from '@/types/schemas';

// Mock the custom hook
vi.mock('@/hooks/useEBayPricing', () => ({
  useEBayPricing: vi.fn(),
}));

// Mock PricingModal component  
vi.mock('../PricingModal', () => ({
  PricingModal: ({ isOpen, witbItem }: { isOpen: boolean; witbItem: WITBItem }) => (
    <div data-testid="pricing-modal">
      {isOpen && (
        <div>
          Modal open for {witbItem.brand} {witbItem.model}
        </div>
      )}
    </div>
  ),
}));

const mockUseEBayPricing = vi.mocked((await import('@/hooks/useEBayPricing')).useEBayPricing);

describe('PriceButton', () => {
  const mockWitbItem: WITBItem = {
    brand: 'TaylorMade',
    model: 'Qi10',
    category: 'Driver',
    loft: '9°',
    shaft: 'Stiff Flex',
  };

  const mockPriceSummary = {
    minPrice: 399.99,
    maxPrice: 599.99,
    averagePrice: 499.99,
    listingCount: 15,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders check price button when no data', () => {
    mockUseEBayPricing.mockReturnValue({
      priceSummary: null,
      searchResponse: null,
      searchResponse: null,
      isLoading: false,
      hasError: false,
      fetchPriceData: vi.fn(),
      reset: vi.fn(),
    });

    render(<PriceButton witbItem={mockWitbItem} />);

    expect(screen.getByRole('button')).toBeInTheDocument();
    expect(screen.getByText('Check Price')).toBeInTheDocument();
    expect(screen.getByTestId('pricing-modal')).toBeInTheDocument();
  });

  test('renders loading state', () => {
    mockUseEBayPricing.mockReturnValue({
      priceSummary: null,
      searchResponse: null,
      isLoading: true,
      hasError: false,
      fetchPriceData: vi.fn(),
      reset: vi.fn(),
    });

    render(<PriceButton witbItem={mockWitbItem} />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeDisabled();
  });

  test('renders error state', () => {
    mockUseEBayPricing.mockReturnValue({
      priceSummary: {
        minPrice: 0,
        maxPrice: 0,
        averagePrice: 0,
        listingCount: 0,
      },
      isLoading: false,
      hasError: true,
      fetchPriceData: vi.fn(),
      reset: vi.fn(),
    });

    render(<PriceButton witbItem={mockWitbItem} />);

    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByRole('button')).toHaveAttribute(
      'title',
      'Error loading prices - click to retry'
    );
  });

  test('renders price range when data available', () => {
    mockUseEBayPricing.mockReturnValue({
      priceSummary: mockPriceSummary,
      searchResponse: null,
      isLoading: false,
      hasError: false,
      fetchPriceData: vi.fn(),
      reset: vi.fn(),
    });

    render(<PriceButton witbItem={mockWitbItem} />);

    expect(screen.getByText('$400 - $600')).toBeInTheDocument();
  });

  test('renders single price when min equals max', () => {
    mockUseEBayPricing.mockReturnValue({
      priceSummary: {
        minPrice: 499.99,
        maxPrice: 499.99,
        averagePrice: 499.99,
        listingCount: 1,
      },
      isLoading: false,
      hasError: false,
      fetchPriceData: vi.fn(),
      reset: vi.fn(),
    });

    render(<PriceButton witbItem={mockWitbItem} />);

    expect(screen.getByText('$500')).toBeInTheDocument();
  });

  test('shows no data when listing count is zero', () => {
    mockUseEBayPricing.mockReturnValue({
      priceSummary: {
        minPrice: 0,
        maxPrice: 0,
        averagePrice: 0,
        listingCount: 0,
      },
      isLoading: false,
      hasError: false,
      fetchPriceData: vi.fn(),
      reset: vi.fn(),
    });

    render(<PriceButton witbItem={mockWitbItem} />);

    expect(screen.getByText('No Data')).toBeInTheDocument();
  });

  test('calls fetchPriceData and opens modal when clicked without data', async () => {
    const user = userEvent.setup();
    const mockFetchPriceData = vi.fn().mockResolvedValue(undefined);

    mockUseEBayPricing.mockReturnValue({
      priceSummary: null,
      searchResponse: null,
      isLoading: false,
      hasError: false,
      fetchPriceData: mockFetchPriceData,
      reset: vi.fn(),
    });

    render(<PriceButton witbItem={mockWitbItem} />);

    await user.click(screen.getByRole('button'));

    expect(mockFetchPriceData).toHaveBeenCalledOnce();
    
    // Modal should be open
    await waitFor(() => {
      expect(screen.getByText('Modal open for TaylorMade Qi10')).toBeInTheDocument();
    });
  });

  test('calls fetchPriceData and opens modal when clicked with error', async () => {
    const user = userEvent.setup();
    const mockFetchPriceData = vi.fn().mockResolvedValue(undefined);

    mockUseEBayPricing.mockReturnValue({
      priceSummary: null,
      searchResponse: null,
      isLoading: false,
      hasError: true,
      fetchPriceData: mockFetchPriceData,
      reset: vi.fn(),
    });

    render(<PriceButton witbItem={mockWitbItem} />);

    await user.click(screen.getByRole('button'));

    expect(mockFetchPriceData).toHaveBeenCalledOnce();
  });

  test('only opens modal when clicked with existing data', async () => {
    const user = userEvent.setup();
    const mockFetchPriceData = vi.fn();

    mockUseEBayPricing.mockReturnValue({
      priceSummary: mockPriceSummary,
      searchResponse: null,
      isLoading: false,
      hasError: false,
      fetchPriceData: mockFetchPriceData,
      reset: vi.fn(),
    });

    render(<PriceButton witbItem={mockWitbItem} />);

    await user.click(screen.getByRole('button'));

    // Should not fetch data when data already exists
    expect(mockFetchPriceData).not.toHaveBeenCalled();
    
    // Modal should be open
    await waitFor(() => {
      expect(screen.getByText('Modal open for TaylorMade Qi10')).toBeInTheDocument();
    });
  });

  test('does not fetch data when already loading', async () => {
    const user = userEvent.setup();
    const mockFetchPriceData = vi.fn();

    mockUseEBayPricing.mockReturnValue({
      priceSummary: null,
      searchResponse: null,
      isLoading: true,
      hasError: false,
      fetchPriceData: mockFetchPriceData,
      reset: vi.fn(),
    });

    render(<PriceButton witbItem={mockWitbItem} />);

    await user.click(screen.getByRole('button'));

    expect(mockFetchPriceData).not.toHaveBeenCalled();
  });

  test('applies correct variant and size classes', () => {
    mockUseEBayPricing.mockReturnValue({
      priceSummary: null,
      searchResponse: null,
      isLoading: false,
      hasError: false,
      fetchPriceData: vi.fn(),
      reset: vi.fn(),
    });

    render(
      <PriceButton
        witbItem={mockWitbItem}
        variant="default"
        size="lg"
        className="custom-class"
      />
    );

    const button = screen.getByRole('button');
    expect(button).toHaveClass('custom-class');
  });

  test('shows correct tooltip for different states', () => {
    // Normal state
    mockUseEBayPricing.mockReturnValue({
      priceSummary: null,
      searchResponse: null,
      isLoading: false,
      hasError: false,
      fetchPriceData: vi.fn(),
      reset: vi.fn(),
    });

    const { rerender } = render(<PriceButton witbItem={mockWitbItem} />);
    
    expect(screen.getByRole('button')).toHaveAttribute(
      'title',
      'Check current eBay prices for TaylorMade Qi10'
    );

    // Error state
    mockUseEBayPricing.mockReturnValue({
      priceSummary: null,
      searchResponse: null,
      isLoading: false,
      hasError: true,
      fetchPriceData: vi.fn(),
      reset: vi.fn(),
    });

    rerender(<PriceButton witbItem={mockWitbItem} />);

    expect(screen.getByRole('button')).toHaveAttribute(
      'title',
      'Error loading prices - click to retry'
    );
  });
});