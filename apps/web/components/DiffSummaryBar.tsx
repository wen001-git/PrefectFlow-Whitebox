"use client";

import { VerdictBadge } from "./VerdictBadge";
import type { DiffResponse } from "@/lib/api";

export function DiffSummaryBar({
  diff,
  majorSheets,
  minorSheets,
  identicalSheets,
}: {
  diff: DiffResponse;
  majorSheets: number;
  minorSheets: number;
  identicalSheets: number;
}) {
  return (
    <div className="flex flex-wrap items-center gap-3 rounded border border-gray-200 bg-white px-3 py-2 text-sm shadow-sm">
      <VerdictBadge verdict={diff.verdict} />
      <span className="text-xs text-gray-500">
        Run <span className="font-mono">{diff.run_id}</span> vs{" "}
        <span className="font-mono">{diff.compared_to}</span>
      </span>
      <span className="ml-auto flex flex-wrap items-center gap-3 text-xs">
        <StatChip label="Major" value={majorSheets} tone="major" />
        <StatChip label="Minor" value={minorSheets} tone="minor" />
        <StatChip label="Identical" value={identicalSheets} tone="identical" />
        <StatChip
          label="Cells changed"
          value={diff.total_cells_changed}
          tone="neutral"
        />
      </span>
    </div>
  );
}

function StatChip({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: "major" | "minor" | "identical" | "neutral";
}) {
  const TONE: Record<typeof tone, string> = {
    major: "bg-red-100 text-red-800 border-red-300",
    minor: "bg-yellow-100 text-yellow-800 border-yellow-300",
    identical: "bg-green-100 text-green-800 border-green-300",
    neutral: "bg-slate-100 text-slate-800 border-slate-300",
  };
  return (
    <span
      className={`inline-flex items-center gap-1 rounded border px-1.5 py-0.5 ${TONE[tone]}`}
    >
      <span className="text-[10px] uppercase tracking-wide">{label}</span>
      <span className="font-mono tabular-nums">{value}</span>
    </span>
  );
}
