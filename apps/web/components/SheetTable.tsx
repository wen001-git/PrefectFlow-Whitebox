import Link from "next/link";

import type { SheetCell, SheetData } from "@/lib/api";
import {
  cellStyleFor,
  contentClass,
  headerStyleFor,
  styleClass,
} from "@/lib/styleMap";

// Renders a SheetData → <table>. Each <td> is a Next.js <Link> to the
// cell drill-down (?cell=A1), which CellDetailPanel listens to on the
// client side. Server-rendered so initial paint shows all data.
export function SheetTable({
  data,
  basePath,
  activeCellRef,
}: {
  data: SheetData;
  basePath: string;
  activeCellRef?: string;
}) {
  const highlightByRef = new Map<string, SheetCell>(
    data.highlighted_cells.map((c) => [c.cell_ref, c]),
  );

  const buildHref = (cellRef: string) => {
    const params = new URLSearchParams();
    params.set("cell", cellRef);
    return `${basePath}?${params.toString()}`;
  };

  return (
    <div className="overflow-auto rounded border border-gray-200">
      <table className="min-w-full border-collapse">
        <thead>
          <tr>
            <th className={styleClass("header")} scope="col">
              #
            </th>
            {data.columns.map((col) => (
              <th
                key={col.id}
                scope="col"
                className={styleClass(
                  headerStyleFor({
                    dtype: col.dtype,
                    isHighlightColumn: col.is_highlight,
                  }),
                )}
                title={col.id}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.rows.map((row) => (
            <tr key={row.row_index} className="hover:bg-slate-50">
              <td
                className={`${styleClass("header")} text-right`}
                scope="row"
              >
                {row.row_index}
              </td>
              {data.columns.map((col, colIdx) => {
                // openpyxl A1 notation: column index 0 -> "A", row 1 ->
                // first data row. The "+1" on row accounts for the
                // header row offset that the renderer applies.
                const cellRef = `${columnLetter(colIdx + 1)}${row.row_index + 1}`;
                const value = row.values[col.id];
                const hl = highlightByRef.get(cellRef);
                const style = cellStyleFor({
                  dtype: col.dtype,
                  isHighlightCell: hl?.is_highlight ?? false,
                  isHighlightColumn: col.is_highlight,
                });
                const isActive = activeCellRef === cellRef;
                return (
                  <td
                    key={col.id}
                    className={`${styleClass(style)} ${
                      isActive ? "ring-2 ring-blue-500 ring-inset" : ""
                    }`}
                    data-cell-ref={cellRef}
                  >
                    <Link
                      href={buildHref(cellRef)}
                      prefetch={false}
                      scroll={false}
                      className={`${contentClass(style)} block hover:underline`}
                    >
                      {formatValue(value)}
                    </Link>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function formatValue(v: unknown): string {
  if (v === null || v === undefined) return "";
  if (typeof v === "number") {
    return Number.isInteger(v) ? v.toLocaleString() : v.toLocaleString();
  }
  return String(v);
}

// 1-indexed openpyxl-style column letter (1 -> A, 26 -> Z, 27 -> AA).
function columnLetter(idx: number): string {
  let n = idx;
  let s = "";
  while (n > 0) {
    const rem = (n - 1) % 26;
    s = String.fromCharCode(65 + rem) + s;
    n = Math.floor((n - 1) / 26);
  }
  return s;
}
