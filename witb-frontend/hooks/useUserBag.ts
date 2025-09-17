import useSWR from 'swr'
import { fetcher } from '@/lib/api'
import { UserBagResponse } from '@/types/schemas'

export function useUserBag() {
  const { data, error, isLoading, mutate } = useSWR<UserBagResponse>(
    '/user-bag',
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      errorRetryCount: 3,
      onError: (error) => {
        console.error('useUserBag error:', error)
      },
      onSuccess: (data) => {
        console.log('useUserBag success:', data)
      }
    }
  )

  return {
    data,
    error,
    isLoading,
    isEmpty: !isLoading && (!data || data.items.length === 0),
    refetch: mutate,
  }
}