import type { DiffVerdict } from "@/lib/api";

const STYLES: Record<DiffVerdict, string> = {
  PASS: "bg-green-100 text-green-800 border-green-300",
  MINOR_DIFFS: "bg-yellow-100 text-yellow-800 border-yellow-300",
  MAJOR_DIFFS: "bg-red-100 text-red-800 border-red-300",
  ERROR: "bg-gray-200 text-gray-800 border-gray-400",
};

const LABELS: Record<DiffVerdict, string> = {
  PASS: "PASS",
  MINOR_DIFFS: "MINOR DIFFS",
  MAJOR_DIFFS: "MAJOR DIFFS",
  ERROR: "ERROR",
};

export function VerdictBadge({ verdict }: { verdict: DiffVerdict }) {
  return (
    <span
      className={`inline-block rounded border px-2 py-0.5 text-xs font-semibold uppercase tracking-wide ${STYLES[verdict]}`}
    >
      {LABELS[verdict]}
    </span>
  );
}
