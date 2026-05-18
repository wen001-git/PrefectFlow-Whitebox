import Link from "next/link";

import { Pagination } from "@/components/Pagination";
import { VerdictBadge } from "@/components/VerdictBadge";
import {
  apiGet,
  type DiffVerdict,
  type RunListResponse,
} from "@/lib/api";

type SearchParams = {
  servicer?: string;
  date?: string;
  from_date?: string;
  to_date?: string;
  limit?: string;
  offset?: string;
};

function parseInt0(s: string | undefined, fallback: number): number {
  if (!s) return fallback;
  const n = Number.parseInt(s, 10);
  return Number.isFinite(n) && n >= 0 ? n : fallback;
}

// Heuristic verdict mapping for the list view: the list endpoint returns
// RunSummary without a verdict field (verdict is on RunDetail only).
// Derive one from validators_failed + status until the backend exposes
// a summary verdict.
function deriveVerdict(opts: {
  status: string;
  failed: number;
}): DiffVerdict {
  if (opts.status === "failed") return "ERROR";
  if (opts.failed > 3) return "MAJOR_DIFFS";
  if (opts.failed > 0) return "MINOR_DIFFS";
  return "PASS";
}

export default async function RunListPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const limit = parseInt0(searchParams.limit, 25);
  const offset = parseInt0(searchParams.offset, 0);
  const servicer = searchParams.servicer ?? "";
  // The picker emits ?date=YYYY-MM-DD as a single-date filter; map it
  // onto the from_date+to_date pair the API understands.
  const fromDate = searchParams.from_date ?? searchParams.date ?? "";
  const toDate = searchParams.to_date ?? searchParams.date ?? "";

  const qs = new URLSearchParams();
  if (servicer) qs.set("servicer", servicer);
  if (fromDate) qs.set("from_date", fromDate);
  if (toDate) qs.set("to_date", toDate);
  qs.set("limit", String(limit));
  qs.set("offset", String(offset));

  const data = await apiGet<RunListResponse>(
    `/api/v1/runs?${qs.toString()}`,
  );

  return (
    <section className="space-y-4">
      <header className="flex flex-wrap items-baseline justify-between gap-2">
        <h1 className="text-2xl font-semibold">Runs</h1>
        <p className="text-xs text-gray-500">
          {servicer && (
            <>
              servicer=<code className="font-mono">{servicer}</code>{" "}
            </>
          )}
          {fromDate && (
            <>
              date=<code className="font-mono">{fromDate}</code>{" "}
            </>
          )}
          <Link href="/" className="ml-2 text-blue-600 hover:underline">
            change filters
          </Link>
        </p>
      </header>

      <div className="overflow-x-auto rounded border border-gray-200">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase text-slate-600">
            <tr>
              <th className="px-3 py-2">Run ID</th>
              <th className="px-3 py-2">Servicer</th>
              <th className="px-3 py-2">Remit date</th>
              <th className="px-3 py-2">Verdict</th>
              <th className="px-3 py-2">Created</th>
              <th className="px-3 py-2">Validators</th>
              <th className="px-3 py-2" />
            </tr>
          </thead>
          <tbody>
            {data.runs.length === 0 && (
              <tr>
                <td
                  colSpan={7}
                  className="px-3 py-6 text-center text-gray-500"
                >
                  No runs match the current filter.
                </td>
              </tr>
            )}
            {data.runs.map((run) => {
              const verdict = deriveVerdict({
                status: run.status,
                failed: run.validators_failed,
              });
              return (
                <tr
                  key={run.run_id}
                  className="border-t border-gray-100 hover:bg-slate-50"
                >
                  <td className="px-3 py-2 font-mono text-xs">
                    {run.run_id}
                  </td>
                  <td className="px-3 py-2">{run.servicer}</td>
                  <td className="px-3 py-2">{run.remit_date}</td>
                  <td className="px-3 py-2">
                    <VerdictBadge verdict={verdict} />
                  </td>
                  <td className="px-3 py-2 text-xs text-gray-600">
                    {new Date(run.created_at).toLocaleString()}
                  </td>
                  <td className="px-3 py-2 text-xs">
                    <span className="text-green-700">
                      {run.validators_passed} ✓
                    </span>
                    {" / "}
                    <span className="text-red-700">
                      {run.validators_failed} ✗
                    </span>
                  </td>
                  <td className="px-3 py-2 text-right">
                    <Link
                      href={`/runs/${encodeURIComponent(run.run_id)}`}
                      className="text-blue-600 hover:underline"
                    >
                      Open →
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <Pagination
        basePath="/runs"
        query={{
          servicer,
          from_date: fromDate || undefined,
          to_date: toDate || undefined,
        }}
        total={data.pagination.total}
        limit={data.pagination.limit}
        offset={data.pagination.offset}
      />
    </section>
  );
}
