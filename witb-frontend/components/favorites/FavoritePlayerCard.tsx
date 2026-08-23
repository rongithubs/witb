'use client'

import { useState } from 'react'
import type { FavoritePlayer } from '@/types/schemas'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Heart } from 'lucide-react'
import { WITBContainer } from '@/components/witb/WITBContainer'

interface FavoritePlayerCardProps {
  favorite: FavoritePlayer
  onRemove: (playerId: string) => Promise<void>
  isRemoving?: boolean
  variant?: 'list' | 'bag'
}

export function FavoritePlayerCard({ 
  favorite, 
  onRemove, 
  isRemoving = false,
  variant = 'bag'
}: FavoritePlayerCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const { player } = favorite

  const handleRemove = async () => {
    await onRemove(player.id)
  }

  const getPrimaryBrand = (items: typeof player.witb_items) => {
    if (!items || items.length === 0) return 'N/A'
    
    // Count brand occurrences
    const brandCounts = items.reduce((acc, item) => {
      acc[item.brand] = (acc[item.brand] || 0) + 1
      return acc
    }, {} as Record<string, number>)
    
    // Return the most common brand
    return Object.keys(brandCounts).reduce((a, b) => 
      brandCounts[a] > brandCounts[b] ? a : b
    )
  }

  const getKeyClubs = (items: typeof player.witb_items) => {
    if (!items || items.length === 0) return []
    
    // Show key clubs: Driver, Putter, and one iron
    const keyCategories = ['Driver', 'Putter', 'Iron']
    return items.filter(item => keyCategories.includes(item.category)).slice(0, 3)
  }

  if (variant === 'list') {
    // Simple list view (existing design)
    return (
      <div className="flex items-center justify-between p-3 bg-surface-subtle rounded-lg">
        <div>
          <h4 className="font-medium">{player.name}</h4>
          <p className="text-sm text-ink-secondary">
            {player.country} • {player.tour}
            {player.ranking && ` • Rank #${player.ranking}`}
          </p>
          <p className="text-xs text-ink-muted">
            Added {new Date(favorite.created_at).toLocaleDateString()}
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRemove}
          disabled={isRemoving}
          className="text-status-critical hover:bg-status-critical-surface disabled:opacity-50"
        >
          {isRemoving ? 'Removing...' : 'Remove'}
        </Button>
      </div>
    )
  }

  // Enhanced bag view with expandable WITB
  return (
    <Card className="p-3 space-y-2 hover:shadow-md transition-shadow duration-200">
      {/* Player Header */}
      <div className="flex items-center gap-2">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand to-status-good-surface flex items-center justify-center text-white font-bold text-xs">
            {player.name.split(" ").map(n => n[0]).join("")}
          </div>
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <h3 className="font-bold text-base text-ink truncate">
              {player.name}
            </h3>
            {player.ranking && (
              <span className="flex-shrink-0 bg-brand-subtle text-brand-strong text-xs font-bold px-1.5 py-0.5 rounded-full">
                #{player.ranking}
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2 text-xs text-ink-secondary">
            <span>{player.country}</span>
            <span>•</span>
            <span>{player.tour}</span>
            <span>•</span>
            <span>{getPrimaryBrand(player.witb_items)}</span>
          </div>
        </div>

        <div className="flex-shrink-0">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRemove}
            disabled={isRemoving}
            className="text-favorite hover:text-favorite hover:bg-favorite-subtle disabled:opacity-50 h-6 w-6 p-0"
          >
            <Heart className="h-3 w-3 fill-current" />
          </Button>
        </div>
      </div>

      {/* Key Equipment Preview (when collapsed) */}
      {!isExpanded && player.witb_items.length > 0 && (
        <div className="flex items-center gap-1 text-xs text-ink-secondary">
          {getKeyClubs(player.witb_items).slice(0, 3).map((club, index) => (
            <span key={index} className="bg-surface-subtle px-2 py-1 rounded-md text-xs">
              {club.category}: {club.brand}
            </span>
          ))}
        </div>
      )}

      {/* Full Equipment Bag */}
      <WITBContainer
        items={player.witb_items}
        playerName={player.name}
        variant="card"
        initialExpanded={false}
        onExpansionChange={setIsExpanded}
      />
    </Card>
  )
}