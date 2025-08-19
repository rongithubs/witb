'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@/providers/auth-provider'
import { authApi } from '@/lib/api'

interface BackendUser {
  id: string
  supabase_user_id: string
  email: string | null
  phone: string | null
  created_at: string
  updated_at: string
}

export function UserProfile() {
  const { user, session } = useAuth()
  const [backendUser, setBackendUser] = useState<BackendUser | null>(null)
  const [loading, setLoading] = useState(false)
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
        setBackendUser(data as BackendUser)
      }
    } catch (err) {
      setError('Failed to fetch user data')
    } finally {
      setLoading(false)
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
    <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold text-green-800 dark:text-green-200 mb-3">
        Welcome to WITB! 🏌️‍♂️
      </h3>
      
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
            <p><strong>User ID:</strong> {backendUser.id}</p>
            <p className="text-green-700 dark:text-green-300 mt-2">
              ✅ Successfully connected to WITB backend!
            </p>
          </div>
        )}
      </div>
    </div>
  )
}