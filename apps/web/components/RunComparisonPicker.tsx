"use client";

import Link from "next/link";

import type { RunSummary } from "@/lib/api";

export function RunComparisonPicker({
  runId,
  candidates,
}: {
  runId: string;
  candidates: RunSummary[];
}) {
  const others = candidates.filter((r) => r.run_id !== runId);

  return (
    <section className="space-y-3 rounded border border-gray-200 bg-white p-4 text-sm shadow-sm">
      <header>
        <h2 className="text-base font-semibold">Pick a comparison run</h2>
        <p className="text-xs text-gray-500">
          Choose another run for the same servicer to diff{" "}
          <span className="font-mono">{runId}</span> against.
        </p>
      </header>
      {others.length === 0 ? (
        <p className="rounded border border-dashed border-gray-300 p-4 text-center text-xs text-gray-500">
          No other runs available to compare against.
        </p>
      ) : (
        <ul className="divide-y divide-gray-100">
          {others.map((r) => (
            <li
              key={r.run_id}
              className="flex flex-wrap items-center justify-between gap-2 py-2"
            >
              <div>
                <div className="font-mono text-xs">{r.run_id}</div>
                <div className="text-[11px] text-gray-500">
                  {r.servicer} · remit {r.remit_date} · {r.status}
                </div>
              </div>
              <Link
                href={`/runs/${encodeURIComponent(runId)}/diff?against=${encodeURIComponent(r.run_id)}`}
                className="rounded border border-blue-200 bg-blue-50 px-2 py-1 text-xs text-blue-700 hover:bg-blue-100"
              >
                Diff against this →
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
