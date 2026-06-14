"use client";

import Link from "next/link";
import { ArrowLeftRight, Minus, Plus } from "lucide-react";
import { useWITBChanges } from "@/hooks/useWITBChanges";
import { formatBagChange, formatRelativeTime } from "@/lib/bag-change-format";
import type { BagChangeItem, ChangeType } from "@/types/schemas";

type BagChangeFeedProps = {
  limit?: number;
  showViewAll?: boolean;
};

const CHANGE_ICON: Record<ChangeType, typeof Plus> = {
  added: Plus,
  removed: Minus,
  switched: ArrowLeftRight,
};

const CHANGE_ACCENT: Record<ChangeType, string> = {
  added:
    "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300",
  removed: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  switched: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
};

function ChangeRow({ change }: { change: BagChangeItem }) {
  const { headline, detail } = formatBagChange(change);
  const Icon = CHANGE_ICON[change.change_type];

  return (
    <li className="flex gap-3 py-3">
      <span
        className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full ${CHANGE_ACCENT[change.change_type]}`}
      >
        <Icon className="h-4 w-4" />
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-gray-900 dark:text-white">
          {headline}
        </p>
        {detail && (
          <p className="truncate text-sm text-gray-600 dark:text-gray-400">
            {detail}
          </p>
        )}
      </div>
      <time
        dateTime={change.detected_at}
        className="flex-shrink-0 text-xs text-gray-400 dark:text-gray-500"
      >
        {formatRelativeTime(change.detected_at)}
      </time>
    </li>
  );
}

const cardClasses =
  "bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6";

export function BagChangeFeed({
  limit = 50,
  showViewAll = false,
}: BagChangeFeedProps) {
  const { changes, error, isLoading, isEmpty, refetch } = useWITBChanges(limit);

  if (isLoading) {
    return (
      <div className={cardClasses} role="status" aria-label="Loading changes">
        <div className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex animate-pulse gap-3">
              <div className="h-8 w-8 flex-shrink-0 rounded-full bg-gray-200 dark:bg-gray-700" />
              <div className="flex-1 space-y-2">
                <div className="h-3 w-1/2 rounded bg-gray-200 dark:bg-gray-700" />
                <div className="h-3 w-2/3 rounded bg-gray-200 dark:bg-gray-700" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={cardClasses}>
        <div className="text-center">
          <h3 className="mb-2 text-lg font-semibold text-red-600 dark:text-red-400">
            Failed to load recent changes
          </h3>
          <p className="mb-4 text-sm text-gray-600 dark:text-gray-400">
            {error.message || "Network error occurred"}
          </p>
          <button
            onClick={() => refetch()}
            className="rounded-md bg-gray-900 px-4 py-2 text-sm text-white hover:bg-gray-800"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div className={cardClasses}>
        <h2 className="mb-1 text-lg font-semibold text-gray-900 dark:text-white">
          Recent Equipment Changes
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          No equipment changes yet. Check back after the next weekly update.
        </p>
      </div>
    );
  }

  return (
    <div className={cardClasses}>
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Recent Equipment Changes
        </h2>
        {showViewAll && (
          <Link
            href="/changes"
            className="text-sm font-medium text-emerald-600 hover:text-emerald-700 dark:text-emerald-400"
          >
            View all
          </Link>
        )}
      </div>
      <ul className="divide-y divide-gray-100 dark:divide-gray-700">
        {changes.map((change) => (
          <ChangeRow key={change.id} change={change} />
        ))}
      </ul>
    </div>
  );
}
