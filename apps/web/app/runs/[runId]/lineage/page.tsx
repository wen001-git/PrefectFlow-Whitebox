"use client";

import ReactFlow, { Background, Controls, type Edge, type Node } from "reactflow";
import "reactflow/dist/style.css";

// TODO: d-ui-core-screens will replace this placeholder with the real
// registry-driven lineage graph (validators -> transforms -> sources).
const nodes: Node[] = [
  { id: "src", position: { x: 0, y: 0 }, data: { label: "source" } },
  { id: "xform", position: { x: 200, y: 0 }, data: { label: "transform" } },
  { id: "sheet", position: { x: 400, y: 0 }, data: { label: "sheet" } },
];

const edges: Edge[] = [
  { id: "e1", source: "src", target: "xform" },
  { id: "e2", source: "xform", target: "sheet" },
];

export default function LineagePage() {
  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Lineage</h1>
      <p className="text-sm text-gray-600">
        Placeholder — react-flow demo with 3 nodes.
      </p>
      <div className="h-[400px] w-full rounded border">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </section>
  );
}
