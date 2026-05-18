import Link from "next/link";

import { VerdictBadge } from "@/components/VerdictBadge";
import {
  apiGet,
  type RunDetail,
  type SheetListResponse,
} from "@/lib/api";

export default async function RunDetailPage({
  params,
}: {
  params: { runId: string };
}) {
  const runId = decodeURIComponent(params.runId);

  // Parallel fetch — detail + sheet list independently.
  const [detail, sheetList] = await Promise.all([
    apiGet<RunDetail>(`/api/v1/runs/${encodeURIComponent(runId)}`),
    apiGet<SheetListResponse>(
      `/api/v1/runs/${encodeURIComponent(runId)}/sheets`,
    ),
  ]);

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <div className="flex items-center justify-between gap-2">
          <h1 className="text-2xl font-semibold">
            Run <span className="font-mono">{detail.run_id}</span>
          </h1>
          <VerdictBadge verdict={detail.verdict} />
        </div>
        <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm md:grid-cols-4">
          <div>
            <dt className="text-xs uppercase text-gray-500">Servicer</dt>
            <dd>{detail.servicer}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase text-gray-500">Remit date</dt>
            <dd>{detail.remit_date}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase text-gray-500">Status</dt>
            <dd>{detail.status}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase text-gray-500">Created</dt>
            <dd>{new Date(detail.created_at).toLocaleString()}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase text-gray-500">Validators</dt>
            <dd>
              <span className="text-green-700">
                {detail.validators_passed} ✓
              </span>
              {" / "}
              <span className="text-red-700">
                {detail.validators_failed} ✗
              </span>
            </dd>
          </div>
          {detail.baseline_run_id && (
            <div>
              <dt className="text-xs uppercase text-gray-500">Baseline</dt>
              <dd className="font-mono text-xs">{detail.baseline_run_id}</dd>
            </div>
          )}
        </dl>
      </header>

      <div className="flex flex-wrap items-center gap-3">
        <DownloadXlsxButton runId={runId} />
        <Link
          href={`/runs/${encodeURIComponent(runId)}/lineage`}
          className="rounded border border-gray-300 px-3 py-1.5 text-sm hover:bg-gray-50"
        >
          Lineage graph
        </Link>
        <Link
          href={`/runs/${encodeURIComponent(runId)}/diff`}
          className="rounded border border-gray-300 px-3 py-1.5 text-sm hover:bg-gray-50"
        >
          Diff vs baseline
        </Link>
      </div>

      <section className="space-y-2">
        <h2 className="text-lg font-semibold">Sheets</h2>
        <div className="overflow-x-auto rounded border border-gray-200">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-600">
              <tr>
                <th className="px-3 py-2">#</th>
                <th className="px-3 py-2">Sheet</th>
                <th className="px-3 py-2 text-right">Rows</th>
                <th className="px-3 py-2 text-right">Columns</th>
                <th className="px-3 py-2 text-right">Highlights</th>
                <th className="px-3 py-2" />
              </tr>
            </thead>
            <tbody>
              {sheetList.sheets
                .slice()
                .sort((a, b) => a.tab_order - b.tab_order)
                .map((s) => (
                  <tr
                    key={s.sheet_name}
                    className="border-t border-gray-100 hover:bg-slate-50"
                  >
                    <td className="px-3 py-2 text-xs text-gray-500">
                      {s.tab_order}
                    </td>
                    <td className="px-3 py-2">
                      <div className="font-medium">{s.title || s.sheet_name}</div>
                      <div className="font-mono text-xs text-gray-500">
                        {s.sheet_name}
                      </div>
                    </td>
                    <td className="px-3 py-2 text-right tabular-nums">
                      {s.row_count}
                    </td>
                    <td className="px-3 py-2 text-right tabular-nums">
                      {s.column_count}
                    </td>
                    <td className="px-3 py-2 text-right tabular-nums">
                      {s.highlight_count > 0 ? (
                        <span className="rounded bg-[#ffc7ce] px-1.5 text-[#df5006]">
                          {s.highlight_count}
                        </span>
                      ) : (
                        <span className="text-gray-400">0</span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-right">
                      <Link
                        href={`/runs/${encodeURIComponent(runId)}/sheets/${encodeURIComponent(s.sheet_name)}`}
                        className="text-blue-600 hover:underline"
                      >
                        Open →
                      </Link>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}

// Server-rendered "Download XLSX" affordance. The export endpoint
// returns 501 today (engine wiring deferred), so we render a visually
// disabled button with a tooltip that links back to the eventual
// contract (ExportResponse in lib/api.ts).
function DownloadXlsxButton({ runId }: { runId: string }) {
  return (
    <span
      title="engine pending — /api/v1/runs/{id}/export returns 501 until the renderer wiring lands"
      className="inline-flex cursor-not-allowed items-center gap-1 rounded border border-gray-200 bg-gray-100 px-3 py-1.5 text-sm text-gray-500"
      aria-disabled
      data-run-id={runId}
    >
      ⬇ Download XLSX
      <span className="rounded bg-gray-300 px-1 text-[10px] uppercase text-gray-700">
        pending
      </span>
    </span>
  );
}
