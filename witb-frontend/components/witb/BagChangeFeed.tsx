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

// Reserved status tokens, never the brand accent — each pill also carries an
// icon and a text headline, so state is never encoded by colour alone.
const CHANGE_ACCENT: Record<ChangeType, string> = {
  added: "bg-status-good-surface text-status-good",
  removed: "bg-status-critical-surface text-status-critical",
  switched: "bg-status-info-surface text-status-info",
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
        <p className="text-sm font-medium text-ink">
          {headline}
        </p>
        {detail && (
          <p className="truncate text-sm text-ink-secondary">
            {detail}
          </p>
        )}
      </div>
      <time
        dateTime={change.detected_at}
        className="flex-shrink-0 text-xs text-ink-muted"
      >
        {formatRelativeTime(change.detected_at)}
      </time>
    </li>
  );
}

const cardClasses =
  "bg-surface rounded-lg shadow-sm border border-hairline p-6";

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
              <div className="h-8 w-8 flex-shrink-0 rounded-full bg-skeleton" />
              <div className="flex-1 space-y-2">
                <div className="h-3 w-1/2 rounded-md bg-skeleton" />
                <div className="h-3 w-2/3 rounded-md bg-skeleton" />
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
          <h3 className="mb-2 text-lg font-semibold text-status-critical">
            Failed to load recent changes
          </h3>
          <p className="mb-4 text-sm text-ink-secondary">
            {error.message || "Network error occurred"}
          </p>
          <button
            onClick={() => refetch()}
            className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
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
        <h2 className="mb-1 text-lg font-semibold text-ink">
          Recent Equipment Changes
        </h2>
        <p className="text-sm text-ink-muted">
          No equipment changes yet. Check back after the next weekly update.
        </p>
      </div>
    );
  }

  return (
    <div className={cardClasses}>
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-ink">
          Recent Equipment Changes
        </h2>
        {showViewAll && (
          <Link
            href="/changes"
            className="text-sm font-medium text-brand-strong hover:opacity-80"
          >
            View all
          </Link>
        )}
      </div>
      <ul className="divide-y divide-hairline">
        {changes.map((change) => (
          <ChangeRow key={change.id} change={change} />
        ))}
      </ul>
    </div>
  );
}
