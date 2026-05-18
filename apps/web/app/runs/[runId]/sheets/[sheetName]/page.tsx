import Link from "next/link";

import { CellDetailPanel } from "@/components/CellDetailPanel";
import { SheetTable } from "@/components/SheetTable";
import { apiGet, type SheetData } from "@/lib/api";

export default async function SheetPage({
  params,
  searchParams,
}: {
  params: { runId: string; sheetName: string };
  searchParams: { cell?: string };
}) {
  const runId = decodeURIComponent(params.runId);
  const sheetName = decodeURIComponent(params.sheetName);
  const cellRef = searchParams.cell;

  const data = await apiGet<SheetData>(
    `/api/v1/runs/${encodeURIComponent(runId)}/sheets/${encodeURIComponent(sheetName)}`,
  );

  const basePath = `/runs/${encodeURIComponent(runId)}/sheets/${encodeURIComponent(sheetName)}`;

  return (
    <section className="space-y-4">
      <header className="space-y-1">
        <div className="text-xs">
          <Link
            href={`/runs/${encodeURIComponent(runId)}`}
            className="text-blue-600 hover:underline"
          >
            ← Back to run
          </Link>
        </div>
        <h1 className="text-2xl font-semibold">
          {data.title || data.sheet_name}
        </h1>
        <p className="font-mono text-xs text-gray-500">
          {data.sheet_name} · {data.rows.length} rows · {data.columns.length}{" "}
          columns · {data.highlighted_cells.length} highlight cells
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <SheetTable
          data={data}
          basePath={basePath}
          activeCellRef={cellRef}
        />
        <CellDetailPanel
          runId={runId}
          sheetName={sheetName}
          cellRef={cellRef}
        />
      </div>
    </section>
  );
}
