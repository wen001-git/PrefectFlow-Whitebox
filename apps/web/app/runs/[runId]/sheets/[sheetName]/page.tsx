// TODO: d-ui-core-screens will replace this placeholder with the per-sheet
// drill-down view (cell grid + validator pass/fail panel).
export default function SheetPage({
  params,
}: {
  params: { runId: string; sheetName: string };
}) {
  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">
        Sheet: {params.sheetName}
      </h1>
      <p className="text-sm text-gray-600">
        Run <code>{params.runId}</code> — placeholder per-sheet page.
      </p>
    </section>
  );
}
