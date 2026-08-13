import clsx from "clsx";

export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={clsx(
        "animate-pulse rounded-lg bg-gradient-to-r from-ink-700/60 via-ink-600/40 to-ink-700/60 bg-[length:200%_100%]",
        className
      )}
      style={{ animation: "shimmer 1.6s ease-in-out infinite" }}
    />
  );
}

export function CardSkeleton() {
  return (
    <div className="glass rounded-2xl p-5 space-y-3">
      <Skeleton className="h-4 w-1/3" />
      <Skeleton className="h-8 w-1/2" />
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="glass rounded-2xl p-5 space-y-3">
      <Skeleton className="h-5 w-1/4" />
      <Skeleton className="h-64 w-full" />
    </div>
  );
}
