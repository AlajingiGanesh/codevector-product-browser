export function LoadingSkeleton() {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="h-4 w-24 animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
      <div className="mt-5 h-5 w-4/5 animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
      <div className="mt-3 h-4 w-2/3 animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
      <div className="mt-8 flex items-center justify-between">
        <div className="h-7 w-20 animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
        <div className="h-4 w-28 animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
      </div>
    </div>
  );
}

