import { describe, expect, test } from "vitest";
import { formatBagChange, formatRelativeTime } from "../bag-change-format";
import type { BagChangeItem } from "@/types/schemas";

const baseChange: BagChangeItem = {
  id: "c1",
  player_id: "p1",
  player_name: "Rory McIlroy",
  category: "Driver",
  change_type: "switched",
  detected_at: "2026-06-13T00:00:00Z",
};

describe("formatBagChange", () => {
  test("switched renders old → new transition with player and category", () => {
    const change: BagChangeItem = {
      ...baseChange,
      change_type: "switched",
      old_brand: "TaylorMade",
      old_model: "Stealth 2",
      new_brand: "TaylorMade",
      new_model: "Qi10",
    };

    expect(formatBagChange(change)).toEqual({
      verb: "switched",
      headline: "Rory McIlroy switched Driver",
      detail: "TaylorMade Stealth 2 → TaylorMade Qi10",
    });
  });

  test("added renders only the new equipment", () => {
    const change: BagChangeItem = {
      ...baseChange,
      category: "Wedge",
      change_type: "added",
      new_brand: "Titleist",
      new_model: "Vokey SM10",
    };

    expect(formatBagChange(change)).toEqual({
      verb: "added",
      headline: "Rory McIlroy added Wedge",
      detail: "Titleist Vokey SM10",
    });
  });

  test("removed renders only the old equipment", () => {
    const change: BagChangeItem = {
      ...baseChange,
      category: "Iron",
      change_type: "removed",
      old_brand: "Titleist",
      old_model: "T100",
    };

    expect(formatBagChange(change)).toEqual({
      verb: "removed",
      headline: "Rory McIlroy removed Iron",
      detail: "Titleist T100",
    });
  });

  test("missing player_name falls back to a generic subject", () => {
    const change: BagChangeItem = {
      ...baseChange,
      player_name: undefined,
      change_type: "added",
      new_brand: "Ping",
      new_model: "G430",
    };

    expect(formatBagChange(change).headline).toBe("A player added Driver");
  });

  test("missing brand or model omits the gap rather than printing 'undefined'", () => {
    const change: BagChangeItem = {
      ...baseChange,
      change_type: "added",
      new_brand: undefined,
      new_model: "Newport 2",
    };

    expect(formatBagChange(change).detail).toBe("Newport 2");
  });
});

describe("formatRelativeTime", () => {
  const now = new Date("2026-06-13T12:00:00Z");

  test.each([
    ["2026-06-13T11:59:30Z", "just now"],
    ["2026-06-13T11:45:00Z", "15m ago"],
    ["2026-06-13T09:00:00Z", "3h ago"],
    ["2026-06-10T12:00:00Z", "3d ago"],
  ])("%s relative to fixed now is %s", (iso, expected) => {
    expect(formatRelativeTime(iso, now)).toBe(expected);
  });

  test("older than a week falls back to an absolute short date", () => {
    expect(formatRelativeTime("2026-05-01T12:00:00Z", now)).not.toMatch(/ago/);
  });
});
