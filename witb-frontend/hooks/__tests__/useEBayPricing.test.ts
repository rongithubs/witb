import { describe, expect, test, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useEBayPricing } from "../useEBayPricing";
import type { WITBItem } from "@/types/schemas";

// Mock the ebayApi
vi.mock("@/utils/ebayApi", () => ({
  ebayApi: {
    searchForWITBItem: vi.fn(),
  },
}));

const mockEBayApi = vi.mocked((await import("@/utils/ebayApi")).ebayApi);

describe("useEBayPricing", () => {
  const mockWitbItem: WITBItem = {
    brand: "TaylorMade",
    model: "Qi10",
    category: "Driver",
    loft: "9°",
    shaft: "Stiff Flex",
  };

  const mockPriceSummary = {
    minPrice: 399.99,
    maxPrice: 599.99,
    averagePrice: 499.99,
    listingCount: 15,
  };

  const mockSearchResponse = {
    products: [
      {
        product_id: "test-1",
        title: "TaylorMade Qi10 Driver",
        brand: "TaylorMade",
        model: "Qi10",
        category: "Driver",
        price_info: {
          current_price: 399.99,
          currency: "USD",
          condition: "New",
        },
        listing_url: "https://example.com/1",
        image_url: "https://example.com/image1.jpg",
        seller_info: {
          username: "seller1",
          feedback_percentage: 99.0,
          feedback_score: 1000,
        },
        location: "US",
        listing_type: "FixedPrice",
      },
      {
        product_id: "test-2",
        title: "TaylorMade Qi10 Driver Used",
        brand: "TaylorMade",
        model: "Qi10",
        category: "Driver",
        price_info: {
          current_price: 599.99,
          currency: "USD",
          condition: "Used",
        },
        listing_url: "https://example.com/2",
        image_url: "https://example.com/image2.jpg",
        seller_info: {
          username: "seller2",
          feedback_percentage: 98.5,
          feedback_score: 500,
        },
        location: "US",
        listing_type: "FixedPrice",
      },
    ],
    total_found: 2,
    search_params: {
      brand: "TaylorMade",
      model: "Qi10",
      category: "Driver",
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("initial state should be correct", () => {
    const { result } = renderHook(() => useEBayPricing(mockWitbItem));

    expect(result.current.priceSummary).toBeNull();
    expect(result.current.searchResponse).toBeNull();
    expect(result.current.isLoading).toBe(false);
    expect(result.current.hasError).toBe(false);
    expect(typeof result.current.fetchPriceData).toBe("function");
    expect(typeof result.current.reset).toBe("function");
  });

  test("fetchPriceData should fetch and set price summary successfully", async () => {
    mockEBayApi.searchForWITBItem.mockResolvedValueOnce(mockSearchResponse);

    const { result } = renderHook(() => useEBayPricing(mockWitbItem));

    await act(async () => {
      await result.current.fetchPriceData();
    });

    expect(mockEBayApi.searchForWITBItem).toHaveBeenCalledWith(
      "TaylorMade",
      "Qi10",
      "Driver",
    );
    expect(result.current.priceSummary).toEqual({
      minPrice: 399.99,
      maxPrice: 599.99,
      averagePrice: 500,
      listingCount: 2,
    });
    expect(result.current.searchResponse).toEqual(mockSearchResponse);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.hasError).toBe(false);
  });

  test("fetchPriceData should handle API errors", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});
    mockEBayApi.searchForWITBItem.mockRejectedValueOnce(new Error("API Error"));

    const { result } = renderHook(() => useEBayPricing(mockWitbItem));

    await act(async () => {
      await result.current.fetchPriceData();
    });

    expect(result.current.hasError).toBe(true);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.priceSummary).toEqual({
      minPrice: 0,
      maxPrice: 0,
      averagePrice: 0,
      listingCount: 0,
    });
    expect(result.current.searchResponse).toBeNull();
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      "Error fetching price data:",
      expect.any(Error),
    );

    consoleErrorSpy.mockRestore();
  });

  test("fetchPriceData should set loading state during API call", async () => {
    let resolvePromise: (value: any) => void;
    const delayedPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    mockEBayApi.searchForWITBItem.mockReturnValueOnce(delayedPromise);

    const { result } = renderHook(() => useEBayPricing(mockWitbItem));

    // Start the fetch without awaiting
    act(() => {
      result.current.fetchPriceData();
    });

    // Check loading state is true during fetch
    expect(result.current.isLoading).toBe(true);

    // Resolve the promise
    resolvePromise!(mockSearchResponse);

    // Wait for the promise to complete
    await act(async () => {
      await delayedPromise;
    });

    // Check loading state is false after fetch
    expect(result.current.isLoading).toBe(false);
  });

  test("reset should clear all state", async () => {
    mockEBayApi.searchForWITBItem.mockResolvedValueOnce(mockSearchResponse);

    const { result } = renderHook(() => useEBayPricing(mockWitbItem));

    // Fetch some data first to set state
    await act(async () => {
      await result.current.fetchPriceData();
    });

    // Verify state is set
    expect(result.current.priceSummary).toBeTruthy();
    expect(result.current.searchResponse).toEqual(mockSearchResponse);

    // Reset the state
    act(() => {
      result.current.reset();
    });

    expect(result.current.priceSummary).toBeNull();
    expect(result.current.searchResponse).toBeNull();
    expect(result.current.isLoading).toBe(false);
    expect(result.current.hasError).toBe(false);
  });

  test("should prevent concurrent requests", async () => {
    mockEBayApi.searchForWITBItem.mockImplementation(
      () =>
        new Promise((resolve) =>
          setTimeout(() => resolve(mockSearchResponse), 100),
        ),
    );

    const { result } = renderHook(() => useEBayPricing(mockWitbItem));

    // Start first request
    await act(async () => {
      result.current.fetchPriceData();
    });

    // Start second request while first is still loading
    await act(async () => {
      result.current.fetchPriceData();
    });

    // Wait for all requests to complete
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 150));
    });

    // Should only have been called once due to concurrent request prevention
    expect(mockEBayApi.searchForWITBItem).toHaveBeenCalledTimes(1);
  });

  test("should update when witbItem changes", async () => {
    mockEBayApi.searchForWITBItem.mockResolvedValue(mockSearchResponse);

    const { result, rerender } = renderHook(
      ({ witbItem }) => useEBayPricing(witbItem),
      {
        initialProps: { witbItem: mockWitbItem },
      },
    );

    await act(async () => {
      await result.current.fetchPriceData();
    });

    expect(mockEBayApi.searchForWITBItem).toHaveBeenCalledWith(
      "TaylorMade",
      "Qi10",
      "Driver",
    );

    // Change the WITB item
    const newWitbItem: WITBItem = {
      brand: "Titleist",
      model: "TSR3",
      category: "Driver",
    };

    rerender({ witbItem: newWitbItem });

    // Clear mock to verify new call
    mockEBayApi.searchForWITBItem.mockClear();
    mockEBayApi.searchForWITBItem.mockResolvedValue(mockSearchResponse);

    await act(async () => {
      await result.current.fetchPriceData();
    });

    expect(mockEBayApi.searchForWITBItem).toHaveBeenCalledWith(
      "Titleist",
      "TSR3",
      "Driver",
    );
  });

  test("calculatePriceSummary should handle empty product list", () => {
    // This tests the pure function logic extracted for better testability
    const { result } = renderHook(() => useEBayPricing(mockWitbItem));
    
    // Test empty case by mocking empty response
    mockEBayApi.searchForWITBItem.mockResolvedValueOnce({
      products: [],
      total_found: 0,
      search_params: { brand: "TaylorMade", model: "Qi10", category: "Driver" },
    });
    
    return act(async () => {
      await result.current.fetchPriceData();
    }).then(() => {
      expect(result.current.priceSummary).toEqual({
        minPrice: 0,
        maxPrice: 0,
        averagePrice: 0,
        listingCount: 0,
      });
    });
  });

  test("calculatePriceSummary should handle single product", () => {
    const singleProductResponse = {
      products: [mockSearchResponse.products[0]], // Just first product
      total_found: 1,
      search_params: { brand: "TaylorMade", model: "Qi10", category: "Driver" },
    };
    
    mockEBayApi.searchForWITBItem.mockResolvedValueOnce(singleProductResponse);
    const { result } = renderHook(() => useEBayPricing(mockWitbItem));
    
    return act(async () => {
      await result.current.fetchPriceData();
    }).then(() => {
      expect(result.current.priceSummary).toEqual({
        minPrice: 399.99,
        maxPrice: 399.99,
        averagePrice: 400, // Rounded
        listingCount: 1,
      });
    });
  });
});
