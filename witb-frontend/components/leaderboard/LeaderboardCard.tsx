import { Button } from "@/components/ui/button";
import { ExternalLinkIcon } from "lucide-react";
import { isChampionItem } from "@/lib/leaderboard-utils";
import { BrandLogo } from "@/components/ui/BrandLogo";
import { ClubImage } from "@/components/ui/ClubImage";
import type { ClubUsageItem } from "@/hooks/useLeaderboardData";

interface LeaderboardCardProps {
  item: ClubUsageItem & { category?: string };
  index: number;
}

export function LeaderboardCard({ item, index }: LeaderboardCardProps) {
  const isChampion = isChampionItem(item);

  return (
    <div
      className={`bg-surface rounded-lg border border-hairline shadow-sm transition-colors hover:bg-surface-hover ${
        isChampion ? "overflow-hidden ring-1 ring-brand/40" : "p-3"
      }`}
      style={{
        animationDelay: `${index * 50}ms`,
        animation: "fadeInUp 0.6s ease-out forwards",
      }}
    >
      {isChampion ? (
        <div className="bg-surface-subtle p-4">
          <div className="mb-3 flex items-start gap-3">
            <span className="flex h-12 w-12 items-center justify-center rounded-md bg-surface text-lg font-bold text-ink">
              #{item.rank}
            </span>
            <span className="flex h-12 flex-col justify-center text-sm font-semibold uppercase tracking-wide text-brand-strong">
              <span className="whitespace-nowrap">Most Played</span>
              <span className="whitespace-nowrap">{item.category}</span>
            </span>
          </div>

          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0 flex-1">
              <BrandLogo
                brandName={item.brand}
                width={600}
                height={120}
                fallbackClassName="text-4xl font-bold text-ink"
                className="mb-1 h-auto max-w-full object-contain"
              />
              <p className="mb-3 text-lg font-semibold text-ink">
                {item.model}
              </p>
              <p className="text-sm text-ink-secondary">
                Trusted by {item.percentage}% of Tour Players
              </p>
            </div>

            <div className="flex w-2/5 flex-shrink-0 items-center justify-center">
              <ClubImage
                brandName={item.brand}
                modelName={item.model}
                category={item.category}
                width={540}
                height={540}
                className="max-h-full max-w-full object-contain"
              />
            </div>
          </div>
        </div>
      ) : (
        <div className="mb-3 flex items-center gap-3">
          <span className="rounded-md bg-surface-subtle px-2 py-1 text-xs font-bold text-ink">
            #{item.rank}
          </span>
          <div className="flex-1">
            <div className="mb-1 flex items-center gap-3">
              <BrandLogo
                brandName={item.brand}
                width={80}
                height={32}
                fallbackClassName="font-bold text-lg leading-tight text-ink"
              />
              <ClubImage
                brandName={item.brand}
                modelName={item.model}
                category={item.category}
                width={40}
                height={40}
                className="flex-shrink-0"
              />
            </div>
            <p className="text-sm font-semibold text-ink">{item.model}</p>
          </div>
        </div>
      )}

      {/* Usage magnitude renders for every rank, champion included, so the
          percentages stay visually comparable across the whole leaderboard. */}
      <div className={isChampion ? "border-t border-hairline p-4" : ""}>
        <div className="mb-3">
          <div className="mb-1 flex items-center justify-between text-xs">
            <span className="text-ink-secondary">Usage</span>
            <span className="font-semibold text-ink">
              {item.count} players ({item.percentage}%)
            </span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-data-track">
            <div
              className="h-full rounded-full bg-data-magnitude transition-all duration-300"
              style={{ width: `${Math.min(item.percentage, 100)}%` }}
            />
          </div>
        </div>

        {item.brand_url && (
          <Button
            variant={isChampion ? "default" : "outline"}
            size="sm"
            className="w-full"
            onClick={() => window.open(item.brand_url, "_blank")}
          >
            <ExternalLinkIcon className="mr-1 h-3 w-3" />
            {isChampion ? "Shop Now" : "View Brand"}
          </Button>
        )}
      </div>
    </div>
  );
}
