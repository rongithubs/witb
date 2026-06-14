import type { BagChangeItem } from "@/types/schemas";

export type FormattedBagChange = {
  verb: string;
  headline: string;
  detail: string;
};

const equipmentLabel = (brand?: string, model?: string): string =>
  [brand, model].filter(Boolean).join(" ").trim();

/**
 * Turn a raw bag-change event into display strings for the timeline feed.
 * Keeps no React/DOM concerns so it can be unit-tested directly.
 */
export const formatBagChange = (change: BagChangeItem): FormattedBagChange => {
  const subject = change.player_name ?? "A player";
  const oldLabel = equipmentLabel(change.old_brand, change.old_model);
  const newLabel = equipmentLabel(change.new_brand, change.new_model);

  const detail =
    change.change_type === "switched"
      ? `${oldLabel} → ${newLabel}`
      : change.change_type === "removed"
        ? oldLabel
        : newLabel;

  return {
    verb: change.change_type,
    headline: `${subject} ${change.change_type} ${change.category}`,
    detail,
  };
};

const MINUTE = 60;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;
const WEEK = 7 * DAY;

/**
 * Compact relative time for the feed (e.g. "3d ago"); older than a week falls
 * back to a short absolute date. `now` is injectable for deterministic tests.
 */
export const formatRelativeTime = (
  iso: string,
  now: Date = new Date(),
): string => {
  const seconds = Math.floor((now.getTime() - new Date(iso).getTime()) / 1000);

  if (seconds < MINUTE) return "just now";
  if (seconds < HOUR) return `${Math.floor(seconds / MINUTE)}m ago`;
  if (seconds < DAY) return `${Math.floor(seconds / HOUR)}h ago`;
  if (seconds < WEEK) return `${Math.floor(seconds / DAY)}d ago`;

  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
};
