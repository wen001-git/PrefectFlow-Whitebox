"use client";

import type { DiffCell } from "@/lib/api";
import { severityOfKind, type DiffSeverity } from "@/lib/diffSeverity";
import { contentClass } from "@/lib/styleMap";

function formatValue(v: DiffCell["left"]): string {
  if (v === null || v === undefined) return "—";
  if (typeof v === "number") return Number.isInteger(v) ? String(v) : v.toFixed(4);
  if (typeof v === "boolean") return v ? "TRUE" : "FALSE";
  return v;
}

export function DiffCellDetailPanel({
  cell,
  onClose,
}: {
  cell: DiffCell | null;
  onClose: () => void;
}) {
  if (!cell) {
    return (
      <aside className="h-full rounded border border-dashed border-gray-300 p-4 text-xs text-gray-500">
        Click a cell in the diff grid to inspect both sides.
      </aside>
    );
  }
  const sev: DiffSeverity = severityOfKind(cell.kind);
  return (
    <aside className="h-full overflow-y-auto rounded border border-gray-200 bg-white p-4 text-sm shadow-sm">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h2 className="font-mono text-sm font-semibold">{cell.cell_ref}</h2>
          <p className="text-[11px] text-gray-500">{cell.sheet}</p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded border border-gray-200 px-1.5 text-xs text-gray-500 hover:bg-gray-50"
          aria-label="Close panel"
        >
          ×
        </button>
      </div>
      <dl className="mt-3 space-y-2 text-xs">
        <div>
          <dt className="text-[10px] uppercase text-gray-500">Severity</dt>
          <dd className="font-semibold capitalize">{sev}</dd>
        </div>
        <div>
          <dt className="text-[10px] uppercase text-gray-500">Diff kind</dt>
          <dd className="font-mono">{cell.kind}</dd>
        </div>
        {cell.column_id && (
          <div>
            <dt className="text-[10px] uppercase text-gray-500">Column id</dt>
            <dd className="font-mono">{cell.column_id}</dd>
          </div>
        )}
        <div className="grid grid-cols-2 gap-2">
          <div>
            <dt className="text-[10px] uppercase text-gray-500">Left (baseline)</dt>
            <dd
              className={`mt-0.5 rounded border border-gray-200 px-1.5 py-1 font-mono ${contentClass("muted")}`}
            >
              <span className="text-slate-800 not-italic">
                {formatValue(cell.left)}
              </span>
            </dd>
          </div>
          <div>
            <dt className="text-[10px] uppercase text-gray-500">Right (new)</dt>
            <dd className="mt-0.5 rounded border border-gray-200 px-1.5 py-1 font-mono">
              {formatValue(cell.right)}
            </dd>
          </div>
        </div>
      </dl>
    </aside>
  );
}
