'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'

export default function AuthCallback() {
  const router = useRouter()
  const [status, setStatus] = useState('Processing...')

  useEffect(() => {
    console.log('🔄 Auth callback page loaded')
    console.log('🌐 Full URL:', window.location.href)
    console.log('🔗 Hash:', window.location.hash)
    
    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('🎯 Auth event in callback:', event)
        console.log('👤 Session in callback:', !!session)
        console.log('📧 Email in callback:', session?.user?.email)

        if (event === 'SIGNED_IN' && session) {
          console.log('✅ Successfully signed in!')
          setStatus('Success! Redirecting...')
          setTimeout(() => {
            router.push('/?welcome=true')
          }, 1500)
        } else if (event === 'TOKEN_REFRESHED' && session) {
          console.log('🔄 Token refreshed')
          setStatus('Success! Redirecting...')
          setTimeout(() => {
            router.push('/?welcome=true')
          }, 1500)
        } else {
          console.log('⚠️ No session after auth event:', event)
          setTimeout(() => {
            router.push('/')
          }, 3000)
        }
      }
    )

    // Cleanup subscription
    return () => {
      subscription.unsubscribe()
    }
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">{status}</p>
      </div>
    </div>
  )
}