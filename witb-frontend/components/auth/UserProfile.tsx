'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@/providers/auth-provider'
import { useFavorites } from '@/providers/favorites-provider'
import { authApi } from '@/lib/api'
import { User } from '@/types/schemas'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Heart, User as UserIcon } from 'lucide-react'

export function UserProfile() {
  const { user, session } = useAuth()
  const { favorites, isLoading: favoritesLoading, error: favoritesError, removeFavorite } = useFavorites()
  const [backendUser, setBackendUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)
  const [removingFavorites, setRemovingFavorites] = useState<Set<string>>(new Set())
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (session) {
      fetchBackendUser()
    }
  }, [session])

  const fetchBackendUser = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const { data, error } = await authApi.getCurrentUser()
      
      if (error) {
        setError(error)
      } else {
        setBackendUser(data as User)
      }
    } catch (err) {
      setError('Failed to fetch user data')
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveFavorite = async (playerId: string) => {
    setRemovingFavorites(prev => new Set(prev).add(playerId))
    
    try {
      const success = await removeFavorite(playerId)
      if (!success && favoritesError) {
        setError(favoritesError)
      }
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
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <p className="text-blue-800 dark:text-blue-200">
          Sign in to see your profile and get personalized golf equipment recommendations!
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* User Info Card */}
      <Card className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 p-4">
        <div className="flex items-center gap-3 mb-3">
          <UserIcon className="h-5 w-5 text-green-600" />
          <h3 className="text-lg font-semibold text-green-800 dark:text-green-200">
            Welcome to WITB! 🏌️‍♂️
          </h3>
        </div>
        
        <div className="space-y-2 text-sm">
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Provider:</strong> {user.app_metadata?.provider || 'unknown'}</p>
          
          {loading && (
            <p className="text-gray-600">Loading backend profile...</p>
          )}
          
          {error && (
            <p className="text-red-600">Error: {error}</p>
          )}
          
          {backendUser && (
            <div className="mt-3 pt-3 border-t border-green-200 dark:border-green-700">
              <p><strong>Account Created:</strong> {new Date(backendUser.created_at).toLocaleDateString()}</p>
              <p className="text-green-700 dark:text-green-300 mt-2">
                ✅ Successfully connected to WITB backend!
              </p>
            </div>
          )}
        </div>
      </Card>

      {/* Favorite Players Card */}
      <Card className="p-4">
        <div className="flex items-center gap-3 mb-4">
          <Heart className="h-5 w-5 text-red-500" />
          <h3 className="text-lg font-semibold">My Favorite Players</h3>
        </div>

        {favoritesLoading && (
          <p className="text-gray-600">Loading favorite players...</p>
        )}

        {!favoritesLoading && favorites.length === 0 && (
          <p className="text-gray-500">
            No favorite players yet. Browse players and add some favorites!
          </p>
        )}

        {!favoritesLoading && favorites.length > 0 && (
          <div className="space-y-3">
            {favorites.map((favorite) => (
              <div
                key={favorite.id}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
              >
                <div>
                  <h4 className="font-medium">{favorite.player.name}</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {favorite.player.country} • {favorite.player.tour}
                    {favorite.player.ranking && ` • Rank #${favorite.player.ranking}`}
                  </p>
                  <p className="text-xs text-gray-500">
                    Added {new Date(favorite.created_at).toLocaleDateString()}
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleRemoveFavorite(favorite.player.id)}
                  disabled={removingFavorites.has(favorite.player.id)}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50 disabled:opacity-50"
                >
                  {removingFavorites.has(favorite.player.id) ? 'Removing...' : 'Remove'}
                </Button>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}