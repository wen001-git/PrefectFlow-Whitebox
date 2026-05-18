import Link from "next/link";

import { LineageGraph } from "@/components/LineageGraph";
import {
  apiGet,
  type LineageFieldListResponse,
} from "@/lib/api";

export default async function LineagePage({
  params,
}: {
  params: { runId: string };
}) {
  const runId = decodeURIComponent(params.runId);
  const fieldList = await apiGet<LineageFieldListResponse>(
    "/api/v1/lineage/fields",
  );

  return (
    <section className="space-y-4">
      <header className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <h1 className="text-2xl font-semibold">Field lineage</h1>
          <p className="text-xs text-gray-500">
            Run <span className="font-mono">{runId}</span> — backward sources +
            forward consumers for a chosen output field.
          </p>
        </div>
        <Link
          href={`/runs/${encodeURIComponent(runId)}`}
          className="text-sm text-blue-600 hover:underline"
        >
          ← Back to run
        </Link>
      </header>

      {fieldList.fields.length === 0 ? (
        <p className="rounded border border-dashed border-gray-300 p-6 text-center text-sm text-gray-500">
          No lineage-known fields registered yet.
        </p>
      ) : (
        <LineageGraph fields={fieldList.fields} />
      )}
    </section>
  );
}
