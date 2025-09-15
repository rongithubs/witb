'use client'

import { useState } from 'react'
import { UserWITBItem } from '@/types/schemas'
import { Badge } from '@/components/ui/badge'
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

    setIsDeleting(true)
    try {
      await api.delete(`/user-bag/${item.id}`)
      onUpdate()
    } catch (error) {
      console.error('Failed to delete equipment:', error)
      alert('Failed to remove equipment. Please try again.')
    } finally {
      setIsDeleting(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price)
  }

  return (
    <Card className="p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3 flex-1">
          {/* Brand Logo */}
          <div className="flex-shrink-0">
            <BrandLogo
              brand={item.brand}
              size="sm"
              className="w-10 h-10"
            />
          </div>

          {/* Equipment Details */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="secondary" className="text-xs">
                {item.category}
              </Badge>
              {item.carry_distance && (
                <div className="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400">
                  <Target className="h-3 w-3" />
                  {item.carry_distance}y
                </div>
              )}
            </div>

            <h4 className="font-medium text-gray-900 dark:text-white">
              {item.brand} {item.model}
            </h4>

            <div className="flex flex-wrap gap-2 mt-1 text-sm text-gray-600 dark:text-gray-400">
              {item.loft && <span>Loft: {item.loft}</span>}
              {item.shaft && <span>Shaft: {item.shaft}</span>}
            </div>

            {item.notes && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 line-clamp-2">
                {item.notes}
              </p>
            )}

            {/* Purchase Info */}
            <div className="flex flex-wrap gap-4 mt-2 text-xs text-gray-500 dark:text-gray-500">
              {item.purchase_date && (
                <div className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {formatDate(item.purchase_date)}
                </div>
              )}
              {item.purchase_price && (
                <div className="flex items-center gap-1">
                  <DollarSign className="h-3 w-3" />
                  {formatPrice(item.purchase_price)}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 ml-4">
          {/* eBay Pricing */}
          <PriceButton
            brand={item.brand}
            model={item.model}
            category={item.category}
            size="sm"
          />

          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              // TODO: Implement edit functionality
              alert('Edit functionality coming soon!')
            }}
            className="h-8 w-8 p-0"
          >
            <Edit2 className="h-4 w-4" />
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleDelete}
            disabled={isDeleting}
            className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
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
    <div className="space-y-3">
      {items.map((item) => (
        <UserWITBItemCard
          key={item.id}
          item={item}
          onUpdate={onUpdate}
        />
      ))}
    </div>
  )
}