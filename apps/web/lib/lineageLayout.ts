// Simple BFS column-layering for the lineage graph.
//
// HARD RESTRAINT (AGENTS § 6.14): NO dagre / elkjs / d3-anything. The
// fixture graphs are small (<50 nodes) and we only need a stable
// left-to-right layering. If we ever need real DAG layout, propose an
// ADR before pulling in a layout library.
//
// Algorithm:
//   1. Build adjacency + indegree maps from the edge list.
//   2. Roots = nodes with indegree 0 → column 0.
//   3. BFS outward: a successor's column = max(successor's current col,
//      predecessor.col + 1).
//   4. Nodes still at col 0 after BFS (e.g. disconnected) stay at col 0.
//   5. Distribute Y within each column evenly around the vertical center
//      so columns of different sizes stay visually balanced.
//
// Returns nodes with overwritten {position: {x, y}} ready for react-flow.

import type { LineageEdge, LineageNode } from "./api";

const COL_WIDTH = 240;
const ROW_HEIGHT = 110;
const TOP_PAD = 20;

export type PositionedLineageNode = LineageNode;

export function layoutLineage(
  nodes: readonly LineageNode[],
  edges: readonly LineageEdge[],
): { nodes: PositionedLineageNode[] } {
  if (nodes.length === 0) return { nodes: [] };

  const succ = new Map<string, string[]>();
  const indeg = new Map<string, number>();
  for (const n of nodes) {
    succ.set(n.id, []);
    indeg.set(n.id, 0);
  }
  for (const e of edges) {
    if (!succ.has(e.source) || !succ.has(e.target)) continue;
    succ.get(e.source)!.push(e.target);
    indeg.set(e.target, (indeg.get(e.target) ?? 0) + 1);
  }

  const col = new Map<string, number>();
  const queue: string[] = [];
  for (const n of nodes) {
    if ((indeg.get(n.id) ?? 0) === 0) {
      col.set(n.id, 0);
      queue.push(n.id);
    }
  }
  // Guard against pure cycles (no indegree-0 nodes): pin first node.
  if (queue.length === 0) {
    col.set(nodes[0].id, 0);
    queue.push(nodes[0].id);
  }

  // Iteration cap = nodes.length * (max possible depth) — defensive
  // against cycles introducing infinite revisits.
  let safety = nodes.length * nodes.length + 1;
  while (queue.length > 0 && safety-- > 0) {
    const id = queue.shift()!;
    const c = col.get(id) ?? 0;
    for (const child of succ.get(id) ?? []) {
      const next = c + 1;
      if (next > (col.get(child) ?? -1)) {
        col.set(child, next);
        queue.push(child);
      }
    }
  }

  // Group node ids per column (preserving original order for stability).
  const byCol = new Map<number, string[]>();
  for (const n of nodes) {
    const c = col.get(n.id) ?? 0;
    if (!byCol.has(c)) byCol.set(c, []);
    byCol.get(c)!.push(n.id);
  }

  const maxRows = Math.max(...Array.from(byCol.values(), (v) => v.length));
  const centerY = TOP_PAD + ((maxRows - 1) * ROW_HEIGHT) / 2;

  const positioned: PositionedLineageNode[] = nodes.map((n) => {
    const c = col.get(n.id) ?? 0;
    const colNodes = byCol.get(c) ?? [n.id];
    const idx = colNodes.indexOf(n.id);
    const yOffset = (idx - (colNodes.length - 1) / 2) * ROW_HEIGHT;
    return {
      ...n,
      position: { x: c * COL_WIDTH, y: centerY + yOffset },
    };
  });

  return { nodes: positioned };
}
