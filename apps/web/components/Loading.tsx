export function Loading({ label = "Loading…" }: { label?: string }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="flex items-center gap-2 text-sm text-gray-500"
    >
      <span className="inline-block h-3 w-3 animate-pulse rounded-full bg-gray-400" />
      {label}
    </div>
  );
}
