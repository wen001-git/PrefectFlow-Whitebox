"use client";

import type { DiffCell, SheetDiff } from "@/lib/api";
import {
  severityOfKind,
  severityRank,
  severityToStyle,
  type DiffSeverity,
} from "@/lib/diffSeverity";
import { contentClass } from "@/lib/styleMap";

function formatValue(v: DiffCell["left"]): string {
  if (v === null || v === undefined) return "—";
  if (typeof v === "number") return Number.isInteger(v) ? String(v) : v.toFixed(4);
  if (typeof v === "boolean") return v ? "TRUE" : "FALSE";
  return v;
}

export type SeverityFilter = "all" | "minor+" | "major-only";

export function DiffGrid({
  sheet,
  activeCellRef,
  onCellClick,
  hideIdentical,
  severityFilter,
}: {
  sheet: SheetDiff;
  activeCellRef: string | null;
  onCellClick: (cell: DiffCell) => void;
  hideIdentical: boolean;
  severityFilter: SeverityFilter;
}) {
  const filtered = sheet.cells.filter((c) => {
    const sev = severityOfKind(c.kind);
    if (hideIdentical && sev === "identical") return false;
    if (severityFilter === "minor+" && severityRank(sev) < severityRank("minor"))
      return false;
    if (severityFilter === "major-only" && sev !== "major") return false;
    return true;
  });

  if (filtered.length === 0) {
    return (
      <div className="rounded border border-dashed border-gray-300 p-6 text-center text-sm text-gray-500">
        No diff cells match the current filter on{" "}
        <span className="font-mono">{sheet.sheet_name}</span>.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded border border-gray-200">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50 text-left text-xs uppercase text-slate-600">
          <tr>
            <th className="px-3 py-2">Cell</th>
            <th className="px-3 py-2">Column</th>
            <th className="px-3 py-2">Left (baseline)</th>
            <th className="px-3 py-2">Right (new)</th>
            <th className="px-3 py-2">Kind</th>
            <th className="px-3 py-2">Severity</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((c) => {
            const sev: DiffSeverity = severityOfKind(c.kind);
            const rowStyle = contentClass(severityToStyle(sev));
            const isActive = c.cell_ref === activeCellRef;
            const missingLeft = c.kind === "missing_left";
            const missingRight = c.kind === "missing_right";
            return (
              <tr
                key={`${c.sheet}:${c.cell_ref}`}
                onClick={() => onCellClick(c)}
                className={`cursor-pointer border-t border-gray-100 ${rowStyle} ${
                  isActive ? "outline outline-2 outline-blue-500" : ""
                }`}
              >
                <td className="px-3 py-2 font-mono text-xs">{c.cell_ref}</td>
                <td className="px-3 py-2 font-mono text-xs">
                  {c.column_id ?? "—"}
                </td>
                <td
                  className={`px-3 py-2 font-mono text-xs ${
                    missingLeft ? contentClass("diff-missing") : ""
                  }`}
                >
                  {formatValue(c.left)}
                </td>
                <td
                  className={`px-3 py-2 font-mono text-xs ${
                    missingRight ? contentClass("diff-missing") : ""
                  }`}
                >
                  {formatValue(c.right)}
                </td>
                <td className="px-3 py-2 text-xs">{c.kind}</td>
                <td className="px-3 py-2 text-xs font-semibold capitalize">
                  {sev}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
