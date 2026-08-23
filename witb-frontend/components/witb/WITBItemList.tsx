'use client'

import type { WITBItem } from '@/types/schemas'
import { Button } from '@/components/ui/button'

interface WITBItemListProps {
  items: WITBItem[]
  isExpanded?: boolean
  animationDelay?: number
}

export function WITBItemList({ items, isExpanded = true, animationDelay = 0 }: WITBItemListProps) {
  if (items.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-ink-muted text-3xl mb-2">⛳</div>
        <p className="text-ink-muted">No equipment data available</p>
      </div>
    )
  }

  return (
    <>
      {/* Mobile Equipment Grid */}
      <div className="md:hidden space-y-4">
        <div className="grid grid-cols-1 gap-4">
          {items.map((club, index) => (
            <div
              key={index}
              className="bg-surface rounded-lg border border-hairline p-5 shadow-sm hover:shadow-md transition-all duration-300"
              style={{
                animationDelay: `${(index * 75) + animationDelay}ms`,
                animation: isExpanded
                  ? "fadeInUp 0.5s ease-out forwards"
                  : "none",
              }}
            >
              {/* Club Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="inline-flex items-center px-3 py-1 bg-brand-subtle text-brand-strong rounded-full text-sm font-medium mb-2">
                    {club.category}
                  </div>
                  <h4 className="font-bold text-lg text-ink mb-1">
                    {club.brand}
                  </h4>
                  <p className="text-base text-ink-secondary font-medium">
                    {club.model}
                  </p>
                </div>
                
                {club.product_url && (
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => window.open(club.product_url, '_blank')}
                    className="flex-shrink-0 text-sm px-3 py-2 rounded-lg border-brand/30 text-brand-strong hover:bg-brand-subtle"
                  >
                    View Product
                  </Button>
                )}
              </div>

              {/* Specifications */}
              {(club.loft || club.shaft) && (
                <div className="space-y-3 pt-3 border-t border-hairline">
                  {club.loft && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-ink-secondary">Loft:</span>
                      <span className="text-sm font-semibold text-ink">{club.loft}</span>
                    </div>
                  )}
                  {club.shaft && (
                    <div className="flex items-start justify-between">
                      <span className="text-sm font-medium text-ink-secondary flex-shrink-0">Shaft:</span>
                      <span className="text-sm font-semibold text-ink text-right ml-2">{club.shaft}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Desktop Table Layout */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full">
          {/* Table Header */}
          <thead>
            <tr className="border-b border-hairline">
              <th className="text-left py-3 px-4 text-sm font-semibold text-ink-secondary">
                Club
              </th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-ink-secondary">
                Brand
              </th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-ink-secondary">
                Model
              </th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-ink-secondary">
                Loft/Grind
              </th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-ink-secondary">
                Shaft
              </th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-ink-secondary">
                Action
              </th>
            </tr>
          </thead>
          
          {/* Table Body */}
          <tbody className="divide-y divide-hairline">
            {items.map((club, index) => (
              <tr key={index} className="hover:bg-surface-hover">
                <td className="py-3 px-4 text-sm font-medium text-ink">
                  {club.category}
                </td>
                <td className="py-3 px-4 text-sm text-ink-secondary">
                  {club.brand}
                </td>
                <td className="py-3 px-4 text-sm text-ink font-medium">
                  {club.model}
                </td>
                <td className="py-3 px-4 text-sm text-ink-secondary">
                  {club.loft || '-'}
                </td>
                <td className="py-3 px-4 text-sm text-ink-secondary">
                  {club.shaft || '-'}
                </td>
                <td className="py-3 px-4">
                  {club.product_url ? (
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => window.open(club.product_url, '_blank')}
                      className="text-xs px-2 py-1 h-6"
                    >
                      View
                    </Button>
                  ) : (
                    <span className="text-xs text-ink-muted">-</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}