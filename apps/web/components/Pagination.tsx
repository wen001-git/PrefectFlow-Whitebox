import Link from "next/link";

// Server-rendered pagination — uses plain <Link href> so no client state
// is needed. HARD RESTRAINT (AGENTS § 6.14): if we end up needing
// client-side cursor state, propose:
//   "ADR: introduce client-state library for apps/web pagination".
export function Pagination({
  basePath,
  query,
  total,
  limit,
  offset,
}: {
  basePath: string;
  query: Record<string, string | undefined>;
  total: number;
  limit: number;
  offset: number;
}) {
  const page = Math.floor(offset / limit) + 1;
  const pageCount = Math.max(1, Math.ceil(total / limit));
  const hasPrev = offset > 0;
  const hasNext = offset + limit < total;

  const buildHref = (newOffset: number) => {
    const params = new URLSearchParams();
    for (const [k, v] of Object.entries(query)) {
      if (v != null && v !== "") params.set(k, v);
    }
    params.set("limit", String(limit));
    params.set("offset", String(newOffset));
    return `${basePath}?${params.toString()}`;
  };

  const baseBtn =
    "rounded border px-3 py-1 text-sm transition-colors";
  const enabled = "border-gray-300 hover:bg-gray-50";
  const disabled = "border-gray-200 text-gray-400 cursor-not-allowed";

  return (
    <nav
      className="flex items-center justify-between"
      aria-label="Pagination"
    >
      <span className="text-xs text-gray-600">
        Page {page} of {pageCount} — {total} total
      </span>
      <div className="flex items-center gap-2">
        {hasPrev ? (
          <Link
            className={`${baseBtn} ${enabled}`}
            href={buildHref(Math.max(0, offset - limit))}
            prefetch={false}
          >
            ← Prev
          </Link>
        ) : (
          <span className={`${baseBtn} ${disabled}`} aria-disabled>
            ← Prev
          </span>
        )}
        {hasNext ? (
          <Link
            className={`${baseBtn} ${enabled}`}
            href={buildHref(offset + limit)}
            prefetch={false}
          >
            Next →
          </Link>
        ) : (
          <span className={`${baseBtn} ${disabled}`} aria-disabled>
            Next →
          </span>
        )}
      </div>
    </nav>
  );
}
