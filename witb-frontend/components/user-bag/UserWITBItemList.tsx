'use client'

import { useState } from 'react'
import { UserWITBItem } from '@/types/schemas'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Edit2, Trash2, Target, Calendar, DollarSign } from 'lucide-react'
import { api } from '@/lib/api'
import { BrandLogo } from '@/components/ui/BrandLogo'
import { PriceButton } from '@/components/pricing/PriceButton'

interface UserWITBItemListProps {
  items: UserWITBItem[]
  onUpdate: () => void
}

interface UserWITBItemCardProps {
  item: UserWITBItem
  onUpdate: () => void
}

function UserWITBItemCard({ item, onUpdate }: UserWITBItemCardProps) {
  const [isDeleting, setIsDeleting] = useState(false)

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to remove this equipment from your bag?')) {
      return
    }

    console.log('DELETE DEBUG - Item ID:', item.id)
    console.log('DELETE DEBUG - Item ID type:', typeof item.id)
    console.log('DELETE DEBUG - Full item:', item)
    console.log('DELETE DEBUG - URL will be:', `/user-bag/${item.id}`)

    setIsDeleting(true)
    try {
      await api.delete(`/user-bag/${item.id}`)
      console.log('DELETE DEBUG - Success!')
      onUpdate()
    } catch (error) {
      console.error('DELETE DEBUG - Error:', error)
      console.error('DELETE DEBUG - Error type:', typeof error)
      console.error('DELETE DEBUG - Error message:', (error as Error)?.message)
      alert('Failed to remove equipment. Please try again.')
    } finally {
      setIsDeleting(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const year = date.getFullYear()
    const month = date.getMonth() + 1
    const day = date.getDate()
    return `${month}/${day}/${year}`
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price)
  }

  const getCategoryColor = (category: string) => {
    const colors = {
      'Driver': 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-300',
      'Fairway': 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300',
      '5-Wood': 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300',
      'Hybrid': 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300',
      'Iron': 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300',
      'Wedge': 'bg-amber-100 text-amber-800 dark:bg-amber-900/20 dark:text-amber-300',
      'Putter': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/20 dark:text-emerald-300',
      'Ball': 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300',
    }
    return colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300'
  }

  return (
    <Card className="relative p-4 pr-16 hover:shadow-lg transition-all duration-200 hover:scale-[1.01] border-0 shadow-sm bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
      {/* Top-Right Action Buttons */}
      <div className="absolute top-3 right-3 flex gap-1 z-10">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            // TODO: Implement edit functionality
            alert('Edit functionality coming soon!')
          }}
          className="h-7 w-7 p-0 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full"
        >
          <Edit2 className="h-3.5 w-3.5" />
        </Button>

        <Button
          variant="ghost"
          size="sm"
          onClick={handleDelete}
          disabled={isDeleting}
          className="h-7 w-7 p-0 hover:bg-red-50 dark:hover:bg-red-900/20 text-red-500 hover:text-red-600 rounded-full"
        >
          {isDeleting ? (
            <div className="h-3.5 w-3.5 animate-spin border border-red-500 border-t-transparent rounded-full" />
          ) : (
            <Trash2 className="h-3.5 w-3.5" />
          )}
        </Button>
      </div>

      {/* Main Content */}
      <div className="flex items-start gap-4">
        {/* Category Badge - Leftmost Position */}
        <div className="flex-shrink-0">
          <div className={`w-16 h-12 rounded-xl p-2 shadow-sm overflow-hidden flex items-center justify-center ${getCategoryColor(item.category)}`}>
            <span className="text-sm font-bold text-center whitespace-nowrap">
              {item.category}
            </span>
          </div>
        </div>

        {/* Equipment Details */}
        <div className="flex-1 min-w-0">
          {/* Header Row */}
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            {item.carry_distance && (
              <div className="inline-flex items-center gap-1 px-2 py-1 bg-emerald-50 dark:bg-emerald-900/20 rounded-md whitespace-nowrap overflow-hidden">
                <Target className="h-3 w-3 text-emerald-600 dark:text-emerald-400 flex-shrink-0" />
                <span className="text-xs font-medium text-emerald-700 dark:text-emerald-300">
                  {item.carry_distance}y
                </span>
              </div>
            )}
          </div>

          {/* Equipment Name - Brand & Model */}
          <h4 className="font-semibold text-lg text-gray-900 dark:text-white mb-1 truncate">
            {item.model}
          </h4>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 truncate">
            by {item.brand}
          </p>

          {/* Specifications */}
          {(item.loft || item.shaft) && (
            <div className="flex flex-wrap gap-3 mb-3">
              {item.loft && (
                <div className="flex items-center gap-1 text-sm whitespace-nowrap">
                  <span className="text-gray-500 dark:text-gray-400">Loft:</span>
                  <span className="font-medium text-gray-900 dark:text-white">{item.loft}</span>
                </div>
              )}
              {item.shaft && (
                <div className="flex items-center gap-1 text-sm">
                  <span className="text-gray-500 dark:text-gray-400 whitespace-nowrap">Shaft:</span>
                  <span className="font-medium text-gray-900 dark:text-white truncate max-w-[120px]">{item.shaft}</span>
                </div>
              )}
            </div>
          )}

          {/* Notes */}
          {item.notes && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2 italic">
              "{item.notes}"
            </p>
          )}

          {/* Bottom Row - Actions & Purchase Info */}
          <div className="flex items-center gap-4 flex-wrap">
            {/* eBay Pricing */}
            <PriceButton
              witbItem={{
                brand: item.brand,
                model: item.model,
                category: item.category
              }}
              size="sm"
              className="text-xs"
            />

            {/* Purchase Info */}
            <div className="flex flex-wrap gap-3 text-xs text-gray-500 dark:text-gray-500">
              {item.purchase_date && (
                <div className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  <span>{formatDate(item.purchase_date)}</span>
                </div>
              )}
              {item.purchase_price && (
                <div className="flex items-center gap-1">
                  <DollarSign className="h-3 w-3" />
                  <span className="font-medium">{formatPrice(item.purchase_price)}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}

export function UserWITBItemList({ items, onUpdate }: UserWITBItemListProps) {
  if (items.length === 0) {
    return null
  }

  return (
    <div className="space-y-4">
      {items.map((item, index) => (
        <div
          key={item.id}
          className="animate-in slide-in-from-bottom-2 fade-in-0"
          style={{ animationDelay: `${index * 100}ms` }}
        >
          <UserWITBItemCard
            item={item}
            onUpdate={onUpdate}
          />
        </div>
      ))}
    </div>
  )
}