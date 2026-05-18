// TODO: d-ui-core-screens will replace this placeholder with the cell-level
// XLSX diff viewer (baseline vs run output).
export default function DiffPage({
  params,
}: {
  params: { runId: string };
}) {
  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Diff viewer</h1>
      <p className="text-sm text-gray-600">
        Run <code>{params.runId}</code> — placeholder diff viewer.
      </p>
    </section>
  );
}
