"use client";

import type { LineageNode } from "@/lib/api";
import { LINEAGE_KIND_STYLES } from "./LineageNodeCard";

export function LineageSidePanel({
  node,
  onClose,
}: {
  node: LineageNode | null;
  onClose: () => void;
}) {
  if (!node) {
    return (
      <aside className="h-full rounded border border-dashed border-gray-300 p-4 text-xs text-gray-500">
        Click a node in the graph to inspect its metadata here.
      </aside>
    );
  }
  const s = LINEAGE_KIND_STYLES[node.type];
  return (
    <aside className="h-full overflow-y-auto rounded border border-gray-200 bg-white p-4 text-sm shadow-sm">
      <div className="flex items-start justify-between gap-2">
        <div>
          <span
            className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${s.chip}`}
          >
            {s.label}
          </span>
          <h2 className="mt-1 break-words font-mono text-sm font-semibold">
            {node.data.label}
          </h2>
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
          <dt className="text-[10px] uppercase text-gray-500">Node id</dt>
          <dd className="break-all font-mono">{node.id}</dd>
        </div>
        <div>
          <dt className="text-[10px] uppercase text-gray-500">Kind</dt>
          <dd>{node.type}</dd>
        </div>
        {node.data.detail && (
          <div>
            <dt className="text-[10px] uppercase text-gray-500">Detail</dt>
            <dd className="whitespace-pre-wrap text-slate-700">
              {node.data.detail}
            </dd>
          </div>
        )}
      </dl>
    </aside>
  );
}
