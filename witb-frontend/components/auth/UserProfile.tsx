'use client'

import { useState } from 'react'
import { useAuth } from '@/providers/auth-provider'
import { useFavorites } from '@/providers/favorites-provider'
import { Card } from '@/components/ui/card'
import { Heart, Target, Plus } from 'lucide-react'
import { FavoritePlayerCard } from '@/components/favorites/FavoritePlayerCard'
import Link from 'next/link'

export function UserProfile() {
  const { user } = useAuth()
  const { favorites, isLoading: favoritesLoading, removeFavorite } = useFavorites()
  const [removingFavorites, setRemovingFavorites] = useState<Set<string>>(new Set())

  const handleRemoveFavorite = async (playerId: string) => {
    setRemovingFavorites(prev => new Set(prev).add(playerId))
    
    try {
      await removeFavorite(playerId)
    } finally {
      setRemovingFavorites(prev => {
        const newSet = new Set(prev)
        newSet.delete(playerId)
        return newSet
      })
    }
  }

  if (!user) {
    return (
      <div className="bg-status-info-surface border border-status-info/30 rounded-lg p-4">
        <p className="text-status-info">
          Sign in to see your profile and get personalized golf equipment recommendations!
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* My Bag Quick Link Card */}
      <Card className="p-6 bg-gradient-to-r from-brand to-status-good-surface border-brand/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Target className="h-5 w-5 text-brand-strong" />
            <div>
              <h3 className="text-lg font-semibold text-brand-strong">My Bag</h3>
              <p className="text-sm text-brand-strong">
                Track your golf equipment and performance
              </p>
            </div>
          </div>
          <Link href="/my-bag">
            <div className="flex items-center gap-2 bg-brand hover:bg-brand/90 text-white px-4 py-2 rounded-lg transition-colors">
              <Plus className="h-4 w-4" />
              <span className="text-sm font-medium">Manage Equipment</span>
            </div>
          </Link>
        </div>
      </Card>

      {/* Favorite Players Card */}
      <Card className="p-6">
        <div className="flex items-center gap-3 mb-6">
          <Heart className="h-5 w-5 text-favorite" />
          <h3 className="text-lg font-semibold">My Favorite Players</h3>
        </div>

        {favoritesLoading && (
          <div className="text-center py-8">
            <div className="animate-pulse">
              <div className="h-4 bg-skeleton rounded-md w-48 mx-auto mb-2"></div>
              <div className="h-3 bg-skeleton rounded-md w-32 mx-auto"></div>
            </div>
          </div>
        )}

        {!favoritesLoading && favorites.length === 0 && (
          <div className="text-center py-12">
            <div className="text-ink-muted text-4xl mb-4">⭐</div>
            <h4 className="text-lg font-medium text-ink mb-2">
              No Favorite Players Yet
            </h4>
            <p className="text-ink-muted">
              Browse players and add some to your favorites to see their complete equipment setups here!
            </p>
          </div>
        )}

        {!favoritesLoading && favorites.length > 0 && (
          <div className="space-y-2">
            {favorites.map((favorite) => (
              <FavoritePlayerCard
                key={favorite.id}
                favorite={favorite}
                onRemove={handleRemoveFavorite}
                isRemoving={removingFavorites.has(favorite.player.id)}
                variant="bag"
              />
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}