# Test report — stage1-carrington (2026-05-17)

## Scope

Stage 1 chapter 1.2.1 — Carrington servicer. Delivered docs:

- `docs/validation-report-logic/carrington.zh.md` (29,715 chars, 13 headings)
- `docs/validation-report-logic/carrington.en.md` (37,131 chars, 13 headings)

Chapter covers: servicer overview, 4-stage dataflow branch (with mermaid + numbered step-by-step), per-sheet detailed generation logic for all 6 sheets (Summary / General / Advance / ServiceFee / Adv_Info / Trans_Info), cross-sheet validation field index, known pitfalls, and complete source citation index.

Also extended `tools/stage_doc_checks.py` PAIRS list to include the new pair.

## P0 checks

| # | Check | Command | Result |
|---|---|---|---|
| 1 | zh/en heading skeleton alignment | `python tools/stage_doc_checks.py` | ✅ ALIGN OK : 13 headings each |
| 2 | source citations resolve | (same) | ✅ 180 PASS / 0 missing-file / 0 out-of-range |
| 3 | pytest suite | `python -m uv run pytest -q` | ✅ 7 passed in 2.56s |
| 4 | mkdocs strict build | `python -m uv run mkdocs build --strict` | ✅ exit 0, built in 9.88s |

## P1 / informational

- mkdocs emitted INFO messages about `*.zh.md` files not in nav — pre-existing baseline behaviour (i18n suffix plugin owns these); not a regression. The same notice applied to `overall-flow.zh.md` in the previous stage and was accepted.
- Citation count grew from 86 → 180 with the addition of the Carrington chapter (~94 new citations); all resolved on first run.

## Verdict

**PASS** — all P0 green. Stage 1 chapter 1.2.1 (Carrington) marked done.

## Next chapter

Next planned: `stage1-shellpoint` (chapter 1.2.2). Shellpoint has 5 validators / 5 sheets; uses a similar but not identical 4-source join pattern. The Carrington chapter structure is reusable as a template.

---

## v1.1 — node-ID labels surfaced in mermaid (2026-05-17)

Same correction as applied to Shellpoint (see `stage1-shellpoint_2026-05-17.md` § v1.1): prefixed every `T<N>` / `V<N>` / `SH<N>` node label in figure 1.2.1-1 with the ID, e.g. `SH1["SH1 · Carrington_Summary_check"]`. No prose changes. Re-validation: all P0 green.
