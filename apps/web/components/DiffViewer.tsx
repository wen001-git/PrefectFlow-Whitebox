"use client";

import { useMemo, useState } from "react";

import type { DiffCell, DiffResponse } from "@/lib/api";
import { severityOfKind, severityRank } from "@/lib/diffSeverity";
import { DiffCellDetailPanel } from "./DiffCellDetailPanel";
import { DiffGrid, type SeverityFilter } from "./DiffGrid";
import { DiffSheetTabs } from "./DiffSheetTabs";
import { DiffSummaryBar } from "./DiffSummaryBar";

function classifySheet(
  cellsChanged: number,
  worstSeverity: number,
): "identical" | "minor" | "major" {
  if (cellsChanged === 0) return "identical";
  // worstSeverity uses severityRank: minor=1, missing=2, major=3.
  if (worstSeverity >= severityRank("major")) return "major";
  return "minor";
}

export function DiffViewer({ diff }: { diff: DiffResponse }) {
  const [activeSheet, setActiveSheet] = useState<string | null>(
    diff.sheets[0]?.sheet_name ?? null,
  );
  const [activeCell, setActiveCell] = useState<DiffCell | null>(null);
  const [hideIdentical, setHideIdentical] = useState<boolean>(true);
  const [severityFilter, setSeverityFilter] = useState<SeverityFilter>("all");

  const sheetBuckets = useMemo(() => {
    let major = 0;
    let minor = 0;
    let identical = 0;
    for (const s of diff.sheets) {
      const worst = s.cells.reduce(
        (acc, c) => Math.max(acc, severityRank(severityOfKind(c.kind))),
        0,
      );
      const cls = classifySheet(s.cells_changed, worst);
      if (cls === "major") major += 1;
      else if (cls === "minor") minor += 1;
      else identical += 1;
    }
    return { major, minor, identical };
  }, [diff]);

  const current =
    diff.sheets.find((s) => s.sheet_name === activeSheet) ?? diff.sheets[0];

  return (
    <div className="space-y-4">
      <DiffSummaryBar
        diff={diff}
        majorSheets={sheetBuckets.major}
        minorSheets={sheetBuckets.minor}
        identicalSheets={sheetBuckets.identical}
      />

      <div className="flex flex-wrap items-center gap-3 text-xs">
        <label className="inline-flex items-center gap-1.5">
          <input
            type="checkbox"
            checked={hideIdentical}
            onChange={(e) => setHideIdentical(e.target.checked)}
          />
          Hide identical
        </label>
        <label className="inline-flex items-center gap-1.5">
          <span>Severity:</span>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value as SeverityFilter)}
            className="rounded border border-gray-300 px-1.5 py-0.5"
          >
            <option value="all">all</option>
            <option value="minor+">minor+</option>
            <option value="major-only">major-only</option>
          </select>
        </label>
      </div>

      {diff.sheets.length > 0 && (
        <DiffSheetTabs
          sheets={diff.sheets}
          active={current?.sheet_name ?? null}
          onSelect={(name) => {
            setActiveSheet(name);
            setActiveCell(null);
          }}
        />
      )}

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-[1fr_320px]">
        <div>
          {current ? (
            <DiffGrid
              sheet={current}
              activeCellRef={activeCell?.cell_ref ?? null}
              onCellClick={setActiveCell}
              hideIdentical={hideIdentical}
              severityFilter={severityFilter}
            />
          ) : (
            <div className="rounded border border-dashed border-gray-300 p-6 text-center text-sm text-gray-500">
              No sheet diffs in the report.
            </div>
          )}
        </div>
        <DiffCellDetailPanel
          cell={activeCell}
          onClose={() => setActiveCell(null)}
        />
      </div>
    </div>
  );
}
