// Severity classification for the XLSX-vs-XLSX diff viewer.
//
// Maps DiffKind (from whitebox/api/schemas.py — mirrors xlsx_diff.py)
// onto a 4-tier severity scale used by the diff grid color coding:
//
//   major   — value / type differs (red)
//   minor   — format-only differs (yellow)
//   missing — present on only one side (grey)
//   identical — both sides equal (green)
//
// The fixture diff payload only contains *differing* cells (identical
// cells are omitted by the backend), so "identical" is only used when
// the FE synthesises an identical row for visual completeness.

import type { DiffKind } from "./api";
import type { SemanticStyle } from "./styleMap";

export type DiffSeverity = "identical" | "minor" | "major" | "missing";

export function severityOfKind(kind: DiffKind): DiffSeverity {
  switch (kind) {
    case "format":
      return "minor";
    case "missing_left":
    case "missing_right":
      return "missing";
    case "value":
    case "type":
    default:
      return "major";
  }
}

export function severityToStyle(s: DiffSeverity): SemanticStyle {
  switch (s) {
    case "identical":
      return "diff-identical";
    case "minor":
      return "diff-minor";
    case "major":
      return "diff-major";
    case "missing":
      return "diff-missing";
  }
}

export function severityRank(s: DiffSeverity): number {
  // Higher = more severe. Used by the "severity filter" dropdown
  // (all / minor+ / major-only).
  switch (s) {
    case "identical":
      return 0;
    case "minor":
      return 1;
    case "missing":
      return 2;
    case "major":
      return 3;
  }
}
