// Typed fetch wrapper for the Stage 2 FastAPI backend.
// HARD RESTRAINT (architecture § 5): do NOT replace with React Query / SWR /
// tRPC. If caching/retries become a real need, propose an ADR:
//   "ADR: introduce a client data-fetching layer for apps/web".
//
// The schema types below mirror the pydantic models in
// `whitebox/api/schemas.py`. Keep them in sync; the OpenAPI snapshot test
// (`tests/api/test_contract_openapi_snapshot.py`) will fail if the backend
// surface drifts.

const DEFAULT_BASE = "http://localhost:8000";

function apiBase(): string {
  return process.env.NEXT_PUBLIC_API_BASE ?? DEFAULT_BASE;
}

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${apiBase()}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: { Accept: "application/json", ...(init?.headers ?? {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`GET ${url} failed: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

export async function apiPost<T>(
  path: string,
  body: unknown,
  init?: RequestInit,
): Promise<T> {
  const url = `${apiBase()}${path}`;
  const res = await fetch(url, {
    method: "POST",
    ...init,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(init?.headers ?? {}),
    },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`POST ${url} failed: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

// ---------------------------------------------------------------------------
// Typed contracts — mirror of whitebox/api/schemas.py
// ---------------------------------------------------------------------------

export type CellValue = string | number | boolean | null;

export type RunStatus = "pending" | "running" | "completed" | "failed";
export type DiffVerdict = "PASS" | "MINOR_DIFFS" | "MAJOR_DIFFS" | "ERROR";
export type DiffKind =
  | "value"
  | "missing_left"
  | "missing_right"
  | "type"
  | "format";
export type LineageNodeKind =
  | "source"
  | "transform"
  | "validator"
  | "sheet"
  | "field";
export type LineageEdgeRelation = "reads" | "writes" | "derives";
export type SheetColumnDtype =
  | "string"
  | "number"
  | "integer"
  | "boolean"
  | "date";

export type Pagination = {
  total: number;
  limit: number;
  offset: number;
};

export type ErrorDetail = {
  code: string;
  message: string;
  hint?: string | null;
};

export type ErrorResponse = { error: ErrorDetail };

export type HealthResponse = { status: "ok"; version: string };

// ----- Runs ---------------------------------------------------------------

export type RunSummary = {
  run_id: string;
  servicer: string;
  remit_date: string; // ISO yyyy-mm-dd
  status: RunStatus;
  created_at: string; // ISO 8601
  validators_passed: number;
  validators_failed: number;
};

export type SheetSummary = {
  sheet_name: string;
  title: string;
  tab_order: number;
  row_count: number;
  column_count: number;
  highlight_count: number;
};

export type RunDetail = RunSummary & {
  sheets: SheetSummary[];
  verdict: DiffVerdict;
  baseline_run_id?: string | null;
};

export type RunListResponse = {
  runs: RunSummary[];
  pagination: Pagination;
};

// ----- Sheets -------------------------------------------------------------

export type SheetColumn = {
  id: string;
  label: string;
  dtype: SheetColumnDtype;
  is_highlight: boolean;
};

export type SheetRow = {
  row_index: number;
  values: Record<string, CellValue>;
};

export type SheetCell = {
  row: number;
  column_id: string;
  cell_ref: string;
  value: CellValue;
  is_highlight: boolean;
  validator_id?: string | null;
};

export type SheetData = {
  run_id: string;
  sheet_name: string;
  title: string;
  columns: SheetColumn[];
  rows: SheetRow[];
  highlighted_cells: SheetCell[];
};

export type SheetListResponse = {
  run_id: string;
  sheets: SheetSummary[];
};

export type CellProvenance = {
  kind: LineageNodeKind;
  id: string;
  label: string;
  detail: string;
};

export type CellDetail = {
  run_id: string;
  sheet_name: string;
  cell: SheetCell;
  computed_expression?: string | null;
  provenance: CellProvenance[];
};

// ----- Diff ---------------------------------------------------------------

export type DiffCell = {
  sheet: string;
  cell_ref: string;
  column_id?: string | null;
  left: CellValue;
  right: CellValue;
  kind: DiffKind;
};

export type SheetDiff = {
  sheet_name: string;
  cells: DiffCell[];
  rows_added: number;
  rows_removed: number;
  cells_changed: number;
};

export type DiffResponse = {
  run_id: string;
  compared_to: string;
  verdict: DiffVerdict;
  total_cells_changed: number;
  sheets: SheetDiff[];
};

// ----- Lineage (react-flow consumable) ------------------------------------

export type LineageNodeData = { label: string; detail: string };
export type LineagePosition = { x: number; y: number };

export type LineageNode = {
  id: string;
  type: LineageNodeKind;
  data: LineageNodeData;
  position: LineagePosition;
};

export type LineageEdge = {
  id: string;
  source: string;
  target: string;
  relation: LineageEdgeRelation;
};

export type LineageGraph = {
  field_id: string;
  nodes: LineageNode[];
  edges: LineageEdge[];
};

export type LineageField = {
  field_id: string;
  servicer: string;
  sheet: string;
  label: string;
};

export type LineageFieldListResponse = { fields: LineageField[] };

// ----- Export (501 until renderer wiring lands) ---------------------------

export type ExportResponse = {
  run_id: string;
  format: "xlsx";
  download_url: string;
  byte_size: number;
  sha256: string;
};
