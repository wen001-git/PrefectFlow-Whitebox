"use client";

import { useEffect, useMemo, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  MarkerType,
  type Edge,
  type Node,
  type NodeMouseHandler,
} from "reactflow";
import "reactflow/dist/style.css";

import {
  apiGet,
  type LineageField,
  type LineageGraph as LineageGraphPayload,
  type LineageNode,
} from "@/lib/api";
import { layoutLineage } from "@/lib/lineageLayout";
import { FieldPicker } from "./FieldPicker";
import {
  LineageNodeCard,
  type LineageNodeRenderData,
} from "./LineageNodeCard";
import { LineageSidePanel } from "./LineageSidePanel";

// Register the one custom node type once at module scope. react-flow
// requires this object identity to stay stable across renders.
const NODE_TYPES = { lineage: LineageNodeCard } as const;

const RELATION_COLOR: Record<string, string> = {
  reads: "#0284c7",
  writes: "#d97706",
  derives: "#059669",
};

export function LineageGraph({ fields }: { fields: LineageField[] }) {
  const [selected, setSelected] = useState<string | null>(
    fields[0]?.field_id ?? null,
  );
  const [graph, setGraph] = useState<LineageGraphPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeNodeId, setActiveNodeId] = useState<string | null>(null);

  useEffect(() => {
    if (!selected) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    apiGet<LineageGraphPayload>(
      `/api/v1/lineage/fields/${encodeURIComponent(selected)}`,
    )
      .then((g) => {
        if (cancelled) return;
        setGraph(g);
        setActiveNodeId(null);
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : String(e));
        setGraph(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selected]);

  const { rfNodes, rfEdges, lookup } = useMemo(() => {
    if (!graph) {
      return {
        rfNodes: [] as Node<LineageNodeRenderData>[],
        rfEdges: [] as Edge[],
        lookup: new Map<string, LineageNode>(),
      };
    }
    const { nodes: positioned } = layoutLineage(graph.nodes, graph.edges);
    const map = new Map<string, LineageNode>();
    const nodes: Node<LineageNodeRenderData>[] = positioned.map((n) => {
      map.set(n.id, n);
      return {
        id: n.id,
        type: "lineage",
        position: n.position,
        data: {
          ...n.data,
          kind: n.type,
          isSelected: n.id === activeNodeId,
        },
      };
    });
    const edges: Edge[] = graph.edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      label: e.relation,
      labelStyle: { fontSize: 10, fill: "#475569" },
      labelBgPadding: [4, 2],
      labelBgBorderRadius: 4,
      labelBgStyle: { fill: "#f8fafc", stroke: "#e2e8f0" },
      animated: e.relation === "writes",
      style: {
        stroke: RELATION_COLOR[e.relation] ?? "#64748b",
        strokeWidth: 1.5,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: RELATION_COLOR[e.relation] ?? "#64748b",
      },
    }));
    return { rfNodes: nodes, rfEdges: edges, lookup: map };
  }, [graph, activeNodeId]);

  const onNodeClick: NodeMouseHandler = (_e, n) => {
    setActiveNodeId(n.id);
  };

  const activeNode = activeNodeId ? lookup.get(activeNodeId) ?? null : null;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <FieldPicker
          fields={fields}
          selected={selected}
          onChange={setSelected}
        />
        <LegendStrip />
      </div>
      {error && (
        <div className="rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">
          Failed to load lineage: {error}
        </div>
      )}
      <div className="grid grid-cols-1 gap-3 lg:grid-cols-[1fr_300px]">
        <div className="h-[520px] w-full rounded border border-gray-200 bg-white">
          {loading && (
            <div className="flex h-full items-center justify-center text-sm text-gray-500">
              Loading lineage…
            </div>
          )}
          {!loading && graph && (
            <ReactFlow
              nodes={rfNodes}
              edges={rfEdges}
              nodeTypes={NODE_TYPES}
              onNodeClick={onNodeClick}
              fitView
              proOptions={{ hideAttribution: true }}
            >
              <Background gap={16} />
              <Controls showInteractive={false} />
            </ReactFlow>
          )}
          {!loading && !graph && !error && (
            <div className="flex h-full items-center justify-center text-sm text-gray-500">
              Pick a field to render its lineage.
            </div>
          )}
        </div>
        <LineageSidePanel
          node={activeNode}
          onClose={() => setActiveNodeId(null)}
        />
      </div>
    </div>
  );
}

function LegendStrip() {
  const items: { color: string; label: string }[] = [
    { color: "bg-sky-200", label: "source-table" },
    { color: "bg-violet-200", label: "transform-step" },
    { color: "bg-amber-200", label: "validator" },
    { color: "bg-rose-200", label: "sheet-cell" },
    { color: "bg-emerald-200", label: "sheet" },
  ];
  return (
    <ul className="flex flex-wrap items-center gap-2 text-[10px] text-gray-600">
      {items.map((i) => (
        <li key={i.label} className="flex items-center gap-1">
          <span className={`inline-block h-2.5 w-2.5 rounded ${i.color}`} />
          {i.label}
        </li>
      ))}
    </ul>
  );
}
