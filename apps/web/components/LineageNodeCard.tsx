"use client";

import { Handle, Position, type NodeProps } from "reactflow";

import type { LineageNodeData, LineageNodeKind } from "@/lib/api";

// Color + icon vocabulary per node kind. Kept here (not styleMap.ts)
// because it's lineage-graph-specific UI chrome, not legacy XLSX
// semantic styling. styleMap.ts owns the renderer-vs-FE shared
// vocabulary; this owns react-flow node chrome.
const KIND_STYLES: Record<
  LineageNodeKind,
  { border: string; bg: string; chip: string; icon: string; label: string }
> = {
  source: {
    border: "border-sky-400",
    bg: "bg-sky-50",
    chip: "bg-sky-200 text-sky-900",
    icon: "▣",
    label: "source-table",
  },
  transform: {
    border: "border-violet-400",
    bg: "bg-violet-50",
    chip: "bg-violet-200 text-violet-900",
    icon: "ƒ",
    label: "transform-step",
  },
  validator: {
    border: "border-amber-400",
    bg: "bg-amber-50",
    chip: "bg-amber-200 text-amber-900",
    icon: "✓",
    label: "validator",
  },
  sheet: {
    border: "border-emerald-400",
    bg: "bg-emerald-50",
    chip: "bg-emerald-200 text-emerald-900",
    icon: "▦",
    label: "sheet",
  },
  field: {
    border: "border-rose-400",
    bg: "bg-rose-50",
    chip: "bg-rose-200 text-rose-900",
    icon: "◉",
    label: "sheet-cell",
  },
};

export type LineageNodeRenderData = LineageNodeData & {
  kind: LineageNodeKind;
  isSelected?: boolean;
};

export function LineageNodeCard(props: NodeProps<LineageNodeRenderData>) {
  const s = KIND_STYLES[props.data.kind];
  const selected = props.data.isSelected
    ? "ring-2 ring-offset-1 ring-blue-500"
    : "";
  return (
    <div
      className={`min-w-[180px] max-w-[220px] rounded-md border ${s.border} ${s.bg} px-3 py-2 text-xs shadow-sm ${selected}`}
    >
      <Handle type="target" position={Position.Left} />
      <div className="flex items-center gap-1.5">
        <span
          className={`inline-flex h-5 w-5 items-center justify-center rounded ${s.chip} text-sm font-semibold`}
          aria-hidden
        >
          {s.icon}
        </span>
        <span
          className={`rounded px-1 text-[10px] font-semibold uppercase tracking-wide ${s.chip}`}
        >
          {s.label}
        </span>
      </div>
      <div
        className="mt-1 break-words font-mono text-[11px] font-medium text-slate-800"
        title={props.data.label}
      >
        {props.data.label}
      </div>
      {props.data.detail && (
        <div className="mt-0.5 line-clamp-2 text-[10px] text-slate-500">
          {props.data.detail}
        </div>
      )}
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

export { KIND_STYLES as LINEAGE_KIND_STYLES };
