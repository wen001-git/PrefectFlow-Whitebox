"use client";

import type { SheetDiff } from "@/lib/api";

export function DiffSheetTabs({
  sheets,
  active,
  onSelect,
}: {
  sheets: SheetDiff[];
  active: string | null;
  onSelect: (sheetName: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-1 border-b border-gray-200">
      {sheets.map((s) => {
        const isActive = s.sheet_name === active;
        const changed = s.cells_changed;
        return (
          <button
            key={s.sheet_name}
            type="button"
            onClick={() => onSelect(s.sheet_name)}
            className={`-mb-px rounded-t border border-b-0 px-3 py-1.5 text-xs ${
              isActive
                ? "border-gray-200 bg-white font-semibold text-slate-900"
                : "border-transparent bg-slate-50 text-slate-600 hover:bg-slate-100"
            }`}
          >
            <span className="font-mono">{s.sheet_name}</span>
            <span
              className={`ml-2 rounded px-1 text-[10px] ${
                changed > 0
                  ? "bg-red-100 text-red-800"
                  : "bg-green-100 text-green-800"
              }`}
            >
              {changed}
            </span>
          </button>
        );
      })}
    </div>
  );
}
