'use client'

import { useState } from 'react'
import { useAuth } from '@/providers/auth-provider'
import { useUserBag } from '@/hooks/useUserBag'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Golf } from 'lucide-react'
import { AddEquipmentForm } from './AddEquipmentForm'
import { UserWITBItemList } from './UserWITBItemList'

export function UserBag() {
  const { user } = useAuth()
  const { data: bagData, error, isLoading, refetch } = useUserBag()
  const [showAddForm, setShowAddForm] = useState(false)

  if (!user) {
    return (
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
        <div className="text-center">
          <Golf className="h-12 w-12 text-blue-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-blue-800 dark:text-blue-200 mb-2">
            Sign In Required
          </h3>
          <p className="text-blue-700 dark:text-blue-300">
            Sign in to track your golf equipment and performance data!
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">
          Error Loading Your Bag
        </h3>
        <p className="text-red-700 dark:text-red-300 mb-4">
          {error.message || 'Unable to load your equipment. Please try again.'}
        </p>
        <Button onClick={refetch} variant="outline" size="sm">
          Try Again
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* My Equipment Card */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Golf className="h-5 w-5 text-emerald-500" />
            <h3 className="text-lg font-semibold">My Equipment</h3>
            {bagData && (
              <span className="text-sm text-gray-500 dark:text-gray-400">
                ({bagData.total} {bagData.total === 1 ? 'club' : 'clubs'})
              </span>
            )}
          </div>
          <Button
            onClick={() => setShowAddForm(true)}
            size="sm"
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Equipment
          </Button>
        </div>

        {/* Add Equipment Form */}
        {showAddForm && (
          <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <AddEquipmentForm
              onSuccess={() => {
                setShowAddForm(false)
                refetch()
              }}
              onCancel={() => setShowAddForm(false)}
            />
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-8">
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-48 mx-auto mb-2"></div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-32 mx-auto"></div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && bagData && bagData.items.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 text-4xl mb-4">⛳</div>
            <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No Equipment Yet
            </h4>
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              Start building your bag by adding your golf clubs and equipment!
            </p>
            <Button
              onClick={() => setShowAddForm(true)}
              className="flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Add Your First Club
            </Button>
          </div>
        )}

        {/* Equipment List */}
        {!isLoading && bagData && bagData.items.length > 0 && (
          <UserWITBItemList items={bagData.items} onUpdate={refetch} />
        )}
      </Card>
    </div>
  )
}