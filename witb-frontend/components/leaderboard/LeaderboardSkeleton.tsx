import styles from "@/components/ui/glassmorphism.module.css";

export function LeaderboardSkeleton() {
  return (
    <div className={styles.glassContainer + " p-6"}>
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 dark:bg-white/20 rounded w-48"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className={styles.glassCard + " p-4 h-24"}></div>
          ))}
        </div>
      </div>
    </div>
  );
}