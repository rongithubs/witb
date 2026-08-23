'use client'

import { useState } from 'react'
import { useAuth } from '@/providers/auth-provider'
import { useUserBag } from '@/hooks/useUserBag'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Target } from 'lucide-react'
import { AddEquipmentForm } from './AddEquipmentForm'
import { UserWITBItemList } from './UserWITBItemList'

export function UserBag() {
  const { user } = useAuth()
  const { data: bagData, error, isLoading, refetch } = useUserBag()
  const [showAddForm, setShowAddForm] = useState(false)

  if (!user) {
    return (
      <div className="bg-status-info-surface border border-status-info/30 rounded-lg p-6">
        <div className="text-center">
          <Target className="h-12 w-12 text-status-info mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-status-info mb-2">
            Sign In Required
          </h3>
          <p className="text-status-info">
            Sign in to track your golf equipment and performance data!
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-status-critical-surface border border-status-critical/30 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-status-critical mb-2">
          Error Loading Your Bag
        </h3>
        <p className="text-status-critical mb-4">
          <strong>Error:</strong> {error.message || 'Unable to load your equipment. Please try again.'}
        </p>
        {error && (
          <details className="mt-2 text-xs text-status-critical">
            <summary>Debug Info</summary>
            <pre className="mt-1 p-2 bg-status-critical-surface rounded-md text-xs overflow-auto">
              {JSON.stringify(error, null, 2)}
            </pre>
          </details>
        )}
        <Button onClick={() => refetch()} variant="outline" size="sm">
          Try Again
        </Button>
      </div>
    )
  }

  const getBagStats = () => {
    if (!bagData || bagData.items.length === 0) return null

    const categories = bagData.items.reduce((acc, item) => {
      acc[item.category] = (acc[item.category] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    const newestItem = bagData.items.reduce((newest, item) => {
      const itemDate = new Date(item.created_at || 0)
      const newestDate = new Date(newest?.created_at || 0)
      return itemDate > newestDate ? item : newest
    }, null as typeof bagData.items[0] | null)

    const totalValue = bagData.items.reduce((sum, item) =>
      sum + (item.purchase_price || 0), 0
    )

    return { categories, newestItem, totalValue }
  }

  const stats = getBagStats()

  return (
    <div className="space-y-6">
      {/* Enhanced My Equipment Card */}
      <Card className="border border-hairline shadow-sm bg-surface">
        {/* Header Section */}
        <div className="p-6 border-b border-hairline">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-brand flex items-center justify-center shadow-lg">
                <Target className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-ink">My Equipment</h3>
                <p className="text-sm text-ink-secondary">
                  {bagData ? `${bagData.total} ${bagData.total === 1 ? 'club' : 'clubs'} in your bag` : 'Loading...'}
                </p>
              </div>
            </div>
            <Button
              onClick={() => setShowAddForm(true)}
              size="sm"
              className="flex items-center gap-2 bg-brand hover:bg-brand/90 text-white shadow-lg hover:shadow-lg transition-all duration-200"
            >
              <Plus className="h-4 w-4" />
              Add Equipment
            </Button>
          </div>

          {/* Stats Grid */}
          {stats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {/* Total Clubs */}
              <div className="bg-surface rounded-lg p-3 border border-hairline shadow-sm">
                <div className="text-2xl font-bold text-brand-strong">
                  {bagData?.total || 0}
                </div>
                <div className="text-xs text-ink-secondary font-medium">
                  Total Clubs
                </div>
              </div>

              {/* Categories */}
              <div className="bg-surface rounded-lg p-3 border border-hairline shadow-sm">
                <div className="text-2xl font-bold text-ink">
                  {Object.keys(stats.categories).length}
                </div>
                <div className="text-xs text-ink-secondary font-medium">
                  Categories
                </div>
              </div>

              {/* Total Value */}
              {stats.totalValue > 0 && (
                <div className="bg-surface rounded-lg p-3 border border-hairline shadow-sm">
                  <div className="text-2xl font-bold text-ink">
                    ${Math.round(stats.totalValue)}
                  </div>
                  <div className="text-xs text-ink-secondary font-medium">
                    Total Value
                  </div>
                </div>
              )}

              {/* Newest Addition */}
              {stats.newestItem && (
                <div className="bg-surface rounded-lg p-3 border border-hairline shadow-sm">
                  <div className="text-sm font-bold text-ink truncate">
                    {stats.newestItem.brand}
                  </div>
                  <div className="text-xs text-ink-secondary font-medium">
                    Latest Addition
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Content Section */}
        <div className="p-6">

        {/* Add Equipment Form */}
        {showAddForm && (
          <div className="mb-6 p-4 bg-surface-subtle rounded-lg">
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
              <div className="h-4 bg-skeleton rounded-md w-48 mx-auto mb-2"></div>
              <div className="h-3 bg-skeleton rounded-md w-32 mx-auto"></div>
            </div>
          </div>
        )}

        {/* Enhanced Empty State */}
        {!isLoading && bagData && bagData.items.length === 0 && (
          <div className="text-center py-12">
            <div className="w-20 h-20 mx-auto mb-6 bg-brand rounded-full flex items-center justify-center">
              <div className="text-brand-strong text-3xl">⛳</div>
            </div>
            <h4 className="text-xl font-bold text-ink mb-2">
              Your Bag is Empty
            </h4>
            <p className="text-ink-muted mb-6 max-w-md mx-auto">
              Start building your perfect golf bag! Add your clubs, track performance, and discover equipment insights.
            </p>

            {/* Quick Start Options */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center items-center mb-6">
              <Button
                onClick={() => setShowAddForm(true)}
                className="flex items-center gap-2 bg-brand hover:bg-brand/90 text-white shadow-lg hover:shadow-lg transition-all duration-200"
              >
                <Plus className="h-4 w-4" />
                Add Your First Club
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowAddForm(true)}
                className="flex items-center gap-2 border-brand text-brand-strong hover:bg-brand/90"
              >
                <Target className="h-4 w-4" />
                Start with Driver
              </Button>
            </div>

            {/* Popular Categories */}
            <div className="max-w-md mx-auto">
              <p className="text-sm text-ink-muted mb-3">Popular categories to start with:</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {['Driver', 'Iron', 'Wedge', 'Putter'].map((category) => (
                  <span
                    key={category}
                    className="px-3 py-1 bg-surface-subtle text-ink-secondary rounded-full text-xs font-medium"
                  >
                    {category}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Equipment List */}
        {!isLoading && bagData && bagData.items.length > 0 && (
          <UserWITBItemList items={bagData.items} onUpdate={refetch} />
        )}
        </div>
      </Card>
    </div>
  )
}