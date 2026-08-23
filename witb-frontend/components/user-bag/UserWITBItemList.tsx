"use client";

import { useState } from "react";
import { UserWITBItem } from "@/types/schemas";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Edit2,
  Trash2,
  Target,
  Calendar,
  DollarSign,
  MoreVertical,
} from "lucide-react";
import { api } from "@/lib/api";
import { PriceButton } from "@/components/pricing/PriceButton";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface UserWITBItemListProps {
  items: UserWITBItem[];
  onUpdate: () => void;
}

interface UserWITBItemCardProps {
  item: UserWITBItem;
  onUpdate: () => void;
}

function UserWITBItemCard({ item, onUpdate }: UserWITBItemCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (
      !confirm("Are you sure you want to remove this equipment from your bag?")
    ) {
      return;
    }

    setIsDeleting(true);
    try {
      await api.delete(`/user-bag/${item.id}`);
      onUpdate();
    } catch (error) {
      console.error("Failed to delete equipment:", error);
      alert("Failed to remove equipment. Please try again.");
    } finally {
      setIsDeleting(false);
    }
  };

  const formatDate = (dateString: string) => {
    // Use UTC methods to avoid timezone hydration mismatches
    const date = new Date(dateString);
    const year = date.getUTCFullYear();
    const month = date.getUTCMonth() + 1;
    const day = date.getUTCDate();
    return `${month}/${day}/${year}`;
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "decimal",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      Driver:
        "bg-surface-subtle text-ink",
      Fairway:
        "bg-status-info-surface text-status-info",
      "5-Wood":
        "bg-status-info-surface text-status-info",
      Hybrid:
        "bg-status-good-surface text-status-good",
      Iron: "bg-surface-subtle text-ink",
      Wedge:
        "bg-surface-subtle text-ink",
      Putter:
        "bg-brand-subtle text-brand-strong",
      Ball: "bg-surface-subtle text-ink-secondary",
    };
    return (
      colors[category as keyof typeof colors] ||
      "bg-surface-subtle text-ink-secondary"
    );
  };

  return (
    <Card className="relative p-4 pr-16 hover:shadow-lg transition-all duration-200 hover:scale-[1.01] border-0 shadow-sm bg-surface/80 backdrop-blur-sm">
      {/* Top-Right Action Menu */}
      <div className="absolute top-3 right-3 z-10">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0 hover:bg-surface-hover rounded-full"
            >
              <MoreVertical className="h-3.5 w-3.5" />
              <span className="sr-only">Equipment options</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              onClick={() => {
                // TODO: Implement edit functionality
                alert("Edit functionality coming soon!");
              }}
              className="flex items-center gap-2"
            >
              <Edit2 className="h-4 w-4" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={handleDelete}
              disabled={isDeleting}
              className="flex items-center gap-2 text-status-critical focus:text-status-critical"
            >
              {isDeleting ? (
                <div className="h-4 w-4 animate-spin border border-favorite border-t-transparent rounded-full" />
              ) : (
                <Trash2 className="h-4 w-4" />
              )}
              {isDeleting ? "Deleting..." : "Delete"}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Main Content */}
      <div className="flex items-start gap-4">
        {/* Category Badge - Leftmost Position */}
        <div className="flex-shrink-0">
          <div
            className={`w-16 h-12 rounded-lg p-2 shadow-sm overflow-hidden flex items-center justify-center ${getCategoryColor(item.category)}`}
          >
            <span className="text-sm font-bold text-center whitespace-nowrap">
              {item.category}
            </span>
          </div>
        </div>

        {/* Equipment Details */}
        <div className="flex-1 min-w-0">
          {/* Header Row */}
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            {item.carry_distance && (
              <div className="inline-flex items-center gap-1 px-2 py-1 bg-brand-subtle rounded-md whitespace-nowrap overflow-hidden">
                <Target className="h-3 w-3 text-brand-strong flex-shrink-0" />
                <span className="text-xs font-medium text-brand-strong">
                  {item.carry_distance}y
                </span>
              </div>
            )}
          </div>

          {/* Equipment Name - Brand & Model */}
          <h4 className="font-semibold text-lg text-ink mb-1 truncate">
            {item.model}
          </h4>
          <p className="text-sm text-ink-secondary mb-3 truncate">
            by {item.brand}
          </p>

          {/* Specifications */}
          {(item.loft || item.shaft) && (
            <div className="flex flex-wrap gap-3 mb-3">
              {item.loft && (
                <div className="flex items-center gap-1 text-sm whitespace-nowrap">
                  <span className="text-ink-muted">
                    Loft:
                  </span>
                  <span className="font-medium text-ink">
                    {item.loft}
                  </span>
                </div>
              )}
              {item.shaft && (
                <div className="flex items-center gap-1 text-sm">
                  <span className="text-ink-muted whitespace-nowrap">
                    Shaft:
                  </span>
                  <span className="font-medium text-ink truncate max-w-[120px]">
                    {item.shaft}
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Notes */}
          {item.notes && (
            <p className="text-sm text-ink-secondary mb-3 line-clamp-2 italic">
              &ldquo;{item.notes}&rdquo;
            </p>
          )}

          {/* Bottom Row - Actions & Purchase Info */}
          <div className="flex items-center gap-4 flex-wrap">
            {/* eBay Pricing */}
            <PriceButton
              witbItem={{
                brand: item.brand,
                model: item.model,
                category: item.category,
              }}
              size="sm"
              className="text-xs"
            />

            {/* Purchase Info */}
            <div className="flex flex-wrap gap-3 text-xs text-ink-muted">
              {item.purchase_date && (
                <div className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  <span>{formatDate(item.purchase_date)}</span>
                </div>
              )}
              {item.purchase_price && (
                <div className="flex items-center gap-1">
                  <DollarSign className="h-3 w-3" />
                  <span className="font-medium">
                    {formatPrice(item.purchase_price)}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}

export function UserWITBItemList({ items, onUpdate }: UserWITBItemListProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      {items.map((item, index) => (
        <div
          key={item.id}
          className="animate-in slide-in-from-bottom-2 fade-in-0"
          style={{ animationDelay: `${index * 100}ms` }}
        >
          <UserWITBItemCard item={item} onUpdate={onUpdate} />
        </div>
      ))}
    </div>
  );
}
