// Centralized semantic style class -> Tailwind class mapping.
//
// Background — the legacy XLSX renderer (and its Stage 2 successor,
// whitebox/renderer) tags cells with a small vocabulary of *semantic*
// style names. The FE intentionally does NOT inline Tailwind classes
// next to data — instead it asks `styleClass(name)` so:
//
//   1. The mapping stays in ONE place. When the renderer's vocabulary
//      grows ("subtotal", "negative", "warning") we add one line here.
//   2. Switching design systems (Tailwind → CSS modules → tokens) is a
//      single-file change.
//   3. Tests can assert "every renderer style name has a FE mapping"
//      against this object's keys.
//
// HARD RESTRAINT (AGENTS § 6.14): no clsx, classnames, cva, twMerge.
// Plain string composition only.
//
// Source of truth for the vocabulary:
//   - docs/stage2/1.3-mrc-sheets.md (header / highlight / money / pct)
//   - docs/stage2/1.6-baseline.en.md § 3 (ffc7ce highlight = "diff")
//   - whitebox/renderer (todo P2.5) — will codify the same names.

export type SemanticStyle =
  | "header"        // tab header row — bold, slate background
  | "header-diff"   // header on a highlight column — keeps header weight + diff bg
  | "header-money" // header on a numeric/$ column — right-aligned
  | "money"         // numeric value cell — right-align + tabular nums
  | "pct"           // percentage value cell — right-align + tabular nums
  | "diff"          // ffc7ce highlight — legacy "differs from baseline"
  | "muted"         // suppressed / informational cell
  | "text"          // plain text cell (default)
  | "cell";         // structural <td>/<th> baseline (border, padding)

const MAP: Record<SemanticStyle, string> = {
  cell: "border border-gray-200 px-2 py-1 text-sm align-top",
  text: "text-left",
  header:
    "bg-slate-100 font-semibold text-slate-800 text-left whitespace-nowrap",
  "header-diff":
    "bg-[#ffc7ce] font-semibold text-[#9b1c1c] text-left whitespace-nowrap",
  "header-money":
    "bg-slate-100 font-semibold text-slate-800 text-right whitespace-nowrap tabular-nums",
  money: "text-right tabular-nums",
  pct: "text-right tabular-nums",
  // ffc7ce + df5006 are the legacy XLSX highlight colors
  // (1.3 mrc-sheets § 4.3 / 1.6 baseline § 3). Reproduced here so the
  // browser view matches the eventual XLSX export pixel-for-pixel.
  diff: "bg-[#ffc7ce] text-[#df5006] font-medium",
  muted: "text-gray-400 italic",
};

export function styleClass(name: SemanticStyle | undefined): string {
  if (!name) return MAP.cell;
  return `${MAP.cell} ${MAP[name]}`;
}

// Returns just the *content* class (no cell-baseline) for cases where
// the consumer composes its own <td>/<th> (e.g. SheetTable header row
// already adds its own border/padding via the cell baseline).
export function contentClass(name: SemanticStyle | undefined): string {
  if (!name) return MAP.text;
  return MAP[name];
}

// Heuristic: pick a sensible class for a data cell given column dtype +
// highlight flags. Centralized so SheetTable doesn't grow ad-hoc logic.
export function cellStyleFor(opts: {
  dtype?: string;
  isHighlightCell?: boolean;
  isHighlightColumn?: boolean;
}): SemanticStyle {
  if (opts.isHighlightCell) return "diff";
  if (opts.dtype === "number" || opts.dtype === "integer") return "money";
  return "text";
}

export function headerStyleFor(opts: {
  dtype?: string;
  isHighlightColumn?: boolean;
}): SemanticStyle {
  if (opts.isHighlightColumn) return "header-diff";
  if (opts.dtype === "number" || opts.dtype === "integer") return "header-money";
  return "header";
}
