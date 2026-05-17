# Test report — stage1-shellpoint (2026-05-17)

## Scope

Stage 1 chapter 1.2.2 — Shellpoint servicer. Delivered docs:

- `docs/validation-report-logic/shellpoint.zh.md` (≈32k chars, 12 headings)
- `docs/validation-report-logic/shellpoint.en.md` (≈38k chars, 12 headings)

Chapter covers: servicer overview (3-schema routing: `to_mysql > to_new_redshift > legacy shellpoint.*`), end-to-end dataflow with mermaid + numbered step-by-step, per-sheet detailed generation logic for all 5 sheets (Summary / General_Check / Advance_Check / ServiceFee_Check / Adv_Info), cross-sheet validation field index, known pitfalls (`servicer='Newrez'` filter, EXCLUDE subquery unique to Shellpoint summary, dual-branch `calc_fee` SLS vs Newrez, `delinq` vs `prevdelinq`, single-DataFrame `shellpoint_other_check`), and complete source citation index.

Also extended `tools/stage_doc_checks.py` PAIRS list to include the new pair.

## P0 checks

| # | Check | Command | Result |
|---|---|---|---|
| 1 | zh/en heading skeleton alignment | `python tools/stage_doc_checks.py` | ✅ ALIGN OK : 12 headings each |
| 2 | source citations resolve | (same) | ✅ 260 PASS / 0 missing-file / 0 out-of-range |
| 3 | pytest suite | `python -m uv run pytest -q` | ✅ 7 passed in 2.23s |
| 4 | mkdocs strict build | `python -m uv run mkdocs build --strict` | ✅ exit 0, built in 9.23s |

## P1 / informational

- One iteration was required: initial citation `shellpoint_validation.py:1-281` was off-by-one (file has 280 lines). Corrected to `1-280` in both zh and en; re-run came back clean.
- mkdocs INFO messages about `*.zh.md` files not in nav — pre-existing baseline behaviour (i18n suffix plugin owns these); not a regression.
- Citation count grew from 180 → 260 with the addition of the Shellpoint chapter (~80 new citations); all resolved after the line-range fix.

## Verdict

**PASS** — all P0 green. Stage 1 chapter 1.2.2 (Shellpoint) marked done.

## Next chapter

Next planned: `stage1-arvest` (chapter 1.2.3, 4 sheets). Alternatives: `stage1-cc5` (2 sheets, fastest), `stage1-selene` (5 sheets), or `stage1-mrc` (5 sheets, frozen scope.md to incorporate). User to confirm.

---

## v1.1 — node-ID labels surfaced in mermaid (2026-05-17)

**Trigger**: user observed that prose under figure 1.2.2-1 references `SH1`/`SH2`/…/`SH5` but those IDs are not visible in the rendered mermaid diagram (only the bracket label shows; `SH1` is just the internal node ID).

**Fix**: prefixed every `T<N>` / `V<N>` / `SH<N>` node's display label with the ID, e.g. `SH1["SH1 · Shellpoint_Summary_check"]`. Applied to `shellpoint.zh.md` + `shellpoint.en.md` (and the same pattern in `carrington.{zh,en}.md` for consistency). No prose changes.

**Re-validation**: stage_doc_checks 4 pairs aligned + 260 citations PASS ✅; pytest 7/7 ✅; mkdocs --strict exit 0 (9.38s) ✅.
