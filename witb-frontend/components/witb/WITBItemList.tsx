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
        <div className="text-gray-400 text-3xl mb-2">⛳</div>
        <p className="text-gray-500 dark:text-gray-400">No equipment data available</p>
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
              className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm hover:shadow-md transition-all duration-300"
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
                  <div className="inline-flex items-center px-3 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 rounded-full text-sm font-medium mb-2">
                    {club.category}
                  </div>
                  <h4 className="font-bold text-lg text-gray-900 dark:text-white mb-1">
                    {club.brand}
                  </h4>
                  <p className="text-base text-gray-700 dark:text-gray-300 font-medium">
                    {club.model}
                  </p>
                </div>
                
                {club.product_url && (
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => window.open(club.product_url, '_blank')}
                    className="flex-shrink-0 text-sm px-3 py-2 rounded-lg border-emerald-200 dark:border-emerald-700 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-50 dark:hover:bg-emerald-900/20"
                  >
                    View Product
                  </Button>
                )}
              </div>

              {/* Specifications */}
              {(club.loft || club.shaft) && (
                <div className="space-y-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                  {club.loft && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Loft:</span>
                      <span className="text-sm font-semibold text-gray-900 dark:text-white">{club.loft}</span>
                    </div>
                  )}
                  {club.shaft && (
                    <div className="flex items-start justify-between">
                      <span className="text-sm font-medium text-gray-600 dark:text-gray-400 flex-shrink-0">Shaft:</span>
                      <span className="text-sm font-semibold text-gray-900 dark:text-white text-right ml-2">{club.shaft}</span>
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
            <tr className="border-b border-gray-200 dark:border-gray-600">
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                Club
              </th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                Brand
              </th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                Model
              </th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                Loft/Grind
              </th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                Shaft
              </th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                Action
              </th>
            </tr>
          </thead>
          
          {/* Table Body */}
          <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
            {items.map((club, index) => (
              <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <td className="py-3 px-4 text-sm font-medium text-gray-900 dark:text-white">
                  {club.category}
                </td>
                <td className="py-3 px-4 text-sm text-gray-700 dark:text-gray-300">
                  {club.brand}
                </td>
                <td className="py-3 px-4 text-sm text-blue-600 dark:text-blue-400 font-medium">
                  {club.model}
                </td>
                <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                  {club.loft || '-'}
                </td>
                <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
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
                    <span className="text-xs text-gray-400">-</span>
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