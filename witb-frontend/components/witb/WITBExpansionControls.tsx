'use client'

import { Button } from '@/components/ui/button'
import { ChevronDownIcon, ChevronUpIcon } from 'lucide-react'

interface WITBExpansionControlsProps {
  isExpanded: boolean
  onToggle: () => void
  variant?: 'mobile' | 'desktop'
}

export function WITBExpansionControls({ 
  isExpanded, 
  onToggle, 
  variant = 'desktop'
}: WITBExpansionControlsProps) {
  if (variant === 'mobile') {
    return (
      <Button
        onClick={onToggle}
        variant="default"
        size="sm"
        className="bg-emerald-600 hover:bg-emerald-700 text-white text-sm px-4 py-2 h-9 rounded-lg font-medium shadow-sm transition-all duration-200"
      >
        <span className="mr-2">
          {isExpanded ? "Hide" : "View"} Full Bag
        </span>
        {isExpanded ? (
          <ChevronUpIcon className="h-4 w-4" />
        ) : (
          <ChevronDownIcon className="h-4 w-4" />
        )}
      </Button>
    )
  }

  return (
    <Button 
      onClick={onToggle}
      variant="ghost" 
      size="sm"
      className="text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 text-sm px-2 py-1 h-8 rounded-md transition-all duration-200"
    >
      <span className="mr-1">View WITB</span>
      {isExpanded ? (
        <ChevronUpIcon className="h-3 w-3" />
      ) : (
        <ChevronDownIcon className="h-3 w-3" />
      )}
    </Button>
  )
}