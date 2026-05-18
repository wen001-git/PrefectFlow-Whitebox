import { apiGet } from "@/lib/api";

type RunSummary = {
  run_id: string;
  status?: string;
  servicer?: string;
  remit_date?: string;
};

// TODO: d-ui-core-screens will replace this placeholder with the real
// run-details view (sheet list, validator pass/fail panel, artifacts).
export default async function RunPage({
  params,
}: {
  params: { runId: string };
}) {
  let data: RunSummary | { error: string };
  try {
    data = await apiGet<RunSummary>(`/api/v1/runs/${params.runId}`);
  } catch (err) {
    data = { error: err instanceof Error ? err.message : String(err) };
  }

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Run {params.runId}</h1>
      <p className="text-sm text-gray-600">
        Placeholder — fetched from FastAPI stub.
      </p>
      <pre className="rounded bg-gray-100 p-4 text-xs overflow-auto">
        {JSON.stringify(data, null, 2)}
      </pre>
      <ul className="list-disc pl-6 text-sm">
        <li>
          <a
            className="text-blue-600 underline"
            href={`/runs/${params.runId}/lineage`}
          >
            Lineage graph
          </a>
        </li>
        <li>
          <a
            className="text-blue-600 underline"
            href={`/runs/${params.runId}/diff`}
          >
            Diff viewer
          </a>
        </li>
      </ul>
    </section>
  );
}
