import Link from "next/link";

import { DiffViewer } from "@/components/DiffViewer";
import { RunComparisonPicker } from "@/components/RunComparisonPicker";
import {
  apiGet,
  type DiffResponse,
  type RunDetail,
  type RunListResponse,
} from "@/lib/api";

type SearchParams = { against?: string };

export default async function DiffPage({
  params,
  searchParams,
}: {
  params: { runId: string };
  searchParams: SearchParams;
}) {
  const runId = decodeURIComponent(params.runId);
  const against = searchParams.against;

  if (!against) {
    // Need to pick a comparison run. Fetch this run's servicer first
    // so the candidate list is scoped to the same servicer.
    const detail = await apiGet<RunDetail>(
      `/api/v1/runs/${encodeURIComponent(runId)}`,
    );
    const qs = new URLSearchParams({
      servicer: detail.servicer,
      limit: "50",
      offset: "0",
    });
    const list = await apiGet<RunListResponse>(`/api/v1/runs?${qs.toString()}`);
    return (
      <section className="space-y-4">
        <Header runId={runId} against={null} />
        <RunComparisonPicker runId={runId} candidates={list.runs} />
      </section>
    );
  }

  const diff = await apiGet<DiffResponse>(
    `/api/v1/runs/${encodeURIComponent(runId)}/diff?against=${encodeURIComponent(against)}`,
  );

  return (
    <section className="space-y-4">
      <Header runId={runId} against={against} />
      <DiffViewer diff={diff} />
    </section>
  );
}

function Header({ runId, against }: { runId: string; against: string | null }) {
  return (
    <header className="flex flex-wrap items-baseline justify-between gap-2">
      <div>
        <h1 className="text-2xl font-semibold">XLSX diff viewer</h1>
        <p className="text-xs text-gray-500">
          Run <span className="font-mono">{runId}</span>
          {against ? (
            <>
              {" "}vs <span className="font-mono">{against}</span>
              <Link
                href={`/runs/${encodeURIComponent(runId)}/diff`}
                className="ml-2 text-blue-600 hover:underline"
              >
                change
              </Link>
            </>
          ) : (
            " — pick a comparison run below."
          )}
        </p>
      </div>
      <Link
        href={`/runs/${encodeURIComponent(runId)}`}
        className="text-sm text-blue-600 hover:underline"
      >
        ← Back to run
      </Link>
    </header>
  );
}
