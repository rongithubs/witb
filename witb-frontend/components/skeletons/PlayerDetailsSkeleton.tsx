import { Skeleton } from "@/components/ui/skeleton"
import { Card } from "@/components/ui/card"

export function PlayerDetailsSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm flex flex-col">
      {/* Header skeleton */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
        <div className="flex items-center gap-4">
          <Skeleton className="w-16 h-16 rounded-full" />
          <div>
            <Skeleton className="h-8 w-48 mb-2" />
            <Skeleton className="h-4 w-32 mb-1" />
            <Skeleton className="h-3 w-24" />
          </div>
        </div>
      </div>
      
      {/* Content skeleton */}
      <div className="flex-1 overflow-y-auto p-6">
        <Skeleton className="h-6 w-40 mb-4" />
        
        <div className="grid gap-3">
          {Array.from({ length: 8 }).map((_, index) => (
            <Card key={index} className="p-4 bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <Skeleton className="h-5 w-24 mb-2" />
                  <Skeleton className="h-4 w-32 mb-2" />
                  <div className="flex gap-2 mt-2">
                    <Skeleton className="h-6 w-16 rounded" />
                    <Skeleton className="h-6 w-20 rounded" />
                  </div>
                </div>
                <Skeleton className="h-8 w-20 rounded ml-4" />
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}