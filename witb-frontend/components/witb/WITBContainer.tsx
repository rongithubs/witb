'use client'

import { useState } from 'react'
import type { WITBItem } from '@/types/schemas'
import { WITBItemList } from './WITBItemList'
import { WITBExpansionControls } from './WITBExpansionControls'

interface WITBContainerProps {
  items: WITBItem[]
  playerName: string
  variant?: 'card' | 'table'
  initialExpanded?: boolean
  onExpansionChange?: (expanded: boolean) => void
}

export function WITBContainer({ 
  items, 
  playerName, 
  variant = 'card', 
  initialExpanded = false,
  onExpansionChange 
}: WITBContainerProps) {
  const [isExpanded, setIsExpanded] = useState(initialExpanded)

  const toggleExpansion = () => {
    const newExpanded = !isExpanded
    setIsExpanded(newExpanded)
    onExpansionChange?.(newExpanded)
  }

  if (variant === 'card') {
    return (
      <div className="space-y-4">
        {/* Header with expansion controls */}
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Equipment Bag
          </h4>
          <WITBExpansionControls 
            isExpanded={isExpanded}
            onToggle={toggleExpansion}
            variant="mobile"
            playerName={playerName}
          />
        </div>
        
        {/* Expandable content */}
        <div 
          className={`transition-all duration-500 ease-in-out overflow-hidden ${
            isExpanded 
              ? 'max-h-[3000px] opacity-100' 
              : 'max-h-0 opacity-0'
          }`}
        >
          <div className="bg-gray-50 dark:bg-gray-900/30 rounded-lg border border-gray-200 dark:border-gray-700">
            <div 
              className={`p-4 transition-all duration-300 delay-200 ${
                isExpanded ? 'translate-y-0' : 'translate-y-4'
              }`}
            >
              <h5 className="text-base font-semibold text-gray-900 dark:text-white mb-4">
                Complete WITB - {playerName}
              </h5>
              <WITBItemList 
                items={items} 
                playerName={playerName}
                isExpanded={isExpanded}
              />
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Table variant (for PlayerTable compatibility)
  return (
    <div 
      className={`transition-all duration-500 ease-in-out overflow-hidden ${
        isExpanded 
          ? 'max-h-[3000px] opacity-100' 
          : 'max-h-0 opacity-0'
      }`}
    >
      <div className="bg-gray-50 dark:bg-gray-900/30 border-t border-gray-200 dark:border-gray-700">
        <div 
          className={`p-4 md:p-6 transition-all duration-300 delay-200 ${
            isExpanded ? 'translate-y-0' : 'translate-y-4'
          }`}
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Complete WITB - {playerName}
          </h3>
          <WITBItemList 
            items={items} 
            playerName={playerName}
            isExpanded={isExpanded}
          />
        </div>
      </div>
    </div>
  )
}