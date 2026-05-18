"use client";

import { useEffect, useState } from "react";

import type { CellDetail } from "@/lib/api";
import { apiGet } from "@/lib/api";

// Client component: fetches /api/v1/runs/{runId}/sheets/{sheet}/cells/{ref}
// on demand and renders the pass/fail explanation + provenance chain.
// Reads ?cell= from the URL via props (set by SheetPage on the server).
//
// HARD RESTRAINT: no SWR/React Query. If we add a second panel that
// also fetches cell-shaped data and we end up duplicating cache logic,
// propose:
//   "ADR: introduce a client data-fetching layer for apps/web".
export function CellDetailPanel({
  runId,
  sheetName,
  cellRef,
}: {
  runId: string;
  sheetName: string;
  cellRef?: string;
}) {
  const [data, setData] = useState<CellDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!cellRef) {
      setData(null);
      setError(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    apiGet<CellDetail>(
      `/api/v1/runs/${encodeURIComponent(runId)}/sheets/${encodeURIComponent(
        sheetName,
      )}/cells/${encodeURIComponent(cellRef)}`,
    )
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [runId, sheetName, cellRef]);

  if (!cellRef) {
    return (
      <aside className="rounded border border-dashed border-gray-300 p-4 text-sm text-gray-500">
        Click a cell to see its provenance + pass/fail reasoning.
      </aside>
    );
  }

  return (
    <aside className="space-y-3 rounded border border-gray-200 bg-white p-4 shadow-sm">
      <header className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">
          Cell <code className="rounded bg-gray-100 px-1">{cellRef}</code>
        </h3>
        {loading && (
          <span className="text-xs text-gray-500">loading…</span>
        )}
      </header>

      {error && (
        <p className="rounded bg-red-50 p-2 text-xs text-red-700">
          Failed to load cell: {error}
        </p>
      )}

      {data && (
        <>
          <dl className="grid grid-cols-3 gap-x-2 gap-y-1 text-xs">
            <dt className="font-medium text-gray-600">Value</dt>
            <dd className="col-span-2 font-mono">
              {data.cell.value === null
                ? "—"
                : String(data.cell.value)}
            </dd>

            <dt className="font-medium text-gray-600">Column</dt>
            <dd className="col-span-2 font-mono">{data.cell.column_id}</dd>

            <dt className="font-medium text-gray-600">Highlight</dt>
            <dd className="col-span-2">
              {data.cell.is_highlight ? (
                <span className="rounded bg-[#ffc7ce] px-1 text-[#df5006]">
                  HIGHLIGHT
                </span>
              ) : (
                <span className="text-gray-500">no</span>
              )}
            </dd>

            {data.cell.validator_id && (
              <>
                <dt className="font-medium text-gray-600">Validator</dt>
                <dd className="col-span-2 font-mono">
                  {data.cell.validator_id}
                </dd>
              </>
            )}
          </dl>

          {data.computed_expression && (
            <section>
              <h4 className="text-xs font-semibold text-gray-700">
                Computed expression
              </h4>
              <pre className="overflow-auto rounded bg-gray-100 p-2 text-xs">
                {data.computed_expression}
              </pre>
            </section>
          )}

          <section>
            <h4 className="text-xs font-semibold text-gray-700">
              Provenance ({data.provenance.length})
            </h4>
            <ol className="mt-1 space-y-1">
              {data.provenance.map((p) => (
                <li
                  key={p.id}
                  className="rounded border border-gray-100 bg-gray-50 px-2 py-1 text-xs"
                >
                  <span className="mr-2 inline-block rounded bg-slate-200 px-1 text-[10px] uppercase tracking-wide">
                    {p.kind}
                  </span>
                  <span className="font-mono">{p.label}</span>
                  {p.detail && (
                    <div className="text-gray-600">{p.detail}</div>
                  )}
                </li>
              ))}
            </ol>
          </section>

          <section>
            <h4 className="text-xs font-semibold text-gray-700">
              Pass / fail
            </h4>
            <p className="text-xs text-gray-700">
              {data.cell.is_highlight ? (
                <>
                  This cell{" "}
                  <strong className="text-[#df5006]">failed</strong>{" "}
                  validator{" "}
                  <code>{data.cell.validator_id ?? "(unknown)"}</code> and
                  was highlighted in the legacy XLSX report.
                </>
              ) : (
                <>
                  This cell{" "}
                  <strong className="text-green-700">passed</strong> all
                  validators that inspected it.
                </>
              )}
            </p>
          </section>
        </>
      )}
    </aside>
  );
}
