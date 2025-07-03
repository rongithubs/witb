import { Skeleton } from "@/components/ui/skeleton"

export function PlayerListSkeleton() {
  return (
    <div className="p-2 space-y-1">
      {Array.from({ length: 10 }).map((_, index) => (
        <div key={index} className="p-3 rounded-md">
          <div className="flex items-center gap-3">
            <Skeleton className="w-10 h-10 rounded-full" />
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-5 w-8 rounded-full" />
              </div>
              <Skeleton className="h-3 w-16 mt-1" />
              <Skeleton className="h-3 w-20 mt-1" />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export function PlayerListItemSkeleton() {
  return (
    <div className="p-3 rounded-md">
      <div className="flex items-center gap-3">
        <Skeleton className="w-10 h-10 rounded-full" />
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-5 w-8 rounded-full" />
          </div>
          <Skeleton className="h-3 w-16 mt-1" />
          <Skeleton className="h-3 w-20 mt-1" />
        </div>
      </div>
    </div>
  )
}