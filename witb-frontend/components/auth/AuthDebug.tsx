'use client'

import { useAuth } from '@/providers/auth-provider'
import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'

export function AuthDebug() {
  const { user, session, loading } = useAuth()
  const [rawSession, setRawSession] = useState<any>(null)

  useEffect(() => {
    const checkSession = async () => {
      const { data } = await supabase.auth.getSession()
      setRawSession(data.session)
    }
    checkSession()
  }, [])

  return (
    <div className="fixed bottom-4 right-4 bg-black text-white p-4 rounded-lg text-xs max-w-sm overflow-hidden">
      <h3 className="font-bold mb-2">Auth Debug:</h3>
      <div className="space-y-1">
        <p>Loading: {loading ? 'Yes' : 'No'}</p>
        <p>User exists: {user ? 'Yes' : 'No'}</p>
        <p>Email: {user?.email || 'None'}</p>
        <p>Session exists: {session ? 'Yes' : 'No'}</p>
        <p>Raw session: {rawSession ? 'Yes' : 'No'}</p>
        <p>Access token: {session?.access_token ? 'Yes' : 'No'}</p>
      </div>
    </div>
  )
}