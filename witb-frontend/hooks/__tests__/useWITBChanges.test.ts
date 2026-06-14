import { describe, expect, test, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import useSWR from "swr";
import { useWITBChanges } from "../useWITBChanges";
import type { BagChangesResponse } from "@/types/schemas";

vi.mock("swr", () => ({
  default: vi.fn(),
}));

vi.mock("@/lib/fetcher", () => ({
  fetcher: vi.fn(),
}));

describe("useWITBChanges", () => {
  const mockSWR = vi.mocked(useSWR);

  test("exposes changes array and not-empty when data is present", () => {
    const mockData: BagChangesResponse = {
      changes: [
        {
          id: "c1",
          player_id: "p1",
          player_name: "Rory McIlroy",
          category: "Driver",
          change_type: "switched",
          detected_at: "2026-06-13T00:00:00Z",
        },
      ],
      total: 1,
    };

    mockSWR.mockReturnValue({
      data: mockData,
      error: null,
      isLoading: false,
      isValidating: false,
      mutate: vi.fn(),
    });

    const { result } = renderHook(() => useWITBChanges());

    expect(result.current.changes).toEqual(mockData.changes);
    expect(result.current.isEmpty).toBe(false);
    expect(result.current.error).toBeNull();
  });

  test("reports empty when the feed has no changes", () => {
    mockSWR.mockReturnValue({
      data: { changes: [], total: 0 },
      error: null,
      isLoading: false,
      isValidating: false,
      mutate: vi.fn(),
    });

    const { result } = renderHook(() => useWITBChanges());

    expect(result.current.changes).toEqual([]);
    expect(result.current.isEmpty).toBe(true);
  });

  test("is not empty while still loading", () => {
    mockSWR.mockReturnValue({
      data: undefined,
      error: null,
      isLoading: true,
      isValidating: false,
      mutate: vi.fn(),
    });

    const { result } = renderHook(() => useWITBChanges());

    expect(result.current.isLoading).toBe(true);
    expect(result.current.isEmpty).toBe(false);
  });

  test("requests the changes endpoint with the given limit", () => {
    mockSWR.mockReturnValue({
      data: undefined,
      error: null,
      isLoading: false,
      isValidating: false,
      mutate: vi.fn(),
    });

    renderHook(() => useWITBChanges(5));

    expect(mockSWR).toHaveBeenCalledWith(
      "/witb/changes?limit=5",
      expect.any(Function),
    );
  });

  test("defaults to a limit of 50", () => {
    mockSWR.mockReturnValue({
      data: undefined,
      error: null,
      isLoading: false,
      isValidating: false,
      mutate: vi.fn(),
    });

    renderHook(() => useWITBChanges());

    expect(mockSWR).toHaveBeenCalledWith(
      "/witb/changes?limit=50",
      expect.any(Function),
    );
  });
});
