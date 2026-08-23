import { Skeleton } from "@/components/ui/skeleton"

export function TournamentWinnerSkeleton() {
  return (
    <div className="bg-status-good-surface border-l-4 border-status-good/30 p-4 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <Skeleton className="h-5 w-5 rounded-md" />
          </div>
          <div className="ml-3">
            <Skeleton className="h-4 w-32 mb-2" />
            <div className="space-y-1">
              <Skeleton className="h-3 w-48" />
              <Skeleton className="h-3 w-24" />
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="w-8 h-8 rounded-full" />
        </div>
      </div>
    </div>
  )
}