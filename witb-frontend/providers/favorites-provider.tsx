'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { useAuth } from '@/providers/auth-provider'
import { authApi } from '@/lib/api'
import { FavoritePlayer, UserFavoritesResponse } from '@/types/schemas'

interface FavoritesContextType {
  favorites: FavoritePlayer[]
  isLoading: boolean
  error: string | null
  addFavorite: (playerId: string) => Promise<boolean>
  removeFavorite: (playerId: string) => Promise<boolean>
  isFavorite: (playerId: string) => boolean
  refreshFavorites: () => Promise<void>
}

const FavoritesContext = createContext<FavoritesContextType | undefined>(undefined)

export function FavoritesProvider({ children }: { children: React.ReactNode }) {
  const { user, session } = useAuth()
  const [favorites, setFavorites] = useState<FavoritePlayer[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refreshFavorites = async () => {
    if (!session) {
      setFavorites([])
      return
    }

    setIsLoading(true)
    setError(null)
    
    try {
      const { data, error: apiError } = await authApi.getFavorites()
      
      if (apiError) {
        setError(`Failed to fetch favorites: ${apiError}`)
      } else {
        const favoritesData = data as UserFavoritesResponse
        setFavorites(favoritesData.favorites)
      }
    } catch (err) {
      setError(`Failed to fetch favorites: ${err}`)
    } finally {
      setIsLoading(false)
    }
  }

  const addFavorite = async (playerId: string): Promise<boolean> => {
    if (!session) return false

    try {
      const { data, error: apiError } = await authApi.addFavorite(playerId)
      
      if (apiError) {
        setError(`Failed to add favorite: ${apiError}`)
        return false
      } else {
        // Refresh the entire list to ensure we have the latest data
        await refreshFavorites()
        return true
      }
    } catch (err) {
      setError(`Failed to add favorite: ${err}`)
      return false
    }
  }

  const removeFavorite = async (playerId: string): Promise<boolean> => {
    if (!session) return false

    try {
      const { error: apiError } = await authApi.removeFavorite(playerId)
      
      if (apiError) {
        setError(`Failed to remove favorite: ${apiError}`)
        return false
      } else {
        // Remove from local state immediately for better UX
        setFavorites(prev => prev.filter(fav => fav.player.id !== playerId))
        return true
      }
    } catch (err) {
      setError(`Failed to remove favorite: ${err}`)
      return false
    }
  }

  const isFavorite = (playerId: string): boolean => {
    return favorites.some(fav => fav.player.id === playerId)
  }

  // Load favorites when user session changes
  useEffect(() => {
    if (session) {
      refreshFavorites()
    } else {
      setFavorites([])
      setError(null)
    }
  }, [session])

  const value = {
    favorites,
    isLoading,
    error,
    addFavorite,
    removeFavorite,
    isFavorite,
    refreshFavorites,
  }

  return (
    <FavoritesContext.Provider value={value}>
      {children}
    </FavoritesContext.Provider>
  )
}

export function useFavorites() {
  const context = useContext(FavoritesContext)
  if (context === undefined) {
    throw new Error('useFavorites must be used within a FavoritesProvider')
  }
  return context
}